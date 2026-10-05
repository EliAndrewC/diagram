"""The class registry is complete, closed and symmetric (feature 134, spec FR-007 / FR-008, SC-007).

Every class the spec's table names is here; every entry has its About paragraphs and says where the text came from
(the classification is per statement since feature 319); every sibling names a class in the
table and is named back. The page (`test_page.py`) and the browser test build on this - a registry
hole would surface there as a reader told nothing, which is the failure this file exists to catch
first.
"""

from __future__ import annotations

import re

import pytest

from l7r.diagram.interactive.classes import CLASSES, NOT_HIGHLIGHTED, NOT_HIGHLIGHTED_OVERTURNED, NOT_HIGHLIGHTED_RULINGS, FeatureClass, slug

# The spec's FR-007 vocabulary, verbatim (plus `field pond`, added at implementation and recorded
# in the spec table). A row added to the spec without an entry here fails this test; an entry here
# the spec does not name fails it too.
SPEC_CLASSES = [
    "alder",  # feature 261: the belt's trees where it runs into the marsh
    "homestead grove",  # feature 291: a farm's own grove, on the sides its settlement rolled
    "farm holding",  # feature 291 amendment 3: a row village's far-row holding
    "farm channel",  # feature 291 amendment 5: the channel into a dispersed farm's grounds
    "farmhouse",
    "storage shed",
    "byre",
    "retirement house",  # 269 B42 (0004)
    "threshing yard",
    "garden",
    "privy",
    "wood shed",  # feature 280: the woodpile is a wood shed
    "manure heap",
    "bath room",  # feature 280: the bath is a room joined to the house
    "hen coop",
    "household shrine",
    "persimmon",
    "burial ground",  # feature 273: a hamlet's own burial ground, on its knob
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
    # the bar across the brook at a `weir` hamlet's intake (feature 230; the form is rolled, so a map may
    # have none - the class is present on the page only when the map drew one)
    "weir",
    # the one `field ditch` became two (feature 230, GM 2026-09-12: the ditches that feed the paddies and the
    # ditch that drains them are different questions with different records behind them)
    "irrigation ditch",
    "drainage ditch",
    "pond canal",
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
    "perimeter dike",
    "fry pond",
    "manure pit",
    "sluice gate",
    "fruit dike",
    "tea dike",
    "pig sty",
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
    assert fc.about and all(len(p) > 40 for p in fc.about), "an About paragraph is a paragraph, not a label"
    assert fc.sources and all(fc.sources), "a sources line, or 'not recorded'"
    assert "research/" in fc.entry, "written FROM a research entry"


def test_the_gm_s_line_between_deviation_and_convention() -> None:
    """Feature 183 (GM 2026-09-05): a deviation is the SETTING differing from history; a map drawing convention is a glyph
    scaled or colored for the eye. Since feature 319's rollout (GM 2026-10-05) no hamlet class carries a feature-level
    label: a deviation is said in About where it applies, a convention on the Depiction tab with its real counterpart, a guess
    as a bullet (dev/modals.md M11-M13, D1-D6). The nine conventions this test listed (the bund beans, the homestead bamboo,
    the household shrine, the shared bamboo grove, the storage shed, the stream, the threshing yard, the weir, the well) each
    tell their convention on that tab now."""
    for key in ("bund beans", "well", "weir", "threshing yard"):
        assert CLASSES[key].depiction, f"{key}: its drawing convention is told on the Depiction tab"

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
        for text in (*fc.about, *fc.guesses, *fc.depiction, *fc.siblings.values()):
            assert not any(d in text for d in dashes), fc.key
            assert not british.search(text), fc.key


def test_a_sibling_pair_naming_an_unknown_class_is_refused() -> None:
    from l7r.diagram.interactive.classes._base import install_siblings

    with pytest.raises(KeyError):
        install_siblings(list(CLASSES.values()), {("house", "no-such-class"): "text"})


@pytest.mark.parametrize(
    ("a", "b"),
    [
        ("irrigation ditch", "drainage ditch"),
        ("mulberry dike", "perimeter dike"),
        ("fruit dike", "perimeter dike"),
        ("tea dike", "perimeter dike"),
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
