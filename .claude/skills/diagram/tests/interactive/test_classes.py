"""The class registry is complete, closed and symmetric (feature 134, spec FR-007 / FR-008, SC-007).

Every class the spec's table names is here; every entry says what, why, which of the three
constitution-XII labels applies and where the text came from; every sibling names a class in the
table and is named back. The page (`test_page.py`) and the browser test build on this - a registry
hole would surface there as a reader told nothing, which is the failure this file exists to catch
first.
"""

from __future__ import annotations

import re

import pytest

from l7r.diagram.interactive.classes import ANNOUNCED, CLASSES, NOT_HIGHLIGHTED, NOT_HIGHLIGHTED_OVERTURNED, NOT_HIGHLIGHTED_RULINGS, FeatureClass, label_phrase, lead_sentence, slug

# The spec's FR-007 vocabulary, verbatim (plus `field pond`, added at implementation and recorded
# in the spec table). A row added to the spec without an entry here fails this test; an entry here
# the spec does not name fails it too.
SPEC_CLASSES = [
    "farmhouse",
    "storage shed",
    "byre",
    "threshing yard",
    "garden",
    "privy",
    "woodpile",
    "manure heap",
    "bathhouse",
    "hen coop",
    "household shrine",
    "persimmon",
    "homestead bamboo",
    "shared bamboo grove",
    "windbreak",
    "copse",
    "woodland commons",
    "scrub and rough grazing",
    "marsh",
    "paddy",
    # the wettest plots, told apart from the rest of the field (feature 159, GM 2026-08-29:
    # "that is its own type of thing, and it deserves its own explanation") - recorded in that
    # spec's Decisions table like `field pond` and the dike-pond rows
    "wet paddy",
    "bund",
    "bund beans",
    "millet",
    "buckwheat",
    "barley",
    "soy",
    "fallow",
    "stream",
    "field ditch",
    "pond",
    "field pond",
    "field rock",
    "grave island",
    "village lane",
    "footbridge",
    "well",
    "notice board",
    # the dike-pond hamlet (feature 150, Kuwabata), recorded in the spec table like `field pond`
    "fish pond",
    "mulberry dike",
    "pond sluice",
    "perimeter dike",
    "fry pond",
    "manure pit",
    "sluice gate",
    "sugarcane dike",
    "banana dike",
    "fruit dike",
    "vegetable ground",
    "pig sty",
    "duck pen",
]


def test_every_spec_class_is_registered_and_nothing_else() -> None:
    assert sorted(CLASSES) == sorted(SPEC_CLASSES)


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_an_entry_is_complete(key: str) -> None:
    fc: FeatureClass = CLASSES[key]
    assert fc.key == key
    # THE NAME IS THE HEADING, THE KEY IS THE INK. They matched for every class until feature 153, when
    # the GM asked that the windbreak modal "actually say 'Windbreak forest' instead of just 'windbreak'"
    # - and the key cannot follow, because it rides on every drawn element and `all_ink_is_ruled_on`
    # reads it. So the rule is that a heading exists and still names the thing the ink is tagged with,
    # not that the two strings are identical.
    assert fc.name and key in fc.name, "the modal's heading names the class its ink carries"
    assert len(fc.what) > 40 and len(fc.why) > 40, "an explanation is a paragraph, not a label"
    assert fc.label in ("accurate", "deviation", "convention", "guess")
    assert fc.label_note, "the label is justified in one line"
    assert fc.sources and all(fc.sources), "a sources line, or 'not recorded'"
    assert "research/" in fc.entry, "written FROM a research entry"


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_a_guess_says_so_in_its_note(key: str) -> None:
    fc = CLASSES[key]
    if fc.label == "guess":
        assert re.search(r"\bguess", fc.label_note, re.I), "a guess is labeled a guess in its own words"
    if fc.label == "deviation":
        assert re.search(r"deviat|departure|liberty|drawn", fc.label_note, re.I), "a deviation says what deviates"
        assert "legibility" not in fc.label_note.lower(), "legibility is a map drawing CONVENTION, not a deviation (feature 183)"
    if fc.label == "convention":
        # THE GM'S FORM (feature 183): "we have rendered <it> ... in order to ... <the real size or color>" -
        # and where the record was searched and is silent on a figure, the note says so in so many words
        assert re.match(r"we have (rendered|drawn) ", fc.label_note), f"{key}: a convention opens in the GM's form"
        assert "in order to" in fc.label_note, f"{key}: a convention states its purpose"
        assert re.search(r"\d", fc.label_note) or "not found" in fc.label_note, f"{key}: a figure, or the words 'not found'"
        assert "deviation" not in fc.label_note.lower(), f"{key}: a convention is not called a deviation"


def test_the_gm_s_line_between_deviation_and_convention() -> None:
    """Feature 183 (GM 2026-09-05): a deviation is the SETTING differing from history; a map drawing
    convention is a glyph scaled or colored for the eye. Six of the seven old deviations were the second."""
    assert sorted(k for k, fc in CLASSES.items() if fc.label == "deviation") == ["grave island"]
    assert sorted(k for k, fc in CLASSES.items() if fc.label == "convention") == ["bund beans", "homestead bamboo", "household shrine", "shared bamboo grove", "stream", "well"]
    beans = CLASSES["bund beans"].label_note
    assert beans.startswith("we have rendered the bund beans as") and "50 to 125 cm" in beans and "medium-green" in beans and "not found" in beans
    well = CLASSES["well"].label_note
    assert "about 1 m across" in well and "not found" in well, "the curb's width was searched for and not read"


def test_siblings_are_closed_over_the_vocabulary_and_symmetric() -> None:
    for key, fc in CLASSES.items():
        for other, text in fc.siblings.items():
            assert other in CLASSES, f"{key} names an unknown sibling {other!r}"
            assert other != key
            assert CLASSES[other].siblings.get(key) == text, f"{key} <-> {other} is one-way"
            assert len(text) > 40


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("farmhouse", "storage shed"),
        ("storage shed", "byre"),
        ("windbreak", "copse"),
        ("windbreak", "woodland commons"),
        ("homestead bamboo", "shared bamboo grove"),
        ("bund", "bund beans"),
        ("millet", "buckwheat"),
        ("millet", "barley"),
        ("buckwheat", "barley"),
        ("scrub and rough grazing", "marsh"),
        ("notice board", "notice board"),
    ],
)
def test_the_distinctions_the_gm_named_are_written(a: str, b: str) -> None:
    """The GM's own examples: a farmhouse is not a shed, storage vs. animals, the windbreak vs. other
    trees, the two bamboos, the beans on the bund, the dry crops apart. (The notice board has no
    sibling - it checks that a class with none has an empty map, not a missing one.)"""
    if a == b:
        assert CLASSES[a].siblings == {}
    else:
        assert b in CLASSES[a].siblings and a in CLASSES[b].siblings


def test_label_phrases_are_the_constitutions_four() -> None:
    assert label_phrase("accurate") == "historically accurate"
    assert label_phrase("deviation") == "a deliberate deviation"
    assert label_phrase("convention") == "a map drawing convention"
    assert label_phrase("guess") == "a guess"


# --- the presumption of accuracy (feature 156, GM 2026-08-29) ---


def test_only_a_liberty_is_announced() -> None:
    """The GM: don't say a thing is historically accurate; call out the liberties. So `accurate`
    produces no lead sentence at all, and the other two are unchanged."""
    assert lead_sentence("accurate", "Plot form and the irregular patchwork are read.") == ""
    assert lead_sentence("deviation", "drawn larger") == "This is a deliberate deviation - drawn larger"
    assert lead_sentence("guess", "") == "This is a guess."
    # a convention opens in the GM's own form (feature 183): "Note: we have rendered ..."
    assert (
        lead_sentence("convention", "we have rendered the beads darker, in order to see them. Real leaves are medium green.")
        == "Note: we have rendered the beads darker, in order to see them. Real leaves are medium green."
    )
    assert {"deviation", "convention", "guess"} == ANNOUNCED


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_the_caveat_is_a_verbatim_half_of_the_record(key: str) -> None:
    """`caveat` is rendered and `label_note` is not, so the two must not be allowed to drift: the
    caveat is always a literal slice of the note it was split out of."""
    fc = CLASSES[key]
    if fc.caveat:
        assert fc.caveat in fc.label_note, f"{key}: the caveat must be verbatim from its own record"


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_only_an_accurate_class_carries_a_caveat(key: str) -> None:
    """A deviation and a guess already lead with their liberty; a second copy below the why would
    say it twice."""
    fc = CLASSES[key]
    if fc.label != "accurate":
        assert fc.caveat == "", f"{key}: a {fc.label} announces its liberty in the lead"


def test_no_caveat_says_a_thing_is_drawn_at_its_TRUE_size() -> None:
    """Drawn at true size is ACCURACY, not a liberty - the trap `bund` and `notice board` fell into,
    and the one a later editor is likeliest to re-open, because "the drawn stroke" sounds like a
    drawing note (settlement-review, 2026-08-29)."""
    for key, fc in CLASSES.items():
        if fc.caveat:
            assert not re.search(r"\b(at its |at )?true(-| )size\b|\bat its true\b", fc.caveat), f"{key}: true size is accuracy, not a liberty"


def test_no_caveat_merely_reasserts_accuracy() -> None:
    """The point of the split (spec-fidelity round 1): "Topology, taper and true-size width are
    read" is the accuracy claim in other words, and moving it below the why would keep the GM's
    complaint alive on most of the map. A caveat says what was DRAWN rather than what was read."""
    for key, fc in CLASSES.items():
        if not fc.caveat:
            continue
        opener = fc.caveat.split(";")[0]
        assert not re.search(r"\bare read\b|\bis read\b|\bare attested\b", opener), f"{key}: the caveat's first clause is a provenance claim, not a liberty"


def test_every_accurate_class_without_a_caveat_is_deliberate() -> None:
    """The classes whose record discloses no liberty at all. Listed so adding one more is a decision
    someone makes on purpose rather than an omission nobody notices.

    Four were there from the split (their whole note is provenance). Three joined on 2026-08-29 when
    settlement-review read the rendered page: `bund` ("the drawn stroke is at true size") and
    `notice board` ("drawn at its true 12 x 5 ft") were the accuracy claim in other words, under an
    "On the drawing:" heading that promises a disclosure and delivered none; `windbreak` ("the belt's
    shape follows the terrain and the cluster") discloses nothing either way.

    `paddy` LEFT the list on 2026-08-29 (feature 160). It now discloses that its water depths and the
    drying stages between them are MODERN extension figures with no pre-modern record behind them -
    a real liberty, and the reason the GM asked for the number to be confirmed or labeled. This
    assertion is what made that a deliberate act rather than a quiet edit."""
    bare = {k for k, fc in CLASSES.items() if fc.label == "accurate" and not fc.caveat}
    assert bare == {"marsh", "field ditch", "pond", "bund", "notice board", "windbreak"}


def test_slug_is_a_css_token() -> None:
    for key in CLASSES:
        assert re.fullmatch(r"[a-z][a-z-]*", slug(key)), key


def test_the_not_highlighted_list_is_a_record_of_rulings() -> None:
    assert NOT_HIGHLIGHTED == "-"
    assert NOT_HIGHLIGHTED not in CLASSES
    assert len(NOT_HIGHLIGHTED_RULINGS) >= 2
    for what, who, when, why in NOT_HIGHLIGHTED_RULINGS + NOT_HIGHLIGHTED_OVERTURNED:
        assert what and who and re.fullmatch(r"\d{4}-\d{2}-\d{2}", when) and why


def test_an_overturned_ruling_is_kept_beside_the_list_rather_than_deleted() -> None:
    """The title placard was ruled map furniture on 2026-08-27 and let back in on 2026-08-29. The
    record should show that a decision was made and then remade, not quietly lose one - so the row
    moves to `NOT_HIGHLIGHTED_OVERTURNED` and neither list holds it twice."""
    standing = {what for what, *_ in NOT_HIGHLIGHTED_RULINGS}
    overturned = {what for what, *_ in NOT_HIGHLIGHTED_OVERTURNED}
    assert "the title placard and its text" in overturned
    assert "the scale bar and its captions" in standing, "the bar beside it keeps its ruling"
    assert not (standing & overturned), "a ruling is on one list or the other, never both"


def test_house_style_in_the_prose() -> None:
    """Hyphens only, American spellings - the page shows this text to the reader. (The forbidden
    forms are assembled at runtime so this file does not itself carry them.)"""
    dashes = (chr(0x2014), chr(0x2013))
    british = re.compile(r"\b(" + "|".join(["col" + "our", "cen" + "tre", "gr" + "ey", "hon" + "our", "label" + "led", "neighb" + "our", "behavi" + "our", "stor" + "ey"]) + r")\b")
    for fc in CLASSES.values():
        for text in (fc.what, fc.why, fc.label_note, *fc.siblings.values()):
            assert not any(d in text for d in dashes), fc.key
            assert not british.search(text), fc.key


def test_a_sibling_pair_naming_an_unknown_class_is_refused(monkeypatch: object) -> None:
    from l7r.diagram.interactive import classes as c

    monkeypatch.setattr(c, "_PAIRS", {("house", "no-such-class"): "text"})  # type: ignore[attr-defined]
    import pytest

    with pytest.raises(KeyError):
        c._install_siblings(tuple(c.CLASSES.values()) if isinstance(c.CLASSES, dict) else tuple(c.CLASSES))


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("pond sluice", "field ditch"),
        ("pond sluice", "sluice gate"),
        ("mulberry dike", "perimeter dike"),
        ("sugarcane dike", "perimeter dike"),
        ("banana dike", "perimeter dike"),
        ("fruit dike", "perimeter dike"),
    ],
)
def test_the_confusable_water_and_dike_pairs_link_both_ways(a: str, b: str) -> None:
    """Feature 153, the GM: the pond sluice modal should link to the field ditch modal "and vice versa,
    as we do with e.g. woodland commands and windbreak forests. We can do the same with the two
    different dike modals too." The crop dike is a four-valued rolled knob, so the dike pair is written
    once per value - a cane hamlet would otherwise ship a half-linked pair (spec Assumptions)."""
    assert b in CLASSES[a].siblings and a in CLASSES[b].siblings
    assert CLASSES[a].siblings[b] == CLASSES[b].siblings[a]


def test_the_windbreak_modal_is_headed_with_the_full_name() -> None:
    """The GM, 2026-08-29: "I would also like the windbreak model to actually say 'Windbreak forest'
    instead of just 'windbreak'." The KEY does not move - it rides on every drawn element and
    `all_ink_is_ruled_on` reads it - so this is the first class whose name and key differ."""
    assert CLASSES["windbreak"].key == "windbreak"
    assert CLASSES["windbreak"].name == "windbreak forest"
