# 負向 fixture(供 check-no-stale-paths.sh --scan 驗證用,故意含禁字)

這份假檔**刻意**寫死已淘汰的舊路徑,證明守衛在 `--scan` 模式下真的會抓到:

- 舊版 dev-flow runtime 路徑:`~/.claude/plugins/local/dev-flow/hooks/devflow-exec.sh`
- 舊版 dev-talk runtime 路徑:`~/.claude/plugins/local/dev-talk/skills/dev-talk/SKILL.md`
- 開發者個人絕對路徑:`/Users/asheng/dev/dev-flow`

正確寫法應為 `~/.claude/plugins/cache/dev-flow/dev-flow/<version>/`,見 `docs/PLUGIN.md`。
