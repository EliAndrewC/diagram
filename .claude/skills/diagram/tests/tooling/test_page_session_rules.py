"""`container-scripts/page-session-rules.md` against the root CLAUDE.md (feature 274 D6, FR-003).

WHY. A headless page session starts WITHOUT the clone's root CLAUDE.md (about 5,200 tokens a turn, research R1) and
carries the slim file in its place, so a rule added to CLAUDE.md later would silently never reach a research session.
This test maps EVERY bullet of the root CLAUDE.md's `### House style` and `### Research` sections, by its opening
words, to the phrase in the slim file that carries it - or to a stated reason it is not for page sessions. A bullet it
does not know, or a known one gone, fails until the table (and the slim file) is brought in step.
"""

from __future__ import annotations

import pathlib
import re

REPO = pathlib.Path(__file__).resolve().parents[5]
SLIM = REPO / "container-scripts" / "page-session-rules.md"

# opening words of the CLAUDE.md bullet -> the phrase in the slim file that carries it (or NOT: <why not>)
CARRIED = {
    "House style": {
        "Hyphens only": "Hyphens only",
        "American spellings": "American spellings everywhere",
        "Both rules stop at a quotation": "Both rules stop at a quotation",
        '"People" has caste meaning': 'only samurai are "people"',
        '"Domain", never': '"Domain", never',
        "Gender-neutral office-holders": "Gender-neutral office-holders",
        "Kanji in generated content": "kanji - romaji - meaning triangle",
        "Never invent setting details": "Never invent setting details that contradict the GM's notes",
    },
    "Research": {
        "A question about how a place was built": "Search before deciding",
        "Where the research supports more than one form": "KNOB rolled per settlement",
        "Every rendering decision is recorded": "four classes",
        "Record the why of every research-driven rule": "Record the why of every research-driven rule",
        "A citation is a footnote at the assertion": "quoting the passage verbatim",
        "The record is HTML under": "Never edit an assembled page",
        "Reading and checking are dispatched to agents": "run the mechanical pre-pass",
        "A record check reads a BUNDLE": "Checks read BUNDLES",
    },
}


def bullets(section: str) -> list[str]:
    """The top-level bullets of one `### <section>` of the root CLAUDE.md, each as its first line."""
    text = (REPO / "CLAUDE.md").read_text(encoding="utf-8")
    m = re.search(rf"^### {re.escape(section)}\n(.*?)(?=^#)", text, re.M | re.S)
    assert m, f"no ### {section} in CLAUDE.md"
    return [ln[2:] for ln in m.group(1).splitlines() if ln.startswith("- ")]


def test_every_house_style_and_research_rule_reaches_a_page_session() -> None:
    slim = " ".join(SLIM.read_text(encoding="utf-8").split())
    for section, table in CARRIED.items():
        got = bullets(section)
        unknown = [b[:60] for b in got if not any(b.startswith(k) for k in table)]
        assert not unknown, f"CLAUDE.md's {section} has a bullet this table does not know - carry it into {SLIM.name} or mark it NOT: {unknown}"
        gone = [k for k in table if not any(b.startswith(k) for b in got)]
        assert not gone, f"CLAUDE.md's {section} lost {gone} - take it out of the table (and the slim file, if it went for good)"
        missing = [p for p in table.values() if not p.startswith("NOT:") and p not in slim]
        assert not missing, f"{SLIM.name} no longer carries: {missing}"


def test_the_slim_file_states_the_caps_and_the_line_rule() -> None:
    slim = " ".join(SLIM.read_text(encoding="utf-8").split())
    for phrase in ("make lines FILE=", "make append FILE=", "at most four questions", "ten new registry keys", "$L7R_CONTINUE"):
        assert phrase in slim, phrase
