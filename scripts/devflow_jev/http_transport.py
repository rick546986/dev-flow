"""真 HTTP transport(W2 P1-F1)。**整個套件唯一准 import 網路模組的檔**。

- `scripts/test-devflow-jev.sh` ① 與 `test_guards.W1Boundary` 只對這一支放行 urllib;其餘模組零網路。
- 只做「送 request、收 raw JSON」;形狀驗證仍在 `transport.parse_response`,錯誤一律轉成
  `TransportError(kind)` 讓 `policy.evaluate` 走 no-op(G2)。這裡沒有 retry、沒有 backoff。
- API key 只存在 transport 物件裡,不進任何 log／錯誤訊息／replay store(`__repr__` 不印)。
- endpoint 只准 https;`DEVFLOW_JEV_ENDPOINT` 覆寫只在測試用,且非 loopback 一律要求 https。
- 未持 key 的呼叫端**不該建這個物件**(runtime 在 `gate.effective_level` 之後才建它);
  建構時 key 空 → fail-loud,不會默默送匿名請求。
"""
import json
import socket
import urllib.error
import urllib.parse
import urllib.request

from . import JevError
from .transport import TransportError

ENDPOINT_DEFAULT = "https://api.typesafe.ai/v1/systemone"
ENDPOINT_ENV = "DEVFLOW_JEV_ENDPOINT"
DEFAULT_TIMEOUT_S = 30.0
USER_AGENT = "devflow-jev/1.0"
HTTP_STATUS_KINDS = {400: "http_400", 401: "http_401", 422: "http_422", 429: "http_429", 529: "http_529"}
_LOOPBACK_HOSTS = ("127.0.0.1", "localhost", "::1")


def endpoint_host(url):
    """用 urllib 自己的 parser 拆 host(手拆會被 `#@localhost`／`?x=@localhost` 騙)。回 (scheme, hostname)。"""
    if not isinstance(url, str) or url != url.strip() or "://" not in url:
        raise JevError("endpoint 形狀不對:%r" % (url,))
    parts = urllib.parse.urlsplit(url)
    if parts.username is not None or parts.password is not None:
        raise JevError("endpoint 不得含 userinfo:%s" % url)
    hostname = parts.hostname
    if not hostname:
        raise JevError("endpoint 缺 host:%s" % url)
    return parts.scheme.lower(), hostname.lower()


def is_loopback(url):
    return endpoint_host(url)[1] in _LOOPBACK_HOSTS


def validate_endpoint(url):
    """https 為預設;http 只准 loopback(測試用閉埠)。其它形狀 fail-loud。"""
    scheme, hostname = endpoint_host(url)
    if scheme == "https":
        return url
    if scheme == "http" and hostname in _LOOPBACK_HOSTS:
        return url
    raise JevError("endpoint 必須是 https(或 loopback 的 http,僅測試):%s" % url)


def default_opener(url):
    """loopback endpoint 一律繞過環境 proxy(否則 `http_proxy` 在、`no_proxy` 不在時,「閉埠零網路」測試會
    把 Bearer key 送到 proxy);https 正式 endpoint 沿用環境 proxy 設定(企業出口)。"""
    if is_loopback(url):
        return urllib.request.build_opener(urllib.request.ProxyHandler({})).open
    return urllib.request.urlopen


class HttpTransport(object):
    """`send(request) -> raw dict`;任何失敗 → TransportError(kind)。"""

    def __init__(self, api_key, endpoint=ENDPOINT_DEFAULT, timeout_s=DEFAULT_TIMEOUT_S, opener=None):
        if not isinstance(api_key, str) or not api_key.strip():
            raise JevError("HttpTransport: api_key 空 —— 未持 key 不該建 transport(雙閘門在前)")
        self._key = api_key.strip()
        self.endpoint = validate_endpoint(endpoint)
        self.timeout_s = float(timeout_s)
        self._opener = opener or default_opener(self.endpoint)
        self.calls = 0

    def __repr__(self):
        return "HttpTransport(endpoint=%r, timeout_s=%s, calls=%d)" % (self.endpoint, self.timeout_s, self.calls)

    def send(self, request):
        self.calls += 1
        body = json.dumps(request, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            self.endpoint, data=body, method="POST",
            headers={"Content-Type": "application/json", "Accept": "application/json",
                     "Authorization": "Bearer " + self._key, "User-Agent": USER_AGENT})
        try:
            with self._opener(req, timeout=self.timeout_s) as resp:
                payload = resp.read()
        except urllib.error.HTTPError as exc:
            kind = HTTP_STATUS_KINDS.get(exc.code)
            if kind is None:
                # 不在 ERROR_KINDS 的狀態碼歸 network(仍 no-op);detail 只帶狀態碼,不帶 body(可能回顯 key)
                raise TransportError("network", "http_%s" % exc.code)
            raise TransportError(kind, "http status %s" % exc.code)
        except socket.timeout:
            raise TransportError("timeout", "socket timeout after %.1fs" % self.timeout_s)
        except urllib.error.URLError as exc:
            reason = exc.reason
            if isinstance(reason, socket.timeout) or "timed out" in str(reason).lower():
                raise TransportError("timeout", "urlopen timeout after %.1fs" % self.timeout_s)
            raise TransportError("network", type(reason).__name__ if not isinstance(reason, str) else reason)
        except (OSError, ValueError) as exc:
            raise TransportError("network", type(exc).__name__)
        try:
            raw = json.loads(payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            raise TransportError("malformed_json", "response body is not JSON")
        if not isinstance(raw, dict):
            raise TransportError("malformed_json", "response JSON is not an object")
        return raw
