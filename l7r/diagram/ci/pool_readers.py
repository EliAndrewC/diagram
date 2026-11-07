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

import json
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
#: the tree whose tests' reads the gate records (`tests/tooling/_test_deps.py`), and the baseline's record of them
TOOLING = "tests/tooling/"
TOOLING_READS = "tooling-reads.json"
#: a recorded module whose test started a program the recorder cannot see into: its reads are not known
UNKNOWN = "*"


def recorded_reads(store: Path) -> dict[str, set[str]] | None:
    """{test module: every path its tests and the module itself read, files and listed directories} from a kept reads store
    (`_test_deps.py`'s), `UNKNOWN` among them where a test started a program it could not see into; None with no store."""
    try:
        kept = json.loads(store.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None
    out: dict[str, set[str]] = {}
    entries = [(n.split("::")[0], e) for n, e in (kept.get("tests") or {}).items()]
    entries += [(m, v.get("entry") or {}) for m, v in (kept.get("files") or {}).items()]
    for module, e in entries:
        out.setdefault(module, set()).update(e.get("files") or [], e.get("dirs") or [], [UNKNOWN] if e.get("opaque") else [])
    return out or None


def touches(reads: set[str], changed: list[str]) -> bool:
    """Did a recorded read see a changed path: the file itself, or the directory that lists it (an added or deleted file)?"""
    return any(c in reads or c.rpartition("/")[0] in reads for c in changed)


def rust_readers(root: Path, changed: list[str] = [], reads: dict[str, set[str]] | None = None, skip: tuple[str, ...] = NOT_GATE) -> list[str]:  # noqa: B006
    """THE TESTS A RUST CHANGE OWES (feature 444 T36; the GM 2026-11-07: "make sure our iteration loop is fast"): no Python test's
    coverage context shows it reading a `.rs` file, so the planner ran the whole Python suite for every Rust edit (213 s).

    A tooling module the gate recorded is selected when one of its tests READ a `changed` path (`reads`, `recorded_reads` of the
    baseline's store); every other module - outside the recorded tree, never recorded, or one whose test started a program the
    recorder could not see into - when its source names the crate, its tooling or `.rs` (`RUST_READS`). The source rule alone
    selected 20 modules for a one-line edit and missed four that read the crate (measured 2026-11-07: `test_bundle_shared_text`,
    `test_modal_checks`, `test_claims_coverage`, `test_doc_links`), and its tooling tests only ran `rust_checks.py` on a fixture
    crate - their change is a `scripts/` change, planned as one."""
    out = []
    for p in sorted((root / "tests").rglob("test_*.py")):
        parts = p.relative_to(root / "tests").parts
        if parts[0] in skip or parts[0].startswith("tier_"):
            continue
        rel = p.relative_to(root).as_posix()
        seen = (reads or {}).get(rel) if rel.startswith(TOOLING) else None
        if touches(seen, changed) if seen is not None and UNKNOWN not in seen else RUST_READS.search(p.read_text(encoding="utf-8")):
            out.append(rel)
    return out
