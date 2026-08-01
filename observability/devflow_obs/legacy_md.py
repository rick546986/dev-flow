"""舊 6-notes「執行軌跡」Markdown 讀取(十一節相容:舊 Markdown 沒有 Run ID 仍能讀)。

軌跡列格式(_templates/6-implementation-notes.md 執行軌跡節):
`| T-id | 失敗分類(SPEC/ENV/IMPL/UNKNOWN;無失敗 —)| 模型升階史 | 回合數 | 原因 |`
產出 row:{"task_id","failure_category","escalations","rounds","reason",
"run_id"(恆 None),"source"("markdown-legacy")}。
"""
import re

_CATS = {"SPEC", "ENV", "IMPL", "UNKNOWN"}
_EMPTY = {"", "—", "-", "–", "none", "n/a"}


def _cell_empty(cell):
    return cell.strip().lower() in _EMPTY


def parse_execution_trace(text):
    """從 6-notes Markdown 抽執行軌跡列;無該節或只有模板註解 → []。"""
    lines = text.splitlines()
    rows, in_section, header_seen = [], False, False
    for line in lines:
        if line.startswith("## "):
            in_section = line.lstrip("# ").startswith("執行軌跡")
            header_seen = False
            continue
        if not in_section:
            continue
        stripped = line.strip()
        if not stripped.startswith("|"):
            continue
        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if not cells:
            continue
        if re.match(r"^:?-{2,}:?$", cells[0].replace(" ", "")):
            continue                                     # 分隔列
        if not re.match(r"^T-\d+$", cells[0]):
            header_seen = True                           # 表頭列
            continue
        row = {"task_id": cells[0], "failure_category": None,
               "escalations": [], "rounds": 1, "reason": None,
               "run_id": None, "source": "markdown-legacy"}
        if len(cells) > 1 and not _cell_empty(cells[1]):
            cat = cells[1].upper()
            row["failure_category"] = cat if cat in _CATS else "UNKNOWN"
        if len(cells) > 2 and not _cell_empty(cells[2]):
            row["escalations"] = [m for m in
                                  re.split(r"→|->", cells[2]) if m.strip()]
            row["escalations"] = [m.strip() for m in row["escalations"]]
        if len(cells) > 3:
            m = re.search(r"\d+", cells[3])
            if m:
                row["rounds"] = int(m.group())
        if len(cells) > 4 and not _cell_empty(cells[4]):
            row["reason"] = cells[4]
        rows.append(row)
    return rows


def parse_file(path):
    with open(path, encoding="utf-8") as f:
        return parse_execution_trace(f.read())
