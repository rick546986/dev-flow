# 架構不變量與慣例(<專案名>)

> 每個 session 自動載入 → **只放「看 repo 不會馬上知道、但做錯會出事」的事**。
> 判準:①這條錯了會出 bug 或被 code review 打回嗎?②新人/新 session 從檔案結構看得出來嗎?
> ①是 ②否 → 寫進來。反之刪掉。
> **禁放**:流程規則(階段/gate/模板 —— 那是 SOP 的事,寫進來會破壞討論階段的隔離)、
> 系統現況行為(那是 `docs/specs/` living spec 的事)、看目錄就知道的結構描述。
> 每條盡量附「錯誤示範 → 正確做法」或檔案位置,一條 1-3 行。
>
> **檔案位置**:`.claude/rules/*.md` 是 Claude Code 官方的專案規則路徑,**無 `paths`
> frontmatter 者每 session 自動載入**(與 `.claude/CLAUDE.md` 同優先級,`.md` 遞迴搜尋)。
> 對應的 `CLAUDE.md` 段落應改成一行指標,不要兩處都留全文(雙正本必漂移)。
>
> **選配:path-scoped 規則**(檔案長大再用,別一開始就分)。加 frontmatter 讓規則只在
> 碰到特定檔時才進 context:
> ```
> ---
> paths: ["backend/**/*.go", "ent/schema/*.go"]
> ---
> ```
> 何時值得:rules 超過 ~100 行 / 多技術棧同 repo(前端 session 吃不到後端規則)/
> 規則只對某類檔有效(如 migration 撰寫規則)。
> **不要 scope 的**:驗證指令、錯誤處理原則、命名慣例、分層依賴方向 —— 任何 session
> 都可能踩到,scope 掉等於沒寫。

## 資料層
<!-- 例:軟刪除一律 deleted_at,查詢預設帶 WHERE deleted_at IS NULL;
     unique violation(pg 23505)必攔截轉 domain error,不得讓 driver error 上浮 -->

## 交易與併發
<!-- 例:寫入路徑一律走 TxManager(可設 isolation level + idempotent retry),
     禁直接開 tx;retry 上限 5 次指數退避 -->

## 錯誤處理
<!-- 例:domain error 定義在 <path>;API 層才轉 HTTP status,domain 層不碰 HTTP -->

## 分層與依賴方向
<!-- 例:業務規則只住 domain/services/,API 層禁寫 if/else 業務判斷;
     依賴方向 api → application → domain,禁反向 -->

## 命名與慣例
<!-- 例:DB 欄位 snake_case、Go struct tag 對映規則;測試檔命名 -->

## 已知地雷(踩過的坑)
<!-- 例:<某模組> 的 cache 需在 <某動作> 後手動失效,否則計算結果會用到舊資料 -->

## 驗證指令
<!-- 例:後端 cd backend && PYTHONPATH=. python -m pytest tests/;前端 npm run build -->
