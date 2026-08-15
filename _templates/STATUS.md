# 進行中變更索引

> 用途:並行開發時的單頁看板。每 feature 一列;階段推進、gate 過都要更新。
> **本檔只回答「現在誰在做什麼、做到哪一站」** —— 做完的不留在這裡。
> 排序:進行中在上。

## Active

| Feature | Lane | Stage | Owner | Gates | Updated |
|---|---|---|---|---|---|
| [<slug>](./<slug>/) | full | 1-discussion | <name> | G1⬜ G2⬜ G3⬜ | YYYY-MM-DD |

## Known Debt(選配)
<!-- 跨 feature 的技術債看板,不對應單一 feature 的 STATUS 列。逐條:# | 內容 | 來源 | 追蹤位置。
     內容可含:D-n 技術債(park 未修的 Deviation)、Failure Model 未覆蓋的 failure mode、
     breaker park 項(7-review 重驗迴圈第 3 輪仍 REQUEST_CHANGES 時的裁決表匯入處)。
     不採用整節留白;已解除的用 ~~刪除線~~ 保留,不刪列。 -->
| # | 內容 | 來源(feature/slug) | 追蹤位置 |
|---|---|---|---|

## 已完成

見 `HISTORY.md`(只增不改的索引,最新在最下面);值得長期保存的決策另立
`docs/adr/NNNN-slug.md`。feature 資料夾 `docs/dev/<slug>/` 一律留著可考古。

**不要直接編輯 `HISTORY.md`**,用唯一寫入口:

```bash
docs/dev/tools/history-append.sh --slug <代號> --what <做了什麼> \
                                 --why <為什麼> --where <落在哪>
```

理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的整段蓋掉,
而且不會報錯。上面那支腳本有目錄鎖 + 重試,並且只做追加。
