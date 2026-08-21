"""受限 YAML:round-trip、deterministic、不支援的形狀一律 fail-loud。"""
import unittest

from memtools import MemoryCase  # noqa: F401  (sys.path 設定)
from agentmem import yamlmini


class RoundTripTest(unittest.TestCase):
    CASES = (
        {"a": 1},
        {"a": "x y", "b": None, "c": True, "d": False, "e": 1.5, "f": -3},
        {"list": ["a", "b c", 1, True]},
        {"nested": {"x": {"y": 1}}},
        {"facts": [{"fact_key": "backend", "value": "sqlite-wasm",
                    "deps": ["a.ts", "b.ts"]},
                   {"fact_key": "port", "value": 38888}]},
        {"cjk": "registration 代表一個客戶,不是 embryo"},
        {"quoted": 'has "quotes" and: colon'},
        {"numeric_string": "1.0.0"},
    )

    def test_round_trip(self):
        for case in self.CASES:
            text = yamlmini.dump(case)
            self.assertEqual(yamlmini.load(text), case, text)

    def test_deterministic_bytes(self):
        for case in self.CASES:
            first = yamlmini.dump(case)
            second = yamlmini.dump(dict(reversed(list(case.items()))))
            self.assertEqual(first, second)
            self.assertTrue(first.endswith("\n"))
            self.assertFalse(first.endswith("\n\n"))
            for line in first.splitlines():
                self.assertEqual(line, line.rstrip())

    def test_key_order_head_then_sorted(self):
        text = yamlmini.dump({"z": 1, "schema_version": 1, "a": 2},
                             key_order=["schema_version"])
        self.assertEqual([line.split(":")[0] for line in text.splitlines()],
                         ["schema_version", "a", "z"])

    def test_header_comment_is_ignored_on_load(self):
        text = yamlmini.dump({"a": 1}, header="hello\nworld")
        self.assertTrue(text.startswith("# hello\n# world\n"))
        self.assertEqual(yamlmini.load(text), {"a": 1})

    def test_string_that_looks_like_scalar_is_quoted(self):
        for value in ("true", "false", "null", "123", "1.5", "", "yes"):
            text = yamlmini.dump({"v": value})
            self.assertEqual(yamlmini.load(text)["v"], value, text)


class RejectTest(unittest.TestCase):
    BAD = (
        "a: {b: 1}",            # flow mapping
        "a: [1, 2]",            # flow sequence
        "a: &anchor 1",         # anchor
        "a: *alias",            # alias
        "---\na: 1",            # 多文件
        "a: |\n  block",        # block scalar
        "a: 'single'",          # 單引號
        "\ta: 1",               # tab 縮排
        "   a: 1",              # 奇數縮排
        "a 1",                  # 不是 key: value
        "a: 1\na: 2",           # 重複 key
    )

    def test_unsupported_shapes_fail_loud(self):
        for text in self.BAD:
            with self.assertRaises(yamlmini.YamlMiniError, msg=text):
                yamlmini.load(text)

    def test_unsupported_python_types_fail_loud(self):
        with self.assertRaises(yamlmini.YamlMiniError):
            yamlmini.dump({"a": {1: 2}})
        with self.assertRaises(yamlmini.YamlMiniError):
            yamlmini.dump({"a": object()})
