"""devflow_jev — G2 自動審查上線用的 Jev 最小套件(從 research/jev-supermemory W9/W10 只搬 G2 需要的部分)。

main 上**只有** G2R 分流(Jev 只分流、不 review、不寫 verdict)與 G2 誤放行紀錄;
research 分支的 J1–J5 runtime(packet／ledger／manifest／report／state／MR)**沒搬**。

模組:
  gate.py            雙閘門:TYPESAFE_API_KEY + .dev-flow/jev.yaml(research 原檔,語意不動)
  transport.py       response schema 驗證 + fake transport(research 原檔)
  http_transport.py  唯一准碰網路的真傳輸(research 原檔;POST 一次、失敗即 TransportError)
  attestation.py     verdict provenance tripwire(research W6 原檔;格式不是 authentication)
  policy.py          G2R 分流 route_g2、spec_risk_of、G2 誤放行驗證與率(research W9/W10,G2 上線版)
  g2auto.py          G2 自動放行的機械判定(devflow_gate.py 寫入前與 check-verdict-attestation.sh 共用)

相容地板:Python 3.9 語法(scripts/check-py-floor.sh);stdlib only。
"""

GATES = ("J1", "J2", "J3", "J4", "J5")      # gate.py 的 jev.yaml `gates:` 鍵;G2R 不在這裡(只看 mode:)
LEVELS = ("off", "shadow", "live")          # 生效等級全序:off < shadow < live
MODEL_PINNED = "jev-1.13.0"


class JevError(Exception):
    """守衛層 fail-loud 的單一例外型別;呼叫端不得吞掉後當成功。"""
