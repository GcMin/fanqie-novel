"""Validated profiles and isolated worker processes for multiple books."""
from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
import signal
import sqlite3
import subprocess
import sys
import tempfile
import time
from contextlib import closing
from pathlib import Path

import yaml
from filelock import FileLock

from .content import Blocked

LOG = logging.getLogger('publisher.manager')


def load_profiles(path: Path):
    document = yaml.safe_load(path.read_text(encoding='utf-8-sig'))
    if not isinstance(document, dict) or not isinstance(document.get('novels'), list):
        raise Blocked('多小说配置必须包含 novels 列表')
    profiles, ids, books, repos = [], set(), set(), set()
    for item in document['novels']:
        if not isinstance(item, dict):
            raise Blocked('小说配置必须是对象')
        profile = dict(item)
        for field in ('id', 'repository', 'book_id', 'book_title'):
            if not isinstance(profile.get(field), str) or not profile[field].strip():
                raise Blocked(f'小说配置缺少字符串字段 {field}（book_id 必须加引号）')
        if not re.fullmatch(r'[a-z][a-z0-9-]{0,63}', profile['id']):
            raise Blocked('小说 id 只允许小写字母开头的字母、数字、连字符')
        if not re.fullmatch(r'[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+', profile['repository']):
            raise Blocked('repository 必须为 owner/repo')
        if not re.fullmatch(r'\d+', profile['book_id']):
            raise Blocked('book_id 必须为数字字符串')
        profile.setdefault('branch', 'main')
        if not isinstance(profile['branch'], str) or not re.fullmatch(r'[A-Za-z0-9_][A-Za-z0-9_./-]*', profile['branch']) or '..' in profile['branch']:
            raise Blocked('非法 Git 分支')
        for field, default, minimum in (('daily_upload_char_limit', 7000, 1), ('publish_interval_seconds', 7200, 30), ('heartbeat_interval_seconds', 300, 30)):
            profile.setdefault(field, default)
            if type(profile[field]) is not int or profile[field] < minimum:
                raise Blocked(f'{field} 必须为至少 {minimum} 的整数')
        for field, default in (('enabled', True), ('publish_enabled', False), ('reuse_login', False), ('migrate_legacy', False)):
            profile.setdefault(field, default)
            if type(profile[field]) is not bool:
                raise Blocked(f'{field} 必须为布尔值')
        if profile['id'] in ids or profile['book_id'] in books:
            raise Blocked('小说 id 或番茄作品 ID 重复')
        ids.add(profile['id']); books.add(profile['book_id'])
        if profile['enabled']:
            key = (profile['repository'], profile['branch'])
            if key in repos:
                raise Blocked('多个启用作品不能归档同一个仓库/分支')
            repos.add(key)
            profiles.append(profile)
    if not profiles:
        raise Blocked('没有启用的小说配置')
    return profiles


def scope(profile):
    return f"{profile['repository']}:{profile['branch']}:{profile['book_id']}"


def prepare_data(profile, root: Path):
    parent = root / 'novels'
    parent.mkdir(parents=True, exist_ok=True)
    target = parent / profile['id']
    if target.is_symlink() or parent.is_symlink():
        raise Blocked('小说数据目录不得为符号链接')
    if target.exists():
        return target
    staging = Path(tempfile.mkdtemp(prefix=f".{profile['id']}-", dir=parent))
    legacy = root / 'journal.sqlite3'
    if profile['migrate_legacy']:
        if not legacy.exists():
            raise Blocked('找不到需要迁移的旧发布记录')
        with FileLock(str(root / 'publisher.lock'), timeout=0):
            with closing(sqlite3.connect(legacy)) as original:
                existing = original.execute('SELECT value FROM scope').fetchone()
                if not existing or existing[0] != scope(profile):
                    raise Blocked('旧发布数据与小说配置不匹配，禁止迁移')
                with closing(sqlite3.connect(staging / 'journal.sqlite3')) as copied:
                    original.backup(copied)
            if (root / 'repo').exists():
                shutil.copytree(root / 'repo', staging / 'repo')
            for name in ('storage-state.json', 'schedule.json', 'heartbeat.json', 'last-status.json'):
                if (root / name).exists():
                    shutil.copy2(root / name, staging / name)
            (staging / 'migration.json').write_text(json.dumps({'source': str(root), 'scope': scope(profile), 'time': time.time()}))
    elif profile['reuse_login'] and (root / 'storage-state.json').exists():
        shutil.copy2(root / 'storage-state.json', staging / 'storage-state.json')
    staging.rename(target)
    LOG.info('[%s] 独立数据目录已初始化%s', profile['id'], '，旧数据库/每日计数/进度已复制保留' if profile['migrate_legacy'] else '')
    return target


def worker_env(profile, root):
    return {**os.environ, 'NOVEL_WORKER': '1', 'NOVEL_ID': profile['id'],
            'DATA_DIR': str(root / 'novels' / profile['id']),
            'GITHUB_REPOSITORY': profile['repository'], 'GITHUB_BRANCH': profile['branch'],
            'FANQIE_BOOK_ID': profile['book_id'], 'FANQIE_BOOK_TITLE': profile['book_title'],
            'PUBLISH_ENABLED': str(profile['publish_enabled']).lower(),
            'DAILY_UPLOAD_CHAR_LIMIT': str(profile['daily_upload_char_limit']),
            'PUBLISH_INTERVAL_SECONDS': str(profile['publish_interval_seconds']),
            'HEARTBEAT_INTERVAL_SECONDS': str(profile['heartbeat_interval_seconds'])}


def run_manager(argv=None):
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--novel')
    selected, forwarded = parser.parse_known_args(argv)
    if not forwarded:
        forwarded = ['watch']
    profiles = load_profiles(Path(os.environ['NOVELS_CONFIG_PATH']))
    if selected.novel:
        profiles = [p for p in profiles if p['id'] == selected.novel]
        if not profiles:
            raise Blocked('指定小说不存在或未启用')
    command = next((a for a in forwarded if not a.startswith('-')), 'watch')
    if '--help' in forwarded or '-h' in forwarded:
        command = 'help'
    if command in {'login', 'login-sms', 'import-cookies', 'reconcile'} and len(profiles) != 1:
        raise Blocked('登录或核验指定章节时必须使用 --novel ID')
    root = Path(os.getenv('DATA_DIR', '/data')).resolve()
    root.mkdir(parents=True, exist_ok=True)
    with FileLock(str(root / 'manager.lock'), timeout=0):
        for p in profiles:
            prepare_data(p, root)
        if command != 'watch':
            failed = False
            for p in profiles:
                print(f"[{p['id']}] {command}", flush=True)
                result = subprocess.run([sys.executable, '-m', 'publisher', *forwarded], env=worker_env(p, root))
                failed |= result.returncode != 0
            return int(failed)
        children = {}
        stopping = False
        def stop(*_):
            nonlocal stopping
            stopping = True
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, stop)
        try:
            while not stopping:
                for p in profiles:
                    child, restart_at = children.get(p['id'], (None, 0))
                    if child is not None and child.poll() is not None:
                        LOG.error('[%s] worker 退出，将于 30 秒后重启', p['id'])
                        children[p['id']] = (None, time.monotonic() + 30)
                    elif child is None and time.monotonic() >= restart_at:
                        children[p['id']] = (subprocess.Popen([sys.executable, '-m', 'publisher', *forwarded], env=worker_env(p, root)), 0)
                time.sleep(1)
        finally:
            active = [child for child, _ in children.values() if child is not None and child.poll() is None]
            for child in active:
                child.terminate()
            for child in active:
                try:
                    child.wait(timeout=20)
                except subprocess.TimeoutExpired:
                    child.kill(); child.wait()
    return 0
