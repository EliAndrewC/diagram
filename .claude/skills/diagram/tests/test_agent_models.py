"""Every subagent check runs on the tier recorded for it: a model AND an effort, pinned in its file.

THE RULING (GM 2026-09-19, feature 251). Judgment stays on Opus; a check that is verification and whose
cost is the pages it reads may run on Sonnet; what is purely mechanical is a script and runs on no model
(`make quote-verbatim`, `make record-prepass`, `make size-table`). Each tier below was the GM-approved
proposal's, and each DOWNGRADE in it was proven on artifacts with known findings before it stood
(`specs/251-tiered-subagent-checks/research.md` R5).

WHAT NEVER CHANGES. Nothing is inherited. An agent file with no `model:` runs on the SESSION's model,
which is how nineteen settlement reviews ran on Fable while that file said `inherit` (research R1), and a
file with no `effort:` runs at the session's effort (R6). So both keys are owed by every file, and this
test derives the roster from the directory: a new agent owes its tier here the day it lands.

TO CHANGE A TIER: change the row here and the frontmatter together, and record why - for a downgrade,
the seeded-fault run that justifies it.
"""

from __future__ import annotations

import pathlib
import re

AGENTS = pathlib.Path(__file__).resolve().parents[4] / ".claude" / "agents"

MODELS = ("opus", "sonnet")
EFFORTS = ("low", "medium", "high", "xhigh", "max")

#: agent -> (model, effort)
TIERS: dict[str, tuple[str, str]] = {
    "record-format": ("sonnet", "medium"),
    "source-reader": ("sonnet", "high"),
    "quote-check": ("opus", "medium"),
    "entry-drift": ("opus", "medium"),
    "escalation-check": ("opus", "medium"),
    "spec-fidelity-verify": ("opus", "medium"),
    "spec-fidelity": ("opus", "high"),
    "source-applicability": ("opus", "high"),
    "size-audit": ("opus", "high"),
    "building-review": ("opus", "high"),
    "settlement-review": ("opus", "high"),
    "perf-audit": ("opus", "high"),
}


def frontmatter(text: str) -> dict[str, str]:
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    assert m, "no YAML frontmatter"
    return {k.strip(): v.strip() for k, v in (line.split(":", 1) for line in m.group(1).splitlines() if ":" in line)}


def _pinned() -> dict[str, dict[str, str]]:
    return {p.stem: frontmatter(p.read_text(encoding="utf-8")) for p in sorted(AGENTS.glob("*.md"))}


def test_the_agents_directory_was_found() -> None:
    assert len(_pinned()) >= 11, "non-vacuity: the roster is derived from the directory"


def test_every_agent_file_has_a_tier_and_every_tier_has_a_file() -> None:
    files, table = set(_pinned()), set(TIERS)
    assert not files - table, f"agent files with no recorded tier - add a row to TIERS: {sorted(files - table)}"
    assert not table - files, f"tiers recorded for agents that do not exist: {sorted(table - files)}"


def test_no_agent_inherits_its_model() -> None:
    wrong = {a: fm.get("model", "<missing>") for a, fm in _pinned().items() if fm.get("model") not in MODELS}
    assert not wrong, f"a check runs on opus or sonnet, pinned - never inherit, never absent, never fable: {wrong}"


def test_no_agent_inherits_its_effort() -> None:
    wrong = {a: fm.get("effort", "<missing>") for a, fm in _pinned().items() if fm.get("effort") not in EFFORTS}
    assert not wrong, f"a check pins its effort ({', '.join(EFFORTS)}) - an absent one is the session's: {wrong}"


def test_every_agent_file_agrees_with_the_tier_table() -> None:
    pinned = _pinned()
    wrong = {a: (pinned[a].get("model"), pinned[a].get("effort")) for a in TIERS if a in pinned and (pinned[a].get("model"), pinned[a].get("effort")) != TIERS[a]}
    assert not wrong, f"frontmatter disagrees with TIERS (file says -> table says): { {a: (v, TIERS[a]) for a, v in wrong.items()} }"


def test_the_tier_table_itself_is_well_formed() -> None:
    assert all(m in MODELS and e in EFFORTS for m, e in TIERS.values())


def test_frontmatter_reads_both_keys_and_refuses_a_file_without_any() -> None:
    assert frontmatter("---\nname: x\nmodel: opus\neffort: high\n---\nbody") == {"name": "x", "model": "opus", "effort": "high"}
    try:
        frontmatter("no frontmatter here")
    except AssertionError:
        return
    raise AssertionError("a file with no frontmatter must fail")  # pragma: no cover
