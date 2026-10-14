"""Read-only validation of the supplied snapshot; no Git sync or publisher session."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import tempfile
from pathlib import Path

import yaml

from .content import Blocked, check_plan, normalized, plan_rows, scan, validate_title


def _file(root: Path, path: Path) -> bytes:
    if path.is_symlink() or not path.resolve().is_relative_to(root):
        raise Blocked(f"拒绝快照外路径或符号链接: {path}")
    return path.read_bytes()


def validate_snapshot(root: Path, candidate: Path | None = None) -> dict:
    root = root.resolve(strict=True)
    ready = root / "chapters/ready"
    if not ready.is_dir() or ready.is_symlink() or ready.resolve() != ready:
        raise Blocked("缺少真实 chapters/ready 目录")
    plan = root / "plans/chapter_plan.csv"
    files = {"plans/chapter_plan.csv": _file(root, plan)}
    for path in sorted(ready.glob("*.md")):
        if path.name.lower() != "readme.md":
            files[str(path.relative_to(root))] = _file(root, path)
    inputs = dict(files)
    proposed = None
    if candidate is not None:
        path = candidate if candidate.is_absolute() else root / candidate
        draft_dir = root / "chapters/draft"
        if draft_dir.is_symlink() or draft_dir.resolve() != draft_dir:
            raise Blocked("draft 目录不得为符号链接")
        if path.parent.resolve() != draft_dir or not re.fullmatch(r"\d{4,}\.md", path.name):
            raise Blocked("candidate 必须是本快照 chapters/draft/NNNN.md")
        raw_bytes = _file(root, path)
        raw = raw_bytes.decode("utf-8-sig")
        match = re.fullmatch(r"---\r?\n(.*?)\r?\n---\r?\n(.*)", raw, re.S)
        if not match:
            raise Blocked("candidate 缺少 Frontmatter")
        meta = yaml.safe_load(match[1])
        if not isinstance(meta, dict) or meta.get("status") != "draft" or meta.get("qa") != "pass":
            raise Blocked("candidate 必须已通过 QA；本命令不会生成或伪造 QA")
        if type(meta.get("chapter")) is not int or meta["chapter"] != int(path.stem):
            raise Blocked("candidate 文件名与章号不一致")
        if not re.search(r"(?m)^status: draft\r?$", match[1]):
            raise Blocked("candidate 需要标准 status: draft")
        proposed = f"chapters/ready/{path.name}"
        if proposed in files or (root / "chapters/published" / path.name).exists():
            raise Blocked("同号章节已在 ready/published；先核对，不覆盖")
        inputs[str(path.relative_to(root))] = raw_bytes
        # Change only delivery status in a disposable validation copy. Source stays untouched.
        header = re.sub(r"(?m)^status: draft\r?$", "status: ready", match[1], count=1)
        files[proposed] = ("---\n" + header + "\n---\n" + match[2]).encode("utf-8")
    with tempfile.TemporaryDirectory(prefix="novel-check-") as directory:
        snapshot = Path(directory)
        (snapshot / "chapters/ready").mkdir(parents=True)
        for name, data in files.items():
            destination = snapshot / name
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(data)
        _, _, rows = plan_rows(snapshot)
        chapters = scan(snapshot)
        for chapter in chapters:
            validate_title(chapter)
            check_plan(snapshot, chapter)
        result = {
            "ok": True,
            "scope": "structural_only_not_reader_or_continuity_approval",
            "ready_count": len(chapters) - (1 if proposed else 0),
            "candidate": str(candidate) if candidate else None,
            "chapters": [{"chapter": c.number, "title": c.title,
                          "effective_chars": len(normalized(c.body))} for c in chapters],
            "input_sha256": {name: hashlib.sha256(data).hexdigest() for name, data in inputs.items()},
        }
    # Detect local concurrent changes rather than attesting a different working tree.
    for name, data in inputs.items():
        if _file(root, root / name) != data:
            raise Blocked("校验期间输入发生变化；重新读取后重试")
    current = {str(p.relative_to(root)) for p in ready.glob("*.md") if p.name.lower() != "readme.md"}
    original = {name for name in inputs if name.startswith("chapters/ready/")}
    if current != original:
        raise Blocked("校验期间 ready 文件集合变化；重新读取后重试")
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--candidate", type=Path)
    args = parser.parse_args(argv)
    try:
        print(json.dumps(validate_snapshot(args.repo, args.candidate), ensure_ascii=False, indent=2))
        return 0
    except (Blocked, OSError, UnicodeError, yaml.YAMLError) as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
