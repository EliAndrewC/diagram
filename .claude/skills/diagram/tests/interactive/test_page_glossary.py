"""The HTML target's string layer (feature 134): wrapping, the ink census, and the page's contents.

What the browser test cannot cheaply prove per string is proved here: each tag shape wraps the way
`page.wrap` promises (a `Split` becomes a fill-only and a stroke-only copy; `Parts` wrap piece by
piece with the unclassed wrapper tags left bare), the census counts ink and only ink and reports
only what nobody ruled on, and the page embeds only the classes present and only the sibling
paragraphs whose other class is present (spec US4 scenario 4).
"""

from __future__ import annotations

import re

import pytest

from l7r.diagram.interactive.classes import CLASSES
from l7r.diagram.interactive.glossary import GLOSSARY
from l7r.diagram.interactive.page import (
    explanations,
    glossary_for,
)

pytestmark = pytest.mark.renders  # tests OF the page's raster / the plates: they render tiny synthetic pictures on purpose (feature 213)

RECT = '<rect x="1" y="2" width="3" height="4" fill="#abc" stroke="#123"/>'


def test_the_glossary_is_well_formed_and_used() -> None:
    for term, (variants, definition) in GLOSSARY.items():
        assert variants and len(definition) > 30 and "\u2014" not in definition, term
    used = {g["term"] for g in glossary_for(explanations(set(CLASSES)))}
    assert {"bund", "coppice", "iriai", "tameike", "yashikirin", "kosatsuba", "hokora"} <= used
    # Since feature 209 the glossary serves the research record too, so a term no modal uses may still be live:
    # `tests/interactive/test_record_format.py` holds the widened rule (used by a modal OR a record page).
    assert "kainyo" in GLOSSARY and "kainyo" not in used, "a record-only term is in the table and not on the map (non-vacuity of the split)"


def test_glossary_for_defines_tsubo_where_an_explanation_counts_in_it() -> None:
    """Feature 205 (GM 2026-09-07): the word is a tooltip wherever a modal uses it, and nowhere else."""
    counted = {"yard": {"what": "an ordinary yard is 20 to 30 tsubo", "why": "", "on_this_map": ""}}
    entry = [g for g in glossary_for(counted) if g["term"] == "tsubo"]
    assert entry and entry[0]["variants"] == ["tsubo"] and "two straw mats" in entry[0]["def"]
    uncounted = {"yard": {"what": "an ordinary yard is 66 to 99 sq m", "why": "", "on_this_map": ""}}
    assert not [g for g in glossary_for(uncounted) if g["term"] == "tsubo"]


def test_a_term_only_in_the_about_or_guesses_tab_is_still_a_tooltip() -> None:
    """Feature 319 (GM 2026-10-03: "any tooltip'ed thing in the research should be automatically tooltipped in the
    interactive HTML map modals"): the terms a page ships are read from EVERY word a modal shows. The five-key allow
    list this replaced never read the About form's `about` paragraphs or `guesses` bullets, so a term used only there
    shipped no definition and was never wrapped."""
    about = {"yard": {"about": ["Before 1868 a yard was swept daily."], "guesses": ["its size, 20 to 30 tsubo"], "questions": [], "siblings": []}}
    terms = {g["term"] for g in glossary_for(about)}
    assert {"1868", "tsubo"} <= terms, terms


def test_every_key_a_modal_carries_is_scanned_for_terms_or_ruled_not_rendered() -> None:
    """The deny list is the rule: a key added to a modal's data is scanned unless it is named in `NOT_RENDERED`, and the
    named ones exist (so a renamed key cannot leave a dead exemption behind)."""
    from l7r.diagram.interactive.page import NOT_RENDERED, rendered_text

    data = explanations(set(CLASSES))
    keys = {k for d in data.values() for k in d}
    assert keys >= NOT_RENDERED, NOT_RENDERED - keys
    assert {"about", "guesses", "depiction", "on_this_map"} <= keys - NOT_RENDERED
    farmhouse = rendered_text(data["farmhouse"])
    assert CLASSES["farmhouse"].about[0] in farmhouse and "farmhouses-minka" not in farmhouse, "the paragraphs, not the links"


def test_glossary_for_with_the_substring_prefilter_is_the_regex_scan() -> None:
    """Feature 224: a variant absent as a substring cannot match with word boundaries, so the `in` test first changes
    no term - checked against the pure regex form over the real GLOSSARY on a text that holds some variants whole,
    one only inside a longer word (not a match either way), and one split across a boundary."""
    from l7r.diagram.interactive.glossary import GLOSSARY
    from l7r.diagram.interactive.page import glossary_for

    terms = list(GLOSSARY.items())
    whole = [v for _t, (vs, _d) in terms[:6] for v in vs][:6]
    inside = [v for _t, (vs, _d) in terms[6:9] for v in vs][:2]
    text = " ".join(whole) + " " + " ".join(f"x{v}y" for v in inside) + " sluice-gate paddy"
    data = {"a": {"what": text, "why": "", "on_this_map": ""}}
    got = {e["term"] for e in glossary_for(data)}
    low = text.lower()
    want = {t for t, (vs, _d) in terms if any(re.search(r"\b" + re.escape(v.lower()) + r"\b", low) for v in vs)}
    assert got == want and got, "the same terms as the regex scan alone"
