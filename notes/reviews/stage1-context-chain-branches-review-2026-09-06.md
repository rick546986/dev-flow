# Stage 1 Context Chain — 三分支實作審查

> **已於 #136／#134 解決（2026-09-06）。** 本檔是第一輪審查，P0-1～P1-4 與 Merge gate
> 所列條件已由 brief 第三版（#136）與 `parser-7d32` 實作（#134）落地。
> 後續收尾見 [round3](stage1-context-chain-branches-review-round3-2026-09-06.md)
> （含第二、三輪對照）。本檔保留作歷史，不再當阻擋項。

日期：2026-09-06

審查分支：

1. `cursor/stage1-context-chain-0ded`
2. `cursor/stage1-context-chain-parser-7d32`
3. `cursor/stage1-context-chain-skills-7f26`

Base：`main@0c230b9d9a6b86addae74eaa58ff6b11bc47db04`

## Verdict

**目前不要直接 merge 三支中的任何一支。**

三支都抓到正確方向：Context 要有 evidence、Interview Log 改巢狀四段、`#scan-log` 四欄、S10／review page 不動。但三支都在 implementation branch 內重新改寫 `notes/design/stage1-context-chain.md` 的已定義語意，且 parser 嚴格度不一致。

若要選一支作為收斂底稿：**`cursor/stage1-context-chain-parser-7d32` 最接近可 merge**。它對空 Log、legacy pipe、缺欄、duplicate、無 citation、path 不在 Context 的 fail-closed 最完整；建議以它為 base 修正以下 P0/P1，再跑完整 checks。

---

## P0 — 必修

### P0-1 Design source 被 implementation branch 反向改寫

`main` 的 design brief 已定義：

- Interview Log conclusion 至少允許 `CONFIRMED`／`NEEDS_VERIFICATION`／`OPEN`。
- narrow viewport 可四段堆疊。
- design note 是本輪實作的 source brief。

三個 implementation branch 卻把 brief 改成：

- conclusion 必須 `已解`／`假設`／`移交`。
- narrow viewport 改成 table horizontal scroll、不做 stack。

這不是單純 implementation detail，而是改 acceptance semantics。尤其 `OPEN / NEEDS_VERIFICATION` 的目的，是避免 agent 為了 schema 強迫下結論；把它改回 Open Questions 的 `已解／假設／移交`，需要先由 design 層明確決定，而不應由 implementation branch 靜默覆寫。

**修正：**

1. implementation branch 不應直接把已核定 brief 改成另一套語意。
2. 先決定 conclusion vocabulary：
   - 若保留 design brief：parser／template／S8／fixtures 全部接受 `CONFIRMED`／`NEEDS_VERIFICATION`／`OPEN`（必要時另處理 `CONFLICT`）。
   - 若真的要統一成 `已解`／`假設`／`移交`：先單獨更新 main design note、寫清楚 mapping 與 unresolved promotion rule，再讓 implementation 跟進。
3. responsive behavior 同理：若不想改 `html-shell`，應先把「horizontal scroll 是否足以符合 narrow 可讀性」回寫 design decision，而不是 implementation branch 自行降低 acceptance criterion。

### P0-2 `cursor/stage1-context-chain-0ded` 的 parser 仍可讓無 citation 的 Fact 通過

`parse_log()` 只對 `LOG_CITE_RE.finditer(current["事實"])` 找到的 citation 做 Context membership check；如果 Fact 完全沒有 `path:Lx`，loop 是 0 次，該 entry 仍會通過。

這違反「Fact 必須引用 Context 已列 evidence」。

**修正：**先抽 citations；若為空直接 `ValueError`。另外 duplicate `事實／推理／結論` 目前會被後值覆寫，也應 fail-closed。

### P0-3 `cursor/stage1-context-chain-skills-7f26` 同樣允許無 citation Fact

`_fact_paths()` 回傳空 list 時，後續 `for path in ...` 不會執行，因此沒有 citation 的 Fact 可通過。

**修正：**`paths = _fact_paths(...)`; `if not paths: raise ValueError(...)`。

`cursor/stage1-context-chain-parser-7d32` 在這點較完整：它明確要求至少一個 citation，建議保留這個行為。

---

## P1 — merge 前建議修

### P1-1 不要只驗證「path 字串存在 Context」，至少要驗證完整 citation grammar

目前 parser branch 的牙 3 本質是：Fact 抽出 `path` 後，檢查該 path 是否為 Context text substring。這可以阻止完全不同檔案，但仍可能讓：

- Context：`scripts/foo.py:L10-L20`
- Fact：`scripts/foo.py:L999-L1000`

通過，因為只比 `scripts/foo.py`。

如果 design 的要求是「Fact 使用 Context 同一批引用，行段可更窄」，那 parser 至少應解析 Context citations，並檢查 Fact citation 的 line interval 是否落在 Context citation interval 內；不能只比 path。

**建議：**建立 citation parser 回傳 `(path, start, end)`，Context 先建 evidence set；Fact citation 必須 path 相同且 range 被 Context range 包含。這仍不需要讀產品 filesystem。

### P1-2 增加 adversarial fixtures

目前 bad fixtures 已涵蓋主要四牙，但建議再補：

- Fact 完全沒有 citation。
- 同一 entry duplicate `事實`。
- Context 有相同 path、Fact 使用 Context 範圍外的 line range。
- citation 被 backticks 包住。
- Fact 文字含 shell pipe `|`、TypeScript `string | null`，應正常通過 nested parser。
- HTML payload：`<script>`、`<img onerror=...>` 出現在 Q／Fact／Reasoning／Conclusion，輸出必須 escaped。
- `⚠️` Q。
- 第 9 條 Log 的 cap 行為是否是刻意截斷；若八條是契約上限，建議超過 8 fail-closed，而不是 silently truncate，避免 reasoning 被無聲丟掉。

### P1-3 `LOG_CAP = 8` / `entries[:8]` 的 silent truncation 要改

三支都傾向只 render 前八條。若 Stage 1 規則是「上限八條」，第九條出現代表輸入不符合規格；silent truncate 會讓 md 有 reasoning、HTML 卻看不到，破壞 auditability。

**修正：**`if len(entries) > 8: raise ValueError("Interview Log 上限八條")`，不要切片吞掉。

### P1-4 parser 不應忽略 Interview Log 內未知的非空普通文字

部分版本遇到不是 Q、不是 child、也不是特定 bullet 的行會直接略過。對 audit grammar 建議 fail-closed：Interview Log section 中除了允許的 comment／blank／fence boundary 外，未知內容應報錯，否則 typo 可能被靜默吞掉。

---

## 分支比較

| 分支 | 評價 | 主要問題 |
|---|---|---|
| `cursor/stage1-context-chain-0ded` | **不建議當底稿** | 無 citation 可過、duplicate field 可覆寫；parser 牙較弱 |
| `cursor/stage1-context-chain-parser-7d32` | **最佳底稿** | 主要四牙最完整；仍需解決 design semantic drift、citation range、8 條 silent truncate |
| `cursor/stage1-context-chain-skills-7f26` | **skill 文案較完整，但 parser 次於 parser branch** | S1 evidence promotion 說明最好；但無 citation Fact 可過，且同樣有 semantic drift |

## 建議收斂方式

不要三支直接互 merge。建議：

1. 以 `cursor/stage1-context-chain-parser-7d32` 作 implementation base。
2. 從 `cursor/stage1-context-chain-skills-7f26` 挑 S1/N1/S8 中較完整的 evidence-promotion 說明合入。
3. 不採 `0ded` 較弱的 `parse_log()`。
4. 先解 P0-1：讓 implementation 與 main design brief 的 conclusion vocabulary / responsive acceptance 重新一致。
5. 補 P0-2/P0-3 類型的「citation 必填」牙，並升級成 citation range containment。
6. >8 entries 改 fail-closed。
7. 跑所有 Stage 1 / guide-sync / graph / fixture checks，再做一次 merge review。

## Merge gate

在以下條件全滿足前維持 **CHANGES REQUIRED**：

- design source 與 implementation semantics 一致；
- Fact 無 citation 必 fail；
- Fact citation 必屬於 Context evidence range；
- duplicate／missing／legacy pipe／empty Log 必 fail；
- >8 不 silent truncate；
- HTML 四欄所有內容 escaped；
- S10 六件不變；
- review page / gate / plugin version 不變；
- fixtures 與既有 checks 全綠。
