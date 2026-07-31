---
name: dev-setup
description: dev-flow 基建安裝與健康檢查 — devtalk-guard hook、skill 兩帳號 md5 成對、盲原則洩漏掃描。當使用者說「dev-setup」「檢查 dev-flow 基建」「guard 檢查」時啟用。
---

# dev-setup — dev-flow 基建

安裝說明(人讀版):`~/dev/dev-flow/dev-setup-record.html`
基建清單:
1. **guard script**:`~/dev/dev-flow/_infra/devtalk-guard.sh`(單一正本,兩帳號 hook 共用)
2. **hook 掛載**:兩帳號 settings.json → `hooks.PostToolUse`(matcher `Edit|Write`)呼叫上述 script
3. 本 skill(兩帳號成對)

## check(預設動作;使用者說「dev-setup」或「dev-setup check」)

逐項驗證,結果列表格回報,異常附修復建議、**不自動修**(使用者說 fix 才修):

1. script 存在且可執行:`test -x ~/dev/dev-flow/_infra/devtalk-guard.sh`
2. 兩帳號 hook 都掛著:
   `jq -e '.hooks.PostToolUse[]|select(.matcher=="Edit|Write")|.hooks[]|select(.command|contains("devtalk-guard"))|.command' <settings.json>`
3. skill md5 成對:dev-talk / dev-flow / dev-setup 各自兩帳號 `md5 -q` 相等
4. dev-talk 盲掃:`grep -rnE "<字詞表見 script 內 grep>" ~/.claude/skills/dev-talk/` 零命中
   (兩帳號都掃;唯一合法例外 = 無,命中即異常)
5. guard 功能自測:以假 JSON pipe 進 script 三案(非 dev-talk 路徑放行 / 乾淨檔放行 /
   洩漏檔 exit 2),見 record html 內指令

## fix(使用者明說才做)

- script 遺失 → 告知從 record html 內容重建 + `chmod +x`
- hook 遺失 → 照 update-config 流程 merge 進對應 settings.json(先讀後併,禁覆蓋既有 hooks)
- md5 漂移 → 先問使用者哪邊為準,再 cp + 複驗
- 盲掃命中 → 修 dev-talk 檔移除字眼(或報使用者裁決誤報)

## uninstall

兩帳號 settings.json 移除該 PostToolUse 條目(matcher Edit|Write、command 含 devtalk-guard);
script 與本 skill 保留無害,可一併刪。

## 注意

- settings.json 的 hook 在 session 開始時載入;改完設定,舊 session 要 `/hooks` 重載或重開才生效。
- guard 是**內容硬檢**(檔案寫入後掃描),不是權限硬擋 —— dev-talk 的讀寫白名單仍屬
  prompt 級圍欄,界線見 `~/dev/dev-flow/README.md` §11。
