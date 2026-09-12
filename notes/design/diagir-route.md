# 圖表 IR 五家族查找路由表

wave-1 查找表。人／agent **先選** `family`；閘不黑盒猜列。
改 id 或併 API = 回第 2 站。契約欄指回已核短冊；各家族「何時不用」原文仍在該契約。

| id | 用這條 | 不用那條 | 產器 | 契約 |
|---|---|---|---|---|
| stage1-now | 第 1 站審頁 `#scan-now` 直式三框 | 掃頁 `build-scan-html.py`；vbox-fig 生命週期四格；gate-twin 五格 | `build-stage1-html.py --action` | `notes/design/stage1-review-ui-contract.md` |
| stage2-arch | 第 2 站審頁 Decision 後直式 `[標籤]` 標題 SVG | mermaid；橫 ASCII；`<pre>` 當圖；手包 html-shell | `build-stage2-html.py --action` | `notes/design/stage2-review-ui-contract.md` + vbox 母版 |
| behavior-flow | gate-twin 行為流程；樹狀改 WARNING+`<pre>` | 樹收成單盒 vbox；mermaid | `build-gate-twin.py` 行為流 | vbox-fig-contract（twin 收口） |
| dir-tree | 手寫 YAML why；產品 dir-tree.html | 掃 repo 猜 why；收成單盒 vbox；跟第 1 站三框搶槽 | `build-dir-tree.py` | `notes/design/dir-tree-contract.md` |
| vbox-lifecycle | 四格固定：新生 → 改行為 → 退役 → 不動 | 第五格／parked；第 1 站三框；七站三走廊 | `build-vbox-fig.py` lifecycle | `notes/design/vbox-fig-contract.md` |
