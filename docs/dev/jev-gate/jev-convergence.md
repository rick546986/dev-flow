---
title: jev 收斂紀錄：七個 roadmap 分叉
slug: jev-gate
status: done
date: 2026-09-22
model: jev-1.13.0（別名 jev-latest）
evidence: evidence/jev-forks-v2-packets.json、evidence/jev-forks-v2-result.json、evidence/jev-forks-v1-result.json
---

# jev 收斂紀錄

roadmap 的七個方向分叉，各寫成證據包問 jev，由 rick 逐題裁決。這也是 dev-flow 第一次真的呼叫 jev，等於 P1 之前的 dogfood。

## 1. 結果總表

| 分叉 | 定案 | jev v2（三跑平均） | 穩定 | 明顯度 noul | 選錯代價 0–3 | 裁決 |
|---|---|---|---|---|---|---|
| F1 哪個接入點先上 | J1 live → J3 → J5 shadow | 0.89 | 是 | 0.39 | 1.2 | rick 一次過 |
| F2 ledger 放哪 | 沿用 `append_events()` 進 `.dev-flow/events/`；P0-6 不行才自立 | 0.95 | 是 | 0.37 | 1.4 | rick 一次過 |
| F3 守衛擋不擋 shadow | 七組全齊才准寫，shadow 也算 | 0.63（拆兩層 0.37） | 是 | 0.34 | 2.0 | rick 一次過 |
| F4 J5 畢業門檻 | Wilson 下界 ≥85%、n≥30、一次推翻即凍結 | 0.72（加安全網事實、六跑）；零推翻 59 筆 0.28；90／20 為 0 | 五跑同 | 0.35 | 1.9 | rick 定案，見 §3 |
| F5 J2 做不做 | **留著**，重點改成 J2 證據包要餵夠 | jev 傾向不做 0.77；排最後 0.22 | 是 | 0.31 | 1.8 | **rick 推翻 jev**：不是拿掉，是把證據做厚 |
| F6 e2e 強制時機 | J5 shadow 開始前做完 | 0.98 | 是 | 0.37 | 1.8 | rick 一次過 |
| F7 標籤怎麼收 | 影子期自動配對 verdict；live 後每週小批、人先答 | 1.00 | 是 | 0.36 | 2.0 | rick 一次過 |

七題「明顯度」全部只有 0.31 到 0.39：jev 的意思是這些都是取捨題，機率高只代表傾向，不代表有標準答案。

## 2. v1 為什麼作廢

第一版證據包由 roadmap 作者自己寫，約 1,000 token，事實由作者挑、選項描述帶評價詞。結果在 F3 給出 0.99 選「拆兩層」，v2 中性化之後反過來 0.63 支持「全齊才寫」。同一題答案對調，證明 v1 的機率反映的是包的寫法，不是決策本身。

v2 的做法（之後 J1／J2／J5 的證據包都照這套）：

1. 由**沒參與決策的 fresh agent** 組包，不透露目前傾向；選項用 A/B/C 中性標籤。
2. 每個選項描述 40–70 詞、長度差 ≤20%、零評價詞（slowest／safest／best／clearly 一類 grep 為 0）。
3. 每個選項附正反論點各 ≥2 條，引審查原文段落，不轉述。
4. 事實 8–15 條，含對每個選項不利的事實；數字逐一對得上來源。
5. 每題跑 3 次，選項與事實順序打亂、標籤換成 OPTION_n；三跑選擇一致才算穩，機率區間一起看。
6. 包長 2,500–5,000 詞（約 4,700–5,100 tokens），遠低於實測上限 32,768。

## 3. F4 深挖

v2 三跑在「85%／30」與「零推翻 59」之間翻，代表包裡沒有分勝負的資訊。補上安全網事實（risk ≥2 一律人看、不可逆改動 Quiz gate、抽查 10–20%、一次推翻即凍結）並拆成子題，六跑：

| 子題 | 答案 |
|---|---|
| 該選哪個 | 85%／30：0.72；零推翻 59：0.28；90／20：0.00 |
| 低風險自動出貨錯一次有多傷（0–3） | 1.24；中等 0.49、可忽略 0.27、輕微 0.24、嚴重 0.01 |
| 多等一年換 95% 把握可接受？（noul） | 0.32 |
| 可容忍的錯放行率 | ≤5%：0.997 |

**要記住的矛盾**：jev 說只容忍 5%，卻選了統計上只能證明 ≤15% 的門檻。這是「用安全網補統計不足、拿時間換把握」的取捨。rick 接受，條件是凍結規則不能拿掉。

## 4. F5 的推翻理由

jev 判「不做 J2」的依據是審查裡的事實：J2 對不到 rick 任一需求、Owner Calls 本來就得人答、錯放行會把錯方向送進 Spec 與 Build、證據只有一張方案比較表。rick 的回應：方向核准這一步可以交給 jev，前提是證據包要餵夠。所以 roadmap 不刪 J2，改為新增 J2 證據包規格（roadmap P2-8）：方案比較表、每個方案的取捨原文、Real-world Context、Open Questions 結論、Owner Calls 答案、reviewer findings，全部進包，並照 §2 的規則由非決策 agent 組包。

## 5. 順手實測到的 API 事實（已回填 roadmap §10）

- 三種題型欄位與草稿一致；`noul` 無 `confidence`。
- state 上限 32,768 tokens（含 questions）；超限回 **HTTP 400** `max_tokens_exceeded`，不是文件寫的 422。
- 延遲：5k tokens 約 0.6–0.7s，20k 約 1.2s，32k 約 1.4s。
- 同一包三次呼叫 `input_tokens` 完全相同；打亂順序不改 token 數。

## 6. 換問法測試（rick 要求：不只換順序，還要換問法）

同一份 v2 中性包，三種問題措辭 × 兩種呈現（結構化 JSON／純文字敘述），每題六個變體（`evidence/jev-phrasing-result.json`）：

| 措辭 | 內容 |
|---|---|
| w0 | Weighing the facts and the arguments for and against each option, which option should the roadmap adopt? |
| w1 | You advise the project owner. Considering every constraint listed, select the single option whose drawbacks are most tolerable. |
| w2 | Which option is most consistent with the owner's stated goals and with the calibration warning in the context? Pick exactly one. |

| 分叉 | 六變體 | 判定 |
|---|---|---|
| F1 | 六個同，0.82–0.96 | 穩 |
| F2 | 六個同，0.79–0.93 | 穩 |
| **F3** | w0 → 全齊才寫 0.68／0.72；w1 → 0.50／0.51；w2 → 拆兩層 0.72／0.75 | **隨問法翻**，是偏好題不是事實題 |
| F4 | w0／w1 → 85%／30（0.58–0.69）；w2 → 零推翻 59 筆微勝（0.52／0.53） | 大致穩；rick 已裁 |
| F5 | 六個同傾向不做，0.66–0.82 | 穩；rick 已推翻 |
| F6 | 六個同，0.94–1.0 | 穩 |
| F7 | 六個同，全 1.0 | 穩 |

**F3 裁決（rick，2026-09-22，看過換問法結果後）：維持「七組全齊才寫」。** 理由：拆兩層只讓 J5 影子記帳早約一週開始，但那段期間的樣本因為沒有 verdict 出處檢查而不能算進畢業的 30 筆，幾乎白記；全齊才寫少一條「哪些樣本算數」的例外。

JSON 與純文字呈現對答案幾乎無影響（同措辭下差 ≤0.1），差別全在措辭。F3 的規律：問「權衡事實」偏安全（全齊才寫），問「缺點最能忍」或「最符合 owner 目標」偏速度（拆兩層）。**教訓寫進 P1-G1**：正式題組的 `instructions` 要固定、進 `questionset_hash`，而且每個 gate 的題目在 shadow 期要用 ≥3 種措辭跑過，措辭之間翻的題不准當放行依據。

## 7. 這輪呼叫的成本

七題 v1 + 七題 v2 三跑 + F4 六跑 + 上限探測十次，合計約 20 萬 input tokens，輸入 $0.042／M，不到一美分。
