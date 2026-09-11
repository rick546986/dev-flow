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
