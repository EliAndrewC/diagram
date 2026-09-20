"""The map declaration and the map check (feature 257): a sheet on a map matches the map in three directions,
within the map's measured grain, and says "on no map" otherwise."""

from __future__ import annotations

import json
import os

import pytest

from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import mapmatch as mm
from l7r.diagram.tools.pack_audit.onmap import OnMap, parse_on_map

COURT = "url(#court-earth)"
LINE = "**On map**: legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json - religious at (392, 1074) = hall"


def test_the_declaration_is_parsed_or_refused_by_name() -> None:
    assert parse_on_map("# notes\n\n**Form**: one roof\n") is None
    got = parse_on_map(f"# notes\n\n{LINE}\n")
    assert got == OnMap("legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json", "religious", 392.0, 1074.0, "hall")
    assert parse_on_map("**On map**: `a/b.json` - houses at (10.5, -3) = `subject`\n") == OnMap("a/b.json", "houses", 10.5, -3.0, "subject")
    with pytest.raises(ValueError, match="does not follow the grammar"):
        parse_on_map("**On map**: somewhere near the pond\n")


def test_read_on_map_reads_the_notes_beside_the_sheet(tmp_path: object) -> None:
    d = str(tmp_path)
    svg = os.path.join(d, "x.svg")
    open(svg, "w").close()
    assert pa.read_on_map(svg) is None
    with open(os.path.join(d, "x.notes.md"), "w", encoding="utf-8") as fh:
        fh.write(LINE + "\n")
    assert pa.read_on_map(svg) is not None
    assert pa.read_on_map(os.path.join(d, "not-an-svg.txt")) is None


# --- a synthetic map: 2 ft per px; the subject a 30 x 24 px hall at (100, 100) ---


def _manifest(d: str, **extra: object) -> str:
    m: dict[str, object] = {
        "meta": {"ftpx": 2},
        "religious": [{"kind": "shrine", "x": 100, "y": 100, "w": 30, "h": 24}],
        "wells": [{"x": 100, "y": 46, "r": 8}],  # 54 px north
        "torii": [[100.0, 122.0, 1]],  # 22 px south
        "tree_crowns": [300.0, 300.0, 6.0],  # far away
        "cemeteries": [],
        "lanes": [{"pts": [[160, 0], [160, 200]], "w": 6}],  # 60 px east, runs north-south
        "village_groves": [{"r": 14.0, "clumps": [[400, 400]]}],
    }
    m.update(extra)
    path = os.path.join(d, "map.json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(m, fh)
    mm.load_map.cache_clear()
    return path


def _sheet(*bodies: str, viewbox: str = "0 0 600 600") -> tuple[str, pa.ParsedPlan]:
    # the hall's center at sheet (300, 300) = map (100, 100); 6 sheet px per map px
    text = f'<svg viewBox="{viewbox}"><rect x="0" y="0" width="600" height="600" fill="{COURT}" id="precinct"/>' + "".join(bodies) + "</svg>"
    return text, pa.parse_svg(text)


HALL = '<rect x="210" y="228" width="180" height="144" fill="#DDB87A" id="hall"/>'  # 60 x 48 ft = 30 x 24 map px
WELL = '<rect x="292" y="-32" width="16" height="16" fill="#9C8C70" id="well"/>'  # map (100, 46): sheet y = 300 - 54*6 = -24
ARCH = '<rect x="280" y="420" width="40" height="24" fill="none" id="arch"/>'  # map (100, 122): sheet y = 432


def test_a_sheet_that_matches_its_map_is_quiet_and_one_on_no_map_is_skipped(tmp_path: object) -> None:
    path = _manifest(str(tmp_path))
    text, plan = _sheet(HALL, WELL, ARCH, viewbox="0 -60 600 540")  # the frame holds the well, the arch, not the lane (x = 660)
    on = OnMap(path, "religious", 100, 100, "hall")
    assert mm.matches_map(plan, text, on) == []
    assert mm.matches_map(plan, text, None) == []
    assert mm.skipped(None) and mm.skipped(on) is None


def test_direction_b_a_sheet_feature_the_map_lacks(tmp_path: object) -> None:
    path = _manifest(str(tmp_path))
    text, plan = _sheet(
        HALL,
        WELL,
        ARCH,
        '<g fill="#7A8C5C"><circle cx="60" cy="60" r="15"/></g>',
        '<rect x="450" y="100" width="100" height="200" fill="url(#bare-earth)" id="burial_ground"/>',
        viewbox="0 -60 600 540",
    )
    found = mm.matches_map(plan, text, OnMap(path, "religious", 100, 100, "hall"))
    assert any(f.startswith("tree at svg(60,60) has no tree on the map") for f in found)
    assert any(f.startswith("burial ground at svg(500,200) has no burial ground on the map") for f in found)
    assert len(found) == 2


def test_direction_c_a_map_feature_inside_the_frame_the_sheet_lacks(tmp_path: object) -> None:
    path = _manifest(str(tmp_path))
    text, plan = _sheet(HALL, ARCH, viewbox="0 -60 600 540")  # no well drawn
    found = mm.matches_map(plan, text, OnMap(path, "religious", 100, 100, "hall"))
    assert found == ["the map's water point at map (100,46) = svg(300,-24) is inside the frame and not on the sheet"]
    # widen the frame east and the lane comes into it
    text2, plan2 = _sheet(HALL, WELL, ARCH, viewbox="0 -60 720 540")
    found2 = mm.matches_map(plan2, text2, OnMap(path, "religious", 100, 100, "hall"))
    assert found2 == ["the map's lane at map (160,0) = svg(660,-300) is inside the frame and not on the sheet"]
    # a lane drawn there satisfies it
    text3, plan3 = _sheet(HALL, WELL, ARCH, '<rect x="650" y="-60" width="20" height="540" fill="#B89060" id="lane"/>', viewbox="0 -60 720 540")
    assert mm.matches_map(plan3, text3, OnMap(path, "religious", 100, 100, "hall")) == []


def test_direction_d_the_subjects_footprint(tmp_path: object) -> None:
    path = _manifest(str(tmp_path))
    text, plan = _sheet('<rect x="186" y="246" width="228" height="108" fill="#DDB87A" id="hall"/>', WELL, ARCH, viewbox="0 -60 600 540")  # 76 x 36 ft
    found = mm.matches_map(plan, text, OnMap(path, "religious", 100, 100, "hall"))
    assert found == ["the subject is 76 x 36 ft on the sheet; the map draws it 60 x 48 ft"]


def test_the_grain_is_the_edge(tmp_path: object) -> None:
    path = _manifest(str(tmp_path))
    on = OnMap(path, "religious", 100, 100, "hall")
    near = '<rect x="292" y="52" width="16" height="16" fill="#9C8C70" id="well"/>'  # 14 map px south of the map's well
    text, plan = _sheet(HALL, near, ARCH, viewbox="0 -60 600 540")
    assert mm.matches_map(plan, text, on) == []
    far = '<rect x="292" y="148" width="16" height="16" fill="#9C8C70" id="well"/>'  # 30 map px south: 22 px from the well's edge
    text2, plan2 = _sheet(HALL, far, ARCH, viewbox="0 -60 600 540")
    assert len(mm.matches_map(plan2, text2, on)) == 2  # (b) the sheet's well, (c) the map's


def test_the_refusals(tmp_path: object) -> None:
    d = str(tmp_path)
    text, plan = _sheet(HALL, WELL, ARCH, viewbox="0 -60 600 540")
    assert mm.matches_map(plan, text, OnMap(os.path.join(d, "none.json"), "religious", 100, 100, "hall"))[0].startswith("the declared manifest")
    path = _manifest(d)
    assert mm.matches_map(plan, text, OnMap(path, "religious", 500, 500, "hall")) == [f"no `religious` feature within 15 map px of (500, 500) in {path}"]
    assert mm.matches_map(plan, text, OnMap(path, "religious", 100, 100, "subject")) == ['no element marked id="subject" on the sheet - the declaration names it as the subject']
    text2, plan2 = _sheet(HALL, WELL, ARCH, '<rect x="10" y="10" width="20" height="20" fill="#B8C4D0" id="pond"/>', viewbox="0 -60 600 540")
    assert any('the sheet marks id="pond", a manifest key' in f for f in mm.matches_map(plan2, text2, OnMap(path, "religious", 100, 100, "hall")))
    text3 = text.replace(' viewBox="0 -60 600 540"', "")
    assert mm.matches_map(pa.parse_svg(text3), text3, OnMap(path, "religious", 100, 100, "hall")) == ["the sheet has no viewBox, so its frame cannot be laid on the map"]
    noscale = _manifest(d, meta={})  # last: it overwrites the manifest
    assert mm.matches_map(plan, text, OnMap(noscale, "religious", 100, 100, "hall")) == [f"the manifest {noscale} records no scale (meta.ftpx)"]


def test_features_of_every_recorded_shape() -> None:
    assert [(f.x, f.y, f.r) for f in mm._features("tree_crowns", "tree", [1.0, 2.0, 3.0, 4.0, 5.0, 6.0])] == [(1.0, 2.0, 3.0), (4.0, 5.0, 6.0)]
    assert [(f.x, f.y, f.r) for f in mm._features("village_groves", "tree", [{"r": 14, "clumps": [[1, 2]]}, "junk"])] == [(1.0, 2.0, 14.0)]
    assert [(f.x, f.y) for f in mm._features("torii", "arch", [[1, 2, 99]])] == [(1.0, 2.0)]
    assert [(f.x, f.y, f.w, f.h) for f in mm._features("pond", "water", [10, 20, 30, 40])] == [(25.0, 40.0, 30.0, 40.0)]
    assert mm._features("pond", "water", [10]) == []
    assert [(f.x, f.y, f.r) for f in mm._features("crescent_ponds", "water", [{"cx": 5, "cy": 6, "r": 7}])] == [(5.0, 6.0, 7.0)]
    assert [f.pts for f in mm._features("streams", "water", [{"poly": [[0, 0], [1, 1]]}, {"nothing": 1}, 3])] == [((0.0, 0.0), (1.0, 1.0))]
    assert mm._features("houses", "building", "not a list") == []
    one = mm.MapFeature("water", 0, 0, pts=((5.0, 5.0),))
    assert one.distance(5, 9) == 4.0 and one.in_frame((0, 0, 10, 10)) and not one.in_frame((20, 20, 30, 30))
    seg = mm.MapFeature("lane", 0, 0, pts=((-50.0, 5.0), (50.0, 5.0)))
    assert seg.in_frame((0, 0, 10, 10)) and not seg.in_frame((0, 20, 10, 30))
    assert mm._seg_distance(0, 0, (3, 4), (3, 4)) == 5.0 and not mm._seg_crosses((3, 4), (3, 4), (0, 0, 10, 10))
    rect = mm.MapFeature("building", 10, 10, 4, 4)
    assert rect.distance(10, 10) == 0.0 and rect.distance(15, 10) == 3.0 and rect.in_frame((0, 0, 9, 9)) and not rect.in_frame((20, 20, 30, 30))
