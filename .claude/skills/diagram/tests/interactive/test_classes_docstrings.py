"""Feature 189: the explanation is the docstring - the parser, the conversion's equality proof, the surface.

The snapshot `tests/fixtures/classes_before_189.json` was taken from the OLD `classes.py`'s source (its
`_DEFS` tuple and `_PAIRS`) before any change; the registry built from the docstrings must equal it in
every field, for every one of the 51 classes. That is what makes the conversion a move and not an edit."""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram.interactive import classes as pkg
from l7r.diagram.interactive.classes import CLASSES, FeatureClass, Kind, parse_explanation
from l7r.diagram.interactive.classes._base import install_siblings

SNAPSHOT = pathlib.Path(__file__).resolve().parents[1] / "fixtures" / "classes_before_189.json"
#: The vocabulary since the snapshot: a key retired -> the keys that replaced it. The snapshot is the record of
#: what the registry WAS before feature 189 and is never edited (spec 230 SC-2); the proof below carries forward
#: through this table instead - every snapshot key is still registered or is retired here, every registered key is
#: in the snapshot or is a successor here, and the count moves with the table rather than by hand.
SINCE_189: dict[str, tuple[str, ...]] = {
    "field ditch": ("irrigation ditch", "drainage ditch"),  # feature 230, GM 2026-09-12: the two ends of the field are two questions
}


def test_the_registry_s_data_fields_equal_the_snapshot_and_its_prose_is_present() -> None:
    """The conversion proof, in two halves. The DATA fields (key, name, covers, label, sources, entry,
    siblings) are class attributes and constants the docstring move never touched; they must equal the
    snapshot permanently - only a CODE edit (which costs the gate) could change them. The PROSE fields
    (what, why, label_note, caveat) were proven equal to the snapshot field by field at the conversion
    commit (`d6d86346`, gate green 2026-09-05, 2,982 passed) - and are NOT pinned here, because a later
    prose edit is exactly what feature 189 exists to make cheap: pinning it would fail `make page-check`
    on every reworded explanation. Here they are only required to be present."""
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    successors = {s for succ in SINCE_189.values() for s in succ}
    assert set(SINCE_189) <= set(before) and not (successors & set(before)), "the table names snapshot keys and NEW keys only"
    assert sorted(set(before) - set(SINCE_189) | successors) == sorted(CLASSES)
    assert len(CLASSES) == 51 - len(SINCE_189) + len(successors)
    for key, was in before.items():
        if key in SINCE_189:
            continue  # retired; its successors are new entries with their own data, judged by test_classes.py
        fc = CLASSES[key]
        for field in ("label", "name", "covers", "entry"):
            assert getattr(fc, field) == was[field], (key, field)
        assert tuple(fc.sources) == tuple(was["sources"]), key
        # a sibling pair that named a retired key now names its successors (the text rewritten for each); every
        # other pair is exactly the snapshot's
        kept = {k: t for k, t in was["siblings"].items() if k not in SINCE_189}
        assert {k: t for k, t in fc.siblings.items() if k in kept} == kept, key
        for retired in set(was["siblings"]) & set(SINCE_189):
            assert set(SINCE_189[retired]) & set(fc.siblings), (key, retired)
        assert fc.what and fc.why and fc.label_note, key
        if fc.caveat:
            assert fc.caveat in fc.label_note, key


def test_the_order_is_the_spec_s_and_comes_from_the_families_in_sequence() -> None:
    assert sorted(CLASSES) == sorted(k.key for k in Kind.registry), "every registered kind is in CLASSES, once"
    assert list(CLASSES)[:3] == ["farmhouse", "storage shed", "byre"] and list(CLASSES)[-1] == "perimeter dike"


def test_parse_explanation_reads_the_four_tags_and_joins_wrapped_lines() -> None:
    doc = """
    What: A house, and
    more house.

    Why: Because.

    Note: The note - drawn
    larger.

    Caveat: drawn larger.
    """
    got = parse_explanation(doc, "X")
    assert got == {"What": "A house, and more house.", "Why": "Because.", "Note": "The note - drawn larger.", "Caveat": "drawn larger."}
    assert "Caveat" not in parse_explanation("What: a\nWhy: b\nNote: c", "X"), "the caveat is optional"


@pytest.mark.parametrize(
    ("doc", "why"),
    [
        (None, "there is none"),
        ("   ", "there is none"),
        ("What: a\nWhy: b", "no Note: section"),
        ("What: a\nNote: c", "no Why: section"),
        ("Why: b\nNote: c", "no What: section"),
        ("stray text\nWhat: a\nWhy: b\nNote: c", "text before the first tag"),
    ],
    ids=["none", "blank", "no-note", "no-why", "no-what", "stray-text"],  # no newlines in a test id - xdist compares ids across workers line by line
)
def test_a_malformed_explanation_fails_loudly_naming_the_class(doc: str | None, why: str) -> None:
    with pytest.raises(ValueError, match=why) as e:
        parse_explanation(doc, "Farmhouse")
    assert "Farmhouse" in str(e.value)


def test_a_kind_builds_its_feature_class_from_its_docstring() -> None:
    class Probe(Kind):
        """What: a probe.

        Why: to test.

        Note: read; the size is a guess.

        Caveat: the size is a guess.

        Name: the probe
        Covers: nothing
        Label: guess
        Sources: not recorded, second-key
        Entry: research/none.md
        """

        key = "probe"

    fc = Probe.feature()
    assert isinstance(fc, FeatureClass) and fc.what == "a probe." and fc.caveat == "the size is a guess." and fc.label == "guess"
    assert fc.name == "the probe" and fc.covers == "nothing" and fc.sources == ("not recorded", "second-key") and fc.entry == "research/none.md"
    Kind.registry.remove(Probe)  # a test class must not join the vocabulary


@pytest.mark.parametrize(
    ("missing", "why"),
    [
        ("Label: guess", "no Label: section"),
        ("Sources: not recorded", "no Sources: section"),
        ("Entry: research/none.md", "no Entry: section"),
        ("Name: the probe", "no Name: section"),
        ("Covers: nothing", "no Covers: section"),
    ],
)
def test_a_kind_without_a_data_tag_fails_loudly_naming_the_class(missing: str, why: str) -> None:
    """Feature 207: the five data tags are required of a Kind (not of `parse_explanation`, which only reads)."""
    doc = "What: a.\n\nWhy: b.\n\nNote: c.\n\nName: the probe\nCovers: nothing\nLabel: guess\nSources: not recorded\nEntry: research/none.md\n".replace(missing + "\n", "")
    Probe = type("Probe", (Kind,), {"__doc__": doc, "key": "probe"})
    try:
        with pytest.raises(ValueError, match=why) as e:
            Probe.feature()
        assert "Probe" in str(e.value)
    finally:
        Kind.registry.remove(Probe)


def test_a_kind_with_a_label_outside_the_four_fails_loudly() -> None:
    Probe = type("Probe", (Kind,), {"__doc__": "What: a.\n\nWhy: b.\n\nNote: c.\n\nName: p\nCovers: n\nLabel: rumor\nSources: not recorded\nEntry: research/none.md\n", "key": "probe"})
    try:
        with pytest.raises(ValueError, match="rumor"):
            Probe.feature()
    finally:
        Kind.registry.remove(Probe)


def test_install_siblings_refuses_an_unknown_pair() -> None:
    with pytest.raises(KeyError):
        install_siblings(list(CLASSES.values()), {("farmhouse", "flying castle"): "x"})


def test_the_package_exports_everything_the_old_module_did() -> None:
    for name in (
        "CLASSES",
        "FeatureClass",
        "Label",
        "ANNOUNCED",
        "NOT_HIGHLIGHTED",
        "PLACE",
        "CONVENTION_LEAD",
        "lead_sentence",
        "label_phrase",
        "slug",
        "NOT_HIGHLIGHTED_RULINGS",
        "NOT_HIGHLIGHTED_OVERTURNED",
    ):
        assert hasattr(pkg, name), name
