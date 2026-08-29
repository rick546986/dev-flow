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
> 兩個 worktree 各改本檔,合併衝突時容易靜默刪掉對方那一列。只在整合分支上改,
> 分支之間的衝突結構上消失。拆成一 feature 一檔等於沒有看板。
>
> ⚠️ 同一條整合分支上多 session 同時寫仍會後寫蓋先寫。下面把窗口縮到最小:
>
> | 什麼時候 | 誰改 |
> |---|---|
> | 開工加列、階段推進、gate 更新 | 該 feature 的 **owner**(`Owner` 欄那個人) |
> | ship 移出 Active | **合併那個 PR 的人** —— 他不一定是 owner |
>
> 交接點 = PR 被合併的那一刻:之前責任在 owner,之後在 merger。
> - 改本檔前先 `git fetch` 再 `git pull --ff-only`(這時還沒分岔,會過);然後
>   「只改自己那一列 → 立刻落地 → 立刻推」一氣做完,不要改完放著。
> - **落點(commit 走哪條路)看專案自己的 git 紀律,不是本檔規定的事**:整合分支
>   允許直接 commit 就直接做;有護欄擋直接 commit(branch protection / pre-commit
>   hook / 團隊規約)就開一條短命 branch → commit → 立刻 `merge --no-ff` 回整合分支。
>   兩條路都要滿足同一個要求:**寫入窗口最短** —— 從改完到推出去之間的時間越短,
>   被別人靜默蓋掉的機會越小。「直接 commit」只是達成它的手段之一,不是規則本身;
>   把手段當規則寫死,在有護欄的專案上會變成「照做就違規」。
> - `push` 被拒 → `git fetch` 後 `git rebase origin/<整合分支>`,把自己還沒發布
>   出去的那個 commit 重放上去,解完衝突再推;重放完**核對整張表的列集合**,
>   確認別人的列沒有在解衝突時被自己刪掉。這**不算改寫共享歷史** —— 重放的是
>   自己本地還沒推出去的 commit;README §7 禁的是對**已經推出去、別人已經拿到**
>   的歷史做 `reset --hard` / `push --force` / `rebase`,兩件事不要混。
> - **不准**用 `push --force` 或 `reset --hard` 解決本檔的推送衝突。
> - 一句理由:看板遺失一列是**靜默**的,沒有紅字、下一個人會照著錯的狀態決策。
>
> **表列(Active / Backlog)的唯一寫入口**是帶鎖的更新器。母版:
> `scripts/status-update.sh`(目錄鎖包住讀→改自己那一列→寫→蓋章)。
> 採用專案本輪尚未散發這支腳本;沒有更新器的 checkout 仍靠上面的
> 寫入紀律,且**不要**同 checkout 並行手改表列。手改表列而不走寫入口,
> 蓋章對不上,`check-status-policy.sh` 會紅。
>
> `Branch` 欄填法:Stage 1–5(尚未開 feature branch,見 README §7 規劃層 git)固定填
> `n-a:尚未建立 branch`(逐字這個字串,方便機械判定);Stage 6 起 branch 建立並
> 推上去之後,換成**已發布的遠端 ref**(如 `origin/feat/<slug>`)—— 不要填本地
> 分支名:本地分支只存在於某一台機器,換一個 clone 算「各 feature 改過的檔」
> (README §7「直接補修」判準)時會靜默漏掉這個 feature。
>
> `OverlapRef` 欄 = 直接補修算法讀的**唯一座標**(STATUS/runtime 名稱就是
> `OverlapRef`;`scripts/status-update.sh --print-overlap-ref` 印出的就是它)。
> 算法只讀這一個,不得另猜第二個 ref,也不得把 `Lane` 當 `execution.mode`。
> 解析規則(寫死,不留二選一):
> - sequential(`5-tasks` frontmatter `execution.mode` 缺省或明寫 sequential):
>   這個座標**就是** `Branch` 遠端 ref。欄可留 sentinel / 空白,runtime 回傳 Branch。
> - parallel:合回 feature branch **之前**,本欄必須寫已發布的
>   `integration/<slug>` tip(如 `origin/integration/<slug>`);合回並 push
>   **之後**,改成與 `Branch` 同一遠端 ref。欄空或仍是 sentinel → fail-closed,
>   不宣稱零交集,也不准 runtime 自己去拼 `integration/<slug>`。
> Stage 1–5 範例列本欄與 `Branch` 一樣填 `n-a:尚未建立 branch`。
>
> ⚠️ `Branch` 這個 ref 是**兩段式發布**:Stage 6 開始時先推一次,是為了建立可查的座標,
> **不代表執行中的 remote 已經完整**(本地可能還有未 commit/未發布的 T);
> Stage 6 收尾由 dev-run 在 bookkeeping 之後、回報 Stage 7 之前**再發布最終
> feature tip** 並驗證 remote tip 等於本地 HEAD(見 `skills/dev-run/SKILL.md`
> 收尾節)。執行中的未發布窗口由 README §7 直接補修算法負責封住:Stage 6 一律
> fail-closed、Stage 7 逐一驗 ACCEPTED commit 是 remote tip 的祖先。
> parallel 在 `OverlapRef` 解不出來之前同樣 fail-closed。

<!-- status-writer-rev:PLACEHOLDER-WILL-REFRESH -->

<!-- status-writer-rev:0f1a84cf04e27b2f6868c6ccce14e2b0d90ebb155d922df724b4dd650ff7ab94 -->

## Active

| Feature | Lane | Stage | Owner | Branch | OverlapRef | Gates | Updated |
|---|---|---|---|---|---|---|---|
| [<slug>](./<slug>/) | full | 1-discussion | <name> | n-a:尚未建立 branch | n-a:尚未建立 branch | G1⬜ G2⬜ G3⬜ | YYYY-MM-DD |

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
