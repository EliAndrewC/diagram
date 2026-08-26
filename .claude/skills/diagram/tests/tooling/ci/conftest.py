"""Fixtures for the dispatcher tests: a throwaway repository with a `main`, a fake AWS client driven
by the RECORDED responses in fixtures/ (Principle X: saved fixtures at the boundary, never a
transport mock), and a scripted `sh` so lint / reference / git outcomes are chosen per test."""

from __future__ import annotations

import json
import subprocess
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
REPO_ROOT = Path(__file__).resolve().parents[6]  # tests/tooling/ci/ is one level deeper than tests/ci/ was (T29)  # the real repository, for scripts/gate-stamp.py


def load(name: str) -> dict[str, Any]:
    return dict(json.loads((FIXTURES / name).read_text(encoding="utf-8")))


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    """A repo shaped like this one: scripts/gate-stamp.py present, the skill dir, one commit on main
    and an `origin/main` ref pointing at it (so merge-base and merge-tree work)."""
    root = tmp_path / "clone"
    root.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main", str(root)], check=True)
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    (root / "scripts").mkdir()
    (root / "scripts" / "gate-stamp.py").write_text((REPO_ROOT / "scripts" / "gate-stamp.py").read_text(encoding="utf-8"), encoding="utf-8")
    skill = root / ".claude" / "skills" / "diagram"
    (skill / "l7r" / "diagram").mkdir(parents=True)
    (skill / "l7r" / "diagram" / "m.py").write_text("x = 1\n", encoding="utf-8")
    (skill / "dev" / "run-log").mkdir(parents=True)
    (skill / "dev" / "bypass-log").mkdir(parents=True)
    (root / "buildspec").mkdir()
    for m in ("check", "merge", "image"):
        (root / "buildspec" / f"{m}.yml").write_text(f"version: 0.2\n# {m}\n", encoding="utf-8")
    (root / "README.md").write_text("base\n", encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "base")
    git(root, "update-ref", "refs/remotes/origin/main", "HEAD")
    return root


def commit(root: Path, rel: str, text: str, msg: str = "work") -> str:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    git(root, "add", "-A")
    git(root, "commit", "-qm", msg)
    return git(root, "rev-parse", "HEAD")


class FakeClient:
    """Replays the recorded responses and logs every call - the tests assert on `calls`."""

    def __init__(self, deny_start: bool = False, statuses: list[str] | None = None, verified: dict[str, bytes] | None = None, artifacts: dict[str, bytes] | None = None) -> None:
        self.calls: list[tuple[str, Any]] = []
        self.deny_start = deny_start
        self.statuses = list(statuses or ["IN_PROGRESS", "SUCCEEDED"])
        self.objects: dict[str, bytes] = dict(verified or {})
        self.objects.update(artifacts or {})
        self._log_pages = 0

    def start_build(self, **kw: Any) -> dict[str, Any]:
        self.calls.append(("start_build", kw))
        if self.deny_start:
            from l7r.diagram.ci.dispatch import AccessDenied

            err = load("start_build_access_denied.json")["Error"]
            raise AccessDenied("codebuild:StartBuild", str(err["Message"]))
        return load("start_build.json")

    def batch_get_builds(self, ids: list[str]) -> dict[str, Any]:
        self.calls.append(("batch_get_builds", ids))
        status = self.statuses.pop(0) if len(self.statuses) > 1 else self.statuses[0]
        fx = load("batch_get_builds_in_progress.json" if status == "IN_PROGRESS" else "batch_get_builds_succeeded.json")
        fx["builds"][0]["buildStatus"] = status
        fx["builds"][0]["id"] = ids[0]
        return fx

    def stop_build(self, id: str) -> dict[str, Any]:
        self.calls.append(("stop_build", id))
        return {"build": {"id": id, "buildStatus": "STOPPED"}}

    def get_log_events(self, group: str, stream: str, token: str | None) -> dict[str, Any]:
        self.calls.append(("get_log_events", (group, stream, token)))
        self._log_pages += 1
        if self._log_pages > 1:
            return {"events": [], "nextForwardToken": token}
        return load("get_log_events.json")

    def put_object(self, bucket: str, key: str, body: bytes) -> None:
        self.calls.append(("put_object", key))
        self.objects[key] = body

    def get_object(self, bucket: str, key: str) -> bytes | None:
        self.calls.append(("get_object", key))
        return self.objects.get(key)

    def list_prefix(self, bucket: str, prefix: str) -> list[str]:
        self.calls.append(("list_prefix", prefix))
        return sorted(k for k in self.objects if k.startswith(prefix))

    def delete_object(self, bucket: str, key: str) -> None:
        self.calls.append(("delete_object", key))
        self.objects.pop(key, None)

    def names(self) -> list[str]:
        return [c[0] for c in self.calls]


class ScriptedSh:
    """`sh` for the dispatcher: git commands run for real; make targets answer from a script."""

    def __init__(self, make: Mapping[str, tuple[int, str]] | None = None, push_rc: int = 0) -> None:
        self.make = dict(make or {})
        self.push_rc = push_rc
        self.ran: list[list[str]] = []

    def __call__(self, args: list[str], cwd: Path, env: Mapping[str, str] | None) -> tuple[int, str]:
        self.ran.append(args)
        if args[0] == "make":
            key = " ".join(a for a in args[1:] if not a.startswith("--"))
            return self.make.get(key, (0, ""))
        if args[:2] == ["git", "push"]:
            assert env and env.get("GIT_ASKPASS", "").endswith("git-askpass-token.sh") and "GITHUB_TOKEN" in env, "the token must travel via GIT_ASKPASS, never the command line"
            return self.push_rc, "" if self.push_rc == 0 else "fatal: could not push"
        if args[:2] == ["git", "fetch"]:
            return 0, ""
        p = subprocess.run(args, cwd=str(cwd), capture_output=True, text=True)
        return p.returncode, p.stdout + p.stderr
