"""No kept file reaches the deleted Python hamlet engine (feature 444 T40, FR-024 part 4; the round arbiter on ask:444-a11-plan-d7).

WHY. The GM 2026-11-07: "literally delete all of the Python code that does any kind of Hamlet generation whatsoever ... by
completely eliminating in every way this Python code, it will not be able to slow us down." A consumer of the deleted packages
fails one of two ways: loudly (an import error, which the kept suite catches) or SILENTLY - a check that names the deleted tree as
a path and passes when it is absent, as the claims gate's `[ -d l7r/diagram/hamletgen ] || exit 0` did. So every kept file is read
for a deleted package named in an import form, a relative form or a path form, and only the history this list names by file -
fixtures that build a fake tree of the old name, closed features' records, notes written about old maps - may still name one.
"""

from __future__ import annotations

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DELETED = ("hamletgen", "settlement", "sitegen", "waterfields", "overlap", "citybudget")
_N = "(" + "|".join(DELETED) + ")"
FORMS = re.compile(
    rf"import l7r\.diagram\.{_N}\b|from l7r\.diagram import [^\n]*\b{_N}\b|from l7r\.diagram\.{_N}\b"  # import forms
    rf"|from \.+{_N}\b|from \.+ import [^\n]*\b{_N}\b"  # relative forms
    rf"|l7r/diagram/{_N}\b|l7r\.diagram\.{_N}\b|tests/{_N}\b"  # path forms
)
#: THE KEPT TREES, by `git ls-files | cut -d/ -f1 | sort -u` (2026-11-08): every top-level entry that holds code or configuration
#: that runs, and `dev/`, whose records code reads; the figures `make figures` re-runs (`specs/*/measurements*.json`); and
#: `docs/` and the root `CLAUDE.md`, which sessions and agents load. Left out: the rest of `specs/` - prose and records that make
#: reads and never runs, 589 hits in 5,360 files (the round arbiter on ask:444-d7-scope-round3) - and `research/` and `LICENSE`,
#: which consume nothing (its plan review of 2026-11-08)
SCOPE = (
    ":(glob)specs/*/measurements*.json",
    # the frozen reference of the Python stages, prose history until its Rust page replaces it (FR-024 part 1) - excluded, not
    # listed, because the remote build does not check it out (tests/tooling/ci/test_sparse_checkout.py), where a listed entry would
    # read as stale; named without its trailing slash, which is the form that sparse check reads as a use of the path
    ":(exclude)dev/placement-stages-frozen",
    "docs/**",
    "CLAUDE.md",
    "l7r/**",
    "tests/**",
    "scripts/**",
    "rust/**",
    ".claude/**",
    ".specify/**",
    "pool/**",
    "legacy-hand-authored-pool/**",
    "dev/**",
    "buildspec/**",
    "Makefile",
    "pyproject.toml",
    "Dockerfile.ci",
    "clippy.toml",
    ":(glob)requirements*",
)

#: THE HISTORY, file by file, each with why it may still name a deleted package - no glob, no directory
HISTORY = {
    "tests/tooling/test_no_deleted_engine.py": "this test, which names what it looks for",
    "l7r/diagram/knobs.json": "the knob registry's export records where each knob was declared, as provenance",
    "l7r/diagram/tools/claims.py": "the claims index's Python root, an empty scope since the deletion; its fixtures build that tree",
    "scripts/reviews/work_budget_bundle.py": "the audit bundle's Python half, read only where a fixture builds it; the Rust half stands alone",
    "scripts/gates/claims-gate.sh": "the guard reads rust/phases first; the old directory is its fixtures' engine",
    "scripts/gates/room_table.json": "closed features' measured room, history",
    "pool/hamlets/inashiro/inashiro.notes.md": "the map's history, written while the Python engine drew it",
    "tests/CLAUDE.md": "the test bed's history of its trees",
    "tests/test-bed-detail.md": "the test bed's history of its trees",
    "tests/hooks/fixtures/bash-parse-corpus-2026-09.json": "a recorded corpus of commands, parsed and never run",
    "tests/hooks/fixtures/command-window-2026-09-13.json": "a recorded corpus of commands, parsed and never run",
    "tests/hooks/fixtures/guard-refusals-2026-09.json": "a recorded corpus of commands, parsed and never run",
    "tests/hooks/fixtures/main-tree-refusals-2026-09.json": "a recorded corpus of commands, parsed and never run",
    "tests/hooks/test-claims-gate.sh": "builds a fake engine tree of the old name in a temporary repository",
    "tests/hooks/test-cohort-gate.sh": "an example engine path in a fixture repository",
    "tests/hooks/test-engine-freeze-hooks.sh": "an example engine path a guard classifies",
    "tests/hooks/test-guard-file-hooks.sh": "an example path a guard classifies",
    "tests/hooks/test-make-only-hooks.sh": "an example command a guard parses",
    "tests/hooks/test-measure-hooks.sh": "an example command a guard parses",
    "tests/hooks/test-phase-source-hooks.sh": "an example engine path a guard classifies",
    "tests/pipeline/test_poolmaps.py": "a fixture pool's scripted engine name",
    "tests/test_tooling_asked.py": "an example test path a selector reads",
    "tests/tooling/ci/test_delta.py": "an example engine path the delta classifies",
    "tests/tooling/ci/test_incremental.py": "an example path in a fixture coverage baseline",
    "tests/tooling/test_apply_edits.py": "an example path an edit sweep rewrites",
    "tests/tooling/test_browser_skip.py": "an example path in a fixture repository",
    "tests/tooling/test_claims_coverage.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_claims_index.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_claims_scoping.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_known_drift.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_measured_surface.py": "the gate surface's history in its message",
    "tests/tooling/test_modal_checks.py": "an example path in a fixture record",
    "tests/tooling/test_phase_sources.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_plan_hold.py": "an example engine path a held feature names",
    "tests/tooling/test_pool_readers.py": "an example path in a fixture repository",
    "tests/tooling/test_review_owed.py": "an example path in a fixture repository",
    "tests/tooling/test_tick_task.py": "an example path in a fixture task",
    "tests/tooling/test_work_budget_bundle_rust.py": "builds a fake engine tree of the old name beside the Rust",
    "tests/tools/test_claims.py": "builds a fake engine tree of the old name",
    "tests/tooling/test_figures_deleted_engine.py": "fixture commands naming the old paths, proven never run",
    "dev/review-ledger.md": "the append-only ledger of every review pass, history",
    "dev/claims-triage-skips.jsonl": "the append-only record of triage skips, history",
    "dev/gate.md": "the Python engine's dev doc, until the Rust's own pages replace it",
    "dev/loop.md": "the Python engine's dev doc, until the Rust's own pages replace it",
    "dev/performance.md": "the Python engine's dev doc, until the Rust's own pages replace it",
    "dev/placement.md": "the Python engine's dev doc, until the Rust's own pages replace it",
    "specs/257-sheet-matches-map/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/261-northwest-wind-by-default/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/267-compound-research-owed/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/269-research-backfill/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/276-engine-hotspots-and-test-scans/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/282-threshing-yard-layout/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/291-homestead-grove-sides/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/302-field-by-construction/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/328-match-the-research/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/372-match-the-research-remaining/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/374-match-the-research-continued/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/375-enforced-wave-process/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/430-faster-landings/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "specs/444-work-budget-program/measurements.json": "frozen figures: make figures lists each command naming a deleted package as not re-measured, never run (scripts/measure/figures.py)",
    "docs/iteration-loop.md": "prose: the loop as the Python engine ran it, history",
    "docs/migration-plan.md": "prose: the namespace portion's history",
    "docs/session-clones.md": "prose: an example path in a recorded failure, history",
}
#: the append-only logs, each named in its own file (FR-024 part 4: "enumerated file by file")
HISTORY |= {line: "an append-only log written while the Python engine ran" for line in (REPO / "tests/tooling/deleted-engine-logs.txt").read_text().splitlines() if line and not line.startswith("#")}


def _hits() -> list[str]:
    out = subprocess.run(["git", "-C", str(REPO), "grep", "-lE", FORMS.pattern, "--", *SCOPE], capture_output=True, text=True, check=False)
    return sorted(set(out.stdout.split()))


def test_no_kept_file_names_a_deleted_package() -> None:
    hits = _hits()
    assert hits, "the search found nothing at all, not even its own history list - it is not reading the tree"
    new = [f for f in hits if f not in HISTORY]
    assert not new, (
        "a kept file names the deleted Python hamlet engine (feature 444 FR-024): "
        + ", ".join(new)
        + " - port it to the Rust (rust/phases), drop it, or, if it is history that runs nothing, add it to HISTORY with why"
    )


def test_every_history_entry_still_names_one() -> None:
    """A stale entry would let a later file of the same name in through a gap no one sees."""
    stale = sorted(set(HISTORY) - set(_hits()))
    assert not stale, f"HISTORY names files that no longer name a deleted package - drop them: {stale}"


def test_each_form_is_caught() -> None:
    for line in (
        "from l7r.diagram.hamletgen import plan",
        "from l7r.diagram import interactive, settlement",
        "import l7r.diagram.waterfields",
        "from .overlap import matrix",
        "from . import sitegen",
        "path = 'l7r/diagram/settlement/core.py'",
        "--ignore=tests/hamletgen",
    ):
        assert FORMS.search(line), line
    for line in ("a settlement map", "the caption overlap", "from l7r.diagram import interactive", "rust/phases/src/field.rs"):
        assert not FORMS.search(line), line
