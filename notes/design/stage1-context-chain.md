# Stage 1：相關脈絡進場＋推理鏈路外顯（merged brief）

> 五份獨立審查共識 = **NARROW**。填既有 Context + Interview Log 槽，不新增章節。
> 審頁正本仍是 `notes/design/stage1-review-ui-contract.md`。本檔不動審頁。
> 本檔用到的 repo 名詞：`talk start` 回傳的 brief（`memory/agentmem/devtalk.py` 的 `probe()` 輸出）、
> `dev-memory.py ask()`、掃頁產生器 `scripts/build-scan-html.py`（S10）。

## 1. Status

本檔是 **design note 正本**，不是契約。後續實作另開 PR。
零版本 bump（`.claude-plugin/plugin.json`、契約 schema 皆不動）。不加 hop／gate／審頁解鎖／第 7 掃頁格。

## 2. Problem

S1 已有 Context（已知事實）＋ Interview Log（Q／事實／推理／結論），但：

- `talk start` 回傳的 brief 常被當裝飾：`known_facts`／`known_knowledge`／`repo_signals` 沒進 S1 的盤點，已核事實也不帶出處。
- Interview Log 常只記結論，事實欄沒有可核對的路徑。
- 掃頁 `build-scan-html.py` 的 `parse_log` 逐行收、`build_body` 逐行包 `<p>`，`#scan-log` 看不到四段鏈路。

## 3. Thesis

**Stage 1 = 強制消化 brief／`ask()` 當脈絡線索 → 經 current repo／spec 驗證後進 Context（帶出處）→ Interview Log 四段外顯，事實欄只引用 Context 已列出處。**

核心原則：**signal ≠ evidence；memory ≠ current fact。** 記得的東西與此刻重新驗證為真的東西分開放。
跨功能複利只走 `.dev-flow` 已確認語意，不傾倒他 slug 的 1–7。Stage 2 的 Approaches／Decision／OC／ADR 不進本 hop。

## 4. Do（實作時）

- N1／S1 **必須消化** brief：`known_facts`／`known_knowledge`／`repo_signals`／`conflicts` 逐項過一遍，每項落到「已驗證進 Context」「留 Log 待驗證」「不相關」三者之一。
- Context：只收 current repo／spec 驗證過的事實，每條帶出處（§6 引用語法）。
- Interview Log：巢狀四段（§6 grammar）。事實欄引用 Context 已列出處。高影響標 ⚠️。
- 掃頁 `#scan-log`：四欄表，與 md 同形。S10 仍六件。
- 跨 feat：semantic intake 入口只有本場 brief + `ask()`；verification 可讀白名單內的 current repo／`docs/specs`。
- decision 固化留給 Stage 2／人確認後。

## 5. Don't

- 傾倒其他 slug 的 1–7 全文、HISTORY 整本、raw CoT、transcript。
- 把 `repo_signals`、`known_facts`、`known_knowledge` 未經 current repo／spec 驗證就寫進 Context。
- Stage 1 做 Decision／OC／ADR／把 Log 升成契約。
- 把 Interview Log 整包 promote 進 `.dev-flow`。
- 只改 html 不改 md（S10：html 要改，先改 md 再重生）。
- 拿掉 `#scan-log` 既有的 `esc()`（不是修 bug，是維持：四欄化後每欄仍逐一 `esc()`）。

## 6. Md 形狀

填既有槽（`_templates/1-discussion.md` 的 `## Context(已知事實)` 與 `## Interview Log(推理鏈外顯)`），不新增章節。

### 6.1 狀態詞彙（三軸，不得互借）

| 軸 | 來源 | 值 | 本檔用法 |
|---|---|---|---|
| 事實狀態 | brief `known_facts[].status`（`truth.LIVE_STATUSES`） | `CANDIDATE`／`VERIFIED`／`STALE`／`CONFLICT`／`UNKNOWN` | 只有 `VERIFIED` 才是 Context candidate |
| 語意狀態 | brief `known_knowledge[].status` | `CONFIRMED`／`CANDIDATE`／`CONFLICT` | 只有 `CONFIRMED` 才是 reasoning signal |
| 檢索狀態 | `ask()` 的 `retrieval_status` | `OK`／`NEEDS_VERIFICATION`／`CONFLICT`／`NO_RELIABLE_MATCH` | 只有 `OK` 的答案可當線索 |

- brief 條目**不帶**檢索狀態；`ask()` 結果**不帶**事實／語意狀態。文件與實作都不得寫「brief 的 `ask()` 狀態」這種混軸句。
- `OPEN` 是 session 狀態（`memory/agentmem/session.py`），不是上表任何一軸，本檔不用。
- 上表任一軸「可當線索」仍不等於 current fact；要進 Context 必須再經 current repo／spec 驗證（§6.2）。

### 6.2 Context（已知事實）

- 每條 = 已驗證斷言 + 出處。出處語法只有一種：`path:L<起>` 或 `path:L<起>-L<迄>`；spec 用 `docs/specs/<domain>.md:L<起>-L<迄>`。不用裸行號、不用 `#anchor`。
- 驗證 = 在 current working tree 讀過該路徑、該行段內容支持斷言。沒讀過的路徑不進 Context。
- brief 的 `known_facts`（`VERIFIED`）與 `known_knowledge`（`CONFIRMED`）只是候選與線索，驗證後才寫入；其他狀態、`repo_signals`、`ask()` 非 `OK` 的答案一律不進 Context，可留 Log 待驗證。
- 同 slug 另開 dev-talk session 覆寫 `1-discussion.md` 時（S8「可改已有的」），S1 必須逐條重讀出處：路徑不存在、行段失效、內容不再支持斷言 → 該條降回 Log 待驗證。此步由 S1 人工執行，**無牙**（掃頁產生器不解析產品 repo 的檔案系統）。

### 6.3 Interview Log（推理鏈外顯）

grammar 從單行 `|` 改為巢狀四段。理由：shell pipe、TypeScript union、markdown 表格都含 `|`，單行 split 會壞。

```text
- Q:為什麼這裡要讀 memory？
  - 事實:scripts/foo.py:L31-L44（Context 同批）
  - 推理:signal 不是證據，仍需讀 current repo 驗證。
  - 結論:已解 Stage 1 把驗證後內容寫進 Context。
```

- 一條 = 一個 `- Q:` 頂層項 + 三個縮排子項，標籤固定為 `事實`／`推理`／`結論`（`事實依據` 不接受，S8 與 SKILL.md 骨架同步改字）。四段齊才算一條。
- 子項縮排剛好 2 個空白（不是 tab、不是 4 空白）。模板註解與掃頁 `parse_log` 都寫死這條。
- 事實欄只放 Context 已列出處（同一路徑，行段可更窄）；不另造無出處斷言。
- 結論欄以 Open Questions 三態之一開頭：`已解`／`假設`／`移交`，後接一句結論。不借用記憶模組的 `CONFIRMED`／`VERIFIED`，也不借用檢索狀態。不得為了填滿四段硬下結論，寫 `假設` 或 `移交` 即可。
- 高影響（難逆轉／意外／真權衡）在 Q 前標 ⚠️。推理是可核對的短句，不是 raw CoT。
- 舊單行 `Q:… | 事實:… | …` 格式：掃頁產生器直接 `ValueError`，訊息指向本節 grammar（fail-closed，與現有「抽不到 Interview Log／問答」同風格）。
- Log 為空：現有「從 Open Questions 合成 `Q:… 著落:…`」的退路**移除**，改為 `ValueError("抽不到 Interview Log")`。理由：SKILL.md 十節骨架不准刪，S8 ④ 已要求每條齊段，空 Log 本來就不該過 S8。
- 上限從「八行」改為「八條」。

## 7. Html 形狀（只動掃頁 `#scan-log`）

S10 六件不變：摘要卡／現況圖／人表／題目／驗收表／問答摘要。

`#scan-log` 仍是預設摺著的 `<details>`，`<summary>` 仍含「問答摘要」（`check-devtalk-fig-graph.sh` 只查這兩件），內文從逐條 `<p>` 改為一張四欄 `<table>`（Q／事實／推理／結論），外包既有 `.tablewrap`。

- 窄 viewport 靠 `.tablewrap{overflow-x:auto}` 橫向捲動。**不做堆疊**：產生器不輸出 CSS，堆疊得改 html-shell，本檔不動殼。
- 每欄內容逐一 `esc()`，維持現狀。
- ⚠️ 以純文字前綴呈現，不加 class。
- Constraints／詞條仍不佔第一屏。

**不動**：`scripts/build-stage1-html.py`、審頁 `#scan-sum`／`#scan-now`／`#scan-people`、`skills/dev-talk/html-shell.html`、gate-twin STAGES、`check-devtalk-fig-graph.sh` 既有規則。

## 8. 記憶規則

- 跨功能 semantic intake 入口只有本場 brief + `ask()`。verification 讀白名單（記憶入口、`docs/specs/`、原始碼），**不讀**其他 `docs/dev/<slug>/`，也不把 `docs/dev` 加進讀取白名單。
- 推理留在本 slug 的 Interview Log；不把 Log 整包 promote 進 `.dev-flow`。transcript 只住本機。
- 語意候選仍走 propose → 人 confirm → end 才固化。Log 結論的 `已解` 不等於記憶的 `CONFIRMED`。

## 9. 範圍：要改與不改的檔

「不升 plugin」= 不 bump `.claude-plugin/plugin.json` 版本，不改 graph、不加節點。節點與模板的**文字**可改。

| 檔 | 改什麼 |
|---|---|
| `scripts/build-scan-html.py` | `parse_log` 改巢狀四段解析；四段檢查與事實欄路徑檢查（§10）；`#scan-log` 四欄表；移除 OQ 合成退路 |
| `scripts/fixtures/devtalk-html-scan/good/1-discussion.md` | Log 改巢狀四段，事實欄引用 Context 路徑 |
| `scripts/fixtures/devtalk-html-scan/good/1-discussion.html` | 重生 |
| `_templates/1-discussion.md` | Context 註解加出處語法；Log 範例行改巢狀 |
| `skills/dev-talk/SKILL.md` | 第 148 行骨架註解「Q → 事實依據 → 推理 → 結論」改四段標籤；第 101 行 S1 入口摘要加「消化 brief」 |
| `skills/dev-talk/nodes/N1-start.md` | brief 用途從「open questions 是 N3 起點」擴為「全部欄位交 S1 消化」 |
| `skills/dev-talk/nodes/S1-survey.md` | 加：逐項消化 brief；Context 每條帶出處；重跑同 slug 時重驗出處 |
| `skills/dev-talk/nodes/S8-review.md` | 第④條「三段」改「四段」，加「結論以三態開頭」「事實欄 ⊆ Context」 |
| `guides/guide-dev-talk.html` | 隨 SKILL.md 第 101／148 行同步（`check-devtalk-guide-sync.sh` 逐字守衛會紅） |
| `example/contract-expiry-reminder/1-discussion.md` | Log 改巢狀四段（現為 `explore:`／`grill-with-docs:` 標籤列，與本檔不符） |

## 10. 牙與判準

**牙**（住 `scripts/build-scan-html.py`，fail-closed）：

1. 每條 Log 四段齊，標籤為 `事實`／`推理`／`結論`，否則 `ValueError`。
2. 結論欄以 `已解`／`假設`／`移交` 開頭，否則 `ValueError`。
3. 事實欄每個 `path`（去行段）必須以字串包含出現在 Context 節文字中，否則 `ValueError`。產生器不讀產品檔案系統。
4. 舊單行 `|` 格式、空 Log → `ValueError`。

**無牙、靠 S8 人工**：出處是否真的支持斷言；重跑時的 stale 重驗；brief 是否真被消化。

**後續實作 PR 過關**＝下列全真（本檔本身不算過關）：

1. §9 表列檔全部改到，`check-devtalk-fig-graph.sh`／`check-devtalk-guide-sync.sh` 綠。
2. 牙 1–4 有對應 fixture（good 一份、每條牙一份 bad）。
3. 掃頁 `#scan-log` 為四欄表，`<details>` 預設摺著、`<summary>` 含「問答摘要」。
4. S10 仍六件；審頁不變；html-shell 不變。
5. 版本零 bump。

## 11. Five-review table

| # | 焦點 | VERDICT | ONE_LINE |
|---|---|---|---|
| A | intake | NARROW | 強制消化 brief 四欄位；不傾倒他 slug；Stage 2 決策鏈不進 S1 hop |
| B | loci | NARROW | 槽位＝Context + Interview Log；Approaches／Decision 留 Stage 2 |
| C | memory | NARROW | 三軸狀態不互借；memory 是 signal，current fact 需 repo／spec 再驗證 |
| D | adversarial | NARROW | 不新 section／gate／hop；不 raw CoT；不只改 html；不動殼 |
| E | delivery | INCLUDE | 巢狀四段 grammar；牙 1–4 進產生器；§9 檔清單全改；版本零 bump |

## 12. 已拍板、可翻的選項

以下由本次修訂拍板，翻任一項請同步改對應章節：

- 巢狀四段取代單行 `|`（§6.3）。翻回單行需另定 escape 規則。
- 出處語法只留 `path:L<起>-L<迄>`（§6.2）。
- 結論三態沿用 Open Questions（§6.3）。
- 窄 viewport 橫向捲動、不堆疊、不動殼（§7）。
- 空 Log 與舊格式 fail-closed、移除 OQ 合成退路（§6.3）。
- 「不升 plugin」= 不 bump 版本，節點文字可改（§9）。
- stale 重驗無牙（§6.2）。
