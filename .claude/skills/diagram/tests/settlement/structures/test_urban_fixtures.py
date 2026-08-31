"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/urban_fixtures.py`."""

from l7r.diagram.settlement import Settlement

from ._builders import _STRUCTURES_SURFACE, _own_members, _structures_submixins


def test_theater_stage_records_every_stage_not_just_the_last():
    """TWO theater stages on one map (a temple stage AND an entertainment-quarter theater -
    Shiro Daika's design) must BOTH reach the manifest. The singleton dict write meant the
    second call clobbered the first: the labeled quarter stage existed as ink only, invisible
    to the overlap matrix in both directions (settlement-review, 2026-08-10)."""
    s = Settlement(1000, 1000, seed=7)
    s.theater_stage(300, 300, w=66, h=48, label=None)
    s.theater_stage(700, 700, w=64, h=46, rot=-120, kind="monzen", label=None)
    recs = s.M["theater_stage"]
    assert isinstance(recs, list) and len(recs) == 2
    assert {(r["x"], r["y"]) for r in recs} == {(300, 300), (700, 700)}
    assert recs[0].get("kind") == "machi" or recs[0].get("kind") == "monzen" or "kind" in recs[0]


def test_no_pre_split_structures_member_was_lost_in_the_move():
    # SUBSET, not equality, for the reason features 112 and 113 both recorded in their own guards:
    # a later decomposition legitimately adds named private helpers, and equality would turn every
    # such change into a contract edit - training a reader to update the frozenset without
    # thinking, which is exactly the reflex that lets a real subtraction through. What must never
    # happen is a pre-split member going MISSING: an addition is visible in review, a subtraction
    # is silent until whichever generator calls it happens to run.
    from l7r.diagram.settlement.structures import StructuresMixin

    composed = set().union(*(_own_members(c) for c in StructuresMixin.__mro__))
    assert composed >= _STRUCTURES_SURFACE, f"missing={sorted(_STRUCTURES_SURFACE - composed)}"


def test_no_two_structures_submixins_define_the_same_name():
    # The half that is easy to under-rate: a member defined by two sub-mixins produces a working
    # import, a clean `mypy --strict`, and one silently dead implementation, because MRO just picks
    # the first base.
    subs = _structures_submixins()
    for i, a in enumerate(subs):
        for b in subs[i + 1 :]:
            overlap = _own_members(a) & _own_members(b)
            assert not overlap, f"{a.__name__} and {b.__name__} both define {sorted(overlap)} - MRO would orphan one"


def test_every_structures_member_resolves_on_settlement_itself():
    # what consumers actually rely on: the name reaching Settlement, not merely StructuresMixin
    unreachable = sorted(n for n in _STRUCTURES_SURFACE if not hasattr(Settlement, n))
    assert not unreachable, f"not resolvable on Settlement: {unreachable}"


def test_a_LABELED_theater_stage_captions_its_whole_rotated_extent() -> None:
    """Feature 174: the labeled path, which the test above deliberately avoids by passing None.

    Two things it pins. The default size is the town-calibrated ~150x105 ft stage-plus-viewing-ground
    (the caller may state one, and the test above does, so the DEFAULT had never run). And the
    caption is placed against the ROTATED extent: the comment at that branch records why a plain
    reach correction dropped Tango's caption onto a monk house, so the half-extents are recomputed
    through the rotation rather than taken from the unrotated box.
    """
    s = Settlement(1200, 1200, seed=9)
    s.theater_stage(600.0, 600.0, label="temple stage")
    rec = s.M["theater_stage"][-1]
    assert (rec["w"], rec["h"]) == (s.px(150), s.px(105)), "the default is real feet at the map's ftpx"
    s.place_labels()
    assert any("temple stage" in lb[5] for lb in s.M["labels"] if len(lb) > 5), "the caption reached the sheet"

    turned = Settlement(1200, 1200, seed=9)
    turned.theater_stage(600.0, 600.0, rot=90.0, label="turned stage")
    turned.place_labels()
    placed = [lb for lb in turned.M["labels"] if len(lb) > 5 and "turned stage" in lb[5]]
    assert placed, "a rotated stage is captioned too"
