"""How many sides a farmstead's grove takes, and which (feature 291): the faces for every wind and side count, the
dispersed layout that plants them, the manifest predicates that read them back, and the roll's frequencies."""

from __future__ import annotations

import collections

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.settlement import Settlement
from l7r.diagram.settlement.homestead_parts.grove_rules import (
    expected_faces,
    gardens_east_shaded,
    grove_farms,
    grove_sides_missing,
    groves_off_windward,
)
from l7r.diagram.settlement.homestead_parts.grove_sides import (
    GROVE_SIDES,
    GROVE_SIDES_FLOOD,
    E,
    N,
    S,
    W,
    bundle_turn,
    grove_faces,
    turn_face,
    windward_pair,
)
from l7r.diagram.settlement.rolling.dispersed import canonical_farmstead, dispersed_layout

WINDS = ("NW", "NE", "SW", "SE", "N", "E", "S", "W")


@pytest.mark.parametrize("wind", WINDS)
@pytest.mark.parametrize("flank", (-1, 1))
@pytest.mark.parametrize("sides", (2, 3, 4))
def test_the_faces_are_the_windward_pair_then_all_but_the_front_then_the_ring(wind: str, flank: int, sides: int) -> None:
    """SC-004: two sides are the windward pair (a cardinal wind's face and its flank); three add the one face that is not
    the front; four close the ring - and the front is always a lee face."""
    deep, thin, front = grove_faces(wind, sides, flank)
    assert len(set(deep)) == 2 and len(set(deep) | set(thin)) == sides, (deep, thin)
    letters = windward_pair(wind, flank)
    assert {d for d in deep} == {{"N": N, "E": E, "S": S, "W": W}[c] for c in letters}
    if len(wind) == 1:
        assert {"N": N, "E": E, "S": S, "W": W}[wind] in deep, "a cardinal wind's own face is always planted"
    assert front not in deep, "the front, where the yard and the way in are, is a lee face"
    if sides == 3:
        assert front not in thin, "three sides leave the front open"
    if sides == 4:
        assert front in thin, "four sides close it"


def test_a_cardinal_wind_takes_the_flank_it_rolled() -> None:
    assert windward_pair("N", -1) == "NW" and windward_pair("N", 1) == "NE"
    assert windward_pair("S", -1) == "SE" and windward_pair("S", 1) == "SW"
    assert windward_pair("E", -1) == "NE" and windward_pair("W", 1) == "NW"
    assert windward_pair("bogus", 1) == "NW", "an unknown key falls to the regional northwest, as `_windward` does"


def test_the_front_keeps_the_sun_where_it_can() -> None:
    """The yard (canonical south) lands on the lee face nearest the south: south under a north-quarter wind, east under
    the southwest (Tonami's front), west under the southeast."""
    assert turn_face(bundle_turn("NW", -1), S) == S and turn_face(bundle_turn("NE", -1), S) == S
    assert turn_face(bundle_turn("SW", -1), S) == E and turn_face(bundle_turn("SE", -1), S) == W


def test_a_grove_takes_two_three_or_four_sides_only() -> None:
    with pytest.raises(ValueError, match="2, 3 or 4"):
        grove_faces("NW", 1, -1)


def _canon(sides: int, by_yard: bool = False) -> dict:
    return canonical_farmstead(50.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=sides, garden_by_yard=by_yard, thin=17.0, sun_east=22.0, way_in=12.0)


def _edges(r):
    return r[0] - r[2] / 2, r[1] - r[3] / 2, r[0] + r[2] / 2, r[1] + r[3] / 2


@pytest.mark.parametrize("sides", (2, 3, 4))
def test_the_canonical_farmstead_plants_every_rolled_side_deep_to_windward_and_thin_elsewhere(sides: int) -> None:
    """SC-004 / FR-008: a deep band on the north and west; a thin band on the east with three sides; the south too with
    four, broken once for the way in; every thin band thinner than every deep one."""
    can = _canon(sides)
    faces = collections.Counter(f for _r, f, _d in can["groves"])
    assert set(faces) == {N, W, E, S}.intersection({N, W} | ({E} if sides >= 3 else set()) | ({S} if sides == 4 else set()))
    deep = [r for r, _f, d in can["groves"] if d == "deep"]
    thin = [r for r, f, d in can["groves"] if d == "thin"]
    assert len(deep) == 2
    depth = {N: lambda r: r[3], S: lambda r: r[3], E: lambda r: r[2], W: lambda r: r[2]}
    deep_depths = [depth[f](r) for r, f, d in can["groves"] if d == "deep"]
    thin_depths = [depth[f](r) for r, f, d in can["groves"] if d == "thin"]
    assert all(t < min(deep_depths) for t in thin_depths), (thin_depths, deep_depths)
    if sides == 4:
        assert faces[S] == 2, "the front band is broken once, for the way in"
        (l0, _t, l1, _b), (r0, _t2, _r1, _b2) = sorted((_edges(r) for r, f, _d in can["groves"] if f == S), key=lambda e: e[0])
        assert r0 - l1 == pytest.approx(12.0), "a way in twelve feet wide"
    assert len(thin) == {2: 0, 3: 1, 4: 3}[sides]


def test_the_thin_bands_stand_clear_of_the_gardens_morning_sun_and_the_yards_drying_strip() -> None:
    can = _canon(4)
    garden_east = _edges(can["garden"])[2]
    yard_south = _edges(can["yard"])[3]
    east_band = next(r for r, f, _d in can["groves"] if f == E)
    south_bands = [r for r, f, _d in can["groves"] if f == S]
    assert _edges(east_band)[0] > garden_east + 22.0
    assert all(_edges(r)[1] > yard_south + 22.0 for r in south_bands)


def test_the_garden_goes_beside_the_yard_when_the_frame_is_moved() -> None:
    home = _canon(2, by_yard=False)
    moved = _canon(2, by_yard=True)
    assert home["garden"][1] == 0.0, "against the house's east wall, at its mid-height"
    assert moved["garden"][1] == moved["yard"][1], "beside the yard"


@pytest.mark.parametrize("wind", WINDS)
def test_the_layout_carried_to_a_wind_plants_the_faces_grove_faces_names(wind: str) -> None:
    """The dispersed layout, turned to each wind, records each band's face as `grove_faces` names it, each band on that
    side of its house, and the house at its own size whatever the turn."""
    lay = dispersed_layout(500.0, 400.0, 50.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=4, turn=bundle_turn(wind, -1), thin=17.0, sun_east=22.0, way_in=12.0)
    deep, thin, _front = grove_faces(wind, 4, -1)
    assert {f for f, _d in lay["grove_faces"]} == set(deep) | set(thin)
    assert lay["house"] == (500.0, 400.0, 50.0, 28.0)
    for (cx, cy, _w, _h), (face, depth) in zip(lay["groves"], lay["grove_faces"], strict=True):
        assert (face in deep) == (depth == "deep")
        if face[0]:
            assert (cx - 500.0) * face[0] > 0
        else:
            assert (cy - 400.0) * face[1] > 0
    fx0, fy0, fx1, fy1 = _edges(lay["_frame"])
    for r in lay["groves"]:
        e = _edges(r)
        assert fx0 <= e[0] and e[2] <= fx1 and fy0 <= e[1] and e[3] <= fy1


def _manifest(sides: int, wind: str = "NW", drop: tuple | None = None, off: bool = False, shade: bool = False) -> dict:
    lay = dispersed_layout(500.0, 400.0, 50.0, 28.0, 3.0, (22.0, 24.0), (40.0, 30.0), sides=sides, turn=bundle_turn(wind, -1), thin=17.0, sun_east=22.0, way_in=12.0)
    groves = []
    for (cx, cy, w, h), (face, depth) in zip(lay["groves"], lay["grove_faces"], strict=True):
        if drop is not None and face == drop:
            continue
        if off and depth == "deep":
            face = (-face[0], -face[1])
        groves.append({"x": cx, "y": cy, "w": w, "h": h, "of": [500.0, 400.0], "face": list(face), "depth": depth})
    gx, gy, gw, gh = lay["garden"]
    if shade:
        groves.append({"x": gx + gw / 2 + 5 + 4, "y": gy, "w": 8.0, "h": 10.0, "of": [900.0, 900.0], "face": [0, -1], "depth": "deep"})
    return {
        "meta": {"settlement_form": "dispersed", "grove_sides": sides, "grove_flank": -1, "windward": wind, "ftpx": 1.0, "toscale": True},
        "houses": [{"x": 500.0, "y": 400.0, "geom": {"groves": lay["groves"]}}, {"x": 50.0, "y": 50.0, "geom": None}],
        "groves": groves,
        "gardens": [{"x": gx, "y": gy, "w": gw, "h": gh}],
    }


@pytest.mark.parametrize("sides", (2, 3, 4))
def test_the_predicates_pass_a_well_formed_grove_and_find_what_they_judged(sides: int) -> None:
    M = _manifest(sides)
    assert len(grove_farms(M)) == 1, "the rule found its farm - not vacuous"
    assert grove_sides_missing(M) == [] and groves_off_windward(M) == [] and gardens_east_shaded(M) == []


def test_the_predicates_catch_a_missing_side_a_lee_stand_and_a_shaded_garden() -> None:
    assert grove_sides_missing(_manifest(3, drop=E)) == [((500.0, 400.0), [E])]
    assert len(groves_off_windward(_manifest(2, off=True))) == 2
    assert len(gardens_east_shaded(_manifest(2, shade=True))) == 1


def test_a_nucleated_or_unrolled_map_owes_no_grove_sides() -> None:
    M = _manifest(3, drop=E)
    M["meta"]["settlement_form"] = "nucleated"
    assert grove_sides_missing(M) == []
    M2 = _manifest(3)
    del M2["meta"]["grove_sides"]
    assert grove_sides_missing(M2) == [] and groves_off_windward(M2) == []
    assert expected_faces({}) == ({N, W}, set())


def test_the_roll_keeps_the_rulings_weights_on_either_ground() -> None:
    """SC-003: over 1,000 seeds each table's counts sit within three standard errors of its weights."""
    for flood, table in ((False, GROVE_SIDES), (True, GROVE_SIDES_FLOOD)):
        counts = collections.Counter(hg.plan_site(hg.HamletSpec(name="X", seed=s, households=15, flood_ground=flood)).grove_sides for s in range(1, 1001))
        for k in (2, 3, 4):
            p = table.count(k) / len(table)
            se = (p * (1 - p) / 1000) ** 0.5
            assert abs(counts[k] / 1000 - p) < 3 * se, (flood, k, counts)


def test_a_polder_site_is_flood_prone_and_a_valley_is_not() -> None:
    """SC-003: the ground is read off the site - the polder archetypes are reclaimed low ground behind dikes."""
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, field_archetype="mulberry_dike_fishpond")).flood_ground
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, field_archetype="polder_grid")).flood_ground
    assert not hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, field_archetype="valley_paddy")).flood_ground
    assert not hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, field_archetype="polder_grid", flood_ground=False)).flood_ground


def test_a_spec_pins_the_side_count_and_refuses_one_no_grove_takes() -> None:
    assert hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, grove_sides=4)).grove_sides == 4
    with pytest.raises(ValueError, match="2, 3 or 4"):
        hg.plan_site(hg.HamletSpec(name="X", seed=3, households=15, grove_sides=5))


def test_a_settlement_rolls_and_records_its_sides_when_no_plan_did() -> None:
    """The house-first path: `meta.grove_sides` is rolled from the seed on the table its ground calls for, and kept."""
    s = Settlement(400, 400, seed=7)
    s.meta(name="C", scale="village")
    n = s._grove_sides()
    assert n in (2, 3, 4) and s.M["meta"]["grove_sides"] == n and s._grove_sides() == n
    assert s._grove_flank() in (-1, 1)
    f = Settlement(400, 400, seed=7)
    f.meta(name="C", scale="village", flood_ground=True, grove_sides=4, grove_flank=1)
    assert f._grove_sides() == 4 and f._grove_flank() == 1
