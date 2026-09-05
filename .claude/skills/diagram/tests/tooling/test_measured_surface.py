"""Feature 178 item 1 - the gate that enforces a coverage floor must be able to see what that floor measures.

THE DEFECT THIS CLOSES (feature 177's R12). Two rules were each correct and together left a hole:
`gate-stamp` excluded `l7r/diagram/ci/` from the `diagram` area by the GM's feature-132 FR-025 ruling
(*"isn't it actually test code?"*), while feature 174's coverage floor MEASURES it, because
`source = ["l7r"]` is derived and `ci/` is under `l7r/`. So a change confined to `ci/` owed 100%
coverage and could not re-open the gate that enforces it - `make done` answered "already verified" on
a delta that rewrote four ci modules, and the floor was reached only by running `make test-full` by
hand. GM 2026-09-03: *"I think a short-circuit for 'measured but engine' is best."*

The fix splits ONE list that was answering TWO questions. `gate-stamp` answers "does this delta owe a
local GATE"; `delta.is_engine` answers "does it owe a PAID BUILD". FR-025 stands for the second.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

pytestmark = pytest.mark.tooling

HERE = Path(__file__).resolve().parents[2]
REPO = HERE.parents[2]


def _gate_stamp():
    spec = importlib.util.spec_from_file_location("gate_stamp_under_test", REPO / "scripts" / "gate-stamp.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_exclusions_are_derived_from_the_coverage_config() -> None:
    """FR-003. A second hand-kept roster would drift from `source` exactly as the roster constitution
    X clause 5 replaced did, so the list is computed: a declared exclusion survives only if coverage
    does not measure it."""
    gs = _gate_stamp()
    assert gs.coverage_sources(REPO) == ("l7r/",), "the authority is [tool.coverage.run] source"
    assert "l7r/diagram/ci/" in gs._DECLARED_EXCLUDE["diagram"], "still DECLARED - the derivation is what drops it"
    assert gs.exclusions("diagram", REPO) == ("tests/",), "measured -> not excludable; tests/ is outside l7r/ and survives"


def test_an_unreadable_coverage_config_fails_CLOSED() -> None:
    """The first draft returned () on an unreadable config, which makes the derivation a no-op and
    silently restores the whole defect - in the failure case nobody tests. Its own comment called that
    "the safe direction"; the gate-stamp suite caught it inside a minute, because its fixture has no
    `pyproject.toml`. The default is not a guess: constitution X clause 5 states the rule the config
    encodes, *"if you add a file under `l7r/`, it is measured"*."""
    gs = _gate_stamp()
    assert gs.coverage_sources(Path("/nonexistent-root")) == ("l7r/",)
    assert gs.exclusions("diagram", Path("/nonexistent-root")) == ("tests/",), "ci/ stays measured even with no config to read"


def test_ci_is_hashed_now_and_the_other_two_populations_are_untouched() -> None:
    """FR-001 and FR-003's add-only rule, on the real tree. The derivation may REMOVE an exclusion
    (widening what the gate sees) and must never ADD one: `AREAS["diagram"]`'s `*.py` crosses `/`, so
    it covers 37 files outside `l7r/` and `tests/` - every pool and legacy `.gen.py`, all of `wip/` -
    that coverage does not measure and that the push-time stamp check must keep hashing."""
    gs = _gate_stamp()
    files = [str(f) for f in gs._area_files(REPO, *gs.AREAS["diagram"])]
    assert sum("/l7r/diagram/ci/" in f for f in files) == 12, "ci/ is inside the gate's surface now (was 0)"
    assert sum("/l7r/" not in f and "/tests/" not in f for f in files) == 37, "the add-only rule: these must not be dropped"
    assert sum("/tests/" in f for f in files) == 0, "FR-024 is untouched - a tests-only change still owes no gate"


def test_the_PAID_route_is_untouched_so_a_ci_change_still_dispatches_nothing() -> None:
    """FR-002, and it is the half of the GM's FR-025 ruling that STANDS. `delta.is_engine` is a
    separate computation from the stamp, so widening the gate does not widen what costs money: a
    ci-only delta still routes DIRECT and still starts no build."""
    from l7r.diagram.ci.delta import is_engine

    S = ".claude/skills/diagram/"
    assert not is_engine(S + "l7r/diagram/ci/decision.py"), "ci/ is not engine for the ROUTE - money is the other question"
    assert not is_engine(S + "l7r/diagram/ci/dispatch.py")
    assert is_engine(S + "l7r/diagram/settlement/houses.py"), "...and real engine code still is"


def test_test_full_records_a_green_state_so_the_strongest_local_proof_counts() -> None:
    """Feature 178 FR-004/FR-005, item 2. `make test-full` runs every tree with all three floors and
    recorded nothing, so it could not satisfy the paid route's `green-local-since-edit` - while a
    `make quick` that selected nothing and reported "no tests ran in 0.97s" could (feature 177, R15).

    Asserted on the recipe rather than by running it, because running it costs four minutes and the
    property is textual: the recording is chained with `&&`, so a red run records nothing."""
    makefile = (HERE / "Makefile").read_text(encoding="utf-8")
    body = makefile.split("\ntest-full:")[1].split("\n\n")[0]
    assert "$(STATE) green-local test-full" in body, "test-full must record, like done/quick/reference/test-file"
    assert "&& $(STATE) green-local test-full" in body, "ONLY on success - a red sweep must vouch for nothing"
    # ...and the four that already recorded still do, so this widened the set rather than moving it.
    for target in ("green-local quick", "green-local reference", "green-local test-file"):
        assert target in makefile, f"{target} must still record"


def test_the_two_engine_definitions_both_see_the_page_assets() -> None:
    """Feature 181: `gate-stamp.py`'s diagram area and `delta.is_engine` are two definitions of engine
    content that must agree, and both must include the interactive page's `.js` and `.css` - a change to
    either is run by the browser test, and before this both said "nothing changed"."""
    from l7r.diagram.ci.delta import is_engine

    gs = _gate_stamp()
    files = [str(f) for f in gs._area_files(REPO, *gs.AREAS["diagram"])]
    assets = sorted(f.rsplit("/", 1)[1] for f in files if "/interactive/assets/" in f)
    assert assets == ["page.css", "page.js"], assets
    for name in assets:
        assert is_engine(".claude/skills/diagram/l7r/diagram/interactive/assets/" + name), name
