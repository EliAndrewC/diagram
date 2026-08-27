"""A ticked `research: physical` task carries three ticked research boxes (constitution v2.12.0, GM 2026-08-27).

THE REQUIREMENT IS A SHAPE, NOT A MEMORY. *"anytime we have a documented requirement that requires
that we remember to do something, then there is always a chance that it will be skipped."* So every
spec-kit task entry says `research: rendering | physical | procedure`, and a `physical` task - one
about how a place was built, farmed, planted, bounded or lived in - carries three sub-boxes:
`research pass`, `source-reader confirmed`, `recorded and cited`. This test reads every
`specs/*/tasks.md` and fails the gate when a task marked `[x]` and `research: physical` has any of
the three boxes unticked or missing. Entries without a `research:` line are older than the rule and
are not judged; the rule binds from the day it was made.

Data-file test: it re-runs under testmon only when this file changes, and always at the gate.
"""

from __future__ import annotations

import re
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
REPO = SKILL.parents[2]
BOXES = ("research pass", "source-reader confirmed", "recorded and cited")

_TASK = re.compile(r"^- \[(?P<tick>[ x])\] (?P<id>T\d+)\b", re.M)


def _entries(text: str) -> list[tuple[str, bool, str]]:
    """(task id, ticked, the entry's body up to the next task or heading)."""
    out = []
    starts = list(_TASK.finditer(text))
    for k, m in enumerate(starts):
        end = starts[k + 1].start() if k + 1 < len(starts) else len(text)
        body = text[m.start() : end]
        head = re.search(r"^## ", body[1:], re.M)
        if head:
            body = body[: head.start() + 1]
        out.append((m.group("id"), m.group("tick") == "x", body))
    return out


def research_box_violations(text: str) -> list[str]:
    """Every ticked `research: physical` task whose three boxes are not all ticked."""
    bad = []
    for tid, ticked, body in _entries(text):
        kind = re.search(r"^\s+research:\s*(\w+)", body, re.M)
        if not kind or kind.group(1) != "physical" or not ticked:
            continue
        for box in BOXES:
            if not re.search(r"- \[x\] " + re.escape(box), body):
                bad.append(f"{tid}: `{box}` not ticked")
    return bad


def test_every_ticked_physical_task_has_its_three_research_boxes_ticked() -> None:
    files = sorted(REPO.glob("specs/*/tasks.md"))
    assert files, "no specs/*/tasks.md found - the repo root resolved wrong"
    bad = [f"{f.relative_to(REPO)} {v}" for f in files for v in research_box_violations(f.read_text())]
    assert not bad, "a ticked physical task owes its research boxes (constitution v2.12.0):\n  " + "\n  ".join(bad)


def test_the_rule_fires_on_a_ticked_physical_task_with_an_open_box() -> None:
    text = "- [x] T01 **x**\n      research: physical\n      - [x] research pass  - [ ] source-reader confirmed  - [x] recorded and cited\n"
    assert research_box_violations(text) == ["T01: `source-reader confirmed` not ticked"]
    assert research_box_violations(text.replace("[ ] source", "[x] source")) == []
    assert research_box_violations(text.replace("- [x] T01", "- [ ] T01")) == [], "an OPEN task may still owe its boxes"
    assert research_box_violations(text.replace("physical", "rendering").replace("- [x] research pass  - [ ] source-reader confirmed  - [x] recorded and cited", "")) == []
