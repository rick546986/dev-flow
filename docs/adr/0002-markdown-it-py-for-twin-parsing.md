# 0002. gate twin 解析層採用 markdown-it-py(推翻散發工具零相依立場)

- Status: accepted
- Date: 2026-08-15
- Source: docs/dev/b8-gate-twin-review-ui/7-review.md(附錄 A7)

> 晉升條件(三條件**全中**才立此檔,否則留在 2-decision 就好):
> 難逆轉 + 反直覺 + 真 trade-off。

## Context

`build-gate-twin.py` 會被 dev-setup 散發到採用專案,原始立場是零外部相依
(「多一個相依就多一個在別人機器上跑不起來的理由」,寫進了工具 docstring)。
但手刻正則解析 markdown(fence 遮蔽、章節切割)在三輪獨立審查共爆 28 條 finding,
其中兩條是修上一輪時引入的新 HIGH、一條已發生在出貨物上(P4:整節從產出 html
消失而 60 項守衛全綠)。每補一個邊界就冒出下一個,靠自審不可能收斂。

## Decision

解析層(什麼算 fence、什麼算標題)的判斷來源改用 markdown-it-py==4.0.0 的
CommonMark token stream;等長遮蔽 + span 切原文的骨架不變。**渲染層維持零相依**
(md_block 的極簡轉換不動)。相依 fail-loud:缺套件或版本不符 → 繁中訊息 + exit 2,
不吐 traceback、不靜默降級回正則(降級 = 兩邊 diverge 卻不吭聲)。

反直覺點:散發工具通常避免相依 —— 但這個 repo 的 renderer 已釘死同一套件同一版本
(scripts/requirements-methodology-render.txt),「散發到別人機器跑不起來」的顧慮
由 fail-loud + dev-setup 散發段的相依交代與散發後探測承接,不再成立。

## Considered Options

1. 繼續手刻正則補邊界 —— 已被三輪審查證偽(28 條 finding,每輪都有新破口)。
2. 表格解析也換 token stream(K-4)—— 否決:markdown-it 遵 GFM 會截斷多於表頭的欄,
   正是 n5 修掉的缺陷,換了會回歸。表格切格維持遮蔽版逐行法。
3. hooks runtime 也吃 markdown-it —— 否決:hooks 在採用端經 plugin cache 直跑、
   無 pip 環節,核心 Stage 6 runtime 綁 pip 相依是不同量級的採用負擔。
   引擎側 fence 問題(幽靈任務)以 twin 警告現形,引擎修法另列 Backlog。

## Consequences

- 換到:fence/標題判斷這一整類 bug 的來源消失(P1/P2/P4/N1/N3 同類);
  對母版範例三站 byte-identical 完成替換,行為零漂移。
- 付出:採用專案跑 twin 需 `pip install 'markdown-it-py==4.0.0'`(缺了 exit 2
  並印安裝指令);版本釘死,升版要同時動 requirements、render 檢查與本工具。
- 回滾成本高:回到正則等於重新接受那 28 條 finding 的失敗模式 —— 這正是「難逆轉」。
