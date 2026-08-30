"""The field's keep-out, which is what holds structures off the rice (feature 166).

Carries the rules the retired `no_structure_on_paddy` and `dry_plots_clear_of_paddies` used to
re-measure on every finished map. A farmhouse, shed or dry plot standing in a flooded paddy is not a
placement the engine should be able to make, and it cannot: `_field_blocks_point` and
`_field_blocks_rect` refuse the ground before anything is seated on it.

THE TWO ARMS ARE DIFFERENT MEASUREMENTS AND BOTH ARE TESTED. Where the seat is known the refusal reads
the field's CHAINS - the open chords facing the seat, each with its outward normal; where it is not, it
reads the closed RING. `dev/gate.md` records what it cost to have the placer and its check read different
ones: a yard cleared a smoothed envelope by its circle and still put a corner inside a drawn basin.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

_PADDY = [(300.0, 300.0), (700.0, 300.0), (700.0, 600.0), (300.0, 600.0)]


def _with_field() -> Settlement:
    s = Settlement(1000, 1000, seed=1)
    s.meta(name="Riceton", scale="hamlet", ftpx=1, down_deg=90)
    s.field_polys = [_PADDY]
    return s


def test_a_point_inside_the_paddy_is_refused() -> None:
    s = _with_field()
    assert s._field_blocks_point(500.0, 450.0, 0.0), "the middle of the rice is not building ground"


def test_a_point_well_clear_of_the_paddy_is_allowed() -> None:
    s = _with_field()
    assert not s._field_blocks_point(100.0, 100.0, 14.0), "open ground away from the field is free"


def test_the_gap_holds_a_structure_off_the_bund_not_merely_out_of_the_water() -> None:
    """The refusal is a GAP, not a containment test. A wall flush against the outline puts the eaves over
    the levee path and the drip line into the crop, which is why the placer keeps a set-back rather than
    just refusing points inside the ring."""
    s = _with_field()
    assert not s._field_blocks_point(290.0, 450.0, 0.0), "10 ft outside, and no gap asked for"
    assert s._field_blocks_point(290.0, 450.0, 14.0), "the same point refused once the 14 ft set-back applies"


def test_a_rect_overlapping_the_paddy_is_refused_even_when_its_centre_is_clear() -> None:
    """The reason the rect arm exists at all. A footprint is refused on its CORNERS, so a house whose
    centre stands on dry ground and whose corner reaches into the basin is still refused - the failure
    `dev/gate.md` records as a yard clearing the envelope by its circle and putting a corner in a basin."""
    s = _with_field()
    assert s._field_blocks_rect((250.0, 250.0, 400.0, 400.0)), "a corner in the rice is enough to refuse it"
    assert not s._field_blocks_rect((50.0, 50.0, 150.0, 150.0)), "a footprint well clear is allowed"
