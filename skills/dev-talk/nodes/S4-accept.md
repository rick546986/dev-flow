# S4-accept — 驗收雛形

## 進條件

N3 已完成。MEMORY_SESSION_ID 仍在。游標在 S4。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

Goals、已核事實、Interview Log。不讀白名單外的文件類資料夾。

## 寫哪裡

不寫 `1-discussion.md`。不寫程式碼。不直接改長期記憶檔。不得 talk end。
本機游標只留在本機,不進 Git。

## 做什麼

每條 Goal 翻成 1-3 條可驗證敘述(假設…當…則…,使用者視角、
不綁做法),每條再問出「怎麼看到」三件:①從哪裡看(畫面/端點/檔案/log)
②看到什麼算對(具體值、畫面上的字、狀態變化)③拿什麼試(現成的真實資料或
情境;沒有就問要不要造一筆)。說不出怎麼看到 = 這條其實還沒定義清楚,回步 3 問。
問現象不問做法 —— 「你會在哪看到它發生」可問,「該用什麼元件/回什麼 JSON」不問。
逐條請使用者確認。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S4-accept "$MEMORY_SESSION_ID"`。

## 完成條件

全數逐條確認且各有觀測方式。本機游標在 S4-accept。

## 下一跳

S5-diverge
