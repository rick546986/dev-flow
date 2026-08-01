"""併發安全寫入(四節)。

原則:
- 每個事件檔**單一寫入者**:attempt 寫自己的 attempts/<id>/events.jsonl,
  reviews/hooks/coordinator 各寫自己的檔;跨 worktree 天然分檔(state per-worktree)。
- 快照類檔案(manifest/result/context-manifest)一律 atomic write:同目錄 temp + rename。
- 事件檔 append + fsync;crash 只可能留下**最後一行不完整**,reader 容忍截尾。
- 鎖檔 O_EXCL 防雙寫;crash 遺留鎖 = incomplete attempt 的佐證(has_stale_lock)。
"""
import json
import os
import tempfile


class AlreadyLocked(Exception):
    """同一事件檔已有寫入者(單一寫入者原則,四節)。"""


def atomic_write_json(path, obj):
    """temp + rename 原子寫 JSON;失敗不留半成品、不毀原檔。"""
    directory = os.path.dirname(os.path.abspath(path))
    os.makedirs(directory, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".tmp-", dir=directory)
    try:
        with os.fdopen(fd, "w") as f:
            json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=True)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


LOCK_NAME = "events.jsonl.lock"
EVENTS_NAME = "events.jsonl"


def _read_complete_events(path):
    """讀事件檔;回傳 (events, partial_tail)。截尾殘行不炸,標記後略過。"""
    events, partial = [], False
    if not os.path.exists(path):
        return events, partial
    with open(path, "rb") as f:
        raw = f.read()
    lines = raw.split(b"\n")
    for i, line in enumerate(lines):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line.decode("utf-8")))
        except (ValueError, UnicodeDecodeError):
            if i >= len(lines) - 2:          # 最後一行(或無換行殘尾)→ crash 截尾
                partial = True
            else:
                raise
    if raw and not raw.endswith(b"\n"):
        partial = True
    return events, partial


class EventWriter:
    """單一寫入者的 events.jsonl appender(自動補 seq,重開續號)。"""

    def __init__(self, directory):
        self.directory = directory
        os.makedirs(directory, exist_ok=True)
        self._lock_path = os.path.join(directory, LOCK_NAME)
        try:
            fd = os.open(self._lock_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError:
            raise AlreadyLocked(
                f"{directory} 已有寫入者(或 crash 遺留鎖;確認無人在寫後清 "
                f"{LOCK_NAME} 再開)")
        with os.fdopen(fd, "w") as f:
            f.write(str(os.getpid()) + "\n")
        self._path = os.path.join(directory, EVENTS_NAME)
        existing, _ = _read_complete_events(self._path)
        self._seq = max([e.get("seq", 0) for e in existing], default=0)
        self._fh = open(self._path, "a", encoding="utf-8")

    def append(self, event):
        """append 一筆事件;seq 缺時自動遞增補上。回傳實際寫入的 dict。"""
        record = dict(event)
        self._seq += 1
        record.setdefault("seq", self._seq)
        self._fh.write(json.dumps(record, ensure_ascii=False, sort_keys=True) + "\n")
        self._fh.flush()
        os.fsync(self._fh.fileno())
        return record

    def close(self):
        if self._fh is not None:
            self._fh.close()
            self._fh = None
        if os.path.exists(self._lock_path):
            os.remove(self._lock_path)


def has_stale_lock(directory):
    """鎖檔仍在 = 寫入者未正常 close(crash 徵兆;搭配 incomplete 判定使用)。"""
    return os.path.exists(os.path.join(directory, LOCK_NAME))
