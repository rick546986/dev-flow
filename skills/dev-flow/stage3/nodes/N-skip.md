# N-skip — 全未命中,或命中但人不要求 Demo

## 進條件

N1 九條全未命中;**或**任一命中但人已親填 `not requested`(人要求才 Demo)。
若有命中且人要求 Demo → 本節點不是入口,走 `fork_required`。

## 讀什麼

N1 判定結果(九條皆未勾)。不重抄九條條文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/3-prototype.md`,不另存。禁止第二份 `3-prototype*.md`。
不建 `3-prototype.html`。`write_mode: overwrite`。
本機游標只留在 `.devstage3-cursor.json`,不進 Git。不改 `.dev-flow`。

## 做什麼

寫最小 `3-prototype.md`:frontmatter `status: approved` + `## Stage 3 觸發判定`
九條(全未勾;或如實勾命中)。有命中時原樣帶進人親填的
`- Demo request: not requested by human:<姓名> @ <日期>` 行 —— 那一行是人的,Agent 不得代填。不建 html。
Owner Call 跳過路徑仍可用(2-decision 該行同時含「Stage 3」與「跳過」)。Agent 不得代決。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage3-graph.sh --write-cursor N-skip`。

## 完成條件

該 slug 有一份最小 `3-prototype.md`(status approved + 九條未勾),
沒有 `3-prototype.html`。游標在 N-skip。

## 下一跳

無
