"""Feature 319: the About form of a modal - `About:` paragraphs and a `Guesses:` list, no feature-level label.

The guidelines are `dev/modals.md`: a guess is a property of one statement, a bullet on the Guesses tab, never the
modal's opening (M11); the About tab answers its kind's questions in short paragraphs (M2)."""

from __future__ import annotations

import pytest

from l7r.diagram.interactive.classes import FeatureClass, Kind, parse_explanation
from l7r.diagram.interactive.classes._base import about_paragraphs, guess_bullets

_DATA = "Name: the probe\nCovers: nothing\nSources: not recorded\nEntry: research/none.md\n"


def _probe(doc: str) -> type[Kind]:
    return type("Probe", (Kind,), {"__doc__": doc, "key": "probe"})


def test_about_keeps_its_paragraph_breaks_and_joins_wrapped_lines() -> None:
    doc = """
    About: A house, and
    more house.

    It had a roof.

    Guesses:
    - its size, 40 by 20
      ft: no record.
    - its color.

    Name: x
    """
    got = parse_explanation(doc, "X")
    assert got["About"] == "A house, and more house.\n\nIt had a roof."
    assert got["Guesses"] == "- its size, 40 by 20 ft: no record.\n- its color."


def test_the_paragraphs_and_the_bullets_are_read_out() -> None:
    assert about_paragraphs("One.\n\nTwo, and\nmore.") == ("One.", "Two, and more.")
    assert guess_bullets("- a\n- b, c") == ("a", "b, c")
    assert guess_bullets("") == ()


def test_a_kind_in_the_about_form_builds_its_feature_class_with_no_label() -> None:
    Probe = _probe("About: What it was.\n\nWhat it looked like.\n\nGuesses:\n- its size.\n\n" + _DATA)
    try:
        fc = Probe.feature()
        assert isinstance(fc, FeatureClass)
        assert fc.about == ("What it was.", "What it looked like.") and fc.guesses == ("its size.",)
        assert fc.label is None and fc.form == "standard", "the classification is per statement in the About form (M11-M13)"
        assert fc.what == "" and fc.why == "" and fc.label_note == "" and fc.caveat == ""
    finally:
        Kind.registry.remove(Probe)


def test_the_guesses_are_optional_and_the_form_may_be_particular() -> None:
    Probe = _probe("About: A stone painted vermilion.\n\nForm: particular\n" + _DATA)
    try:
        fc = Probe.feature()
        assert fc.guesses == () and fc.form == "particular"
    finally:
        Kind.registry.remove(Probe)


@pytest.mark.parametrize(
    ("extra", "why"),
    [
        ("Label: guess\n", "no Label:"),
        ("Why: b.\n", "What/Why/Note/Caveat"),
        ("Note: c.\n", "What/Why/Note/Caveat"),
        ("Form: odd\n", "Form: 'odd'"),
    ],
    ids=["label", "why", "note", "form"],
)
def test_the_about_form_refuses_the_old_tags_and_an_unknown_form(extra: str, why: str) -> None:
    Probe = _probe("About: a.\n\n" + extra + _DATA)
    try:
        with pytest.raises(ValueError, match=why) as e:
            Probe.feature()
        assert "Probe" in str(e.value)
    finally:
        Kind.registry.remove(Probe)


def test_a_guess_that_is_not_a_bullet_is_refused() -> None:
    Probe = _probe("About: a.\n\nGuesses: its size.\n\n" + _DATA)
    try:
        with pytest.raises(ValueError, match="bullet"):
            Probe.feature()
    finally:
        Kind.registry.remove(Probe)
