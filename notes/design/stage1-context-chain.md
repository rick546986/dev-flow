# Stage 1：相關脈絡進場＋推理鏈路外顯（merged brief）

> 五份獨立審查共識 = **NARROW**。填既有 Context + Interview Log 槽。
> 審頁正本仍是 `notes/design/stage1-review-ui-contract.md`。本檔不動審頁。

## 1. Status

本檔是 **design note 正本**。後續實作另開 PR。本檔不升 plugin、不升契約、不加 hop／gate。

## 2. Problem

S1 已有 Context（已知事實）＋ Interview Log（`Q | 事實 | 推理 | 結論`），但相關脈絡常沒吃 talk-start brief：brief 當裝飾，已核事實不帶檔:行。掃頁 `build-scan-html.py` 把 Log 壓成 `#scan-log` 短 `<p>`，審的人看不到四欄鏈路。

## 3. Thesis

**Stage 1 = 強制消化 talk-start brief／`ask()` 進 Context（可引用路徑）＋ Interview Log 四段外顯。** 跨功能複利只走已確認的 `.dev-flow` 語意，不傾倒他 slug 的 1–7。Stage 2 的 Approaches／Decision／OC／ADR 不進本 hop。

## 4. Do（實作時）

- N1／S1 **必須消化** talk-start brief（不得當裝飾）。
- Context：已核事實 + `docs/specs` + `檔:行`。可用 brief 的 `repo_signals` 路徑當線索；讀正文仍守白名單。
- Interview Log：`Q | 事實 | 推理 | 結論`。事實欄引用 Context 路徑。高影響可 ⚠️。
- 掃頁 `#scan-log` 四欄結構渲染。S10 仍六件。
- 跨 feat：只經 `.dev-flow` 已確認語意 + `ask()`。decision 固化留給 Stage 2／人確認後。

## 5. Don't

- 傾倒其他 slug 的 1–7 全文、HISTORY 整本、raw CoT、transcript。
- Stage 1 做 Decision／OC／ADR／把 Log 升成契約。
- 新 hop／新 gate／審頁解鎖／第 7 掃頁格。
- 把 Interview Log 整包 promote 進 `.dev-flow`。
- 只改 html 不改 md。

## 6. Md 形狀

填既有槽，不新增章節。

**Context（已知事實）**

- 每條已核事實帶出處：`docs/specs/<domain>.md` 與／或 `path:line`。
- brief 的 `known_facts`／`known_knowledge`（`ask()` 狀態 `OK` 者）寫進來。
- `repo_signals` 只當線索：讀過且白名單內才引用；沒讀過的路徑不進 Context。

**Interview Log（推理鏈外顯）**

```
- Q:… | 事實:<Context 同批路徑> | 推理:… | 結論:…
```

- 四段齊才算一條。事實欄引用 Context 已列路徑，不另造無出處斷言。
- 高影響（難逆轉／意外／真權衡）標 ⚠️。推理是可核對的短句，不是 raw CoT。

## 7. Html 形狀（只動掃頁 `#scan-log`）

S10 六件不變：摘要卡／現況圖／人表／題目／驗收表／問答摘要。

`#scan-log` 從壓扁 `<p>` 改成四欄鏈路（`Q | 事實 | 推理 | 結論`），與 md 同形。不是新格、不是第七件。Constraints／詞條仍不佔第一屏。

**不動**：`scripts/build-stage1-html.py`、審頁 `#scan-sum`／`#scan-now`／`#scan-people`、html-shell、gate-twin STAGES。

## 8. 記憶規則

- S1 只吃本場 talk-start brief + `dev-memory.py ask()`。推理留在本 slug 的 Interview Log。
- 跨 feat 複利：只讀 `.dev-flow` **已確認**語意（`ask()` 狀態 `OK`）。`NEEDS_VERIFICATION`／`CONFLICT`／`NO_RELIABLE_MATCH` 不當現況。
- **不讀** 其他 `docs/dev/<slug>/`。不把 Log 整包 promote 進 `.dev-flow`。transcript 只住本機。
- 語意候選仍走 propose → 人 confirm → end 才固化。Stage 1 不代 Stage 2 做 decision 固化。

## 9. 契約／版本

零 bump。不加 G0。不放寬 `docs/dev/**` 白名單。不加 hop／gate。本檔不是契約。

## 10. Later PR success criteria

後續實作 PR 過關＝下列全真（本檔本身不算過關）：

1. Context 在 md 有 `檔:行`／specs 引用。
2. Interview Log 事實欄用**同一批**引用。
3. 掃頁 `#scan-log` 渲染四欄鏈路，不壓成短段落。
4. S10 仍六件。
5. 審頁不變。
6. 不升 plugin／契約。

## 11. Five-review table

| # | 焦點 | VERDICT | ONE_LINE |
|---|---|---|---|
| A | intake | NARROW | 強制消化 talk-start brief；不傾倒他 slug；Stage 2 決策鏈不進 S1 hop |
| B | loci | NARROW | 槽位＝Context + Interview Log；Approaches／Decision 留 Stage 2 |
| C | memory | NARROW | S1 只 brief + `ask()`；推理留本 slug；跨 feat 只經已確認 `.dev-flow` |
| D | adversarial | NARROW | 不新 section／gate／hop；不 raw CoT；不只改 html；填既有槽 |
| E | delivery | INCLUDE | 後續 PR 必帶：md 引用＝事實欄；`#scan-log` 四欄；S10 六件；審頁／版本不動 |
