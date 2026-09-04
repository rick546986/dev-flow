"""Signal Gate 與敏感內容守衛(§19/§34)。"""
import time
import unittest

from memtools import MemoryCase  # noqa: F401
from agentmem import signal


class SignalGateTest(unittest.TestCase):
    def test_low_signal_kinds_stay_local(self):
        for kind in ("file_read", "grep", "list_directory", "command_ok"):
            verdict = signal.gate(kind, "x", "y")
            self.assertEqual(verdict["signal"], signal.LOW, kind)
            self.assertFalse(verdict["durable_allowed"], kind)

    def test_high_signal_kinds_may_persist(self):
        for kind in ("architecture_change", "schema_change", "bug_root_cause",
                     "business_rule", "design_decision", "verified_workflow",
                     "domain_clarification", "breaking_config_change"):
            verdict = signal.gate(kind, "title", "body")
            self.assertEqual(verdict["signal"], signal.HIGH, kind)
            self.assertTrue(verdict["durable_allowed"], kind)

    def test_unknown_kind_defaults_to_low(self):
        self.assertEqual(signal.gate("whatever")["signal"], signal.LOW)

    def test_explicit_can_downgrade_but_not_upgrade(self):
        self.assertEqual(
            signal.gate("schema_change", explicit=signal.LOW)["signal"], signal.LOW)
        self.assertEqual(
            signal.gate("file_read", explicit=signal.HIGH)["signal"], signal.LOW)


class SensitiveTest(unittest.TestCase):
    SECRETS = (
        'API_KEY = "sk-live-9f8a7b6c5d4e"',
        "password: hunter2000",
        "-----BEGIN RSA PRIVATE KEY-----",
        "AKIAIOSFODNN7EXAMPLE",
        "ghp_abcdefghijklmnopqrstuvwxyz012345",
        "Authorization: Bearer abc.def.ghi",
        "postgres://user:secretpw@db.internal/app",
        "xoxb-1234567890-abcdefghijkl",
        "密碼是 hunter2000",
        "金鑰是 sk-live-9f8a7b6c5d4e",
    )

    def test_secrets_block_durable_persist(self):
        for secret in self.SECRETS:
            verdict = signal.gate("schema_change", "t", secret)
            self.assertTrue(verdict["sensitive"], secret)
            self.assertFalse(verdict["durable_allowed"], secret)

    def test_placeholders_are_not_flagged(self):
        for benign in ("password: <redacted>", "token = null",
                       "api_key: ${API_KEY}", "secret: xxx"):
            self.assertEqual(signal.scan_sensitive(benign), [], benign)

    def test_scan_does_not_echo_secret_value(self):
        hits = signal.scan_sensitive('API_KEY = "sk-live-9f8a7b6c5d4e"')
        self.assertEqual(hits, ["assigned_secret"])
        self.assertNotIn("sk-live-9f8a7b6c5d4e", "".join(hits))

    def test_chinese_assignment_is_assigned_secret(self):
        # 正向:明確賦值記號(空白、無空白、冒號、等號)後接看起來像憑證的
        # token。中文書寫 ASCII 值時常常不留空白(「密碼是hunter2000」),
        # 不能要求一定要有空白才算賦值句。
        for text in ("密碼是 hunter2000", "密碼是hunter2000",
                     "金鑰是 sk-live-9f8a7b6c5d4e", "金鑰是 sk-live-abc123XYZ",
                     "密碼是: P@ssw0rd!", '密碼是 "hunter2000"'):
            self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                             text)
        # AKIA 開頭同時撞上 aws_access_key,兩個 pattern 都該命中。
        self.assertIn("assigned_secret",
                       signal.scan_sensitive("金鑰是=AKIAIOSFODNN7EXAMPLE"))

    def test_bare_token_regression_vs_pr110_baseline(self):
        # #95 R2 審查 finding 2:裸 token 分支曾比 7fd15cd 基準更窄 —— 拿掉了
        # `/`、且要求首字元一定是英數字,導致「資料庫密碼是 root/root」
        # 「密碼是 -abc-1234-」「金鑰是 _Abc12345」從會攔變不攔。補回:允許字元
        # 集含 `/`,首字元允許 `-`/`_`。
        for text in ("資料庫密碼是 root/root", "密碼是 -abc-1234-",
                     "金鑰是 _Abc12345"):
            self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                             text)

    def test_bare_token_longer_than_shape_bound_still_detected(self):
        # ReDoS 修法(finding 1)把形狀 lookahead 的量詞改成有界 `{0,64}`,但
        # 存在性/邊界 lookahead 必須維持不設上限 —— 否則 65 字元以上的裸
        # token 邊界永遠卡在字元類別內側、等不到終止條件,整支失配,是修
        # ReDoS 時新引入的假陰性(對抗審查抓到)。這裡用一個 81 字元、混合
        # 大小寫特徵落在中段的 token 驗證兩件事都還成立。
        text = "密碼是 " + ("a" * 40) + "B" + ("c" * 40)
        self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                         text)

    def test_chinese_narrative_sentence_is_not_assigned_secret(self):
        # 反向(#95 回歸,PR #110 審查 finding C):「密碼是／金鑰是」後接接續詞
        # 或純敘述文字(無賦值記號、非憑證形狀)不是賦值句,不該擋 durable 寫入。
        # 含全形冒號的敘述句(「密碼是:需要定期更換的」)是最容易漏測的一種:
        # 有冒號但後面接的仍是中文敘述,不是憑證。
        for text in ("密碼是否要定期更換", "密碼是公司規定",
                     "金鑰是託管在 KMS", "金鑰是由 KMS 管理",
                     "密碼是要保密的資訊", "這個密碼是給測試用的",
                     "密碼是:需要定期更換的", "金鑰是:由 KMS 統一託管",
                     '密碼是"需要定期更換的"'):
            verdict = signal.gate("schema_change", "t", text)
            self.assertEqual(signal.scan_sensitive(text), [], text)
            self.assertTrue(verdict["durable_allowed"], text)

    def test_absolute_path_blocks_durable_persist(self):
        verdict = signal.gate("schema_change", "t", "見 /Users/rick/proj/db.ts")
        self.assertTrue(verdict["absolute_paths"])
        self.assertFalse(verdict["durable_allowed"])

    def test_clean_high_signal_passes_all_three_gates(self):
        verdict = signal.gate("schema_change", "改名 pgs_intake → lab_order",
                              "migration 落在 migrations/20260820_rename.sql")
        self.assertTrue(verdict["durable_allowed"])
        self.assertEqual(verdict["reasons"], [])

    def test_scan_sensitive_is_bounded_time_against_redos(self):
        # #95 R2 審查 finding 1(blocker,ReDoS):「密碼是」後接一長段同大小寫
        # ASCII 字母,曾讓裸 token 形狀 lookahead 的兩個不定長 `[...]*`
        # 互相重疊、災難性回溯。200KB 這類輸入必須在有界時間內回傳,不能隨
        # 輸入長度退化。
        text = "密碼是" + ("a" * 200000)
        start = time.perf_counter()
        signal.scan_sensitive(text)
        elapsed = time.perf_counter() - start
        self.assertLess(elapsed, 0.5,
                         "scan_sensitive 對 200KB 輸入耗時 {0:.3f}s,"
                         "疑似 ReDoS 回退".format(elapsed))
