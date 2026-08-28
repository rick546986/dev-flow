# html 產檔缺口循環（3–4 小時，可貼）

貼給審查循環。**不開刀。不合 main。不改 builder。**
從現在起到 **2026-08-26 21:00（台北）** 收工。半點審：17:30／18:30／19:30／20:30。20:30 出總表後刪 routine。

這條線不是 hop／Journey／圖對文字牙，也不是請人看樣式好不好看（使用者還在看 `example/subsidy-3-0-plus` html，答案還沒來）。
咬的是：**產檔器跟新規則之間還有哪些洞，會讓下一場 feat 再長出舊臉。**

## 正本／對照

- 新規則：第 1 站掃頁六件（摘要卡 → `#scan-now` 直式現況圖 → 人表 → 題表 → 驗收表 → 問答摺著）。第 2 站 twin：五格、Decision 釘住、決策點分組卡、選定標、圖可見、其餘摺疊。
- 手樣張（人看的臉，不要覆寫）：`example/subsidy-3-0-plus/`（本機；GitHub 還沒這夾）。
- 舊臉（壞對照）：`/Users/asheng/dev/ivf_platform_subsidy-3-0-plus/docs/dev/subsidy-3-0-plus/2-decision.html`（14 張卡、表頭假卡、Rejected 抽不到、OC 變 —）。
- 產生器現況：`scripts/build-gate-twin.py` + `devflow_twin_ui.py`。第 1 站**沒有**掃頁產生器。
- GitHub `rick546986/dev-flow` main 已有 `#43` `b1328bb`、`#44` `e656554`、`#45` `aca273b`。不要 revert。

## 已知洞（不要當新發現再報一次）

1. Twin 把多個 `### 決策點` 表摊成平卡；A/B/C id 撞號。
2. 表頭列變成假卡（「方案／摘要」）。
3. `## Rejected` 不叫 `Rejected Alternatives` → 駁回格 0。
4. Owner Calls 是條列 → 頂區顯示 —。
5. 第 1 站沒有從 md 重生掃頁的腳本。
6. subsidy md 有「邏輯圖」（明天）沒有「現況圖」（今天）；`#scan-now` 不准拿邏輯圖充。
7. 舊 twin 把方案架構圖摺進背景；樣張改放 Decision 底下。

## 要找的（新洞才報）

對 `build-gate-twin.py` 真實抽法、S10／掃頁六件契約、手樣張、舊 feat html，找**還會讓下一場 feat 產壞**的洞。至少看：

- 決策點 >1 張表時，產生器有沒有分組／略過表頭的路（沒有就是洞，已列；有半套算新洞）。
- `## Rejected`／`## Rejected Alternatives`／`## Rejected` 別名。
- OC 表 vs 條列。
- frontmatter `status` 抽錯（舊臉 draft vs approved）。
- 第 1 站：OQ 三態 `[x]`／`[>]`／假設；`#scan-now` 誤吃邏輯圖；掃頁六件順序；沒產生器時人用手寫會漏哪件。
- 第 2 站圖：橫箭頭、摺疊、選定標。
- 樣張自己有沒有跟契約打架（例如題表 15 列還算不算 30 秒掃頁）。
- **不要**把 3–7 站、五格改名、mermaid、第 6 站發明圖槽、IVF 本體、live `docs/dev/<slug>` 當這輪洞。

## 白名單（這輪只准讀）

准讀：`scripts/build-gate-twin.py`、`scripts/devflow_twin_ui.py`、`scripts/check-gate-twin.sh`、`skills/dev-talk/nodes/S10-html.md`、掃頁／Journey fixture、`example/subsidy-3-0-plus/`、舊 feat 的 1／2 md+html。
不准寫任何檔。不准開 PR。不准動 `#43`／`#44`／`#45` 牙、`check-devstageN-graph.sh`、`check-devtalk-fig-*.sh`、`html-shell`、`diagram-style`、`fig-lifecycle`、`docs/dev/tools`、exec／guard／Gauntlet、HISTORY、五格、`graph.yaml`、IVF 本體、`example/contract-expiry-reminder`。

## 半點審怎麼走

醒來先開兩個獨立審查（不要自己兼兩份）：

- **A** 盯：還在不開刀／不寫檔／不越界；現在幾點；過 21:00 沒有就刪 routine。
- **B** 盯：有沒有**新洞**（能指到檔＋抽法＋下一場 feat 會怎麼壞）。只複誦已知 7 條不算新洞。

然後只對差異回報一句：

1. 兩邊都沒新洞 → 「第 N 輪無新洞」。
2. 兩邊都指同一條新洞 → 列入總表，仍不開刀。
3. 兩邊結論不一樣 → 先講差在哪，不列入總表。
4. 有人開始改檔／開 PR → 不授權，寫越界在哪。
5. 20:30 或已過 21:00 → 總表（已知 7 + 這輪新洞），刪這個 routine。不要重開。

回報繁體中文、短。不要 mermaid。不要改 repo。使用者 html 還沒拍版，樣張不要覆寫。
