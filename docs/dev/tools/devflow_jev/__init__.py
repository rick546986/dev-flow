"""devflow_jev — jev-gate 七組守衛的 **foundation**(W1;roadmap P1-G1～G7)。

這是 pure functions / schema / fake transport,**不是 runtime**:
- 沒有任何對真 API 發送的程式(`urllib` 完全不 import);
- 沒有 `scripts/devflow-jev.py`;roadmap §0 第 2 條:七組守衛負面測試全綠前不准寫 runtime,shadow 也算。
- 這裡通過只代表 guard foundation 完成,不等於 Jev 已部署、任何 AUTO gate 已核准。

模組對照(roadmap §3.1):
  G1 packet.py       evidence packet + reference isolation(header 永不砍、body 才裁)
  G2 policy.py       failure/no-op、deadline、breaker、budget、route formula
  G3 gate.py         雙閘門:TYPESAFE_API_KEY + .dev-flow/jev.yaml,min(mode, gates[Jn])
  G4 ledger.py       雙層 ledger:durable 只存 ID/hash/結構化指標;local replay store 存全文
  G5 manifest.py     jev-questions.json + evaluation manifest → questionset_hash;Score level==index
  G6 provenance.py   derived-only route、tamper 重算、risk_paths 縮窄留痕、runtime 改動當次 HUMAN
  G7 attestation.py  verdict provenance tripwire(格式不是 authentication)
     transport.py    fake transport + response schema 驗證(唯一的「傳輸」實作)
     report.py       最小 Wilson / 分層計數(P2-2 之前的 helper)

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
