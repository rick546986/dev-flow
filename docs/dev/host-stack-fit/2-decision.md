---
feature: host-stack-fit
stage: 2-decision
status: approved
verdict: PASS
owner: rick
reviewers: [user]
updated: 2026-09-09
baseline: v3.22.1 / 1768130
contract: 2.0.0
---

# 2. 收斂 — 主機執法貼近與堆疊盤點

> 把 `1-discussion.md` 的 lean 收成 Decision。G1 已核:`verdict` PASS、`status` approved、OC-1～OC-4 ✅。契約維持 `2.0.0`。本 hop 不升 plugin、不改 hooks／skills、不改 `STATUS.md` 表列。
> Stage 1 當時寫 lean、Q13 曾 `[>]`;owner 2026-09-09 Stage 2 brief 把組合包鎖死。1-discussion 留當時措辭,改口記在本檔,不回改正本討論。

## Approaches Considered

### 決策點：主機策略
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| H1 | 非 Claude 開工必須留下「已跑該站 `--action`」紀錄;缺則不得宣稱武裝 | 假安全感有對向牙;對準既有共同 runtime,不造假 hook | 要定紀錄形狀與誰執行;可能碰 graph／setup 文字 | 中 | `1-discussion.md:117-124` H1 利／害;`L232-235` start ≠ 執法;`L99-101` Goals G1/G2。成本 `[Assumption]` |
| H2 | 只加厚 `#host`／SKILL／N-handoff 的「你沒有 PreToolUse」句 | 最小;不動牙 | `#host` 已寫過,痛仍在;軟提醒救不了跳過的人 | 低 | `1-discussion.md:24` `#host` 已寫;`L119` H2 害;`L81-97` 實驗 A 高分 ≠ 取代牙;`L93-97` DA caveats。成本 `[Assumption]` |
| H3 | 擴大 host-adapter probe:印執法食譜或查「本次是否跑過 `--action`」 | 探針已是開工入口;延續 #78 | probe 檔頭已寫「不是 `--action`」;overload 再假綠 | 中 | `1-discussion.md:27` probe ≠ action;`L67` #78 空樹假綠;`L120` H3 害;`L236-239` 用 probe 冒充執法 = 第四型假綠。成本 `[Assumption]` |

### 決策點：牙形與嚴度
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| C | fail-closed + **script-minted receipt**(條件 C):沒有腳本鑄出的收據就紅 | 不可手填冒充;缺口可觀測;對準共同 runtime `--action` | 實驗 C 9/10(C08 empty;部分缺 DONE);要定義收據欄位與核對 | 中 | `1-discussion.md:81-97` 條件 C;`L156` Q9 lean;`L124` 牙形偏 C。成本 `[Assumption]` |
| A | 只靠軟提醒(短句／長 brief／稀釋進 HOST_GUIDE) | 實驗 A／LA／DA／LAC 皆 10/10,可見時遵從高 | DA 不是野外 SOP(仍要讀長 guide、name leak、env hints);跳過的人零紀錄 | 低 | `1-discussion.md:86-97` A 高分 + DA caveats;`L250` 軟提醒不取代牙。成本 `[Assumption]` |
| B | 手填 markdown checklist,或 warning-only | 實作短;人不想停也可以往下走 | B08 noop;手填可偽造;warning 不擋「已武裝」宣稱 | 低 | `1-discussion.md:87` B 9/10;`L156` B 可偽造。成本 `[Assumption]` |

### 決策點：堆疊落點
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| I2+I4 | **I2 底**:`dev-setup` 寫專案級盤點;**I4 選配**:要機器可讀摘要才加 `0-stack`／digest | 專案級、fast 也吃得到;不碰 Stage 1–4 凍結;digest 與討論檔分離 | setup 不每條 feature 重跑;`git pull` 後套件可漂;多一個選配產物 | 中 | `1-discussion.md:126-136` I2/I4;`L66` fast 無 Stage 1;`L33`/`L69` 凍結擋 I1;`L154` Q7。成本 `[Assumption]` |
| I1 | Stage 1 Context／S1-survey 加盤點節 | 最早;4-spec 直接吃得到 | 改 Stage 1 模板／節點,撞凍結;fast lane 整段沒有 Stage 1 | 高 | `1-discussion.md:129` I1 害;`L31` S1 現無版本步;`L66` fast 會漏;`L158` Q11。成本 `[Assumption]` |
| I3 | `STATUS.md` Active 旁加一節 | 人本來就看 STATUS | 母版 STATUS 禁 feature branch 手改;採用專案也不是每 feature 重寫 | 低 | `1-discussion.md:131` I3 害;`L164` feature branch 不改 STATUS。成本 `[Assumption]` |

### 決策點：盤點深度
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| D1 | v1 = **宣告 pin + 本次碰到的直接相依**;不做 full transitive | 夠抓 #122 那種地板／API 落差;不把 lock 全樹當 v1 範圍 | 漏間接套件仍可能晚爆 | 中 | `1-discussion.md:155` Q8;`L29-30` 3.9 地板 vs `markdown-it-py==4.0.0`;`L183-186` AC-4。成本 `[Assumption]` |
| D2 | lock 全樹含 transitive 當 v1 必寫 | 最完整 | 噪音大;等於另造真相源;與「不另造 lockfile 當正本」衝突 | 高 | `1-discussion.md:145` 已拒另造 lockfile;`L155` v1 不做全樹。成本 `[Assumption]` |
| D3 | 只寫語言／runtime,不寫套件版本 | 最短 | 不滿足「每個套件版本」;AC-3／#122 套件地板抓不到 | 低 | `1-discussion.md:102` Goal G3;`L149` Q4 必須納入盤點;`L179-182` AC-3。成本 `[Assumption]` |

### 決策點：母版 vs 產品 schema
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| S1 | 方法論母版與產品專案**同一 schema／同一深度**(內容各填) | 一套欄位、兩種內容;agent 不用記兩套 | 產品專案可能暫時沒有母版那麼多 pin | 低 | `1-discussion.md:76` Q13 lean;`L160` owner:一致比較好;`L134` 欄位形狀共用。成本 `[Assumption]` |
| S2 | 母版較深、產品較薄 | 產品開場較短 | 兩套深度 = 兩套規則;違反「一致比較好」 | 中 | `1-discussion.md:160` owner lean 同一深度。對立項為推演。成本 `[Assumption]` |
| S3 | 兩套不同 artifact | 各自最佳化 | 第二套產物形狀,靠近第二套方法論 | 高 | `1-discussion.md:106` 禁第二套方法論;`L149` Q2。成本 `[Assumption]` |

### 決策點：slug
| 方案 | 摘要 | 優 | 劣 | 成本 | 依據(`檔:行` 或 `[Assumption]`) |
|---|---|---|---|---|---|
| One | 維持單一 slug `host-stack-fit`(主機 + 堆疊同場) | 已開討論／#149;組合包本來就要一起交 | 一票兩痛,Diff 可能偏大 | 低 | `1-discussion.md:152` Q5;`L157` Q10。成本 `[Assumption]` |
| Split | 拆 `host-fit` + `stack-fit` | 可分開過 gate | owner 未要求拆;接縫要再發明 | 中 | `1-discussion.md:157` 除非 owner 之後要拆。成本 `[Assumption]` |
| Rename | 改名 `early-stack` | 較短 | 只蓋盤點,蓋不住 H1 | 低 | `1-discussion.md:152` 不取。成本 `[Assumption]` |

## 方案架構圖
```
[H1] 強制清單+牙(選定)
[C] 腳本鑄收據 fail-closed(選定)
[I2] dev-setup 盤點底(選定)
[I4] 選配 digest(選定)
```

## Decision
採 **H1 + 條件 C** 與 **I2 底 + I4 選配**:非 Claude 開工必須留下腳本鑄出的該站 `--action` 收據,缺則 fail-closed、不得把 `devflow-exec start` 當成與 Claude 同級武裝;堆疊盤點以 `dev-setup` 寫專案級底稿,要機器可讀摘要時才加 I4。深度 v1 = 宣告 pin + 本次碰到的直接相依,不做 lock 全樹。方法論母版與產品專案同一 schema／同一深度。單一 slug `host-stack-fit`。契約維持 `2.0.0`。本 hop 不解除 Stage 1–4 模板凍結、不升 plugin。

## Rejected Alternatives
| 不選 | 一句棄因 |
|---|---|
| H2 只加硬文件 | `#host` 已寫「無 PreToolUse、誰開工誰先跑 `--action`」,痛仍在;軟文件救不了跳過的人。 |
| H3 擴大 probe | probe ≠ `--action`;#78 已證空樹假綠;拿探針當執法證明會再假綠。 |
| I1 Stage 1 S1 | 要先解凍 Q11 才動 Stage 1–4 模板,且 fast lane 沒有 Stage 1。 |
| I3 STATUS 一節 | 母版 STATUS 禁 feature branch 手改;不是每 feature 可寫的落點。 |
| A 只靠軟提醒 | 實驗可見時 10/10,但 DA 不是野外 SOP;零收據仍可宣稱武裝。 |
| B 手填 checklist／warning-only | 可偽造;warning 不擋假安全感。 |
| D2 lock 全樹 | v1 不做 transitive;會逼近另造 lock 真相。 |
| D3 只寫語言／runtime | 不滿足「每個套件版本」;#122 套件地板抓不到。 |
| S2／S3 兩套深度或兩套 artifact | 與 Q13「同一 schema／同一深度」相反;S3 靠近第二套方法論。 |
| Split／Rename | 不拆 slug;`early-stack` 只蓋盤點。 |
| 假 PreToolUse／把 `hooks.json` 抄進 Cursor | owner 禁;Cursor 薄殼無 hooks 鍵;guide 禁假裝。 |
| 第二套方法論 | owner 禁;host-adapter 也不重寫 1–7。 |
| 改鬆 `--action` 遷就無 hook 主機 | `#host` 與 host-adapter 第三刀已釘死。 |
| 等 Stage 6／7 才發現版本 | owner 要早期寫下;#122 已證晚發現成本高。 |
| 另造 lockfile 當套件正本 | 與 pip／npm lock 雙源,會漂。 |

## Rationale
主機缺口的第一因是「讀得到 skills ≠ 跑得到 PreToolUse」。`start` 只給 Claude hook 米,在 Cursor／Grok 不會擋 Write。H2 重複已寫過的句子;H3 把探針 overload 成執法證明,重演 #78。實驗證明軟提醒**看得見時**遵從高,但 DA caveats 與「跳過的人零紀錄」表示主牙必須是不可手填的腳本收據,而且缺就紅。

堆疊缺口是另一因:S1 不盤版本,#122 是檢查全綠、本機才爆。I1 最早但本 feat 不解凍模板,且漏 fast。I3 撞 STATUS 寫入窗。I2 跟 setup 走、專案級、fast 也吃得到;I4 只在需要機器可讀摘要時才加,避免每 slug 再造一份。深度先釘宣告 pin + 本次直接相依,夠寫出 3.9 vs `markdown-it-py==4.0.0`,不必把 lock 全樹當 v1。母版與產品同一欄位形狀,才不必養第二套盤點語言。兩痛同一 slug,因為牙與盤點都要在「進完整 lane 之前」同時存在。

## Risks & Mitigations
| 風險 | 對策 |
|---|---|
| 收據欄位未在本檔釘死,Stage 4 之前各寫各的 | 本 Decision 只鎖「腳本鑄、可核對、不可手填冒充、缺則紅」。欄位／檔名進 4-spec;OC-1 先收窄「沿用既有 `--action` 腳本,不另造檢查家族」。 |
| 條件 C 實驗 9/10,C08 empty、部分缺 DONE | 核對必須咬空白與缺 DONE;空檔 ≠ 有效收據。 |
| I2 不每條 feature 重跑,`git pull` 後套件漂 | setup 指引寫「依賴變了要重跑」;I4 digest 選配對 lock,digest 不是正本。 |
| 軟提醒高分誘惑退回 H2 | DA caveats 已削弱「野外只靠軟提醒」;H2 進 Rejected,翻案要回本站。 |
| Q11 凍結限制落地 | 本 feat 只延伸 `dev-setup`／既有 check,不改 Stage 1–4 模板。要動模板 = 另開 feat 先過 Q11。 |
| 現場 plugin cache 仍 3.6.1 vs tip | Q12 已確認;對齊 cache 不是本 feat。發版或行為看起來舊了再 Refresh。 |
| fail-closed 增加開工摩擦 | 摩擦換的是「不得假武裝」。不退 warning-only;收據由既有 `--action` 順手鑄,避免第二套儀式。 |

## Success Criteria
- SC-1(主機誠實):非 Claude session 宣稱「可寫碼／已武裝」時,人能指出本次 **script-minted receipt** 在或不在;文案含「無 PreToolUse」與「`--action`」,且不是只看到 `devflow-exec start` 成功。
- SC-2(有牙):只跑 `start`、不跑該站 `--action` → 檢查紅(exit ≠ 0)或明確「未跑 `--action`」;不得出現「已與 Claude 同等武裝」。
- SC-3(收據真偽):手填／空白檔不得算有效收據;核對只接受腳本鑄出的形狀。
- SC-4(早期堆疊):`dev-setup` 底稿寫出語言名、runtime 版本、宣告 pin、本次直接相依的套件名+版本。母版樣張能對上 Python 3.9 地板與 `markdown-it-py==4.0.0`。
- SC-5(落差可見):本機 3.9、套件要 3.12+ 時,落差列在進 Stage 4 之前就在檔上,不是等 render 爆。
- SC-6(同一 schema):方法包與產品專案盤點欄位形狀相同、深度同為宣告 pin + 直接相依;內容各填。
- SC-7(Non-Goal):`.cursor-plugin/plugin.json` 仍無 hooks 鍵;沒有新的假 PreToolUse;既有 `--action` 圍欄未改鬆;契約仍 `2.0.0`。

## Scope & Non-Goals(定稿)
- In:H1+C 收據契約(形狀細節進 4-spec);I2 `dev-setup` 專案級盤點;I4 選配機器可讀摘要;Q8 深度;Q13 同一 schema;單一 slug `host-stack-fit`。
- Out:假 PreToolUse;第二套方法論;改鬆 `--action`;另造 lockfile 當正本;解凍並改 Stage 1–4 模板;本 hop bump plugin;Grok marketplace／主機 SKU 表;把 haiku–sonnet–opus dispatch-guard 搬到非 Claude;本 hop 對齊現場 3.6.1 cache。

## Owner Calls(自判裁決,已核)

### 逐條裁決(上層)
| OC | 決定了什麼 | 為什麼 | 依據(`檔:行` 或 `[Assumption]`) | 若被推翻會怎樣 | 狀態(待人審→✅/✗) |
|---|---|---|---|---|---|
| OC-1 | 收據由**既有**該站 `--action` 腳本鑄造、走既有核對路徑。不另造第二套檢查家族。使用者 brief 只鎖「script-minted receipt」;「沿用既有腳本」是 owner 延伸 | 共同 runtime 已經是 `--action` + check;另造家族等於靠近第二套方法論 | `1-discussion.md:28` 共同 runtime;`L106` 禁第二套方法論;`L237-239` probe 不能冒充 action。延伸本身 `[Assumption]` | 要新腳本／新入口;G4 與「不重寫 1–7」要重審 | ✅ |
| OC-2 | I4 預設落點 = 專案級 `docs/dev/0-stack.md`,不是每 slug 一份。使用者只鎖「I4 optional」;落點是延伸 | I2 是專案級;每 slug 再寫一份會漂而且 fast／多 feature 重複 | `1-discussion.md:132` I4 候選含專案根;`L130` I2 專案級。檔名 `[Assumption]` | 改成 `docs/dev/<slug>/0-stack.md` 或 lock digest 檔名;SC-4 觀測點跟著變 | ✅ |
| OC-3 | I4 **不是**每專案強制;只有需要機器可讀摘要／lock digest 時才加。這是對組合包「I2+I4」的收窄 | 強制 I4 = 每專案多一個產物;digest 不是 lock 正本 | `1-discussion.md:136` 「要機器可讀摘要時才加」;`L145` digest 不取代 lock | I4 變必做;Scope 與 setup 步驟加長 | ✅ |
| OC-4 | 本 feat **不修** plugin cache 落後(Q12)。對齊 cache 留在發版或行為看起來舊了。使用者 brief 未要求本 hop 修 cache;此為收窄 | #152 已確認仍落後,但「不是每條 feature」 | `1-discussion.md:75`/`L159` Q12 CONFIRMED + 不是每 feature | Scope 加上 Refresh／cache 對齊;與 H1+I2 交付纏在一起 | ✅ |

### 內部技術選擇(下層,告知即可)
- 契約維持 `2.0.0`;本 hop 不 bump `.claude-plugin/plugin.json`(模板未要求 2-decision 寫 plugin 版本欄)。
- `1-discussion.md` 保留 lean／「非定案」原文;本檔才把它們改口成 Decision。
- feature branch 不改 `docs/dev/STATUS.md` 表列。
- Stage 3 不預先跳過;觸發判定留給第 3 站(本檔無「跳過 Stage 3」流程層 OC)。

## ADR 晉升檢查
- 難逆轉:否(契約 2.0.0 不變;G3 前可改本檔 Decision／OC;收據與 setup 面可改版)
- 反直覺:是(`start` ≠ 武裝;軟提醒高分仍要 C 牙;最早的 I1 反而不取)
- 真 trade-off:是(fail-closed 摩擦 vs 假綠;I2 新鮮度 vs I1 凍結)
→ 晉升:**否**(三條件未全中;留在本檔。不抄 `docs/adr/`)

## 確認紀錄
- 決策點清單確認 | 2026-09-09 | owner Stage 2 brief 鎖:主機 H1+C、堆疊 I2+I4、深度 D1、schema S1、slug One;本檔六個決策點對應該鎖板
- Stage 1 改口 | 2026-09-09 | 1-discussion 仍 draft、Q6–Q11／Q13 仍寫 lean;本檔改口為 Decision。Q13 自 `[>]`／`[~]` 收成 S1。不回改正本討論
- G1 | 2026-09-09 | owner 在 chat 說「G1 ok」並確認 merge #154;OC-1～OC-4 隨 Decision 組合包一併視為接受。owner 自審(有記錄);reviewers: [user]
