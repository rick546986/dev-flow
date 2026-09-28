"""http_transport 的牙:假 opener + loopback 閉埠;零外部網路。key 不得出現在任何錯誤訊息。"""
import io
import json
import socket
import unittest
import urllib.error

from devflow_jev import JevError, http_transport
from devflow_jev.transport import TransportError, parse_response


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


if __name__ == "__main__":
    unittest.main()
