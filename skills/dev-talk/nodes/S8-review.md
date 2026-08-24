# S8-review — 獨立複核

## 進條件

N9 已完成(`1-discussion.md` 已在)。MEMORY_SESSION_ID 仍在。游標在 S8。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

`1-discussion.md` 全檔、步 0 的範圍、已核事實、真實世界五份。
不讀白名單外的文件類資料夾。

## 寫哪裡

可改已有的 `1-discussion.md`,不得另存第二份。不得寫程式碼。不得 talk end。
不直接改長期記憶檔。本機游標只留在本機,不進 Git。

## 做什麼

換上嚴格審視者視角重讀全檔:①每條驗收敘述自洽嗎?有無
斷言超出可驗範圍?②所有結論都有「已核事實」或問答背書嗎?③與使用者
原話有無矛盾?④Interview Log 每條齊「事實→推理→結論」三段嗎?
⑤範圍對照步 0 的界定,有沒有悄悄長大?長大 → 問使用者拆或收。⑥同一
名詞/事實多處出現,逐處比對數字、條件、方向一致嗎?不一致 → 統一
或標 Open Question。⑦真實世界五份裡,每條沒有證據的敘述都標了
`[Assumption]` 嗎?有沒有把訪談印象寫成事實?
發現問題 → 改檔或回步 3 補問。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S8-review "$MEMORY_SESSION_ID"`。

## 完成條件

七掃完畢、問題清零。本機游標在 S8-review。

## 下一跳

S9-terms
