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
    # 269 E9, the GM 2026-09-28: a form attested only in modern sources is not drawn - retired with no successor
    "sugarcane dike": (),
    "banana dike": (),
    "vegetable ground": (),
    "duck pen": (),
}
#: Kinds the map draws that the snapshot's registry did not have at all.
ADDED_SINCE_189: tuple[str, ...] = (
    "weir",
    "pond canal",
    "alder",  # feature 261: the belt's trees where it runs into the marsh
    "burial ground",  # feature 273: a hamlet's own burial ground, on its knob
    "retirement house",  # 269 B42: the old couple's own roof in the homestead, on the family-form knob
    "tea dike",  # 269 E9 (B34): the attested tea dike, a third dike-crop form beside mulberry and fruit
)  # feature 230: what stands where the head race leaves the brook; and a dike-pond's two-way canals, which the irrigation ditch mislabeled (pass 10)


def test_the_registry_s_data_fields_equal_the_snapshot_and_its_prose_is_present() -> None:
    """The conversion proof, in two halves. The DATA fields (key, name, covers, label, sources, entry,
    siblings) are class attributes and constants the docstring move never touched; they must equal the
    snapshot permanently - only a CODE edit (which costs the gate) could change them. The PROSE fields
    (what, why, label_note, caveat) were proven equal to the snapshot field by field at the conversion
    commit (`d6d86346`, gate green 2026-09-05, 2,982 passed) - and are NOT pinned here, because a later
    prose edit is exactly what feature 189 exists to make cheap: pinning it would fail `make page-check`
    on every reworded explanation. Here they are only required to be present.

    THE ONE DATA FIELD THAT LEGITIMATELY MOVES IS `entry`, AND THE SNAPSHOT IS UPDATED WITH IT
    (feature 229). `entry` holds no value of its own: it NAMES a heading on a research page, and a
    research heading is written as the question a reader would ask from the map, so renaming one to a
    better question re-points every class that cites it. Thirteen moved when feature 229 renamed three
    headings that were addressed to a session rather than to a reader; two of those thirteen had been
    pointing at 'Why dikes were planted at all', a heading that does not exist, so the resolver matched
    nothing and two classes showed no question at all. The rule when you rename a heading: sweep every
    pointer, then re-point these snapshot strings in the same change, and expect the gate, since this
    pins a class attribute.

    AND `sources` MOVES WITH IT WHEN AN ENTRY IS REWRITTEN FROM NEW RESEARCH (feature 233). This
    docstring said "every other field here stays pinned permanently", which cannot hold: a class's
    `Sources:` names the keys its explanation was written FROM, so an entry rewritten against new
    findings whose sources it does not name is simply miscited. Feature 233 rewrote the `pig sty` and
    `duck pen` explanations against a new research section and both gained keys; the snapshot moved with
    them. The pin that matters is unchanged - `label`, `name` and `covers` still never move, and a
    `sources` change is only legitimate as part of a rewrite of the prose it supports. Two fields have ever moved this way; a THIRD moved once, for the same
    reason and under the same bar: a SIBLING TEXT carrying a factual claim the record has since
    contradicted (feature 234 - `crop-vs-perimeter` told a reader a crop dike is "six to ten meters of
    dredged mud" where the drawn collar measures 2.0 m, the same error the `MulberryDike` entry carried).
    A sibling text is reader-facing prose like an explanation, so a correction to it moves the snapshot
    exactly as a rewritten `What:` does. What still never moves is `label`, `name` and `covers`, and none
    of the three is license for a fourth.

    Feature 232 moved `sources` three more times, all under the same bar and all in the same direction -
    a key the record stopped being able to cite. `stream` and `field ditch` had been written from the
    Chinese national standard GB 50288, whose text is readable on no public page, and the pass found the
    provincial standard that defers to it by number and IS served openly; `fry pond` lost the closed
    article its township and its century came from. A class whose explanation rests on a key the record
    no longer cites is miscited in the other direction, which is why these move rather than stay pinned.

    Feature 250 (T23) moved `pig sty`'s once more, the 233 direction: its `Why:` was rewritten from the
    sluice question's paragraph on manure rate and the dead patch under the shed, and gained the two keys
    that paragraph and the "lift its boards" wording rest on (`fao-ac257e`, `fao-x6708e`).

    Feature 267 moved `grave island`'s `label` and `covers` - the first research finding to move a label, and under
    the same bar: the class was a DEVIATION because nothing read attested a grave in a working field, and the record
    now reads graves "in every field" around Shanghai (the island, accurate as the Chinese form) and graves at the
    bund edge or a field's corner in Japan, which the engine now draws as the knob's second form - so `covers` names
    both. A label that research overturns is miscited exactly as a stale `sources` is; what a PROSE edit alone may
    never do is still move any of the three. The same feature moved `field rock` from accurate to guess: research fields
    010 found no source putting outcrops on terraces and off valley, polder and delta ground (entry-drift, 2026-09-27).

    Feature 269 (K1) moved `fallow`'s `label` from guess to accurate under the same bar: its section was recorded as
    silent, and fields/250 now reads the resting paddy basin - scattered among the cropped plots, grazed - which the
    engine draws as a rolled form; its entry and sources moved with it. The same pass re-pointed paddy (fields/270),
    bund (fields/260) and the four dry crops (fields/180, and 050 on the three that lacked it) and gave each the keys
    its rewritten prose rests on, and corrected the five fallow sibling texts, which still called fallow a patch of
    ground resting for the season.

    Feature 269 (K2) moved three more labels from guess to accurate under the same bar, each once the engine drew
    what the record now reads: `bathhouse` (homesteads/214 - the village-by-village share and the front-yard or
    corridor seat), `hen coop` (215 - Buck's 82% of farms) and `persimmon` (218 - the dooryard or behind the house,
    the 23 ft crown). It re-pointed farmhouse (240, the spread of bearings), byre (300, the beast living with its
    keeper), privy and manure heap (260, the four seats and the field pit), and corrected two sibling texts the
    engine had made false: a byre drawn against its farmhouse, and a night-soil pit out at the fields.

    Feature 269 (K3) re-pointed the seven greenery kinds at what the engine now draws, each gaining the keys its
    rewritten prose rests on: homestead bamboo (vegetation/154 and 260 - the windward side read), windbreak (270 -
    the conifer-led and mixed-broadleaf forms, and 260's bamboo low in the grove), copse (210 - the homesteads' own
    woods), woodland commons (220 and 230 - beyond the fields, ~1,700 a hectare; 060 dropped, its figures no longer
    the commons'), scrub (090's flat-ground figure) and marsh (vegetation/280's yearly cutting, water/340's unharvested
    pond fringe). It corrected five sibling texts the engine had made false: a cedar-backed belt, a copse of loose
    greenery, a bamboo strip always on the damp north or west, a 10-30 year cycle, and a coppice on the slope above
    the paddy.

    Feature 269 (K4) moved `footbridge`'s `label` from guess to accurate under the same bar: water/290 reads the three
    crossings over small water (a single log or board, logs under trodden earth, a planked deck), which the engine now
    rolls per settlement; the evenness of the roll, the 2 ft line and the spacing stay disclosed guesses and rulings.
    Its entry gained ways/030 and its sources the keys 290 and 030 rest on. The same pass gave `village lane`
    homesteads/310 (the run-out rule, its distances a guess) and fields/290 (the field path ends on the bund) with the
    keys 290 cites; re-pointed the irrigation ditch (water/310, the bare intake mouth), the drainage ditch (water/090 and
    fields/090 - where the drain lets its water go and why it runs across the fall; the retired 'Water-first v2'
    heading dropped) and the weir (300's four forms and 310's choice); and corrected two sibling texts the engine had
    made false: a weir always of stone-packed crib, and a ditch always crossed by a plank.

    Feature 269 (K5) moved `pig sty`'s `label` from guess to accurate under the same bar: archetypes/210 reads the pig
    as the dike-pond district's own animal and a pen on a fish-pond bank as a late-Ming instruction, so the sty is read
    and only the share of households keeping one stays a disclosed guess. The same pass re-pointed the mulberry dike
    (220 - the density continuum, the drawn spacing the late-Qing figure by the GM's ruling), the fruit dike (230 - the
    oldest dike planting, lychee above all; the modern cane-and-vegetable succession no longer its why), the fry pond
    (200 - the fry bought from one township, the two kinds of village), the manure pit (homesteads/260 - the field
    pit), and, by the GM's ruling that a write-up of a place where animals lived says so, the fish pond (200 and 210 -
    its carp) and the paddy (210 - the delta's ducks herded in the rice fields), each with the keys its prose rests on.

    Feature 282 moved `threshing yard`'s `label`, `covers`, `sources` and `entry` under the same bar: the GM asked whether
    the one centered mat and the south-edge rack were accurate, and research homesteads 025 and 505 found the harvest yard
    covered in mats and racks by the house only where the harvest weather is changeable - so the glyph now draws mats over
    the whole yard, fewer than covered it (a CONVENTION, the GM's own form), and a rack by the house on its weather; the
    garden sibling's "bare" moved with it."""
    before = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    added = {s for succ in SINCE_189.values() for s in succ} | set(ADDED_SINCE_189)
    assert set(SINCE_189) <= set(before) and not (added & set(before)), "the tables name snapshot keys and NEW keys only"
    assert sorted(set(before) - set(SINCE_189) | added) == sorted(CLASSES)
    assert len(CLASSES) == 51 - len(SINCE_189) + len(added)
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
            if SINCE_189[retired]:  # a key retired with no successor (269 E9) leaves its pairs with nothing to name
                assert set(SINCE_189[retired]) & set(fc.siblings), (key, retired)
        assert fc.what and fc.why and fc.label_note, key
        if fc.caveat:
            assert fc.caveat in fc.label_note, key


def test_the_order_is_the_spec_s_and_comes_from_the_families_in_sequence() -> None:
    # the hamlet families only: `Kind` also registers the Mode A kinds (`compound_kinds/`, feature 262), which build their own registry
    hamlet = [k.key for k in Kind.registry if k.__module__.startswith("l7r.diagram.interactive.classes.")]
    assert sorted(CLASSES) == sorted(hamlet), "every registered hamlet kind is in CLASSES, once"
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
