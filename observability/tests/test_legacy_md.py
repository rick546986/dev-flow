"""十三節測試對應:舊 Markdown(6-notes 執行軌跡)沒有 Run ID 時仍能讀。"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from devflow_obs import legacy_md  # noqa: E402

SAMPLE = """---
feature: contract-expiry-reminder
stage: 6-implementation
status: shipped
---

# 6. 實作筆記

## 執行軌跡(選配,只供 dev-run 引擎;手動實作留白,不虛構模型歷史)

| T-id | 失敗分類 | 模型升階史 | 回合數 | 原因 |
|---|---|---|---|---|
| T-1 | — | — | 1 | — |
| T-2 | IMPL | haiku→sonnet | 2 | verify 紅一次 |
| T-3 | ENV | — | 1 | 依賴壞,重跑不計 |

## TDD Evidence
(略)
"""


class TestLegacyMarkdown(unittest.TestCase):
    def test_parses_rows_without_run_id(self):
        rows = legacy_md.parse_execution_trace(SAMPLE)
        self.assertEqual(len(rows), 3)
        self.assertEqual(rows[0], {
            "task_id": "T-1", "failure_category": None, "escalations": [],
            "rounds": 1, "reason": None, "run_id": None,
            "source": "markdown-legacy"})
        self.assertEqual(rows[1]["failure_category"], "IMPL")
        self.assertEqual(rows[1]["escalations"], ["haiku", "sonnet"])
        self.assertEqual(rows[1]["rounds"], 2)

    def test_template_without_rows_yields_empty(self):
        template = ("# 6. 實作筆記\n\n## 執行軌跡(選配)\n"
                    "<!-- 每 T 一列:... -->\n\n## TDD Evidence\n")
        self.assertEqual(legacy_md.parse_execution_trace(template), [])

    def test_document_without_section_yields_empty(self):
        self.assertEqual(legacy_md.parse_execution_trace("# 別的文件\n內容"), [])

    def test_ascii_arrow_also_accepted(self):
        text = ("## 執行軌跡\n\n| T-id | 失敗分類 | 升階史 | 回合數 | 原因 |\n"
                "|---|---|---|---|---|\n"
                "| T-9 | UNKNOWN | haiku->sonnet->opus | 4 | 三層連敗 |\n")
        rows = legacy_md.parse_execution_trace(text)
        self.assertEqual(rows[0]["escalations"], ["haiku", "sonnet", "opus"])
        self.assertEqual(rows[0]["rounds"], 4)


if __name__ == "__main__":
    unittest.main()
