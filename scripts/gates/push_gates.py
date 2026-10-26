#!/usr/bin/env python3
"""push_gates.py - what each push gate judges, so a push whose delta holds none of it skips the gate, and a gate that passed on
this exact content is not run again (feature 430 T04, D4; the GM 2026-10-26, item 4).

    push_gates.py skip <gate>    exit 0, saying why, when the delta holds nothing the gate judges or a pass is stored for it
    push_gates.py pass <gate>    store the gate's pass for the delta as it stands (the gate calls it when it passes)

WHY. A push of records alone took 10.9 s, the claims gate 5.7 s and the record gate 2.3 s of it, each reading the whole claims
index or the whole record to find nothing owed (the push timed gate by gate, 2026-10-26, `specs/430-faster-landings/request.md`);
and the same delta was judged again on every retry of a push.

WHAT EACH JUDGES (`JUDGES`), read off the gate's own constants and pinned by `tests/tooling/test_push_gates.py`, which fails when a
constant names a path the list lacks:
- `claims`: the engine and the Mode A procedures (`claims.BASE_PATHS`), the claims index, its deferred list and page store, and
  `specs/` (a known drift reads its open task row, and its record in `gm-review.jsonl`);
- `entry`: the research record and the pop-ups' registry (`record_units.RECORD`, `entry_owed.CLASSES`, `entry_owed.COMPOUND_KINDS`,
  `modal_owed.MODALS` - all under `research/` and `l7r/diagram/interactive/`);
- `cohort`: the engine (`ci/delta.is_engine`), and the cohort's run records.

THE DELTA is what the merge base with `origin/main` and the working tree differ in, untracked files included - the delta every
gate already judges. A PASS is stored under the clone's git directory keyed on the gate, the merge base, the tree of `scripts/` at
HEAD (the gate's own code) and the blob ids of the delta's paths it judges; a refusal is never stored, and a delta with an
uncommitted path the gate judges is never served from the store.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

#: the path prefixes each gate judges (the module docstring says where each comes from)
JUDGES: dict[str, tuple[str, ...]] = {
    "claims": ("l7r/", "docs/buildings.md", "docs/buildings/", "research/questions/", "dev/claims-index.json", "dev/claims-deferred.json", "dev/claims-pages.json", "specs/"),
    "entry": ("research/", "l7r/diagram/interactive/"),
    "cohort": ("l7r/", "pool/", "legacy-hand-authored-pool/", "dev/cohort-log/"),
}
#: what the gate's message says it found none of
WHAT = {"claims": "engine code, Mode A procedure, cited page, claims record or task row", "entry": "research record or pop-up", "cohort": "engine code"}


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def delta(root: Path) -> tuple[str, list[str], set[str]] | None:
    """(the merge base, every path the delta holds, the uncommitted ones), or None when there is no merge base with `origin/main`
    to read a delta from - then nothing is skipped and the gate judges as it always did (a tree with no `origin/main`, as the
    guard suites' fixtures, reads its own base)."""
    base = git(root, "merge-base", "HEAD", "origin/main").strip()
    if not base:
        return None
    committed = set(git(root, "diff", "--name-only", base, "HEAD").split())
    dirty = set(git(root, "diff", "--name-only", "HEAD").split()) | set(git(root, "ls-files", "--others", "--exclude-standard").split())
    return base, sorted(committed | dirty), dirty


def judged(gate: str, paths: list[str]) -> list[str]:
    prefixes = JUDGES[gate]
    return [p for p in paths if any(p.startswith(x) if x.endswith("/") else p == x for x in prefixes)]


def key(root: Path, gate: str, base: str, paths: list[str]) -> str:
    h = hashlib.sha256(f"{gate}\n{base}\n{git(root, 'rev-parse', 'HEAD:scripts').strip()}\n".encode())
    h.update(git(root, "ls-tree", "-r", "HEAD", "--", *paths).encode() if paths else b"")
    return h.hexdigest()


def store(root: Path) -> Path:
    common = git(root, "rev-parse", "--git-common-dir").strip() or ".git"
    p = Path(common)
    return (p if p.is_absolute() else root / p) / "push-gates"


def skip(root: Path, gate: str) -> str:
    """Why the gate need not run, or ''."""
    got = delta(root)
    if got is None:
        return ""
    base, paths, dirty = got
    mine = judged(gate, paths)
    if not mine:
        return f"{gate}-gate: nothing to judge - the delta holds no {WHAT[gate]} (feature 430 T04)"
    if not set(mine) & dirty and (store(root) / gate / key(root, gate, base, mine)).is_file():
        return f"{gate}-gate: passed already on this delta's content ({len(mine)} path(s) it judges, unchanged) (feature 430 T04)"
    return ""


def record_pass(root: Path, gate: str) -> None:
    got = delta(root)
    if got is None:
        return
    base, paths, dirty = got
    mine = judged(gate, paths)
    if mine and not set(mine) & dirty:
        d = store(root) / gate
        d.mkdir(parents=True, exist_ok=True)
        (d / key(root, gate, base, mine)).write_text("pass\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[0] not in ("skip", "pass") or argv[1] not in JUDGES:
        print(__doc__.split("\n\n")[1], file=sys.stderr)
        return 2
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip() or ".")
    if argv[0] == "pass":
        record_pass(root, argv[1])
        return 0
    why = skip(root, argv[1])
    if why:
        print(why)
        return 0
    return 1


if __name__ == "__main__":
    sys.dont_write_bytecode = True
    sys.exit(main(sys.argv[1:]))
