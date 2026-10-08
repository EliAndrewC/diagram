"""Split from the 1,152-line `tests/settlement/test_structures.py` by feature 174 - see this
directory's CLAUDE.md for the index. Tests for `settlement/structures/ground.py`."""

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _town


def test_merchant_residences_skips_an_off_map_home():
    s = Settlement(1000, 1000, seed=1)
    s.road([(50, 500), (950, 500)])
    s.building(300, 950, 40, 28, "shop", rot=180)  # so deep that its home lands ~y=994, off the bottom edge
    assert s.merchant_residences() == 0


def test_place_punishment_spot_is_a_no_op_when_opted_out():
    s = _town()
    s.meta(punishment_spot=False)
    s.road([(100, 500), (900, 500)])
    assert s.place_punishment_spot() is None
    assert not s.M["punishment_spots"]


def test_place_punishment_spot_walks_the_label_off_a_building_it_would_cover():
    s = _town()
    s.road([(100, 500), (900, 500)])
    s.building(145, 536, 20, 20, "merchant")  # sits under the DEFAULT below-label, not under the spot
    spot = s.place_punishment_spot()
    assert spot is not None
    s.place_labels()  # feature 157: the LABEL PHASE draws the queued caption
    lb = [line for line in s.M["labels"] if len(line) > 5 and line[5] == "punishment ground"][0]
    below_default = spot[1] + s.px(12) / 2 + 11
    assert abs((lb[1] + lb[3]) / 2 - below_default) > 4  # the label moved off its default band
