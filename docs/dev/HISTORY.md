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

## 2026-08-14 · release-v3-2-0 · v3.2.0
- 做了什麼:發布 v3.2.0:內含 history-index-and-adr 那筆的全部改動,其他機器 /plugin update 後才拿得到新守衛
- 為什麼:外掛更新判斷是比對版本字串不是比對 commit —— 推上去但版號沒動,其他機器更新會回「無內容」而且不會有任何提示
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json
- 詳細:本次為 minor:新增工具/檢查/hook,既有專案 dev-setup upgrade 後仍相容;契約版本維持 2.0.0 未動

## 2026-08-15 · b8-gate-twin-review-ui
- 做了什麼:G1/G2/G3 三站的 html 從「文件視覺版」改成「審查介面」:規格寫進 README §6 與兩份模板,並做出產生器 build-gate-twin.py(三站共用,讀 md 逐條解析不手抄)
- 為什麼:owner 打開一份完全合規的 4-spec.html 第一句話是「這份給人看得有點雜亂」—— 規範只管「必含什麼元素」不管「長什麼形狀」,所以照規則做仍然難審;同一個病 2026-08-13 修過一次但只修了 7-review 一站
- 落在哪:README.md §6、_templates/{2-decision,4-spec}.md、scripts/{build-gate-twin.py,devflow_twin_ui.py,check-gate-twin.sh}、scripts/fixtures/gate-twin/、docs/dev/tools/、skills/{dev-setup,dev-release}/SKILL.md
- 詳細:形狀由 owner 拍板 = 先寫規格再做工具;devflow-check 17→18 組;守衛 21 項含負向案(缺觀測欄紅底、空 spec 不產空殼、artifact 片段不得含外殼標籤)。5-tasks 執行板未納入本輪。來源 notes/adoption-findings-2026-08-04.md 第三輪 B-8

## 2026-08-15 · release-v3-3-0 · v3.3.0
- 做了什麼:發布 v3.3.0:gate twin 審查介面(規格 + 三站共用產生器 + 21 項守衛),其他機器 /plugin update 後才拿得到
- 為什麼:新增了工具與檢查,版號不動的話其他機器更新會回「無內容」且沒有任何提示
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json
- 詳細:minor:既有專案 dev-setup upgrade 後相容;契約版本維持 2.0.0 未動

## 2026-08-15 · gate-twin-markdown-it
- 做了什麼:gate twin 解析層換 markdown-it-py token stream(對母版範例 byte-identical),並納入 5-tasks 執行板(第三種 twin 形狀)、缺任一必填欄即紅底、抽驗格決定論取實列;守衛 60→108 項
- 為什麼:三輪獨立審查 28 條 finding 證明手刻正則解析 markdown 靠自審不可能收斂,其中一條已發生在出貨物上;owner 兩次反映 5-tasks md 直轉難讀
- 落在哪:scripts/build-gate-twin.py、scripts/check-gate-twin.sh、README §6、_templates/{4-spec,5-tasks,7-review}.md、example/、skills/dev-setup/SKILL.md、docs/dev/tools/
- 長期決策:0002
- 詳細:docs/dev/b8-gate-twin-review-ui/7-review.md 附錄 A7

## 2026-08-15 · backlog-14-sweep
- 做了什麼:採用現場回饋 14 條(A-1~A-6/A-11/A-12/B-1~B-6)全數處置:散發 README 剝除機制、s_id 鏈恢復牙齒、Boundaries 進 task dict、Stage 7 審查圍欄(圍欄③,exec-v3)、doctor 必跑、Verify/Files/Diff Budget 紀律、upgrade 三方比對
- 為什麼:四個採用專案的現場回饋積了兩輪沒處理,其中多條是「方法論規定了做不到的事」等級;owner 授權裁決後一次清完
- 落在哪:hooks/、_templates/、skills/dev-setup/SKILL.md、README、tests/parallel-stage6/;裁決記錄 notes/adoption-findings-2026-08-04.md 各節
- 詳細:selftest 297→326;check-parallel 117→120

## 2026-08-15 · stale-state-cleanup
- 做了什麼:散落過期狀態六件結案:4cap 狀態改正+O-1~O-8 裁決+§7 六件、活文件過期外掛路徑統一並新增 check-no-stale-paths 守衛(devflow-check 18→20 組)、五處外掛待辦核對標掉、A-13/B-9 標記已修、v3.1.0 release notes 數字勘誤註記
- 為什麼:外掛併入(ADR-0001)讓一批「外部 plugin 待辦/舊路徑」前提失效卻沒人回頭標;寫死的狀態與數字會誤導照導覽走的人
- 落在哪:docs/dev/4cap-remediation/、guides/、scripts/check-no-stale-paths.sh、notes/change-manifests/、notes/adoption-findings-2026-08-04.md

## 2026-08-15 · release-v3-4-0 · v3.4.0
- 做了什麼:發布 v3.4.0:待辦清空輪全部改動(解析層換 markdown-it-py、執行板、Backlog 14 條、4cap 結案、路徑守衛),其他機器 /plugin update 後才拿得到
- 為什麼:外掛更新判斷是比對版本字串不是 commit —— 推上去但版號沒動,其他機器更新會回無內容且不會有任何提示
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json
- 詳細:minor:既有專案 dev-setup upgrade 後相容;契約版本 exec_state 升 exec-v3(runtime 讀取雙版相容,舊 worktree 不斷線);devflow-check 18→20 組、selftest 297→326

## 2026-08-16 · guard-coverage-sweep
- 做了什麼:補 6 條守衛覆蓋缺口(通用章節對帳/地板+心跳+靜態互釘/fail-closed 路徑掃描/用法驗內容/未閉合註解警告/行號引用勘誤)+ 前輪 12 條修復的行為層補驗與三件補強
- 為什麼:v3.4.0 獨立審查判詞:有些東西壞掉了而 108 項守衛不會發現 —— 第 4 型假綠二次發生、第 5 型(斷言被刪沒人知道)新確認
- 落在哪:scripts/{build-gate-twin.py,check-gate-twin.sh,check-no-stale-paths.sh,check-dev-setup-discipline.sh,check-realworld.sh,check-readme-markers.sh,test-architecture-guards.sh}、hooks/selftest.sh、tests/parallel-stage6/
- 詳細:守衛 108→133;devflow-check 20→21 組;docs/dev/b8-gate-twin-review-ui/7-review.md 附錄 A8

## 2026-08-16 · engine-fence-masking
- 做了什麼:Stage 6 引擎 parse_5_tasks 遮蔽 fenced code block(幽靈任務/fence 內假重複欄退場),contract_ref 鏡射同步;twin 幽靈警告退場 —— 母版第一個全程武裝走 dev-flow fast lane 的 feature,G3 PASS
- 為什麼:twin 側同病已修但引擎沒修:Boundaries 裡 fenced 的 ## T-xx 會被引擎長成有 Files scope 的幽靈任務,審查者與引擎看到兩個世界(A7 H1)
- 落在哪:hooks/devflow-lib.py、tests/parallel-stage6/contract_ref.py、hooks/selftest.sh、scripts/{build-gate-twin.py,check-gate-twin.sh};流程紀錄 docs/dev/engine-fence-masking/
- 詳細:fast lane 全程武裝:A-7 軟提醒/圍欄③禁讀 Self-Review/postbash 偵測網都實際觸發過;dogfood 撞出 D-4 收 Backlog

## 2026-08-16 · release-v3-5-0 · v3.5.0
- 做了什麼:發布 v3.5.0:守衛覆蓋輪(6 條缺口+行為層補驗三補強+引擎 fence 遮蔽 fast lane),其他機器 /plugin update 後才拿得到
- 為什麼:外掛更新比對版本字串不比 commit,版號不動其他機器拿不到
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json
- 詳細:minor:新增守衛與引擎修復,既有專案相容;守衛 108→133、selftest 326→339、devflow-check 20→21 組

## 2026-08-17 · guard-symmetry · v3.6.0
- 做了什麼:對稱守衛輪:第 2 層對帳推廣三站、模型分層稽核+首派攔截、雙生圖三層同步守衛、恆真斷言跨檔掃、掃描來源自釘;三輪審修(9 審查者+二次複審+終驗)全部弄壞會紅
- 為什麼:v3.5.0 獨立審查判定第 6 型假綠(不對稱保護)第三次發作:修法只套觸發實例沒推廣同類;另 prompt 級模型分層零機械層
- 落在哪:scripts/check-*(gate-twin/model-tiering/guides-fig-sync/no-stale-paths/design-contract)、hooks/(dispatch-guard/exec/selftest)、test-architecture-guards.sh、README §5、7-review.md A9

## 2026-08-17 · guides-hooks-registry · v3.6.1
- 做了什麼:hooks 註冊資訊文件化(掛哪裡/event/matcher/handler 折疊區塊)+導覽補第四支 hook 敘事+README 過期計數與幽靈敘述除鏽
- 為什麼:v3.6.0 新增的派工分層守衛只進了檔案地圖,⑥-3 敘事與速查表沒跟上;owner 另要求 hooks 註冊三要素可查且預設收合
- 落在哪:guides/guide-dev-flow.html ⑥-3、guide-quickstart.html 速查表、兩張生命週期 SVG、README、dev-setup-record.html

