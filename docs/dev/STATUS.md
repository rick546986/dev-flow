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

> 2026-08-16 守衛覆蓋輪:上表原 5 條中 3 條已做(引擎 fence 遮蔽 → feature
> `engine-fence-masking` 走 fast lane 全程武裝完成,G3 PASS;devtalk-guard obs 事件;
> postbash 圍欄③收緊),詳見 `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A8。

> 2026-08-17 對稱守衛輪:X-1~X-7 與兩件記帳問題已處置,詳見
> `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A9。以下是該輪明文列入
> Backlog、裁決「暫不補」的兩個已知邊界。

| 級 | 一句 | 來源 |
|---|---|---|
| B | 第二個範例 feature,破「唯一範例自證循環」= 4cap O-3。本輪不做的理由更新:`docs/dev/engine-fence-masking/` 已是母版第一份真實走完 fast lane 的流程紀錄,日後要 example 可從它清洗,不必現編 | `docs/dev/4cap-remediation/4cap-audit-fixes-2026-08.md` O-3 裁決 |
| C | 審查圍欄的寫入白名單(7-review*/evidence/)在 guard 側有、**postbash 偵測網側沒有** —— review 期間產 7-review.md 會被當 scope 外改動(實測撞到,已依 L1 allow 處置;修法=postbash 比照 guard 豁免,配 selftest) | `docs/dev/engine-fence-masking/7-review.md` D-4 |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred;投資未定,防守清單 #3 同邏輯) | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |
| C | tier-exempt 豁免卡是 repo 級非 run 級,`devflow-exec.sh stop` 不清卡 —— 未消耗的豁免可能跨 run 存活 | `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A9 Known Limits |
| C | MT-2:`bad-skip-level` 缺一條比照 MT-1 的 real-mode 外部案例(目前 skip-level 只在自測模式內驗) | `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A9 Known Limits |
