from __future__ import annotations

import argparse
import asyncio
import getpass
import json
import logging
import os
import sqlite3
import time
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

import yaml
from filelock import FileLock

from .browser import Fanqie
from .content import Blocked, DailyQuota, archive, scan, validate_title
from .repository import Repository
from .session import heartbeat, heartbeat_status, parse_cookies
from .schedule import Schedule

LOG = logging.getLogger("publisher")


class Journal:
    def __init__(self, path: Path, scope: str):
        self.db = sqlite3.connect(path)
        self.db.execute("PRAGMA synchronous=FULL")
        self.db.execute("CREATE TABLE IF NOT EXISTS scope (value TEXT NOT NULL)")
        existing = self.db.execute("SELECT value FROM scope").fetchone()
        if existing and existing[0] != scope:
            self.db.close()
            raise Blocked("数据卷绑定的是另一仓库/分支/作品，需使用独立数据卷")
        if not existing:
            self.db.execute("INSERT INTO scope VALUES (?)", (scope,))
        self.db.execute("CREATE TABLE IF NOT EXISTS chapters (number INTEGER PRIMARY KEY, digest TEXT NOT NULL, phase TEXT NOT NULL, url TEXT, updated REAL NOT NULL)")
        self.db.commit()

    def get(self, number):
        row = self.db.execute("SELECT digest, phase, url, updated FROM chapters WHERE number=?", (number,)).fetchone()
        return dict(zip(("digest", "phase", "url", "updated"), row)) if row else None

    def put(self, chapter, phase, url=None):
        previous = self.get(chapter.number)
        if previous and previous["digest"] != chapter.digest:
            raise Blocked("事务中的正文已改变，需人工处理")
        self.db.execute("INSERT OR REPLACE INTO chapters VALUES (?, ?, ?, ?, ?)",
                        (chapter.number, chapter.digest, phase, url or (previous or {}).get("url"), time.time()))
        self.db.commit()

    def rows(self):
        return self.db.execute("SELECT number, phase, url FROM chapters ORDER BY number").fetchall()


async def cycle(args, data, repo, journal, browser_factory):
    repo.sync()
    chapters = scan(repo.root)
    if args.command == "check":
        LOG.info("本地校验通过：%s 个 ready 章节；未打开编辑器", len(chapters))
        for chapter in chapters:
            LOG.info("第 %s 章，正文 %s 字符", chapter.number, len(chapter.body))
        return
    numbers = {c.number for c in chapters}
    for number, phase, _ in journal.rows():
        if phase not in {"published", "archiving"} and number not in numbers:
            raise Blocked(f"第 {number} 章存在未结束事务，但 ready 文件消失")
        if phase == "archiving":
            # Successful commit/push followed by crash is safe but needs an explicit audit.
            raise Blocked(f"第 {number} 章归档曾中断；核对 published 快照/CSV/GitHub 后修复事务，不重发")
    if not chapters:
        LOG.info("没有待发布章节")
        return
    if args.command == "watch" and os.getenv("PUBLISH_ENABLED", "false").lower() != "true":
        LOG.info("发现 %s 章；PUBLISH_ENABLED=false，仅检查", len(chapters))
        return
    if args.command == "run" and os.getenv("PUBLISH_ENABLED", "false").lower() != "true":
        raise Blocked("请在 .env 设置 PUBLISH_ENABLED=true 才能发布")
    async with browser_factory() as site:
        await site.login()
        count = 0
        for chapter in chapters:
            record = journal.get(chapter.number)
            if record and record["digest"] != chapter.digest:
                raise Blocked(f"第 {chapter.number} 章发布事务正文发生变化，禁止继续")
            if args.command == "reconcile":
                if chapter.number != args.chapter:
                    continue
                if not record:
                    raise Blocked("只能核验已有事务")
                if args.url:
                    site.assert_url(args.url)
                    journal.put(chapter, "submitted", args.url)
                    record = journal.get(chapter.number)
            if record and record["phase"] == "published":
                LOG.info("第 %s 章内容与成功发布记录一致，跳过", chapter.number)
                continue
            deferred = record and record['phase'] == 'quota_deferred' and args.command != 'reconcile'
            if deferred:
                zone = ZoneInfo('Asia/Shanghai')
                if datetime.fromtimestamp(record['updated'], zone).date() >= datetime.now(zone).date():
                    LOG.info('第 %s 章达到每日字数上限，次日再恢复原章节', chapter.number)
                    return
            if record and record["phase"] in {"preparing", "editing"}:
                raise Blocked(f"第 {chapter.number} 章创建/填写曾中断；核对后台后使用 reconcile --chapter N --url URL；不会自动重试提交")
            if not record:
                if args.command == "reconcile":
                    raise Blocked("reconcile 不能创建章节")
                validate_title(chapter)
                await site.duplicate_check(chapter)
                journal.put(chapter, "preparing")
                url = await site.create()
                journal.put(chapter, "editing", url)
                await site.fill(chapter)
                # Persist BEFORE the first potentially consequential click.
                journal.put(chapter, "submitted", url)
                try:
                    await site.submit()
                except DailyQuota:
                    journal.put(chapter, 'quota_deferred', url)
                    raise
            else:
                url = record["url"]
                if deferred and await site.resume_deferred(chapter, url):
                    journal.put(chapter, 'submitted', url)
                    try:
                        await site.submit()
                    except DailyQuota:
                        journal.put(chapter, 'quota_deferred', url)
                        raise
            if not url:
                raise Blocked("缺少远端章节 URL，请人工核对")
            state = await site.verify(chapter, url)
            if state == "pending":
                LOG.info("第 %s 章审核中，保留 ready；下轮只核验，不重发", chapter.number)
                return
            journal.put(chapter, "archiving", url)
            archive(repo.root, chapter)
            repo.commit_archive(chapter.path.name, chapter.number)
            journal.put(chapter, "published", url)
            LOG.info("第 %s 章已发布、核验并回写 GitHub", chapter.number)
            count += 1
            limit = int(os.getenv("MAX_CHAPTERS_PER_RUN", "0"))
            if args.command == "reconcile" or (limit > 0 and count >= limit):
                return
        if args.command == "reconcile":
            raise Blocked("未找到指定 ready 章节")


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    parser = argparse.ArgumentParser(description="番茄无头发布器")
    parser.add_argument("command", choices=["login", "login-sms", "import-cookies", "heartbeat", "check", "run", "watch", "status", "reconcile"])
    parser.add_argument("--chapter", type=int)
    parser.add_argument("--url")
    args = parser.parse_args()
    if args.command == "reconcile" and not args.chapter:
        parser.error("reconcile 必须指定 --chapter")
    os.umask(0o077)
    data = Path(os.getenv("DATA_DIR", "runtime")).resolve()
    data.mkdir(parents=True, exist_ok=True)
    config = yaml.safe_load(Path(os.getenv("CONFIG_PATH", "config/publisher.yaml")).read_text(encoding="utf-8"))
    slug, branch = os.getenv("GITHUB_REPOSITORY", "GcMin/fanqie-novel"), os.getenv("GITHUB_BRANCH", "main")
    book, title = os.getenv("FANQIE_BOOK_ID", ""), os.getenv("FANQIE_BOOK_TITLE", "")
    def factory():
        return Fanqie(data, book, title, config)
    with FileLock(str(data / "publisher.lock"), timeout=0):
        journal = Journal(data / "journal.sqlite3", f"{slug}:{branch}:{book}")
        if args.command == "status":
            print(json.dumps(journal.rows(), ensure_ascii=False, indent=2))
            return
        if args.command in {"login", "login-sms", "import-cookies", "heartbeat"}:
            async def authenticate():
                async with factory() as site:
                    if args.command == "import-cookies":
                        raw = await asyncio.to_thread(getpass.getpass, "粘贴 Cookie 请求头（隐藏输入，不写日志）: ")
                        cookies = parse_cookies(raw)
                        await site.context.clear_cookies()
                        await site.context.add_cookies(cookies)
                        await site.login()
                    elif args.command == "heartbeat":
                        await site.login()
                    elif args.command == "login-sms":
                        await site.login_sms()
                    else:
                        LOG.info("正在等待扫码；截图持续更新至 /data/login.png，认证最长 %s 秒", config["login_timeout_seconds"])
                        await site.login(interactive=True)
                    LOG.info("登录态已保存，后续任务自动复用")
            try:
                asyncio.run(authenticate())
                heartbeat_status(data, True)
            except Exception as error:
                heartbeat_status(data, False)
                LOG.error("%s", str(error) if isinstance(error, Blocked) else
                          f"{type(error).__name__}；登录失败，请查看 last-error.png")
                raise SystemExit(1) from None
            return
        repo = Repository(data / "repo", slug, branch)
        schedule = Schedule(data, int(os.getenv('PUBLISH_INTERVAL_SECONDS', '7200')))
        heartbeat_interval = max(30, int(os.getenv('HEARTBEAT_INTERVAL_SECONDS', '300')))
        next_heartbeat = 0
        if args.command == 'watch':
            LOG.info('定时发布每 %s 秒；心跳每 %s 秒；按 ready 文件与发布记录增量处理', schedule.interval, heartbeat_interval)
        while True:
            if args.command == 'watch':
                if time.time() >= next_heartbeat:
                    try:
                        asyncio.run(heartbeat(data, factory))
                        LOG.info('Heartbeat：登录态有效，已保存服务器更新的 Cookie')
                    except Exception as error:
                        LOG.error('Heartbeat 失败：%s', str(error) if isinstance(error, Blocked) else type(error).__name__)
                    next_heartbeat = time.time() + heartbeat_interval
                if not schedule.due(time.time()):
                    time.sleep(max(0.1, min(30, next_heartbeat-time.time(), schedule.next_at-time.time())))
                    continue
                # Record before doing any work: restart/failure never causes rapid duplicate runs.
                schedule.started(time.time())
                LOG.info('开始本轮目录增量扫描；下轮时间 %s', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(schedule.next_at)))
            try:
                asyncio.run(cycle(args, data, repo, journal, factory))
                (data / "last-status.json").write_text(json.dumps({"ok": True, "time": time.time()}))
            except Exception as error:
                # Playwright exceptions can include form data: do not log raw exceptions.
                message = str(error) if isinstance(error, Blocked) else f"{type(error).__name__}，请查看 last-error.png；未确认成功"
                LOG.error("%s", message)
                (data / "last-status.json").write_text(json.dumps({"ok": False, "time": time.time(), "error": message}, ensure_ascii=False))
                if args.command != "watch":
                    raise SystemExit(1) from None
            if args.command != "watch":
                return


if __name__ == "__main__":
    main()
