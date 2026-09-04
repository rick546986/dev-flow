# dev-flow

七站開發流程，給 agent 跑、人還握著方向（不拿走控制，不像 GSD／BMAD 整包代操）。

<p align="center">
  <a href="https://rick546986.github.io/dev-flow/guides/fig-flow-full.html">
    <img src="https://rick546986.github.io/dev-flow/guides/fig-flow-full.svg" alt="七階段流程圖含 Gate 與能力分層">
  </a>
</p>

## 安裝

兩層，不要混。

**A) 裝方法包**（這台機器／這個主機一次）。不是 `dev-setup`。

- **Claude**：裝：`/plugin marketplace add rick546986/dev-flow` 後 `/plugin install dev-flow@dev-flow`。更新：`/plugin marketplace update dev-flow` + `/plugin update dev-flow`。
- **Cursor**：Dashboard → Plugins → Import from Repo `rick546986/dev-flow`。更新：Refresh 在已匯入的 rick546986/dev-flow 那一列。
- **Codex**：沒有 `plugin install`／`plugin update`。裝：`codex plugin marketplace add rick546986/dev-flow` 後 `codex plugin add dev-flow@dev-flow`。更新：`codex plugin marketplace upgrade dev-flow` 再 `add` 一次。
- **Grok**：不要發明 Grok marketplace。Grok Bot 吃 Cursor 帳裝好的同一包。本機技能庫可掛整棵 `.grok/skills`。

細節與 `DEVFLOW_ROOT`：[guide #host](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#host)。安裝長文在 [docs/PLUGIN.md](docs/PLUGIN.md)。

**B) 產品專案**：進專案根目錄打 `dev-setup`（不帶參數）。這不是 `/plugin update`。

## 開始

[開工](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#start)

<!-- devflow:master-only:start -->
母版目錄樹見 [目錄關係](https://rick546986.github.io/dev-flow/guides/guide-dev-flow.html#dirmap)，不要在入口重畫樹。
<!-- devflow:master-only:end -->
