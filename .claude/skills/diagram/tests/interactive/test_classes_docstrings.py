"""Feature 189: the explanation as tagged text - the parser, the conversion's equality proof, the surface.

The snapshot `tests/fixtures/classes_before_189.json` was taken from the OLD `classes.py`'s source (its
`_DEFS` tuple and `_PAIRS`) before any change; the registry still equals it in `name`, `covers` and the sibling texts,
the fields no rewrite may move (the old form's label and prose were retired in feature 319)."""

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
    # 269 E9, the GM 2026-09-28: a form attested only in modern sources is not drawn - retired with no successor
    "sugarcane dike": (),
    "banana dike": (),
    "vegetable ground": (),
    "duck pen": (),
    # feature 280 M57 (research/questions/0018-dike-ponds-fish-ponds-ringed-by-mulberry-dikes-sangji-yutang.html): a sluice through each pond's dike is a modern manual's form - retired
    "pond sluice": (),
    # feature 280 (settlement-review of Inashiro): the heading named the form eliminated - the bath is a room joined to the
    # house (M22) and the firewood is kept in a wood shed (M21); renamed, the prose and data carried over unchanged
    "bathhouse": ("bath room",),
    "woodpile": ("wood shed",),
}
#: Kinds the map draws that the snapshot's registry did not have at all.
ADDED_SINCE_189: tuple[str, ...] = (
    "weir",
    "pond canal",
    "alder",  # feature 261: the belt's trees where it runs into the marsh
    "burial ground",  # feature 273: a hamlet's own burial ground, on its knob
    "retirement house",  # 269 B42: the old couple's own roof in the homestead, on the family-form knob
    "tea dike",  # 269 E9 (B34): the attested tea dike, a third dike-crop form beside mulberry and fruit
    "homestead grove",  # feature 291: a farm's own grove, on the sides its settlement rolled - drawn once the forms rolled again
    "farm holding",  # feature 291 amendment 3: a row village's far-row farm's holding behind its lot (research 0033)
    "farm channel",  # feature 291 amendment 5: the channel led into a dispersed farm's grounds (research homesteads/200)
)  # feature 230: what stands where the head race leaves the brook; and a dike-pond's two-way canals, which the irrigation ditch mislabeled (pass 10)


def test_the_registry_s_data_fields_equal_the_snapshot() -> None:
    """The conversion proof, carried forward. `name` and `covers` are what the snapshot pins permanently: they name the
    kind and what it draws, and no rewrite of the prose may move them. The sibling texts are pinned too, except where a
    pair named a retired key (it now names the successors). The snapshot's other fields belonged to the old form - the
    label, the What/Why/Note/Caveat prose - and went with it in feature 319; `entry` and `sources` are rewritten with the
    About text they support (`dev/modals.md` M14). The history of every field that ever moved, and why, is in this file's
    git log and the features it names (229, 232-234, 250, 267, 269, 280, 282, 291, 292, 301)."""
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    added = {s for succ in SINCE_189.values() for s in succ} | set(ADDED_SINCE_189)
    assert set(SINCE_189) <= set(before) and not (added & set(before)), "the tables name snapshot keys and NEW keys only"
    assert sorted(set(before) - set(SINCE_189) | added) == sorted(CLASSES)
    assert len(CLASSES) == 51 - len(SINCE_189) + len(added)
    for key, was in before.items():
        if key in SINCE_189:
            continue  # retired; its successors are new entries with their own data, judged by test_classes.py
        fc = CLASSES[key]
        assert fc.name == was["name"] and fc.covers == was["covers"], key
        kept = {k: t for k, t in was["siblings"].items() if k not in SINCE_189}
        assert {k: t for k, t in fc.siblings.items() if k in kept} == kept, key
        for retired in set(was["siblings"]) & set(SINCE_189):
            if SINCE_189[retired]:  # a key retired with no successor (269 E9) leaves its pairs with nothing to name
                assert set(SINCE_189[retired]) & set(fc.siblings), (key, retired)


def test_the_order_is_the_spec_s_and_comes_from_the_families_in_sequence() -> None:
    # the hamlet families only: `Kind` also registers the Mode A kinds (`compound_kinds/`, feature 262), which build their own registry
    hamlet = [k.key for k in Kind.registry if k.__module__.startswith("l7r.diagram.interactive.classes.")]
    assert sorted(CLASSES) == sorted(hamlet), "every registered hamlet kind is in CLASSES, once"
    assert list(CLASSES)[:3] == ["farmhouse", "storage shed", "byre"] and list(CLASSES)[-1] == "perimeter dike"


@pytest.mark.parametrize(
    ("doc", "why"),
    [
        (None, "there is none"),
        ("   ", "there is none"),
        ("What: a\nWhy: b\nNote: c", "no About: section"),
        ("About:\nName: x", "no About: section"),
        ("stray text\nAbout: a", "text before the first tag"),
    ],
    ids=["none", "blank", "old-form", "empty-about", "stray-text"],  # no newlines in a test id - xdist compares ids across workers line by line
)
def test_a_malformed_explanation_fails_loudly_naming_the_class(doc: str | None, why: str) -> None:
    """Feature 319 retired the What/Why/Note/Caveat form: a text without `About:` is refused, never shown blank."""
    with pytest.raises(ValueError, match=why) as e:
        parse_explanation(doc, "Farmhouse")
    assert "Farmhouse" in str(e.value)


def test_a_kind_builds_its_feature_class_from_its_docstring() -> None:
    """A class with no modal file (a test's probe) is read from its docstring."""

    class Probe(Kind):
        """About: a probe.

        Name: the probe
        Covers: nothing
        Sources: not recorded, second-key
        Entry: research/none.md
        """

        key = "probe"

    fc = Probe.feature()
    assert isinstance(fc, FeatureClass) and fc.about == ("a probe.",)
    assert fc.name == "the probe" and fc.covers == "nothing" and fc.sources == ("not recorded", "second-key") and fc.entry == "research/none.md"
    Kind.registry.remove(Probe)  # a test class must not join the vocabulary


def test_install_siblings_refuses_an_unknown_pair() -> None:
    with pytest.raises(KeyError):
        install_siblings(list(CLASSES.values()), {("farmhouse", "flying castle"): "x"})


def test_the_package_exports_the_vocabulary_and_not_the_retired_label_machinery() -> None:
    for name in ("CLASSES", "FeatureClass", "NOT_HIGHLIGHTED", "PLACE", "slug", "NOT_HIGHLIGHTED_RULINGS", "NOT_HIGHLIGHTED_OVERTURNED"):
        assert hasattr(pkg, name), name
    for name in ("Label", "ANNOUNCED", "CONVENTION_LEAD", "lead_sentence", "label_phrase"):  # feature 319: the label is per statement
        assert not hasattr(pkg, name), name
