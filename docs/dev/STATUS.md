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
> `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A9。
>
> 2026-08-17 清空輪(同日第二輪):原 Backlog 5 條處置 3 條 —— postbash 審查
> 白名單(D-4)已修(第 6 型實例,postbash 比照 guard 豁免 7-review*/evidence/,
> selftest +3)、tier-exempt 改 run 級(stop 清未消耗卡、留已消耗卡當留痕,
> selftest +3)、MT-2 real-mode 案例已補(test-architecture-guards 比照 MT-1)。
> 詳見 `docs/dev/b8-gate-twin-review-ui/7-review.md` 附錄 A10。以下是仍留的兩條
> 與各自「本輪不做」的理由。

| 級 | 一句 | 來源 |
|---|---|---|
| B | 第二個範例 feature,破「唯一範例自證循環」= 4cap O-3。2026-08-17 清空輪裁決仍不做:清洗 `docs/dev/engine-fence-masking/`(母版第一份真實 fast lane 紀錄)成第二範例是 feature 級工程 —— 要讓所有掃 example/ 的機械檢查認得 fast lane 範例、且範例是機械檢查的地基,半吊子的第二範例比沒有更糟(假信心)。素材是 append-only 的歷史檔,不會腐化,無急迫性衰減;應開專屬 feature 走完整 G1-G3 來做 | `docs/dev/4cap-remediation/4cap-audit-fixes-2026-08.md` O-3 裁決 |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred)。2026-08-17 清空輪裁決仍不做:投資未定且**零採用現場疼痛訊號**(G1/G2/G3 全是現場真踩到的,這兩件沒有);等有採用專案真的要 SDC 級指引再立案,不為清空而硬做 | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |
