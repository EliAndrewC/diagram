"""The compound draft's service buildings (feature 374 waves 124-126 and batch 4): the stables as 0108 draws them, the
servants' and grooms' privies, the rowhouses divided into dwellings a door each, and no lodgers' privy by the main gate.
Split from `test_compound.py` at the 1,000-line bar; its helpers are repeated here, small as they are."""

from __future__ import annotations

import re
from dataclasses import replace

from l7r.diagram import compound as c
from l7r.diagram import compound_parts as cp


def _b(name: str, w: float, h: float, court: str, wall: str, order: int = 0, rank: int = 1, feature: str = "barracks") -> c.BuildingSpec:
    return c.BuildingSpec(name, "service", w, h, court, wall, order, rank, feature=feature)


def _env(w: float = 200.0, h: float = 200.0, div: float = 100.0, gate: float = 13.0) -> c.Envelope:
    return c.Envelope(w, h, div, gate)


def _county() -> tuple[c.CompoundProgram, c.PlaceResult, str]:
    prog = c.county_magistracy_program()
    result = c.place(prog)
    return prog, result, c.emit_svg(prog, result)


def test_a_servants_privy_serves_the_stables_only_when_it_stands_near_them() -> None:
    """Feature 374 wave 124: the grooms share the servants' privy where the servants' row stands by the stables; stables a
    servants' privy cannot serve (farther than GROOMS_PRIVY_FT) keep their own."""

    def privies(spine: tuple[c.CourtZone, ...]) -> int:
        prog = c.CompoundProgram(
            "t",
            _env(300.0, 120.0, 40.0, 8.0),
            spine,
            (_b("servants", 40.0, 15.0, "outer", "S", order=6, feature="servants' quarters"), _b("stables", 30.0, 20.0, "outer", "S", order=5, feature="stables")),
        )
        return c.emit_svg(prog, c.place(prog)).count('fill="#7E726A"')

    assert privies(()) == 1, "the stables beside the servants' row: one privy serves both"
    assert privies((c.CourtZone("cart yard", 50.0, 95.0, 90.0, 22.0),)) == 2, "pushed past a yard ~90 ft off: each keeps its own"


def test_a_stable_draws_its_passage_grooms_room_and_stalls_on_any_wall() -> None:
    """Feature 374 wave 126: the stable's inner form, as 0108's drawing page draws a warrior's - three bays along its court
    face; in its depth the grooms' room, the passage running its length, the stalls at the back - on whichever wall."""
    south = c.Placed(_b("stables", 18.0, 24.0, "outer", "S", feature="stables"), 10.0, 100.0)
    passage, walls = cp._stable_parts(south)
    assert passage == (10.0, 109.0, 28.0, 115.0)  # 6 ft deep, 9 ft in from the court (north) face, the room before it
    assert [w[0] for w in walls[:2]] == [16.0, 22.0] and (walls[0][1], walls[0][3]) == (115.0, 124.0)  # the stalls' walls, passage to back
    assert walls[-1][4] is True and walls[-2][4] is False  # the stall fronts dashed, the room's wall solid
    east = c.Placed(_b("stables", 24.0, 18.0, "outer", "E", feature="stables"), 100.0, 10.0)
    passage, walls = cp._stable_parts(east)
    assert passage == (109.0, 10.0, 115.0, 28.0) and [w[1] for w in walls[:2]] == [16.0, 22.0]


def test_the_county_rowhouses_draw_their_dwellings_and_a_door_each() -> None:
    """Feature 374 batch 4 (plan R4-4): the barracks, the staff long-house and the servants' row are divided into
    dwellings (0097), each with its door; the storehouses draw their doors (0117)."""
    prog, result, svg = _county()
    by = {p.spec.name: p for p in result.placed}
    for name, walls in (("barracks", 3), ("senior retainers' quarters", 4), ("servants' row", 3)):
        p = by[name]
        group = svg.split(f'<g data-kind="{p.spec.feature}">', 1)[1].split("</g>", 1)[0]
        assert group.count("<line ") >= walls, name
    doors = svg.count('data-kind="door" data-part-of="barracks"')
    assert doors == 4, doors
    # every dwelling of the servants' row draws its door (building-review round 4: the west one had none)
    assert svg.count("data-kind=\"door\" data-part-of=\"servants' quarters\"") == 4  # four dwellings since wave 128
    assert svg.count('data-kind="door" data-part-of="storehouse"') == 2


def test_bay_walls_run_across_the_short_side() -> None:
    def px(x: float, y: float) -> tuple[float, float]:
        return (3 * x, 3 * y)

    long_ew = c.Placed(replace(_b("row", 40.0, 10.0, "outer", "S"), bays=(20.0,)), 0.0, 0.0)
    assert c._bay_walls(long_ew, px, "#000") == ['<line x1="60" y1="0" x2="60" y2="30" stroke="#000" stroke-width="1"/>']
    long_ns = c.Placed(replace(_b("row", 10.0, 40.0, "outer", "E"), bays=(20.0,)), 0.0, 0.0)
    assert c._bay_walls(long_ns, px, "#000") == ['<line x1="0" y1="60" x2="30" y2="60" stroke="#000" stroke-width="1"/>']


def test_no_lodgers_privy_stands_by_the_main_gate() -> None:
    """Feature 374 batch 4 (plan R4-3, building-review E3): the stables' latrine sat 6 ft from the gatehouse, ~24 ft from
    the main gate's opening."""
    from l7r.diagram.tools import pack_audit as pa
    from l7r.diagram.tools.pack_audit.checks import wall_openings

    _prog, _result, svg = _county()
    gate = wall_openings(pa.parse_svg(svg))[0]  # the widest opening: the main gate
    privies = [(float(m[1]) + 7.5, float(m[2]) + 7.5) for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="15" height="15"[^>]*data-kind="latrine" data-id', svg)]
    assert len(privies) >= 3, "the lodgers' privies are drawn"
    assert all(abs(x - gate.x) > cp.GATE_PRIVY_FT * 3 or gate.y - y > cp.GATE_PRIVY_FT * 3 for x, y in privies), privies


def test_the_servants_row_takes_the_entry_form_its_roll_gives() -> None:
    """Feature 374 batch 4: 0097's two entry forms are a knob set per compound; the county draft rolls its own."""
    from l7r.diagram import compound_example as ce

    dwellings, common = ce.servants_row(ce.SERVANTS_FORMS[1]), ce.servants_row(ce.SERVANTS_FORMS[0])
    assert len(dwellings.extra_doors) == 3 and len(dwellings.bays) == 3  # four dwellings since wave 128
    assert common.extra_doors == () and common.bays == () and common.door_fracs == (0.5,)
    assert ce.SERVANTS_FORM == "a door to each dwelling"  # this draft's roll, as its notes record


def test_the_county_draft_rolls_its_granary_and_gate_by_the_records_order() -> None:
    """Feature 374 wave 128 (T20's plan review: the key the knob's name, the forms in the record's order)."""
    from l7r.diagram import compound_example as ce

    assert ce.GRANARY_FORMS == ("raised timber storehouse", "earth-walled kura") and ce.GRANARY_FORM == "earth-walled kura"
    assert ce.GATE_FORMS == ("one-bay gate", "gate range") and ce.GATE_FORM == "one-bay gate"
    prog = c.county_magistracy_program()
    by = {b.name: b for b in prog.buildings}
    assert by["granary"].kind == "kura" and (by["granary"].w_ft, by["granary"].h_ft) == (50.0, 27.0)
    assert prog.envelope.gate_w_ft == ce.YAKUIMON_FRONTAGE_FT - ce.YAKUIMON_PILLAR_FT == 7.0 and by["gatehouse"].w_ft == 40.0  # wave 132


def test_a_takakura_draws_its_slats_and_four_posts() -> None:
    """The granary roll's other form (0098's raised timber storehouse): the slatted body and a post at each corner."""
    env = c.Envelope(200.0, 200.0, 100.0, 13.0)
    prog = c.CompoundProgram("t", env, (), (c.BuildingSpec("granary", "takakura", 45.0, 25.0, "outer", "E", 6, feature="granary"),))
    svg = c.emit_svg(prog, c.place(prog))
    assert 'fill="url(#granary-slats)"' in svg and 'id="granary-slats"' in svg
    stilts = svg.split('<g data-kind="granary stilts">', 1)[1].split("</g>", 1)[0]
    assert stilts.count("<rect") == 4


def test_the_county_outer_court_keeps_a_way_west_past_the_stable_well() -> None:
    """Feature 374 batch 5 (building-review E1): the stable well stood in the 12 ft band between the hearing court and the
    stables, ~2.3 ft either side - the only way to the west of the outer court. The court is 26 ft deep and the well 6 ft
    out, a way of 6 ft or more beside it."""
    prog = c.county_magistracy_program()
    court = next(z for z in prog.spine if z.name == "oshirasu")
    svg = c.emit_svg(prog, c.place(prog))
    wells = [(float(m[1]), float(m[2])) for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="22" height="22"[^>]*data-kind="well"', svg)]
    stable_well = max(wells, key=lambda w: w[1])  # the southmost: the stables'
    assert (stable_well[1] - 45) / 3 - court.y2 >= 6.0, stable_well


def test_the_stables_privy_stands_against_the_wall_with_its_hatch() -> None:
    """Feature 374 batch 5 (building-review E2): a lodgers' privy seats against the wall at a building's end first."""
    _prog, _result, svg = _county()
    privies = [(float(m[1]), float(m[2])) for m in re.finditer(r'<rect x="([\d.]+)" y="([\d.]+)" width="15" height="15"[^>]*data-kind="latrine" data-id', svg)]
    assert any(y > 600 and 190 < x < 220 for x, y in privies), privies  # flush to the south wall, west of the stable
