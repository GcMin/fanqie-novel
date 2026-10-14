"""Repository layouts; editorial acceptance and platform publication stay separate."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from .content import Blocked, Chapter, archive, check_plan, scan, validate_title


def blob_hash(raw: bytes):
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def safe_path(root: Path, relative: str):
    path = root / relative
    if Path(relative).is_absolute() or '..' in Path(relative).parts or not path.resolve().is_relative_to(root.resolve()):
        raise Blocked('发布证据路径越界')
    if any(p.is_symlink() for p in (path, *path.parents) if p != root and p.is_relative_to(root)):
        raise Blocked('发布证据/状态路径不能为符号链接')
    return path


def read_json(root, name, evidence=None):
    try:
        raw = safe_path(root, name).read_bytes()
        value = json.loads(raw)
    except (OSError, ValueError) as error:
        raise Blocked(f'缺少或无效的接纳/发布记录: {name}') from error
    if not isinstance(value, dict):
        raise Blocked(f'接纳/发布记录必须是对象: {name}')
    if evidence is not None:
        evidence[name] = raw
    return value


def chinese_number(value):
    if value.isdecimal():
        return int(value)
    digits = dict(zip('零〇一二两三四五六七八九', (0, 0, 1, 2, 2, 3, 4, 5, 6, 7, 8, 9)))
    total = section = digit = 0
    for char in value:
        if char in digits:
            digit = digits[char]
        elif char in '十百千':
            section += (digit or 1) * {'十': 10, '百': 100, '千': 1000}[char]
            digit = 0
        elif char == '万':
            total += (section + digit) * 10000
            section = digit = 0
        else:
            raise Blocked('无法解析正文标题中的章节号')
    return total + section + digit


class ReadyAdapter:
    def scan(self, root): return scan(root)
    def check(self, root, chapter): return check_plan(root, chapter)
    def archive(self, root, chapter, url): return archive(root, chapter)
    def commit(self, repo, chapter): return repo.commit_archive(chapter.path.name, chapter.number)


class AcceptedReviewsAdapter:
    def __init__(self, book_id=''):
        self.book_id = book_id

    def parse(self, root, chapter_id):
        name = f'chapters/{chapter_id}.md'
        evidence = {}
        try:
            raw = safe_path(root, name).read_bytes()
        except OSError as error:
            raise Blocked(f'缺少接纳正文: {name}') from error
        evidence[name] = raw
        sha = blob_hash(raw)
        prefix = f'reviews/{chapter_id}'
        acceptance = read_json(root, f'{prefix}/acceptance.json', evidence)
        prose = acceptance.get('prose', {})
        if (acceptance.get('status') != 'COMMITTED' or acceptance.get('chapter_id') != chapter_id
                or acceptance.get('accepted_draft_hash') != sha
                or not isinstance(prose, dict) or prose.get('path') != name or prose.get('sha') != sha
                or acceptance.get('idempotency_key') != f'{chapter_id}+{sha}'):
            raise Blocked(f'第 {chapter_id} 章接纳记录与正文版本不一致')
        if not all(isinstance(acceptance.get(k), str) and acceptance[k] for k in ('run_id', 'revision', 'contract_hash')):
            raise Blocked('接纳记录缺少运行/版本/契约标识')
        review_shas = {}
        refs = acceptance.get('reviews', {})
        if not isinstance(refs, dict):
            raise Blocked('双审引用格式错误')
        for role in ('continuity', 'reader_editor'):
            path = f'{prefix}/{role}/review.json'
            ref = refs.get(role, {})
            if not isinstance(ref, dict) or ref.get('path') != path or ref.get('verdict') != 'PASS':
                raise Blocked(f'第 {chapter_id} 章缺少 {role} PASS 凭据')
            review = read_json(root, path, evidence)
            review_shas[role] = blob_hash(evidence[path])
            if (ref.get('sha') != review_shas[role] or review.get('verdict') != 'PASS'
                    or review.get('draft_hash') != sha or review.get('role_id') != role
                    or review.get('chapter_id') != chapter_id
                    or any(review.get(k) != acceptance[k] for k in ('run_id', 'revision', 'contract_hash'))
                    or review.get('blocking_issue_count', 0) != 0
                    or review.get('must_fix_issues', [])
                    or not isinstance(review.get('issues', []), list)
                    or any(not isinstance(i, dict) or i.get('blocking') is not False or i.get('severity') in {'critical', 'major'} for i in review.get('issues', []))):
                raise Blocked(f'第 {chapter_id} 章 {role} 审核哈希/版本/门槛不一致')
        decision_path = f'{prefix}/showrunner/decision.json'
        if acceptance.get('decision') != decision_path:
            raise Blocked('接纳记录缺少对应总编裁决')
        decision = read_json(root, decision_path, evidence)
        if (decision.get('decision') not in {'ACCEPT', 'ACCEPT_UNCHANGED'}
                or decision.get('draft_hash') != sha or decision.get('chapter_id') != chapter_id
                or any(decision.get(k) != acceptance[k] for k in ('run_id', 'revision', 'contract_hash'))
                or decision.get('blocking_critical') != 0 or decision.get('blocking_major') != 0
                or decision.get('revision_required') is not False):
            raise Blocked('总编接纳裁决与双审/正文不一致')
        results = decision.get('review_results', [])
        if not isinstance(results, list) or len(results) != 2 or not all(isinstance(r, dict) for r in results) or any(sum(r.get('role') == role and r.get('verdict') == 'PASS' and r.get('review_sha') == sha for r in results) != 1 for role, sha in review_shas.items()):
            raise Blocked('总编裁决未引用当前双审哈希')
        text = raw.decode('utf-8-sig')
        heading = re.match(r'\A# 第([^\s章]+)章[ \t]+([^\r\n]+)\r?\n(.*)\Z', text, re.S)
        if not heading or int(chapter_id) < 1 or chinese_number(heading[1]) != int(chapter_id):
            raise Blocked('正文标题章节号与文件名不一致')
        title, body = heading[2].strip(), heading[3].strip()
        if re.search(r'[<>]|第\s*\d+\s*章', title):
            raise Blocked('正文标题包含内部章号或 HTML')
        body = re.sub(r'<!--.*?-->', '', body, flags=re.S).strip()
        body = re.sub(r'\*\*([^*\n]+)\*\*', r'\1', body)
        # Reuse the ready parser's body guard without inventing editorial QA.
        from .content import validate_body
        validate_body(body, name)
        if '`' in body or '**' in body or re.search(r'(?m)^\s*(?:[-*+]\s|>\s|\|)|<[^>]+>|(?:reviews|work|workflow|research|outlines)/|(?<!\w)[*_][^\n]+?[*_](?!\w)', body):
            raise Blocked('接纳正文含未支持的 Markdown/HTML，请先明确纯文本转换规则')
        digest = hashlib.sha256(json.dumps({k: hashlib.sha256(v).hexdigest() for k, v in evidence.items()}, sort_keys=True).encode()).hexdigest()
        chapter = Chapter(root / name, int(chapter_id), title, body, text, digest)
        validate_title(chapter)
        if any(safe_path(root, k).read_bytes() != v for k, v in evidence.items()):
            raise Blocked('接纳证据在校验期间发生变化')
        return chapter

    def record_path(self, chapter):
        return f'publication/fanqie/{chapter.path.stem}.json'

    def scan(self, root):
        safe_path(root, 'chapters')
        chapters, seen = [], set()
        for path in sorted((root / 'chapters').glob('*.md')):
            if not re.fullmatch(r'\d{6,}', path.stem):
                continue
            acceptance_path = f'reviews/{path.stem}/acceptance.json'
            if not safe_path(root, acceptance_path).exists():
                continue
            if read_json(root, acceptance_path).get('status') != 'COMMITTED':
                continue
            chapter = self.parse(root, path.stem)
            if chapter.number in seen:
                raise Blocked('接纳目录存在重复章节号')
            seen.add(chapter.number)
            if safe_path(root, self.record_path(chapter)).exists():
                record = read_json(root, self.record_path(chapter))
                if (record.get('status') != 'published' or record.get('source_digest') != chapter.digest
                        or record.get('chapter') != chapter.number or record.get('title') != chapter.title
                        or record.get('source_path') != str(chapter.path.relative_to(root)).replace('\\', '/')
                        or (self.book_id and record.get('book_id') != self.book_id)
                        or record.get('accepted_draft_hash') != blob_hash(chapter.path.read_bytes())
                        or record.get('body_sha256') != hashlib.sha256(chapter.body.encode()).hexdigest()
                        or not isinstance(record.get('book_id'), str) or not re.fullmatch(r'\d+', record['book_id'])
                        or not re.match(rf"https://fanqienovel\.com/main/writer/{record['book_id']}/publish/\d+(?:[/?]|$)", record.get('url', ''))
                        or not record.get('verified_at')):
                    raise Blocked('已发布状态与接纳正文/作品不一致，禁止重发或覆盖')
                continue
            chapters.append(chapter)
        if len({c.number for c in chapters}) != len(chapters):
            raise Blocked('接纳目录存在重复章节号')
        return sorted(chapters, key=lambda c: c.number)

    def check(self, root, chapter):
        if self.parse(root, chapter.path.stem) != chapter:
            raise Blocked('接纳正文/审核记录在发布期间发生变化')

    def archive(self, root, chapter, url):
        self.check(root, chapter)
        if not re.fullmatch(r'\d+', self.book_id) or not re.match(rf'https://fanqienovel\.com/main/writer/{self.book_id}/publish/\d+(?:[/?]|$)', url):
            raise Blocked('独立发布记录缺少正确作品 ID 或远端章节 URL')
        path = safe_path(root, self.record_path(chapter))
        record = {'schema_version': 1, 'status': 'published', 'book_id': self.book_id,
                  'chapter': chapter.number, 'title': chapter.title,
                  'source_path': chapter.path.relative_to(root).as_posix(), 'source_digest': chapter.digest,
                  'accepted_draft_hash': blob_hash(chapter.path.read_bytes()),
                  'body_sha256': hashlib.sha256(chapter.body.encode()).hexdigest(), 'url': url,
                  'verified_at': datetime.now(timezone.utc).isoformat()}
        if path.exists():
            old = read_json(root, self.record_path(chapter))
            if any(old.get(k) != v for k, v in record.items() if k != 'verified_at'):
                raise Blocked('独立发布状态已存在且冲突')
            return
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = safe_path(root, self.record_path(chapter) + '.tmp')
        temporary.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
        temporary.replace(path)

    def commit(self, repo, chapter):
        repo.git('add', '--', self.record_path(chapter))
        repo.git('commit', '-m', f'chore: record verified Fanqie chapter {chapter.number}')
        repo.git('push', 'origin', f'HEAD:refs/heads/{repo.branch}')


def get_adapter(source_format='ready', book_id=''):
    if source_format == 'ready': return ReadyAdapter()
    if source_format == 'accepted_reviews': return AcceptedReviewsAdapter(book_id)
    raise Blocked('不支持的 source_format')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='只读仓库格式/接纳证据校验，不创建发布记录或访问番茄')
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--source-format', choices=('ready', 'accepted_reviews'), required=True)
    args = parser.parse_args()
    try:
        adapter = get_adapter(args.source_format)
        root = args.repo.resolve(strict=True)
        chapters = adapter.scan(root)
        for chapter in chapters: adapter.check(root, chapter)
        print(json.dumps({'ok': True, 'count': len(chapters), 'chapters': [{'chapter': c.number, 'title': c.title} for c in chapters]}, ensure_ascii=False))
    except (Blocked, OSError, ValueError, TypeError) as error:
        print(json.dumps({'ok': False, 'error': str(error)}, ensure_ascii=False))
        raise SystemExit(1)
