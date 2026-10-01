"""Feature 294's Mode A rules (plan B15b, B15c, B16-B24), each on plain synthetic sheets: the tagged-element reader, the
program rules, the roads, the palette, the map's gate and ways, the notes counts and the size marks - and the draft's
family privy, which `privies_by_zone` caught missing on the round-trip draft."""

from __future__ import annotations

import json
import os

from l7r.diagram import compound as c
from l7r.diagram import compound_parts as cp
from l7r.diagram.tools import notes_census as N
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import mapmatch as mm
from l7r.diagram.tools.pack_audit import palette as pal
from l7r.diagram.tools.pack_audit import program_rules as pr
from l7r.diagram.tools.pack_audit import roads as rd
from l7r.diagram.tools.pack_audit import size_marks as sm
from l7r.diagram.tools.pack_audit import tagged as tg
from l7r.diagram.tools.pack_audit.onmap import OnMap, declares, parse_on_map

COURT = "url(#court-earth)"


def _svg(*body: str, viewbox: str = "0 0 600 600", precinct: str = "") -> str:
    ground = precinct or f'<rect x="0" y="100" width="600" height="500" fill="{COURT}" id="precinct"/>'
    return f'<svg viewBox="{viewbox}">{ground}' + "".join(body) + "</svg>"


# --- tagged.py ---------------------------------------------------------------------------------------------------------


def test_path_points_reads_the_absolute_points_in_order() -> None:
    assert tg.path_points("M 0 0 L 10 0 H 20 V 5 C 1 1 2 2 30 30 Z") == ((0.0, 0.0), (10.0, 0.0), (20.0, 0.0), (20.0, 5.0), (30.0, 30.0))
    assert tg.path_points("m 3 4 l 5 5") == ()  # relative steps are offsets, not points
    assert tg.path_points("M1,2 3,4") == ((1.0, 2.0), (3.0, 4.0))


def test_marks_carry_kind_lineage_paint_and_translate() -> None:
    svg = (
        '<svg viewBox="0 0 100 100"><defs><rect x="1" y="1" width="1" height="1" data-kind="x"/></defs>'
        '<g data-kind="house" fill="#DDB87A" transform="translate(10, 20)"><rect x="0" y="0" width="5" height="4"/>'
        '<g data-kind="door" data-part-of="porch"><rect x="1" y="1" width="1" height="1" stroke-width="2"/></g></g>'
        '<circle cx="5" cy="5" r="2"/><ellipse cx="5" cy="5" rx="3" ry="1"/><line x1="0" y1="0" x2="3" y2="4"/>'
        '<polyline points="0,0 1,1 2,0"/><polygon points="0,0 4,0 4,4"/><path d="z"/><use href="#a"/>'
        '<text x="3" y="4" font-size="12" font-weight="bold">Title <tspan>A</tspan></text><text font-size="x">caption</text></svg>'
    )
    ms = tg.marks(svg)
    house, door = ms[0], ms[1]
    assert (house.x, house.y, house.kind, house.fill) == (10.0, 20.0, "house", "#DDB87A") and house.belongs_to("house")
    assert door.kind == "door" and door.lineage == ("house", "porch", "door") and door.belongs_to("porch") and door.stroke_width == 2.0
    assert house.stroke_width == 0.0 and house.font_size == 0.0 and house.x2 == 15.0 and house.y2 == 24.0
    tags = [m.tag for m in ms]
    assert tags == ["rect", "rect", "circle", "ellipse", "line", "polyline", "polygon", "text", "text"]
    title, caption = ms[-2], ms[-1]
    assert title.text == "Title A" and title.font_size == 12.0 and title.placed and not caption.placed and caption.font_size == 0.0
    assert tg.gap(ms[2], ms[3]) == 0.0 and tg.gap(house, ms[2]) > 0
    assert tg.marks('<rect x="0" y="0" width="1" height="1"/>') == ()  # a fragment with no <svg> root: nothing tagged


# --- program_rules.py: B16 lodging_entrances --------------------------------------------------------------------------

HOUSE = '<g data-kind="residence"><rect x="100" y="200" width="200" height="100" fill="#DDB87A"/></g>'
WING = '<g data-kind="kitchen"><rect x="300" y="200" width="60" height="60" fill="#C9A57A"/></g>'


def test_a_lodging_block_needs_a_door_on_its_outer_wall() -> None:
    bare = _svg(HOUSE, WING)
    assert pr.lodging_entrances(bare, pa.parse_svg(bare)) == ["the residence block at svg(100,200) has no door or genkan on its outer wall - a lodging is entered from the ground"]
    on_wing = _svg(HOUSE, WING, '<rect x="340" y="256" width="10" height="4" fill="#4A3318" data-kind="door"/>')  # on the joined wing's wall
    assert pr.lodging_entrances(on_wing, pa.parse_svg(on_wing)) == []
    untagged = _svg(HOUSE, '<rect x="150" y="296" width="10" height="4" fill="#4A3318"/>')  # an untagged dark door rect
    assert pr.lodging_entrances(untagged, pa.parse_svg(untagged)) == []
    deep = _svg(HOUSE, '<rect x="150" y="240" width="10" height="4" fill="#4A3318" data-kind="door"/>')  # inside, not on the wall
    assert pr.lodging_entrances(deep, pa.parse_svg(deep))
    shed = _svg('<g data-kind="shed"><rect x="10" y="200" width="40" height="40" fill="#C9A57A"/></g>')
    assert pr.lodging_entrances(shed, pa.parse_svg(shed)) == []  # no lodging kind: nothing asked


def test_components_join_touching_blocks_transitively() -> None:
    blocks = [tg.Mark("rect", "a", (), x, 0, 10, 10, i) for i, x in enumerate((0.0, 10.5, 21.0, 50.0))]
    assert sorted(len(g) for g in pr.components(blocks)) == [1, 3]


# --- B17 privies_by_zone ------------------------------------------------------------------------------------------------


def _courts(*body: str) -> str:
    ground = (
        f'<rect x="0" y="0" width="600" height="300" fill="{COURT}" id="precinct" data-kind="inner court"/>'
        f'<rect x="0" y="300" width="600" height="300" fill="{COURT}" id="precinct" data-kind="outer court"/>'
    )
    return _svg(*body, precinct=ground)


def _privy(x: int, y: int, part: str = "") -> str:
    of = f' data-part-of="{part}"' if part else ""
    return f'<g data-kind="latrine"{of}><rect x="{x}" y="{y}" width="15" height="15" fill="#7E726A"/></g>'


def test_privies_one_of_the_house_one_per_court_three_in_all() -> None:
    house = '<g data-kind="residence"><rect x="100" y="100" width="200" height="60" fill="#DDB87A"/></g>'
    good = _courts(house, _privy(300, 120), _privy(50, 50), _privy(50, 400))  # attached flush to the house's east end
    assert pr.privies_by_zone(good) == []
    tagged = _courts(house, _privy(400, 120, "residence"), _privy(50, 50), _privy(50, 400))
    assert pr.privies_by_zone(tagged) == []
    bad = _courts(house, _privy(400, 120), _privy(50, 50))
    found = pr.privies_by_zone(bad)
    assert found[0].startswith("no privy is the residence's own")
    assert found[1] == "the outer court at svg(0,300) has no privy - one stands in each functional zone"
    assert found[2].startswith("2 privies on the sheet")
    assert pr.privies_by_zone(_courts(_privy(50, 50), _privy(50, 400), _privy(60, 400))) == []  # no house: (a) asks nothing


# --- B18 fire_water_distribution ------------------------------------------------------------------------------------------


def _tubs(*xy: tuple[int, int]) -> str:
    return '<g fill="#8FB0C6" data-kind="fire-water tubs">' + "".join(f'<circle cx="{x}" cy="{y}" r="3.8"/>' for x, y in xy) + "</g>"


def test_a_tub_at_every_listed_building_two_at_the_kitchen_none_at_a_kura_alone() -> None:
    kitchen = '<g data-kind="kitchen"><rect x="100" y="200" width="60" height="60" fill="#C9A57A"/></g>'
    kura = '<g data-kind="tax archive"><rect x="400" y="200" width="60" height="60" fill="#F2EFE4"/></g>'
    room = '<g data-kind="residence"><rect x="200" y="400" width="100" height="60" fill="#DDB87A"/><rect x="210" y="410" width="20" height="20" fill="#DDB87A" data-kind="lord\'s quarters"/></g>'
    good = _svg(kitchen, kura, room, _tubs((96, 210), (96, 250), (196, 420)))
    assert pr.fire_water_distribution(good, pa.parse_svg(good)) == []
    bad = _svg(kitchen, kura, room, _tubs((96, 210), (464, 210)))
    found = pr.fire_water_distribution(bad, pa.parse_svg(bad))
    assert found == [
        "the residence at svg(200,400) has 0 fire-water tub(s) by its eaves - it needs 1",
        "the kitchen at svg(100,200) has 1 fire-water tub(s) by its eaves - it needs 2",
        "a fire-water tub at svg(464,210) stands by a plaster kura alone - a kura carries no tub",
    ]


# --- B19 size_hierarchy ---------------------------------------------------------------------------------------------------


def test_the_compound_ranks_its_buildings() -> None:
    stables = '<g data-kind="stables"><rect x="0" y="200" width="90" height="90" fill="#C9A57A"/></g>'
    barracks = '<g data-kind="barracks"><rect x="200" y="200" width="60" height="60" fill="#C9A57A"/></g>'
    text = _svg(stables, barracks)
    assert pr.size_hierarchy(pa.parse_svg(text)) == ["the stables (900 sq ft) is not smaller than the barracks (400 sq ft) - the compound ranks its buildings"]
    assert pr.size_hierarchy(pa.parse_svg(_svg(stables))) == []  # a pair with one kind absent is skipped


# --- B20 sheet_furniture --------------------------------------------------------------------------------------------------


def test_a_title_and_no_compass_or_key() -> None:
    title = '<text x="300" y="80" font-size="30" font-weight="bold">Title</text>'
    assert pr.sheet_furniture(_svg(title, '<text x="10" y="300" font-size="10">court</text>')) == []
    assert pr.sheet_furniture(_svg('<text x="300" y="200" font-size="30" font-weight="bold">Low</text>'))[0].startswith("no title block")  # below the precinct's top
    assert pr.sheet_furniture('<svg><text x="1" y="1" font-size="9" font-weight="bold">T</text></svg>') == []  # no precinct: no edge to stand above
    found = pr.sheet_furniture(_svg(title, '<text x="5" y="5" font-size="9">N</text>', '<text x="5" y="9" font-size="9">Legend:</text>', '<g id="compass-rose"><circle cx="5" cy="5" r="3"/></g>'))
    assert [f.split(" ")[1] for f in found] == ["compass", "key", "element"]


# --- roads.py: B21 and B23 --------------------------------------------------------------------------------------------------

WALL = (
    '<g stroke="#2D2A24" stroke-width="9" data-kind="compound wall">'
    '<line x1="0" y1="500" x2="280" y2="500"/><line x1="320" y1="500" x2="600" y2="500"/></g>'
)  # a 40 px (13.3 ft) opening, butt-capped, centered on x = 300


def _road(d: str, w: int, kind: str = "road") -> str:
    return f'<g data-kind="{kind}"><path d="{d}" stroke-width="{w}"/><path d="{d}" stroke-width="{w}"/></g>'


def test_a_road_end_meets_the_frame_a_gate_a_door_an_arch_or_a_road() -> None:
    text = _svg(WALL, _road("M 300 600 L 300 500", 30), viewbox="0 0 600 600")
    plan = pa.parse_svg(text)
    assert rd.roads_leave_the_frame(text, plan) == [] and len(rd.roads(text)) == 1
    stub = _svg(WALL, _road("M 300 560 L 300 500", 30))
    assert rd.roads_leave_the_frame(stub, pa.parse_svg(stub)) == ["a 10.0 ft road ends at svg(300,560) in the open - it runs off the frame or arrives at a gate, a door, an arch or another road"]
    door = '<rect x="95" y="300" width="10" height="4" fill="#4A3318" data-kind="door"/>'
    arch = '<g data-kind="torii"><line x1="190" y1="300" x2="210" y2="300"/></g>'
    spur = _svg(door, arch, _road("M 0 200 L 600 200", 20), _road("M 100 200 L 100 300", 6, "footpath"), _road("M 200 200 L 200 300", 6))
    assert rd.roads_leave_the_frame(spur, pa.parse_svg(spur)) == []
    no_frame = spur.replace(' viewBox="0 0 600 600"', "")
    assert len(rd.roads_leave_the_frame(no_frame, pa.parse_svg(no_frame))) == 2  # the trunk's ends meet nothing without a frame


def test_a_road_is_no_wider_than_the_gate_it_feeds() -> None:
    wide = _svg(WALL, _road("M 300 600 L 300 500", 50))
    assert rd.gate_feeds_its_road(wide, pa.parse_svg(wide)) == ["a 16.7 ft road meets a 13.3 ft gate at svg(300,500) - a road is no wider than the gate it feeds"]
    ok = _svg(WALL, _road("M 300 600 L 300 500", 43))  # 14.3 ft: within the foot of grain
    assert rd.gate_feeds_its_road(ok, pa.parse_svg(ok)) == []
    posts = '<g fill="#2D2A24" data-kind="main gate"><rect x="276" y="493" width="4" height="14"/><rect x="320" y="493" width="4" height="14"/></g>'
    gated = _svg(WALL, posts, _road("M 300 600 L 300 500", 40))
    assert len(rd.gates_met((300.0, 500.0), 20.0, pa.parse_svg(gated))) == 2  # the wall's opening and the main gate's passage
    assert rd.gate_passage_box(pa.parse_svg(wide)) is None


def test_road_geometry() -> None:
    dot = rd.Road(((0.0, 0.0),), 4.0)
    assert dot.distance(3, 4) == 5.0 and dot.half == 2.0
    assert rd._seg(3, 4, (0, 0), (0, 0)) == 5.0
    assert rd.Road(((0.0, 0.0), (10.0, 0.0)), 2.0).distance(5, 3) == 3.0


# --- palette.py: B22 --------------------------------------------------------------------------------------------------------


def test_a_kind_is_painted_in_its_role() -> None:
    hall = '<g data-kind="office hall"><rect x="0" y="200" width="300" height="80" fill="#DDB87A"/><rect x="10" y="210" width="60" height="40" fill="#DDB87A" data-kind="clerks\' room"/></g>'
    good = _svg(hall, '<rect x="400" y="200" width="60" height="60" fill="#F2EFE4" data-kind="granary"/>')
    assert pal.palette_roles(good) == []  # the clerks' room is a room of the hall; the granary in its kura form
    bad = _svg('<rect x="0" y="200" width="60" height="60" fill="#DDB87A" data-kind="stables"/>')
    assert pal.palette_roles(bad) == ["the stables at svg(0,200) is painted #DDB87A - its palette role is #C9A57A"]
    assert pal.main_fill("stables", _svg()) is None


# --- mapmatch.py: B24 -------------------------------------------------------------------------------------------------------


def _town(d: str, **manor: object) -> str:
    rec: dict[str, object] = {"x": 100, "y": 100, "w": 100, "h": 60}
    rec.update(manor)
    m = {"meta": {"ftpx": 1}, "manors": [rec, "junk"], "road": [[0, 160], [300, 160]], "tree_crowns": [100.0, 100.0, 5.0]}
    path = os.path.join(d, "town.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(m, fh)
    mm.load_map.cache_clear()
    return path


def _compound(*body: str) -> tuple[str, pa.ParsedPlan]:
    # the compound 300 x 180 px = 100 x 60 ft, two courts; its center (150, 90) = map (100, 100); 3 sheet px per map px
    ground = f'<rect x="0" y="0" width="300" height="90" fill="{COURT}" id="precinct"/><rect x="0" y="90" width="300" height="90" fill="{COURT}" id="precinct"/>'
    posts = '<g fill="#2D2A24" data-kind="main gate"><rect x="128" y="173" width="4" height="14"/><rect x="168" y="173" width="4" height="14"/></g>'
    text = f'<svg viewBox="-30 -30 360 300">{ground}{posts}' + "".join(body) + "</svg>"
    return text, pa.parse_svg(text)


ROAD_ON_MAP = _road("M -30 270 L 330 270", 9)  # map y = 100 + (270 - 90) / 3 = 160: the map's road


def test_the_compound_is_one_glyph_its_footprint_the_union_and_its_gate_agrees(tmp_path: object) -> None:
    path = _town(str(tmp_path), gate=[100, 130], gate_dir="south", gate_w=12)
    garden_tree = '<g fill="#7A8C5C"><circle cx="150" cy="60" r="10"/></g>'  # inside the compound: the glyph's own
    text, plan = _compound(garden_tree, ROAD_ON_MAP)
    on = OnMap(path, "manors", 100, 100, "precinct")
    assert mm.matches_map(plan, text, on) == []
    assert mm.subject_box(plan, "precinct") is not None and mm.subject_box(plan, "nothing") is None


def test_the_gate_rule_fires_on_side_place_and_width(tmp_path: object) -> None:
    text, plan = _compound(ROAD_ON_MAP)
    on = OnMap(_town(str(tmp_path), gate=[160, 100], gate_dir="east", gate_w=20), "manors", 100, 100, "precinct")
    found = mm.matches_map(plan, text, on)
    assert any(f.startswith("the main gate at svg(150,180)") and "from the map's gate at (160,100)" in f for f in found)
    assert "the main gate is on the sheet's S side; the map faces it east" in found
    assert "the main gate's passage is 12.0 ft on the sheet; the map records it 20.0 ft" in found
    nogate = text.replace('data-kind="main gate"', 'data-kind="side gate"')
    on2 = OnMap(_town(str(tmp_path), gate_dir="south"), "manors", 100, 100, "precinct")
    assert mm.matches_map(pa.parse_svg(nogate), nogate, on2)[-1].startswith("the map records the subject's gate, and the sheet draws no `main gate`")
    on3 = OnMap(_town(str(tmp_path)), "manors", 100, 100, "precinct")  # no gate recorded: nothing asked
    assert mm.matches_map(plan, text, on3) == []


def test_roads_are_read_under_every_key_both_ways(tmp_path: object) -> None:
    on = OnMap(_town(str(tmp_path)), "manors", 100, 100, "precinct")
    text, plan = _compound()  # no road drawn: the map's road crosses the frame
    assert mm.matches_map(plan, text, on) == ["the map's lane at map (0,160) = svg(-150,270) is inside the frame and not on the sheet"]
    off, plan2 = _compound(ROAD_ON_MAP, _road("M -30 -20 L 330 -20", 9))  # a second road the map does not draw
    assert mm.matches_map(plan2, off, on) == ["the road at svg(330,-20) runs 97 map px from every way on the map (the grain is 15)"]
    assert [f.pts for f in mm._features("ring_road", "lane", [[0, 0], [1, 1]])] == [((0.0, 0.0), (1.0, 1.0))]
    assert mm._features("road", "lane", []) == []


def test_way_and_side_helpers() -> None:
    assert mm.densify(((0.0, 0.0), (10.0, 0.0)), 4.0) == [(0.0, 0.0), (10 / 3, 0.0), (20 / 3, 0.0), (10.0, 0.0)]
    box = pa.Rect(0, 0, 100, 50)
    assert [mm.side_of(x, y, box) for x, y in ((50, 0), (50, 50), (0, 25), (100, 25))] == ["N", "S", "W", "E"]
    assert mm.sheet_ways(_svg(_road("M 0 0 L 5 5", 2), _road("M 0 0 L 5 5", 2))) == [((0.0, 0.0), (5.0, 5.0))]
    on = OnMap("x.json", "manors", 0, 0, "precinct")
    assert mm.subject_record({"manors": [{"x": 50, "y": 50}, 3]}, on, 15.0) is None


def test_maps_recording_reads_the_place_and_the_tier_key(tmp_path: object) -> None:
    root = str(tmp_path)
    os.makedirs(os.path.join(root, "pool", "towns", "kawa"))
    os.makedirs(os.path.join(root, "legacy-hand-authored-pool", "towns", "kawa"))
    with open(os.path.join(root, "pool", "towns", "kawa", "kawa.json"), "w", encoding="utf-8") as fh:
        json.dump({"manors": [{"x": 1, "y": 1}]}, fh)
    with open(os.path.join(root, "legacy-hand-authored-pool", "towns", "kawa", "kawa.json"), "w", encoding="utf-8") as fh:
        json.dump({"manors": []}, fh)
    mm.load_map.cache_clear()
    assert mm.maps_recording("kawa-magistracy", "magistracies", root) == ["pool/towns/kawa/kawa.json"]
    assert mm.maps_recording("kawa-shrine", "country-shrines", root) == []
    assert mm.maps_recording("kawa-magistracy", "magistracies", os.path.join(root, "nowhere")) == []


def test_the_on_map_opt_out() -> None:
    assert parse_on_map("**On map**: none - drawn as the type's exemplar, not the town's manor\n") is None
    assert declares("**On map**: none - why\n") and not declares("# notes\n")


# --- notes_census.py: B15b ----------------------------------------------------------------------------------------------------


def test_a_sheets_notes_counts_agree_with_what_it_draws() -> None:
    sheet = _svg(
        _tubs((1, 1), (2, 2)),
        _privy(10, 200),
        '<g data-kind="latrine"><rect x="30" y="200" width="15" height="15" fill="#7E726A"/><rect x="31" y="216" width="4" height="2" fill="#4A3318"/></g>',
        '<g data-kind="well"><rect x="100" y="200" width="22" height="22" fill="#9C8C70"/></g>',
    )
    assert N.sheet_counts(sheet) == {"tubs": 2, "privies": 2, "wells": 1}
    notes = (
        "# Sheet\n\n- **Two privies** and 3 fire-water tubs.\n- the house's two tubs stand by it.\n- a shrine takes 1-2 wells.\n\n"
        "- 2026-07 a journal entry: 9 tubs then.\n\n## Review log 2026-08-01\n\n5 wells.\n"
    )
    assert N.stale_sheet_counts(notes, sheet) == ["'3 fire-water tubs' - the sheet draws 2 tubs"]
    assert "9 tubs" not in N.sheet_prose(notes) and "5 wells" not in N.sheet_prose(notes)


# --- size_marks.py: B15c ------------------------------------------------------------------------------------------------------


def test_the_size_marks_list_every_sized_kind() -> None:
    sheet = _svg(
        '<g data-kind="landing"><rect x="0" y="200" width="30" height="30" data-kind="dock"/></g>',
        '<g data-kind="trees"><circle cx="50" cy="300" r="15"/></g>',
        _road("M 0 400 L 300 400", 12),
        '<text x="5" y="5" data-kind="alcove">alcove</text><text x="5" y="9" data-kind="-">x</text>',
    )
    rows = sm.mark_rows(sheet)
    assert {(r.tag, r.kind) for r in rows} == {("circle", "trees"), ("path", "road")}
    road = next(r for r in rows if r.kind == "road")
    assert (road.length_ft, road.stroke_ft) == (100.0, 4.0)
    assert sm.untabled_kinds(sheet) == ["alcove"]  # the landing is listed by its dock's row
    assert "marks (circles" in sm.render(rows) and "road" in sm.render(rows)


# --- compound_parts._family_privy: B17's fix --------------------------------------------------------------------------------


def test_the_family_privy_is_attached_to_the_house_at_its_rear_else_an_end() -> None:
    env = c.Envelope(w_ft=200.0, h_ft=200.0, divider_ft=100.0, gate_w_ft=13.0)
    spec = c.BuildingSpec("house", "lord", 60.0, 20.0, "inner", "N", feature="residence")
    free = c.Placed(spec, 50.0, 30.0)  # court south: its rear (north) is clear
    seat = cp._family_privy(env, [free], [], [], ())
    assert seat is not None and seat[1] == 25.0  # flush on the north face
    walled = c.Placed(spec, 50.0, 2.0)  # set against the north wall: the rear has no room, an end does
    seat2 = cp._family_privy(env, [walled], [], [], ())
    assert seat2 is not None and seat2[0] in (45.0, 110.0)
    boxed = [(0.0, 0.0, 200.0, 2.0 - 1e-9), (40.0, 0.0, 50.0, 30.0), (110.0, 0.0, 120.0, 30.0), (50.0, 22.0, 110.0, 30.0)]
    assert cp._family_privy(env, [walled], boxed, [], ()) is None
