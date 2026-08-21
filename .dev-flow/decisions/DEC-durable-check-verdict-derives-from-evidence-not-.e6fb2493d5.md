# DEC-durable-check-verdict-derives-from-evidence-not-flags — durable-check 的 verdict 三值,且 PASS 由 remote_ref_matches 這個證據欄位推導,不由 local_only 旗標推導

```dev-flow-decision
schema_version: 1
key: durable-check-verdict-derives-from-evidence-not-flags
status: ACCEPTED
decided_at: "2026-08-21T07:37:20Z"
decision_id: dec_01M0HM1EWVB83TB72H6DSX3MS4
```

## Decision

durable-check 的 verdict 拆成 PASS / LOCAL_ONLY_PASS / FAIL。PASS 的條件是「沒有 problems 且 remote_ref_matches 為真」——判斷式寫成 `elif remote_ref_matches:`,不寫成 `elif not local_only:`。另新增兩個**必填**欄位誠實回報實際證據:remote_ref_matches(ls-remote 問到的 ref 等於本機 HEAD)與 preflight_not_known_local(預檢解析到的位址不在**已知的**本機位址集合裡)。verdict 不再宣稱跨機器物理耐久性。CLI 兩種 pass 都退 0;需要強保證的關卡讀 verdict 或 remote_ref_matches,不看退出碼。

## Alternatives

(a) 接管 Git 實際連線目標、做真正的 endpoint attestation:那是傳輸層重新設計,owner 裁決明確排除,未來可單獨排一輪。(c) 維持現狀 + 補文件:一個已知的 false-positive 路徑本身就是這道 barrier 的正確性缺陷,文件不會讓假證明變安全。另外考慮過讓 --local-only 直接退非零:那會逼人忽略退出碼,因為它是呼叫端明確要求的合法用法。

## Reason

兩個獨立的謊。① --local-only 走 rev-parse <upstream>,那是本機快取,所以 `pushed` 會是 True 而伺服器從頭到尾沒被問過 —— 舊契約讓它與「真的觀察過遠端」共用同一個 PASS,只讀 verdict 的呼叫端分不出兩者,而「記憶離開這台機器了嗎」的答案完全取決於分得出來。② 宣稱過強:_local_machine_ips() 是 best-effort、非空也可能不完整,對不完整集合做否定成員測試只能得到「不在已知集合裡」;而且 SSH config 的 HostName 重映不在偵測範圍內,預檢解析到的位址與 Git transport 實際連上的位址之間沒有綁定。能證明的寫成欄位,證明不到的不要寫進 verdict。verdict 從證據推導而非從旗標推導是 fail-closed:未來若多一條也拿不到遠端證據的路徑,它自動落在 LOCAL_ONLY_PASS,不必記得多加一個分支。誠實欄位必填而非選填,是因為選填會讓呼叫端寫 .get(),而 None 在布林語境下與 False 同義 —— 少一個欄位就靜默降級成某一邊,取決於呼叫端怎麼寫而不是取決於實際證據。

## Tradeoff

(未填)
