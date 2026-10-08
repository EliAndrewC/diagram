"""A glossary term marked `"cased"` matches only as written (feature 265 FR-003)."""

from __future__ import annotations


def test_a_cased_glossary_term_matches_only_as_written() -> None:
    """Feature 265 (FR-003): `ochiba`, the fallen leaves, fired on Ochiba, the manor of that name. A term marked
    `"cased"` matches only as written - on the modal (`glossary_for`) and in the record's derived asset, which carries
    the flag for `record.js` and `page.js`; an uncased term still matches in any case."""
    from l7r.diagram.interactive.glossary import CASED, record_glossary_js
    from l7r.diagram.interactive.page import glossary_for

    assert "ochiba" in CASED

    def terms(text: str) -> set[str]:
        return {e["term"] for e in glossary_for({"a": {"what": text}})}

    assert "ochiba" not in terms("The manor of Ochiba keeps its wall."), "the manor's name is not the word"
    got = [e for e in glossary_for({"a": {"what": "The ochiba is raked in autumn."}}) if e["term"] == "ochiba"]
    assert got and got[0]["cased"] is True, "the lowercase word is, and the page is told the term is cased"
    assert "tsubo" in terms("Counted in TSUBO."), "an uncased term matches in any case"
    js = record_glossary_js()
    assert js.count('"cased": true') == len(CASED), "the record's asset carries the flag on the cased terms alone"
