# 可摺疊目錄包含樹(dir-tree)

> 人看資料夾怎麼疊、每列幹嘛。產圖:`scripts/build-dir-tree.py`。
> 牙:`scripts/check-dir-tree.sh`。畫法總冊:`_templates/diagram-style.md`
> (本家族與 vbox-fig、第 1 站三框、七站三走廊不是同一支 API)。

## 何時用

專案大、接手、跨模組、人要先看檔案脈絡。第 1 站條件式,不新增閘、
不新增必跑 hop。母版樹插在 `guides/guide-dev-flow.html#dirmap`，由本產器吐片段。

## 畫法鎖死

- 一棵 **monospace** 樹,`├─` `│` `└─`。摺疊時仍是同一棵樹。
  不是卡片／步驟圖／mermaid／橫 ASCII／`<pre>` 當圖。
- **巢狀 details**;預設全關＝只露 L1。不准 `<details open>`。
- 可點的是藍色資料夾名(`summary .name` 用 `--acc`)。
- 每列:`.g` + `.name` + `.why`。why 貼近 name,不准大 gap,不准名與 why
  中間再加 `.sep`／第二根 `│`。why 一句到兩句。不要另開說明卡。
- 每顆 `├` 半根上下都接（`::before` 往上、`::after` 往下，字高一半）。
  `└─`／`.last` 只留頭頂。不是另開一列、不拉滿 why 折行。祖先前綴
  的 `│` 不要重複畫。產器不准預插假列。
- 葉子(檔案、或不再展開的資料夾)不是 summary。
- 不要把整包 scripts／hooks 列完;用一列 `…`(ellipsis)指到盤點。
- 類名沿用手樣,不准另發明:

| class | 用途 |
|---|---|
| `.treewrap` | 樹外框 |
| `.tree` | monospace 樹 |
| `.tline` | 一列 |
| `.g` | `├─` `│` `└─` gutter;`::before` 頭頂半根 |
| `.last` | 末子 gutter,只留頭頂、腳底不畫 |
| `.name` | 檔名／夾名 |
| `.why` | 同一列右邊的用途 |

## 輸入

產器吃這份 YAML,**不要掃整棵 repo 自動猜 why**。

```yaml
title: 產品名 目錄關係
root:
  name: app/
  why: 產品根。一句到兩句。
  children:
    - name: src/
      why: 業務碼。改行為從這裡找。
      children:
        - name: domain/
          why: 領域物件。跟 src/ 其它夾分開。
    - name: scripts/
      why: 入口腳本。人工或 CI 跑。
      ellipsis: 其餘見盤點
```

`ellipsis` 在該夾底下多一列 `…`,why 就是這句。

## 輸出

html 片段(`--fragment`)或整頁。母版 `#dirmap` 必須由這支產,`--check`
對得上手改會紅。產品落到 `docs/dev/<slug>/` 一個 html,不要跟 1-discussion
掃頁三框搶槽。

## 何時不用

| 別用本家族 | 走哪條 |
|---|---|
| 第 1 站三框現況圖(`#scan-now`) | `build-scan-html.py` |
| 步驟方塊 | `vbox-fig-contract.md` + `build-vbox-fig.py` |
| 脚本盤點 | `guide-dev-flow.html#filemap` |
| 七站圖／三走廊生命週期 | `fig-lifecycle` |

不改 hop graph,不進 ship-manifest,不改契約 2.0.0。
