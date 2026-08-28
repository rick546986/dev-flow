# S10-html — 產 html

## 進條件

S9 已完成。`1-discussion.md` 已在。MEMORY_SESSION_ID 仍在。游標在 S10。
不得 talk start。不得寫程式碼。不得 talk end。

## 讀什麼

`1-discussion.md`(正本)。Open Questions 只認三態。
不讀白名單外的文件類資料夾。

## 寫哪裡

只寫同目錄 `1-discussion.html`。md 是唯一正本;html 要改,先改 md 再重生。
不另存第二份 md。不得寫程式碼。不得 talk end。不直接改長期記憶檔。
本機游標只留在本機,不進 Git。

## 做什麼

先自核 md:Open Questions 僅含三態符號,出現其他記號(如 `[ ]`)
→ 回步 3 定態後才產。不准手寫 `1-discussion.html`。跑
`${DEVFLOW_ROOT}/scripts/build-scan-html.py --action` 指向本場 md
(或 `python3 ${DEVFLOW_ROOT}/scripts/build-scan-html.py <md路徑>`)。
產生器從 md 產出掃頁六件,殼用 `skills/dev-talk/html-shell.html`。
html 要改,先改 md 再重生。
內容與圖判準見入口檔「視覺版」。掃頁六件,不多不少:
1. 摘要卡(痛 + 現在怎麼繞 + Open Questions 三態 badge)
2. 直式現況圖(誰／做什麼／工具／痛點,直式三框,每框四行;inline SVG;直式,不要橫排;禁 mermaid／外連圖／外部庫)
3. 人與土法(誰／要什麼／缺什麼;[Assumption] 看得見)
4. 題目(每列一題 + 著落:已解／假設／移交)
5. 驗收一小表(假設…當…則…｜從哪看｜看到什麼)
6. 問答摘要預設摺著(`<details>`);Constraints／詞條不佔第一屏
html `#scan-now`(svg 或 pre)只從 md 現況圖重生;兩邊抽出的誰／工具／動作／痛點
指紋不同就紅。不准拿明天系統流充 `#scan-now`。
跑 `${DEVFLOW_ROOT}/scripts/check-devtalk-graph.sh --write-cursor S10-html "$MEMORY_SESSION_ID"`。

## 完成條件

自核過+掃頁六件齊。md 現況圖與 html `#scan-now` 指紋相同。本機游標在 S10-html。

## 下一跳

N13-end
