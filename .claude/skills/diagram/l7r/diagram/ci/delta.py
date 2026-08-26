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
from typing import Any

SKILL = ".claude/skills/diagram/"

# (directory under the skill, accepted suffixes). An empty suffix tuple means "everything under it".
_ENGINE_DIRS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("l7r/", (".py",)),
    # tests/ is NOT engine content (GM 2026-08-25, feature 132 FR-024, asked and answered: *"if the only
    # thing that changed were tests AND the previous test run was green then we skipped the lengthy AWS
    # tests"* - "Yes, locally AND on AWS"). A tests-only delta is DIRECT, outside the engine key, and
    # outside gate-stamp's diagram area. The cost is recorded in the spec: a test edited after the last
    # green run lands unexecuted and runs on the next real gate. Feature 130's first cut had tests/ here.
    ("pool/", (".gen.py", ".json")),  # a generator, or a manifest (a generator's output under test)
)
# Subtrees of l7r/ that are NOT engine either (feature 132 FR-025, GM 2026-08-25): the ci package is
# tooling that decides whether the tests need to run - *"the engine itself isn't using it ... which
# makes it test code"*. Nothing in it is imported by a generator; its tests are fast and live in
# `make quick`, which is the check a ci-only change gets. Exactly what the GM named.
_NOT_ENGINE_DIRS: tuple[str, ...] = ("l7r/diagram/ci/",)
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
    if rel.endswith(".notes.md") or rel.startswith(_NOT_ENGINE_DIRS):
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
    Computed from `git ls-tree` + `git cat-file` - no checkout, and the build computes it the same
    way on its merge. Each file's id is its SEMANTIC content (`_content_id`), not its blob sha: a
    comment or docstring edit to engine Python keeps the key (GM 2026-08-26).
    """
    out = _git(root, "ls-tree", "-r", tree)
    entries = [(line.split()[2], line.split(maxsplit=3)[3]) for line in out.splitlines() if line.strip() and is_engine(line.split(maxsplit=3)[3])]
    return _key_from_ids(root, entries, lambda shas: _cat_blobs(root, shas))


def _cat_blobs(root: Path, shas: list[str]) -> dict[str, bytes]:
    """Blob contents by id, one `git cat-file --batch` call - only for the ids the semantic cache lacks."""
    if not shas:
        return {}
    blobs = subprocess.run(["git", "-C", str(root), "cat-file", "--batch"], input="".join(f"{s}\n" for s in shas).encode(), capture_output=True, check=True).stdout
    out: dict[str, bytes] = {}
    pos = 0
    for sha in shas:
        nl = blobs.index(b"\n", pos)
        size = int(blobs[pos:nl].split()[2])
        out[sha] = blobs[nl + 1 : nl + 1 + size]
        pos = nl + 1 + size + 1
    return out


def _key_from_ids(root: Path, entries: list[tuple[str, str]], fetch: Any) -> str:
    """The engine key from (git blob id, path) pairs. A `.py` keys on its SEMANTIC id, served from the
    cache by blob id; only cache MISSES are read (`fetch(shas) -> {sha: bytes}`). Anything else keys on
    the blob id itself. (T27, GM 2026-08-26: this used to read every engine file on every green run.)"""
    from l7r.diagram.ci.state import _gate_stamp  # local: state imports nothing from here

    gs = _gate_stamp(root)
    table = gs._cache_table(root)
    misses = [sha for sha, p in entries if p.endswith(".py") and sha not in table]
    contents = fetch(misses)
    rows = []
    for sha, p in entries:
        if p.endswith(".py"):
            rows.append(f"{table.get(sha) or gs.content_id(contents[sha], p, root)} {p}")
        else:
            rows.append(f"{sha} {p}")
    return hashlib.sha256("\n".join(sorted(rows)).encode()).hexdigest()


def engine_key_worktree(root: Path) -> str:
    """`engine_key` for the WORKING TREE (tracked + untracked-not-ignored engine files, current
    contents), so a `make done` run before committing keys the same content the commit will carry.
    Content ids come from `_content_id` on the file bytes, so the formula is identical to `engine_key(tree)`."""
    out = _git(root, "ls-files", "-co", "--exclude-standard")
    paths = sorted(p for p in out.splitlines() if p.strip() and is_engine(p) and (root / p).is_file())
    if not paths:
        return hashlib.sha256(b"").hexdigest()
    # RAW IDS FROM GIT, CONTENTS ONLY ON A MISS (GM 2026-08-26, T27): this ran on every green run and cost
    # 0.31 s of a 7.5 s quick - reading all 160 engine files in Python to sha256 them, when `git hash-object`
    # does exactly that in C and the semantic cache is keyed by that very sha. Now: one git call for the
    # raw ids, the cache answers every hit, and a file is read only when its semantic id is not cached.
    # THE INDEX ALREADY KNOWS EVERY UNCHANGED FILE'S BLOB ID (T27). `git hash-object` over all ~1,060 engine
    # files - the 856 regression manifests included - cost 270 ms on every green run; `ls-files -s` hands
    # back the staged ids in 15 ms, so only files that differ from the index (modified, or untracked) are
    # hashed. Exact: a modified file's index id is stale and is never used.
    staged = {line.split()[3]: line.split()[1] for line in _git(root, "ls-files", "-s", "--", *paths).splitlines() if line.strip()}
    changed = set(_git(root, "diff", "--name-only", "--", *paths).splitlines())
    fresh = [p for p in paths if p in changed or p not in staged]
    ids = dict(staged)
    if fresh:
        ids.update(
            zip(fresh, subprocess.run(["git", "-C", str(root), "hash-object", "--stdin-paths"], input="\n".join(fresh) + "\n", capture_output=True, text=True, check=True).stdout.split(), strict=True)
        )
    entries = [(ids[p], p) for p in paths]
    by_sha = {sha: p for sha, p in entries}
    return _key_from_ids(root, entries, lambda miss: {s: (root / by_sha[s]).read_bytes() for s in miss})
