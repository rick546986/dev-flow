# 進行中變更索引

> 用途:並行開發時的單頁看板。每 feature 一列;階段推進、gate 過都要更新。
> **本檔只回答「現在誰在做什麼、做到哪一站」** —— 做完的不留在這裡。
> 排序:進行中在上。
>
> **本檔只在整合分支(`develop` 或 `main`,依專案)上維護;feature branch / worktree
> 內一律不碰本檔。**開工加列(含 `Branch` 欄,填法見下)、過 gate 更新,都切到
> 整合分支上直接改並推;ship 移出 Active 的完整動線是「PR 合併 → 切到整合分支 →
> 移出該列 → 推」—— 在合併之後、同一個時間點一氣做完,不塞進 feature branch 的 PR
> (那會讓 PR 的 diff 混進看板變更,也會在多 worktree 下製造衝突),也不要累積 ——
> 看板落後一天,下一個人就會照著錯的狀態決策。
> 理由:兩個 worktree 各 checkout 不同 branch、各自編輯本檔,合併必然衝突;解衝突時
> 很容易把對方那一列刪掉,而那是**靜默的資料遺失**(沒有紅字、沒有人會發現)。
> 只在整合分支上改,同一個檔案永遠只有一個分支在動 —— **分支之間的合併衝突**
> 結構上消失,不是機率降低。拆成一 feature 一檔可以零衝突,但等於沒有看板(看板的
> 價值就在一頁看完全部,拆了還是要有人彙整)。代價是在 worktree 裡看不到最新看板;
> 但看板本來就是給別人/別的 session 看的,那些人本來就該看整合分支。
>
> ⚠️ 上面消滅的只有「分支之間」的衝突;**同一條整合分支上多個人/多個 session
> 同時改本檔的競爭沒有被消滅**——最糟的形態是兩個 session 在同一個 checkout 上
> 先後寫本檔:後寫的直接蓋掉先寫的,沒有任何紅字。下面的寫入紀律只是把窗口縮到
> 最小,是機率問題,不像分支衝突可以結構上消除:
>
> | 什麼時候 | 誰改 |
> |---|---|
> | 開工加列、階段推進、gate 更新 | 該 feature 的 **owner**(`Owner` 欄那個人) |
> | ship 移出 Active | **合併那個 PR 的人** —— 他不一定是 owner |
>
> 交接點 = PR 被合併的那一刻:之前責任在 owner,之後在 merger。
> - 改本檔前先 `git fetch` 再 `git pull --ff-only`(這時還沒分岔,會過);然後
>   「只改自己那一列 → 立刻 commit → 立刻推」一氣做完,不要改完放著。
> - `push` 被拒 → `git fetch` 後 `git rebase origin/<整合分支>`,把自己還沒發布
>   出去的那個 commit 重放上去,解完衝突再推;重放完**核對整張表的列集合**,
>   確認別人的列沒有在解衝突時被自己刪掉。這**不算改寫共享歷史** —— 重放的是
>   自己本地還沒推出去的 commit;README §7 禁的是對**已經推出去、別人已經拿到**
>   的歷史做 `reset --hard` / `push --force` / `rebase`,兩件事不要混。
> - **不准**用 `push --force` 或 `reset --hard` 解決本檔的推送衝突。
> - 一句理由:看板遺失一列是**靜默**的,沒有紅字、下一個人會照著錯的狀態決策。
>
> `Branch` 欄填法:Stage 1–5(尚未開 feature branch,見 README §7 規劃層 git)固定填
> `n-a:尚未建立 branch`(逐字這個字串,方便機械判定);Stage 6 起 branch 建立並
> 推上去之後,換成**已發布的遠端 ref**(如 `origin/feat/<slug>`)—— 不要填本地
> 分支名:本地分支只存在於某一台機器,換一個 clone 算「各 feature 改過的檔」
> (README §7「直接補修」判準)時會靜默漏掉這個 feature。

## Active

| Feature | Lane | Stage | Owner | Branch | Gates | Updated |
|---|---|---|---|---|---|---|
| [<slug>](./<slug>/) | full | 1-discussion | <name> | n-a:尚未建立 branch | G1⬜ G2⬜ G3⬜ | YYYY-MM-DD |

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
