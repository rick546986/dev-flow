"""devflow_jev — jev-gate 套件(W1 七組守衛 + W2 起的 runtime 函式庫)。

W1 是 pure functions / schema / fake transport。W2 起 runtime 在 `scripts/devflow-jev.py`
(stdlib、雙閘門、`GRADUATED = False` 寫死、沒有 AUTO):
- 套件內只有 `http_transport.py` 可以載入網路模組;其餘模組與 runtime 腳本本身都不碰網路。
- `transport.py` 仍是 fake transport + response schema,不是真傳輸。
- 雙閘門 off 時 runtime 不建 transport、不落盤。
- 測試通過 ≠ Jev 已部署、≠ 任何 AUTO gate 已核准。

模組對照(roadmap §3.1;W2 加 runtime 層,不改守衛語意):
  G1 packet.py         evidence packet + reference isolation(header 永不砍、body 才裁)
  G2 policy.py         failure/no-op、deadline、breaker、budget、route formula
  G3 gate.py           雙閘門:TYPESAFE_API_KEY + .dev-flow/jev.yaml,min(mode, gates[Jn])
  G4 ledger.py         雙層 ledger:durable 只存 ID/hash/結構化指標;local replay store 存全文
  G5 manifest.py       jev-questions.json + evaluation manifest → questionset_hash;Score level==index
  G6 provenance.py     derived-only route、tamper 重算、risk_paths 縮窄留痕、runtime 改動當次 HUMAN
  G7 attestation.py    verdict provenance tripwire(格式不是 authentication)
     transport.py      fake transport + response schema 驗證
     http_transport.py 唯一准碰網路的真傳輸(POST 一次、失敗即 TransportError)
     state.py          budget / breaker 的原子狀態
     report.py         最小 Wilson / 分層計數(P2-2 之前的 helper)

相容地板:Python 3.9 語法(scripts/check-py-floor.sh);stdlib only。
"""

# manifest component versions(roadmap §3.4:任一欄改變 → 新 questionset_hash → 新 group、n=0)
RUBRIC_SCHEMA_VERSION = "1.0.0"
PACKET_BUILDER_VERSION = "1.0.0"
POLICY_VERSION = "1.0.0"
ROUTE_FORMULA_VERSION = "1.0.0"
NORMALIZATION_VERSION = "1.0.0"

GATES = ("J1", "J2", "J3", "J4", "J5")
LEVELS = ("off", "shadow", "live")          # 生效等級全序:off < shadow < live
ROUTES = ("AUTO", "HUMAN", "REQUEST_CHANGES")
MODEL_PINNED = "jev-1.13.0"


class JevError(Exception):
    """守衛層 fail-loud 的單一例外型別;呼叫端不得吞掉後當成功。"""
