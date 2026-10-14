import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher.check_local import validate_snapshot
from publisher.content import Blocked


class SnapshotCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for directory in ("chapters/ready", "chapters/draft", "plans"):
            (self.root / directory).mkdir(parents=True)
        self.rows = []
        self.plan()

    def plan(self):
        with (self.root / "plans/chapter_plan.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["chapter", "title", "status", "qa_status", "publish_status"])
            writer.writeheader()
            writer.writerows(self.rows)

    def chapter(self, number=137, folder="ready", title="下一次夜班", qa="pass"):
        path = self.root / f"chapters/{folder}/{number:04d}.md"
        path.write_text(f"---\nchapter: {number}\ntitle: {title}\nstatus: {folder}\nqa: {qa}\n---\n周衡把伞放在门边。\n", encoding="utf-8")
        self.rows.append(dict(chapter=number, title=title, status="completed", qa_status="pass", publish_status="ready"))
        self.plan()
        return path

    def snapshot(self):
        return {str(p.relative_to(self.root)): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}

    def test_valid_and_no_source_writes_or_network(self):
        self.chapter()
        before = self.snapshot()
        with patch("socket.socket", side_effect=AssertionError("network forbidden")), patch("subprocess.run", side_effect=AssertionError("git forbidden")):
            self.assertTrue(validate_snapshot(self.root)["ok"])
        self.assertEqual(before, self.snapshot())
        self.assertFalse((self.root / "runtime").exists())

    def test_missing_plan_rejected(self):
        self.chapter()
        self.rows.clear()
        self.plan()
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_duplicate_plan_rejected(self):
        self.chapter()
        self.rows.append(dict(self.rows[0]))
        self.plan()
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_title_mismatch_rejected(self):
        self.chapter()
        self.rows[0]["title"] = "完全不同的标题"
        self.plan()
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_short_title_rejected(self):
        self.chapter(title="夜班")
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_candidate_checks_actual_uncommitted_content_without_promoting(self):
        path = self.chapter(folder="draft")
        before = self.snapshot()
        result = validate_snapshot(self.root, path)
        self.assertEqual(0, result["ready_count"])
        self.assertEqual(137, result["chapters"][0]["chapter"])
        self.assertEqual(before, self.snapshot())
        self.assertIn("chapters/draft/0137.md", result["input_sha256"])

    def test_pending_qa_candidate_is_not_force_passed(self):
        path = self.chapter(folder="draft", qa="pending")
        with self.assertRaises(Blocked):
            validate_snapshot(self.root, path)

    def test_ready_pending_qa_rejected(self):
        self.chapter(qa="pending")
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_candidate_does_not_overwrite_ready(self):
        self.chapter()
        path = self.chapter(folder="draft")
        with self.assertRaises(Blocked):
            validate_snapshot(self.root, path)

    def test_symlink_rejected(self):
        path = self.chapter()
        target = self.root / "target.md"
        path.rename(target)
        path.symlink_to(target)
        with self.assertRaises(Blocked):
            validate_snapshot(self.root)

    def test_empty_queue_still_checks_plan_file(self):
        (self.root / "plans/chapter_plan.csv").unlink()
        with self.assertRaises(OSError):
            validate_snapshot(self.root)

    def test_wrong_candidate_chapter_number_rejected(self):
        path = self.chapter(folder="draft")
        path.write_text(path.read_text().replace("chapter: 137", "chapter: 138"))
        with self.assertRaises(Blocked):
            validate_snapshot(self.root, path)


if __name__ == "__main__":
    unittest.main()
