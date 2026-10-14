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

<!-- status-writer-rev:42c61926fdbc35bbff5d97d4263e9faefb859725824bff17a506da390aaceb6b -->

## Active

目前無進行中的改版軌。

## 已完成

見 `HISTORY.md`(只增不改,最新在最下面)。**不要直接編輯那個檔**,用:

```bash
scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
```

理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的蓋掉且不報錯。

## Backlog

| 級 | 一句 | 來源 |
|---|---|---|
| B | 拿 dev-flow 自己跑一次完整 normal-risk full lane(1-discussion → 7-review、過 G1/G2/G3)當觀測實驗 —— owner 已排定,是下一輪的事;在那之前不動 Stage 1–4 模板內容,免得污染觀測 | `notes/dispatch-parallel-feature-gaps.md` 末節 |
| C | SDC 大表、Reference App(4cap §7 第 5 點收攏的低優先 deferred)。2026-08-17 清空輪裁決仍不做:投資未定且**零採用現場疼痛訊號**(G1/G2/G3 全是現場真踩到的,這兩件沒有);等有採用專案真的要 SDC 級指引再立案,不為清空而硬做 | `docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md` §7 |

## Jev 現況（程式常數快照）

> 這一節**不是 Active／Backlog 表列**（不在 `status-writer-rev` 蓋章範圍），是 jev-gate 各 gate 目前狀態的**一頁快照**，
> 每個值都從 repo 程式常數讀出，出處列在每列最右。程式一改、本節就要跟著改（以程式為準，不以本節為準）。
> 快照基線：main `14aead2`（#426）；下列出處中的 `devflow-jev.py`、`devflow_jev/{gate,policy,g2auto}.py` 在 `docs/dev/tools/` 的散發副本經 `cmp` 驗證逐字相同。

**生效等級的規則**（`scripts/devflow_jev/gate.py`）：生效 = `min(jev.yaml mode, gates[Jn])`，全序 `off < shadow < live`；
**沒有 `TYPESAFE_API_KEY` 或沒有專案 `.dev-flow/jev.yaml` opt-in → 一律 off（零出境）**。下表的「預設」是 opt-in 檔存在、但沒列該 gate 時的值。

| Gate | 現況 | 說明 | 出處 |
|---|---|---|---|
| J1 | **live**（預設） | 見 `docs/dev/jev-gate/roadmap.md` P1-F2（Decide 入口、失敗／逾時照舊流程） | `scripts/devflow_jev/gate.py` `OWNER_DEFAULT_GATES["J1"]` |
| J2 | **off**（預設）；即使打開也**永遠 shadow** | `route_taken("J2", …)` 不看 level、恆回 HUMAN（`j2_shadow_window_not_ratified`）；沒有 AUTO_PASS 路徑 | `gate.py` `OWNER_DEFAULT_GATES["J2"]`；`scripts/devflow_jev/policy.py` `route_taken`、`J2_WINDOW_RATIFIED` |
| J3 | **live**（預設，只給建議） | recommendation 只顯示，不寫 verdict／attestation | `gate.py` `OWNER_DEFAULT_GATES["J3"]`；`policy.py` `route_taken` |
| J4 | **off**（預設）；assist only | 只當 routing signal，`route_taken` 恆 HUMAN（`j4_assist_only`） | `gate.py` `OWNER_DEFAULT_GATES["J4"]`；`policy.py` `route_taken` |
| G2R | **未定（依各專案 jev.yaml `mode`）** | 不在 `gates:`，只看 `mode`：`live` = Jev 分流算數；`shadow` = 呼叫並記錄、分流上視同沒有 Jev；`off`／無 key／無 opt-in = no-op。程式沒有 G2R 的預設等級 | `scripts/devflow-jev.py` `g2r_level`（G2R 題組：`policy.py` `G2R_QUESTIONS`；`g2r_fingerprint()` 現為 `229764f20d8a`） |
| J5 | **shadow**（預設；上限） | yaml 寫 `live` 也被 cap 成 shadow、reason 留痕；G3 固定人審 | `gate.py` `OWNER_DEFAULT_GATES["J5"]`、`J5_LIVE_RATIFIED`、`effective_level` |
| MR | **未定（沒寫 `gates.MR` 時跟 jev.yaml `mode`）；上限 shadow** | 不在 J1–J5；`live` 一律 cap 成 shadow（`mr_live_not_ratified`）；沒有預設等級 | `gate.py` `mr_effective_level`、`MR_LIVE_RATIFIED` |

**旗標**（寫死的常數；各常數旁的程式註解載明沒有旗標可改）：

| 常數 | 值 | 意義 | 出處 |
|---|---|---|---|
| `G2_AUTO_LIVE` | **True** | G2 自動審（fresh agent reviewer + 機械檢查）全域開；改 False = G2 全回人審 | `scripts/devflow_jev/g2auto.py` |
| `GRADUATED` | **False** | 沒有任何 AUTO 畢業；`route_taken == "AUTO"` 寫盤前有 tripwire | `scripts/devflow-jev.py` |
| `J5_LIVE_RATIFIED` | **False** | J5 live 未核准 | `scripts/devflow_jev/gate.py` |
| `J2_WINDOW_RATIFIED` | **False** | J2 rolling window 未核定（候選 `J2_WINDOW_CANDIDATE = 50`）；J2 永遠 shadow | `scripts/devflow_jev/policy.py` |
| `MR_LIVE_RATIFIED` | **False** | MR live 未核准 | `scripts/devflow_jev/gate.py` |

**G1／G3 固定人審；Demo verdict 與 `root_cause: spec` 只准人填**（出處：`docs/dev/jev-gate/roadmap.md` §0 第 8、12 條與 P2-10；Jev 不寫 verdict）。

**PR #426（2026-10-12 owner 三項拍板，已落程式與文件；合併日期文件未載明，commit `14aead2` 的 git 日期為 2026-10-14）**：

1. **誤放行率分母**只算「已有 G3 結果者」＝「已走到 G3 的 agent 自動放行 G2」：證據是 `docs/dev/<slug>/7-review.md` 有人簽 verdict，判不出就 fail-closed、不進分母；分母 0 → `insufficient_data`（不是 0%）。出處：`scripts/devflow_jev/g2auto.py` `g3_reached`、`scripts/devflow_jev/policy.py` `g2_misrelease_rate`。
2. **誤放行事件範圍**：G3 退件（`g3_request_changes`／`g3_hold`，且 7-review 人勾 `root_cause: spec`）**加上**實作階段三種事件（`spec_amended` 實作中回頭改 spec、`spec_returned` spec 被退回 Stage 4、`reverted` 被 revert；出處：`policy.py` `G2M_STAGES`）。**是否進誤放率看該 case 有沒有走到 G3，不看事件階段**：`scripts/devflow-jev.py` 的 `misreleased_g3_reached = misreleased & g3_reached_released`——只要該 case 已走到 G3，實作階段事件也進分子；「尚未走到 G3」的 case 不進率，只計入報表的 `misreleased_not_reached_g3`。
3. **`risk_paths` 判定來源**＝4-spec Diff Budget 的 `- Paths:` ∪ R 列提到的檔案（`g2auto.r_row_paths`、G2R case 的 `r_paths`）；「沒宣告任何 paths」與「改到 Jev runtime」仍只看 `- Paths:`。出處：`policy.py` `route_g2`、`g2auto.py` `build_case`。

#426 沒動任何旗標（上表值不變）。細節：`docs/adr/0004-g2-spec-auto-review.md`、`docs/dev/jev-gate/w10-g2-misrelease.md`、`docs/dev/jev-gate/roadmap.md`（P2-9／P2-10）。
