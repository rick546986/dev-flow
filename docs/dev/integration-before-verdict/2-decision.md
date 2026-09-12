---
feature: integration-before-verdict
stage: 2-decision
status: in-review
verdict:
owner: rick
reviewers: []
updated: 2026-09-12
---

# 2. 收斂 — 整合回歸須在 Fresh／Verdict 之前

> 把 `1-discussion.md` 的發散收成一個選定方案。**G1 未核**:`verdict` 留空,等人類填;本 hop 不代寫 Human PASS。
> Owner 2026-09-12 chat「對」核准 Stage 1 方向。本檔只收斂「散文已搬之後還鎖什麼」。
> 不實作模板／守衛、不碰 #196、不發版、不做 Stage 3+。

## Approaches Considered

### 決策點：剩餘工作性質（Q5）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| L 鎖牙對帳 | 2c→2d 散文已對,本 slug 不重寫節序;剩餘是牙、活文件、用本 slug 跑通 full lane | 對準本 tree 已核事實,不把已搬散文當還沒搬 | 人可能以為「沒做事」;要明列還活著的舊序殘留 | 中 | `1-discussion.md:23-25` 模板／指南／節點已是 2c→2d;`L93` Q5 假設剩餘=鎖牙／範例／STATUS;`L155-157` 派工行號對不上現檔。成本 `[Assumption]` |
| R 當舊序重寫 | 當模板仍是 Fresh→Verdict→Exit 才合,再搬一次 2c／2d 散文 | 表面上對齊派工舊敘事 | 現檔已搬;重寫會撞 ST／graph 已綠的針,製造假 diff | 高 | `_templates/7-review.md:100-120` 2c 已在 2d 前;`L330-333` Exit 已禁補碼;`scripts/check-stage67-enforcement.sh:298-322` 已咬模板字面順序。成本 `[Assumption]` |
| C 宣布做完結案 | 散文已搬 → 關 feature,不當第一條 full lane | 零施工 | 範例仍教 2c=Fresh;腳本 GUIDANCE 仍只說「輸出不算數」;owner 要的是跑通鎖定 | 低 | `1-discussion.md:26` 範例舊編號;`L90-92` Q2/Q3 owner:必須在 Fresh 前、且當第一條 full lane;`scripts/devflow-integration-regression.sh:203-205` ALREADY_SYNCED 仍無恢復句。成本 `[Assumption]` |

### 決策點：牙與錨怎麼鎖（Q6）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| T1 延伸既有 ST 家族 | 既有模板順序牙留下;再咬「還在教人怎麼做」的活文件:範例編號、腳本檔頭／GUIDANCE、manifests 若當 SOP。ALREADY_SYNCED 人讀句必須點名重綁 Fresh 或 FAIL | 不另造檢查家族;對準已綠的 ST／graph／integration-guard | 擋不住人跳過 2c(無主機攔截);只鎖文字與產物形狀 | 中 | `1-discussion.md:95` Q6 移交牙／錨;`L62` 誰都可跳過 2c;`scripts/check-stage67-enforcement.sh:298-322` 已咬模板;`scripts/check-integration-regression-guard.sh:469-518` 已咬 2c 工具先於合併;`scripts/devflow-integration-regression.sh:2` 檔頭仍寫 Exit Checklist;`L203-205` GUIDANCE 無恢復。成本 `[Assumption]` |
| T2 新主機攔截 | 跳過 2c 就 fail-closed(receipt／cursor 當入場券) | 對準「現場仍走舊序」假設 | 另造牙家族;跟 host-stack-fit 收據題重疊;本 slug 未裁主機策略 | 高 | `1-discussion.md:62` `[Assumption]` 現場跳過 2c、無採用 log;`L86` 不重寫整合腳本演算法;`docs/dev/host-stack-fit/2-decision.md:71` 已鎖 script-minted receipt。成本 `[Assumption]` |
| T3 只改文件 | 改範例與指南句,不加新機械檢查 | 最短 | 範例再漂回去沒人紅;ST 現在只咬模板不咬範例 | 低 | `example/contract-expiry-reminder/7-review.md:24` 仍寫「執行清單 2c 的 Final Fresh」;`example/contract-expiry-reminder/4-spec.md:223` 仍寫「2c gauntlet」。成本 `[Assumption]` |

### 決策點：範例舊編號何時改（Q7）
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| E1 本 slug 改 | 完整範例把 2c=Fresh／2c=gauntlet 改成現行編號(2c 整合、2d Fresh／gauntlet),當鎖牙的一部分 | 採用者抄範例就不會走舊編號;Q7 有著落 | Diff 含 example,不是純牙 | 低 | `1-discussion.md:26`／`L166-169` CONFIRMED 範例漂移;`L96` Q7 移交後續站(本站正是後續)。成本 `[Assumption]` |
| E2 另開 follow-up | 本 slug 只寫牙,範例等下一條 feat | 本 slug Diff 較瘦 | 第一條 full lane 自己的範例仍教錯序;G-out-3 載體不完整 | 中 | `1-discussion.md:72-74` G-out-3 用本 slug 鎖出貨樹=核准樹。另開的接縫 `[Assumption]` |
| E3 當歷史不改 | 範例留舊編號,只加「舊寫法」橫幅 | 零改 example | 人仍會照 2c 跑 Fresh;橫幅救不了抄指令的人 | 低 | 同 E1 出處;「橫幅夠用」為 `[Assumption]` |

## 方案架構圖
[L] 散文不重寫 (選定)
[T1] 延伸既有牙 (選定)
[E1] 本 slug 改範例 (選定)
[2c] 先整合再 Fresh
[V] Verdict 後禁改碼

## Decision
採 **L + T1 + E1**:本 tree 的 7-review／指南／Stage 7 節點已經是 2c 整合 → 2d Fresh → 雙軸 → Verdict → Exit 只准文件,本 slug **不把節序當還沒搬再重寫一遍**。剩餘工作是把「還在教舊序」的活文件與人讀句鎖進既有 ST／模板順序家族:完整範例不得再寫「2c = Final Fresh／gauntlet」;整合腳本檔頭不得再把自己安在 Exit Checklist; `ALREADY_SYNCED` 的 GUIDANCE 必須點名「重綁 Fresh 或 FAIL」,不能只說「輸出不算數」。本 slug 繼續當第一條真實 full lane 的載體。不新造跳過 2c 的主機攔截,不改整合腳本判定演算法。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| R 當舊序重寫 | 模板頂註與 Exit 條已是 2c→2d;ST／graph／integration-guard 已綠。再搬一次是假施工,且會撞已咬住的針。 |
| C 宣布做完結案 | 範例仍教 2c=Fresh;腳本仍把整合安在 Exit、ALREADY_SYNCED 仍無恢復句。Owner 要的是鎖住並跑通,不是關檔。 |
| T2 新主機攔截 | 「現場跳過 2c」無採用 log;另造牙家族,跟已核的 host-stack-fit 收據重疊;超出「不重寫演算法／本 hop 不選定全新守衛家族」。 |
| T3 只改文件 | 沒有牙,範例下次一漂就回到舊編號;現有 ST 只咬模板不咬範例。 |
| E2 另開 follow-up | 本 slug 是鎖定載體;把最高槓桿的舊編號留在完整範例,等於第一條 full lane 自己示範錯序。 |
| E3 當歷史不改 | 抄範例的人不會先讀橫幅;舊編號本身就是痛。 |

## Rationale
痛的因果沒變:Verdict 綁當下 HEAD,之後再合 `INTEGRATION_SHA` 就讓核准樹≠出貨樹;`ALREADY_SYNCED` 若只寫「證據不算數」就能勾過,恢復路徑是空話。Owner 已裁「整合必須在 Fresh／雙軸／Verdict 之前」,而且要拿本 slug 當第一條真實 full lane。

Stage 2 對帳把 Q5 假設收成事實:**節序散文已經搬完,牙只咬母版模板,活文件還沒跟。** 派工／舊 Backlog 講的 Fresh→Verdict→Exit 才合,對不上現檔行號。指南 renderer 與 `S2c-integration → S2d-fresh` 已是新序。還在教舊序的是:(1) `example/contract-expiry-reminder` 把 2c 當 Fresh／gauntlet;(2) `devflow-integration-regression.sh` 檔頭仍自稱 Exit Checklist 工具,GUIDANCE 的 `ALREADY_SYNCED` 只有「輸出不算數」;(3) `manifests/p4-gauntlet-gates.md` 仍寫「執行清單 2c」當 gauntlet 命令。STATUS 舊 Backlog 句已在 #199 移進 Active,不是本 PR 能改的表列。

所以贏的組合是「承認散文已搬 + 把牙延伸到活文件 + 本 slug 改範例編號」。R 假裝還沒搬;C 假裝已經鎖住;T2 用沒有現場 log 的假設去開第二套主機牙;T3／E2／E3 都留下「完整範例教錯步號」這條最高流量的舊路。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 人以為 L=沒事做,G1 看不出剩餘範圍 | Decision／SC 逐條點名範例編號、腳本檔頭、GUIDANCE、既有 ST 必須繼續綠;4-spec 用可測句接這三點 |
| T1 擋不住跳過 2c | 承認這是已知缺口。本 Decision 不開 T2。要做主機攔截另開 feat,並先對帳 host-stack-fit。現場跳過仍是 `[Assumption]`,過期不自動升級成本 slug 的 T2 |
| 改腳本 GUIDANCE 被誤當成改演算法 | OC-2 收窄:exit code／STATUS 判定不動;只改檔頭與人讀句,以及咬這些字的牙 |
| 改完整範例讓歷史 G3 紀錄對不上 | 只改「還在教人怎麼做」的編號句;示範 SHA／當時 verdict 不當成本次重審 |
| 既有 ST 針因改模板誤紅 | L 禁止重寫已對的 2c／2d 散文;Stage 4+ 若動模板只加針、不改已綠順序句 |
| 本 PR 去改 STATUS 跟別人搶列 | 流程層 OC:feature branch 不跑 `status-update.sh` 改正本;升 Stage 2 等合進 main 再寫 |

## Success Criteria
- SC-1(G-out-1 節序):人按執行清單做 Stage 7 時,整合步出現在 Final Fresh／雙軸／Verdict 之前。觀測:`_templates/7-review.md` 頂註 `2c.**整合回歸**` 的字面位置仍在 `2d.**Final Fresh Run**` 之前;Exit Checklist 仍禁 Verdict 後合併 `INTEGRATION_SHA`。
- SC-2(G-out-1 出貨樹):本 slug 自己走到 Stage 7 並勾完 Exit 之後,7-review 所記 Source SHA 與 `git rev-parse HEAD` 逐字相同。
- SC-3(G-out-2):腳本印 `ALREADY_SYNCED` 時,同一份輸出／人讀句出現「重跑 Final Fresh」或「本項 FAIL」其中一個可執行下一步;不得只出現「輸出不算數／證據不算數」卻讓人勾過。觀測:`scripts/devflow-integration-regression.sh` 的 `ALREADY_SYNCED` GUIDANCE,加上模板恢復句仍在。
- SC-4(活文件不再教舊編號):`example/contract-expiry-reminder/7-review.md` 與 `4-spec.md`(及其 html twin)不再把「執行清單 2c」寫成 Final Fresh 或 gauntlet;改成現行 2c=整合、2d=Fresh／gauntlet。
- SC-5(牙有鑑別力):一份故意把完整範例寫回「2c = Final Fresh」的負向樣本,既有或本 slug 新增的檢查必須紅(exit ≠ 0)。只改文件、檢查仍綠 = 未達。
- SC-6(腳本安家):`devflow-integration-regression.sh` 檔頭不再把「Exit Checklist」當整合步的家;改指 7-review 步 2c(Final Fresh 之前)。
- SC-7(Non-Goal):整合腳本的 STATUS／exit code 判定與本 slug 開工時相同;沒有新的跳過 2c 主機攔截;不碰 #196;本 hop 不填 Human G1 PASS。

## Scope & Non-Goals(定稿)
- In:承認 2c→2d 散文已搬;延伸既有 ST／模板順序家族去咬範例編號、腳本檔頭／GUIDANCE、仍當 SOP 的 manifests 舊 2c 句;本 slug 改完整範例編號;本 slug 繼續當第一條真實 full lane。
- Out:把 7-review 節序當舊序再重寫一遍;新造跳過 2c 的主機攔截;改整合腳本判定演算法;九條制度缺口實作;open PR #196;發版／bump plugin;Windows 真機;本 PR 改 `docs/dev/STATUS.md` 表列;本 hop 寫 Human G1 PASS;Stage 3+ 本 hop 施工。

## Owner Calls(自判裁決,待人審)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 本 slug **不**新造「跳過 2c」主機攔截。使用者只裁「整合在 Fresh／Verdict 前」;「用既有 ST 家族延伸、不另開 T2」是 owner 延伸 | 跳過 2c 無採用 log;另造牙靠近第二套方法論,且跟 host-stack-fit 收據重疊 | `1-discussion.md:62` 假設無 log;`L86` 不重寫演算法;`docs/dev/host-stack-fit/2-decision.md:71` 已鎖 receipt。延伸本身 `[Assumption]` | Scope 加上主機入場券;要跟 host-stack-fit 對帳牙形,本 slug 不再是「鎖活文件」薄刀 | 待人審 |
| OC-2 | 整合腳本只改檔頭與 `ALREADY_SYNCED` GUIDANCE(及咬這些字的牙)。**不改** STATUS／exit code 判定。這是對「加強 ALREADY_SYNCED」的收窄 | 弱點在人讀句與安家,不在判定碼;改演算法會重跑八情境+mutant,且撞 Stage 1 Non-Goal | `1-discussion.md:86` 不重寫演算法;`scripts/devflow-integration-regression.sh:169-187` 判定已 fail-closed;`L203-205` 缺的是恢復句 | 要重簽 integration-regression 守衛;SC-7 改寫 | 待人審 |
| OC-3 | 歷史 notes／HISTORY 裡的舊序敘事不改(當時事實)。只改「還在教人怎麼做」的活文件。使用者 brief 說 reconcile docs;「活文件≠考古檔」是收窄 | 派工／HISTORY 記錄的是當時痛,改掉會假造時間線 | `1-discussion.md:21-22` 派工舊序是 Context;`docs/dev/HISTORY.md` 只增不改。收窄 `[Assumption]` | Scope 加上改 notes／HISTORY;跟「只增不改」衝突 | 待人審 |

### 內部技術選擇(下層,告知即可)
- 本 PR 不跑 `scripts/status-update.sh` 改正本表列(腳本在 feature branch 拒寫;升 Stage 2 等合進 `main`)。
- `1-discussion.md` 維持 `status: draft`(Stage 1 hop 原文);本 hop 依 owner chat「對」進 Stage 2,不回改正本討論。
- 審頁只走 `scripts/build-stage2-html.py --action`,不手包 html-shell、不另產 gate-twin 當本 hop 主產出。
- 契約／plugin 不 bump。Stage 3 觸發判定留給第 3 站;本檔無「跳過 Stage 3」流程層 OC。
- Human G1 `verdict` 留空,feature agent 不填 PASS／REQUEST_CHANGES／HOLD。

## ADR 晉升檢查
- 難逆轉:否(G3 前可改本檔 Decision／OC;落地後要翻案另開 feat,但契約與演算法本 hop 不動)
- 反直覺:是(模板散文已搬,人以為做完;真正剩餘是牙與還在教舊序的活文件)
- 真 trade-off:是(重寫散文 vs 鎖牙;主機攔截 vs 延伸既有 ST;本 slug 改範例 vs 另開)
→ 晉升:**否**(三條件未全中;留在本檔。不抄 `docs/adr/`)

## 確認紀錄
- 決策點清單確認 | 2026-09-12 | owner 核准 Stage 1 方向(chat「對」);本 hop brief 指定收斂「模板已寫 2c→2d vs 腳本／牙／範例／文件仍教舊序」。本檔三決策點 = Q5 剩餘工作性質、Q6 牙怎麼鎖、Q7 範例何時改
- Stage 1 改口 | 2026-09-12 | 1-discussion 仍 draft、Q5 仍 `[~]`、Q6／Q7 仍 `[>]`;本檔把 Q5 收成 L、Q6 收成 T1、Q7 收成 E1。不回改正本討論
- G1 | 2026-09-12 | 未核。`verdict` 空。不代寫 Human PASS
