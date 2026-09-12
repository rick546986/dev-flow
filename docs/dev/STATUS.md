# docs/dev — 改版流程索引

> 本檔追蹤**方法論母版自身**的改版工作(非採用專案的 feature)。兩表:
> Active(進行中)/ Backlog(待處理,多數來自採用現場回饋)。
>
> **做完的不留在本檔** —— 一律追加到 `HISTORY.md`(只增不改的索引,最新在最下面),
> 值得長期保存的決策另立 `docs/adr/NNNN-slug.md`。這樣本檔永遠只回答一個問題:
> **現在誰在做什麼、還有什麼沒做。**
>
> **本檔只在整合分支(本 repo = `main`)上維護;feature branch / worktree 內一律
> 不碰本檔**(規則正本與完整理由見 `_templates/STATUS.md` 頂註,本段是母版自己
> 套用同一條規則,兩份要點由 `scripts/check-status-policy.sh` 對帳):ship 移出
> Active 由**合併那個 PR 的人**在合併之後、於整合分支上做,不塞進 feature branch
> 的 PR。寫入紀律:改本檔前 `git fetch` 再 `git pull --ff-only`;「只改自己那一列
> → 立刻落地 → 立刻推」一氣做完 —— 落點看專案 git 紀律(本 repo 的整合分支 `main`
> 有全域 hook 擋直接 commit,所以走短命 branch → commit → 立刻 `merge --no-ff`
> 回來;允許直接 commit 的專案就直接做),兩條路都要滿足**寫入窗口最短**這個真正
> 的要求;`push` 被拒 → `git fetch` 後
> `git rebase origin/main` 重放自己未發布的 commit,解完衝突再推,並核對整張表的
> **列集合**沒有把別人的列刪掉;**不准**用 `push --force` / `reset --hard` 解決
> 本檔的推送衝突。
>
> **表列(Active / Backlog)的唯一寫入口**是 `scripts/status-update.sh`
> (目錄鎖包住讀→改自己那一列→寫→蓋章)。不要直接編輯表列:兩個 session
> 在同一 checkout 手改,後寫會靜默蓋掉先寫的列。手改而不走寫入口會讓
> 蓋章對不上,`check-status-policy.sh` 會紅。feature branch 上本腳本拒改正本表列。

<!-- status-writer-rev:7cbc6f3ee44bfa9a5c249de70b6784477c78e33dfdbf4386bd60b4a0a4db04f2 -->

## Active

| Feature | Lane | Stage | Owner | Branch | OverlapRef | Gates | Updated |
|---|---|---|---|---|---|---|---|
| [integration-before-verdict](./integration-before-verdict/) | full | 6-exec | rick | n-a:尚未建立 branch | n-a:尚未建立 branch | G1✅ G2✅ G3⬜ | 2026-09-12 |
| [diagram-ir-gate](./diagram-ir-gate/) | full | 3-prototype | rick | n-a:尚未建立 branch | n-a:尚未建立 branch | G1✅ G2⬜ G3⬜ | 2026-09-12 |

## 已完成

見 `HISTORY.md`(只增不改,最新在最下面)。**不要直接編輯那個檔**,用:

```bash
scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
```

理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的蓋掉且不報錯。

## Backlog

| 級 | 一句 | 來源 |
|---|---|---|
| B | owner 親自打開 gate twin 產出的 html 驗收「好不好審」,b8 的 verdict 才能從 `REQUEST_CHANGES` 改掉 —— **這件事只有 owner 做得了** | `docs/dev/b8-gate-twin-review-ui/7-review.md:5,180,181` |
| B | 拿 dev-flow 自己跑一次完整 normal-risk full lane(1-discussion → 7-review、過 G1/G2/G3)當觀測實驗 —— owner 已排定,是下一輪的事;在那之前不動 Stage 1–4 模板內容,免得污染觀測 | `notes/dispatch-parallel-feature-gaps.md` 末節 |
| B | 需求討論九條制度缺口已於 2026-09-12 裁決（A-1~A-4/A-6/A-7/B-1/B-2 DO；A-5 LIGHT）；實作另開後續 feature，見 Owner Call | notes/review-requirement-discovery-gaps.md Owner Call |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred)。2026-08-17 清空輪裁決仍不做:投資未定且**零採用現場疼痛訊號**(G1/G2/G3 全是現場真踩到的,這兩件沒有);等有採用專案真的要 SDC 級指引再立案,不為清空而硬做 | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |
