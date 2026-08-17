# G3 回歸 fixture:全形冒號版 4-spec(必須通過 check-spec-gate)

> 2026-08-17 採用專案回報:C1 觀測欄的冒號字元集把「:或：」打成兩個半形冒號
> (四碼全 0x3a,肉眼看不出來),全形冒號寫的觀測欄被判「缺欄」,誘導使用者
> 去編造沒實跑過的觀測值。本 fixture 的觀測欄與例外欄**全部用全形冒號**,
> 由 devflow-check(methodology 群)對它跑 check-spec-gate —— 字元集退化時先紅。
> 政策裁決:結構化欄位的冒號**全形半形皆可**(對照 build-gate-twin 的 observe
> pattern 既有寫法);機械守衛 = check-regex-charclass.sh + 本 fixture。

## Verification Profile

- lane: fast
- Risk: high
- Owner Call 例外：G3 回歸 fixture 需要驗證全形冒號的例外欄同樣被 runtime 認出

## S-1 全形冒號觀測欄

- GIVEN 一份觀測欄用全形冒號寫的 4-spec WHEN 跑 check-spec-gate THEN C1 認出該欄
- **觀測**：check-spec-gate 對本檔 exit 0(全形冒號 + 粗體寫法)

## S-2 帶承接註記的全形觀測

- GIVEN 觀測欄帶括號承接註記且用全形冒號 WHEN 跑 check-spec-gate THEN 同樣被認出
- 觀測(承接T-1)：check-spec-gate 對本檔 exit 0(全形冒號 + 括號註記寫法)
