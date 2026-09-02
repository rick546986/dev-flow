# CLAUDE.md

> 本檔**只放工具/環境授權**。dev-flow 的流程規則正本在
> `guides/guide-dev-flow.html`，契約句在 `docs/dev/readme-contract-extract.md`，
> 架構不變量與技術慣例在 `.claude/rules/` —— **不要往這裡搬**
> (每 session 自動注入 = 盲測全滅,見
> [guide #fence](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#fence)；
> gate 禁令在契約檔 §7)。

## Google Drive:「記憶系統」資料夾

擁有者 `rick546986@gmail.com`,已分享給 `rick.kuan@icryobank.com`(Drive 連線帳號)。

- 資料夾 ID:`18MCgqo5mEYSyItRH3ZNbJkKOPMTyt5Ry`
- 連結:https://drive.google.com/drive/folders/18MCgqo5mEYSyItRH3ZNbJkKOPMTyt5Ry

**授權**:這個資料夾底下的**讀取**與**新建檔案**不必逐次徵詢,直接做。

**仍要先問**:刪除(`trash_file`)、覆蓋既有檔案的內容、變更共用權限
(`share_file`)。這三件事不可逆或對外,授權不涵蓋。

**範圍僅限這個資料夾**。Drive 其他位置照原本規矩走 —— `.claude/settings.json`
的 `permissions.allow` 只能按工具名放行、無法按資料夾收斂,所以真正的邊界是這一節,
不是那份設定。

**這一節只服務本機的互動 session。** autoloop 那個每小時的 Cursor Automation
跑在雲端、沒有 Google 認證,它讀這個資料夾走的是公開連結的純 HTTP
(`embeddedfolderview` + `uc?export=download`,見
`docs/prompts/autoloop-contract.md` §1),完全不經過這裡列的 MCP 工具。
**不要以為那個迴圈依賴本節或 `.claude/settings.json`** —— 拿掉它們迴圈照跑,
壞掉的只會是本機 session 的便利性。
