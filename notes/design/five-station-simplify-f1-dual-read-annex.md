# F1 dual-read annex（five-station-simplify）

> 九個 SLOT- id 是語意槽，不是 JSON／YAML 必填鍵（OC-3：不鎖欄位鍵名）。
> F1 牙讀本檔：少一槽 = dual-read 未完成。本檔不 bump 契約、不改 doctor 握手。

## SLOT-PARSE-OLD7

能解析舊 7 站檔（`1-discussion.md`…`7-review.md` 形狀與既有欄）。缺新 5 別名欄不影響這槽。

## SLOT-PARSE-NEW5

能解析新 5 站別名（Intake／Decide／Spec／Build／Ship）。別名對到七個凍結檔名，不是新檔名家族。

## SLOT-MISSING-NEW5-DEFAULT

舊 7 檔缺新 5 欄 = 合法缺席，該檢查不紅。禁止把缺欄當缺陷（已拒 2B）。

## SLOT-UNDECLARED-ROUTE

未宣告契約 2.1.0 dual-read 時，採用端路線 = 舊 7。marketplace 包裝不能單獨改線。

## SLOT-REJECT-2.0.0-PLUS-FIVE-HOPS

契約仍 2.0.0 且 hops 已是五站預設 → 紅、不得改線。契約版本與 hops 哪個先寫入都一樣（S-5.9）。

## SLOT-DOCTOR-GREEN-MEANS

`devflow-doctor.sh` 綠／`COMPATIBLE`／exit 0 只證明握手（`2.0.0 ∈ supported`）。≠ 路線沒變，≠ 已切五站。文案「doctor exit 0 所以可以跟 hops 走」必須紅。

## SLOT-IN-FLIGHT-DETECT

`docs/dev/<slug>/` 已有 1–7 任一 `.md` → in_flight=true，整段舊 7，不得寫入五站狀態（RP-15）。僅 html、零個 1–7 `.md` → in_flight=false。本目錄因 md 而凍，不是因 html。

## SLOT-RP-MIN-SET

RP-1…RP-16 只准加不准減。減列 annex 必須紅。計數落點（event 鍵名）不在本檔鎖定。

## SLOT-SKIP-NEGATION

「不／無／不得」加上「跳過」不得被讀成 skip Owner Call。否定跳過句不是「已跳過 Stage 3」。
