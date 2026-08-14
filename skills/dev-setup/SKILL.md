---
name: dev-setup
description: dev-flow 專案安裝器 — 打「dev-setup」即自動偵測現況並分流(初裝/升級/修復/健檢)。當使用者說「dev-setup」「初始化 dev-flow」「升級模板」「檢查基建」時啟用。
---

# dev-setup — 專案安裝器 + 基建檢查(plugin 版)

架構:skills 與 hooks 隨 plugin 全域生效(單一正本,**專案不需要裝任何 hook**);
本 skill 負責把「文檔面」裝進專案並保持可升級。
散發方式:`dev-flow` 單一 plugin,內含 `dev-talk` skill 與方法論(repo 根目錄即方法論母版)
(repo `rick546986/dev-flow`,`marketplace.json` 一個 entry:`./`)。
安裝 = `/plugin marketplace add rick546986/dev-flow` 後
`/plugin install dev-flow@dev-flow`(裝一次,dev-talk 隨附,不再是獨立 plugin);
更新 = `/plugin marketplace update dev-flow` + `/plugin update dev-flow`。
**實際 plugin root = `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`**
——會隨版本改變,腳本與檢查一律用 `${CLAUDE_PLUGIN_ROOT}` 或由自身位置推導,禁寫死。
說明書:`${CLAUDE_PLUGIN_ROOT}/guides/dev-setup-record.html`。

## 開場第一動:偵測 → 分流(使用者只打「dev-setup」時的預設行為)

不需要參數。依序偵測,判定狀態後**直接執行對應動作**(破壞性步驟仍先摘要+徵得同意):

| 偵測 | 狀態 | 動作 |
|---|---|---|
| 無 `docs/dev/` | **fresh** | 跑 install(見下);完成後跑 check 回報 |
| 有 `docs/dev/`,但 README/模板與方法論母版 `${CLAUDE_PLUGIN_ROOT}/` 有差異 | **stale** | 跑 upgrade(先列 diff 摘要徵同意)→ check |
| 有 `docs/dev/` 且與母版一致 | **current** | 只跑 check |
| check 抓到異常(缺件/殘留/陳年旗標/盲掃命中) | **broken** | 列異常+修法,**徵得同意後**跑 fix |

回報格式固定:①判定狀態一句 ②做了什麼(逐條)③check 結果表 ④還需要你決定的事(可空)。
使用者若明講子命令(`dev-setup check` / `upgrade` / `install` / `refresh` / `fix` /
`uninstall`),照該子命令走,跳過偵測。`refresh` = 重掃並比對 rules(見下),
自動分流**不會**主動跑它(重掃有成本,且結果需要人裁決)。

## install(fresh)

1. `docs/dev/` 建立:cp 方法論 `${CLAUDE_PLUGIN_ROOT}/README.md` → `docs/dev/README.md`、
   `_templates/` → `docs/dev/_templates/`、**`devflow-contract.json` →
   `docs/dev/devflow-contract.json`**(版本握手契約;doctor 無 `--contract`/
   `$DEVFLOW_CONTRACT` 明示時在此找,缺件必 fail-closed);從模板建 `STATUS.md`;
   repo root 無 `CONTEXT.md` 則從模板建。
   **改版歷史**:`mkdir -p docs/adr`(長期決策一決策一檔;編號唯一性由
   `check-adr-integrity.sh` 驗)、`docs/dev/HISTORY.md` 不存在則從
   `_templates/HISTORY.md` 建(只增不改的索引);並比照 gauntlet 散發寫入口
   `${CLAUDE_PLUGIN_ROOT}/scripts/history-append.sh` → `docs/dev/tools/history-append.sh`
   並 `chmod +x`(**該檔是 HISTORY.md 的唯一寫入口** —— 直接用 Edit/Write 改會在
   多 session 並行時靜默覆蓋,由 `history-guard` hook 擋下)。
2. `.claude/rules/arch-invariants.md`:從 `_templates/arch-invariants.md` 建檔,**並自動產草稿**
   (不留空殼):
   - 先收割既有素材:使用者指名的外部 workflow artifacts 中的架構指引
     (架構不變量/技術慣例類搬入,流程類丟棄)、專案 `CLAUDE.md` 的技術規則段、
     `docs/specs/` 裡屬慣例而非行為的敘述。未經使用者指名的外部目錄不掃描;
     原 artifacts 不移動、不覆蓋、不刪除。
   - 再派 **sonnet subagent 掃 codebase 產候選**(派工三件套;不逐檔讀全庫,採樣:
     入口/資料層/錯誤處理/測試設定 + grep 反覆出現的 pattern)。要它回報格式:
     `分類 | 規則一句 | 證據(檔:行)| 信心(高/中/低)`。
   - 落檔時**每條標 `【待確認】`**,且**每一條都要經使用者明確裁決**(採/砍/改),
     不得一句「其餘都 OK」帶過 —— 這檔錯一條會長期誤導每個 session,值得逐條看。
     問法:用 AskUserQuestion **按 `##` 分節、每題 ≤4 條 multiSelect**(勾選 = 收錄,
     沒勾 = 砍),節與節之間停;使用者明說「這節全收/全砍」可整節裁決。
     裁決後拿掉標記;**未經裁決的條目一律保留標記**(有標記 = 不可當事實引用),
     check 第 7 項會計數殘留並提醒回頭補裁。
   - **去重(避免雙正本)**:收割來源若是專案 `CLAUDE.md`,把該段落**改成一行指標**
     (如「架構不變量見 `.claude/rules/arch-invariants.md`」),不要兩處都留全文 ——
     否則改一條規則要同步兩處,漂移是遲早的事。
   - 判準提醒:只收「錯了會出事、但看 repo 不會馬上知道」的;看目錄就懂的結構描述、
     系統現況行為(→`docs/specs/`)、流程規則(→ 盲禁令)一律不收。
   - **預設單檔常駐**(無 `paths` frontmatter = 每 session 自動載入)。只有在
     rules 超過 ~100 行、或前後端等多技術棧同 repo 時,才建議拆多檔 + `paths:`
     frontmatter 做 path-scoped 按需載入(判準見模板頂註);一開始就分是過度工程。
3. `.gitignore` 加 `.devflow/`。
4. 文檔歸位(散檔 git mv 進 specs/dev/adr,引用 sed 歸零)照 README §1。
5. 未識別的既有外部 workflow artifacts 與目錄**一律保留**:不移動、
   不覆蓋、不刪除。dev-setup 只安裝 dev-flow 的文檔面,不轉換也不接管外部 workflow。
6. **evidence gauntlet 散發**:`mkdir -p docs/dev/tools` 後 cp 方法論
   `${CLAUDE_PLUGIN_ROOT}/scripts/devflow-evidence-gauntlet.sh` →
   `docs/dev/tools/devflow-evidence-gauntlet.sh` 並 `chmod +x`(Stage 7 Final Fresh
   Run 的文檔層機械檢查 E1–E13;契約正本 = 方法論 `notes/design/evidence-gauntlet.md`)。
   散發後**可執行驗證**(兩道都跑,任一不符即列 broken,不得靜默):
   ①無參數跑 → 預期印 usage 且 exit 2;
   ②`bash docs/dev/tools/devflow-evidence-gauntlet.sh ${CLAUDE_PLUGIN_ROOT}/scripts/fixtures/evidence-gauntlet/good-evidence.md`
   → 預期 exit 0(checks 數以輸出為準)。

## upgrade(stale)

- 只覆蓋 `docs/dev/README.md`、`docs/dev/_templates/`、`docs/dev/tools/`
  (gauntlet 腳本;覆蓋後重跑 install 步 6 的可執行驗證)與
  `docs/dev/devflow-contract.json`(版本握手契約;覆蓋後重跑 check 第 10 項)——
  先 diff 摘要給使用者過目。
- **絕不動 `docs/dev/<slug>/` 已產出的 feature 檔**與 STATUS/CONTEXT/rules。

## refresh(使用者說「重掃 rules」「rules 過期了」「更新架構規則」)

codebase 會演進,rules 會腐化(規則指的檔案沒了、行為變了、新慣例沒收錄)。
本模式**只比對與建議,不自動覆蓋**:

1. 重掃 codebase 產候選(同 install 步驟 2 的採樣方法)。
2. 與現有 `.claude/rules/*.md` 逐條三向比對,輸出三張表:
   - **新候選**:rules 沒有的慣例/坑 → 標 `【待確認】` 附證據,問使用者要不要收。
   - **疑似過期**:既有條目的證據**失效**(引用的檔/行不存在、內容已變、grep 命中數
     與描述不符)→ 附「當初說什麼 vs 現在是什麼」,問使用者要改、刪、還是保留。
   - **仍成立**:證據複驗過的,不動也不列(只回報數量)。
3. 使用者裁決後才落檔;裁決方式同 install 步驟 2(AskUserQuestion 分節逐條,
   未裁決者保留【待確認】)。**禁止整檔重產** —— 核可過的條目是人工判斷的成果,
   重掃不得沖掉。
4. 同場加映:掃 `CLAUDE.md` 與 rules 是否又出現重複段落(雙正本),有則提議把
   CLAUDE.md 那段改回指標。

⚠️ **不要用 `/init` 來「更新」已導入的專案**:`/init` 會覆蓋整份 CLAUDE.md,
沖掉收斂過的指標句與專案特有段落,且它重新寫的架構描述會與 rules 形成雙正本。
真要重掃 CLAUDE.md:先備份 → `/init` 產出後**人工挑**要保留的段落 → 再跑本 refresh 去重。

## check(每種分流結尾都跑)

逐項驗證列表回報,異常附建議、不自動修(fresh/stale 流程末尾自動跑;broken 才問要不要 fix):
1. **三份 JSON** jq 過:`<root>/.claude-plugin/plugin.json`(dev-flow;dev-talk 併入後
   不再有獨立 plugin.json)、`<root>/.claude-plugin/marketplace.json`(**一份、一 entry**:
   `./`)、**`<root>/hooks/hooks.json`**。hooks.json 壞掉 → 五條掛載全靜默失效,而自測
   照樣全綠 → 必驗。另比對 plugin.json 的 `version` 與 installed_plugins.json 記錄的
   版本一致(不一致 = 有人改了檔沒 bump,或裝的不是最新)。
2. 兩帳號 settings `enabledPlugins`:`dev-flow@dev-flow` 為 true(dev-talk 已
   併入,不再是獨立 enabledPlugins 項;舊值 `@local` 或 `@dev-flow-plugin` =
   尚未遷到現行 marketplace 名稱散發,應改;`known_marketplaces.json` 的 `dev-flow`
   須為 github source)。
3. **hooks/ 七支可執行**:devtalk-guard、devflow-guard、**devflow-prebash**、
   devflow-postbash、devflow-exec、selftest、**history-guard**。
   **hooks.json 應有 5 條掛載**:
   PreToolUse `Edit|Write|Read`→devflow-guard、PreToolUse `Edit|Write`→history-guard、
   PreToolUse `Bash`→devflow-prebash、PostToolUse `Edit|Write`→devtalk-guard、
   PostToolUse `Bash`→devflow-postbash。
   (實作為 shell 薄殼 + `devflow-lib.py` 與 `_*_impl.py`,改動時兩層都要在。)
4. **功能自測(可重跑)**:①執行守衛跑 `hooks/selftest.sh`(自建 temp 假 repo 後自清;
   **案數以腳本輸出為準,不在本檔寫死** —— 曾因寫死「33 案」漂移至實際 80)→ 需全過;
   ②devtalk-guard pipe 三案(非 dev-talk 放行 / 現行 SKILL 放行 /
   洩漏假檔 exit 2)。⚠️ **自測只證 script 邏輯,不證掛載** —— 掛載靠第 1、3 項。
5. dev-talk 盲掃:掃**整個 `skills/dev-talk/` 目錄**(含 SKILL.md frontmatter 的
   description —— 使用者在 skill 清單直接看到,洩漏槓桿最高;dev-talk 併入單一
   plugin 後不再有自己的 plugin.json/marketplace entry,description 洩漏風險全落在
   這份 SKILL.md 本身):
   `grep -rniE "<字詞表見 devtalk-guard.sh>" "${CLAUDE_PLUGIN_ROOT}/skills/dev-talk/"` 零命中
   (`CLAUDE_PLUGIN_ROOT` 未設時用 dev-flow plugin root 的 `skills/dev-talk/` 子目錄;
   **不寫死 `~/.claude/plugins/local/dev-talk/`** —— 併入單一 plugin 後該路徑與獨立
   marketplace entry 皆不存在)。
6. 專案面(在專案內跑時):docs/dev/README 與模板版本 vs 母版 diff;`.devflow/exec.json`
   陳年旗標(>24h 警告);舊 skills 目錄殘留(`~/.claude*/skills/dev-{talk,flow,setup}`)。
   模板檢查說明:4-spec 模板含 Verification Profile 節後(VNext),lane 依規則填 ——
   Full 完整 Profile、Fast 最小 Profile(`Risk: normal`/`Verify:`/`Negative
   Constraints:`/`Advanced verification excluded:`/`Exclusion reason:`);
   `lane: fast` + `Risk: high` 的**拒絕屬 runtime start 檢查(devflow-exec)與 G2
   gate**,本項 diff 只驗模板未漂移,不代驗個別 feature 填寫內容。
7. **rules 未核可殘留**(在專案內跑時):`grep -c '【待確認】' .claude/rules/*.md`
   非 0 → 回報「N 條未核可,該檔每 session 自動注入,未核可條目不得當事實引用」,
   並提議**按 `##` 分節批次核可**(逐條問不現實)。
8. **gate 摘要 vs §7 正本一致性**(手動跑,非掛載 hook,不計入第 3 項六支可執行清單):
   跑 `hooks/gate-consistency.sh` —— 從母版 README §7(G1/G2/G3 唯一正本)動態抽取
   每個 gate 的關鍵 token,比對 plugin `dev-flow` SKILL.md 階段表、README §3 表、
   三份模板(2-decision/4-spec/7-review)頂註送審步是否都含該 token(同義詞如
   OC/Owner Calls、DD/Drafting Decisions、回歸綠/既有全綠,靠小型映射表正規化)。
   **不把 gate 條件字串寫死在 script 裡**——寫死等於讓 script 自己變成第四份會漂移
   的複本,必須每次從正本動態重新抽取才驗得住漂移。exit 0 = 一致;非 0 = 有漂移
   或抽取失敗(anchor 不見,需人工檢查)。已知限界:只做 token 級比對,不驗語序/
   否定式,也不驗摘要多出的過期條件(§7 明文摘要=「關鍵條件一句」即正本子集,
   反向相等檢查與制度定義矛盾,故為刻意取捨非遺漏)。
   **VNext 錨**(共享契約 §1/§2):G2 新增 **Verification Profile**、**Demo
   verdict**,G3 新增 **Evidence 契約全過** —— 新條文落入 §7 正本後(Phase 3),
   動態抽取自動涵蓋,本檢查無須改碼;粗體錨的 + 串接支援 `**+ 錨**` 與 `+ **錨**`
   兩種寫法(selftest p4_ fixture 案為證)。條文未落地前,live 檢查行為不變。
9. **evidence gauntlet 散發檢查**(在專案內跑時):
   `docs/dev/tools/devflow-evidence-gauntlet.sh` ①存在且可執行(缺件 = broken,
   走 install 步 6 補);②與方法論 `${CLAUDE_PLUGIN_ROOT}/scripts/devflow-evidence-gauntlet.sh`
   diff 無差異(有差異 = stale,走 upgrade 覆蓋 —— 專案側不得自改此腳本,要改改方法論);
   ③無參數跑 exit 2(usage);④對方法論 fixture `good-evidence.md` 跑 exit 0
   (同 install 步 6 的兩道可執行驗證)。任一不符 → broken,列異常+修法。
10. **版本握手**(在專案內跑時):①`docs/dev/devflow-contract.json` 存在
    (缺件 = broken,走 install 步 1 補 —— doctor 無明示指定時就在這裡找契約,
    缺件必 fail-closed)且與方法論 `${CLAUDE_PLUGIN_ROOT}/devflow-contract.json` diff
    無差異(有差異 = stale,走 upgrade 覆蓋);②在專案內跑
    `hooks/devflow-exec.sh doctor` 可執行並看 verdict。doctor 報 `INCOMPATIBLE`
    時的指引:fail-closed 是刻意行為,不得繞過或改綠 —— 修復它列出的不相容項、
    或升級 runtime/方法論後重跑,不靜默退回舊行為。

## fix / uninstall

- fix:缺件按 install/upgrade 對應步驟補;陳年旗標 → 問使用者後 `devflow-exec.sh stop`。
- uninstall:兩帳號 enabledPlugins 設 false(hooks 隨停);專案文檔面留給使用者決定。

## 注意

- 改 plugin 後執行中 session 要 `/reload-plugins`。
- devtalk-guard = 內容硬檢;devflow 守衛 = 旗標期硬擋+偵測網;讀寫白名單其餘部分
  仍是 prompt 圍欄 —— 界線見 record html「誠實聲明」。
