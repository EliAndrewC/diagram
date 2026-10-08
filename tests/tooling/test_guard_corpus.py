"""The refusal corpus replays through the guards' decision functions (feature 212, FR-007).

`scripts/fixtures/guard-refusals-2026-09.json` is every make-only, pair, no-poll and clone-sync
refusal recovered from the Claude Code transcripts between 2026-08-25 and 2026-09-07, each with the
verdict this feature expects of it - `rewrite` with the exact command, `permit`, `refuse` with the
token that stops it, or `other` for a row the guard no longer reaches. The make-only and no-poll rows
are replayed here through `_hm_make.py` and `_hm_shape.py`; a verdict that moves fails, which is what
keeps a later change to a matcher from quietly un-converting a shape. The pair and clone-sync rows are
replayed by their shell suites, which own the state those decisions read (`scripts/test-pair-hooks.sh`,
`scripts/test-clone-sync-hooks.sh`); here they are only counted, so the census in the feature's
research stays derivable from the fixture.
"""

from __future__ import annotations

import collections
import importlib.util
import json
import pathlib
import sys
from typing import Any

import pytest

SKILL = pathlib.Path(__file__).resolve().parents[2]
REPO = SKILL.parents[2]
SCRIPTS = REPO / "scripts"
FIXTURE = SCRIPTS / "fixtures" / "guard-refusals-2026-09.json"


def _leaf(name: str) -> Any:
    sys.path.insert(0, str(SCRIPTS))
    spec = importlib.util.spec_from_file_location(f"{name}_212", SCRIPTS / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


ROWS: list[dict[str, Any]] = json.loads(FIXTURE.read_text())
MAKE_ONLY = [r for r in ROWS if r["guard"] == "make-only" and r["command"]]
NO_POLL = [r for r in ROWS if r["guard"] == "no-poll" and r["command"]]


def test_the_fixture_is_the_census_the_research_quotes() -> None:
    by = collections.Counter(r["guard"] for r in ROWS)
    assert by == {"make-only": 97, "no-poll": 44, "pair": 26, "clone-sync": 16}, by
    verdicts = collections.Counter((r["guard"], r["expect"]["verdict"]) for r in ROWS)
    # the numbers research R1/R2 state, derived rather than remembered
    assert verdicts[("make-only", "rewrite")] == 14  # 11 targeted pytest runs + 3 wrapped entry points
    assert verdicts[("clone-sync", "permit")] == 13  # every stale-head refusal, synced in
    assert verdicts[("pair", "permit")] == 23  # 21 Bash gate shapes + 2 agent mentions
    assert verdicts[("no-poll", "permit")] == 7  # the backgrounded waits the qualifier had refused


@pytest.mark.parametrize("row", MAKE_ONLY, ids=[r["when"] for r in MAKE_ONLY])
def test_a_make_only_row_gets_the_verdict_the_feature_recorded(row: dict[str, Any]) -> None:
    hm = _leaf("_hm_make")
    cmd = row["command"]
    verdict = hm.classify(cmd)
    want = row["expect"]
    if verdict == "bare-pytest":
        got = hm.as_make_target(cmd)
    elif verdict == "engine-entry-point":
        got = hm.as_wrapped_target(cmd, str(SKILL))
    elif verdict == "ok":
        assert want["verdict"] == "permit"
        return
    else:
        assert want["verdict"] == "refuse" and want["because"] == verdict
        return
    if want["verdict"] == "rewrite":
        assert got == want["command"]
    else:
        assert got is None, f"a shape recorded as refused now rewrites to {got!r}"
        why = hm.why_not_make_target(cmd) if verdict == "bare-pytest" else hm.why_not_wrapped_target(cmd, str(SKILL))
        assert why.startswith(want["because"][:40])


@pytest.mark.parametrize("row", NO_POLL, ids=[r["when"] for r in NO_POLL])
def test_a_no_poll_row_gets_the_verdict_the_feature_recorded(row: dict[str, Any]) -> None:
    shape = _leaf("_hm_shape")
    want = row["expect"]["verdict"]
    if want == "other":
        return  # not a loop with a sleep once heredocs and quotes are blanked; the busy-wait branch never reaches it
    qualifies = shape.file_watching_loop(row["command"])
    if want in ("permit", "rewrite"):
        assert qualifies, "a wait the feature recorded as the permitted file-watching shape no longer qualifies"
        assert shape.file_watching_wait({"tool_input": {"command": row["command"], "run_in_background": True}})
    else:
        assert not qualifies, "a wait recorded as refused (a process, a pid list, a network call) now qualifies"
