# 站審 html 掛 Pages(真的 html 頁)

> Pages 要掛的是站審 html,不是倉庫裡點 html 看原始碼。
> 本檔是三邊食譜的**正文**。GitHub／GitLab／Gitea 薄殼不抄正文。
> 本機對應是既有 `serve`,不要另開一套本機伺服器。
> 不改 `build-gate-twin.py` STAGES、不改掃頁／第 6 站產檔器、不改 #61 產器、
> 不改 #60 verdict 正本。補助產品詞不得當通用規則。

## 掛什麼(鎖死)

站審 html 檔名鎖定,跟 example 同名:

`docs/dev/<feat>/{1-discussion,2-decision,5-tasks,6-implementation-notes,7-review}.html`

`example/<feat>/` 底下同名 html 一併掛。

圖用相對路 `shots/`(與 html 同目錄)。Pages 跟本機同一棵相對路徑,
不要改寫成絕對 URL、不要另開 `docs/` source path。

`guides/` 一併鏈進同一棵樹,既有 guide 超連才不會斷。

`scripts/build-public-docs.py` 只轉 ADR／HISTORY,不是站審 html。

## 三邊薄殼(正文只這一份)

| 邊 | 薄殼 | 掛法 |
|---|---|---|
| GitHub | 本節超連規則(母版已開根目錄 Pages,source=`main` path=`/`) | 不要改成另一個 source path |
| GitLab | `.gitlab-ci.yml` `pages` job,artifacts `public/` | 呼叫食譜正文腳本組樹 |
| Gitea | `.gitea/workflows/pages.yml`(pages branch 或 Actions) | 呼叫同一支腳本,掛同一棵 html |

食譜正文腳本:`scripts/publish-pages.sh`(散發面 `docs/dev/tools/publish-pages.sh`)。
CLI 用 `--root`(不是位置參數)。產品專案走 `dev-setup` 同一條發散路拿到這支,
薄殼沒有才從方法包抄,已有不覆蓋。

### GitHub 超連規則

母版已用根目錄 Pages。超連:

`https://<owner>.github.io/<repo>/<path-to-html>`

例:`https://rick546986.github.io/dev-flow/docs/dev/<feat>/7-review.html`

不要改 source path 去掛別的目錄,會把現有 guides 搞壞。

### GitLab

`pages` job 把審查 html + `shots/` + `guides/` 鏈進 `public/`,保相對路徑。
組樹只准呼叫 `publish-pages.sh --root`,不要在 yml 裡再抄一份複製清單。

### Gitea

通常 `pages` branch 或 Actions。薄殼同樣呼叫 `publish-pages.sh --root`,
掛出同一棵 html(相對路與 GitHub／GitLab／本機相同)。

## 本機

`serve` 就是 Pages 的本機對應。開同一棵站審 html:

`python3 scripts/devflow_gate.py serve --root .`

然後開 `http://127.0.0.1:8765/docs/dev/<feat>/7-review.html`。
不要另開一套本機伺服器。CLI 用 `--root`,不是位置參數。

## 何時不用

| 別用本檔 | 走哪條 |
|---|---|
| Human verdict 怎麼落盤 | `notes/design/gate-verdict-write.md`(#60 正本,不改) |
| 第 7 站截圖槽版面 | `notes/design/stage7-review-ui-contract.md` |
| 第 6 站審碼 hunk | `notes/design/stage5-review-ui-contract.md` |
| ADR／HISTORY 人頁 | `scripts/build-public-docs.py` |
