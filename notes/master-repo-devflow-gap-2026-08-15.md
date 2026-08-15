# 調查紀錄:母版自身的改版為何從未走 dev-flow 流程(2026-08-15)

**性質**:純紀錄,不改任何規則、不加任何機制。owner 問「這輪為什麼沒用 dev-flow」,
本檔是那次調查的存檔。後續要不要處理,歸 owner(即 b8 7-review 的 K-1,派工單明定
是 owner 自己的事)。

## 結論

「沒走流程」不是 2026-08-15 待辦清空輪的單次疏忽,是**結構模式**:
母版自身的改版**從來沒有任何一輪**走過完整 1~7 站。三個原因層層疊加——
規則面沒有這個義務、機制面沒有任何提醒、工作形狀本身塞不進單一 feature slug。

## 查證(全部唯讀,行號為 2026-08-15 當日)

### 1. 規則面:「必須走站」是慣例想像,不是明文義務

| 出處 | 實際寫的是 |
|---|---|
| `README.md:99-100` | 「docs/dev/ 本 repo 用自己的流程管自己」—— 目錄結構圖的**描述句**,無「必須/不得/gate」字樣 |
| `README.md:26`(讀者路由表「要改 dev-flow 本身」列) | 只指路「先看 §7 連動誰」,沒要求開 feature slug |
| `README.md:160-170`(§2 lane 判準) | 判準寫的是變更類型(新能力/bugfix),「母版維護」零命中 |
| `docs/dev/STATUS.md:3-8` | 自我定位是追蹤表(Active/Backlog),不是關卡 |
| `skills/dev-flow/SKILL.md:3`、`skills/dev-run/SKILL.md:3` | 觸發條件全是「跑 feature」情境,無母版自用條款 |

### 2. 機制面:不 start,守衛連知道都不知道

未武裝時的軟提醒(`hooks/_guard_impl.py:59-70`)刻意極窄:只在寫
`docs/dev/<slug>/{5-tasks,6-implementation-notes}.md` 時響一次。
直接改 `scripts/`、`hooks/`、`_templates/`、README —— 零提醒。
這個缺口 `docs/dev/b8-gate-twin-review-ui/7-review.md:185-194`(附錄 A1)已自首過:
「規則寫在 README 裡,但沒有任何機制在『有人開始改母版』時提醒他該走流程」。

### 3. 歷史面:每一輪大改版都是同一個模式

`docs/dev/` 內**沒有任何一個 slug 具備完整 1~7 站檔案**;HISTORY 全部條目分類:

| 形式 | 輪次 |
|---|---|
| 派工 prompt 驅動 | methodology-corrections、vnext-runtime、4cap-remediation(執行指令書 `claude-opus5-devflow-execution-prompt.md`)、design-boundary-hardening、backlog-14-sweep(2026-08-15)|
| 修 bug/結構輪(無站點文檔) | single-plugin-merge、a13-start-ignored-dirty、b9-spec-gate、guides-visual-rewrite、history-index-and-adr、gate-twin-markdown-it |
| 事後補第 7 站 | b8-gate-twin-review-ui(唯一有 7-review,K-1 自認未走 1~6)|
| 維運/發版 | release-v3-2-0、release-v3-3-0、stale-state-cleanup |

### 4. 2026-08-15 待辦清空輪的直接原因

觸發文件 `notes/dispatch-backlog-sweep.md` 自帶另一套執行協定(指揮官/批次/模型分層/
每批 fresh-context 審查),全文無一句要求走站,且明文把 K-1 劃為「owner 自己要處理,
不要動」(:118)。派工單是 owner 事前寫好並 commit 的,實質承擔了 G1/G2(方向與範圍
的事前裁決)的角色。

## 補充判斷(供日後參考,非決定)

「沒走站」不等於「沒驗證」:歷次實際使用的替代協定(事前派工單 + 每批 fresh-context
對抗審查 + 破壞實驗 + 六道機械驗證全綠)提供了 G3 等級的驗證強度(b8 四輪審查共抓
32 條 finding)。真正缺的是**流程分類**——「跨多主題的母版維運輪」這種工作形狀
在方法論裡沒有名字,於是每次都體制外運行、事後自首。可能的出路(A 明文化母版維護
lane / B 強制走站 / C 補未武裝提醒)已於當日對話評估過利弊;owner 裁示**先只留紀錄**,
三案皆未實施。
