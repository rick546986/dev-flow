"""中文 / Unicode 不被 strip,exact code symbol 抽得出來(§22/§23/§31)。"""
import unittest

from memtools import MemoryCase  # noqa: F401
from agentmem import textnorm


class ChineseTest(unittest.TestCase):
    QUERIES = (
        "現在使用哪一張資料表?",
        "之前為什麼修改 registration?",
        "目前 lab_order 使用哪張 table?",
        "之前 PGS registration 為什麼改?",
    )

    def test_chinese_queries_produce_tokens(self):
        for query in self.QUERIES:
            toks = textnorm.tokens(query)
            self.assertTrue(toks, query)
            self.assertTrue(any(len(t) >= 1 and not t.isascii() for t in toks),
                            (query, toks))

    def test_chinese_is_not_stripped_by_query_normalizer(self):
        for query in self.QUERIES:
            self.assertTrue(textnorm.normalize_query(query), query)

    def test_bigrams_present_for_cjk(self):
        toks = textnorm.tokens("資料表")
        self.assertIn("資", toks)
        self.assertIn("資料", toks)
        self.assertIn("料表", toks)

    def test_mixed_language_keeps_both_sides(self):
        toks = textnorm.tokens("之前 PGS registration 為什麼改?")
        self.assertIn("pgs", toks)
        self.assertIn("registration", toks)
        self.assertIn("之前", toks)

    def test_pure_punctuation_yields_no_tokens(self):
        self.assertEqual(textnorm.tokens("??? --- !!!"), [])
        self.assertEqual(textnorm.normalize_query("???"), "")


class SymbolTest(unittest.TestCase):
    def test_snake_case_table_name(self):
        self.assertIn("pgs_intake_registration",
                      textnorm.symbols("查 pgs_intake_registration 這張表"))

    def test_file_path_and_camel_case(self):
        syms = textnorm.symbols("getUserById 定義在 src/services/db.ts")
        self.assertIn("getUserById", syms)
        self.assertIn("src/services/db.ts", syms)

    def test_env_key_and_route_and_sha(self):
        syms = textnorm.symbols(
            "設 DEVFLOW_MEMORY_DIR,打 /api/v1/orders,commit abc123f")
        self.assertIn("DEVFLOW_MEMORY_DIR", syms)
        self.assertIn("/api/v1/orders", syms)
        self.assertIn("abc123f", syms)

    def test_normalize_symbol_bridges_naming_styles(self):
        self.assertEqual(textnorm.normalize_symbol("pgs_intake_registration"),
                         textnorm.normalize_symbol("pgsIntakeRegistration"))
        self.assertNotEqual(textnorm.normalize_symbol("pgs_intake_registration"),
                            textnorm.normalize_symbol("pgs_intake_specimen"))

    def test_subwords_available_for_lexical_channel(self):
        toks = textnorm.tokens("pgs_intake_registration")
        for expected in ("pgs_intake_registration", "pgs", "intake", "registration"):
            self.assertIn(expected, toks)

    def test_trigrams_cover_cjk(self):
        self.assertIn("資料表", textnorm.trigrams("資料表"))
