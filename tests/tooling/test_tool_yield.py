"""`scripts/measure/tool_yield.py` - every tool measured: its uses, its interventions, its misfires (feature 406 T04, D161-D166).

The GM, 2026-10-19: "Whether or not it's doing something for us should be a measurable question ... in cases where a tool is
too new to have gathered measurements, then that's fine, but there should at least be a way that it is notionally possible for
us to see how often a tool is used, right? Or how often it makes a difference". Each reader below is pinned on a small record
of its own, so dropping any one of them turns its test red.
"""

from __future__ import annotations

import datetime
import json
import pathlib
import sys

REPO = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts" / "measure"))
import tool_yield as ty  # noqa: E402

T0 = datetime.datetime(2026, 10, 1, tzinfo=datetime.UTC).timestamp()


def _iso(t: float) -> str:
    return datetime.datetime.fromtimestamp(t, datetime.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def test_guard_firings_count_hits_and_escapes() -> None:
    t: dict = {}
    ty.tally_guards(
        t,
        [
            {"guard": "plan-hold", "utc": _iso(T0), "event": "blocked"},
            {"guard": "plan-hold", "utc": _iso(T0 + 60), "event": "rewrote"},
            {"guard": "plan-hold", "utc": _iso(T0 + 120), "event": "escaped"},
            {"guard": "plan-hold", "utc": _iso(T0 + 180), "event": "allowed"},
        ],
    )
    g = t[("guard", "plan-hold")]
    assert (len(g.uses), g.hits, g.misses, g.first) == (4, 2, 1, T0)


def test_usage_log_counts_refusals_and_returns_its_start() -> None:
    t: dict = {}
    began = ty.tally_usage(
        t,
        [
            {"utc": _iso(T0 + 10), "tool": "approach_gate", "kind": "check", "outcome": "passed"},
            {"utc": _iso(T0), "tool": "approach_gate", "kind": "check", "outcome": "refused"},
            {"utc": _iso(T0 + 20), "tool": "checks", "kind": "hook", "outcome": "changed"},
        ],
    )
    assert began == T0
    assert (len(t[("check", "approach_gate")].uses), t[("check", "approach_gate")].hits) == (2, 1)
    assert t[("guard", "checks")].hits == 1  # a hook's own record lands with the guards


def test_event_log_targets_before_usage_and_failures_by_call_id() -> None:
    t: dict = {}
    rows = [
        {"ev": "PreToolUse", "id": "a", "make": "quick", "t": _iso(T0)},
        {"ev": "PostToolUse", "id": "a", "make": "quick", "t": _iso(T0 + 5)},
        {"ev": "PreToolUse", "id": "b", "make": "quick", "t": _iso(T0 + 10)},
        {"ev": "PostToolUseFailure", "id": "b", "make": "quick", "t": _iso(T0 + 15)},
        {"ev": "PreToolUse", "id": "c", "make": "quick", "t": _iso(T0 + 3600)},
        {"ev": "PostToolUse", "id": "c", "make": "quick", "t": _iso(T0 + 3605)},
        {"ev": "SubagentStart", "agent": "spec-fidelity", "t": _iso(T0 + 20)},
    ]
    t[("target", "quick")] = ty.Tally("target", "quick")
    t[("target", "quick")].uses += [T0 + 3600, T0 + 7200]  # the usage log's two runs after it began
    ty.tally_events(t, rows, usage_began=T0 + 1800)
    q = t[("target", "quick")]
    assert len(q.uses) == 4  # two from the event log before the usage log began, two from the usage log
    assert q.hits == 1  # call b failed
    assert q.unseen == 1  # the usage log's second run has no session event
    assert len(t[("review", "spec-fidelity")].uses) == 1


def test_ledger_findings_and_declines_from_the_first_use() -> None:
    t: dict = {("review", "quote-check"): ty.Tally("review", "quote-check")}
    t[("review", "quote-check")].use(T0)
    held = ty.tally_ledger(
        t,
        [
            ("2026-09-01", "quote-check", "3 findings", "", ""),  # before its first dispatch: not counted
            ("2026-10-01", "quote-check", "2 findings", "", "declined"),
            ("2026-10-02", "quote-check", "CLEAN", "", ""),
            ("2026-10-03", "quote-check", "findings", "MISSED-BY-REVIEWER", ""),
        ],
    )
    q = t[("review", "quote-check")]
    assert held == {"quote-check"}
    assert (q.hits, q.misses) == (2, 2)


def test_arbiter_rulings_are_its_outcomes(tmp_path: pathlib.Path) -> None:
    (tmp_path / "specs" / "900-x").mkdir(parents=True)
    (tmp_path / "specs" / "900-x" / "arbiter.jsonl").write_text(
        "\n".join(
            json.dumps(r)
            for r in [
                {"utc": _iso(T0), "ruling": "continue"},
                {"utc": _iso(T0), "ruling": "process-fault"},
                {"utc": _iso(T0), "ruling": "continue", "tooling_fix": "a hook"},
            ]
        )
        + "\n"
    )
    t: dict = {}
    assert ty.tally_arbiter(t, tmp_path)
    assert t[("review", "round-arbiter")].hits == 2


def test_bypass_counts_from_the_first_use(tmp_path: pathlib.Path) -> None:
    (tmp_path / "dev" / "bypass-log" / "x").mkdir(parents=True)
    for i, when in enumerate((T0 - 86400, T0 + 60)):
        (tmp_path / "dev" / "bypass-log" / "x" / f"{i}.json").write_text(json.dumps({"target": "done FULL=1", "utc": _iso(when)}))
    t: dict = {("target", "done"): ty.Tally("target", "done")}
    t[("target", "done")].use(T0)
    ty.tally_bypass(t, tmp_path)
    assert t[("target", "done")].misses == 1


def test_reached_follows_prerequisites_and_sub_makes() -> None:
    make = "done: lint\n\t$(MAKE) cohort-landing\nlint:\n\t@python3 scripts/gates/x.py\ncohort-landing:\n\t@true\nquick:\n\t@true\ntick:\n\t@true\nlost:\n\t@true\n"
    assert ty.reached(make) == {"done", "lint", "cohort-landing", "quick", "tick"}


def test_the_report_notes_too_new_and_no_outcome_record() -> None:
    now = T0 + 30 * 86400
    new = ty.Tally("check", "fresh")
    new.use(now - 86400)
    silent = ty.Tally("check", "silent", outcome_record=False)
    old = ty.Tally("review", "seasoned", hits=3)
    old.use(T0)
    text = ty.table({("check", "fresh"): new, ("check", "silent"): silent, ("review", "seasoned"): old}, now=now)
    assert "| fresh |" in text and "too new |" in text
    assert "| silent |" in text and "no outcome record |" in text
    assert "| review | seasoned | 2026-10-01 | 0 | 1 | 3 | 0 |  |" in text
    assert "What this report still cannot see:" in text


def test_the_live_inventory_lists_every_kind() -> None:
    t = ty.collect(REPO, guard_log=REPO / "nonexistent-guard-log")
    kinds = {k for k, _ in t}
    assert {"guard", "check", "target", "review"} <= kinds
    assert ("target", "tool-yield") in t and ("review", "round-arbiter") in t and ("check", "speckit-todo") in t
