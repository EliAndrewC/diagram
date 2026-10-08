"""The settlement-review agent's first stage and verdict record, found in its own file (feature 240, SC-006).

An agent file is prose, so what a test can prove is that the contract is WRITTEN where the agent reads it, in
the order it must run, and that every command it names exists. Whether an agent obeys is the hook's half
(`scripts/hooks/pair-hooks.sh`) and the verdict writer's (`make review-verdict` re-reads the gate itself) - D2: each
layer the other's backstop.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]
AGENT = (ROOT / ".claude" / "agents" / "settlement-review.md").read_text(encoding="utf-8")
MAKEFILE = (ROOT / "Makefile").read_text(encoding="utf-8")


FIX_CHECK = (ROOT / ".claude" / "agents" / "fix-check.md").read_text(encoding="utf-8")
GLYPH_CHECK = (ROOT / ".claude" / "agents" / "glyph-check.md").read_text(encoding="utf-8")
#: The review checks that write a verdict record (feature 294 split the old settlement-review into these three).
CHECKS = {"settlement-review": AGENT, "fix-check": FIX_CHECK, "glyph-check": GLYPH_CHECK}


def _section(heading: str, text: str = AGENT, name: str = "settlement-review") -> str:
    m = re.search(rf"^## {re.escape(heading)}.*?(?=^## )", text, re.S | re.M)
    assert m, f"{name}.md has no '## {heading}' section"
    return m.group(0)


def test_the_first_stage_runs_before_any_map_is_read() -> None:
    for name, text in CHECKS.items():
        first = text.index("## First stage")
        assert first < text.index("## Output"), name
        if "## Inputs" in text:
            assert first < text.index("## Inputs"), name


def test_the_first_stage_reads_the_paired_gate_and_again_before_the_verdict() -> None:
    """Feature 294 dispatches a check only on a GREEN gate (US6), so the stage reads it once and again before the verdict."""
    for name, text in CHECKS.items():
        stage = _section("First stage", text, name)
        assert "make review-paired-gate" in stage and "`green`" in stage and "NOT-REVIEWABLE" in stage, name
        assert "immediately before" in stage, name


def test_the_fix_check_judges_a_records_source_with_the_canopy_as_its_worked_example() -> None:
    """Feature 240's worked example moved with the question it answers: did a fix's record read the thing complained of."""
    judged = _section("What you judge", FIX_CHECK, "fix-check")
    for token in ("proxy", "`source`", "CROWNS", "16.3 ft", "R2"):
        assert token in judged, token


def test_the_reviewer_keeps_the_right_to_measure_independently() -> None:
    assert "right to measure independently" in _section("First stage")


def test_the_verdict_record_is_the_last_act_and_both_commands_exist() -> None:
    for name, text in CHECKS.items():
        out = text[text.index("## Output") :]
        assert "make review-verdict UNIT=" in out, name
    assert "last act" in AGENT[AGENT.index("## Output") :].lower()
    for target in ("review-paired-gate", "review-verdict"):
        assert re.search(rf"^{target}:", MAKEFILE, re.M), target


PERF_AUDIT = (ROOT / ".claude" / "agents" / "perf-audit.md").read_text(encoding="utf-8")


def test_the_perf_audit_first_stage_exits_on_a_missing_control_and_runs_the_counterfactual_on_unverified() -> None:
    """SC-008's agent half: the first stage precedes the bands and names both exits."""
    m = re.search(r"^## FIRST STAGE.*?(?=^## )", PERF_AUDIT, re.S | re.M)
    assert m and PERF_AUDIT.index("## FIRST STAGE") < PERF_AUDIT.index("## Band 1")
    stage = m.group(0)
    recipe = re.search(r"^perf-explain:.*?(?=^perf-confirm:)", MAKEFILE, re.S | re.M)
    assert recipe and '--control "$(CONTROL)" --unverified "$(UNVERIFIED)"' in recipe.group(0)
    assert '$(if $(UNVERIFIED),&& $(LOGBYPASS) permitted "perf-explain UNVERIFIED: $(UNVERIFIED)",)' in recipe.group(0), "SC-008: an UNVERIFIED reason is logged where make audit lists it"
    for token in ("`control`", "names no\n  record", "`unverified`", "run the counterfactual\n  yourself, before any other work", "NOT-REVIEWABLE", "4.70 s", "R2"):
        assert token in stage, token
