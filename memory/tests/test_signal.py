"""Signal Gate 與敏感內容守衛(§19/§34)。"""
import base64
import os
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
        # #95 R3 finding 2 修法把形狀判斷整段搬出正則,改成 scan_sensitive
        # 對正則抓到的 tok 候選用 Python 判定(_looks_like_credential)——
        # 判斷對象是已擷取的完整字串,不再受正則裡任何量詞上限影響。這裡用
        # 一個 81 字元、混合大小寫特徵落在中段的 token,驗證即使特徵落在
        # 「舊版有界 lookahead 看不到的位置」,新版仍然攔得住。
        text = "密碼是 " + ("a" * 40) + "B" + ("c" * 40)
        self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                         text)

    def test_bare_token_digit_only_at_tail_past_shape_bound_is_detected(self):
        # #95 R3 審查 finding 2(major):形狀判斷改成 Python 端對整個 tok 字串
        # 判定(不再受正則裡任何長度上限限制)之前,若形狀判斷還留在正則裡並
        # 對量詞設界,65 字元以上、判別特徵(數字/連字號/大小寫轉換)只出現
        # 在尾端的裸 token 會漏放 —— 這裡的 71 字元 token 只有最後 4 碼是
        # 數字,其餘全是小寫字母,驗證修法後仍然攔得住。
        text = ("密碼是 productionapiendpointsecretforinternalservicemesh"
                "connectivityregion2026")
        self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                         text)

    def test_english_keyword_prefix_longer_than_suffix_bound_is_detected(self):
        # #95 R3 對抗審查 minor:第一輪修法把英文 key 名分支兩側量詞都改成
        # 有界 `{0,64}`,連關鍵字「前綴」也一起設了界 —— 變數名在 password
        # 等關鍵字前有 65 字元以上連續 [\w.-] 字元時,`\b` 只落在整段識別字
        # 最前面、離關鍵字超過 64 字元,有界前綴量詞搆不到,漏放。修法把
        # 前綴整段拿掉(關鍵字前不再要求任何字元),這裡驗證正向(超長前綴
        # 仍攔)與貼著門檻的正向(常見全大寫 env var 名)都成立。
        long_prefix = ("my_super_long_internal_service_configuration_"
                       "database_admin_root_")
        self.assertGreater(len(long_prefix), 64, "測資前綴長度前提")
        text = long_prefix + "password=abc123"
        self.assertEqual(signal.scan_sensitive(text), ["assigned_secret"],
                         text)
        self.assertEqual(
            signal.scan_sensitive("MY_DB_PASSWORD=x1y2z3"), ["assigned_secret"])

    def test_passwordless_without_assignment_marker_is_not_flagged(self):
        # 反向:拿掉前綴的界之後,關鍵字前不再有任何限制,但「有沒有賦值
        # 記號」這一關維持不變 —— `passwordless` 內含 `password` 字面,
        # 沒有 `[:=]` 跟在後面就不該命中,不能因為拿掉前綴界而變寬鬆。
        self.assertEqual(
            signal.scan_sensitive("passwordless login enabled"), [])

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
        # assigned_secret 踩過兩次 ReDoS,病灶不同支、修法也不同支,三種病態
        # 輸入都要各自留一份計時回歸,不能只測其中一種就當作「這顆函式
        # 沒有 ReDoS」:
        #   ①中文裸 token(#95 R2 finding 1):「密碼是」後接一長段同大小寫
        #     ASCII 字母,曾讓裸 token 形狀 lookahead 的兩個不定長 `[...]*`
        #     互相重疊、災難性回溯。
        #   ②英文分支長 blob(#95 R3 finding 1):英文關鍵字分支兩個不定長
        #     `[\\w.-]*` 夾住必須字面,對一段無空白的 base64url 長串,`\\b`
        #     在其中幾乎每個字元都是邊界起點,每個起點各自回溯到底。
        #   ③英文分支 `x.-_` 重複(同一顆 finding,另一種輸入形狀):`.`/`-`
        #     反覆出現讓 `\\b` 邊界起點更密集,是①的加強版重現。
        # 三案對齊成同一個量級(200KB),不要一案 200KB、一案 60KB 各測各的
        # ——量級不齊,門檻就不是同一把尺(#95 R3 對抗審查 nit)。實測(2026-09,
        # 本機)三案都在 0.05s 內、離 0.5s 門檻還有 10 倍以上餘裕,不是
        # 90% 佈滿的 flaky 門檻,維持 0.5s 不用放寬到 1.0s。
        cases = {
            "chinese_bare_token": "密碼是" + ("a" * 200000),
            "english_blob": (
                "please rotate the session token sess_v2." +
                base64.urlsafe_b64encode(os.urandom(150000)).decode("ascii") +
                " before shipping"
            ),
            "x_dot_dash_underscore_repeat": "x.-_" * 50000,
        }
        for label, text in cases.items():
            start = time.perf_counter()
            signal.scan_sensitive(text)
            elapsed = time.perf_counter() - start
            self.assertLess(
                elapsed, 0.5,
                "scan_sensitive 對病態輸入({0})耗時 {1:.3f}s,"
                "疑似 ReDoS 回退".format(label, elapsed))
