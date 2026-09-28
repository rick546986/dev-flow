"""P1-F5 — daily budget / breaker 的落盤(gitignored `.devflow/jev/state/`)。零網路。

- budget 檔按 UTC 日切:`budget-YYYY-MM-DD.json`;attempts 與 tokens_committed 跨 process 累計,
  先到者停(§8.2)。unknown usage 的保留額**不退款**,所以落盤的是 `tokens_committed`(settled+reserved 合計)。
- breaker 檔:`breaker.json`,per key 連續失敗數。
- 寫入 mkstemp tmp + os.replace;同一台機器同時兩個 process 可能 lost update(不會壞檔) —— 這裡是成本護欄不是帳本,
  漏算一次 attempt 的方向是「多花一次」,不會放行 AUTO;帳本正本仍是 durable evaluation 的 usage 欄。
"""
import json
import os
import time

from . import JevError
from .policy import Breaker, Budget

STATE_DIRNAME = os.path.join(".devflow", "jev", "state")


def utc_day(now=None):
    return time.strftime("%Y-%m-%d", time.gmtime(now if now is not None else time.time()))


def _atomic_write(path, payload):
    """每個 writer 自己的 tmp(mkstemp),不共用固定 .tmp 名 —— 同日兩個 ask 同時存檔時,共用名會讓後者
    os.replace 撲空或把半截 JSON 留在檔裡,之後整天的 ask/status 都讀不出 budget。"""
    import tempfile
    fd, tmp = tempfile.mkstemp(prefix=os.path.basename(path) + ".", suffix=".tmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(payload, fh, ensure_ascii=False, sort_keys=True, indent=1)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


class StateStore(object):
    def __init__(self, repo_root, dirname=STATE_DIRNAME):
        self.dir = os.path.join(repo_root, dirname)

    def budget_path(self, day):
        if not isinstance(day, str) or len(day) != 10:
            raise JevError("day 必須是 YYYY-MM-DD")
        return os.path.join(self.dir, "budget-%s.json" % day)

    def breaker_path(self):
        return os.path.join(self.dir, "breaker.json")

    def load_budget(self, day=None):
        day = day or utc_day()
        budget = Budget()
        path = self.budget_path(day)
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("schema") != "devflow-jev-budget/1":
                raise JevError("%s: schema 不對" % path)
            budget.attempts = int(data["attempts"])
            budget.settled = int(data["tokens_committed"])       # 上次的保留額已視為花掉(不退款)
        return budget

    def save_budget(self, budget, day=None):
        day = day or utc_day()
        os.makedirs(self.dir, exist_ok=True)
        payload = {"schema": "devflow-jev-budget/1", "day": day, "attempts": budget.attempts,
                   "attempts_cap": budget.attempts_cap, "tokens_committed": budget.tokens_committed(),
                   "tokens_cap": budget.tokens_cap}
        _atomic_write(self.budget_path(day), payload)
        return payload

    def load_breaker(self):
        breaker = Breaker()
        path = self.breaker_path()
        if os.path.isfile(path):
            with open(path, encoding="utf-8") as fh:
                data = json.load(fh)
            if data.get("schema") != "devflow-jev-breaker/1":
                raise JevError("%s: schema 不對" % path)
            breaker.failures = {str(k): int(v) for k, v in (data.get("failures") or {}).items()}
        return breaker

    def save_breaker(self, breaker):
        os.makedirs(self.dir, exist_ok=True)
        payload = {"schema": "devflow-jev-breaker/1", "threshold": breaker.threshold,
                   "failures": dict(breaker.failures)}
        _atomic_write(self.breaker_path(), payload)
        return payload
