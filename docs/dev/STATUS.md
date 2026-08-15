# docs/dev — 改版流程索引

> 本檔追蹤**方法論母版自身**的改版工作(非採用專案的 feature)。兩表:
> Active(進行中)/ Backlog(待處理,多數來自採用現場回饋)。
>
> **做完的不留在本檔** —— 一律追加到 `HISTORY.md`(只增不改的索引,最新在最下面),
> 值得長期保存的決策另立 `docs/adr/NNNN-slug.md`。這樣本檔永遠只回答一個問題:
> **現在誰在做什麼、還有什麼沒做。**

## Active

目前無進行中的改版軌。

## 已完成

見 `HISTORY.md`(只增不改,最新在最下面)。**不要直接編輯那個檔**,用:

```bash
scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
```

理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的蓋掉且不報錯。

## Backlog

> 2026-08-15 待辦清空輪:原列的 14 條(A-1~A-6/A-11/A-12/B-1~B-6)已**全數處置**,
> 逐條裁決與修法見 `notes/adoption-findings-2026-08-04.md` 各節「已採用的修法(2026-08-15)」;
> 4cap 的 O-1~O-8 與 §7 六件亦已裁決結案(`docs/dev/4cap-remediation/4cap-audit-fixes-2026-08.md`)。
> 以下是該輪**產生或收攏**的剩餘項。

| 級 | 一句 | 來源 |
|---|---|---|
| B | Boundaries 裡的 fenced `## T-xx` 會被 Stage 6 引擎長成幽靈任務 —— 引擎的 `parse_5_tasks` 不遮蔽 code fence(twin 已加警告現形;修引擎屬 live runtime 改動,與 contract_ref/selftest 要一起動)(`hooks/devflow-lib.py::parse_5_tasks`) | `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A7 H1 |
| B | 第二個範例 feature(fast lane 或合法跳過 Stage 3),破「唯一範例自證循環」= 4cap O-3 | `docs/dev/4cap-remediation/4cap-audit-fixes-2026-08.md` O-3 裁決 |
| C | `devtalk-guard.sh` 的 deny 沒寫 obs 事件,也無 selftest 覆蓋(observability manifest 第 4 項僅部分落地) | `notes/change-manifests/observability.md` 2026-08-15 核對註 |
| C | 審查圍欄(圍欄③)期間 postbash 的 `allowed_prefix` 豁免未收緊 —— shell 改動 5-tasks/6-notes 仍走既有豁免 | `notes/adoption-findings-2026-08-04.md` A-11 已採用的修法 |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred) | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |
