"""Signal Gate 與敏感內容守衛(§19/§34)。"""
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
        for text in ("密碼是 hunter2000", "金鑰是 sk-live-9f8a7b6c5d4e"):
            self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"], text)

    def test_absolute_path_blocks_durable_persist(self):
        verdict = signal.gate("schema_change", "t", "見 /Users/rick/proj/db.ts")
        self.assertTrue(verdict["absolute_paths"])
        self.assertFalse(verdict["durable_allowed"])

    def test_clean_high_signal_passes_all_three_gates(self):
        verdict = signal.gate("schema_change", "改名 pgs_intake → lab_order",
                              "migration 落在 migrations/20260820_rename.sql")
        self.assertTrue(verdict["durable_allowed"])
        self.assertEqual(verdict["reasons"], [])
