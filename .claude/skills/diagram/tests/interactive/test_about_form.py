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
        assert fc.form == "standard" and not hasattr(fc, "label"), "the classification is per statement in the About form (M11-M13)"
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
        ("What: a.\n", "What/Why/Note/Caveat"),
        ("Caveat: d.\n", "What/Why/Note/Caveat"),
        ("Form: odd\n", "Form: 'odd'"),
    ],
    ids=["label", "why", "note", "what", "caveat", "form"],
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


def test_every_modal_is_its_own_file_and_no_class_carries_its_text() -> None:
    """Plan D12 (GM 2026-10-03): one file per modal under `assets/modals/<hamlet|sheet>/`. Every registered kind has its
    file, no kind's class still carries a tagged docstring (one source for the text), and no file is an orphan."""
    import glob
    import os
    import re

    from l7r.diagram.interactive.classes._base import MODALS_DIR, modal_path
    from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES  # noqa: F401 - registers the sheet kinds

    kinds = [k for k in Kind.registry if k.__module__.startswith(("l7r.diagram.interactive.classes.", "l7r.diagram.interactive.compound_kinds."))]
    assert len(kinds) >= 155
    paths = {modal_path(k.__module__, k.key) for k in kinds}
    assert all(os.path.isfile(p) for p in paths), sorted(p for p in paths if not os.path.isfile(p))
    tagged = [k.__name__ for k in kinds if k.__doc__ and re.search(r"^\s*(What|About|Name):", k.__doc__, re.M)]
    assert tagged == [], f"modal text left in a class docstring: {tagged}"
    # the title card's choice modals (plan D10) have no class: their files are their names, held by test_choices.py
    files = set(glob.glob(os.path.join(MODALS_DIR, "*", "*.md"))) - set(glob.glob(os.path.join(MODALS_DIR, "choice", "*.md")))
    assert files == paths, f"orphan modal files: {sorted(files - paths)}"


@pytest.mark.parametrize("missing", ["Name", "Covers", "Sources", "Entry"])
def test_an_about_form_without_a_data_tag_fails_loudly_naming_the_class(missing: str) -> None:
    """The About form's four data tags are required, as the old form's were (feature 207)."""
    doc = "About: a.\n\n" + "".join(line + "\n" for line in _DATA.splitlines() if not line.startswith(missing + ":"))
    Probe = _probe(doc)
    try:
        with pytest.raises(ValueError, match=f"no {missing}: section") as e:
            Probe.feature()
        assert "Probe" in str(e.value)
    finally:
        Kind.registry.remove(Probe)


def test_the_depiction_tab_has_its_paragraphs_and_its_drawing_pages() -> None:
    """Plan D13 (GM 2026-10-04: "I want 'How we draw it' things on its own tab"): `Depiction:` keeps its paragraphs as About
    does, and `Drawing:` names the "how our maps draw it" pages, which leave `Entry:`."""
    Probe = _probe(
        "About: a.\n\nDepiction: The map draws it bold.\n\nIt was pale.\n\n"
        + _DATA
        + "Drawing: research/questions/0001-x.drawing.html\n"
    )
    try:
        fc = Probe.feature()
        assert fc.depiction == ("The map draws it bold.", "It was pale.") and fc.drawing == "research/questions/0001-x.drawing.html"
    finally:
        Kind.registry.remove(Probe)


def test_a_drawing_page_under_entry_is_refused_with_the_tag_it_belongs_under() -> None:
    Probe = _probe("About: a.\n\n" + _DATA.replace("research/none.md", "research/questions/0001-x.drawing.html"))
    try:
        with pytest.raises(ValueError, match="belongs under Drawing:"):
            Probe.feature()
    finally:
        Kind.registry.remove(Probe)


@pytest.mark.parametrize(
    "said",
    ["Except on the older hand-drawn maps, it is kept", "the hand-drawn maps keep the higher share", "On the legacy maps it is not",
     "the frozen pool draws it", "an earlier hamlet map", "the hand-authored maps"],
)
def test_a_modal_naming_the_older_maps_is_refused_with_the_fix(said: str) -> None:
    """GM 2026-10-04: the older hand-drawn maps will all be scripted before anyone else reads a modal, so no modal mentions
    them - a mechanical check, not an agent's (M21). Each tab is read; the message says what to write instead."""
    for tab in ("About: a.\n\n{}.\n\n", "About: a.\n\nGuesses:\n- {}.\n\n", "About: a.\n\nDepiction: {}.\n\n"):
        Probe = _probe(tab.format(said) + _DATA)
        try:
            with pytest.raises(ValueError, match="names the older maps .* say what the scripted maps do"):
                Probe.feature()
        finally:
            Kind.registry.remove(Probe)


def test_a_sheets_hand_drawn_plans_and_an_old_house_are_not_the_older_maps() -> None:
    """Building plans stay, and "old" alone is history, not the pool: neither is refused."""
    Probe = _probe("About: The hand-drawn plans give it a room; an older house had one; an old map of the county shows it.\n\n" + _DATA)
    try:
        assert Probe.feature().about
    finally:
        Kind.registry.remove(Probe)


def test_a_malformed_knob_condition_is_refused_when_the_modal_is_read() -> None:
    """FR-015: a condition's form is checked at read, so a typo never reaches a reader as text (M22)."""
    Probe = _probe("About: a.\n\nGuesses:\n- [Settlement Form=nucleated] a guess.\n\n" + _DATA)
    try:
        with pytest.raises(ValueError, match=r"written \[knob=value\]"):
            Probe.feature()
    finally:
        Kind.registry.remove(Probe)
