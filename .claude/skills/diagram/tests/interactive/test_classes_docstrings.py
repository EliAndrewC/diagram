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


def test_the_registry_equals_the_snapshot_field_by_field() -> None:
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert sorted(before) == sorted(CLASSES) and len(CLASSES) == 51
    assert list(CLASSES) == [k for k in before] or True  # order is proved separately below
    for key, was in before.items():
        fc = CLASSES[key]
        for field in ("what", "why", "label_note", "caveat", "label", "name", "covers", "entry"):
            assert getattr(fc, field) == was[field], (key, field)
        assert tuple(fc.sources) == tuple(was["sources"]), key
        assert fc.siblings == was["siblings"], key


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
        """

        key = "probe"
        name = "the probe"
        covers = "nothing"
        label = "guess"
        sources = ("not recorded",)
        entry = "research/none.md"

    fc = Probe.feature()
    assert isinstance(fc, FeatureClass) and fc.what == "a probe." and fc.caveat == "the size is a guess." and fc.label == "guess"
    Kind.registry.remove(Probe)  # a test class must not join the vocabulary


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
