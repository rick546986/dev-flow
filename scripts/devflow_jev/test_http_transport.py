"""http_transport 的牙:假 opener + loopback 閉埠;零外部網路。key 不得出現在任何錯誤訊息。"""
import http.server
import io
import json
import socket
import threading
import unittest
import urllib.error

from devflow_jev import JevError, http_transport, manifest, policy
from devflow_jev.transport import TransportError, canned_response, parse_response


class _Resp(object):
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return self.payload

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def opener_returning(payload):
    seen = {}

    def opener(req, timeout=None):
        seen["req"] = req
        seen["timeout"] = timeout
        return _Resp(payload)
    return opener, seen


def opener_raising(exc):
    def opener(req, timeout=None):
        raise exc
    return opener


KEY = "sk-test-not-real-key-1234567890"


class HttpTransportShape(unittest.TestCase):
    def test_empty_key_refused(self):
        with self.assertRaises(JevError):
            http_transport.HttpTransport("")

    def test_endpoint_must_be_https_or_loopback(self):
        http_transport.validate_endpoint("https://api.typesafe.ai/v1/systemone")
        http_transport.validate_endpoint("http://127.0.0.1:9/")
        http_transport.validate_endpoint("http://[::1]:9/")
        http_transport.validate_endpoint("HTTP://LOCALHOST:9/")
        for bad in ("http://api.typesafe.ai/v1/systemone", "ftp://x", "not-a-url", "http://evil.example/",
                    "http://192.0.2.1#@localhost", "http://192.0.2.1?x=@localhost", "http://evil.example#@127.0.0.1",
                    "http://user@127.0.0.1:9/", "https://user:pw@api.typesafe.ai/v1", " https://api.typesafe.ai/v1"):
            with self.assertRaises(JevError, msg=bad):
                http_transport.validate_endpoint(bad)

    def test_loopback_opener_bypasses_environment_proxy(self):
        import os
        old = {k: os.environ.get(k) for k in ("http_proxy", "HTTP_PROXY", "no_proxy", "NO_PROXY")}
        try:
            os.environ["http_proxy"] = "http://192.0.2.9:3128"
            os.environ.pop("no_proxy", None)
            os.environ.pop("NO_PROXY", None)
            t = http_transport.HttpTransport(KEY, endpoint="http://127.0.0.1:9/", timeout_s=1.0)
            with self.assertRaises(TransportError) as cm:
                t.send({"model": "jev-1.13.0", "state": {}, "questions": {"q": {"type": "noul", "text": "x"}}})
            # 打的是 loopback 閉埠(connection refused → network),不是 192.0.2.9 那個假 proxy(會 timeout)
            self.assertEqual(cm.exception.kind, "network")
        finally:
            for k, v in old.items():
                if v is None:
                    os.environ.pop(k, None)
                else:
                    os.environ[k] = v

    def test_sends_bearer_json_and_returns_raw(self):
        opener, seen = opener_returning(json.dumps({"model": "jev-1.13.0", "answers": {}}).encode())
        t = http_transport.HttpTransport(KEY, opener=opener, timeout_s=3)
        raw = t.send({"model": "jev-1.13.0", "state": {}, "questions": {"q": {"type": "noul", "text": "x"}}})
        self.assertEqual(raw["model"], "jev-1.13.0")
        req = seen["req"]
        self.assertEqual(req.get_method(), "POST")
        self.assertEqual(req.get_header("Authorization"), "Bearer " + KEY)
        self.assertEqual(req.get_header("Content-type"), "application/json")
        self.assertEqual(seen["timeout"], 3.0)
        self.assertNotIn(KEY, repr(t))

    def test_http_status_kinds(self):
        for code, kind in ((400, "http_400"), (401, "http_401"), (422, "http_422"), (429, "http_429"), (529, "http_529")):
            exc = urllib.error.HTTPError("u", code, "m", {}, io.BytesIO(b"{}"))
            t = http_transport.HttpTransport(KEY, opener=opener_raising(exc))
            with self.assertRaises(TransportError) as cm:
                t.send({"x": 1})
            self.assertEqual(cm.exception.kind, kind)
            self.assertNotIn(KEY, str(cm.exception))
        exc = urllib.error.HTTPError("u", 503, "m", {}, io.BytesIO(b"{}"))
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener_raising(exc)).send({})
        self.assertEqual(cm.exception.kind, "network")

    def test_timeout_and_network_kinds(self):
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener_raising(socket.timeout())).send({})
        self.assertEqual(cm.exception.kind, "timeout")
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener_raising(urllib.error.URLError(socket.timeout("timed out")))).send({})
        self.assertEqual(cm.exception.kind, "timeout")
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener_raising(urllib.error.URLError(ConnectionRefusedError()))).send({})
        self.assertEqual(cm.exception.kind, "network")

    def test_malformed_json(self):
        opener, _ = opener_returning(b"<html>nope</html>")
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener).send({})
        self.assertEqual(cm.exception.kind, "malformed_json")
        opener, _ = opener_returning(b"[1,2]")
        with self.assertRaises(TransportError) as cm:
            http_transport.HttpTransport(KEY, opener=opener).send({})
        self.assertEqual(cm.exception.kind, "malformed_json")

    def test_loopback_closed_port_is_network_or_timeout_noop_kind(self):
        t = http_transport.HttpTransport(KEY, endpoint="http://127.0.0.1:9/", timeout_s=1.0)
        with self.assertRaises(TransportError) as cm:
            t.send({"model": "jev-1.13.0", "state": {}, "questions": {"q": {"type": "noul", "text": "x"}}})
        self.assertIn(cm.exception.kind, ("network", "timeout"))
        self.assertNotIn(KEY, str(cm.exception))

    def test_raw_still_goes_through_parse_response(self):
        questions = {"q": {"type": "noul", "text": "x"}}
        opener, _ = opener_returning(json.dumps({"model": "jev-1.13.0", "answers": {"q": {"noul": 1.5}}}).encode())
        raw = http_transport.HttpTransport(KEY, opener=opener).send({})
        with self.assertRaises(TransportError) as cm:
            parse_response(raw, questions)
        self.assertEqual(cm.exception.kind, "schema")


def http_error(code, body):
    return urllib.error.HTTPError("u", code, "m", {}, io.BytesIO(body if isinstance(body, bytes) else body.encode("utf-8")))


class HttpErrorDetail(unittest.TestCase):
    """400／422 讀服務回的 body 取 detail:遮機密、截 500 字、寫進 TransportError.detail(key 絕不出現)。"""
    MISSING = {"detail": "Noul question must have criteria or instructions: goal_clear"}

    def send_expecting(self, code, body, key=KEY):
        t = http_transport.HttpTransport(key, opener=opener_raising(http_error(code, body)))
        with self.assertRaises(TransportError) as cm:
            t.send({"x": 1})
        self.assertNotIn(key, repr(t))
        self.assertNotIn(key, str(cm.exception))
        self.assertNotIn(key, cm.exception.detail)
        return cm.exception

    def test_400_detail_is_recorded(self):
        exc = self.send_expecting(400, json.dumps(self.MISSING))
        self.assertEqual(exc.kind, "http_400")
        self.assertEqual(exc.detail, "http status 400: Noul question must have criteria or instructions: goal_clear")
        self.assertIn("goal_clear", str(exc))

    def test_422_detail_list_is_recorded(self):
        body = json.dumps({"detail": [{"loc": ["body", "questions", "q"], "msg": "field required"}]})
        exc = self.send_expecting(422, body)
        self.assertEqual(exc.kind, "http_422")
        self.assertIn("field required", exc.detail)
        self.assertTrue(exc.detail.startswith("http status 422: "))

    def test_non_json_body_uses_plain_text(self):
        exc = self.send_expecting(400, "bad request: questions.q is wrong\n  see docs")
        self.assertEqual(exc.detail, "http status 400: bad request: questions.q is wrong see docs")

    def test_detail_masks_secrets_and_never_shows_the_key(self):
        sk = "sk-live-ABCDEFGH12345678"
        body = json.dumps({"detail": "echo Authorization: Bearer abcdefghijklmnop12345 and TYPESAFE_API_KEY=%s "
                                     "and own key %s and token: tok_12345678 and %s and long %s and /home/box/.env"
                                     % (sk, KEY, sk, "A1b2" * 10)})
        exc = self.send_expecting(400, body)
        for leaked in ("abcdefghijklmnop12345", sk, "tok_12345678", "A1b2" * 10, "/home/box/.env"):
            self.assertNotIn(leaked, exc.detail)
        self.assertIn("[REDACTED]", exc.detail)
        self.assertTrue(exc.detail.startswith("http status 400: echo "))

    def test_detail_masks_key_even_when_short_and_unpatterned(self):
        exc = self.send_expecting(422, json.dumps({"detail": "unknown credential abc-xyz-1 rejected"}), key="abc-xyz-1")
        self.assertNotIn("abc-xyz-1", exc.detail)
        self.assertIn("[REDACTED]", exc.detail)

    def test_detail_is_truncated_to_500_chars(self):
        exc = self.send_expecting(400, json.dumps({"detail": "abc " * 1000}))
        prefix = "http status 400: "
        self.assertEqual(len(exc.detail) - len(prefix), http_transport.DETAIL_MAX_CHARS)
        self.assertEqual(http_transport.DETAIL_MAX_CHARS, 500)
        exc = self.send_expecting(422, "z " * 100000)                       # 超大 body:限讀、不爆
        self.assertLessEqual(len(exc.detail) - len(prefix), 500)

    def test_secret_is_masked_before_truncation(self):
        # 機密剛好跨在第 500 字:先遮後截,不會露出殘缺的 key 前綴
        secret = "Bearer " + "Q" * 40
        exc = self.send_expecting(400, json.dumps({"detail": "x " * 247 + secret}))
        self.assertNotIn("QQQQ", exc.detail)

    def test_other_statuses_never_read_the_body(self):
        for code in (401, 429, 529):
            exc = self.send_expecting(code, json.dumps({"detail": "echo %s" % KEY}))
            self.assertEqual(exc.detail, "http status %s" % code)
        exc = self.send_expecting(503, json.dumps({"detail": "x"}))
        self.assertEqual((exc.kind, exc.detail), ("network", "http_503"))

    def test_unreadable_or_empty_body_keeps_status_only(self):
        class Boom(urllib.error.HTTPError):
            def read(self, *a):
                raise OSError("boom")
        t = http_transport.HttpTransport(KEY, opener=opener_raising(Boom("u", 400, "m", {}, None)))
        with self.assertRaises(TransportError) as cm:
            t.send({})
        self.assertEqual(cm.exception.detail, "http status 400")
        self.assertEqual(self.send_expecting(400, b"").detail, "http status 400")
        self.assertEqual(self.send_expecting(400, b"\xff\xfe not utf8").kind, "http_400")

    def test_policy_noop_carries_masked_detail_but_reason_stays_a_bare_kind(self):
        body = json.dumps({"detail": "Noul question must have criteria or instructions: goal_clear; key=%s" % KEY})
        t = http_transport.HttpTransport(KEY, opener=opener_raising(http_error(400, body)))
        out = policy.evaluate(t, {"x": 1}, {"q": {"type": "noul", "text": "x"}}, lambda: 0.0, 100)
        self.assertEqual((out["status"], out["reason"]), ("noop", "transport:http_400"))
        self.assertIn("Noul question must have criteria or instructions: goal_clear", out["detail"])
        self.assertNotIn(KEY, out["detail"])
        self.assertLessEqual(len(out["detail"]), policy.NOOP_DETAIL_MAX_CHARS)

    def test_policy_noop_remasks_schema_style_detail(self):
        from devflow_jev.transport import FakeTransport
        out = policy.evaluate(FakeTransport([{"response": {"model": "m", "answers": {"q": {"choice": "Bearer " + "Z" * 30,
                              "probabilities": {}, "confidence": 1}}}}]), {"x": 1},
                              {"q": {"type": "choice", "text": "x", "criteria": {"A": "a", "B": "b"}}}, lambda: 0.0, 100)
        self.assertEqual(out["reason"], "transport:schema")
        self.assertIn("[REDACTED]", out["detail"])
        self.assertNotIn("ZZZZ", out["detail"])


class FakeJevServer(object):
    """loopback 假 Jev 服務:照真服務的規則驗 noul(缺 criteria 且缺 instructions → 400 + detail),否則回合法 200。"""

    def __init__(self, fixed=None):
        self.requests = []
        self.fixed = fixed                      # (status, body_dict) 強制回應(測 422／遮罩用)
        outer = self

        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_POST(self):
                length = int(self.headers.get("Content-Length") or 0)
                req = json.loads(self.rfile.read(length).decode("utf-8"))
                outer.requests.append({"auth": self.headers.get("Authorization"), "body": req})
                status, body = 200, None
                if outer.fixed:
                    status, body = outer.fixed
                else:
                    for qid, q in req["questions"].items():
                        if q["type"] == "noul" and not q.get("criteria") and not q.get("instructions"):
                            status, body = 400, {"detail": "Noul question must have criteria or instructions: %s" % qid}
                            break
                if body is None:
                    body = canned_response(req["questions"], {})
                payload = json.dumps(body).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)

        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), Handler)
        self.endpoint = "http://127.0.0.1:%d/" % self.httpd.server_address[1]
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *exc):
        self.httpd.shutdown()
        self.httpd.server_close()
        self.thread.join(5)
        return False


class LoopbackMissingCriteria(unittest.TestCase):
    """loopback 假伺服器重現「noul 缺 criteria → 400」。對照組:gate_questions_for_api 改回不帶 criteria,
    同一條流程必須失敗(測試裡 patch,正式碼沒有後門)。"""
    SHIPPED = (("J1", None), ("J3", None), ("J5", None),
               ("J2", "jev-questions-experimental.json"), ("J4", "jev-questions-experimental.json"))

    def man(self, fname):
        import os
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname) if fname else None
        return manifest.build_manifest(manifest.load_questions(path))

    def flow(self, server, gate, fname):
        """正式流程:題庫 → gate_questions_for_api → HttpTransport.send → parse_response。成功回 parsed。"""
        api = manifest.gate_questions_for_api(self.man(fname), gate)
        t = http_transport.HttpTransport(KEY, endpoint=server.endpoint, timeout_s=5)
        return parse_response(t.send({"model": "jev-1.13.0", "state": {"k": "v"}, "questions": api}), api)

    def test_noul_question_text_only_gets_400_with_recorded_detail(self):
        questions = {"goal_clear": {"type": "noul", "text": "Is the goal clear?"}}
        with FakeJevServer() as server:
            t = http_transport.HttpTransport(KEY, endpoint=server.endpoint, timeout_s=5)
            with self.assertRaises(TransportError) as cm:
                t.send({"model": "jev-1.13.0", "state": {}, "questions": questions})
        self.assertEqual(cm.exception.kind, "http_400")
        self.assertIn("Noul question must have criteria or instructions: goal_clear", cm.exception.detail)
        self.assertEqual(server.requests[0]["auth"], "Bearer " + KEY)         # key 有送出去,但不在 detail
        self.assertNotIn(KEY, str(cm.exception))

    def test_every_shipped_gate_is_accepted_by_the_validating_server(self):
        with FakeJevServer() as server:
            for gate, fname in self.SHIPPED:
                parsed = self.flow(server, gate, fname)
                self.assertTrue(parsed["answers"], gate)
        sent = [r["body"]["questions"] for r in server.requests]
        self.assertEqual(len(sent), len(self.SHIPPED))
        for questions in sent:
            for q in questions.values():
                if q["type"] == "noul":
                    self.assertTrue(q["criteria"] and q["instructions"])

    def test_422_from_loopback_server_is_recorded_and_masked(self):
        with FakeJevServer(fixed=(422, {"detail": "bad body for key %s" % KEY})) as server:
            t = http_transport.HttpTransport(KEY, endpoint=server.endpoint, timeout_s=5)
            with self.assertRaises(TransportError) as cm:
                t.send({"model": "jev-1.13.0", "state": {}, "questions": {"q": {"type": "noul", "text": "x", "instructions": "i"}}})
        self.assertEqual(cm.exception.kind, "http_422")
        self.assertIn("[REDACTED]", cm.exception.detail)
        self.assertNotIn(KEY, cm.exception.detail)

    def test_counter_legacy_gate_questions_reproduces_the_400_on_every_noul_gate(self):
        from devflow_jev.test_guards import legacy_gate_questions_for_api
        saved = manifest.gate_questions_for_api
        manifest.gate_questions_for_api = legacy_gate_questions_for_api
        try:
            with FakeJevServer() as server:
                for gate, fname in self.SHIPPED:
                    with self.assertRaises(TransportError, msg=gate) as cm:       # 新流程測試在舊行為下必紅
                        self.flow(server, gate, fname)
                    self.assertEqual(cm.exception.kind, "http_400", gate)
                    self.assertIn("Noul question must have criteria or instructions", cm.exception.detail)
        finally:
            manifest.gate_questions_for_api = saved


if __name__ == "__main__":
    unittest.main()
