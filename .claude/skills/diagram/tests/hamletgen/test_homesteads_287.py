"""Feature 287's homes guarantees at the homestead stage: the well pockets laid at seating and drawn (H10-H12), the
household bamboo on its house's bank (H01), the eaves stack against its steading (H35) and the woodpile form (H33).

Split from test_homesteads.py when feature 287 took it past the 1,000-line bar; the helpers stay there.
"""

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement

from ._builders import a_plan
from .test_homesteads import _WELL_HOUSES, _one_kind, _only_seat, _toy_hamlet


def test_a_well_past_the_crop_is_refused_now_the_pockets_water_every_house() -> None:
    """Feature 287, homes H12: a lattice seat whose wellhead would reach past the crop's box is not drawn."""
    from types import SimpleNamespace

    from l7r.diagram.hamletgen.homesteads.wells import crop_extent_added

    boxed = SimpleNamespace(_crop_boxes=lambda city: [(900.0, 1100.0, 900.0, 1100.0)])
    assert crop_extent_added(boxed, (1000.0, 1000.0), [0.0], [0.0]) == 0.0
    assert crop_extent_added(boxed, (1100.0, 1000.0), [0.0], [0.0]) == pytest.approx(12.0)
    east = (1110.0, 1000.0)
    plan = SimpleNamespace(spec=SimpleNamespace(households=6), ftpx=1.0)
    fake = _only_seat(*east)
    fake._crop_boxes = lambda city: [(950.0, 1100.0, 950.0, 1450.0)]  # type: ignore[attr-defined]
    assert hg.place_wells(fake, plan, _WELL_HOUSES) == 0, "the one legal seat reaches 22 px past the box"  # type: ignore[arg-type]


def test_every_household_seated_has_a_well_pocket_or_water_within_reach() -> None:
    """Feature 287, homes H10 and H11: the first household always carries a pocket; a later one exactly when no pocket
    and no open water stands within 760 ft - so every house is watered and no settlement is wellless."""
    from l7r.diagram.settlement.rolling.lot import needs_pocket

    s = Settlement(3000, 3000, seed=3)
    s.meta(name="W", scale="hamlet", ftpx=1, toscale=True)
    assert not needs_pocket(s, 100.0, 100.0), "no seating: no pockets asked"
    s._pockets = []
    assert needs_pocket(s, 100.0, 100.0), "the first household carries one"
    s._pockets.append((100.0, 100.0))
    assert not needs_pocket(s, 700.0, 100.0), "600 ft from a pocket"
    assert needs_pocket(s, 1000.0, 100.0), "900 ft from it, and no water"
    s.M["streams"] = [{"poly": [[1000.0, 0.0], [1000.0, 200.0]], "w": 6.0}]
    assert not needs_pocket(s, 1000.0, 100.0), "open water beside it"


def test_a_seating_draws_a_well_at_every_pocket_it_laid() -> None:
    """The seat half and the draw half together: a toy hamlet's pockets are laid in the bundles (inside each envelope,
    beside the yard, among the doors) and `place_wells` draws every one."""
    from l7r.diagram.hamletgen.homesteads import stage_homesteads
    from l7r.diagram.hamletgen.homesteads.wells import WELL_AMONG_DWELLINGS_PX, well_gap_to_dwellings

    s, plan = _toy_hamlet(10)
    stage_homesteads(s, plan)
    pockets = [h for h in s.M["houses"] if h.get("well_pocket")]
    assert pockets and pockets[0] is s.M["houses"][0], "the first household carries one"
    for h in pockets:
        px, py = h["well_pocket"]
        ex, ey, ew, eh = h["geom"]["bbox"]
        assert abs(px - ex) <= ew / 2 and abs(py - ey) <= eh / 2
        assert well_gap_to_dwellings(s.M["houses"], px, py) <= WELL_AMONG_DWELLINGS_PX
    hg.place_wells(s, plan, s.M["houses"])
    drawn = {(round(w["x"], 1), round(w["y"], 1)) for w in s.M["wells"]}
    assert all((round(h["well_pocket"][0], 1), round(h["well_pocket"][1], 1)) in drawn for h in pockets)


def test_a_household_bamboo_strip_stands_on_its_house_bank_and_names_its_house() -> None:
    """Feature 287, homes H01: a strip whose seat lies across the brook from its house is refused and the next tried; a
    seated strip records its owner (`plan.bamboo_of`, by its index among the stands)."""
    from l7r.diagram.hamletgen.homesteads.bamboo import household_bamboo
    from l7r.diagram.settlement._geom.water_index import crosses_a_stream

    got = 0
    for seed in range(40):
        s, plan = _toy_hamlet(10, seed=seed)
        plan.bamboo = "homestead"
        houses = [{"x": 200.0 + 120.0 * k, "y": 200.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"} for k in range(8)]
        s.M["streams"] = [{"poly": [[100.0, 180.0], [1300.0, 180.0]], "w": 2.0}]  # across every house's back
        rings = household_bamboo(s, plan, houses)
        for i, ring in enumerate(rings):
            cx, cy = sum(p[0] for p in ring) / 4, sum(p[1] for p in ring) / 4
            owner = plan.bamboo_of[i]
            assert not crosses_a_stream(owner, (cx, cy), s.M["streams"])
        got += len(rings)
    assert got, "some strips seated over the seeds"


def test_an_eaves_stack_stands_against_a_wall_of_its_own_steading_or_passes_on(monkeypatch: pytest.MonkeyPatch) -> None:
    """Feature 287, homes H35: an eaves woodpile is offered only the seats against a wall of its steading (the house, its
    kura), never the outward rungs; with every wall taken it passes on, and no stack stands off a wall."""
    from l7r.diagram.hamletgen.homesteads import fixtures as fx
    from l7r.diagram.hamletgen.homesteads.fixtures import against_a_wall, steading_rects

    walls = steading_rects(46.0, 28.0, "N")
    assert against_a_wall((0.0, -(14.0 + 3.5 + 2.0), 10.0, 4.0), walls, 3.5), "the back wall, a wall gap off"
    assert not against_a_wall((0.0, -(14.0 + 3.5 + 4.0 + 3.5 + 2.0), 10.0, 4.0), steading_rects(46.0, 28.0, None), 3.5), "a stack's depth further out"
    assert against_a_wall((0.0, -(14.0 + 3.5 + 4.0 + 3.5 + 2.0), 10.0, 4.0), walls, 3.5), "...which is the north kura's own wall"
    assert len(steading_rects(46.0, 28.0, "W")) == 2 and len(steading_rects(46.0, 28.0, None)) == 1
    _one_kind(monkeypatch, fx, ("woodpile",))
    monkeypatch.setattr(fx, "WOODPILE_FORMS", ("eaves",))
    for boxed in (False, True):
        s = Settlement(W=900, H=700, seed=7)
        s.meta(name="T", scale="hamlet", ftpx=1)
        house = {"x": 400.0, "y": 350.0, "w": 46.0, "h": 28.0, "rot": 0.0, "shed_side": "N"}
        s.M["houses"].append(dict(house))
        s.placed.append((400.0, 350.0, 46.0, 28.0))
        if boxed:  # a ring of posts a wall gap off every wall: no seat against any wall
            s.placed += [(400.0, 350.0 + d * 20.0, 60.0, 4.0) for d in (-1, 1)] + [(400.0 + d * 29.0, 350.0, 4.0, 40.0) for d in (-1, 1)]
        fx.farmstead_fixtures(s, a_plan(), [house])
        piles = [f for f in s.M["farm_fixtures"] if f["kind"] == "woodpile"]
        if boxed:
            assert not piles and s.M["meta"]["farm_fixtures_unseated"] == {"woodpile": 1}
        else:
            (p,) = piles
            lx, ly = p["x"] - 400.0, p["y"] - 350.0
            gap = max(abs(lx) - 23.0, abs(ly) - 14.0)
            assert gap <= 3.5 + 4.0 + 1.5, f"against a wall ({gap:.1f} px)"


def test_the_woodpile_form_a_homestead_draws_is_the_one_the_predicate_names() -> None:
    """Feature 287, homes H33: the kizuma where the knob rolled it and the belt stands within reach, else the eaves stack."""
    from l7r.diagram.hamletgen.homesteads.fixtures import woodpile_form_for

    assert woodpile_form_for("kizuma", True) == "kizuma"
    assert woodpile_form_for("kizuma", False) == "eaves"
    assert woodpile_form_for("shed", False) == "shed" and woodpile_form_for("eaves", True) == "eaves"
