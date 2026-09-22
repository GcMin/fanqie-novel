from __future__ import annotations

import csv
import hashlib
import io
import re
from dataclasses import dataclass
from pathlib import Path

import yaml


class Blocked(RuntimeError):
    pass


class DailyQuota(Blocked):
    """An explicit platform rejection; unlike a timeout, safe to defer."""


@dataclass(frozen=True)
class Chapter:
    path: Path
    number: int
    title: str
    body: str
    source: str
    digest: str


def normalized(text: str) -> str:
    return re.sub(r"\s+", "", text)


def parse(path: Path, repo: Path) -> Chapter:
    if path.is_symlink() or path.resolve().parent != (repo / "chapters/ready").resolve():
        raise Blocked(f"非法发布路径: {path.name}")
    raw = path.read_text(encoding="utf-8-sig")
    match = re.match(r"\A---\r?\n(.*?)\r?\n---\r?\n(.*)\Z", raw, re.S)
    if not match:
        raise Blocked(f"缺少 Frontmatter: {path.name}")
    meta = yaml.safe_load(match[1])
    if not isinstance(meta, dict) or meta.get("status") != "ready" or meta.get("qa") != "pass":
        raise Blocked(f"未通过 ready/QA 门槛: {path.name}")
    if not re.search(r"(?m)^status: ready$", match[1]):
        raise Blocked("归档要求使用标准格式 status: ready")
    number, title = meta.get("chapter"), meta.get("title")
    if type(number) is not int or number < 1 or not isinstance(title, str) or not title.strip():
        raise Blocked("Frontmatter 必须含正整数 chapter 和非空 title")
    title = title.strip()
    if re.search(r"[\r\n<>]|第\s*\d+\s*章", title):
        raise Blocked("title 只写章名，不含第 N 章、换行或 HTML")
    body = re.sub(r"<!--.*?-->", "", match[2], flags=re.S).strip()
    lines = body.splitlines()
    if lines and lines[0].startswith("# "):
        heading = re.sub(r"^第\s*\d+\s*章\s*", "", lines.pop(0)[2:]).strip()
        if heading != title:
            raise Blocked("正文标题与 Frontmatter 不一致")
        body = "\n".join(lines).strip()
    # Unstructured internal notes cannot be safely distinguished from prose: reject.
    if not body or re.search(
        r"TODO|FIXME|<!--|-->|```|(?im:^\s*(?:#{1,6}\s|---\s*$|(?:status|qa|chapter):))"
        r"|(?im:^\s*(?:字数统计|字数|章节摘要|摘要|大纲|内部说明|Agent备注|QA备注|提示词)\s*[:：])"
        r"|作为(?:一个)?(?:AI|人工智能)|(?:memory|bible|qa|plans)/|\[[^\]]*\]\([^)]*\)", body
    ):
        raise Blocked(f"正文存在内部资料或非纯文本标记: {path.name}")
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return Chapter(path, number, title, body, raw, digest)


def validate_title(chapter: Chapter):
    if len(normalized(chapter.title)) < 5:
        raise Blocked(f'第 {chapter.number} 章标题至少需要 5 个非空白字符，请在上传前修改')


def plan_rows(repo: Path):
    path = repo / "plans/chapter_plan.csv"
    if path.is_symlink():
        raise Blocked("计划文件不能为符号链接")
    reader = csv.DictReader(io.StringIO(path.read_text(encoding="utf-8-sig")))
    rows = list(reader)
    if not reader.fieldnames or not {"chapter", "status", "qa_status", "publish_status"} <= set(reader.fieldnames):
        raise Blocked("章节计划缺少必要列")
    return path, reader.fieldnames, rows


def check_plan(repo: Path, chapter: Chapter):
    _, _, rows = plan_rows(repo)
    matches = [r for r in rows if r["chapter"] == str(chapter.number)]
    if len(matches) != 1 or matches[0]["status"] not in {"completed", "ready"} or matches[0]["qa_status"] != "pass":
        raise Blocked(f"第 {chapter.number} 章计划未完成/QA 未通过或重复")
    if matches[0].get("title") != chapter.title:
        raise Blocked("计划标题不一致")


def scan(repo: Path) -> list[Chapter]:
    ready = repo / "chapters/ready"
    if ready.is_symlink() or ready.resolve() != repo.resolve() / "chapters/ready":
        raise Blocked("ready 目录不得为符号链接")
    chapters = [parse(p, repo) for p in sorted(ready.glob("*.md")) if p.name.lower() != "readme.md"]
    numbers = [c.number for c in chapters]
    if len(set(numbers)) != len(numbers):
        raise Blocked("ready 中存在重复章节号")
    for chapter in chapters:
        check_plan(repo, chapter)
    return sorted(chapters, key=lambda c: c.number)


def archive(repo: Path, chapter: Chapter):
    check_plan(repo, chapter)
    destination = repo / "chapters/published" / chapter.path.name
    if destination.parent.is_symlink() or destination.parent.resolve() != repo.resolve() / "chapters/published":
        raise Blocked("published 目录不得为符号链接")
    published = re.sub(r"(?m)^status: ready\s*$", "status: published", chapter.source, count=1)
    if published == chapter.source:
        raise Blocked("status 必须使用标准格式 status: ready")
    if destination.exists() and destination.read_text(encoding="utf-8") != published:
        raise Blocked("已发布快照存在冲突")
    path, fields, rows = plan_rows(repo)
    for row in rows:
        if row["chapter"] == str(chapter.number):
            row["publish_status"] = "published"
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    writer.writerows(rows)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(published, encoding="utf-8", newline="\n")
    path.write_text(output.getvalue(), encoding="utf-8", newline="")
    chapter.path.unlink()
