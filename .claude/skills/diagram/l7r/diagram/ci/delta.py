"""The Delta: what THIS clone's own commits changed, and whether any of it is engine code.

FR-007: the delta is the diff from the MERGE BASE with main to HEAD (research R1) - equivalently
`git diff --name-only origin/main...HEAD`. A sync-in that merged main moves the merge base forward
to main's tip, so what main contributed drops out by construction; no per-commit filtering of merge
commits is needed, and a hand-made merge commit's content is main's and disappears the same way.

FR-008: `ENGINE` below is THE ONE LIST of paths whose change requires the paid gate. It governs
DISPATCH only - it must never narrow what `scripts/gate-stamp.py` hashes (that guard has its own
list and its own reasons). Documentation, design notes, research, the append-only logs and a pool
map's `.notes.md` are not engine code even inside the skill; the GM: *"even if the diagram
documentation was touched, but not the code itself, then we should not rerun the tests."*
`tests/ci/test_delta.py` walks every path KIND and pins its classification, so a new kind of file
cannot be silently either.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

SKILL = ".claude/skills/diagram/"

# (directory under the skill, accepted suffixes). An empty suffix tuple means "everything under it".
_ENGINE_DIRS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("l7r/", (".py",)),
    ("tests/", ()),  # a test change can change what the gate proves - fixtures included
    ("pool/", (".gen.py", ".json")),  # a generator, or a manifest (a generator's output under test)
)
_ENGINE_FILES = ("Makefile", "pyproject.toml", "requirements.txt", "requirements-dev.txt", "requirements.in", "requirements-dev.in")


def is_engine(path: str) -> bool:
    """Is this repo-relative path diagram ENGINE code (dispatch-relevant)?"""
    if not path.startswith(SKILL):
        return False
    rel = path[len(SKILL) :]
    if rel in _ENGINE_FILES:
        return True
    if rel.endswith(".notes.md"):
        return False
    for prefix, suffixes in _ENGINE_DIRS:
        if rel.startswith(prefix):
            return not suffixes or rel.endswith(suffixes)
    return False


@dataclass(frozen=True)
class Delta:
    base: str
    files: tuple[str, ...]
    engine: tuple[str, ...]

    @property
    def route(self) -> str:
        return "GATED" if self.engine else "DIRECT"

    @property
    def reason(self) -> str:
        if not self.files:
            return "no commits of our own since main - nothing to push"
        if self.engine:
            shown = ", ".join(self.engine[:4]) + (f" (+{len(self.engine) - 4} more)" if len(self.engine) > 4 else "")
            return f"{len(self.engine)} engine path(s) in our delta: {shown}"
        return f"{len(self.files)} file(s) changed, none of them diagram engine code - docs, specs or config only"


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout


def compute_delta(root: Path, base_ref: str = "origin/main") -> Delta:
    """The files our own commits changed since we diverged from `base_ref` (R1)."""
    base = _git(root, "merge-base", base_ref, "HEAD").strip()
    files = tuple(sorted(f for f in _git(root, "diff", "--name-only", base, "HEAD").splitlines() if f.strip()))
    return Delta(base=base, files=files, engine=tuple(f for f in files if is_engine(f)))


def engine_key(root: Path, tree: str) -> str:
    """The VERIFICATION KEY: a hash over the ENGINE paths' blob ids in `tree` (a tree or commit ref).

    A green build vouches for the engine CONTENT it tested - not for the docs beside it. Keying the
    record by the whole tree (the first cut, feature 130 R2) threw a $0.64 verification away every
    time a .notes.md, a run-log entry or a buildspec changed after the build (GM 2026-08-25: the same
    tests against literally the same content must not be paid for twice). The same `is_engine` that
    decides the ROUTE decides what is hashed, so the two can never disagree about what "engine" is.
    Computed from `git ls-tree` - no checkout, and the build computes it the same way on its merge.
    """
    out = _git(root, "ls-tree", "-r", tree)
    rows = sorted(f"{line.split()[2]} {line.split(maxsplit=3)[3]}" for line in out.splitlines() if line.strip() and is_engine(line.split(maxsplit=3)[3]))
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()
