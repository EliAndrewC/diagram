"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/packing.py`."""

import pytest

from tests.settlement._builders import _town


def test_pack_full_placement_stays_silent(capsys):
    s = _town()
    s.pack((100, 100, 900, 900), ["merchant"] * 2)
    assert "SHORTFALL" not in capsys.readouterr().out


def test_pack_face_streets_true_skips_streetless_ground(capsys):
    # face_streets=True means businesses line a frontage ONLY: with no street within reach,
    # every grid spot is skipped and nothing places (the branch Hirameki's gate-market pack
    # exercised until 2026-07-24, when the market moved to fixed coordinates)
    s = _town()
    n = s.pack((100, 100, 400, 400), ["shop"] * 2, face_streets=True)
    assert n == 0 and "PACK SHORTFALL" in capsys.readouterr().out


def test_a_pack_SHORTFALL_is_printed_AND_recorded_never_silently_dropped(capsys) -> None:
    """Feature 174, and the rule's two recorded defects.

    GM 2026-08-05: *"we definitely want that to be visible"*. A placement helper that silently drops
    what does not fit is how authored-vs-landed drift happens - Hirameki's gate market authored 12
    businesses and landed 4 with nothing said (2026-07-24 town audit), and a later map shipped 88 of
    its 118 merchant households, noticed only during an unrelated perf investigation.

    So BOTH halves are asserted: the print, which the gen author sees, and the manifest record,
    which survives the terminal. And the record must carry NO geometry key - it is a diagnostic, not
    a drawn feature, and the overlap classifier keys off exactly those names.
    """
    s = _town()
    s._shortfall("rowpack", (100.0, 200.0), 4, ["shop", "shop", "kura"])
    printed = capsys.readouterr().out
    assert "ROWPACK SHORTFALL" in printed and "placed 4/7" in printed, printed
    assert "shop x2" in printed and "kura x1" in printed, "and it says WHAT was dropped"

    rec = s.M["shortfalls"][-1]
    assert (rec["by"], rec["placed"], rec["wanted"]) == ("rowpack", 4, 7)
    assert rec["at"] == [100.0, 200.0]
    assert not ({"x", "y", "pts", "poly", "outline", "boundary"} & set(rec)), "a diagnostic must not look like a drawn feature"


def test_a_pack_that_placed_EVERYTHING_records_no_shortfall_at_all() -> None:
    """The mirror branch: an empty leftover list is silence, not a zero-row. A standing empty record
    would train a reader to ignore the key."""
    s = _town()
    s._shortfall("pack", (0.0, 0.0), 9, [])
    assert "shortfalls" not in s.M


def test_a_shortfall_at_a_POLYLINE_flattens_its_coordinates_for_the_record() -> None:
    """`where` is a point for a pack and a run of points for a frontage, and the record has to
    carry either - the branch exists because both callers exist."""
    s = _town()
    s._shortfall("frontage", [(10.0, 20.0), (30.0, 40.0)], 1, ["stall"])
    assert s.M["shortfalls"][-1]["at"] == [10.0, 20.0, 30.0, 40.0], "flattened, not nested"


@pytest.mark.parametrize(
    ("a", "b", "hits", "why"),
    [
        ((0.0, 50.0), (200.0, 50.0), True, "straight through the middle"),
        ((0.0, 50.0), (200.0, 50.0), True, "and the reverse direction is the same segment"),
        ((0.0, 500.0), (200.0, 500.0), False, "horizontal, wholly below the rect (the p == 0 slab)"),
        ((50.0, -500.0), (50.0, -400.0), False, "vertical, wholly above it (the other p == 0 slab)"),
        ((300.0, 50.0), (400.0, 50.0), False, "beyond the right edge: it enters after it has left"),
        ((-400.0, 50.0), (-300.0, 50.0), False, "short of the left edge: it leaves before it enters"),
        ((50.0, 50.0), (60.0, 60.0), True, "a segment wholly INSIDE still hits"),
        ((-50.0, -50.0), (50.0, 50.0), True, "a diagonal clipped by two slabs at once"),
    ],
)
def test_seg_hits_rect_clips_a_segment_against_a_rect_on_every_slab(a: tuple[float, float], b: tuple[float, float], hits: bool, why: str) -> None:
    """The exact rect-vs-polyline test `rowpack` uses instead of sampling corners - a lane crossing
    BETWEEN two corners is invisible to a corner sample, which is why this is not point-based.

    Each of the four early exits is a separate row, because they are the branches a seed reaches only
    by luck: a segment parallel to a slab and outside it, one that enters after it leaves, and one
    that leaves before it enters."""
    from l7r.diagram.settlement.structures.packing import seg_hits_rect

    assert seg_hits_rect(a, b, 0.0, 0.0, 100.0, 100.0) is hits, why
    assert seg_hits_rect(b, a, 0.0, 0.0, 100.0, 100.0) is hits, f"and reversed: {why}"


def test_rowpack_lays_a_walkable_ROJI_between_pairs_and_a_court_only_every_few_rows() -> None:
    """The row cadence is three gaps, not one: the back-to-back eave gap INSIDE a pair, a walkable
    roji BETWEEN pairs so both pair-fronts have entrance ground, and a full idobata court every
    `court_every` rows. At the default `court_every=2` the court falls on every pair boundary and the
    roji branch never runs, which is why a wider cadence had never been drawn."""
    s = _town()
    n = s.rowpack((200.0, 200.0, 700.0, 700.0), ["laborer"] * 60, court_every=4)
    assert n > 0
    ys = sorted({round(b["y"], 1) for b in s.M["buildings"] if b["kind"] == "laborer"})
    gaps = sorted({round(ys[i + 1] - ys[i], 1) for i in range(len(ys) - 1)})
    assert len(gaps) >= 3, f"three distinct row gaps - eave, roji, court: {gaps}"


def test_rowpack_steps_a_terrace_PAST_blocked_ground_rather_than_building_on_it() -> None:
    """A row runs until something is in the way; the placer scans past the obstacle and picks the
    terrace up again, so a reserved pocket mid-row costs the row its middle and not its whole length.
    Every corner AND the center of each unit is tested, because a corner sample alone would walk a
    house's edge over a reservation."""
    s = _town()
    s.block_polys.append([(400.0, 190.0), (500.0, 190.0), (500.0, 710.0), (400.0, 710.0)])
    n = s.rowpack((200.0, 200.0, 700.0, 700.0), ["laborer"] * 60)
    assert n > 0, "the ground either side of the reservation still builds"
    for b in [b for b in s.M["buildings"] if b["kind"] == "laborer"]:
        assert b["x"] + b["w"] / 2 <= 400.0 or b["x"] - b["w"] / 2 >= 500.0, f"nothing stands on the reservation: {b}"
