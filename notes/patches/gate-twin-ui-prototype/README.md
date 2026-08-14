# gate twin 原型(2026-08-14,PGS 現場)—— 大部分已被正式工具取代

| 檔 | 狀態 |
|---|---|
| `devflow_ui.py` | **已被取代** → `scripts/devflow_twin_ui.py`(移植時去掉 5-tasks 專用的 `CSS_TASKS`) |
| `build_review.py` | **已被取代** → `scripts/build-gate-twin.py`(4-spec 那條路徑;解析器改用寬鬆標題 pattern,與 `check-spec-gate.sh` 對齊,兩種 md 寫法都吃得到) |
| `build_tasks.py` | **仍是唯一實作** —— 5-tasks 是「執行板」,是 gate twin 與紀錄 twin 之外的第三種形狀,B-8 本輪只做了 gate 三站,執行板尚未進母版 |

⚠️ **不要拿這裡的檔案當正本改**。要改 gate twin 的產生方式,改 `scripts/build-gate-twin.py`
(有守衛 `scripts/check-gate-twin.sh` 盯著,21 項檢查含負向案)。

留著的理由:`build_tasks.py` 還沒有替代品,而且它示範了執行板的形狀(Boundaries 摺疊、
四欄表、DAG inline SVG),日後要把 5-tasks 納進來時直接照抄。
