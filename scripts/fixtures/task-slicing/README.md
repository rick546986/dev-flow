# 反水平切層 heuristic fixture

`scripts/check-task-slicing.sh` 的自我測試材料。三份都是**假的** 5-tasks,
只為釘住啟發式的判定邊界,不是任何真實 feature。

| 檔 | 期望 | 為什麼 |
|---|---|---|
| `horizontal-5-tasks.md` | warn | 整份按 DB→Repository→Service→API→UI 切,Intent 全是「建立 X 層」 |
| `vertical-5-tasks.md` | ok | tracer bullet 縱切,每個 T 的 Intent 都說得出可觀測結果 |
| `infra-5-tasks.md` | ok | 合法的純 Migration/Infrastructure Task —— 標題是架構層名詞,但 Intent 寫得出可觀測結果,不該被誤傷 |
