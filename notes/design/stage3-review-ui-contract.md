# 第 3 站審頁(觸發判定／Demo／回寫)

> 第 3 站給人看的**審頁**版面正本。本站選配:feat 沒有 `3-prototype.md`
> 時產檔器 **n-a／跳過**,不得當硬缺 `exit 1`。有檔才印頁。
> 產檔器:`scripts/build-stage3-html.py`。牙:`scripts/check-stage3-proto-contract.sh`。
> 不進 `build-gate-twin.py` STAGES、不包 html-shell。
> 不要把 html-shell 舊樣當正式。第 4 站那種卡殼優先;本站至少自足單檔、深淺色。

## 何時用

寫或改第 3 站給人看的審頁時。chrome 跟第 2／4／5／7 站同一套 token,
不要另發明殼。沒有 `3-prototype.md` 就不要建頁。

## 版面鎖死(已拍板)

下列六條是鎖死,不是口味、不是選配。產檔器吃 md 的觸發判定／Demo Script／
Result／Verdict:`scripts/build-stage3-html.py` 吐觸發判定 + Demo + 答案回寫
2-decision。授權 `--action`。不包 markdown-it + html-shell。
寫法落點:`_templates/3-prototype.md`(本檔是正本,不另開家族)。

1. **觸發判定**:把「Stage 3 觸發判定」九條印出來,命中數上頂區。
2. **Demo**:Demo Script 各 Scenario 成卡,不是把 md 直轉成長文。
3. **答案回寫 2-decision**:Result／Verdict 必須點名回寫 `2-decision`,
   頁上看得見寫回哪一條。
4. **選配 n-a**:給的 feat 沒有 `3-prototype.md`(檔不存在或目錄裡沒這檔)
   → 印 `n-a`、exit 0、不寫 html。不是硬缺、不是 usage error。
5. **chrome／自足單檔**:必須點名 `--ground`、`--panel`、`--accent`;
   `.masthead` `.dash` `.r-block`。深淺色(`prefers-color-scheme:dark`)。
   自足單檔,無外部資源。不是 html-shell 長文直轉。
6. **不是 twin**:不准把第 3 站審頁塞進 `build-gate-twin.py` STAGES。
   圖若有,直式 SVG 置中 `max-width:360px`,不是 mermaid、不是橫 ASCII。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| 全未命中、不建 3-prototype | `skills/dev-flow/stage3/nodes/N-skip.md` |
| 回寫 2-decision 正文 | `_templates/3-prototype.md` 頂註步 3 + S3-writeback |
| G1／G2／G3 五格卡 | `scripts/build-gate-twin.py` |
| 第 4 站 R/S 卡／生命週期 | `notes/design/stage4-review-ui-contract.md` |
| html-shell 舊樣 | `_templates/html-shell.html`(不是本站正式審頁) |

不改 twin、不改 gate-twin STAGES、不改已合的 1／2／5／6／7 產器。
