"""tier town tests split out of `tests.settlement.test_shrines_wells` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import math

import pytest

from l7r.diagram.settlement import Settlement
from tests.settlement._builders import _town


@pytest.mark.tiers("town")
def test_open_seat_answers_where_a_feature_can_actually_stand():
    # GM 2026-07-25: fitting one extra well into a packed quarter cost three regenerate-and-check
    # cycles of hand-picked coordinates because nothing outside the engine could ask _fits where
    # there was room. open_seat asks it directly, so its answer is what placement will actually take.
    s = Settlement(1200, 1200, seed=3)
    s.meta(name="T", scale="town")
    s.block_polys.append([(390, 390), (500, 390), (500, 510), (390, 510)])  # the left half of the rect is no-build
    seat = s.open_seat((400, 400, 600, 500), 20, 20)
    assert seat is not None and s._fits(seat[0], seat[1], 20, 20)  # a seat the real placement path accepts
    assert seat[0] >= 500 and not s._in_blocked(*seat)  # ... off the blocked ground, which a manifest-only scan could not have known

    far = s.open_seat((400, 400, 600, 500), 20, 20, clear_of=[(600, 500)])  # stand away from an existing feature
    assert far is not None and math.hypot(far[0] - 600, far[1] - 500) > math.hypot(seat[0] - 600, seat[1] - 500)

    s.M["commons"] = [{"poly": [(490, 380), (620, 380), (620, 520), (490, 520)]}]  # grazed waste over the clear half
    assert s.open_seat((400, 400, 600, 500), 20, 20, well=True) is None  # a wellhead may not stand in it...
    assert s.open_seat((400, 400, 600, 500), 20, 20) is not None  # ... though anything else may

    s.block_polys.append([(0, 0), (1200, 0), (1200, 1200), (0, 1200)])  # nowhere left at all
    assert s.open_seat((400, 400, 600, 500), 20, 20) is None


@pytest.mark.tiers("city", "town")
def test_draft_byres_uses_the_legacy_size_off_the_to_scale_tiers():
    # a legacy tier (town/city) sizes its byre from the urban glyph grain (bscale), not px(feet) - the
    # non-to-scale branch of the byre sizer.
    s = _town()  # scale="town" -> not to-scale
    hs = [{"x": 300 + i * 170, "y": 350, "w": 40, "h": 28, "kind": "plain", "rot": 0, "wealth": 1.0} for i in range(3)]
    s.M["houses"] = hs
    for h in hs:
        s.placed.append((h["x"], h["y"], h["w"], h["h"]))
    placed = s.draft_byres(fraction=1.0, gap=40)
    assert placed and all(b["w"] > 0 for b in s.M["byres"])


@pytest.mark.tiers("city", "town")
def test_farm_wells_seats_in_a_dooryard_dodging_crop():
    """The SUCCESS path of the dooryard grid scan (previously covered only incidentally by the city
    regens, which stopped triggering it once Tango's belt got its own seeded wells 2026-07-21): the
    well seats near the steading on clear ground, skipping a crop patch in the scan ring."""
    s = Settlement(1000, 1000, seed=3)
    s.meta(name="Fw2", scale="town", ftpx=1)
    s.M["houses"].append({"x": 500, "y": 500, "w": 44, "h": 29, "rot": 0})
    # the field ENVELOPE blankets every ring spot (well_at refuses inside field_polys), so the ring
    # pass fails; the DRAWN crop covers only the top half, so the fallback - which suspends the
    # envelope and tests the drawn plots - seats the well on the bottom-half rim slack
    s.field_polys.append([(340, 340), (660, 340), (660, 660), (340, 660)])
    s.dry_polys.append([(340, 340), (660, 340), (660, 500), (340, 500)])
    s.M["fields"].append(
        {"name": "f", "kind": "paddy", "outline": [[340, 340], [660, 340], [660, 660], [340, 660]], "plot_polys": [[[600, 600], [648, 600], [648, 648], [600, 648]]]}
    )  # a drawn paddy plot the fallback also dodges
    assert s.farm_wells() == 1
    w = s.M["wells"][0]
    assert w["y"] > 514  # on the rim slack below the drawn crop (+14 margin), never on the crop


@pytest.mark.tiers("town")
def test_farm_wells_drops_a_cluster_with_no_seatable_ground():
    """A steading whose whole reach-disc is blocked ground gets skipped rather than spinning the
    cover loop forever - the well simply cannot seat, and the gate will say so."""
    s = Settlement(1000, 1000, seed=3)
    s.meta(name="Fw", scale="town", ftpx=1)
    s.M["houses"].append({"x": 500, "y": 500, "w": 44, "h": 29, "rot": 0})
    s.block_polys.append([(300, 300), (700, 300), (700, 700), (300, 700)])  # blanket the reach disc
    assert s.farm_wells() == 0
    assert not s.M["wells"]


@pytest.mark.tiers("town")
def test_farm_wells_falls_back_to_envelope_rim_slack():
    """When a steading's whole neighborhood sits inside a field ENVELOPE (the smoothed outline
    claiming more than the crop fills), the primary seating fails and the fallback suspends the
    envelope blocks, seating the well on unplanted rim slack - but never on a DRAWN plot."""
    s = Settlement(1000, 1000, seed=4)
    s.meta(name="Fw2", scale="town", ftpx=1)
    s.M["houses"].append({"x": 500, "y": 500, "w": 44, "h": 29, "rot": 0})
    s.field_polys.append([(200, 200), (800, 200), (800, 800), (200, 800)])  # envelope blankets the disc
    s.M["fields"].append(
        {"name": "t", "kind": "paddy", "outline": [[200, 200], [800, 200], [800, 800], [200, 800]], "bbox": [200, 200, 800, 800], "plot_polys": [[[430, 430], [570, 430], [570, 570], [430, 570]]]}
    )  # drawn crop hugs the house
    assert s.farm_wells() == 1
    wx, wy = s.M["wells"][0]["x"], s.M["wells"][0]["y"]
    assert not (430 <= wx <= 570 and 430 <= wy <= 570)  # seated on rim slack, not on the crop
