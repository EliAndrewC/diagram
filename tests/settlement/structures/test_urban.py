"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/urban.py`."""

import math

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _crop_settlement, _ground_points


def test_commons_clears_the_urban_halo_around_buildings():
    s = _crop_settlement()
    s.building(300, 300, 40, 28, "merchant")  # axis-aligned
    s.building(430, 300, 40, 28, "laborer", rot=30)  # rotated - covered by its half-diagonal square
    s.building(1900, 1400, 40, 28, "shop")  # far outside the cover poly - the bbox prefilter drops it
    before = len(s.out)
    s.commons([(150, 150), (600, 150), (600, 500), (150, 500)], role="pasture")
    pts = _ground_points(s, before)
    assert pts  # the open ground beyond the halos still got its scatter
    halo = 30 * s.bscale - 0.06  # the SVG rounds coords to 0.1, so a base just OUTSIDE the halo can print ON its edge
    hd = math.hypot(20, 14) + halo
    for px, py in pts:
        assert not (280 - halo <= px <= 320 + halo and 286 - halo <= py <= 314 + halo)
        assert not (430 - hd <= px <= 430 + hd and 300 - hd <= py <= 300 + hd)


def test_marsh_clears_the_urban_halo_and_wellheads():
    s = _crop_settlement()
    s.building(300, 300, 40, 28, "merchant")
    s.well(460, 300)
    before = len(s.out)
    s.marsh([(150, 150), (600, 150), (600, 450), (150, 450)])
    lim = s.M["wells"][0]["vr"] + 20 * s.bscale - 0.06  # 0.1-rounding slack, as in the halo test
    halo = 30 * s.bscale - 0.06
    pts = _ground_points(s, before)
    assert pts
    for px, py in pts:
        assert not (280 - halo <= px <= 320 + halo and 286 - halo <= py <= 314 + halo)
        assert (px - 460) ** 2 + (py - 300) ** 2 > lim * lim


def test_a_TILTED_board_caption_walks_its_whole_fallback_ladder() -> None:
    """Feature 174. The caption ladder in `boards.py` is four rungs deep and every one of them was
    added because a previous version shipped a defect:

      - the SATISFICE rung, because an unbounded `max(..., key=box_clearance)` has no lateral term;
      - the HUG CAP, for the same reason one rung down;
      - the FLOOR rung ("give up the MARGIN, never the 2 ft the rule asks");
      - and only then the old thirty-seat search, "so a board with genuinely nowhere to put its
        caption behaves as it always has".

    Measured across 48 cohort seeds, six boards took the unbounded fallback and every one landed at
    the coarse ladder's own +/-38.9 px lateral against bounds of 10.7-11.3 - "the GM's Kuwabata
    defect, reproduced by the fallback on maps nobody had looked at".

    A board TILTED beside a lane with its ground built up on both sides drives the ladder past its
    early rungs, which a board on open ground never does.
    """
    s = Settlement(1200, 1200, seed=21)
    s.meta(name="T", scale="town")
    s.lane([(200.0, 600.0), (1000.0, 600.0)], width=16)
    for i in range(10):  # frontage on both sides, so the easy seats are taken
        s.building(360.0 + i * 36, 636.0, 32.0, 22.0, "kura", 0.0)
        s.building(360.0 + i * 36, 566.0, 32.0, 22.0, "kura", 0.0)
    s.kosatsuba(600.0, 612.0, rot=-32.0)
    s.place_labels()

    captions = [lb for lb in s.M["labels"] if len(lb) > 5 and "notice board" in str(lb[5])]
    assert captions, "the board is captioned even where every easy seat is taken"
