from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from .content import Blocked


class Repository:
    def __init__(self, root: Path, slug: str, branch: str):
        if not re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", slug):
            raise Blocked("GITHUB_REPOSITORY 必须为 owner/repo")
        if not re.fullmatch(r"[A-Za-z0-9_][A-Za-z0-9_./-]*", branch) or ".." in branch:
            raise Blocked("非法 Git 分支")
        self.root, self.branch = root, branch
        self.url = f"https://github.com/{slug}.git"
        # Git reads the token only on credential prompt; never embed it in remote URLs.
        helper = root.parent / "git-askpass.py"
        helper.write_text(
            '#!/usr/bin/env python3\nimport os,sys\nfrom pathlib import Path\n'
            'print("x-access-token" if "username" in sys.argv[1].lower() else '
            'Path(os.environ["GITHUB_TOKEN_FILE"]).read_text().strip())\n', encoding="utf-8"
        )
        helper.chmod(0o700)
        self.env = {**os.environ, "GIT_ASKPASS": str(helper), "GIT_TERMINAL_PROMPT": "0"}

    def git(self, *args: str, cwd: Path | None = None) -> str:
        result = subprocess.run(["git", "-c", "credential.helper=", *args], cwd=cwd or self.root,
                                env=self.env, capture_output=True, text=True, timeout=120)
        if result.returncode:
            # stderr may contain credential/provider information. Keep logs secret-free.
            raise Blocked(f"Git {args[0]} 失败（认证、网络、分支保护或冲突）；保留本地状态，请检查")
        return result.stdout.strip()

    def sync(self):
        if not (self.root / ".git").exists():
            self.git("clone", "--branch", self.branch, "--single-branch", self.url, str(self.root), cwd=self.root.parent)
        if self.git("remote", "get-url", "origin") != self.url:
            raise Blocked("持久化仓库 origin 与配置不符")
        if self.git("branch", "--show-current") != self.branch:
            raise Blocked("持久化仓库分支与配置不符")
        if self.git("status", "--porcelain"):
            raise Blocked("发布仓库有未提交修改；请先修复/恢复归档，不覆盖文件")
        self.git("config", "user.name", "Fanqie Publisher")
        self.git("config", "user.email", "fanqie-publisher@users.noreply.github.com")
        self.git("fetch", "origin", self.branch)
        ahead = int(self.git("rev-list", "--count", f"origin/{self.branch}..HEAD"))
        behind = int(self.git("rev-list", "--count", f"HEAD..origin/{self.branch}"))
        if ahead and behind:
            raise Blocked("GitHub 与本地均有新提交；需解决分支分叉，禁止强推")
        if ahead:
            self.git("push", "origin", f"HEAD:refs/heads/{self.branch}")
        else:
            self.git("merge", "--ff-only", f"origin/{self.branch}")

    def commit_archive(self, filename: str, number: int):
        self.git("add", "--", f"chapters/ready/{filename}", f"chapters/published/{filename}", "plans/chapter_plan.csv")
        self.git("commit", "-m", f"chore: archive verified Fanqie chapter {number}")
        self.git("push", "origin", f"HEAD:refs/heads/{self.branch}")
