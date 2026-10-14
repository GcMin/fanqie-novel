import os
import sqlite3
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from publisher.content import Blocked
from publisher.__main__ import Journal
from publisher.novels import load_profiles, prepare_data, run_manager, scope, worker_env


class NovelsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / 'novels.yaml'
        self.items = [dict(id='first', repository='owner/first', book_id='123', book_title='第一部'),
                      dict(id='second', repository='owner/second', book_id='456', book_title='第二部')]

    def profiles(self):
        self.path.write_text(yaml.safe_dump({'novels': self.items}), encoding='utf-8')
        return load_profiles(self.path)

    def test_worker_environment_and_same_chapter_numbers_are_isolated(self):
        profiles = self.profiles()
        first, second = [prepare_data(p, self.root) for p in profiles]
        j1, j2 = [Journal(d / 'journal.sqlite3', scope(p)) for p, d in zip(profiles, (first, second))]
        self.addCleanup(j1.db.close); self.addCleanup(j2.db.close)
        chapter = SimpleNamespace(number=1, digest='source', body='文' * 7001)
        j1.put(chapter, 'submitted', 'url-first'); j1.reserve_upload(chapter)
        self.assertEqual(j1.daily_chars(), 7001)
        self.assertEqual(j2.daily_chars(), 0)
        self.assertIsNone(j2.get(1))
        e1, e2 = [worker_env(p, self.root) for p in profiles]
        self.assertNotEqual(e1['DATA_DIR'], e2['DATA_DIR'])
        self.assertNotEqual(e1['GITHUB_REPOSITORY'], e2['GITHUB_REPOSITORY'])
        self.assertEqual(e2['DAILY_UPLOAD_CHAR_LIMIT'], '7000')

    def test_invalid_ids_books_and_duplicate_targets_rejected(self):
        for field, value in [('id', '../outside'), ('book_id', 123), ('repository', 'bad'), ('daily_upload_char_limit', 0), ('enabled', 'true')]:
            original = dict(self.items[0])
            self.items[0][field] = value
            with self.assertRaises(Blocked): self.profiles()
            self.items[0] = original
        for field in ('id', 'book_id', 'repository'):
            original = dict(self.items[1])
            self.items[1][field] = self.items[0][field]
            with self.assertRaises(Blocked): self.profiles()
            self.items[1] = original

    def test_legacy_migration_keeps_daily_usage_and_is_idempotent(self):
        self.items = self.items[:1]
        self.items[0]['migrate_legacy'] = True
        profile = self.profiles()[0]
        original = Journal(self.root / 'journal.sqlite3', scope(profile))
        self.addCleanup(original.db.close)
        chapter = SimpleNamespace(number=124, digest='unchanged', body='文' * 7100)
        original.put(chapter, 'submitted', 'original-url'); original.reserve_upload(chapter)
        (self.root / 'repo').mkdir(); (self.root / 'repo' / 'progress').write_text('keep')
        (self.root / 'storage-state.json').write_text('{}')
        destination = prepare_data(profile, self.root)
        migrated = Journal(destination / 'journal.sqlite3', scope(profile))
        self.addCleanup(migrated.db.close)
        self.assertEqual(migrated.get(124)['url'], 'original-url')
        self.assertEqual(migrated.daily_chars(), 7100)
        self.assertEqual((destination / 'repo' / 'progress').read_text(), 'keep')
        self.assertTrue((self.root / 'journal.sqlite3').exists())
        self.assertEqual(prepare_data(profile, self.root), destination)

    def test_migration_refuses_other_book(self):
        self.items[0]['migrate_legacy'] = True
        profile = self.profiles()[0]
        original = Journal(self.root / 'journal.sqlite3', 'other:main:999')
        self.addCleanup(original.db.close)
        with self.assertRaises(Blocked): prepare_data(profile, self.root)
        self.assertFalse((self.root / 'novels' / 'first').exists())

    def test_failure_of_one_command_does_not_skip_next_novel(self):
        self.profiles()
        with patch.dict(os.environ, {'NOVELS_CONFIG_PATH': str(self.path), 'DATA_DIR': str(self.root)}), patch('publisher.novels.subprocess.run') as run:
            run.side_effect = [SimpleNamespace(returncode=1), SimpleNamespace(returncode=0)]
            self.assertEqual(run_manager(['check']), 1)
            self.assertEqual(run.call_count, 2)
            self.assertNotEqual(run.call_args_list[0].kwargs['env']['DATA_DIR'], run.call_args_list[1].kwargs['env']['DATA_DIR'])

    def test_interactive_commands_require_selection(self):
        self.profiles()
        with patch.dict(os.environ, {'NOVELS_CONFIG_PATH': str(self.path), 'DATA_DIR': str(self.root)}), patch('publisher.novels.subprocess.run', return_value=SimpleNamespace(returncode=0)) as run:
            with self.assertRaises(Blocked): run_manager(['login-sms'])
            self.assertEqual(run_manager(['status', '--novel', 'second']), 0)
            self.assertEqual(run.call_args.kwargs['env']['NOVEL_ID'], 'second')
