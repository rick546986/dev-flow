# 第 2 站審頁(分組卡／Decision 後直式圖)

> 第 2 站給人看的**審頁**版面正本。G1 twin 仍是五格審查介面
> (`scripts/build-gate-twin.py` STAGES 的 2-decision),不是這份。
> 本檔只鎖審頁樣子。直式步驟方塊母版見
> `notes/design/vbox-fig-contract.md`(不改那份的生命週期四格規則)。
> 產檔器:`scripts/build-stage2-html.py`。牙:`scripts/check-stage2-card-contract.sh`。
> 不進 `build-gate-twin.py` STAGES、不包 html-shell。

## 何時用

寫或改第 2 站給人看的審頁時。chrome 跟第 5／6／7 站同一套 token,
不要另發明殼、不要另發明 class 名。

## 版面鎖死(已拍板)

下列六條是鎖死,不是口味、不是選配。產檔器吃 md 的 Approaches／Decision／
方案架構圖:`scripts/build-stage2-html.py` 吐分組卡 + Decision 後直式 SVG。
授權 `--action`。不包 markdown-it + html-shell。
寫法落點:`_templates/2-decision.md`(本檔是正本,不另開家族)。

1. **分組卡**:方案按決策點收進分組卡(每決策點一個 `.r-block`,內 A/B/C 卡)。
   Approaches 是表格也要吃,不要只認 `#### A`。不要一坨傾倒。四組不得皆 0 張卡。
2. **Decision 置頂後直式 SVG**:順序是 Decision 置頂 → 直式 SVG 方塊,置中
   `max-width:360px` → 每決策點卡。不是 mermaid、不是橫 ASCII、不是 ASCII `<pre>` 當圖。
3. **背景摺疊**:既有脈絡／Rationale／風險等背景進 `<details>`,預設收合。
4. **chrome 同一套**:必須點名 `--ground`、`--panel`、`--accent`,加
   `--ok-soft`／`--bad-soft`;`.masthead` `.dash` `.cell` `.r-block`。
5. **不是舊主產檔器樣**:不要「勾選提示」、不要「你要審什麼」、
   不要 Rejected 釘頂那版(那是 gate-twin 卡,不是這份審頁)。
6. **不是 twin**:不准把第 2 站審頁塞進 `build-gate-twin.py` STAGES。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| G1 twin 五格／勾選卡 | `_templates/2-decision.md` 頂註 + `scripts/build-gate-twin.py` |
| 直式步驟方塊母版 | `notes/design/vbox-fig-contract.md` |
| 第 1 站三框現況圖 | `notes/design/stage1-review-ui-contract.md` |
| Human verdict 寫入 | `notes/design/gate-verdict-write.md` |

不改 twin、不改 gate-twin STAGES、不改 `build-stage6-html.py`。
