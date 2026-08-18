# Plugin Workstream Result

- Base SHA: 24057d5
- Branch: devflow-runtime-vnext/observability
- HEAD: (見本 commit;前五 commit = 28f65cc vendor / d14ea90 selftest RED / 6689981 obs impl / 30ff6f4 registry+caps / 94b3ab1 doctor)
- Modified files:
  - `hooks/selftest.sh`(**只增**:p3 節 44 案 + p3_ 前綴 helper;既有 80 案未動)
- Added files(全屬 P3 所有權,契約 §10):
  - `hooks/devflow_obs_vendor/`(vendor:devflow_obs 6 模組 + schema 3 JSON byte-identical;
    來源 SHA 9f08c947556cf6e596c45fe20a7bdf6bb5598829,標頭 + VENDOR-SOURCE.md;`.gitignore` 堵 `__pycache__`)
  - `hooks/_obs_impl.py` + `hooks/devflow-obs.sh`
  - `hooks/_doctor_impl.py` + `hooks/devflow-doctor.sh`
  - `hooks/runtime-capabilities.json`、`hooks/prompt-registry.json`
- Added capabilities:
  - **event 落盤通道**(`.devflow/` 受 guard 禁寫 → CLI 唯一合法通道;stdin 吃 JSON,
    命令列不鋪 `.devflow/` 路徑,prebash regex 不會攔):`event` 依事件型別路由
    coordinator/attempts/reviews/verifier 分檔,attempt_completed 併寫 result.json(atomic)。
    run_id 只從 exec.json(exec-v2)讀;v1/未武裝 → 明確錯誤(run_id 生成歸 P1)。
  - **hook 機械事件**:`hook-event` → `hooks/events-<session>.jsonl`;schema 機械拒收
    agent_role/model/prompt(hook 不推測歸屬)。
  - **runtime 加嚴**(共享契約 §6):欄位級長度(prompt.id≤100/prompt.version≤40/model≤100/
    reason≤500/title≤1000/command_ref≤500/artifact_ref≤1000/result_summary≤2000)+
    追加禁載 source_body/customer_data + `x_task_tags` 受控 enum(devflow-contract.json 12 值,禁自由字串)。
  - **derive/stats/recommend/validate**:直接呼叫 vendor 模組,輸出格式與方法論 CLI 相同。
  - **Retention(OC-5)**:`archive`(→ `$DEVFLOW_LEDGER_HOME/runs/<repo_id>/<run_id>/`,
    歸檔 manifest 補齊 repo_id/run_id/schema_version/created_at/expires_at/source_sha)、
    `retention status|prune --dry-run|prune`(raw 180 天;**僅手動,禁背景自動刪除;預設不雲端同步**);
    LEDGER_HOME 解析:env → macOS `~/Library/Application Support/DevFlow/ledger/` →
    Linux `${XDG_STATE_HOME:-~/.local/state}/devflow/ledger/`。
  - **doctor(§9)**:契約解析(--contract / $DEVFLOW_CONTRACT / 受測專案 docs/dev/ 散發副本;
    找不到明確報)→ 比對契約版本/必要 capability/vendored schema versions/gate-consistency 實跑/
    prompt registry;不相容 fail-closed 並印 §9 例句;exec.json v1 → `legacy compatibility mode` 明示。
  - **Prompt registry 初版**:5 prompt id(stage6-worker/reviewer/adviser、
    stage7-standards-reviewer/spec-reviewer)@1.0.0;hash = sha256(`devflow-prompt:<id>\n` + SKILL 檔全文)。
- Tests before: `hooks/selftest.sh` 80/80(基線 @24057d5 實跑)
- Tests after: **124/124 全綠**(80 既有不動 + 44 p3_);RED 證據:d14ea90 時 82/124(42 紅;
  44 案中 2 案在 RED 期為 vacuous pass:「prune 後 run 已移除」「vendor 無 __pycache__」)
- Raw outputs(對拍,方法論 fixtures 行為正本 §11):
  - `validate`:方法論母版 CLI vs plugin CLI on fixtures R01+R02 → **diff 空,rc 0=0**
  - `derive`:兩份 fixtures 副本各自重建 → `derived/run-events.jsonl` **byte-identical**(R01、R02 皆)
  - `stats --legacy-md`(含 legacy 6-notes fixture)與 `recommend` → 輸出 **byte-identical**
  - 對拍為 REFERENCE_PASS + 本軌 selftest RUNTIME_PASS;E2E 歸 Phase 4
  - doctor 實跑(temp 專案 + 真方法論契約):INCOMPATIBLE(fail-closed)——
    缺 P1/P2/P4 五 capability(含「Parallel execution is unavailable」)、agent_event 1.1 vs 1.0.0、
    gate-consistency 1/14 漂移(audit 已知基線紅);= 整合前誠實現狀
- Known limitations:
  1. `runtime-capabilities.json` 誠實只聲明 `attempt_ledger` → doctor 在本軌必 fail-closed;
     Integrator 隨 merge 擴列(見下)後才可能全綠。
  2. registry `approved_by = "pending-owner-approval"`:初版由 P3 建檔,**待 rick 簽核**
     (不偽造人類核准);stage7-* hash 對 skills/dev-flow/SKILL.md 全文,P4 建立獨立
     Stage 7 dispatch 素材檔後應 minor 升版換 hash 來源。
  3. prompt_hash 漂移偵測未掛 selftest/doctor(避免 P1/P2 改 SKILL 時整合期紅);後續版補。
  4. 去識別化 aggregate 尚無落盤產物(stats 即時計算),retention 現僅管 raw runs;
     未來落盤 aggregate 需自帶 expires_at(365 天)。
  5. hook-event 在 run_id 不可得時明確錯誤,由 caller try/except 吞掉 → P1 exec-v2 落地前
     hook 機械事件不落盤(僅觀測面損失,不影響守衛裁決)。
- External dependencies(跨軌;wiring 屬 P1 檔案,本軌不動):
  - **P1 exec.json v2**:`schema:"exec-v2"` + `run_id`(run_<26 字 Crockford ULID>)於 start 生成。
    P1 若同時建 run 目錄+manifest 亦可(本軌 ensure_manifest 見檔即跳過);未建則首事件自動補
    (含 OC-5 六必填)。
  - **方法論 §11 sync**:agent-event schema 6.6 欄位級上限 + schema_version 升 1.1
    (契約已聲明 1.1,vendored 為 1.0.0 → doctor 現報漂移,by design)。落地後照
    VENDOR-SOURCE.md 重新 vendor,並檢視 `_obs_impl.FIELD_MAX` 與正本收斂。
  - **P4 gate-consistency**:doctor 實跑其結果;現制 1/14 基線紅由 OC-2 條文落地一併綠。

## 交 Integrator patch(P1 檔案;Phase 3 套用)

### 1) `hooks/devflow-exec.sh` — case 區塊 `*)` 前插入兩行(§9 doctor 掛載 + event 別名)

```bash
  event)   "$HERE/devflow-obs.sh" event "${2:-}";;
  doctor)  shift; "$HERE/devflow-doctor.sh" "$@";;
```

### 2) `hooks/_guard_impl.py` / `hooks/_prebash_impl.py` — L 載入後插入 helper(兩檔同文)

```python
import subprocess

def _obs_deny(gate, violation, target=""):
    """deny 時 best-effort 記機械事件(P3 hook-event);失敗不影響守衛裁決。"""
    try:
        payload = {"event_type": "mechanical_gate_completed", "gate": gate,
                   "result": "FAIL", "violation": violation}
        if target:
            payload["target"] = target
        try:
            sid = json.loads(os.environ.get("HOOK_INPUT", "{}")).get("session_id", "")
        except Exception:
            sid = ""
        if sid:
            payload["session_ref"] = sid
        subprocess.run(
            [sys.executable,  # 呼叫自己這個直譯器;路徑解析正本 = hooks/devflow-python-lib.sh
             os.path.join(os.path.dirname(os.path.abspath(__file__)), "_obs_impl.py"),
             "hook-event", root],
            input=json.dumps(payload), text=True, capture_output=True, timeout=5)
    except Exception:
        pass
```

各 deny 的 `L.die(...)` 前一行插入(gate/violation 對照):

| 檔:位置 | 插入 |
|---|---|
| _guard_impl 圍欄②禁讀(L37) | `_obs_deny("guard-read", "upstream_read", rel)` |
| _guard_impl 契約防篡改(L43) | `_obs_deny("guard-write", "contract", rel)` |
| _guard_impl .devflow 直寫(L47) | `_obs_deny("guard-write", "guard_state", rel)` |
| _guard_impl .gitignore(L49) | `_obs_deny("guard-write", "guard_state", rel)` |
| _guard_impl scope 外寫入(L55) | `_obs_deny("guard-write", "scope", rel)` |
| _prebash_impl ①守衛破壞(L27) | `_obs_deny("prebash", "guard_state")` |
| _prebash_impl ②上游讀(L32) | `_obs_deny("prebash", "upstream_read")` |

### 3) `hooks/_postbash_impl.py` — 頂部補 `import json`,同 helper;`sys.exit(2 ...)` 前插入

```python
if tampered:
    _obs_deny("postbash-detect", "contract", tampered[0])
if bad:
    _obs_deny("postbash-detect", "scope", bad[0])
```

### 4) `hooks/runtime-capabilities.json` — capabilities 隨 merge 擴列(檔屬 P3,Integrator 代改)

| merge 軌 | 追加能力名(照 devflow-contract.json) |
|---|---|
| P1 execution | `task_scoped_guard`、`parallel_wave_execution`、`candidate_gate` |
| P2 operational | `operational_demo_gate` |
| P4 gauntlet-gates | `final_fresh_run` |

全軌合流 + §11 schema sync + gate-consistency 綠 → doctor 才會 COMPATIBLE;在那之前
fail-closed 是**預期行為**,不得為了綠而預聲明未合流能力。

- Status: **RUNTIME_PASS(本軌範圍)** — plugin selftest 124/124 + fixtures 對拍 byte-identical;
  E2E_PENDING(Phase 4);doctor 全綠 PENDING(依賴四軌合流 + §11 sync)。
