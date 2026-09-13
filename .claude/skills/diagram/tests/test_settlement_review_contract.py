"""The settlement-review agent's first stage and verdict record, found in its own file (feature 240, SC-006).

An agent file is prose, so what a test can prove is that the contract is WRITTEN where the agent reads it, in
the order it must run, and that every command it names exists. Whether an agent obeys is the hook's half
(`scripts/pair-hooks.sh`) and the verdict writer's (`make review-verdict` re-reads the gate itself) - D2: each
layer the other's backstop.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[4]
AGENT = (ROOT / ".claude" / "agents" / "settlement-review.md").read_text(encoding="utf-8")
MAKEFILE = (ROOT / ".claude" / "skills" / "diagram" / "Makefile").read_text(encoding="utf-8")


def _section(heading: str) -> str:
    m = re.search(rf"^## {re.escape(heading)}.*?(?=^## )", AGENT, re.S | re.M)
    assert m, f"settlement-review.md has no '## {heading}' section"
    return m.group(0)


def test_the_first_stage_runs_before_any_map_is_read() -> None:
    assert AGENT.index("## FIRST STAGE") < AGENT.index("## Inputs") < AGENT.index("## Output")


def test_the_first_stage_reads_the_paired_gate_before_the_first_map_between_maps_and_before_the_verdict() -> None:
    stage = _section("FIRST STAGE")
    assert stage.count("make review-paired-gate") >= 2
    assert "Before each further map" in stage and "immediately before you write" in stage
    assert "NOT-REVIEWABLE" in stage and "`red`" in stage


def test_the_first_stage_judges_a_records_source_with_the_canopy_as_its_worked_example() -> None:
    stage = _section("FIRST STAGE")
    for token in ("measurements.json", "`verifies`", "`subject`", "`source`", "review-dispositions", "`clumps`", "`tree_crowns`", "16.3 ft", "R2"):
        assert token in stage, token


def test_the_reviewer_keeps_the_right_to_measure_independently() -> None:
    assert "right to measure independently" in _section("FIRST STAGE")


def test_the_verdict_record_is_the_last_act_and_both_commands_exist() -> None:
    out = _section("Output")
    assert "LAST ACT" in out and "make review-verdict MAP=" in out
    for target in ("review-paired-gate", "review-verdict"):
        assert re.search(rf"^{target}:", MAKEFILE, re.M), target


PERF_AUDIT = (ROOT / ".claude" / "agents" / "perf-audit.md").read_text(encoding="utf-8")


def test_the_perf_audit_first_stage_exits_on_a_missing_control_and_runs_the_counterfactual_on_unverified() -> None:
    """SC-008's agent half: the first stage precedes the bands and names both exits."""
    m = re.search(r"^## FIRST STAGE.*?(?=^## )", PERF_AUDIT, re.S | re.M)
    assert m and PERF_AUDIT.index("## FIRST STAGE") < PERF_AUDIT.index("## Band 1")
    stage = m.group(0)
    for token in ("`control`", "names no\n  record", "`unverified`", "run the counterfactual\n  yourself, before any other work", "NOT-REVIEWABLE", "4.70 s", "R2"):
        assert token in stage, token
