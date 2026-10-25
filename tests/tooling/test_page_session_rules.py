"""`scripts/container/page-session-rules.md` against the root CLAUDE.md (feature 274 D6, FR-003).

WHY. A headless page session starts WITHOUT the clone's root CLAUDE.md (about 5,200 tokens a turn, research R1) and
carries the slim file in its place, so a rule added to CLAUDE.md later would silently never reach a research session.
This test maps EVERY bullet of the root CLAUDE.md's `### House style` and `### Research` sections, by its opening
words, to the phrase in the slim file that carries it - or to a stated reason it is not for page sessions. A bullet it
does not know, or a known one gone, fails until the table (and the slim file) is brought in step.
"""

from __future__ import annotations

import pathlib
import re

from tests._scripts import script

REPO = pathlib.Path(__file__).resolve().parents[2]
SLIM = script("page-session-rules.md")

# opening words of the CLAUDE.md bullet -> the phrase in the slim file that carries it (or NOT: <why not>)
# the research bullets were cut to one line each on 2026-10-17 (feature 383 amendment 6, plan D44); the keys follow them
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
        "The ARCHIVE before the web": "make archive-find URL=<u>",
        "Geography resolves China first": "Geography resolves China first",
        "Several attested forms are a KNOB": "KNOB rolled per settlement",
        "Every rendering decision is labeled": "four classes",
        "Record the why of every research-driven rule": "Record the why of every research-driven rule",
        "A citation quotes the passage verbatim": "quoting the passage verbatim",
        "The record is HTML fragments": "Never edit a built page",
        "Reading and checking go to agents": "run the mechanical pre-pass",  # the BUNDLE rule joined this bullet (slim: "Checks read BUNDLES")
        "A research page is worked in two fresh sessions": "at most four questions",
        "A `research record` feature closes only": "NOT: feature 378's implementation check is owed by the session that closes the feature, never by a page session",
        "**Room before packing**": "NOT: a rule for the engine's placement work (the GM, 2026-10-12), which a page session never does",
        "Whether a finding APPLIES to a case": "NOT: a rule for what reaches the GM (escalation-check), and a page session asks him nothing",
        "A `GUESS`, `UNRESEARCHED` or `CONVENTION` value": "NOT: a rule for the engine's fixing work (feature 417 T28), which a page session never does",
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
    for phrase in (
        "make lines FILE=",
        "make append FILE=",
        "at most four questions",
        "ten new registry keys",
        "$L7R_CONTINUE",
        "make source-outcome",
        "rejected` for the same question",
    ):  # feature 288: the ledger's two rules
        assert phrase in slim, phrase
