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
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

SKILL = ".claude/skills/diagram/"

# (directory under the skill, accepted suffixes). An empty suffix tuple means "everything under it".
_ENGINE_DIRS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("l7r/", (".py",)),
    ("tests/", ()),  # a test change can change what the gate proves - fixtures included
    ("pool/", (".gen.py", ".json")),  # a generator, or a manifest (a generator's output under test)
)
# NOT engine, by the GM's definition (2026-08-25): "code changes which would be exercised by the
# tests". The Makefile, pyproject.toml, the lockfiles and scripts/ shape HOW the gate runs, and the
# local gate, gate-stamp and the hook suites cover them - they never cost a build. The first day's
# list carried the Makefile, pyproject and the lockfiles as engine on the theory that they change
# what the gate runs; that theory dispatched a build for a Makefile comment.
_ENGINE_FILES: tuple[str, ...] = ()


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


_GATE_FILES = ("Makefile", "pyproject.toml")


def is_gate(path: str) -> bool:
    """Is this repo-relative path something the LOCAL gate exercises (feature 132 amendment)?

    THE RULE: everything `make done` reads or runs - and this predicate is its known instances,
    not its extent. EVERY `*.py` under the skill (what lint/format/typecheck walk and what
    `gate-stamp`'s `diagram` area hashes: `.explain.py` and `wip/*.gen.py` count, not only
    `l7r/**` - the amendment's fidelity review caught the narrower list), the engine key's data
    (`tests/**`, `pool/*.gen.py`, `pool/*.json`), the gate's own configuration (Makefile,
    pyproject.toml, the pip lockfiles and their `.in` sources), and `scripts/**` (what `hooks-test`
    runs and `gate-stamp`'s `hooks` area hashes). The configuration paths were excluded from the
    REMOTE key precisely because they are "covered locally" (GM 2026-08-25) - this is that
    coverage. A documentation-only change matches nothing here, which is the whole point: *"it's
    only documentation"* must not cost a five-minute gate. CONTAINMENT MATTERS: the short-circuit
    re-writes the gate-stamp, which is safe only because every file the stamp hashes is in this
    key - `tests/ci/test_state.py` proves it against gate-stamp's own file list.
    """
    if is_engine(path) or path.startswith("scripts/"):
        return True
    if not path.startswith(SKILL):
        return False
    rel = path[len(SKILL) :]
    return rel.endswith(".py") or rel in _GATE_FILES or (rel.startswith("requirements") and rel.endswith((".txt", ".in")))


def engine_key_worktree(root: Path) -> str:
    """`engine_key` for the WORKING TREE (tracked + untracked-not-ignored engine files, current
    contents), so a `make done` run before committing keys the same content the commit will carry.
    Blob ids come from `git hash-object`, so the formula is identical to `engine_key(tree)`."""
    return _worktree_key(root, is_engine)


def gate_key_worktree(root: Path) -> str:
    """`_worktree_key` over `is_gate` - what a green local `make done` vouched for, exactly."""
    return _worktree_key(root, is_gate)


def _worktree_key(root: Path, keep: Callable[[str], bool]) -> str:
    out = _git(root, "ls-files", "-co", "--exclude-standard")
    paths = sorted(p for p in out.splitlines() if p.strip() and keep(p) and (root / p).is_file())
    if not paths:
        return hashlib.sha256(b"").hexdigest()
    shas = subprocess.run(["git", "-C", str(root), "hash-object", "--stdin-paths"], input="\n".join(paths) + "\n", capture_output=True, text=True, check=True).stdout.split()
    rows = sorted(f"{sha} {path}" for sha, path in zip(shas, paths, strict=True))
    return hashlib.sha256("\n".join(rows).encode()).hexdigest()
