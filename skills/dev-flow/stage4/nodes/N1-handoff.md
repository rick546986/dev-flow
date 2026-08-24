# N1-handoff — 接手盤點

## 進條件

`docs/dev/<slug>/2-decision.md` 在,且 frontmatter status=approved(G1 過)。
缺 → 本節點不是入口,退回第 2 站。
第 3 站若必要(`3-prototype.md`「Stage 3 觸發判定」有命中)卻缺 approved 的
`3-prototype.md`、又無 skip OC(`2-decision.md` 同一行同時寫「Stage 3」與「跳過」)
→ 本節點不是入口,退回第 3 站。不要寫 `4-spec.md`。

## 讀什麼

只讀 `1-discussion.md`(驗收雛形／Open Questions／Real-world Context)與
`2-decision.md`(Decision／Scope／Success Criteria)。對話不是契約。
乘客清單正本是相對 DEVFLOW_ROOT 的 `_templates/4-spec.md` 頂註 0–6,本檔不重抄步原文。
`graph.yaml` 是下一跳正本。

## 寫哪裡

不寫 `4-spec.md`。禁止第二份 `4-spec*.md`。
本機游標(現在節點)只留在 `.devstage4-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

核前站:G1 是否過、第 3 站 findings 是否已回寫且 frontmatter 收尾,再清點雙源
(驗收雛形 N 條、living spec 受影響條文)給人確認。完成 = 前站核對過。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor N1-handoff`。

## 完成條件

G1 過;第 3 站若必要則已 approved 或有 skip OC。本機游標在 N1-handoff。

## 下一跳

S1-requirements
