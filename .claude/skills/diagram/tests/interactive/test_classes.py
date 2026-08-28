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

from l7r.diagram.interactive.classes import CLASSES, NOT_HIGHLIGHTED, NOT_HIGHLIGHTED_RULINGS, FeatureClass, label_phrase, slug

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
]


def test_every_spec_class_is_registered_and_nothing_else() -> None:
    assert sorted(CLASSES) == sorted(SPEC_CLASSES)


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_an_entry_is_complete(key: str) -> None:
    fc: FeatureClass = CLASSES[key]
    assert fc.key == key and fc.name == key
    assert len(fc.what) > 40 and len(fc.why) > 40, "an explanation is a paragraph, not a label"
    assert fc.label in ("accurate", "deviation", "guess")
    assert fc.label_note, "the label is justified in one line"
    assert fc.sources and all(fc.sources), "a sources line, or 'not recorded'"
    assert "research/" in fc.entry, "written FROM a research entry"


@pytest.mark.parametrize("key", SPEC_CLASSES)
def test_a_guess_says_so_in_its_note(key: str) -> None:
    fc = CLASSES[key]
    if fc.label == "guess":
        assert re.search(r"\bguess", fc.label_note, re.I), "a guess is labeled a guess in its own words"
    if fc.label == "deviation":
        assert re.search(r"deviat|legibility|drawn", fc.label_note, re.I), "a deviation says what deviates"


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


def test_label_phrases_are_the_constitutions_three() -> None:
    assert label_phrase("accurate") == "historically accurate"
    assert label_phrase("deviation") == "a deliberate deviation"
    assert label_phrase("guess") == "a guess"


def test_slug_is_a_css_token() -> None:
    for key in CLASSES:
        assert re.fullmatch(r"[a-z][a-z-]*", slug(key)), key


def test_the_not_highlighted_list_is_a_record_of_rulings() -> None:
    assert NOT_HIGHLIGHTED == "-"
    assert NOT_HIGHLIGHTED not in CLASSES
    assert len(NOT_HIGHLIGHTED_RULINGS) >= 3
    for what, who, when, why in NOT_HIGHLIGHTED_RULINGS:
        assert what and who and re.fullmatch(r"\d{4}-\d{2}-\d{2}", when) and why


def test_house_style_in_the_prose() -> None:
    """Hyphens only, American spellings - the page shows this text to the reader. (The forbidden
    forms are assembled at runtime so this file does not itself carry them.)"""
    dashes = (chr(0x2014), chr(0x2013))
    british = re.compile(r"\b(" + "|".join(["col" + "our", "cen" + "tre", "gr" + "ey", "hon" + "our", "label" + "led", "neighb" + "our", "behavi" + "our", "stor" + "ey"]) + r")\b")
    for fc in CLASSES.values():
        for text in (fc.what, fc.why, fc.label_note, *fc.siblings.values()):
            assert not any(d in text for d in dashes), fc.key
            assert not british.search(text), fc.key
