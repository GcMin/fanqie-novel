import argparse
import asyncio
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher.adapters import AcceptedReviewsAdapter, blob_hash, chinese_number
from publisher.content import Blocked
from publisher.__main__ import Journal, cycle


class AcceptedReviewsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.adapter = AcceptedReviewsAdapter('999')
        self.make_fixture()

    def write(self, name, value):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        raw = json.dumps(value, ensure_ascii=False, indent=2).encode() if isinstance(value, dict) else value.encode()
        p.write_bytes(raw)
        return blob_hash(raw)

    def make_fixture(self, review_changes=None, body=None):
        self.body_sha = self.write('chapters/000001.md', body or '# 第一章 投币口不负责出鱼\n\n**三个人一起走进游戏。**\n\n出口还亮着。\n')
        common = dict(chapter_id='000001', run_id='run-1', revision='v001', contract_hash='contract-1', draft_hash=self.body_sha)
        refs, results = {}, []
        for role in ('continuity', 'reader_editor'):
            review = dict(common, role_id=role, verdict='PASS', issues=[])
            if role == 'reader_editor': review.update(review_changes or {})
            path = f'reviews/000001/{role}/review.json'
            sha = self.write(path, review)
            refs[role] = dict(path=path, sha=sha, verdict='PASS')
            results.append(dict(role=role, review_sha=sha, verdict='PASS'))
        decision = dict(common, decision='ACCEPT_UNCHANGED', review_results=results,
                        blocking_critical=0, blocking_major=0, revision_required=False)
        self.write('reviews/000001/showrunner/decision.json', decision)
        self.acceptance = dict(common, status='COMMITTED', accepted_draft_hash=self.body_sha,
                               prose=dict(path='chapters/000001.md', sha=self.body_sha), reviews=refs,
                               decision='reviews/000001/showrunner/decision.json',
                               idempotency_key=f'000001+{self.body_sha}', publication=False)
        self.write('reviews/000001/acceptance.json', self.acceptance)

    def test_plain_text_and_number_from_accepted_source(self):
        chapter, = self.adapter.scan(self.root)
        self.assertEqual(chapter.number, 1)
        self.assertEqual(chapter.title, '投币口不负责出鱼')
        self.assertEqual(chapter.body, '三个人一起走进游戏。\n\n出口还亮着。')
        self.assertEqual(chinese_number('一百二十四'), 124)
        self.assertEqual(chinese_number('1001'), 1001)
        self.assertFalse((self.root / 'publication').exists())

    def test_missing_or_uncommitted_acceptance_is_never_a_publish_source(self):
        self.write('chapters/000002.md', '# 第二章 还没有审核正文\n草稿。')
        self.assertEqual(len(self.adapter.scan(self.root)), 1)
        self.acceptance['status'] = 'DUAL_REVIEW'
        self.write('reviews/000001/acceptance.json', self.acceptance)
        self.assertEqual(self.adapter.scan(self.root), [])

    def test_exact_prose_review_and_acceptance_hashes_are_required(self):
        for name in ('chapters/000001.md', 'reviews/000001/continuity/review.json', 'reviews/000001/reader_editor/review.json'):
            self.make_fixture()
            p = self.root / name
            p.write_bytes(p.read_bytes() + b' ')
            with self.assertRaises(Blocked, msg=name): self.adapter.scan(self.root)
        self.make_fixture()
        self.acceptance['accepted_draft_hash'] = 'wrong'
        self.write('reviews/000001/acceptance.json', self.acceptance)
        with self.assertRaises(Blocked): self.adapter.scan(self.root)

    def test_even_rehashed_failed_stale_or_blocking_reviews_are_rejected(self):
        for changes in ({'verdict': 'REVISE'}, {'draft_hash': 'older'}, {'chapter_id': '000002'},
                        {'contract_hash': 'older'}, {'run_id': 'other'}, {'revision': 'v002'},
                        {'issues': [{'severity': 'major', 'blocking': False}]}, {'must_fix_issues': ['fix']}):
            self.make_fixture(changes)
            with self.assertRaises(Blocked, msg=str(changes)): self.adapter.scan(self.root)

    def test_unapproved_body_and_number_mismatch_are_rejected(self):
        for body in ('# 第二章 投币口不负责出鱼\n正文。', '# 第一章 投币口不负责出鱼\n## 内部大纲\n不能上传。',
                     '# 第一章 投币口不负责出鱼\n[内部文件](reviews/x.json)', '# 第一章 投币口不负责出鱼\n<script>内部</script>',
                     '# 第一章 投币口不负责出鱼\n*未支持的斜体*', '# 第一章 投币口不负责出鱼\n`未支持的行内代码`'):
            self.make_fixture(body=body)
            with self.assertRaises(Blocked): self.adapter.scan(self.root)

    def test_archive_is_independent_idempotent_and_never_moves_prose(self):
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        chapter, = self.adapter.scan(self.root)
        self.adapter.archive(self.root, chapter, 'https://fanqienovel.com/main/writer/999/publish/777')
        path = self.root / 'publication/fanqie/000001.json'
        first = path.read_bytes()
        self.adapter.archive(self.root, chapter, 'https://fanqienovel.com/main/writer/999/publish/777')
        self.assertEqual(path.read_bytes(), first)
        self.assertEqual(self.adapter.scan(self.root), [])
        for name, raw in before.items(): self.assertEqual((self.root / name).read_bytes(), raw)
        self.assertFalse((self.root / 'chapters/published').exists())
        with self.assertRaises(Blocked): AcceptedReviewsAdapter('998').scan(self.root)

    def test_archive_checks_remote_book_and_new_proof_version(self):
        chapter, = self.adapter.scan(self.root)
        with self.assertRaises(Blocked): self.adapter.archive(self.root, chapter, 'https://fanqienovel.com/main/writer/998/publish/777')
        self.acceptance['run_id'] = 'changed'
        self.write('reviews/000001/acceptance.json', self.acceptance)
        with self.assertRaises(Blocked): self.adapter.archive(self.root, chapter, 'https://fanqienovel.com/main/writer/999/publish/777')

    def test_external_proof_symlink_is_rejected(self):
        path = self.root / 'reviews/000001/continuity/review.json'
        target = self.root / 'outside.json'
        target.write_bytes(path.read_bytes()); path.unlink()
        try: path.symlink_to(target)
        except OSError: self.skipTest('Symbolic links unavailable')
        with self.assertRaises(Blocked): self.adapter.scan(self.root)

    def test_pending_then_published_cycle_keeps_source_and_stages_only_record(self):
        calls = []
        root = self.root
        class Repo:
            branch = 'main'
            def __init__(inner): inner.root = root
            def sync(inner): pass
            def git(inner, *args): calls.append(args)
        class Site:
            submits = 0
            state = 'pending'
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def duplicate_check(inner, chapter): pass
            async def create(inner): return 'https://fanqienovel.com/main/writer/999/publish/777'
            async def fill(inner, chapter): pass
            async def submit(inner): inner.submits += 1
            async def save_session(inner): pass
            async def verify(inner, chapter, url): return inner.state
        site = Site(); journal = Journal(self.root / 'journal.db', 'test')
        self.addCleanup(journal.db.close)
        args = argparse.Namespace(command='run', chapter=None, url=None, until_quota=False)
        with patch.dict(os.environ, {'SOURCE_FORMAT': 'accepted_reviews', 'FANQIE_BOOK_ID': '999', 'PUBLISH_ENABLED': 'true'}):
            asyncio.run(cycle(args, root, Repo(), journal, lambda: site))
            self.assertFalse((root / 'publication').exists())
            site.state = 'published'
            asyncio.run(cycle(args, root, Repo(), journal, lambda: site))
            asyncio.run(cycle(args, root, Repo(), journal, lambda: site))
        self.assertEqual(site.submits, 1)
        self.assertEqual(journal.get(1)['phase'], 'published')
        self.assertTrue((root / 'chapters/000001.md').exists())
        self.assertEqual(calls[0], ('add', '--', 'publication/fanqie/000001.json'))

    def test_changed_proof_after_filling_never_clicks_submit(self):
        root = self.root
        class Repo:
            def __init__(inner): inner.root = root
            def sync(inner): pass
        owner = self
        class Site:
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def duplicate_check(inner, chapter): pass
            async def create(inner): return 'url'
            async def fill(inner, chapter):
                owner.acceptance['status'] = 'REVISE'
                owner.write('reviews/000001/acceptance.json', owner.acceptance)
            async def submit(inner): raise AssertionError('Stale evidence must not submit')
        journal = Journal(self.root / 'journal.db', 'test'); self.addCleanup(journal.db.close)
        args = argparse.Namespace(command='run', chapter=None, url=None)
        with patch.dict(os.environ, {'SOURCE_FORMAT': 'accepted_reviews', 'FANQIE_BOOK_ID': '999', 'PUBLISH_ENABLED': 'true'}):
            with self.assertRaises(Blocked): asyncio.run(cycle(args, root, Repo(), journal, Site))
        self.assertEqual(journal.get(1)['phase'], 'editing')
