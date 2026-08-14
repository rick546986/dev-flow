# 改版歷史索引

> **只增不改(append-only),最新的在最下面。**
> 本檔是**索引**,不是內容:每筆三到五行講清楚「做了什麼/為什麼/落在哪」,
> 細節住個別檔 —— 長期決策 `docs/adr/NNNN-slug.md`、
> 過程文檔 `docs/dev/<slug>/`、執行報告與稽核紀錄各自留在原地。
> 同一件事之後又變了,**不要改舊條目**,追加新的一筆並在該筆註明推翻了哪一筆。
>
> ⚠️ **不要直接編輯本檔。**用:
> ```
> scripts/history-append.sh --slug <代號> --what <做了什麼> --why <為什麼> --where <落在哪>
> ```
> 理由:同一個專案可能同時有多個 session 在寫,直接編輯會讓後寫的把先寫的蓋掉,
> 而且不會報錯。上面那支腳本有目錄鎖 + 重試,並且只做追加。

## 2026-07-31 · methodology-corrections
- 做了什麼:拿掉 dev-flow 對外部引擎 harness 的正式依賴,大案改用「合法規格切片」自己處理;手動走第 6 站也要逐任務獨立審查
- 為什麼:當時流程規定「大案自動轉給 harness」,等於方法論有個逃生門,走出去就不受本流程管;手動實作也缺了 dev-run 才有的每任務獨立審查義務
- 落在哪:README §13、_templates/、skills/
- 詳細:原計畫檔 docs/dev/_archive/2026-07-31-dev-flow-methodology-corrections.md(內容已全數落地,該檔於 2026-08-14 移除,可在 git 歷史查回)

## 2026-08-02 · vnext-runtime
- 做了什麼:第 6 站執行層改成可並行:任務級守衛、wave 派工、候選件機械關卡、嘗試帳、最終重跑
- 為什麼:原本一次只能跑一個任務,大 feature 只能排隊;而且執行過程沒有可稽核的事件紀錄
- 落在哪:manifests/p1-execution.md ~ p4-gauntlet-gates.md、hooks/_exec_impl.py、hooks/_obs_impl.py、hooks/_doctor_impl.py
- 詳細:需求正本 docs/prompts/devflow-vnext-runtime.md;指標 docs/dev/vnext-runtime/README.md

## 2026-08-02 · 4cap-remediation
- 做了什麼:四能力補強:封住追溯鏈頂端、第 3 站情境對帳、交付證據補兩項存在性檢查、README 補「由誰強制」對照表、任務切法補反水平切層判準
- 為什麼:五項缺口都有實測證據 —— 追溯鏈頂端的檢查恆綠(漏一個情境期望集會跟著縮小)、人工確認過的展示情境會無聲消失
- 落在哪:scripts/check-methodology-corrections.sh、scripts/check-realworld.sh、scripts/devflow-evidence-gauntlet.sh、README §7、_templates/5-tasks.md
- 詳細:執行報告 docs/dev/4cap-remediation/devflow-4cap-remediation-2026-08.md;PR #1 squash 96f01e9

## 2026-08-02 · design-boundary-hardening
- 做了什麼:規格模板加「設計邊界契約」條件式區塊,並新增四支完整性守衛(ADR 編號唯一、版本同步、架構守衛自測、關卡條款機械化)
- 為什麼:審查抓到真洞:把 Risk 從 high 改成 normal,整組表格檢查會靜默略過但仍回綠 —— 兩層條件式串接造成的假綠
- 落在哪:_templates/4-spec.md、scripts/check-adr-integrity.sh、scripts/check-version-sync.sh、notes/design/design-boundary-contract.md
- 詳細:PR #2 https://github.com/rick546986/dev-flow/pull/2

## 2026-08-13 · single-plugin-merge · v3.0.0
- 做了什麼:把 Claude Code 外掛(hooks/skills/manifests)從獨立 repo 併進本 repo,repo 名 = 市集名 = 外掛名統一為 dev-flow;導覽網頁收進 guides/
- 為什麼:方法論和執行它的程式分兩個 repo,版本永遠對不上;而且外掛那個 repo 沒有遠端,改動進不了版本控制
- 落在哪:hooks/、skills/、manifests/、.claude-plugin/、docs/PLUGIN.md、guides/
- 長期決策:0001
- 詳細:https://github.com/rick546986/dev-flow/releases/tag/v3.0.0

## 2026-08-14 · a13-start-ignored-dirty · v3.1.0
- 做了什麼:開工檢查不再把 .gitignore 已忽略的檔算成「範圍外未提交的改動」;守衛自測 294→297
- 為什麼:同一條問題在第一輪(A-0)與第三輪(A-13)各被發現一次:凡是 repo 裡有本機開發環境(設定切換檔、快取、IDE 目錄)的專案,一律開不了工,而且沒有安全的繞法
- 落在哪:hooks/devflow-lib.py、hooks/_exec_impl.py、hooks/selftest.sh
- 詳細:修法不是拿掉 --ignored 參數(那會打開 .gitignore 遮蔽漏洞),而是讓同一支函式依呼叫者回傳不同內容;來源 notes/adoption-findings-2026-08-04.md:232 與 :1103

## 2026-08-14 · b9-spec-gate · v3.1.0
- 做了什麼:第 4 站(規格)有了機械關卡:新增 check-spec-gate.sh 五項形狀檢查,註冊進總檢查(15→16 組)
- 為什麼:模板明文寫「每個情境都要有觀測欄」,但沒有任何程式在擋;實測一份 16 個情境的規格缺了 5 個,照樣走到送審
- 落在哪:scripts/check-spec-gate.sh、scripts/devflow-check.sh、skills/dev-flow/SKILL.md、_templates/4-spec.md
- 詳細:https://github.com/rick546986/dev-flow/releases/tag/v3.1.0

## 2026-08-14 · guides-visual-rewrite · v3.1.0
- 做了什麼:三份導覽改成以圖為主(15 張手寫 SVG 逐張過幾何檢查),README 重整閱讀動線
- 為什麼:導覽是純文字長頁,新人讀不下去;而規則正本與解釋文字混在一起,分不出哪句是規定
- 落在哪:guides/(3 檔)、README.md
- 詳細:13 個逐字同步區一字未動,第一次實跑 scripts/render-methodology-corrections.sh --write

## 2026-08-14 · history-index-and-adr
- 做了什麼:改版歷史從三張表裡拆出來:新增只增不改的 HISTORY.md 索引 + 唯一寫入口腳本 + 擋直接編輯的 hook + 形狀守衛;建 docs/adr/ 並補立第一筆長期決策
- 為什麼:做過的事散在五個地方(看板、封存資料夾、執行報告、發版說明、git),而看板的已落地表規則上「保留一季後刪列」—— 等於歷史會被刪掉;另外多 session 並行時直接編輯同一個檔會靜默覆蓋
- 落在哪:docs/dev/HISTORY.md、docs/adr/0001-*.md、scripts/history-append.sh、scripts/check-history-integrity.sh、hooks/history-guard.sh、hooks/hooks.json、_templates/{HISTORY,STATUS}.md、docs/dev/STATUS.md、README §1、skills/{dev-setup,dev-release}/SKILL.md
- 長期決策:0001
- 詳細:docs/dev/_archive/ 內容摘要進本索引後移除;總檢查 16→17 組

