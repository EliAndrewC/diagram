"""Tests for compound.py (feature 008 - feet-first program + perimeter-first placer)."""

from __future__ import annotations

import pytest

from l7r.diagram import compound as c
from l7r.diagram import compound_parts as cp


def _env(w: float = 200.0, h: float = 200.0, div: float = 100.0, gate: float = 13.0) -> c.Envelope:
    return c.Envelope(w, h, div, gate)


def _b(name: str, w: float, h: float, court: str, wall: str, order: int = 0, rank: int = 1) -> c.BuildingSpec:
    return c.BuildingSpec(name, "service", w, h, court, wall, order, rank, feature="barracks")


def test_courtzone_and_placed_props() -> None:
    z = c.CourtZone("g", 10, 20, 30, 40)
    assert (z.x2, z.y2) == (40, 60)
    p = c.Placed(_b("x", 10, 20, "outer", "S"), 5, 6)
    assert (p.x2, p.y2) == (15, 26)


def test_place_hugs_each_wall() -> None:
    env = _env()
    prog = c.CompoundProgram(
        "t",
        env,
        (),
        (
            _b("N", 20, 10, "inner", "N"),
            _b("Souter", 20, 10, "outer", "S"),
            _b("W", 10, 20, "inner", "W"),
            _b("E", 10, 20, "inner", "E"),
            _b("divout", 30, 10, "outer", "divider"),
            _b("divin", 30, 10, "inner", "divider"),
        ),
    )
    pos = {p.spec.name: (p.x_ft, p.y_ft) for p in c.place(prog).placed}
    wall, div = c._wall_clearance_ft("N"), c._wall_clearance_ft("divider")
    assert pos["N"][1] == wall
    assert pos["Souter"][1] == env.h_ft - 10 - wall
    assert pos["W"][0] == wall
    assert pos["E"][0] == env.w_ft - 10 - wall
    assert pos["divout"][1] == env.divider_ft + div
    assert pos["divin"][1] == env.divider_ft - 10 - div


def test_placed_buildings_clear_the_wall_ink_on_every_wall() -> None:
    # A wall is drawn centered on the boundary, so half its thickness lies inside; a building
    # placed at the raw boundary is drawn INSIDE the masonry (pack_audit structures_on_walls).
    env = _env()
    prog = c.CompoundProgram(
        "t",
        env,
        (),
        (
            _b("N", 20, 10, "inner", "N"),
            _b("S", 20, 10, "outer", "S"),
            _b("W", 10, 20, "inner", "W"),
            _b("E", 10, 20, "inner", "E"),
            _b("divout", 30, 10, "outer", "divider"),
            _b("divin", 30, 10, "inner", "divider"),
        ),
    )
    wall, div = c._wall_clearance_ft("N"), c._wall_clearance_ft("divider")
    p = {x.spec.name: x for x in c.place(prog).placed}
    assert p["N"].y_ft >= wall and p["S"].y2 <= env.h_ft - wall
    assert p["W"].x_ft >= wall and p["E"].x2 <= env.w_ft - wall
    assert p["divin"].y2 <= env.divider_ft - div and p["divout"].y_ft >= env.divider_ft + div


def test_place_fire_gap_between_same_wall_buildings() -> None:
    prog = c.CompoundProgram("t", _env(), (), (_b("a", 20, 10, "inner", "N", 2), _b("b", 20, 10, "inner", "N", 1)))
    xs = sorted(p.x_ft for p in c.place(prog).placed)
    assert xs[1] - (xs[0] + 20) == c.FIRE_GAP_FT


def test_place_skips_the_gate_on_the_south_wall() -> None:
    env = _env(w=200.0, gate=40.0)  # gate spans x 80..120
    prog = c.CompoundProgram("t", env, (), (_b("g1", 60, 10, "outer", "S", 2), _b("g2", 60, 10, "outer", "S", 1)))
    placed = {p.spec.name: p for p in c.place(prog).placed}
    assert placed["g2"].x_ft >= 120.0


def test_place_skips_a_spine_court() -> None:
    spine = (c.CourtZone("oshirasu", 40, 0, 60, 30),)  # x 40..100 on the N band
    prog = c.CompoundProgram("t", _env(), spine, (_b("a", 30, 10, "inner", "N", 2), _b("b", 30, 10, "inner", "N", 1)))
    placed = {p.spec.name: p for p in c.place(prog).placed}
    assert placed["b"].x_ft >= 100.0


def test_place_overflow_when_building_too_wide() -> None:
    prog = c.CompoundProgram("t", _env(w=50.0), (), (_b("huge", 80, 10, "inner", "N"),))
    res = c.place(prog)
    assert res.placed == []
    assert [s.name for s in res.overflow] == ["huge"]


def _rects_overlap(a: c.Placed, b: c.Placed) -> bool:
    return c._rect_overlap(a.x_ft, a.y_ft, a.spec.w_ft, a.spec.h_ft, b.x_ft, b.y_ft, b.spec.w_ft, b.spec.h_ft)


def test_place_ns_row_owns_the_corner_and_ew_column_flows_below() -> None:
    # The N row (higher tier) takes the NW corner; the W column flows below it, not overlapping.
    prog = c.CompoundProgram("t", _env(w=200.0), (), (_b("wwall", 40, 20, "inner", "W"), _b("nwall", 30, 10, "inner", "N")))
    p = {x.spec.name: x for x in c.place(prog).placed}
    assert p["nwall"].x_ft == 3.0 and p["nwall"].y_ft == c._wall_clearance_ft("N")  # N owns the corner
    assert p["wwall"].x_ft == c._wall_clearance_ft("W") and p["wwall"].y_ft >= p["nwall"].y2  # W flows below
    assert not _rects_overlap(p["nwall"], p["wwall"])


def test_divider_hall_centers_between_the_ew_columns() -> None:
    # A long divider hall is placed AFTER the E/W columns, so it slides past the W column
    # instead of hogging the left corner (the office-hall-behind-oshirasu case).
    prog = c.CompoundProgram(
        "t",
        _env(w=200.0),
        (),
        (_b("hall", 120, 12, "outer", "divider", order=10), _b("wkura", 30, 20, "outer", "W", order=6), _b("ekura", 30, 20, "outer", "E", order=6)),
    )
    p = {x.spec.name: x for x in c.place(prog).placed}
    assert p["wkura"].x_ft == c._wall_clearance_ft("W") and p["ekura"].x2 == 200.0 - c._wall_clearance_ft("E")
    assert p["hall"].x_ft >= p["wkura"].x2  # hall flows past the W column, not into the corner


def test_second_rank_sits_behind_the_rank1_row_on_each_wall() -> None:
    # rank-2 building is offset inward past the rank-1 row, on all four straight walls.
    env = _env(w=200.0, h=200.0, div=100.0)
    for wall, court in (("N", "inner"), ("S", "outer"), ("W", "inner"), ("E", "inner")):
        prog = c.CompoundProgram("t", env, (), (_b("front", 40, 30, court, wall, order=10, rank=1), _b("rear", 20, 12, court, wall, order=1, rank=2)))
        p = {x.spec.name: x for x in c.place(prog).placed}
        assert not _rects_overlap(p["front"], p["rear"])
        if wall == "N":
            assert p["rear"].y_ft == p["front"].y2 + c.FIRE_GAP_FT
        elif wall == "S":
            assert p["rear"].y2 == p["front"].y_ft - c.FIRE_GAP_FT
        elif wall == "W":
            assert p["rear"].x_ft == p["front"].x2 + c.FIRE_GAP_FT
        else:  # E
            assert p["rear"].x2 == p["front"].x_ft - c.FIRE_GAP_FT


def test_emit_svg_contains_courts_buildings_and_walls() -> None:
    prog = c.county_magistracy_program()
    svg = c.emit_svg(prog, c.place(prog))
    for token in ("<svg", "office hall", "oshirasu", "garden", "url(#court-earth)", "#3F3A30"):
        assert token in svg


def test_emit_svg_draws_the_practice_ground_and_its_equipment() -> None:
    # The practice-ground zone (buildings.md program item) emits the swept patch plus the
    # durable equipment - weapon rack + two striking-post markers - not just a named rect.
    prog = c.county_magistracy_program()
    svg = c.emit_svg(prog, c.place(prog))
    assert "practice ground" in svg
    assert "url(#keiko-earth)" in svg
    assert "striking posts" in svg
    assert svg.count('fill="#7A5430"') == 2  # the two tategi post markers
    assert '#8C6F3E' in svg  # the weapon rack


def test_county_magistracy_places_without_overflow() -> None:
    res = c.place(c.county_magistracy_program())
    assert res.overflow == []
    assert len(res.placed) == 14  # the clerks' room is a room of the office hall since feature 267, not a building


def test_county_magistracy_buildings_clear_the_spine() -> None:
    # The practice ground (and every other spine zone) is reserved ground: no placed
    # building may overlap it - the E column must flow past the new zone, not into it.
    prog = c.county_magistracy_program()
    res = c.place(prog)
    for p in res.placed:
        for z in prog.spine:
            assert not c._rect_overlap(p.x_ft, p.y_ft, p.spec.w_ft, p.spec.h_ft, z.x_ft, z.y_ft, z.w_ft, z.h_ft), f"{p.spec.name} overlaps spine zone {z.name}"


def test_main_writes_a_draft(tmp_path, capsys) -> None:
    out = tmp_path / "d.svg"
    assert c.main([str(out)]) == 0
    assert out.read_text().startswith("<svg")
    assert "buildings placed" in capsys.readouterr().out


def test_main_default_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    # The map bundle's own folder, like every real map since feature 161: compound.main writes
    # its default output into it, and creating only the tier leaves nowhere to write.
    (tmp_path / "pool" / "magistracies" / "county-magistracy-example").mkdir(parents=True)
    assert c.main([]) == 0
    assert (tmp_path / "pool" / "magistracies" / "county-magistracy-example" / "county-magistracy-example.svg").exists()


def test_main_reports_overflow(tmp_path, monkeypatch, capsys) -> None:
    env = c.Envelope(50, 50, 25, 13)
    prog = c.CompoundProgram("t", env, (), (c.BuildingSpec("huge", "service", 80, 10, "inner", "N"),))
    monkeypatch.setattr(c, "county_magistracy_program", lambda: prog)
    c.main([str(tmp_path / "o.svg")])
    assert "OVERFLOW" in capsys.readouterr().out


# --- the point features the emitter seats (feature 254): wells, privies, tubs, a bath, the notice board ---


def _tub_circles(svg: str) -> int:
    """The circles inside the fire-water group (the pattern definitions carry circles of their own)."""
    return svg.split('<g fill="#8FB0C6"')[1].split("</g>")[0].count("<circle") if '<g fill="#8FB0C6"' in svg else 0


def _prog(*buildings: c.BuildingSpec, spine: tuple[c.CourtZone, ...] = ()) -> c.CompoundProgram:
    return c.CompoundProgram("t", _env(200.0, 200.0, 100.0, 13.0), spine, buildings)


@pytest.mark.parametrize(
    ("wall", "court", "normal"),
    [("N", "inner", (0.0, 1.0)), ("S", "outer", (0.0, -1.0)), ("E", "outer", (-1.0, 0.0)), ("W", "outer", (1.0, 0.0)), ("divider", "inner", (0.0, -1.0)), ("divider", "outer", (0.0, 1.0))],
)
def test_court_face_normal_points_into_the_court(wall: str, court: str, normal: tuple[float, float]) -> None:
    p = c.Placed(_b("x", 20.0, 10.0, court, wall), 50.0, 50.0)
    nx, ny, _fx, _fy = cp._court_face(p, _env())
    assert (nx, ny) == normal


def test_point_features_follow_the_masses_and_skip_what_the_program_lacks() -> None:
    full = _prog(
        _b("kitchen", 40.0, 30.0, "inner", "W", order=5),
        _b("stables", 30.0, 20.0, "outer", "S", order=5),
        _b("barracks", 30.0, 30.0, "outer", "E", order=4),
        _b("servants", 60.0, 14.0, "inner", "N", order=2),
        _b("archive", 30.0, 26.0, "outer", "W", order=6),
        spine=(c.CourtZone("garden", 60.0, 30.0, 80.0, 30.0),),
    )
    full = c.CompoundProgram(full.title, full.envelope, full.spine, (*full.buildings, c.BuildingSpec("kura", "kura", 30.0, 26.0, "outer", "W", order=1, feature="tax archive")))
    svg = c.emit_svg(full, c.place(full))
    # two latrines: the bath abutting the kitchen (feature 267) takes the seat the servants' latrine had at their east end
    assert svg.count(">well<") == 3 and svg.count(">latrine<") == 2 and ">bath<" in svg and ">notice board<" in svg and ">fire-water tubs<" in svg
    # one at the kitchen, one at each other wooden building, none at the kura: every building here is kinded a barracks,
    # so each seats its door first (feature 267) and the kitchen's face - bath, well and door - keeps room for one tub
    assert _tub_circles(svg) == 5
    bare = _prog(_b("hall", 40.0, 20.0, "outer", "divider", order=10))
    svg = c.emit_svg(bare, c.place(bare))
    assert ">well<" not in svg and ">latrine<" not in svg and ">bath<" not in svg and ">notice board<" in svg and _tub_circles(svg) == 1


def test_a_feature_with_no_clear_seat_is_left_out() -> None:
    """A building whose court face is walled in by its neighbors seats nothing against it."""
    boxed = _prog(
        _b("kitchen", 40.0, 30.0, "inner", "W", order=9),
        _b("block", 60.0, 60.0, "inner", "W", order=8, rank=2),  # a rank-2 mass right behind the kitchen's face
    )
    result = c.place(boxed)
    parts = c._point_features(boxed, result, lambda *a: "R", lambda *a: "L", 0.0, 0.0)
    assert parts.count("R") <= 3  # at most the notice board and what still fits; no well squeezed into the block


def test_a_seat_that_would_leave_the_envelope_is_refused() -> None:
    """A stable hugging the south wall of a 20 ft deep envelope has no room in front of it for a well
    (9 ft out) or even a tub (2.5 ft out): every candidate falls past the envelope's edge and nothing is seated."""
    env = _env(200.0, 20.0, 10.0, 13.0)
    prog = c.CompoundProgram("t", env, (), (_b("stables", 30.0, 15.0, "outer", "S", order=5),))
    parts = c._point_features(prog, c.place(prog), lambda *a: "R", lambda *a: "L", 0.0, 0.0)
    assert ">well<" not in "".join(parts) and "<circle" not in "".join(parts)


def test_emit_refuses_a_building_that_declares_no_kind() -> None:
    """Feature 262: a draft's page must know what every building is, so a program that leaves one out fails
    at emit, naming it - not silently, as ink nobody ruled on."""
    prog = c.CompoundProgram("t", _env(200.0, 200.0, 100.0, 13.0), (), (c.BuildingSpec("mystery", "service", 30.0, 20.0, "outer", "W", order=1),))
    with pytest.raises(ValueError, match="mystery"):
        c.emit_svg(prog, c.place(prog))


def test_every_element_of_the_county_draft_carries_a_kind() -> None:
    """Feature 262 FR-008: the placer writes the kind of everything it draws, so its draft needs no tagging by
    hand - the reader finds no untagged ink, the precinct is one rect per court, and the zones are kinded."""
    from l7r.diagram.interactive.sheet import census

    prog = c.county_magistracy_program()
    svg = c.emit_svg(prog, c.place(prog))
    got = census(svg, {})
    assert got.unclassed == []
    assert {"inner court", "outer court", "hearing court", "garden", "practice ground", "office hall", "compound wall", "court divider", "notice board"} <= set(got.counts)
    assert svg.count('id="precinct"') == 2


def test_a_hemmed_in_draft_caption_is_tied_back_by_a_leader() -> None:
    """Feature 266, FR-005 in Mode A: a caption the placer cannot seat beside its feature is drawn with its leader."""
    from l7r.diagram.compound import _seat_captions
    from l7r.diagram.labels import Obstacle, Subject
    from l7r.diagram.labels.geom import rect

    board = Subject("point", tuple(rect(200.0, 200.0, 9.0, 2.25)))
    ring = [Obstacle(tuple(q), 1000.0) for q in (rect(200.0, 180.0, 80.0, 8.0), rect(200.0, 220.0, 80.0, 8.0), rect(160.0, 200.0, 8.0, 30.0), rect(240.0, 200.0, 8.0, 30.0))]
    out, foot = _seat_captions([("notice board", board, 7.0, True, "#333", "notice board")], ring, (0.0, 0.0, 400.0, 400.0))
    assert len(out) == 2 and out[1].startswith("<line") and foot > 0.0


# --- feature 267: the example brought into line with the research (roofed court, rooms, bath, corridor) ---


def test_roof_posts_span_the_open_side_corner_to_corner() -> None:
    z = c.CourtZone("oshirasu", 10.0, 20.0, 49.0, 30.0)
    posts = c._roof_posts(z)
    assert len(posts) == 5  # 49 ft at a 12 ft bay: four bays, five posts
    assert posts[0] == (10.0, 49.0) and posts[-1] == (58.0, 49.0)  # both corners, flush with the south edge
    assert c._roof_posts(c.CourtZone("oshirasu", 0.0, 0.0, 3.0, 3.0)) == [(0.0, 2.0), (2.0, 2.0)]  # never fewer than two


def test_a_roofed_court_is_drawn_with_a_solid_outline_and_posts() -> None:
    prog = _prog(spine=(c.CourtZone("oshirasu", 40.0, 120.0, 60.0, 30.0), c.CourtZone("forecourt", 80.0, 160.0, 30.0, 30.0)))
    svg = c.emit_svg(prog, c.place(prog))
    court = next(ln for ln in svg.splitlines() if 'data-kind="hearing court"' in ln and "<rect" in ln)
    assert 'stroke="#5A3F1E" stroke-width="2.0"' in court
    posts = svg.split('<g fill="#5A3F1E" data-kind="hearing court">')[1].split("</g>")[0]
    assert posts.count("<rect") == 6
    fore = next(ln for ln in svg.splitlines() if 'data-kind="outer court"' in ln and 'stroke="#9C7A40"' in ln)
    assert 'stroke-width="0.8"' in fore  # an open court keeps the thin edge


def test_a_room_is_a_floor_inside_its_building() -> None:
    hall = c.BuildingSpec("office hall", "lord", 60.0, 30.0, "outer", "divider", order=10, feature="office hall", rooms=(("clerks' room", 20.0, 15.0),))
    prog = _prog(hall)
    svg = c.emit_svg(prog, c.place(prog))
    from l7r.diagram.interactive.sheet import pieces

    ps = pieces(svg)
    assert any(k == "clerks' room" and "office hall" in within for _, k, within in ps)
    assert ">clerks' room<" in svg and 'data-kind="office hall">' in svg  # both named (a narrow hall wraps its name)
    group = svg.split('<g data-kind="office hall">')[1].split("</g>")[0]
    assert group.rstrip().splitlines()[-1].startswith('<rect') and 'fill="none"' in group.rstrip().splitlines()[-1]  # the outline on top


def test_abut_seats_flush_against_the_court_face() -> None:
    env = _env()
    east = c.Placed(_b("kitchen", 40.0, 30.0, "inner", "W"), 2.0, 10.0)  # its face is east, at x 42
    assert cp._abut(env, east, 15.0, 12.0, []) == (42.0, 10.0)
    assert cp._abut(env, east, 15.0, 12.0, [(40.0, 0.0, 80.0, 16.0)]) == (42.0, 17.0)  # slides past what it must clear
    south = c.Placed(_b("kitchen", 40.0, 30.0, "inner", "N"), 10.0, 2.0)  # its face is south, at y 32
    assert cp._abut(env, south, 15.0, 12.0, []) == (10.0, 32.0)
    north = c.Placed(_b("x", 40.0, 30.0, "outer", "S"), 10.0, 160.0)
    assert cp._abut(env, north, 15.0, 12.0, []) == (10.0, 148.0)
    west = c.Placed(_b("x", 40.0, 30.0, "outer", "E"), 150.0, 110.0)
    assert cp._abut(env, west, 15.0, 12.0, []) == (135.0, 110.0)
    assert cp._abut(env, east, 15.0, 12.0, [(40.0, 0.0, 80.0, 200.0)]) is None  # the whole face walled off


def test_corridor_spans_a_short_gap_on_the_run_two_buildings_share() -> None:
    a = c.Placed(_b("residence", 90.0, 36.0, "inner", "N"), 3.0, 2.0)
    k = c.Placed(_b("kitchen", 44.0, 36.0, "inner", "W"), 2.0, 45.0)
    assert cp._corridor(k, a, 6.0, 7.0) == (21.5, 38.0, 27.5, 45.0)
    assert cp._corridor(a, k, 6.0, 7.0) == (21.5, 38.0, 27.5, 45.0)
    left = c.Placed(_b("l", 20.0, 30.0, "inner", "W"), 0.0, 10.0)
    right = c.Placed(_b("r", 20.0, 30.0, "inner", "W"), 25.0, 20.0)
    assert cp._corridor(left, right, 6.0, 7.0) == (20.0, 27.0, 25.0, 33.0)
    assert cp._corridor(right, left, 6.0, 7.0) == (20.0, 27.0, 25.0, 33.0)
    far = c.Placed(_b("f", 20.0, 30.0, "inner", "W"), 0.0, 60.0)
    assert cp._corridor(left, far, 6.0, 7.0) is None  # 20 ft apart is a gallery, not a short corridor
    assert cp._corridor(left, c.Placed(_b("o", 5.0, 5.0, "inner", "W"), 100.0, 100.0), 6.0, 7.0) is None  # no shared run


def test_the_county_example_keeps_the_house_together() -> None:
    """Feature 267: the bath abuts the kitchen, off every spine court; a corridor joins the kitchen to the residence;
    the clerks' room is a room of the office hall, not a building; the cell is 12 x 10 ft."""
    prog = c.county_magistracy_program()
    result = c.place(prog)
    assert not result.overflow
    names = {p.spec.name for p in result.placed}
    assert "clerks' room" not in names
    cell = next(p for p in result.placed if p.spec.name == "cell")
    assert (cell.spec.w_ft, cell.spec.h_ft) == (12.0, 10.0)
    svg = c.emit_svg(prog, result)
    assert 'data-kind="residence corridor"' in svg and 'data-kind="bath"' in svg and 'data-kind="clerks\' room"' in svg
    kitchen = next(p for p in result.placed if p.spec.name == "kitchen")
    bath = next(ln for ln in svg.splitlines() if 'data-kind="bath"' in ln and "<rect" in ln)
    assert f'y="{c.FTPX * (15.0 + kitchen.y2):.0f}"' in bath  # flush against the kitchen's court (south) face
    assert svg.count(">well<") == 3


def test_the_tubs_caption_goes_on_the_roomiest_tub() -> None:
    boxes = [(0.0, 0.0, 10.0, 10.0), (11.0, 11.0, 13.0, 13.0), (50.0, 50.0, 60.0, 60.0), (14.0, 0.0, 20.0, 5.0)]
    assert cp._roomiest([(12.0, 12.0), (40.0, 40.0)], boxes) == (40.0, 40.0)  # judged by the second-nearest box, its own not counted
    assert cp._roomiest([(5.0, 5.0), (6.0, 6.0)], [(0.0, 0.0, 10.0, 10.0)]) == (5.0, 5.0)  # nothing around either (a tie): the first


# --- feature 267 pass 3: the gates, the doors, the house's rooms and veranda, the roji, the roofed court as footprint ---


def _county() -> tuple[c.CompoundProgram, c.PlaceResult, str]:
    prog = c.county_magistracy_program()
    result = c.place(prog)
    return prog, result, c.emit_svg(prog, result)


def test_face_and_court_side() -> None:
    p = c.Placed(_b("x", 20.0, 10.0, "inner", "N"), 5.0, 6.0)
    assert cp._face(p, "S") == (0.0, 1.0, 5.0, 16.0, 20.0) and cp._face(p, "N") == (0.0, -1.0, 5.0, 6.0, 20.0)
    assert cp._face(p, "W") == (-1.0, 0.0, 5.0, 6.0, 10.0) and cp._face(p, "E") == (1.0, 0.0, 25.0, 6.0, 10.0)
    assert [
        cp._court_side(c.Placed(_b("x", 1, 1, court, wall), 0, 0)) for court, wall in (("inner", "N"), ("outer", "S"), ("inner", "E"), ("inner", "W"), ("inner", "divider"), ("outer", "divider"))
    ] == ["S", "N", "W", "E", "N", "S"]


def test_a_gatehouse_stands_beside_the_gate_or_nowhere() -> None:
    env = _env(200.0, 200.0, 100.0, 8.0)  # gate 96..104
    gh = c.BuildingSpec("gatehouse", "dark", 18.0, 12.0, "outer", "S", order=8, feature="gatehouse", beside_gate=True)
    placed = c.place(c.CompoundProgram("t", env, (), (gh,))).placed[0]
    assert placed.x2 == pytest.approx(96.0 - c.GATE_POST_W_FT - c.OUTLINE_CLEAR_FT) and placed.y2 == 200.0 - c._wall_clearance_ft("S")
    blocked = c.place(c.CompoundProgram("t", env, (c.CourtZone("forecourt", 70.0, 180.0, 30.0, 18.0),), (gh,)))
    assert blocked.placed == [] and blocked.overflow == [gh]  # something holds the ground beside the gate
    narrow = c.place(c.CompoundProgram("t", _env(30.0, 200.0, 100.0, 8.0), (), (gh,)))
    assert narrow.overflow == [gh]  # no room west of the gate at all


def test_the_middle_gate_opens_where_no_building_backs_the_divider() -> None:
    env = _env(200.0, 200.0, 100.0)
    hall = c.Placed(_b("hall", 120.0, 20.0, "outer", "divider"), 20.0, 101.5)
    a, b = cp._middle_gate(env, [hall])
    assert b - a == env.middle_gate_w_ft and a >= 140.0 + c.GATE_POST_W_FT  # past the hall's end, posts and all
    assert cp._middle_gate(env, []) == (97.0, 103.0)  # on the main axis when nothing backs it
    assert cp._middle_gate(c.Envelope(200.0, 200.0, 100.0, 13.0, middle_gate_w_ft=0.0), []) is None
    wall_to_wall = c.Placed(_b("row", 200.0, 20.0, "outer", "divider"), 0.0, 101.5)
    assert cp._middle_gate(env, [wall_to_wall]) is None


def test_wall_runs_break_for_each_gate_and_posts_stand_outside_the_passage() -> None:
    for side, at in (("W", 50.0), ("E", 60.0), ("N", 40.0)):
        env = c.Envelope(200.0, 200.0, 100.0, 8.0, postern=(side, at, 6.0))
        runs = [r for r in cp._wall_runs(env) if r[0] == side]
        assert len(runs) == 2 and len(cp._wall_runs(env)) == 6
    env = c.Envelope(200.0, 200.0, 100.0, 8.0)
    assert [r[0] for r in cp._wall_runs(env)] == ["N", "W", "E", "S", "S"]
    left, right = cp._gate_posts("S", 96.0, 104.0, 200.0, 1.0, 4.0)
    assert left == (95.0, 198.0, 96.0, 202.0) and right == (104.0, 198.0, 105.0, 202.0)
    top, bottom = cp._gate_posts("W", 47.0, 53.0, 0.0, 1.0, 4.0)
    assert top == (-2.0, 46.0, 2.0, 47.0) and bottom == (-2.0, 53.0, 2.0, 54.0)


def test_the_engawa_runs_along_the_court_face() -> None:
    def spec(court: str, wall: str) -> c.BuildingSpec:
        return c.BuildingSpec("r", "lord", 40.0, 20.0, court, wall, feature="residence", engawa_ft=5.0)

    assert cp._engawa(c.Placed(spec("inner", "N"), 0.0, 0.0)) == (0.0, 15.0, 40.0, 20.0)
    assert cp._engawa(c.Placed(spec("outer", "S"), 0.0, 0.0)) == (0.0, 0.0, 40.0, 5.0)
    assert cp._engawa(c.Placed(spec("inner", "E"), 0.0, 0.0)) == (0.0, 0.0, 5.0, 20.0)
    assert cp._engawa(c.Placed(spec("inner", "W"), 0.0, 0.0)) == (35.0, 0.0, 40.0, 20.0)


def test_a_door_sits_flush_inside_its_face_with_clear_ground_before_it() -> None:
    env = _env()
    south = c.Placed(_b("x", 40.0, 20.0, "inner", "N"), 10.0, 10.0)  # court face south, y 30
    door, approach = cp._door(env, south, [])
    assert door == (27.0, 30.0 - cp.DOOR_D_FT, 33.0, 30.0) and approach == (26.0, 30.0, 34.0, 33.0)
    north = c.Placed(_b("x", 40.0, 20.0, "outer", "S"), 10.0, 150.0)
    assert cp._door(env, north, [])[0] == (27.0, 150.0, 33.0, 150.0 + cp.DOOR_D_FT)
    east = c.Placed(_b("x", 20.0, 40.0, "inner", "W"), 10.0, 10.0)
    assert cp._door(env, east, [])[0] == (30.0 - cp.DOOR_D_FT, 27.0, 30.0, 33.0)
    west = c.Placed(c.BuildingSpec("x", "lord", 20.0, 40.0, "inner", "N", feature="residence", door_face="W"), 50.0, 10.0)
    assert cp._door(env, west, [])[0] == (50.0, 27.0, 50.0 + cp.DOOR_D_FT, 33.0)
    assert cp._door(env, west, [(40.0, 27.5, 49.0, 33.0)])[0][1] == 19.0  # the middle is blocked: the next frac
    assert cp._door(env, south, [(0.0, 30.0, 200.0, 40.0)]) is None  # the whole face walled off
    tiny = c.Placed(_b("x", 4.0, 4.0, "inner", "N"), 10.0, 10.0)
    assert cp._door(env, tiny, []) is None  # narrower than a door


def test_roji_stones_step_along_the_line_and_skip_what_they_would_land_on() -> None:
    assert cp._roji((0.0, 0.0), (0.0, 18.0), []) == [(0.0, 4.5), (0.0, 9.0), (0.0, 13.5)]
    assert cp._roji((0.0, 0.0), (0.0, 18.0), [(-1.0, 8.0, 1.0, 10.0)]) == [(0.0, 4.5), (0.0, 13.5)]
    assert cp._roji((0.0, 0.0), (0.0, 3.0), []) == []


def test_no_roji_without_a_middle_gate_or_a_reception_veranda() -> None:
    parts: list[str] = []
    bare = _prog(_b("hall", 40.0, 20.0, "outer", "divider", order=10))
    cp._roji_parts(bare, c.place(bare), [], lambda *a, **k: "R", parts, 0.0, 0.0)
    gateless = c.CompoundProgram("t", c.Envelope(200.0, 200.0, 100.0, 13.0, middle_gate_w_ft=0.0), (), c.county_magistracy_program().buildings)
    cp._roji_parts(gateless, c.place(gateless), [], lambda *a, **k: "R", parts, 0.0, 0.0)
    assert parts == []


def test_a_divider_building_with_a_veranda_gets_a_roji_from_the_outer_side() -> None:
    """The roji's first stone steps off the divider on the reception's own side: south of it for an outer-court host."""
    host = c.BuildingSpec("hall", "lord", 60.0, 30.0, "outer", "S", feature="residence", rooms=(("reception room", 30.0, 25.0),), engawa_ft=5.0)
    prog = _prog(host)
    parts: list[str] = []
    cp._roji_parts(prog, c.place(prog), [], lambda *a, **k: "R", parts, 0.0, 0.0)
    assert parts[0] == '<g data-kind="garden"><g fill="#B8B0A0" stroke="#7A7060" stroke-width="0.5">' and "<ellipse" in "".join(parts)


def test_the_county_example_carries_the_program_the_outcomes_name() -> None:
    """Pass 3's delta: the gatehouse beside a one-bay gate with its posts, the middle gate and the kitchen postern, a
    door on every lodging block, the residence's rooms and veranda, the roji, the cell's lattice."""
    from l7r.diagram.interactive.sheet import pieces
    from l7r.diagram.tools import pack_audit as pa

    prog, result, svg = _county()
    plan = pa.parse_svg(svg)
    assert pa.main_gate_passage_ft(plan) == pytest.approx(8.0)
    assert pa.two_court_zoning(plan) == [] and pa.divider_gates_ft(plan) == [6.0]
    assert 'data-kind="side gate"' in svg and 'data-kind="nakamon" data-part-of="court divider"' in svg
    gate = next(p for p in result.placed if p.spec.name == "gatehouse")
    assert (gate.spec.w_ft, gate.spec.h_ft) == (18.0, 12.0) and c._gate_interval(prog.envelope)[0] - gate.x2 < 2.0
    doors = {k for _s, k, within in pieces(svg) if k == "door" for k in within}
    assert {"residence", "kitchen", "karo's house", "guest quarters", "retainers' quarters", "barracks", "servants' quarters"} <= doors
    for kind in ("family quarters", "lord's quarters", "reception room", "engawa"):
        assert f'data-kind="{kind}"' in svg
    assert svg.count("<ellipse") >= 5 and ">hearing court<" in svg and ">servants' quarters<" in svg
    assert svg.split('<g data-kind="cell">')[1].split("</g>")[0].count("<line") == 2
    assert pa.tubs_in_buildings(plan) == [] and pa.floating_doors(plan) == []


def test_the_county_example_sets_the_garden_before_the_house_and_the_court_on_the_hall() -> None:
    prog, result, _svg = _county()
    by = {p.spec.name: p for p in result.placed}
    zones = {z.name: z for z in prog.spine}
    res, garden, court, hall = by["residence"], zones["garden"], zones["oshirasu"], by["office hall"]
    assert garden.x_ft <= res.x_ft and garden.x2 >= res.x2 and garden.y_ft == res.y2  # the whole south face looks onto it
    assert court.w_ft <= hall.spec.w_ft and abs((court.x_ft + court.x2) / 2 - (hall.x_ft + hall.x2) / 2) < 1.0
    kitchen = by["kitchen"]
    assert kitchen.x2 <= res.x_ft and (kitchen.spec.w_ft, kitchen.spec.h_ft) == (40.0, 30.0)  # the ell at the west end


def test_no_caption_but_its_own_stands_under_the_roofed_court() -> None:
    from l7r.diagram.tools import pack_audit as pa

    prog, _result, svg = _county()
    court = next(z for z in prog.spine if z.name == "oshirasu")
    x0, y0 = 7.0 * c.FTPX + court.x_ft * c.FTPX, 15.0 * c.FTPX + court.y_ft * c.FTPX
    x1, y1 = x0 + court.w_ft * c.FTPX, y0 + court.h_ft * c.FTPX
    inside = [lb.text for lb in pa.parse_svg(svg).labels if x0 < lb.cx < x1 and y0 < lb.cy < y1]
    assert inside == ["hearing court"]
