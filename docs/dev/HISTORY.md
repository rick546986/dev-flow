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

## 2026-08-17 · backlog-sweep · v3.7.0
- 做了什麼:清空所有已知待辦:F1~F6(ARG_MAX 靜默自壞/第7型不對稱記帳+對帳守衛/AST恆真/豁免卡fail-open/§6快照釘死)+ Backlog 3做2留 + 採用現場 G1(history-append 巢狀路徑)/G2(dev-talk 自擋)/G3(全形冒號六處+通解掃描器)+ devflow-check 四組平行化 + 新增 dev-report skill 與 devflow-report-guard hook(第7條掛載)
- 為什麼:獨立審查與兩個採用專案回報的缺陷一次清空;第7型『不對稱記帳』要機械層對帳,採用現場→母版的回報路徑要標準化且去識別化
- 落在哪:hooks/(四殼+四impl+report-guard新增+selftest 348→378)、scripts/(check-hooks-accounting/check-regex-charclass/check-devtalk-selfclean/check-devtalk-guide-sync 新增,devflow-check 平行化+註冊自審)、skills/dev-report 新增、README/PLUGIN.md/guide 記帳同步
- 詳細:docs/dev/b8-gate-twin-review-ui/7-review.md 附錄 A10;notes/dispatch-accounting-symmetry.md

## 2026-08-17 · ci-registration-audit-pipefail · v3.7.1
- 做了什麼:修 devflow-check 註冊自審在 Linux CI 的假紅:pipefail 下 grep -q 提早退出令前段 grep 吃 SIGPIPE(141),四組同炸;改 bash 內建字串比對零管線
- 為什麼:v3.7.0 推上去 CI 立即紅,macOS 本地因管線緩衝時序不同全綠(假陰性),擋住後續 session 的乾淨環境
- 落在哪:scripts/devflow-check.sh 註冊自審段

## 2026-08-18 · parallel-feature-gaps
- 做了什麼:多 feature 並行的四個制度空白寫進母版:STATUS.md 只在整合分支維護(STATUS 模板頂註+6-notes 步0+README 並行段)、合併後回滾走 revert -m 1 且禁改寫整合分支歷史(README §7 新節「合併後出事怎麼辦」+7-review Exit Checklist 路標)、Exit Checklist 新增條件式整合回歸(merge-base 為基準+comm 共同戰場交集)、多 worktree 執行環境隔離檢查項(6-notes 步0,含 atlas_schema_revisions 實例);四項的機械化判定入 README §7 強制力對照表
- 為什麼:第一個完整 feature 跑完後開兩模組並行,發現母版只講了 worktree 隔離、沒講隔離之後看板/回滾/整合回歸/環境四件事怎麼辦;owner 已裁定四個決定,本輪照決定落檔(notes/dispatch-parallel-feature-gaps.md)
- 落在哪:_templates/STATUS.md、_templates/6-implementation-notes.md、_templates/7-review.md、README.md §5/§7、guides 兩份 render

## 2026-08-18 · parallel-feature-gaps · v3.8.0
- 做了什麼:v3.8.0 發版:上一條 parallel-feature-gaps 四項並行制度空白隨模板散發(minor:模板加節+README §7 新節,既有專案 dev-setup upgrade 後相容)
- 為什麼:版本字串不動,其他機器 /plugin update 拉不到新模板
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json

## 2026-08-18 · v380-blockers · v3.8.0
- 做了什麼:v3.8.0 發版前七項必修:H-1 整合回歸演算法工具化(模板內嵌版在合併後才算交集,座標被污染 → 交集灌水或判 n-a 假綠;改為散發工具 devflow-integration-regression.sh,分岔點用 6-notes 步 0 持久化錨點 FORK_INTEGRATION_SHA,fail-closed;母版自檢 wrapper 八情境+五 mutant+模板順序+parity 掛進 devflow-check)、M-1 開 branch=四步不可拆並記錨點、M-2 STATUS 寫入紀律(限定「分支之間」+owner/merger 交接+rebase 重放)、M-3 直接補修走 hotfix branch+PR 且判準可算(Active 表新增 Branch 欄)、S-1 母版自用 STATUS 補同一條規則+check-status-policy.sh 對帳、S-2 check-file-map 地板改精確計數 EXPECTED_MAPPED_FILES=77、L-1 九條審核檔殘留清理。版號維持 3.8.0 —— 該版從未推出、無 tag 無 release,對外不存在,故續編不 bump
- 為什麼:v3.8.0 建好未推,跨家族三輪審+主線程盤點發現模板內嵌的整合回歸演算法本身是錯的(六輪審查都在查有沒有照抄、沒人查原文對不對),另六條為記帳與對稱補強;bootstrap 例外:「STATUS.md 只在整合分支維護」規則由本輪寫入,而本輪自己在 fix/v380-blockers branch 上改了 docs/dev/STATUS.md —— 規則要到本輪 merge 後才生效,且當時只有一條 branch 在跑,不存在該規則要防的衝突,僅此一次,下一輪起一律照新規則
- 落在哪:scripts/(新 devflow-integration-regression.sh、check-integration-regression-guard.sh、check-status-policy.sh;check-file-map、test-architecture-guards、devflow-check 修)、docs/dev/tools/ 散發、_templates/{7-review,6-implementation-notes,STATUS}.md、README §5/§7、skills/{dev-setup,dev-release}/SKILL.md、guides 兩份、notes 兩份加註
- 詳細:notes/dispatch-v380-blockers.md

## 2026-08-18 · v380-landing · v3.8.0
- 做了什麼:v3.8.0 發版前最後一輪 17 項落地修正:A 批會咬人 3(整合回歸工具參數死迴圈+用法輸出/dev-setup 安裝時序 mkdir 前移+baseline 收尾落地/Quickstart Stage 6 兩動線補完整錨點流程統一 feat/<slug>)+B 批守衛補強 5(順序守衛動作定位/STATUS actor 儲存格/sentinel 範例列/兩支新守衛地板+AST 外釘/baseline 段落綁定)+C 批 3(worktree cd 交接/直接補修判準 pinned remote tree+ancestor+dev-run 發布紀律/sentinel 冒號定案)+D 批 Windows 可攜 6(hooks 直譯器解析共用化 DEVFLOW_PYTHON→/usr/bin/python3→PATH,缺直譯器 fail-open,CI 回歸選 B 面,文件補環境需求)。62 個破壞實驗全紅、散發路徑演練六面全過。本輪使用 owner-push handoff:agent 在 main 完成 merge+HISTORY+STATUS 後停下,由 owner 跑 git push origin main
- 為什麼:上一輪修完檔案層,這一輪修「人真的照著用」層:參數打錯卡死終端機、fresh install 照文件做就炸、Quickstart 到 Stage 7 拿不出 fork-sha、Windows 上七支 hook 全掛只能關 plugin —— 母版守衛驗的是檔案對不對,不是照著做會發生什麼
- 落在哪:notes/dispatch-v380-landing.md(派工單)、scripts/devflow-integration-regression.sh、scripts/check-{integration-regression-guard,status-policy,dev-setup-discipline,file-map}.sh、scripts/test-architecture-guards.sh、skills/dev-setup/SKILL.md、skills/dev-run/SKILL.md、_templates/{6-implementation-notes,STATUS}.md、guides/、hooks/(新增 devflow-python-lib.sh 644)、manifests/、.github/workflows/runtime-selftest.yml

## 2026-08-18 · v380-counterproof · v3.8.0
- 做了什麼:補上兩個守衛的反證(只驗現版、沒驗壞版本):E-1 整合回歸母版自檢加三個參數解析 mutant —— M-f 把解析換回舊寫法(靠 shift 2 回傳值前進)→ 情境 I②/I③ 必須逾時、M-g 拆掉「值不得是另一個旗標」→ I⑦、M-h 拆掉「值不得為空字串」→ I⑨/I⑩;情境 I 的十個子案抽成 usage_cases() 單一正本供情境與 mutant 共用;檢查數 36→41,守衛自身 MIN_CHECKS 與 test-architecture-guards.sh 逐字互釘同步。E-2 runtime-selftest CI 加第 4 面:BASH_ENV 注入只讓 [ -x /usr/bin/python3 ] 回假的 [ 覆寫 + PATH 前置一支留腳印的 python3 shim,斷言 hook 實際用了 PATH 上那支(不設 DEVFLOW_PYTHON)。E-3 check-file-map.sh 註解改成不寫分解、數字以 scanned= 輸出為準,常數 78 未動
- 為什麼:上一輪十七項全綠,但整合回歸守衛的情境 I 從沒對改壞的複本跑過、CI 三面都顯式設 DEVFLOW_PYTHON 而短路了預設值 —— 兩者守的正好是那一輪的兩個核心修復(參數死迴圈、Windows 可攜):把解析退化成 ${DEVFLOW_PYTHON:-/usr/bin/python3}(Windows 上會壞的形態),既有三面全綠。沒有反證的保護等於沒有保護
- 落在哪:scripts/check-integration-regression-guard.sh、scripts/test-architecture-guards.sh、.github/workflows/runtime-selftest.yml、scripts/check-file-map.sh(僅註解)
- 詳細:notes/dispatch-v380-counterproof.md

## 2026-08-19 · status-commit-landing · v3.8.0
- 做了什麼:F-1 STATUS 寫入紀律拆成「動作/落點」兩層:動作(只改自己那一列 → 立刻落地 → 立刻推)照舊,落點(commit 走哪條 branch)改成依專案 git 紀律 —— 允許直接 commit 整合分支就直接做,有護欄擋(branch protection / pre-commit hook / 全域 hook)就開短命 branch → commit → 立刻 merge --no-ff 回去,兩條路都要滿足「窗口最短」。改四處:_templates/STATUS.md 頂註、docs/dev/STATUS.md 頂註、README §7 規劃層 git、guides/guide-dev-flow.html:1217 手寫鏡像卡片(renderer 不產它)。F-1-e check-status-policy.sh 的 POINTS 補 ("寫入窗口最短", ["窗口最短"]) 並配兩個負向 fixture,檢查數 30→32,守衛自身 MIN_CHECKS 與 test-architecture-guards.sh 逐字互釘同步。F-2 README 第 7 型補實例二(check-file-map.sh 註解的分解式過期且本來就算錯),明訂註解裡的分解式同受本條約束,並說明為什麼不另立守衛
- 為什麼:母版三處假設「整合分支可以直接 commit」,在裝了護欄的專案上照做就違規 —— owner 這台的全域 git-flow-guard 擋 main 上的非合併 commit,反證輪的收尾表就因此撞牆三次(0d1ebe0 commit → 419b957 merge 是繞過去的痕跡)。根因是母版把手段(直接 commit)寫成了規則,規則真正要的是窗口最短。另實查發現:check-status-policy.sh 原本四條 POINTS 沒有任何一條指向寫入窗口,把「立刻推」整句刪掉守衛全綠 —— owner 最在意的那條要求原本零守衛。⚠️ 例外聲明(比照 v380-blockers 輪):本輪在 feature branch docs/status-commit-landing 上改了 docs/dev/STATUS.md,與「STATUS 只在整合分支維護」相衝 —— 但只改頂註的規則段、Active 表與 Backlog 一列都沒動,而該規則要防的是 Active 表的靜默互蓋;且當時只有一條 branch 在跑,不存在該規則要防的衝突
- 落在哪:_templates/STATUS.md、docs/dev/STATUS.md(僅頂註規則段)、README.md、guides/guide-dev-flow.html、scripts/check-status-policy.sh、scripts/test-architecture-guards.sh
- 詳細:notes/dispatch-status-commit-landing.md

## 2026-08-19 · release-v380 · v3.8.0
- 做了什麼:v3.8.0 正式發版(打 tag + GitHub release)。本版從 v3.7.1 起累積四輪:①並行制度空白四項(STATUS 只在整合分支維護/合併後回滾走 revert -m 1/條件式整合回歸/執行環境隔離檢查項)②v380-blockers 七項必修(整合回歸演算法工具化 devflow-integration-regression.sh、開 branch 四步不可拆並記錨點 FORK_INTEGRATION_SHA、STATUS 寫入紀律、直接補修走 hotfix branch、check-file-map 改精確計數)③v380-landing 十七項落地修正(參數死迴圈、dev-setup 安裝時序、Quickstart 兩動線、Windows 可攜 hooks 直譯器解析共用化 DEVFLOW_PYTHON→/usr/bin/python3→PATH 且缺直譯器 fail-open)④反證輪(整合回歸守衛補 M-f~M-h 三個參數解析 mutant、CI 加第 4 面驗 PATH fallback)⑤STATUS 寫入紀律拆「動作/落點」兩層。既有專案 dev-setup upgrade 後相容(minor)
- 為什麼:v3.8.0 的版號字串在 08-18 就已就位但一直沒 tag 沒 release,對外等於不存在 —— 其他機器 /plugin update 拉不到;Windows 現場那台把 dev-flow 整個關掉,要等本版發出去才能重裝驗證
- 落在哪:.claude-plugin/plugin.json 與 hooks/runtime-capabilities.json(版號兩處,本輪未再動,維持 3.8.0)、docs/dev/STATUS.md(Backlog 移除已完成的 A 級發版項)
- 詳細:https://github.com/rick546986/dev-flow/releases/tag/v3.8.0

## 2026-08-19 · dispatch-agent-dispatch-layer · v3.9.0
- 做了什麼:派工分層第一輪落地 + 探針結案:①sequential 三條武裝路徑補 exec-v4 schema 與 run_id(守衛原本在最常用的那條路整支失效)②新增 agents/devflow-reviewer.md 與 devflow-adviser.md 兩支唯讀具名 subagent(tools: Read,不給 Bash/Edit/Write)③check-model-tiering.sh 補 worker-tasks == 0 → exit 2 地板④白話回覆 hook(預設關,DEVFLOW_PLAINSPEAK=1 才開)⑤四張自判表加「依據」欄⑥兩個平台探針重跑 + 第二人獨立複核結案(型別欄位名 subagent_type、plugin 型別帶 dev-flow: 命名空間)⑦契約檔最外層加 exec_state_note 記 exec-v3/exec-v4 雙軌並存⑧README 補 render 相依與 Windows 已知限制
- 為什麼:守衛只在四條武裝路徑的其中一條生效,sequential(預設、最常用)全程不設防,不修的話派工分層做什麼都是 no-op;agents/*.md 原本把型別字串標成「實測確認」但沒有第二人複核,其中 dev-flow:devflow-adviser 一次都沒被叫過
- 落在哪:hooks/_exec_impl.py、hooks/_dispatch_impl.py、hooks/_doctor_impl.py、hooks/selftest.sh、agents/(新增兩支)、hooks/devflow-plainspeak.sh、hooks/plainspeak-rules.md、scripts/check-model-tiering.sh、scripts/check-{file-map,hooks-accounting}.sh、devflow-contract.json 與 docs/dev/devflow-contract.json、README.md、docs/PLUGIN.md、guides/guide-dev-flow.html、scripts/fixtures/dispatch-guard/、notes/
- 詳細:notes/dispatch-agent-dispatch-layer.md

## 2026-08-19 · history-template-defects · v3.9.0
- 做了什麼:採用現場回報的三個缺陷修畢 + 補上宣告 Python 最低版本的守衛:①_templates/HISTORY.md 教的寫入口路徑改成「採用專案側 docs/dev/tools/ 與方法論母版側 scripts/」雙行寫法(原本只寫母版側,採用專案照著打會找不到檔)②清掉檔尾那筆可見的出廠種子紀錄(該檔禁止手改且有守衛攔截,清不掉)③check-history-integrity.sh 補 H8/H9 兩項守衛,H8 的對帳來源動態取自 skills/dev-setup/SKILL.md 不寫死路徑④scripts/build-gate-twin.py 與 check-gate-twin.sh 兩處 f-string 表達式含反斜線的寫法改成先落成變數⑤新增 scripts/check-py-floor.sh 用舊版直譯器逐檔真編譯 40 個 .py,找不到舊版就 exit 2 不退回靜態掃描⑥README 環境需求段宣告最低 3.9
- 為什麼:①②是一個採用專案在 v3.8.0 fresh install 當下踩到,而缺陷把使用者推向守衛要防的行為(照模板打指令失敗後最自然的下一步就是直接編輯那個檔);④是 scripts/build-gate-twin.py 會散發到採用專案、三個 gate 的審查頁全靠它產,但那個寫法 Python 3.12 才允許,macOS 內建 /usr/bin/python3 是 3.9 直接 SyntaxError 整支讀不進去,而挑直譯器的順序把系統內建排在 PATH 之前;上述四件在 v3.8.0 都已出貨,而當時全部既有機械檢查皆綠 —— 零覆蓋才是根因
- 落在哪:_templates/HISTORY.md、scripts/check-history-integrity.sh、scripts/build-gate-twin.py 與 docs/dev/tools/ 副本、scripts/check-gate-twin.sh、scripts/check-py-floor.sh(新增)、scripts/devflow-check.sh、scripts/check-file-map.sh、scripts/test-architecture-guards.sh、README.md、guides/guide-dev-flow.html、docs/dev/STATUS.md
- 詳細:notes/dispatch-history-template-defects.md

## 2026-08-19 · release-v390 · v3.9.0
- 做了什麼:記一筆偏差:需求正本 §10 裁決 10 要求「拆兩版」(§7 守衛在 sequential 生效那批單獨一版、§4 A′ 兩支審查者那批再一版),實際沒有達成 —— 兩批在同一個窗口進了 main(§7 是 812a9fb+c9411c2,A′ 是 a44b92e+f3d9e4a),3.9.0 一版全包
- 為什麼:裁決 10 要的隔離目的是「出事時分得出是哪一批造成的」,現在分不出來了。補兩個標籤的路(3.9.0 指 c9411c2、3.10.0 指 f3d9e4a)被 owner 2026-08-19 否決:c9411c2 的 plugin.json 寫的是 3.8.0,標籤叫 3.9.0 名實不符,而發版器存在的理由正是比對那個字串 —— 補得不乾淨不如記偏差
- 落在哪:.claude-plugin/plugin.json、hooks/runtime-capabilities.json(版號兩處)

## 2026-08-20 · issue-345-fixes · v3.9.1
- 做了什麼:doctor 在 Windows 上的兩項紅各自修掉(腳本路徑被當成一整句命令、證據工具印出的路徑形式與比對端對不上),安裝器比對 README 時兩側都先統一行尾,開工訊息不再把固定釘住的 .gitignore 算進「既有髒檔」;CI 補上檢查 Python 下限所需的舊版直譯器。⚠️ Windows 整體仍未全綠 —— 派工單 §2.1(兩個 /tmp)與 §2.2(Python 直接執行 .sh)未動
- 為什麼:doctor 是一項紅就整體判不相容,而那兩項原本被寫成同一個成因,照著舊敘述修只會修好一半;README 比對只有母版側做正規化,Windows 上每一行都差一個換行字元、每次健檢都被判成過期並覆蓋一次
- 落在哪:hooks/_doctor_impl.py、hooks/_exec_impl.py、scripts/devflow-evidence-gauntlet.sh 與 docs/dev/tools/ 副本、skills/dev-setup/SKILL.md、notes/dispatch-windows-parity.md、.github/workflows/devflow-ci.yml
- 詳細:issue #3/#4/#5;https://github.com/rick546986/dev-flow/releases/tag/v3.9.1

## 2026-08-20 · issue-7-path-separator · v3.9.2
- 做了什麼:Windows 上開得了工了:scope 內的檔不再被判成 scope 外,而且執行期禁讀上游、契約 hash 釘住這兩道原本在 Windows 靜默失效的保護真的會擋
- 為什麼:守衛靠字串比對判範圍,但路徑有兩個來源 —— git 一律正斜線、Windows 的 Python 吐反斜線,逐字比對永不命中。過度阻擋那面(拒絕啟動)吵、看得見;保護那面(禁讀上游整條放行、契約 hash 記錄零個檔)靜默,而產出看起來完整
- 落在哪:hooks/devflow-lib.py(新增 to_posix,四個出入口各過一次)、hooks/selftest.sh(w1 組 6 案,MIN_CASES 392→398)、scripts/test-architecture-guards.sh、tests/parallel-stage6/contract_ref.py、hooks/devtalk-guard.sh
- 詳細:issue #7;https://github.com/rick546986/dev-flow/releases/tag/v3.9.2

## 2026-08-20 · windows-parity-round2 · v3.10.0
- 做了什麼:收四項:①測試腳本的 /tmp 在 Git Bash 與 Windows 原生 Python 解讀不同(後者解成 C:\tmp 且該目錄常存在,不噴錯只是安靜找不到樣本),兩個入口各正規化 TMPDIR 一次;②三處 subprocess 直接 exec .sh 改顯式帶 bash(Windows 無 shebang,WinError 193 整支崩);③dev-setup check 的散發副本比對集合改成取自檔案地圖散發面標註;④去識別化守衛掃描面從 .devflow/reports/ 放寬到 .devflow/ 全部 .md
- 為什麼:①②是 Windows 上 selftest 71 案紅與 devflow-check 崩的根因;③母版側 parity 守衛早已 map-driven,採用專案側仍逐支硬列且已真的漏掉 history-append.sh(HISTORY.md 唯一寫入口,G1 巢狀 bug 出處)—— 第 7 型不對稱記帳;④回報檔放在 .devflow/ 但不在 reports/ 就靜默繞過,絕對路徑因此貼進 public issue
- 落在哪:hooks/selftest.sh(TMPDIR 區塊+w2 兩案+report-guard 兩案,MIN_CASES 398→402)、scripts/devflow-check.sh(TMPDIR 逐字副本)、scripts/test-architecture-guards.sh(check_twin_block 新對帳+靜態釘)、hooks/_report_impl.py、skills/dev-setup/SKILL.md(check 第 13 項)、scripts/check-dev-setup-discipline.sh(紀律⑩,MIN_CHECKS 15→18)、scripts/check-methodology-corrections.sh、scripts/check-realworld.sh、README.md §7 已知限界
- 詳細:notes/dispatch-windows-parity.md §2.1/§2.2

## 2026-08-20 · agent-memory-v3
- 做了什麼:把 agent 記憶從人工維護的 Markdown 換成結構化、可 Git 同步的七類記憶(.dev-flow/),並新增本機檢索索引與 LVP 式的現況真相驗證
- 為什麼:舊載體(CONTEXT.md/HISTORY.md)沒有 identity、沒有狀態、也分不出現況與願景;換一台機器就等於失憶,而且腐化時沒有任何機制會發現
- 落在哪:memory/(新增)、skills/dev-setup 與 dev-run 與 dev-talk、README §16、scripts/check-memory-architecture.sh、scripts/check-status-policy.sh(W6 順序鏈)、_templates/CONTEXT.md(移除)
- 另含耐久性屏障:更正在固化成功前不動現況、revision 只有真的寫進 .dev-flow 才標 durable、fact 整檔寫回逐筆過 Signal Gate、Stage 6 收尾補 memory commit 與 durable-check
- 詳細:長期決策 docs/adr/0003-agent-memory-two-layer-split.md

## 2026-08-28 · v320-host-plugins · v3.20.0
- 做了什麼:Cursor／Codex／Grok 各自 plugin 安裝；補助手樣進 example/subsidy-3-0-plus；七站審頁產器與 Pages 已在 main。
- 為什麼:Claude 以外只能 git pull + 手掛；plugin.json 字串不動，其他機器 update 會靜默不拉。
- 落在哪:.claude-plugin/ .cursor-plugin/ .codex-plugin/ hooks/runtime-capabilities.json example/subsidy-3-0-plus/ notes/prompt-html-gap-loop.md

## 2026-08-28 · v3201-patch · v3.20.1
- 做了什麼:#65 修正進版號；清補助手樣對照殘件與過時 html-gap 便條。
- 為什麼:Claude /plugin update 只看 version 字串；停在 3.20.0 會靜默不拉 #65。
- 落在哪:.claude-plugin/ .cursor-plugin/ .codex-plugin/ hooks/runtime-capabilities.json example/subsidy-3-0-plus/ notes/prompt-html-gap-loop.md docs/dev/HISTORY.md

## 2026-08-28 · field-fixes-six
- 做了什麼:六項現場修復:upgrade 刪 pack 停出殘件、產圖 Python 3.12+ venv、gate-twin 2/4 站直式 SVG、worktree 雙生頁併回整合線、HISTORY 出廠種子選配清理、主機 --probe 印下一句安裝指令
- 為什麼:採用樹仍留 _templates/CONTEXT.md、macOS 3.9 靜默裝不出 markdown-it-py 4、審查頁仍吐橫 ASCII pre、worktree 雙生頁不知該併哪條線、出廠 HISTORY 種子清不掉、Codex/Grok/Cursor 更新指令對不上現場
- 落在哪:scripts/devflow-upgrade-leftovers.sh scripts/test-upgrade-leftovers.sh hooks/_doctor_impl.py scripts/build-gate-twin.py scripts/devflow_twin_ui.py scripts/history-append.sh scripts/check-host-adapter.sh skills/dev-setup/SKILL.md docs/PLUGIN.md _templates/

## 2026-08-29 · field-fixes-six-b
- 做了什麼:半點審第 3 顆牙:example 2-decision／4-spec 用 3.20.1 產器重生直式 SVG;第 4 站行為圖契約真咬 SVG-not-pre。doctor 對系統 leftover markdown-it-py 3.x 改 info,不連坐 EXTERNAL_RUNTIME 握手。
- 為什麼:審 B FAIL:example 雙生頁仍是橫 ASCII pre,契約只釘置頂 id。CI selftest 因 runner 系統 python 帶 mdit 3.0.0 整組 doctor 紅。
- 落在哪:example/contract-expiry-reminder/{2-decision,4-spec}.html scripts/build-stage{2,4}-html.py scripts/check-stage4-rs-contract.sh scripts/check-gate-twin.sh hooks/_doctor_impl.py

## 2026-08-29 · field-fixes-six-c
- 做了什麼:CI 兩紅修復:doctor 不寫死系統 python 路徑字串;stage2 產器吐 Owner Calls／依據表,example 2-decision 直式 SVG 與自判表並存
- 為什麼:半點審重生蓋掉自判表,methodology/check-selfjudgment-tables 32/36;_doctor_impl 字串觸發 runtime-selftest 禁寫死路徑
- 落在哪:hooks/_doctor_impl.py scripts/build-stage2-html.py example/contract-expiry-reminder/2-decision.html scripts/check-selfjudgment-tables.sh

## 2026-08-29 · field-fixes-six-d
- 做了什麼:doctor 對系統 leftover markdown-it-py 3.x 維持 info:DEVFLOW_PYTHON 指到系統 python3 不算專案 venv
- 為什麼:CI selftest 用 DEVFLOW_PYTHON=$(command -v python3) 覆寫,系統 leftover 3.x 被判成 env 連坐握手,EXTERNAL_RUNTIME 仍紅
- 落在哪:hooks/_doctor_impl.py

## 2026-08-29 · engine-fence-masking-exit
- 做了什麼:關 engine-fence-masking 第 7 站出貨文書:status 改 shipped、Exit Checklist 誠實收尾、產 7-review.html
- 為什麼:功能早已合進 main,STATUS Backlog 那列寫的就是收尾文書沒關;本刀只補文書,不動引擎與 STATUS.md
- 落在哪:docs/dev/engine-fence-masking/{7-review.md,7-review.html}、docs/dev/HISTORY.md

## 2026-08-29 · ship-manifest
- 做了什麼:散發清單收成一份正本 docs/dev/ship-manifest.json(每列 source/destination/mode);install/check/baseline/upgrade、dev-release、parity、檔案地圖散發面都讀這一份
- 為什麼:新加工具要改八處,漏一處就假綠;掃 docs/dev/tools/ 當 expected set 則正副本同刪全綠(第 4 型)
- 落在哪:docs/dev/ship-manifest.json scripts/devflow_ship_manifest.py scripts/check-ship-manifest.sh skills/dev-setup/SKILL.md skills/dev-release/SKILL.md scripts/check-integration-regression-guard.sh scripts/check-dev-setup-discipline.sh scripts/devflow-check.sh guides/guide-dev-flow.html

## 2026-08-29 · bash-write-prevent
- 做了什麼:Bash 寫 scope 外改成當場攔:解出寫路徑後走與 Edit 同一套判定,檔不落盤;三邊共同入口是 check-write-scope.sh --action
- 為什麼:engine-fence-masking 第 7 站觀察到 Edit 當場擋、Bash 先寫再 postbash 示警;STATUS Backlog C 列的就是這落差
- 落在哪:hooks/devflow-lib.py hooks/_guard_impl.py hooks/_prebash_impl.py hooks/selftest.sh scripts/check-write-scope.sh scripts/test-write-scope.sh scripts/devflow-check.sh scripts/check-file-map.sh scripts/test-architecture-guards.sh guides/guide-dev-flow.html

## 2026-08-29 · verbosity-trim
- 做了什麼:方法包技能、模板頂註、guides／README 收掉重複贅字；契約句與守衛釘句不動
- 為什麼:同一件事講三遍，讀的人要掃很長才碰到要做的
- 落在哪:skills/dev-setup/SKILL.md skills/dev-run/SKILL.md skills/dev-talk/SKILL.md skills/dev-flow/SKILL.md _templates/ README.md guides/guide-dev-flow.html

## 2026-08-29 · status-single-writer
- 做了什麼:STATUS 表列唯一寫入口 scripts/status-update.sh:目錄鎖包住 read-modify-write、寫完蓋章;手改表列章對不上就紅;feature branch 拒改正本表列。test-status-update.sh 含無鎖互蓋會丟列、拿掉蓋章檢查的 mutant 對手改檔又綠。未進 ship-manifest、未升版。
- 為什麼:v3.8.0 只縮寫入窗口,同 checkout 兩 session 手改仍 last-write-wins 且不報錯。HISTORY 已有單寫入者,STATUS 沒有。本輪是 Backlog「真正的單寫入者」那列的牙,不划掉該列(main 上由 merger 收)。
- 落在哪:scripts/status-update.sh scripts/test-status-update.sh scripts/check-status-policy.sh scripts/devflow-check.sh scripts/check-file-map.sh scripts/test-architecture-guards.sh _templates/STATUS.md docs/dev/STATUS.md(只改頂註+蓋章,Active/Backlog 表列未動) guides/guide-dev-flow.html

## 2026-08-29 · status-refresh-stamp-gate
- 做了什麼:--refresh-stamp 必須表列已與基準相同才准補章;正本還要 HEAD=main。手改表列再 refresh-stamp 拒,章不變。fixture 帶 --base-file 且表列相同仍可補章。
- 為什麼:--refresh-stamp 原本不查 branch、不查表列,手改一列再補章,verify-stamp 與 check-status-policy 全綠。後面若把 parallel canonical ref 寫進 STATUS,這扇門會把假座標蓋成合法章。
- 落在哪:scripts/status-update.sh scripts/test-status-update.sh scripts/check-status-policy.sh guides/guide-dev-flow.html

## 2026-08-29 · overlap-ref · v3.20.1
- 做了什麼:定義「直接補修」檔案重疊用的單一座標 OverlapRef:sequential 就是 Branch;parallel 合回並 push 前是已發布的 integration/<slug> tip,之後變成 Branch。status-update.sh --print-overlap-ref 印出這一個;解不出來 fail-closed,不猜 Lane、不拼第二個 ref。未升版、未進 ship-manifest、未划 Backlog。
- 為什麼:C-2 把 parallel 一律 fail-closed,是因為當時沒有一個 STATUS/runtime 可提供的 canonical integration ref。沒有這一個座標,算法就會自己在 feature tip 與 integration tip 之間猜,或把 Lane 當 mode。
- 落在哪:scripts/status-update.sh scripts/test-status-update.sh scripts/check-status-policy.sh scripts/test-architecture-guards.sh _templates/STATUS.md README.md guides/guide-quickstart.html guides/guide-dev-flow.html docs/dev/HISTORY.md

## 2026-08-29 · late-owner-change-tooth · v3.20.1
- 做了什麼:晚改可見行為鎖進 Stage 2／4 hop＋模板:G3 未過先回寫 Decision 再走 4→5→6→7;G3 已過另開薄刀。C6 擋「不採 Decision、跟 4-spec」停成 DD。
- 為什麼:owner 改口後 agent 只改 4-spec,把 2-decision 戰火停成 Drafting Decision,1／2／5／7 過期。覆寫已核 Decision 不是合法 DD。
- 落在哪:skills/dev-flow/stage2/nodes/N3-write-md.md skills/dev-flow/stage4/nodes/{N1-handoff,S4-dd}.md _templates/{2-decision,4-spec}.md scripts/check-spec-gate.sh scripts/check-devstage{2,4}-graph.sh scripts/fixtures/spec-gate-late-owner/ guides/guide-dev-flow.html

## 2026-08-29 · example-subsidy-stage4 · v3.20.1
- 做了什麼:依現行 _templates/4-spec.md 重寫 example/subsidy-3-0-plus/4-spec.md 並用官方產器重生 4-spec.html；Stage 4 牙改認兩個範例 fixture
- 為什麼:Backlog「第二個範例 feature」：破唯一範例自證循環。手樣 R/S 鎖兩格／切日／年齡／OPU 小字；Risk 從非法 medium 改 high。不代填 Human verdict、不升版
- 落在哪:example/subsidy-3-0-plus/4-spec.md example/subsidy-3-0-plus/4-spec.html scripts/devflow-check.sh scripts/check-selfjudgment-tables.sh scripts/check-stage4-rs-contract.sh scripts/check-devstage-fig-text.sh docs/dev/HISTORY.md

## 2026-08-29 · subsidy-two-cell-align
- 做了什麼:整條 example/subsidy-3-0-plus 回望對齊 PLUS 畫面兩格：2-decision 改選定 2B、2A 三格改列 Rejected（完工時使用者改兩格）；1 驗收雛形改兩格、歷史問答留當時三格；4-spec DD-1 不再說兩份打架；5/6/7 用語對齊。官方產器重生 1/2/4/5/7 html
- 為什麼:Owner lock：PLUS 畫面兩格不是三格。先前只改第 4 站，2A 三格 vs R-2 兩格是假矛盾。不改產品行為、不填 verdict、不升版
- 落在哪:example/subsidy-3-0-plus/{1-discussion,2-decision,4-spec,5-tasks,6-implementation-notes,7-review}.{md,html} docs/dev/HISTORY.md

## 2026-08-29 · release-v3-20-2 · v3.20.2
- 做了什麼:發 v3.20.2：C6 晚改可見行為牙、補助手樣兩格第二 fixture、STATUS 單寫入／OverlapRef／活針、F/S/W 關帳等已在 main 的刀讓 Claude plugin update 拉得到
- 為什麼:Claude 比 plugin.json version 字串；3.20.1 字串不變則 /plugin update 回 (no content) 且無提示
- 落在哪:.claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json hooks/runtime-capabilities.json

## 2026-08-29 · probe-empty-tree-fail-closed · v3.20.2
- 做了什麼:--probe 無專案根不得 probe: ok；採用樹必須帶根+DEVFLOW_ROOT；方法包無參數改印 pack-self-check；detect_host 優先序寫進 SKILL；test-host-adapter 地板 46→54
- 為什麼:SKILL 教的無參數 --probe 空樹 missing=[] 恆綠（第 4 型假綠），採用專案以為掛載已驗過
- 落在哪:scripts/check-host-adapter.sh scripts/test-host-adapter.sh skills/dev-setup/SKILL.md

## 2026-08-30 · release-v3-20-3 · v3.20.3
- 做了什麼:發 v3.20.3：--probe 空樹不得 probe: ok（#79 / #78）已在 main，讓 Claude plugin update 拉得到
- 為什麼:Claude 比 plugin.json version 字串；3.20.2 字串不變則 /plugin update 回 (no content) 且無提示
- 落在哪:.claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json hooks/runtime-capabilities.json

## 2026-08-30 · path-after-subcommand · v3.20.3
- 做了什麼:dev-memory --path 兩種順序都通；usage 與 SKILL 1b/14 改成 --path 在子命令前；subparser --path 用 SUPPRESS
- 為什麼:SKILL 寫 setup --path / doctor --path，argparse 只收子命令前 → exit 2 unrecognized arguments，dev-setup 步 1b 紅
- 落在哪:memory/dev-memory.py memory/tests/test_cli.py skills/dev-setup/SKILL.md

## 2026-08-30 · path-after-subcommand-mem4 · v3.20.3
- 做了什麼:MEM-4 負向錨改對新的 doctor parser 寫法（_add_path 三行），毒才能種出 init
- 為什麼:CI architecture/test-architecture-guards：MEM-4 舊錨 sub.add_parser("doctor").set_defaults 已不在，mutation 沒種毒 → 預期 fail 實得 pass
- 落在哪:scripts/test-architecture-guards.sh

## 2026-08-30 · pages-noarg-not-usage · v3.20.3
- 做了什麼:SKILL pages 驗證句拆開：--help 才是 usage exit 2；無參數會真組 public/，健檢不得用無參數
- 為什麼:3.20.2 起 SKILL 把無參數跟 --help 併成 exit 2，照做會在採用專案根長出 public/ 並誤以為驗到 usage
- 落在哪:skills/dev-setup/SKILL.md

## 2026-08-30 · release-v3-20-4 · v3.20.4
- 做了什麼:發 v3.20.4：#81 pages 驗證句拆開、#82 --path 子命令後也通，已在 main，讓 Claude plugin update 拉得到
- 為什麼:Claude 比 plugin.json version 字串；3.20.3 字串不變則 /plugin update 回 (no content) 且無提示
- 落在哪:.claude-plugin/plugin.json .cursor-plugin/plugin.json .codex-plugin/plugin.json hooks/runtime-capabilities.json

## 2026-08-30 · test-status-update-main-count
- 做了什麼:main 上「拒改正本」略過從 1 案改成 2 案,對齊 feature 的 --set / --refresh-stamp 兩顆牙;MIN_CASES 維持 30
- 為什麼:main-push 的 abbrev-ref 是 main,只跑 29 案撞地板;同樹 PR 是 detached HEAD 走 else 兩案所以綠。產品寫入者未改
- 落在哪:scripts/test-status-update.sh docs/dev/HISTORY.md

## 2026-08-31 · readme-pages-html-links
- 做了什麼:README 的 *.html 超連改成 GitHub Pages 絕對網址,GitHub 上點開是渲染頁不是 blob 原始碼;pages-hosting 牙加咬 README 相對路／blob
- 為什麼:相對路 guides/*.html 在 GitHub README 會解析成 blob/main/... 顯示 HTML 原始碼,不是渲染頁
- 落在哪:README.md、scripts/check-pages-hosting.sh、guides/guide-dev-flow.html 檔案地圖列

## 2026-08-31 · readme-filemap-one-link
- 做了什麼:README 同一個 #filemap 只留一條可點超連;標籤拿掉巢狀反引號,GitHub 不再把標籤跟網址拆成兩截
- 為什麼:巢狀 [flow `#filemap`] 破 GitHub renderer,標籤跟 URL 各顯一次甚至退化成 blob;§4 與 master-only 頁尾又是同一條 URL
- 落在哪:README.md docs/dev/HISTORY.md

## 2026-08-31 · guide-dir-map
- 做了什麼:新增 guides/guide-dir-map.html：母版五塊目錄關係用 vbox-fig 直式 SVG 重畫，巢狀 details 分五層摺疊
- 為什麼:人要看資料夾怎麼疊，不是 #filemap 那五張腳本清單；入口 README 不准重畫樹，只留一條 Pages 超連
- 落在哪:guides/guide-dir-map.html README.md guides/guide-dev-flow.html#filemap docs/dev/HISTORY.md

## 2026-08-31 · guide-dir-map-tree
- 做了什麼:guide-dir-map 改成 monospace 目錄樹：預設只露 L1，點資料夾才用 ├─ │ └─ 接子層
- 為什麼:人要的是資料夾包含關係，不是 hop 流程也不是 vbox-fig 步驟方塊
- 落在哪:guides/guide-dir-map.html docs/dev/HISTORY.md

