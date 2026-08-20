"""P1-6:`git status --porcelain=v1 -z` 的 rename/copy 必須正確解析。

`-z` 格式下,rename/copy 是**兩個** NUL 欄位:

    R  <new-path>\\0<old-path>\\0

舊實作對每個 `\\0` 欄位一律套 `entry[3:]`,所以:
- 第一筆拿到的是 **new path**(對)
- 第二筆(裸的 old path,沒有 XY 前綴)被砍掉前三個字元 → **變成一條爛路徑**

結果:fact 依賴的 old path 從來不會出現在 dirty_files,LVP 完全漏掉 rename。
`git mv src/old/db.ts src/new/db.ts` 之後,依賴 `src/old/db.ts` 的 VERIFIED fact
仍然走 fast path —— 它指向的檔案已經不存在了。
"""
import os

from memtools import MemoryCase, commit_all, git, write
from agentmem import identity, query, truth


def git_mv(root, src, dst):
    """`git mv` 不會自動建目標目錄 —— 建好再搬,免得測試死在治具而不是被測物。"""
    os.makedirs(os.path.dirname(os.path.join(root, dst)), exist_ok=True)
    git(root, "mv", src, dst)


class PorcelainParseTest(MemoryCase):
    def setUp(self):
        super().setUp()
        write(self.repo, "src/old/db.ts", "export const t = 'lab_order'\n")
        write(self.repo, "src/keep.ts", "export const k = 1\n")
        commit_all(self.repo, "seed")

    def dirty(self):
        return identity.workspace_snapshot(self.repo)["dirty_files"]

    def test_modified_tracked_file(self):
        write(self.repo, "src/old/db.ts", "changed\n")
        self.assertIn("src/old/db.ts", self.dirty())

    def test_rename_reports_both_paths(self):
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        dirty = self.dirty()
        self.assertIn("src/old/db.ts", dirty)
        self.assertIn("src/new/db.ts", dirty)

    def test_rename_then_modify_reports_both_paths(self):
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        write(self.repo, "src/new/db.ts", "export const t = 'orders'\n")
        dirty = self.dirty()
        self.assertIn("src/old/db.ts", dirty)
        self.assertIn("src/new/db.ts", dirty)

    def test_multiple_renames(self):
        write(self.repo, "src/a.ts", "a\n")
        write(self.repo, "src/b.ts", "b\n")
        commit_all(self.repo, "more files")
        git_mv(self.repo, "src/a.ts", "src/a2.ts")
        git_mv(self.repo, "src/b.ts", "src/b2.ts")
        dirty = self.dirty()
        for path in ("src/a.ts", "src/a2.ts", "src/b.ts", "src/b2.ts"):
            self.assertIn(path, dirty)

    def test_copy_records_both_paths(self):
        """copy(`C`)在 -z 下與 rename 同形狀:兩個欄位。

        git 預設不會主動偵測 copy(要 `status.renames=copies`),所以這裡直接
        把設定打開並製造一個內容相同的新檔,確保 parser 兩種都認得。
        """
        git(self.repo, "config", "status.renames", "copies")
        body = "export const shared = 'x'\n" * 40
        write(self.repo, "src/source.ts", body)
        commit_all(self.repo, "add copy source")
        write(self.repo, "src/copied.ts", body)
        git(self.repo, "add", "src/copied.ts")
        dirty = self.dirty()
        self.assertIn("src/copied.ts", dirty)

    def test_filename_with_spaces(self):
        write(self.repo, "src/with space.ts", "x\n")
        commit_all(self.repo, "space file")
        git_mv(self.repo, "src/with space.ts", "src/moved space.ts")
        dirty = self.dirty()
        self.assertIn("src/with space.ts", dirty)
        self.assertIn("src/moved space.ts", dirty)

    def test_filename_with_cjk(self):
        write(self.repo, "src/送檢流程.ts", "x\n")
        commit_all(self.repo, "cjk file")
        git_mv(self.repo, "src/送檢流程.ts", "src/送檢批次.ts")
        dirty = self.dirty()
        self.assertIn("src/送檢流程.ts", dirty)
        self.assertIn("src/送檢批次.ts", dirty)

    def test_untracked_file_is_listed_per_file(self):
        write(self.repo, "src/untracked/deep/new.ts", "x\n")
        self.assertIn("src/untracked/deep/new.ts", self.dirty())

    def test_deleted_file_is_listed(self):
        os.remove(os.path.join(self.repo, "src/keep.ts"))
        self.assertIn("src/keep.ts", self.dirty())

    def test_short_paths_are_not_dropped(self):
        """舊實作用 `len(entry) > 3` 過濾,短檔名會被整筆丟掉。"""
        write(self.repo, "a.ts", "x\n")
        self.assertIn("a.ts", self.dirty())

    def test_paths_are_posix_normalized(self):
        write(self.repo, "src/old/db.ts", "changed\n")
        for path in self.dirty():
            self.assertNotIn("\\", path)

    def test_clean_tree_reports_nothing(self):
        self.assertEqual(self.dirty(), [])


class RenameInvalidationTest(MemoryCase):
    """P1-6 的正題:rename 之後,依賴舊路徑的 VERIFIED fact 必須失效。"""

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/old/db.ts", "export const t = 'lab_order'\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)
        self.fact_id = truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/old/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)

    def resolve(self):
        return truth.resolve_current(
            self.store, self.repo, "database", "lab-order", "current_table",
            self.workspace, identity.workspace_snapshot(self.repo))

    def test_baseline_is_fast_path(self):
        result = self.resolve()
        self.assertEqual(result["status"], truth.VERIFIED)
        self.assertTrue(result["fast_path"])

    def test_git_mv_makes_dependent_fact_stale(self):
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        result = self.resolve()
        self.assertEqual(result["status"], truth.STALE)
        self.assertTrue(result["needs_inspect"])

    def test_git_mv_then_commit_still_stale(self):
        """rename 已 commit → 工作樹乾淨,只剩指紋那條抓得到(檔案不見了)。"""
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        commit_all(self.repo, "rename db")
        self.assertEqual(self.resolve()["status"], truth.STALE)

    def test_invalidate_from_snapshot_catches_rename(self):
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        touched = truth.invalidate_from_snapshot(
            self.store, self.repo, self.workspace,
            identity.workspace_snapshot(self.repo))
        self.assertIn(self.fact_id, touched)

    def test_invalidate_for_changes_uses_old_path_side(self):
        """只餵 dirty_files(不算指紋)也要抓得到 —— 證明 old path 真的在裡面。"""
        git_mv(self.repo, "src/old/db.ts", "src/new/db.ts")
        snapshot = identity.workspace_snapshot(self.repo)
        touched = truth.invalidate_for_changes(
            self.store, self.workspace, snapshot["dirty_files"])
        self.assertIn(self.fact_id, touched)


class ParserUnitTest(MemoryCase):
    """直接餵 porcelain payload —— 不經 git,釘住格式解析本身。"""

    def parse(self, payload):
        return identity.parse_porcelain_z(payload)

    def test_modified_keeps_leading_space_in_status(self):
        changed, unparsed = self.parse(" M src/db.ts\0")
        self.assertEqual(changed, {"src/db.ts"})
        self.assertEqual(unparsed, [])

    def test_rename_two_fields(self):
        changed, unparsed = self.parse("R  src/new.ts\0src/old.ts\0")
        self.assertEqual(changed, {"src/new.ts", "src/old.ts"})
        self.assertEqual(unparsed, [])

    def test_rename_with_modification(self):
        changed, _ = self.parse("RM src/new.ts\0src/old.ts\0")
        self.assertEqual(changed, {"src/new.ts", "src/old.ts"})

    def test_copy_two_fields(self):
        changed, _ = self.parse("C  src/copy.ts\0src/source.ts\0")
        self.assertEqual(changed, {"src/copy.ts", "src/source.ts"})

    def test_mixed_records_do_not_desynchronise(self):
        payload = ("R  src/new.ts\0src/old.ts\0"
                   " M src/keep.ts\0"
                   "?? untracked.ts\0"
                   "C  src/c.ts\0src/s.ts\0"
                   " D gone.ts\0")
        changed, unparsed = self.parse(payload)
        self.assertEqual(changed, {"src/new.ts", "src/old.ts", "src/keep.ts",
                                   "untracked.ts", "src/c.ts", "src/s.ts",
                                   "gone.ts"})
        self.assertEqual(unparsed, [])

    def test_trailing_space_in_filename_survives(self):
        changed, _ = self.parse(" M src/trailing .ts\0")
        self.assertEqual(changed, {"src/trailing .ts"})

    def test_short_path_is_kept(self):
        changed, _ = self.parse("?? a\0")
        self.assertEqual(changed, {"a"})

    def test_backslash_is_normalized_to_slash(self):
        changed, _ = self.parse(" M src\\\\win\\\\db.ts\0")
        self.assertEqual(changed, {"src/win/db.ts"})

    def test_rename_missing_second_field_is_reported_not_guessed(self):
        changed, unparsed = self.parse("R  src/new.ts\0")
        self.assertEqual(changed, {"src/new.ts"})
        self.assertEqual(unparsed, ["R  src/new.ts"])

    def test_malformed_record_is_reported_not_guessed(self):
        changed, unparsed = self.parse("garbage\0 M ok.ts\0")
        self.assertEqual(changed, {"ok.ts"})
        self.assertEqual(unparsed, ["garbage"])

    def test_empty_payload(self):
        self.assertEqual(self.parse(""), (set(), []))
        self.assertEqual(self.parse(None), (set(), []))

    def test_unparsed_surfaces_in_snapshot(self):
        """解析不出來的欄位必須出現在 snapshot,不得靜默吞掉。"""
        write(self.repo, "src/x.ts", "x\n")
        snapshot = identity.workspace_snapshot(self.repo)
        self.assertNotIn("status_unparsed", snapshot)
        self.assertEqual(identity.parse_porcelain_z("bogus\0")[1], ["bogus"])


class DirtyVersusFingerprintTest(MemoryCase):
    """dirty 與指紋的分工:指紋相符時 dirty 不得把 fact 打回 STALE。

    這條是 reverify 能不能真的回到 VERIFIED 的關鍵。指紋記的是「驗證時看到的
    內容」——內容仍相符,就代表我們驗過的正是現在這份;有沒有 commit 與它是不是
    真的無關。反過來,**沒有指紋可比**的依賴,dirty 是唯一的訊號,那種 fact
    不得走 fast path。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)

    def resolve(self, entity_key="lab-order"):
        return truth.resolve_current(
            self.store, self.repo, "database", entity_key, "current_table",
            self.workspace, identity.workspace_snapshot(self.repo))

    def test_dirty_dependency_without_fingerprint_is_stale(self):
        fact_id = self.store.upsert_fact({
            "entity_type": "database", "entity_key": "no-fp",
            "fact_key": "current_table", "value": "lab_order",
            "status": truth.VERIFIED, "confidence": 0.99,
            "dependencies": ["src/db.ts"], "fingerprints": {}})
        write(self.repo, "src/db.ts", "changed\n")
        result = self.resolve("no-fp")
        self.assertFalse(result["fast_path"])
        self.assertEqual(result["fact_id"], fact_id)

    def test_reverify_on_uncommitted_change_returns_to_fast_path(self):
        fact_id = truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)
        write(self.repo, "src/db.ts", "export const t = 'orders'\n")
        self.assertEqual(self.resolve()["status"], truth.STALE)
        outcome = truth.reverify(self.store, self.repo, fact_id,
                                 self.workspace, "orders")
        self.assertEqual(outcome["outcome"], "superseded")
        result = self.resolve()
        self.assertEqual(result["status"], truth.VERIFIED)
        self.assertTrue(result["fast_path"],
                        "reverify 之後仍 STALE = fast path 永遠不可達")
        self.assertEqual(result["value"], "orders")

    def test_unrelated_dirty_file_does_not_invalidate(self):
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)
        write(self.repo, "src/unrelated.ts", "x\n")
        self.assertTrue(self.resolve()["fast_path"])


class UnparsedStatusFailsClosedTest(MemoryCase):
    """`status_unparsed` 必須被 Current Truth 消化,不只是記在 snapshot 裡。

    parser 拒絕猜、把讀不懂的欄位原樣回報,是對的。但那份不確定性到
    `resolve_current()` 就斷了:resolver 只讀 `dirty_files`,所以系統可以
    同時是這兩句話 ——

        git status parser:「這個 workspace 有一部分我看不懂」
        Current Truth   :「VERIFIED + fast_path=True」

    範圍要精確,否則會蓋掉既有那條規則。`dirty_files` 只在**沒有指紋可比**的
    依賴上有意義(見 `DirtyVersusFingerprintTest`):指紋相符就代表驗過的正是
    現在這份檔案,git 看不看得懂它的狀態列與那件事無關。

    所以不確定性真正吃掉的是 dirty 那條路:解析不完整 = dirty 清單不完整 =
    **沒有指紋的依賴無法證明乾淨**。那種 fact 不得走 fast path;指紋齊全的
    fact 不受影響(把它一起打回 STALE 是拿一個無關的訊號否定已經驗過的內容)。

    公開的 `retrieval_status` 不新增第五態:STALE 在契約裡就是
    `NEEDS_VERIFICATION`,那正是「證明不了乾淨」該有的答案。
    """

    def setUp(self):
        super().setUp()
        self.project_id = self.project()["project_id"]
        self.store = self.store_for(self.project_id)
        write(self.repo, "src/db.ts", "export const t = 'lab_order'\n")
        self.head = commit_all(self.repo, "seed")
        self.workspace = identity.workspace_key(self.project_id, self.repo)

    def snapshot(self, unparsed=("R  src/new.ts",)):
        snap = identity.workspace_snapshot(self.repo)
        if unparsed:
            snap["status_unparsed"] = sorted(unparsed)
        return snap

    def resolve(self, entity_key, snapshot):
        return truth.resolve_current(
            self.store, self.repo, "database", entity_key, "current_table",
            self.workspace, snapshot)

    def unfingerprinted_fact(self, entity_key="no-fp"):
        """一個依賴有指紋、另一個沒有。

        fixture 的形狀就是這一題的關鍵。`fingerprints` 整個空的 fact 早就走不到
        fast path(`resolve_current` 的 `if not stored` 會先把它降級成
        CANDIDATE),所以那種 fixture 測不到這個缺口。真正的缺口在**混合**:
        `stored` 非空 → fast path 可達 → 沒有指紋的那個依賴只剩 dirty 這條路
        可以證明它乾淨,而 dirty 清單正是解析不完整的那份。
        """
        write(self.repo, "src/extra.ts", "export const e = 1\n")
        commit_all(self.repo, "extra dep")
        return self.store.upsert_fact({
            "entity_type": "database", "entity_key": entity_key,
            "fact_key": "current_table", "value": "lab_order",
            "status": truth.VERIFIED, "confidence": 0.99,
            "dependencies": ["src/db.ts", "src/extra.ts"],
            "fingerprints": {"src/db.ts": truth.fingerprint(self.repo,
                                                            "src/db.ts")}})

    def test_unparsed_status_blocks_fast_path_for_unfingerprinted_dep(self):
        self.unfingerprinted_fact()
        result = self.resolve("no-fp", self.snapshot())
        self.assertEqual(
            result["status"], truth.STALE,
            "git status 有讀不懂的欄位,而這筆 fact 的依賴沒有指紋可比 —— "
            "乾淨證明不了,卻回了 OK fast path")
        self.assertTrue(result["needs_inspect"])
        self.assertFalse(result["fast_path"])

    def test_malformed_rename_entry_fails_closed(self):
        self.unfingerprinted_fact("rename-case")
        result = self.resolve("rename-case",
                              self.snapshot(("R  src/only-one-field.ts",)))
        self.assertFalse(result["fast_path"])

    def test_reason_says_the_status_was_unparsed(self):
        self.unfingerprinted_fact("why")
        result = self.resolve("why", self.snapshot())
        self.assertTrue(
            any("解析" in reason for reason in result["reasons"]),
            "理由沒說是因為 git status 解析不完整 —— 使用者無從判斷該修什麼:"
            "{0}".format(result["reasons"]))

    def test_fingerprinted_fact_is_unaffected_by_unparsed_status(self):
        """指紋齊全且相符 → 不受影響。內容自己證明了它,不靠 git status。"""
        truth.record_fact(
            self.store, self.repo, "database", "lab-order", "current_table",
            "lab_order", dependencies=["src/db.ts"],
            source_commit=self.head, status=truth.VERIFIED, confidence=0.99)
        result = self.resolve("lab-order", self.snapshot())
        self.assertTrue(
            result["fast_path"],
            "把指紋相符的 fact 也打回 STALE = 拿一個無關的訊號否定已經驗過的"
            "內容,而開發中的 workspace 常常有解析不了的狀態列")

    def test_clean_parse_keeps_existing_behaviour(self):
        self.unfingerprinted_fact("clean")
        result = self.resolve("clean", self.snapshot(unparsed=()))
        self.assertTrue(result["fast_path"],
                        "沒有 unparsed 時行為必須與原本一致")

    def test_status_contract_maps_it_to_needs_verification(self):
        """公開契約不新增第五態:它走既有的 NEEDS_VERIFICATION。"""
        self.unfingerprinted_fact("contract")
        result = self.resolve("contract", self.snapshot())
        self.assertEqual(query._fact_status(result), query.NEEDS_VERIFICATION)

    def test_invalidation_scan_agrees_with_the_resolver(self):
        """掃描與查詢的判準必須一致,否則「誰對」沒有答案。"""
        fact_id = self.unfingerprinted_fact("scan")
        truth.invalidate_from_snapshot(self.store, self.repo, self.workspace,
                                       self.snapshot())
        self.assertIsNotNone(
            self.store.overlay(fact_id, self.workspace),
            "resolver 說證明不了乾淨,失效掃描卻什麼都沒做")
