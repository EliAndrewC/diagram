"""The tests that READ the shipped pool manifests - one rule for `make quick` and for the gate's planner (feature 430 T01, D1).

WHY. A pool manifest is data: no test's coverage context shows that it read one, so file-level selection cannot see the
dependency, and until feature 430 the gate planned FULL whenever one changed - 11 of 2026-10-26's 24 gates ran the whole
suite only because `pool/hamlets/inashiro/inashiro.json` moved (`specs/430-faster-landings/measurements.json`,
`m:full-plan-reasons`). Feature 328 wave 54 had already met the same blindness in `make quick` and answered it with a text
search: a test whose source names the pool as a path part reads the manifests. The planner now asks the same search over the
gate's own trees, and `scripts/gates/pool-readers.py` asks it over quick's.

A READER is a test module (`test_*.py`) whose source names the pool as a path part (`"pool"`, as `"pool", "hamlets"` or a loop
over `("pool", "legacy-hand-authored-pool")`) or globs `pool/hamlets/*`. Broad on purpose: the notes census
(`tests/test_notes_census.py`) reached the manifests through a tree loop a narrower pattern missed, and a reader too many costs
a fraction of a second.
"""

from __future__ import annotations

import re
from pathlib import Path

#: the pool named as a path part: `"pool", "hamlets"`, or a tree loop's `("pool", ...)`, or a glob of the hamlets
READS = re.compile(r'"pool"|pool/hamlets/\*')
#: a shipped map's manifest: `pool/<tier>/<map>/<map>.json` (a generator's output under test)
MANIFEST = re.compile(r"^pool/[^/]+/([^/]+)/\1\.json$")
#: the trees the gate does not collect (`tests/CLAUDE.md`: soak is no ordinary run; a tier tree runs only on its own marker)
NOT_GATE = ("soak",)


def is_manifest(path: str) -> bool:
    """Is this repository-relative path a shipped pool map's manifest?"""
    return bool(MANIFEST.match(path))


def readers(root: Path, skip: tuple[str, ...] = NOT_GATE) -> list[str]:
    """The reader test modules under `tests/`, repository-relative and sorted, leaving out the top-level trees `skip` names
    and every `tier_*` tree."""
    out = []
    for p in sorted((root / "tests").rglob("test_*.py")):
        parts = p.relative_to(root / "tests").parts
        if parts[0] in skip or parts[0].startswith("tier_"):
            continue
        if READS.search(p.read_text(encoding="utf-8")):
            out.append(p.relative_to(root).as_posix())
    return out


#: a test that READS the Rust crate's sources or runs its tooling: the crate named as a path part or by its tooling's names
RUST_READS = re.compile(r'"rust"|rust/phases|rust_checks|claims_rust|\.rs\b')


def rust_readers(root: Path, skip: tuple[str, ...] = NOT_GATE) -> list[str]:
    """THE TESTS A RUST CHANGE OWES (feature 444 T36; the GM 2026-11-07: "make sure our iteration loop is fast"): no Python test's
    coverage context shows it reading a `.rs` file, so the planner ran the whole Python suite for every Rust edit (213 s) - the
    reader test modules under `tests/`, as `readers` finds the pool's: those whose source names the crate, its tooling or `.rs`."""
    out = []
    for p in sorted((root / "tests").rglob("test_*.py")):
        parts = p.relative_to(root / "tests").parts
        if parts[0] in skip or parts[0].startswith("tier_"):
            continue
        if RUST_READS.search(p.read_text(encoding="utf-8")):
            out.append(p.relative_to(root).as_posix())
    return out
