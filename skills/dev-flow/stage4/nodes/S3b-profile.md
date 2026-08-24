# S3b-profile — Verification Profile 與 Design Boundary

## 進條件

S3a-close 完成:四小節齊。游標在 S3a-close。
Out of Scope 還沒定就填 Negative Constraints = 兩邊會對不上,退回 S3a。

## 讀什麼

已落檔的 R／S 與四小節。lane 規則、Risk 判準、Failure Model 必填條件、
Design Boundary Contract 的十一條觸發條件,正本都在 `_templates/4-spec.md`
該節頂註;語意詳解在 `notes/design/design-boundary-contract.md`。
本檔不抄乘客步原文。`graph.yaml` 是下一跳正本。

## 寫哪裡

只覆寫 `docs/dev/<slug>/4-spec.md` 的 Verification Profile 與
Design Boundary Contract 兩節,不另存。禁止第二份 `4-spec*.md`。
`write_mode: overwrite`。本機游標不進 Git。

## 做什麼

同步填兩節:Profile 的 `lane:` 依判準決定(不由指示決定,偏離要在本節明記理由),
Risk: high 時 Failure Model 表必填,Reliability triage 三問兩 lane 都要答;
Design Boundary Contract 觸發條件全未命中才可 `n-a` 附具體理由,fast lane 不豁免。
跑 `${DEVFLOW_ROOT}/scripts/check-devstage4-graph.sh --write-cursor S3b-profile`。

## 完成條件

Verification Profile 填畢(依 lane)、Reliability triage 三問皆有答,
Design Boundary Contract 有結論(applicable 全填,或 n-a 附理由)。
只有一份 `4-spec.md`。本機游標在 S3b-profile。

## 下一跳

S3c-stage3
