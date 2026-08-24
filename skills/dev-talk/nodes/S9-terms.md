# S9-terms — 詞彙對帳

## 進條件

S8 已完成。MEMORY_SESSION_ID 仍在。游標在 S9。
本節點 = 舊執行清單步 9,不是 N9-write-md。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

本場浮現的業務詞彙、長期記憶現況(`dev-memory.py ask`)。
不讀白名單外的文件類資料夾。

## 寫哪裡

只經 `dev-memory.py talk propose` / `confirm` / `reject` / `correct` 登記候選。
不直接改長期記憶檔。不寫 `1-discussion.md`。不寫程式碼。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

先查長期記憶的現況(`dev-memory.py ask "<詞> 是什麼意思"`
——其他討論可能已經確認過詞條,只增改自己本輪的、不動他人的),再把本輪浮現的
業務詞彙逐一登記成候選(`dev-memory.py talk propose $MEMORY_SESSION_ID
--kind domain --payload-json '{"key":"…","title":"…","body":"…"}'`;
詞條 + _Avoid_ 寫在同一則裡;只收語言不收解法 —— 逐詞自問「這詞條在解釋語言,
還是在記方案?」後者刪;尚未實作的語意用 `--kind intent` 而不是 domain,
它不能被當成現況;同名異義分立互註)。使用者明確確認的才
`dev-memory.py talk confirm <candidate>`;使用者否定的走
`dev-memory.py talk reject <candidate>`;使用者推翻先前已記錄的理解時走
`dev-memory.py talk correct $MEMORY_SESSION_ID --kind domain --key <詞>
--title "<新理解>" --reason "<為什麼改>"`(舊的會保留並標成被取代,
看得到轉折才叫記憶)。未確認的候選一律不寫進長期記憶。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S9-terms "$MEMORY_SESSION_ID"`。

## 完成條件

逐詞打勾。本機游標在 S9-terms。

## 下一跳

S10-html
