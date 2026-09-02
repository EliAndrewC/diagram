"""The operative documents must describe the coverage mechanism the tree ACTUALLY has.

WHY THIS EXISTS, and it is not a style rule. Feature 174 spent SIX consecutive `spec-fidelity`
rounds on one failure: an item settled in the spec while a sentence asserting the old state stood in
a document a session reads before acting. Every round found real instances by hand and every round
missed others. Two of them were not merely stale but ACTIVELY WRONG - `CLAUDE.md` and `settlements.md`
each told a reader the floor is `fail_under = 100` in `[tool.coverage.report]`, and a session acting
on that would put it where `pytest-cov` reads it: the global floor would then fire on every partial
run (`make test-file`, and `make quick`, which the GM exempted) and the deliberate ordering - the
floor runs LAST, so a run's own failures are reported before the coverage table - would be destroyed.

The reviewer proposed this check three times before it was built. Twelve rounds of prose review did
not end the class; the check does, because it asks the CONFIG rather than the prose.

`tooling`, because it reads the repository's own files.
"""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import pytest

pytestmark = pytest.mark.tooling

SKILL = Path(__file__).resolve().parents[2]
ROOT = SKILL.parents[2]

# The files a session reads before it acts. A doc not listed here is free to be a historical record;
# these are the ones that instruct.
OPERATIVE = [
    ROOT / "CLAUDE.md",
    ROOT / ".specify/memory/constitution.md",
    ROOT / ".specify/templates/plan-template.md",
    ROOT / "docs/efficiency-tooling.md",
    SKILL / "CLAUDE.md",
    SKILL / "SKILL.md",
    SKILL / "settlements.md",
    SKILL / "settlements/fields.md",
    SKILL / "tests/CLAUDE.md",
    SKILL / "dev/gate.md",
    SKILL / "migration-plan.md",
]


def _present() -> list[Path]:
    return [p for p in OPERATIVE if p.is_file()]


def test_no_operative_document_names_a_coverage_key_the_config_does_not_set() -> None:
    """`fail_under` is deliberately NOT in `[tool.coverage.report]` - the floor is a command-line flag
    in the Makefile so it runs last and so partial runs do not trip it. A document naming the config
    key is not describing the mechanism, it is prescribing a change that would break it."""
    cfg = tomllib.loads((SKILL / "pyproject.toml").read_text())
    report = cfg.get("tool", {}).get("coverage", {}).get("report", {})
    assert "fail_under" not in report, "the config sets it after all - then this test's premise, and the docs, need revisiting together"

    bad: list[str] = []
    for p in _present():
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines, 1):
            names_it = re.search(r"\[tool\.coverage\.report\][^\n]*fail_under|fail_under[^\n]*\[tool\.coverage\.report\]|`fail_under = 100` in the config", line)
            if not names_it:
                continue
            # A DESCRIPTION is fine and often necessary - "the config deliberately omits it", "do NOT
            # put it there". Only a line PRESCRIBING the key is wrong. The window is +/-2 lines
            # because the negation is regularly on the wrapped line before or after (measured: the
            # constitution's own clause 5 wraps "deliberately omits" onto the next line).
            window = " ".join(lines[max(0, i - 3) : i + 2]).lower()
            if re.search(r"\bnot\b|never|omits|deliberately|used to|no longer|would break|forbid", window):
                continue
            bad.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()[:90]}")
    assert not bad, "these PRESCRIBE a coverage config key that is not set; the floor is `coverage report --fail-under=100` in the skill Makefile:\n  " + "\n  ".join(bad)


def test_the_floor_the_docs_describe_is_the_one_the_makefile_runs() -> None:
    """The positive half: the Makefile really does carry the flag the docs are told to name."""
    mk = (SKILL / "Makefile").read_text()
    assert re.search(r"coverage report -m --fail-under=100", mk), "the mechanism the docs describe must exist"
    floored = next(ln for ln in mk.splitlines() if "--fail-under=100" in ln)
    assert "--omit" not in floored, "and it must still cover the whole tree"


def test_no_engine_module_claims_exemption_from_the_coverage_rule() -> None:
    """GM 2026-09-02: *"a new tool absolutely should silently owe one hundred percent coverage the day
    it lands ... for everything."* Four modules carried such a claim in their own docstrings and the
    first sweep found only three - the fourth said "NOT UNDER THE COVERAGE GATE" where the others said
    "not under the 100% rule", so the grep that found them missed it. This asks for the CLAIM in any
    wording rather than for one phrase."""
    patterns = re.compile(
        r"not under the (100%|coverage)|NOT UNDER THE COVERAGE|outside the coverage gate|"
        r"stays outside the coverage|exempt from the (100%|coverage)|owes no (coverage|tests)",
        re.I,
    )
    bad: list[str] = []
    for p in sorted(SKILL.glob("l7r/**/*.py")):
        lines = p.read_text().splitlines()
        for i, line in enumerate(lines, 1):
            if not patterns.search(line):
                continue
            # the same +/-2 window: a docstring recording that it USED to claim exemption wraps, and
            # the disclaimer is regularly on the line above the quoted claim
            window = " ".join(lines[max(0, i - 3) : i + 2]).lower()
            if re.search(r"used to|no longer|this paragraph|the opposite|was removed|abolished", window):
                continue
            bad.append(f"{p.relative_to(SKILL)}:{i}: {line.strip()[:80]}")
    assert not bad, "an engine module claiming it owes no coverage - the opt-in the GM abolished:\n  " + "\n  ".join(bad)


def test_no_operative_document_says_the_coverage_floors_are_DEFERRED() -> None:
    """The deferral was real until feature 174 and is what the GM's request closed. A document still
    describing it as current sends a session to `make done FULL=1` for a floor a plain `make done`
    now enforces - and, worse, implies a plain gate can go green below it."""
    bad: list[str] = []
    for p in _present():
        for i, line in enumerate(p.read_text().splitlines(), 1):
            # a line that says it USED to be so, or marks it retired, is the record and is fine
            current = re.search(r"floors? (are |is )?deferred|deferred to `make done FULL=1`", line, re.I) and not re.search(
                r"retired|had been|used to|was DEFERRED|is what that feature closed|printed", line, re.I
            )
            if current:
                bad.append(f"{p.relative_to(ROOT)}:{i}: {line.strip()[:90]}")
    assert not bad, "these describe the retired deferral as current:\n  " + "\n  ".join(bad)
