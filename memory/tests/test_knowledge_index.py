"""#155 knife-2: ask 接短知識索引(docs/knowledge/index.yaml)。"""
import os

from memtools import MemoryCase, write
from agentmem import embedding, identity, knowledge_index, query, retrieval


MINI_INDEX = """\
schema_version: 1
generated_from:
  - docs/adr/*.md
notes:
topics:
  agent-memory:
    glossary: []
    active_adr: ["0003"]
    active_spec: []
    durable:
      decisions: []
      knowledge: []
    supersedes: []
    conflicts: []
unscoped:
  decisions: []
  knowledge: []
"""


class KnowledgeIndexRouteTest(MemoryCase):
    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.snapshot = identity.workspace_snapshot(self.repo)

    def _seed_adr_0003(self):
        write(self.repo, os.path.join("docs", "adr",
                                      "0003-agent-memory-two-layer-split.md"),
              "---\nstatus: accepted\ntopics: [agent-memory]\n---\n# 0003\n")
        # decoy ADR — index 不得因為掃目錄而回這份
        write(self.repo, os.path.join("docs", "adr",
                                      "0001-unrelated-other-topic.md"),
              "---\nstatus: accepted\ntopics: [other]\n---\n# 0001\n")

    def _write_index(self, text=MINI_INDEX):
        write(self.repo, os.path.join("docs", "knowledge", "index.yaml"), text)

    def ask(self, text):
        return query.execute(self.store, self.repo, text, self.workspace,
                             self.snapshot, self.embedder)

    def test_topic_hit_routes_to_0003_path_only(self):
        self._seed_adr_0003()
        self._write_index()
        answer = self.ask("目前 agent-memory 決策指向哪份 ADR?")
        self.assertEqual(answer["retrieval_status"], retrieval.OK)
        route = answer["knowledge_index"]
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["matched_topics"], ["agent-memory"])
        paths = [p["path"] for p in route["paths"]]
        self.assertEqual(
            paths,
            ["docs/adr/0003-agent-memory-two-layer-split.md"])
        # 不得預載 / 誤帶 0001
        self.assertFalse(any("0001" in p for p in paths))
        refs = [r["ref"] for r in answer["results"]
                if r.get("item_type") == "knowledge_index"]
        self.assertEqual(refs, ["0003"])

    def test_unknown_topic_does_not_invent_paths(self):
        self._seed_adr_0003()
        self._write_index()
        answer = self.ask("目前 totally-unknown-topic 怎麼運作?")
        route = answer["knowledge_index"]
        self.assertEqual(route["status"], knowledge_index.UNKNOWN_TOPIC)
        self.assertEqual(route["paths"], [])
        self.assertFalse(any(
            r.get("item_type") == "knowledge_index" for r in answer["results"]))
        # 無 store 命中 → 既有 NO_RELIABLE_MATCH 語意保留
        self.assertEqual(answer["retrieval_status"], retrieval.NO_RELIABLE_MATCH)

    def test_missing_index_degrades_gracefully(self):
        self._seed_adr_0003()
        # 故意不寫 index.yaml
        self.assertFalse(os.path.isfile(
            os.path.join(self.repo, "docs", "knowledge", "index.yaml")))
        answer = self.ask("目前 agent-memory 決策指向哪份 ADR?")
        route = answer["knowledge_index"]
        self.assertEqual(route["status"], knowledge_index.MISSING_INDEX)
        self.assertIn("missing", route["note"])
        self.assertEqual(route["paths"], [])
        # 降級:不炸,走既有檢索;此 fixture 無記憶 → NO_RELIABLE_MATCH
        self.assertEqual(answer["retrieval_status"], retrieval.NO_RELIABLE_MATCH)
        self.assertIn("knowledge_index", answer)

    def test_block_style_fixture_index_also_loads(self):
        """Pilot-3 fixture 用 block list,產生器用 flow list —— 兩種都要能讀。"""
        self._seed_adr_0003()
        write(self.repo, os.path.join("docs", "knowledge", "index.yaml"),
              "schema_version: 1\n"
              "topics:\n"
              "  agent-memory:\n"
              "    glossary: []\n"
              "    active_adr:\n"
              "      - \"0003\"\n"
              "    active_spec: []\n"
              "    durable:\n"
              "      decisions: []\n"
              "      knowledge: []\n"
              "    supersedes: []\n"
              "    conflicts: []\n")
        route = knowledge_index.route(
            self.repo, "agent-memory",
            {"query": "agent-memory", "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["paths"][0]["ref"], "0003")

    def test_unquoted_cjk_space_topic_keys_load_and_ask_run_hits(self):
        """#190: legacy unquoted CJK/space keys must not make whole index UNREADABLE.

        Previously yamlmini rejected `Report 資料夾:` → status=unreadable even when
        asking for an ASCII topic like Run that would otherwise hit.
        """
        from agentmem import durable

        durable.write_knowledge(self.repo, {
            "kind": "domain", "key": "Run",
            "title": "Run = one processing execution",
            "body": "A Run is one execution unit, not a folder.",
            "authority": "domain_expert", "status": "CONFIRMED",
            "confidence": 0.95, "recorded_at": "2026-09-12T00:00:00Z",
        })
        # Intentionally unquoted (pre-fix generator shape) + flow lists.
        index = (
            "schema_version: 1\n"
            "generated_from:\n"
            "  - docs/adr/*.md\n"
            "notes:\n"
            "topics:\n"
            "  Report 資料夾:\n"
            "    glossary: [Report 資料夾]\n"
            "    active_adr: []\n"
            "    active_spec: []\n"
            "    durable:\n"
            "      decisions: []\n"
            "      knowledge: []\n"
            "    supersedes: []\n"
            "    conflicts: []\n"
            "  來源衝突:\n"
            "    glossary: [來源衝突]\n"
            "    active_adr: []\n"
            "    active_spec: []\n"
            "    durable:\n"
            "      decisions: []\n"
            "      knowledge: []\n"
            "    supersedes: []\n"
            "    conflicts: []\n"
            "  Run:\n"
            "    glossary: [Run]\n"
            "    active_adr: []\n"
            "    active_spec: []\n"
            "    durable:\n"
            "      decisions: []\n"
            "      knowledge: []\n"
            "    supersedes: []\n"
            "    conflicts: []\n"
            "unscoped:\n"
            "  decisions: []\n"
            "  knowledge: []\n"
        )
        self._write_index(index)

        status, data, _path = knowledge_index.load(self.repo)
        self.assertEqual(status, "ok", "legacy CJK/space keys must load")
        self.assertIn("Report 資料夾", data["topics"])
        self.assertIn("來源衝突", data["topics"])
        self.assertIn("Run", data["topics"])

        route = knowledge_index.route(
            self.repo, "Run",
            {"query": "Run", "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["matched_topics"], ["Run"])
        self.assertTrue(any(
            p["kind"] == "glossary" and p["ref"] == "Run"
            and p["path"].startswith(".dev-flow/knowledge/domain/")
            for p in route["paths"]), route["paths"])

        answer = self.ask("Run")
        self.assertEqual(answer["knowledge_index"]["status"], knowledge_index.HIT)
        self.assertEqual(answer["knowledge_index"]["matched_topics"], ["Run"])
        refs = [r["ref"] for r in answer["results"]
                if r.get("item_type") == "knowledge_index"]
        self.assertEqual(refs, ["Run"])

    def test_quoted_cjk_space_topic_keys_also_load(self):
        """#190: generator-quoted topic keys must load the same way."""
        index = (
            "schema_version: 1\n"
            "topics:\n"
            '  "Report 資料夾":\n'
            '    glossary: ["Report 資料夾"]\n'
            "    active_adr: []\n"
            "    active_spec: []\n"
            "    durable:\n"
            "      decisions: []\n"
            "      knowledge: []\n"
            "    supersedes: []\n"
            "    conflicts: []\n"
            '  "Run":\n'
            "    glossary: [Run]\n"
            "    active_adr: []\n"
            "    active_spec: []\n"
            "    durable:\n"
            "      decisions: []\n"
            "      knowledge: []\n"
            "    supersedes: []\n"
            "    conflicts: []\n"
        )
        self._write_index(index)
        status, data, _path = knowledge_index.load(self.repo)
        self.assertEqual(status, "ok")
        self.assertIn("Report 資料夾", data["topics"])
        route = knowledge_index.route(
            self.repo, "Run",
            {"query": "Run", "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)


CJK_SPACE_INDEX = """\
schema_version: 1
topics:
  Report 資料夾:
    glossary: []
    active_adr: ["0003"]
    active_spec: []
    durable:
      decisions: []
      knowledge: []
    supersedes: []
    conflicts: []
  來源衝突:
    glossary: []
    active_adr: ["0003"]
    active_spec: []
    durable:
      decisions: []
      knowledge: []
    supersedes: []
    conflicts: []
  Run Specimen:
    glossary: []
    active_adr: ["0003"]
    active_spec: []
    durable:
      decisions: []
      knowledge: []
    supersedes: []
    conflicts: []
  Run:
    glossary: []
    active_adr: ["0003"]
    active_spec: []
    durable:
      decisions: []
      knowledge: []
    supersedes: []
    conflicts: []
unscoped:
  decisions: []
  knowledge: []
"""


class TopicKeyContainmentConsultTest(MemoryCase):
    """#194: long / CJK NL consults index when it contains a real topic key."""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        self.embedder = embedding.Embedder()
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.snapshot = identity.workspace_snapshot(self.repo)
        write(self.repo, os.path.join("docs", "adr",
                                      "0003-agent-memory-two-layer-split.md"),
              "---\nstatus: accepted\ntopics: [agent-memory]\n---\n# 0003\n")
        write(self.repo, os.path.join("docs", "knowledge", "index.yaml"),
              CJK_SPACE_INDEX)

    def ask(self, text):
        return query.execute(self.store, self.repo, text, self.workspace,
                             self.snapshot, self.embedder)

    def test_cjk_key_inside_chinese_sentence_hits(self):
        # Pure-CJK key + long Chinese framing → 0 ASCII words → old heuristic skips.
        q = (
            "能不能幫我仔細說明一下這個叫做來源衝突的東西"
            "在整條處理流程裡面到底扮演什麼角色以及它跟其他步驟的關係"
        )
        self.assertFalse(
            knowledge_index.should_consult(
                {"query": q, "primary": "DISCOVERY"}, query=q),
            "baseline: long pure-CJK sentence is not short-ASCII topic-like")
        route = knowledge_index.route(
            self.repo, q, {"query": q, "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["matched_topics"], ["來源衝突"])
        answer = self.ask(q)
        self.assertEqual(answer["knowledge_index"]["status"], knowledge_index.HIT)
        self.assertEqual(
            answer["knowledge_index"]["matched_topics"], ["來源衝突"])

    def test_cjk_space_key_report_folder_in_long_query_hits(self):
        # Key has ASCII+CJK; bury it in >6 ASCII words so slug/word heuristics miss.
        q = (
            "please carefully explain what the Report 資料夾 concept means "
            "for operators during overnight batch processing and how it "
            "connects to upstream intake validation checkpoints overall"
        )
        self.assertFalse(
            knowledge_index.should_consult(
                {"query": q, "primary": "DISCOVERY"}, query=q),
            "baseline: >6 ASCII words is not short topic-like")
        route = knowledge_index.route(
            self.repo, q, {"query": q, "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["matched_topics"], ["Report 資料夾"])

    def test_space_key_run_specimen_inside_query_hits(self):
        q = (
            "please walk me through how the Run Specimen concept fits into "
            "our production pipeline and what operators should check first "
            "before kicking off another batch overnight"
        )
        self.assertFalse(
            knowledge_index.should_consult(
                {"query": q, "primary": "DISCOVERY"}, query=q),
            "baseline: long English (>6 ASCII words) is not topic-like")
        route = knowledge_index.route(
            self.repo, q, {"query": q, "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        # "Run" is a word-boundary substring of "Run Specimen" → multi-hit
        self.assertEqual(route["matched_topics"], ["Run", "Run Specimen"])
        self.assertIn("Run Specimen", route["matched_topics"])
        self.assertIn("multi-topic match", route["note"] or "")

    def test_long_sentence_without_topic_key_is_skipped(self):
        q = (
            "能不能幫我仔細說明一下整條處理流程裡面各個步驟之間的關係"
            "以及操作人員在夜間批次啟動前應該先檢查哪些事項"
        )
        route = knowledge_index.route(
            self.repo, q, {"query": q, "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.SKIPPED)
        self.assertEqual(route["matched_topics"], [])
        self.assertEqual(route["paths"], [])
        answer = self.ask(q)
        self.assertEqual(
            answer["knowledge_index"]["status"], knowledge_index.SKIPPED)

    def test_ascii_short_slug_path_unchanged(self):
        route = knowledge_index.route(
            self.repo, "Run",
            {"query": "Run", "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(route["matched_topics"], ["Run"])
        self.assertTrue(
            knowledge_index.should_consult(
                {"query": "Run", "primary": "DISCOVERY"}, query="Run"))

    def test_multi_topic_match_returns_union_and_documents(self):
        q = (
            "please carefully compare 來源衝突 versus Run Specimen including "
            "responsibility boundaries handoff points and overnight operator "
            "checklist items across the whole processing pipeline end to end"
        )
        self.assertFalse(
            knowledge_index.should_consult(
                {"query": q, "primary": "DISCOVERY"}, query=q))
        route = knowledge_index.route(
            self.repo, q, {"query": q, "primary": "DISCOVERY"})
        self.assertEqual(route["status"], knowledge_index.HIT)
        self.assertEqual(
            route["matched_topics"], ["Run", "Run Specimen", "來源衝突"])
        self.assertIn("multi-topic match", route["note"] or "")
        self.assertTrue(any(
            p["path"] == "docs/adr/0003-agent-memory-two-layer-split.md"
            for p in route["paths"]))
