"""The Mode A kinds and the five magistracy pages they are written for (feature 262).

The GM, 2026-09-26: *"highlight things like the outer courtyard versus the inner courtyard and see write-ups of what
these things were and the extent to which this is indeed based on real historical research or is a thing specific
to this fictional setting"* - and the one constraint, that *"changing that source in one place is enough to change it
downstream"*. So the registry is held complete and closed over the maps it serves, every sheet is held to carry a
known kind on every drawn element, and the GM's two named examples are asserted on the page's own data.
"""

from __future__ import annotations

import importlib.util
import os
import re

import pytest

from l7r.diagram import compound
from l7r.diagram.interactive.classes import NOT_HIGHLIGHTED, lead_sentence
from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES
from l7r.diagram.interactive.notes import read_map_notes
from l7r.diagram.interactive.page import explanations, present_classes
from l7r.diagram.interactive.sheet import census, flatten, pieces
from l7r.diagram.interactive.sources import registry_keys, research_questions

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MAGI = os.path.join(SKILL, "pool", "magistracies")
HAND = ("ochiba-magistracy", "hayakawa-magistracy", "ubame-magistracy")
SILENT = "(no dedicated entry - recorded as silent)"


def _roundtrip_svg() -> str:
    path = os.path.join(MAGI, "ochiba-roundtrip-test", "ochiba-roundtrip-test.gen.py")
    spec = importlib.util.spec_from_file_location("ochiba_roundtrip_gen", path)
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    program = mod.ochiba_program()
    return compound.emit_svg(program, compound.place(program))


def _sheets() -> dict[str, str]:
    """Every magistracy the pool draws, as SVG text: the three tracked hand-drawn sheets, and the two placer drafts
    emitted fresh (their SVG is derived and gitignored)."""
    out: dict[str, str] = {}
    for name in HAND:
        with open(os.path.join(MAGI, name, name + ".svg"), encoding="utf-8") as fh:
            out[name] = fh.read()
    county = compound.county_magistracy_program()
    out["county-magistracy-example"] = compound.emit_svg(county, compound.place(county))
    out["ochiba-roundtrip-test"] = _roundtrip_svg()
    return out


SHEETS = _sheets()


def test_the_pool_s_magistracies_are_the_five_this_test_reads() -> None:
    assert sorted(SHEETS) == sorted(d for d in os.listdir(MAGI) if os.path.isdir(os.path.join(MAGI, d)))


@pytest.mark.parametrize("name", sorted(SHEETS))
def test_every_drawn_element_carries_a_kind_the_registry_knows(name: str) -> None:
    """FR-006: ink with no kind, or a kind nobody wrote, fails naming it."""
    got = census(SHEETS[name], COMPOUND_CLASSES)
    assert got.unclassed == [], f"{name}: ink with no kind - tag it (data-kind) or rule it out (data-kind=\"-\"): {got.unclassed}"
    assert got.unregistered == [], f"{name}: kinds the registry does not know: {got.unregistered}"


#: Every part a sheet draws inside a feature, and the feature it is part of (feature 264, `inventory.md`; the GM,
#: 2026-09-27: *"individual features inside of buildings or other features to get their own individual
#: highlighting"*). A part lights and opens as itself and lights with its parent - the reader must say both.
#: (part, parent) pairs, since one kind of part (a well) can be part of different parents on one sheet.
_SHARED = [("hearth", "kitchen"), ("well", "kitchen"), ("well", "garden"), ("garden pond", "garden"), ("latrine", "residence")]
PARTS: dict[str, list[tuple[str, str]]] = {
    "ochiba-magistracy": _SHARED
    + [
        ("genkan", "office hall"),
        ("engawa", "residence"),
        ("door", "residence"),
        ("door", "granary"),
        ("door", "office hall"),
        ("kitchen", "residence"),
        ("lord's quarters", "residence"),
        ("family quarters", "residence"),
        ("reception room", "residence"),
        ("guest quarters", "residence"),
        ("shrine altar", "compound shrine"),
        ("day office", "office hall"),
        ("official study", "office hall"),
        ("clerks' room", "office hall"),
        ("clerks' seats", "office hall"),
        ("kneeling positions", "hearing court"),
        ("striking posts", "practice ground"),
        ("weapon rack", "practice ground"),
        ("drying stones and bowls", "cinnabar workshop"),
        ("nakamon", "court divider"),
    ],
    "hayakawa-magistracy": _SHARED
    + [
        ("stone lantern", "garden"),
        ("garden pines", "garden"),
        ("engawa", "residence"),
        ("residence corridor", "residence"),
        ("lord's quarters", "residence"),
        ("family quarters", "residence"),
        ("reception room", "residence"),
        ("inner rooms", "residence"),
        ("ancestral alcove", "residence"),
        ("shrine altar", "compound shrine"),
        ("torii", "compound shrine"),
        ("door", "guest quarters"),
        ("door", "gatehouse"),
        ("clerks' room", "office hall"),
        ("day office", "office hall"),
        ("official study", "office hall"),
        ("clerks' seats", "office hall"),
        ("kneeling positions", "hearing court"),
        ("granary stilts", "granary"),
        ("striking posts", "practice ground"),
        ("weapon rack", "practice ground"),
        ("revetment", "river landing"),
        ("dock", "river landing"),
        ("tax barge", "river landing"),
        ("boatmen's altar", "river landing"),
        ("river watch", "river landing"),
        ("nakamon", "court divider"),
    ],
    "ubame-magistracy": _SHARED
    + [
        ("stone lantern", "border court"),
        ("engawa", "residence"),
        ("residence corridor", "residence"),
        ("door", "parley room"),
        ("lord's quarters", "residence"),
        ("family quarters", "residence"),
        ("reception room", "residence"),
        ("shuttered wing", "residence"),
        ("inner rooms", "residence"),
        ("ancestral alcove", "residence"),
        ("guest quarters", "residence"),
        ("torii", "compound shrine"),
        ("day office", "office hall"),
        ("official study", "office hall"),
        ("clerks' room", "office hall"),
        ("clerks' seats", "office hall"),
        ("kneeling positions", "hearing court"),
        ("granary stilts", "granary"),
        ("striking posts", "practice ground"),
        ("weapon rack", "practice ground"),
        ("steelyard", "weighing floor"),
        ("charcoal bales", "weighing floor"),
        ("parley mats", "parley room"),
        ("nakamon", "court divider"),
    ],
    "county-magistracy-example": [("striking posts", "practice ground"), ("weapon rack", "practice ground"), ("clerks' room", "office hall"), ("residence corridor", "residence")],
    "ochiba-roundtrip-test": [("striking posts", "practice ground"), ("weapon rack", "practice ground")],
}


@pytest.mark.parametrize("name", sorted(PARTS))
def test_every_part_is_its_own_kind_and_lights_with_its_parent(name: str) -> None:
    """FR-001 and FR-003: each inventoried part is drawn with its own kind, as part of its parent; and FR-009: the
    parent keeps ink of its own, so it is still named somewhere under the pointer and opens its own write-up."""
    ps = pieces(SHEETS[name])
    for part, parent in PARTS[name]:
        assert any(k == part and parent in within for _, k, within in ps), f"{name}: no {part!r} drawn as part of {parent!r}"
    for parent in {parent for _, parent in PARTS[name]}:
        assert any(k == parent for _, k, _ in ps), f"{name}: {parent!r} has no ink of its own left to point at"


def test_the_registry_is_closed_over_the_maps_it_serves() -> None:
    """FR-007: a kind no magistracy draws is a write-up nobody can open."""
    drawn = set().union(*(present_classes(flatten(svg)[1]) for svg in SHEETS.values()))
    assert sorted(set(COMPOUND_CLASSES) - drawn) == []


@pytest.mark.parametrize("key", sorted(COMPOUND_CLASSES))
def test_an_entry_is_complete(key: str) -> None:
    fc = COMPOUND_CLASSES[key]
    assert fc.key == key and key in fc.name.lower(), "the modal's heading names the kind its ink carries"
    assert len(fc.what) > 40 and len(fc.why) > 40, "an explanation is a paragraph, not a label"
    assert fc.label_note and fc.sources and all(fc.sources) and "research/" in fc.entry


@pytest.mark.parametrize("key", sorted(COMPOUND_CLASSES))
def test_each_label_speaks_in_its_own_form(key: str) -> None:
    """The same rules the hamlet vocabulary keeps (constitution XII, features 156 and 183)."""
    fc = COMPOUND_CLASSES[key]
    note = fc.label_note
    # the modal's lead already says "This is a guess - " or "This is a deliberate deviation - " (feature 264, building
    # review: nine notes that opened "this is a guess - " printed it twice)
    assert not re.match(r"\s*(this is\b|a guess\b|a deliberate deviation\b)", note, re.I), "the lead announces the label; the note must not repeat it"
    assert not re.match(r"\s*the [\w' ]+ (is|are) a (deliberate )?deviation", note, re.I), "the lead announces the deviation"
    if fc.label == "guess":
        assert re.search(r"\bguess", note, re.I), "a guess is labeled a guess in its own words"
    if fc.label == "deviation":
        assert re.search(r"deviat|departure|liberty|drawn", note, re.I) and "legibility" not in note.lower()
    if fc.label == "convention":
        assert re.match(r"we have (rendered|drawn) ", note) and "in order to" in note and "deviation" not in note.lower()
        assert re.search(r"\d", note) or "not found" in note
    if fc.caveat:
        assert fc.label == "accurate", "a liberty is announced in the lead; only an accurate kind carries a caveat"
        assert fc.caveat in note, "the caveat is a verbatim half of the note"
        assert not re.search(r"\b(at its |at )?true(-| )size\b", fc.caveat), "true size is accuracy, not a liberty"


@pytest.mark.parametrize("key", sorted(COMPOUND_CLASSES))
def test_the_entry_resolves_or_says_it_is_silent(key: str) -> None:
    """FR-005: a kind names the research question(s) it was written from, or declares that none covers it - and then
    the page shows the gap by having no references to list. A cited source is a registry key."""
    fc = COMPOUND_CLASSES[key]
    questions = research_questions(fc.entry)
    assert bool(questions) != (SILENT in fc.entry), f"{key}: {fc.entry!r} resolves to {len(questions)} question(s)"
    keys = registry_keys()
    assert fc.sources == ("not recorded",) or all(s in keys for s in fc.sources), f"{key}: {fc.sources}"


def test_house_style_in_the_prose() -> None:
    dashes = (chr(0x2014), chr(0x2013))
    british = re.compile(r"\b(" + "|".join(["col" + "our", "cen" + "tre", "gr" + "ey", "hon" + "our", "label" + "led", "neighb" + "our", "behavi" + "our", "stor" + "ey", "demes" + "ne"]) + r")\b")
    for fc in COMPOUND_CLASSES.values():
        for text in (fc.what, fc.why, fc.label_note, fc.caveat, *fc.siblings.values()):
            assert not any(d in text for d in dashes), fc.key
            assert not british.search(text), fc.key


def test_the_gm_s_two_examples_hold_on_the_ochiba_page() -> None:
    """SC-002: the threshold stones are the setting's and say so first; the hearing court rests on research, announces
    no liberty and lists the questions it was written from. And the two courts are two kinds, each with ground."""
    strings, tags = flatten(SHEETS["ochiba-magistracy"])
    notes = read_map_notes(os.path.join(MAGI, "ochiba-magistracy", "ochiba-magistracy.notes.md"))
    data = explanations(present_classes(tags), notes, registry=COMPOUND_CLASSES)
    stones, court = data["threshold stones"], data["hearing court"]
    assert stones["lead"].startswith("This is a deliberate deviation") and stones["on_this_map"], "FR-010: the map's own note rides along"
    assert court["lead"] == "" and court["questions"]
    grounds = {t for s, t in zip(strings, tags, strict=True) if s.startswith("<rect") and 'id="precinct"' in s}
    assert grounds == {"inner court", "outer court"}
    assert NOT_HIGHLIGHTED not in data


def test_a_kind_with_no_section_shows_its_gap_as_no_references() -> None:
    """User Story 4: a kind the record's sections do not cover opens with no questions to list."""
    silent = [k for k, fc in COMPOUND_CLASSES.items() if SILENT in fc.entry]
    assert silent, "the measurement found kinds no section covers; the registry must show them"
    data = explanations(set(silent), registry=COMPOUND_CLASSES)
    assert all(data[k]["questions"] == [] for k in silent)
    assert all(data[k]["lead"] == lead_sentence(COMPOUND_CLASSES[k].label, COMPOUND_CLASSES[k].label_note) for k in silent)
