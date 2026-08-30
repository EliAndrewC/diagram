"""Where a torii may stand (feature 166).

Carries `torii_clear_of_walls` and the seating half of the torii family, which the retired battery
re-measured on every finished map.

THE CHECK WAS A MIRROR, and `_geom/walls.py` says so in its own docstring: "check_village mirrors this
function; keep the two in sync". Two copies of one geometry, maintained in parallel, is the arrangement
this whole feature exists to end - so the test goes on the ORIGINAL and the mirror goes with the battery.

TRUE SCALE IS THE POINT OF THE BOX. The legacy glyph reserved a fixed 38 px half-box, which over-reserved
about five times the arch's real footprint - a village torii is ~8 px at 16 ft, not 38 - and that pushed
the crop out around the end of an approach avenue. `torii_halfbox` follows the drawn geometry instead.
"""

from __future__ import annotations

from l7r.diagram.settlement._geom.walls import torii_halfbox, torii_seat_on_wall


def test_the_arch_box_follows_the_drawn_glyph_at_true_scale() -> None:
    """A 16 ft arch at 1 ft/px is about 8 px of half-width plus a stroke pad - not the legacy 19."""
    hx, up, down = torii_halfbox(1.0, span_ft=16.0)
    assert 6.0 < hx < 12.0, f"half-width {hx:.1f} - the legacy fixed box was 19"
    assert up > 0 and down > 0
    assert down > up, "the posts drop further than the rail rises, as the glyph draws it"


def test_the_box_scales_with_the_map_grain() -> None:
    """The same 16 ft arch is fewer pixels on a coarser map. A box that ignored `ftpx` would reserve a
    village-sized margin on a city sheet, which is how the legacy fixed box went wrong."""
    fine = torii_halfbox(1.0, span_ft=16.0)[0]
    coarse = torii_halfbox(3.0, span_ft=16.0)[0]
    assert coarse < fine, f"at 3 ft/px the arch must draw smaller ({coarse:.1f} vs {fine:.1f})"


def test_a_wider_arch_reserves_more_room() -> None:
    assert torii_halfbox(1.0, span_ft=40.0)[0] > torii_halfbox(1.0, span_ft=16.0)[0]


def test_an_arch_seated_in_a_wall_is_named_and_one_standing_clear_is_not() -> None:
    """`torii_clear_of_walls`. The seat is asked of ONE candidate BEFORE the arch is drawn, which is what
    makes this a placement guarantee rather than an audit: a torii that would stand in the wall is never
    drawn there, instead of being drawn and reported."""
    M = {"meta": {"ftpx": 1}, "wall": [(0.0, 500.0), (1000.0, 500.0)], "wall_z": 1}
    assert torii_seat_on_wall(M, 500.0, 500.0, 1.0) is not None, "an arch on the wall line is refused"
    assert torii_seat_on_wall(M, 500.0, 50.0, 1.0) is None, "and one well inside the ward stands clear"
