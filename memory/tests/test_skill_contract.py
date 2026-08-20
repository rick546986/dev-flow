"""SKILL 契約:Agent-facing workflow 必須真的接上 Python API。

**為什麼需要這一支**:Python API 有功能、Skill 忘了接,是這個專案最容易發生
而且最不會被抓到的失敗 —— 所有單元測試都綠,實際上沒有任何 agent 會呼叫它。
`memory/tests/test_devtalk.py` 測的是 `devtalk.py` 的函式;這一支測的是
**SKILL.md 有沒有告訴 agent 去呼叫它們**,以及那些指令是不是真的存在。

兩個方向都驗:
  ①SKILL.md 提到的每一個 memory 指令,CLI 真的收得下(不是寫給人看的假指令)
  ②CLI 提供的生命週期指令,SKILL.md 真的有寫(不是只有 Python 有)
"""
import os
import re
import subprocess
import sys
import unittest

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CLI = os.path.join(REPO, "memory", "dev-memory.py")


def read(rel):
    with open(os.path.join(REPO, rel), encoding="utf-8") as stream:
        return stream.read()


def cli_help(*args):
    out = subprocess.run([sys.executable, CLI, *args, "--help"],
                         capture_output=True, text=True, cwd=REPO)
    assert out.returncode == 0, out.stderr
    return out.stdout


class DevTalkSkillContractTest(unittest.TestCase):
    """P0-2:dev-talk 的 start → turn → propose → confirm/reject → end 全鏈。"""

    def setUp(self):
        self.skill = read("skills/dev-talk/SKILL.md")

    def test_start_is_the_first_memory_action(self):
        self.assertIn("dev-memory.py talk start", self.skill)
        start_at = self.skill.index("talk start")
        for later in ("talk turn", "talk propose", "talk confirm", "talk end"):
            self.assertIn(later, self.skill, later)
            self.assertLess(start_at, self.skill.index(later),
                            "{0} 出現在 talk start 之前".format(later))

    def test_session_id_is_named_as_workflow_state(self):
        self.assertIn("MEMORY_SESSION_ID", self.skill)
        self.assertIn("session_id", self.skill)

    def test_every_lifecycle_command_is_wired(self):
        for command in ("talk start", "talk turn", "talk propose",
                        "talk confirm", "talk reject", "talk correct",
                        "talk end", "talk abort"):
            self.assertIn(command, self.skill, command)

    def test_turn_covers_both_roles(self):
        self.assertRegex(self.skill, r"talk turn \$MEMORY_SESSION_ID user")
        self.assertRegex(self.skill, r"talk turn \$MEMORY_SESSION_ID agent")

    def test_later_commands_use_the_captured_session(self):
        """propose/confirm/end 必須用 start 拿到的 session,不是憑空的 <session>。"""
        for command in ("talk propose", "talk end", "talk abort"):
            index = self.skill.index(command)
            window = self.skill[index:index + 200]
            self.assertIn("$MEMORY_SESSION_ID", window, command)

    def test_transcript_is_declared_local_only(self):
        self.assertIn("永遠不進版本控制", self.skill)

    def test_abnormal_termination_is_covered(self):
        self.assertIn("ABORTED", self.skill)
        self.assertIn("絕不接上一個", self.skill)

    def test_unconfirmed_candidates_are_declared_not_durable(self):
        self.assertIn("未確認的候選一律不寫進長期記憶", self.skill)

    def test_zero_promoted_is_declared_legal(self):
        self.assertIn("promoted: 0", self.skill)

    def test_retrieval_status_contract_is_explained(self):
        for status in ("OK", "NEEDS_VERIFICATION", "CONFLICT",
                       "NO_RELIABLE_MATCH"):
            self.assertIn(status, self.skill, status)


class DevRunSkillContractTest(unittest.TestCase):
    """P0-1:dev-run 的 session start → observe → checkpoint 全鏈。"""

    def setUp(self):
        self.skill = read("skills/dev-run/SKILL.md")

    def test_session_start_is_in_the_preflight(self):
        self.assertIn("session start", self.skill)
        self.assertIn("--mode implementation", self.skill)
        preflight = self.skill[self.skill.index("## 前置"):
                               self.skill.index("## 誰做什麼")]
        self.assertIn("session start", preflight,
                      "memory session 必須在前置就開,不是做完才想起來")

    def test_observe_and_checkpoint_are_wired(self):
        self.assertIn("session observe", self.skill)
        self.assertIn("checkpoint $MEMORY_SESSION_ID", self.skill)

    def test_checkpoint_happens_after_regression_green(self):
        self.assertIn("回歸綠", self.skill)
        wrap_up = self.skill[self.skill.index("## 收尾"):]
        self.assertIn("checkpoint $MEMORY_SESSION_ID", wrap_up,
                      "固化必須在收尾(回歸綠之後),不是每個 T 就寫 Git")

    def test_high_and_low_signal_guidance_present(self):
        for term in ("高訊號", "低訊號", "schema 變更", "grep"):
            self.assertIn(term, self.skill, term)

    def test_verified_fact_evidence_rule_is_stated(self):
        self.assertIn("VERIFIED", self.skill)
        self.assertIn("dependencies", self.skill)
        self.assertIn("CANDIDATE", self.skill)

    def test_domain_knowledge_is_not_auto_confirmed(self):
        self.assertIn("code_inference", self.skill)
        self.assertIn("dev-talk", self.skill)

    def test_zero_promoted_is_declared_legal(self):
        self.assertIn("promoted: 0", self.skill)
        self.assertIn("本次完成", self.skill)

    def test_abort_is_covered(self):
        self.assertIn("abort $MEMORY_SESSION_ID", self.skill)
        self.assertIn("ABORTED", self.skill)


class CliSurfaceMatchesSkillsTest(unittest.TestCase):
    """雙向:SKILL 寫的指令 CLI 收得下;CLI 的生命週期指令 SKILL 有寫。"""

    TALK_SUBCOMMANDS = ("start", "turn", "propose", "confirm", "reject",
                        "correct", "checkpoint", "end", "status", "abort")
    SESSION_SUBCOMMANDS = ("start", "observe", "status", "list")

    def test_cli_exposes_every_talk_subcommand(self):
        text = cli_help("talk")
        for name in self.TALK_SUBCOMMANDS:
            self.assertIn(name, text, name)

    def test_cli_exposes_every_session_subcommand(self):
        text = cli_help("session")
        for name in self.SESSION_SUBCOMMANDS:
            self.assertIn(name, text, name)

    def test_cli_exposes_checkpoint_and_abort(self):
        top = cli_help()
        for name in ("checkpoint", "abort", "session", "talk"):
            self.assertIn(name, top, name)

    def test_skills_do_not_reference_commands_the_cli_lacks(self):
        """SKILL 裡出現的 `dev-memory.py <cmd>` 必須是 CLI 真的有的子命令。"""
        top = cli_help()
        available = set(re.findall(r"[a-z][a-z-]+", top.split("{", 1)[-1]
                                   .split("}", 1)[0]))
        for skill_path in ("skills/dev-talk/SKILL.md", "skills/dev-run/SKILL.md",
                           "skills/dev-setup/SKILL.md"):
            text = read(skill_path)
            for command in set(re.findall(r"dev-memory\.py\s+([a-z][a-z-]+)",
                                          text)):
                self.assertIn(command, available,
                              "{0} 寫了 CLI 沒有的指令:{1}".format(
                                  skill_path, command))

    def test_no_second_setup_entrypoint_in_skills(self):
        """dev-setup 是唯一 setup 入口 —— SKILL 不得教人用別的初始化指令。"""
        for skill_path in ("skills/dev-talk/SKILL.md", "skills/dev-run/SKILL.md"):
            text = read(skill_path)
            self.assertNotIn("dev-memory.py init", text)
            self.assertNotIn("dev-memory.py setup", text)
