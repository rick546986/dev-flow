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
> → 立刻 commit → 立刻推」一氣做完;`push` 被拒 → `git fetch` 後
> `git rebase origin/main` 重放自己未發布的 commit,解完衝突再推,並核對整張表的
> **列集合**沒有把別人的列刪掉;**不准**用 `push --force` / `reset --hard` 解決
> 本檔的推送衝突。

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

> 2026-08-18 並行制度空白輪:多 feature 並行的四個制度空白(STATUS 只在整合分支
> 維護/合併後回滾走 revert -m 1/條件式整合回歸/執行環境隔離檢查項)已全數寫進
> 母版,詳見 `notes/dispatch-parallel-feature-gaps.md` 與 HISTORY 對應條目。
>
> 2026-08-18 v3.8.0 blockers 輪:發版前七項必修(H-1 整合回歸演算法工具化、
> M-1 fork 錨點、M-2 STATUS 寫入紀律、M-3 直接補修判準、S-1 兩份 STATUS 對帳、
> S-2 檔案地圖精確計數、L-1 殘留清理)已全數處置,詳見
> `notes/dispatch-v380-blockers.md` 與 HISTORY 對應條目。同輪定案:
> **本表是待辦的唯一正本**,散在派工單尾節的欠帳全數收攏進來。
> 排序 A → B → C,同級之間「擋住別人」的在前。

| 級 | 一句 | 來源 |
|---|---|---|
| A | v3.8.0 推上去 + 打 tag + 發 release + 確認 CI 綠 —— 修完就該做,目前唯一的 A 級 | 發版流程第 6–8 步(`skills/dev-release/SKILL.md`) |
| B | owner 親自打開 gate twin 產出的 html 驗收「好不好審」,b8 的 verdict 才能從 `REQUEST_CHANGES` 改掉 —— **這件事只有 owner 做得了** | `docs/dev/b8-gate-twin-review-ui/7-review.md:5,180,181` |
| B | 拿 dev-flow 自己跑一次完整 normal-risk full lane(1-discussion → 7-review、過 G1/G2/G3)當觀測實驗 —— owner 已排定,是下一輪的事;在那之前不動 Stage 1–4 模板內容,免得污染觀測 | `notes/dispatch-parallel-feature-gaps.md` 末節 |
| B | 需求討論的九條制度缺口(A-1~A-7、B-1、B-2)逐條裁決 —— owner 已裁定暫緩,等上一列的 full lane 觀測跑完再對照裁決 | `notes/review-requirement-discovery-gaps.md` |
| B | 散發清單收斂成一份正本(source/destination/mode),讓 dev-setup 的 install/check/baseline、dev-release、parity、檔案地圖全部讀同一份 | `notes/dispatch-v380-blockers.md` H-1 八個記帳點 |
| B | STATUS 真正的單寫入者(或帶鎖的更新器)—— v3.8.0 輪只縮小了窗口,沒消除同 checkout 的靜默互蓋 | `_templates/STATUS.md` 頂註、`notes/dispatch-v380-blockers.md` M-2 |
| B | 第二個範例 feature,破「唯一範例自證循環」= 4cap O-3。2026-08-17 清空輪裁決仍不做:清洗 `docs/dev/engine-fence-masking/`(母版第一份真實 fast lane 紀錄)成第二範例是 feature 級工程 —— 要讓所有掃 example/ 的機械檢查認得 fast lane 範例、且範例是機械檢查的地基,半吊子的第二範例比沒有更糟(假信心)。素材是 append-only 的歷史檔,不會腐化,無急迫性衰減;應開專屬 feature 走完整 G1-G3 來做 | `docs/dev/4cap-remediation/4cap-audit-fixes-2026-08.md` O-3 裁決 |
| C | `engine-fence-masking` 功能早就合進 main,收尾文書沒關(狀態還是 `draft`,Exit Checklist 尚未收尾,見該檔第 106–111 行;未勾項數以檔案現況為準,不寫死) | `docs/dev/engine-fence-masking/7-review.md:4,106-111` |
| C | 用 Bash 寫檔只有「事後偵測」沒有「當場攔下」(Edit 那條路有擋),文中說要開 ticket 或記 STATUS —— 兩件都沒做 | `docs/dev/engine-fence-masking/7-review.md:100` |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred)。2026-08-17 清空輪裁決仍不做:投資未定且**零採用現場疼痛訊號**(G1/G2/G3 全是現場真踩到的,這兩件沒有);等有採用專案真的要 SDC 級指引再立案,不為清空而硬做 | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |
