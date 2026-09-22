import argparse
import asyncio
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from publisher.content import Blocked, DailyQuota, archive, parse, scan, validate_title
from publisher.__main__ import Journal, cycle


SOURCE = '''---
chapter: 1
title: 门后的脚步
status: ready
qa: pass
---
# 第1章 门后的脚步
<!-- QA备注：只供内部阅读 -->
门外传来脚步声。

她把信塞进袖口。
'''


class ContentTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'chapters/ready').mkdir(parents=True)
        (self.root / 'plans').mkdir()
        self.path = self.root / 'chapters/ready/001.md'
        self.path.write_text(SOURCE, encoding='utf-8')
        (self.root / 'plans/chapter_plan.csv').write_text(
            'chapter,title,status,qa_status,publish_status\n1,门后的脚步,completed,pass,ready\n', encoding='utf-8')

    def test_strip_internal_content(self):
        chapter = scan(self.root)[0]
        self.assertEqual(chapter.body, '门外传来脚步声。\n\n她把信塞进袖口。')
        self.assertEqual(chapter.title, '门后的脚步')

    def test_short_title_rejected_before_upload(self):
        self.path.write_text(SOURCE.replace('title: 门后的脚步', 'title: "704"').replace('# 第1章 门后的脚步', '# 第1章 704'), encoding='utf-8')
        with self.assertRaisesRegex(Blocked, '至少需要 5'):
            validate_title(parse(self.path, self.root))

    def test_draft_and_failed_qa_block(self):
        for source in (SOURCE.replace('status: ready', 'status: draft'), SOURCE.replace('qa: pass', 'qa: fail')):
            self.path.write_text(source, encoding='utf-8')
            with self.assertRaises(Blocked):
                scan(self.root)

    def test_internal_notes_block(self):
        for note in ('TODO 下一章', '## 大纲', '字数统计：3000', 'QA备注：pass', '<!-- 未关闭', '摘要：上一章', 'status: draft'):
            self.path.write_text(SOURCE + note, encoding='utf-8')
            with self.assertRaises(Blocked, msg=note):
                scan(self.root)

    def test_readme_excluded_and_duplicate_number_block(self):
        (self.path.parent / 'README.md').write_text('内部说明', encoding='utf-8')
        self.assertEqual(len(scan(self.root)), 1)
        (self.path.parent / '002.md').write_text(SOURCE, encoding='utf-8')
        with self.assertRaises(Blocked):
            scan(self.root)

    def test_other_directory_block(self):
        draft = self.root / 'chapters/draft'
        draft.mkdir()
        path = draft / '001.md'
        path.write_text(SOURCE, encoding='utf-8')
        with self.assertRaises(Blocked):
            parse(path, self.root)

    def test_plan_gate(self):
        (self.root / 'plans/chapter_plan.csv').write_text(
            'chapter,title,status,qa_status,publish_status\n1,门后的脚步,planned,pending,blocked\n', encoding='utf-8')
        with self.assertRaises(Blocked):
            scan(self.root)

    def test_archive(self):
        chapter = scan(self.root)[0]
        archive(self.root, chapter)
        self.assertFalse(self.path.exists())
        self.assertIn('status: published', (self.root / 'chapters/published/001.md').read_text(encoding='utf-8'))
        self.assertIn('completed,pass,published', (self.root / 'plans/chapter_plan.csv').read_text(encoding='utf-8'))

    def test_journal_scope_and_immutable_source(self):
        journal = Journal(self.root / 'journal.db', 'a')
        self.addCleanup(journal.db.close)
        chapter = scan(self.root)[0]
        journal.put(chapter, 'submitted', 'url')
        self.path.write_text(SOURCE + '变更', encoding='utf-8')
        with self.assertRaises(Blocked):
            journal.put(scan(self.root)[0], 'published')
        with self.assertRaises(Blocked):
            Journal(self.root / 'journal.db', 'b')

    def run_cycle(self, site, journal):
        class Repo:
            root = self.root
            def sync(inner):
                pass
            def commit_archive(inner, *args):
                pass
        args = argparse.Namespace(command='run', chapter=None, url=None)
        with patch.dict(os.environ, {'PUBLISH_ENABLED': 'true'}):
            asyncio.run(cycle(args, self.root, Repo(), journal, lambda: site))

    def test_submit_failure_never_resubmits(self):
        journal = Journal(self.root / 'journal.db', 'a')
        self.addCleanup(journal.db.close)
        class Site:
            submits = 0
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def duplicate_check(inner, chapter): pass
            async def create(inner): return 'url'
            async def fill(inner, chapter): pass
            async def submit(inner):
                inner.submits += 1
                raise TimeoutError('network failed after submit')
            async def verify(inner, chapter, url): return 'pending'
        site = Site()
        with self.assertRaises(TimeoutError): self.run_cycle(site, journal)
        self.assertEqual(journal.get(1)['phase'], 'submitted')
        self.run_cycle(site, journal)
        self.assertEqual(site.submits, 1)
        self.assertTrue(self.path.exists())

    def test_verified_success_archives(self):
        journal = Journal(self.root / 'journal.db', 'a')
        self.addCleanup(journal.db.close)
        journal.put(scan(self.root)[0], 'submitted', 'url')
        class Site:
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def verify(inner, chapter, url): return 'published'
        self.run_cycle(Site(), journal)
        self.assertFalse(self.path.exists())
        self.assertEqual(journal.get(1)['phase'], 'published')

    def test_quota_retries_same_url_next_day_only(self):
        journal = Journal(self.root / 'journal.db', 'a')
        self.addCleanup(journal.db.close)
        class Site:
            creates = 0
            submits = 0
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def duplicate_check(inner, chapter): pass
            async def create(inner):
                inner.creates += 1
                return 'original-url'
            async def fill(inner, chapter): pass
            async def resume_deferred(inner, chapter, url):
                self.assertEqual(url, 'original-url')
                return True
            async def submit(inner):
                inner.submits += 1
                if inner.submits == 1: raise DailyQuota('quota')
            async def verify(inner, chapter, url): return 'published'
        site = Site()
        with self.assertRaises(DailyQuota): self.run_cycle(site, journal)
        self.assertEqual(journal.get(1)['phase'], 'quota_deferred')
        self.run_cycle(site, journal)
        self.assertEqual(site.submits, 1)
        journal.db.execute('UPDATE chapters SET updated=updated-86400')
        journal.db.commit()
        self.run_cycle(site, journal)
        self.assertEqual((site.creates, site.submits), (1, 2))
        self.assertEqual(journal.get(1)['phase'], 'published')

    def test_previously_published_file_is_skipped_without_commit_check(self):
        journal = Journal(self.root / 'journal.db', 'a')
        self.addCleanup(journal.db.close)
        journal.put(scan(self.root)[0], 'published', 'url')
        class Site:
            async def __aenter__(inner): return inner
            async def __aexit__(inner, *args): pass
            async def login(inner): pass
            async def create(inner): raise AssertionError('Must not create again')
        self.run_cycle(Site(), journal)
        self.assertEqual(journal.get(1)['phase'], 'published')


if __name__ == '__main__':
    unittest.main()
