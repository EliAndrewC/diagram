"""Feature 328's ranking holds every finding of the audit once, tiered (spec FR-001, SC-001).

The audit read `make claims-report` at `a52ff1bcd` (snapshot: `specs/328-match-the-research/findings.json`) and ranked each
finding by the implementation work it takes (tiers E0-E4, spec FR-003) into `ranking.json`; `ranking.md` is the readable
table of the same rows. A finding a wave's re-check exposed joins with a `found` field (spec Edge Cases). A finding
missing, doubled or untiered would drop out of the GM's easiest-first order unseen.

Data-file test: it re-runs under testmon only when this file changes, and always at the gate.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[2]
FEATURE = REPO / "specs" / "328-match-the-research"
TIERS = ("E0", "E1", "E2", "E3", "E4")


def _load(name: str) -> list[dict]:
    return json.loads((FEATURE / name).read_text())


def ranking_problems(findings: list[dict], ranking: list[dict], table: str) -> list[str]:
    """Every way the ranking fails to hold the findings once each, tiered, fixed and in the readable table."""
    problems = []
    keys = Counter(r["key"] for r in ranking)
    problems += [f"doubled: {k}" for k, n in keys.items() if n > 1]
    problems += [f"missing: {f['key']}" for f in findings if f["key"] not in keys]
    known = {f["key"] for f in findings} | {r["key"] for r in ranking if r.get("found")}
    problems += [f"not a finding of the audit: {k}" for k in keys if k not in known]
    for r in ranking:
        if r.get("tier") not in TIERS:
            problems.append(f"no tier: {r['key']}")
        if not str(r.get("fix") or "").strip():
            problems.append(f"no fix: {r['key']}")
        if f"`{r['key']}`" not in table:
            problems.append(f"not in ranking.md: {r['key']}")
    order = [TIERS.index(r["tier"]) for r in ranking if r.get("tier") in TIERS]
    if order != sorted(order):
        problems.append("ranking.json is not in tier order")
    return problems


def test_the_ranking_holds_every_finding_once_tiered() -> None:
    problems = ranking_problems(_load("findings.json"), _load("ranking.json"), (FEATURE / "ranking.md").read_text())
    assert not problems, "\n".join(problems[:20])


def test_a_missing_a_doubled_and_an_untiered_row_are_each_caught() -> None:
    findings = [{"key": "a"}, {"key": "b"}, {"key": "c"}]
    ranking = [
        {"key": "a", "tier": "E1", "fix": "x"},
        {"key": "a", "tier": "E1", "fix": "x"},
        {"key": "c", "tier": "E9", "fix": ""},
        {"key": "z", "tier": "E0", "fix": "y"},
    ]
    problems = ranking_problems(findings, ranking, "`a` `c`")
    assert "doubled: a" in problems
    assert "missing: b" in problems
    assert "no tier: c" in problems and "no fix: c" in problems
    assert "not a finding of the audit: z" in problems
    assert "not in ranking.md: z" in problems
    assert "ranking.json is not in tier order" in problems
