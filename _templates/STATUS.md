# 進行中變更索引

> 用途:並行開發時的單頁看板。每 feature 一列;階段推進、gate 過都要更新。
> **本檔只回答「現在誰在做什麼、做到哪一站」** —— 做完的不留在這裡。
> 排序:進行中在上。

## Active

| Feature | Lane | Stage | Owner | Gates | Updated |
|---|---|---|---|---|---|
| [<slug>](./<slug>/) | full | 1-discussion | <name> | G1⬜ G2⬜ G3⬜ | YYYY-MM-DD |

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
