"""The checks feature 254 added to `pack_audit/shared.py`, on synthetic sheets: each branch of each check."""

from __future__ import annotations

import os

import pytest

from l7r.diagram.buildings import types as _bt
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import labels as L
from l7r.diagram.tools.pack_audit import shared as s

COURT = "url(#court-earth)"
BLDG = "#DDB87A"


def _rect(x: float, y: float, w: float, h: float, fill: str, ident: str = "") -> str:
    tag = f' id="{ident}"' if ident else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{tag}/>'


def _svg(*bodies: str, viewbox: str = "0 0 400 400") -> str:
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}">' + "".join(bodies) + "</svg>"


PRECINCT = _rect(20, 20, 360, 360, COURT, "precinct")
SCALE = '<text x="60" y="15" text-anchor="middle" font-size="10">30 ft</text><text x="60" y="26" font-size="8">(3 px = 1 ft)</text>'


def _plan(*bodies: str, viewbox: str = "0 0 400 400") -> tuple[str, pa.ParsedPlan]:
    text = _svg(PRECINCT, *bodies, viewbox=viewbox)
    return text, pa.parse_svg(text)


# --- structures_overlap ---


def test_overlap_flags_a_substantial_lap_and_allows_containment_and_a_corridor_end() -> None:
    _, plan = _plan(_rect(40, 40, 100, 60, BLDG), _rect(100, 50, 100, 60, BLDG))  # lap 40x50 of 6000 = 33%
    assert len(s.structures_overlap(plan)) == 1 and "overlap by" in s.structures_overlap(plan)[0]
    _, plan = _plan(_rect(40, 40, 100, 60, BLDG), _rect(50, 50, 20, 20, "#E8D2A8"))  # an engawa strip inside
    assert s.structures_overlap(plan) == []
    _, plan = _plan(_rect(40, 40, 100, 60, BLDG), _rect(135, 60, 60, 12, BLDG))  # a corridor lapping 5 px into the block
    assert s.structures_overlap(plan) == []
    _, plan = _plan(_rect(40, 40, 100, 60, BLDG), _rect(140, 40, 100, 60, BLDG))  # flush neighbors
    assert s.structures_overlap(plan) == []
    _, plan = _plan(_rect(40, 40, 100, 60, BLDG), _rect(60, 120, 100, 60, BLDG))  # no lap in y
    assert s.structures_overlap(plan) == []


# --- scale_bar_present ---


def test_scale_bar_needs_both_labels() -> None:
    _, plan = _plan(SCALE)
    assert s.scale_bar_present(plan) == []
    _, plan = _plan('<text x="60" y="15" font-size="10">30 ft</text>')
    assert s.scale_bar_present(plan) == ["no `(3 px = 1 ft)` note"]
    _, plan = _plan()
    assert len(s.scale_bar_present(plan)) == 2


# --- viewbox_cropped / ink_bounds ---


def test_crop_reads_every_kind_of_ink_and_skips_definitions_and_the_parchment() -> None:
    body = (
        '<rect x="0" y="0" width="400" height="400" fill="#EFE3C2"/>'  # parchment: not ink
        '<defs><pattern id="p"><rect x="-500" y="-500" width="5" height="5" fill="#000"/></pattern></defs>'
        '<symbol id="s"><line x1="-900" y1="0" x2="10" y2="0"/></symbol>'
        '<g transform="translate(100, 100)"><circle cx="0" cy="0" r="5" fill="#000"/><ellipse cx="10" cy="10" rx="4" ry="2"/></g>'
        '<line x1="30" y1="30" x2="60" y2="30"/>'
        '<path d="M 200 350 L 200 380 q 3 -8 -2 -14 H 210 V 385 A 5 5 0 0 1 215 390"/>'
        '<text x="200" y="40" text-anchor="middle" font-size="10">title</text>'
        '<text x="390" y="60" text-anchor="end" font-size="10">right</text>'
        '<text x="30" y="60" font-size="10"> </text>'
        '<g data-kind="hall"><text font-size="10">a caption declared, not yet placed</text></g>'  # feature 286: no ink until placed
    )
    text, plan = _plan(body)
    x1, y1, x2, y2 = s.ink_bounds(text, plan, 400 * 400)
    assert x1 == 20.0 and y1 == 20.0 and x2 == 390.0 and y2 == 390.0  # the precinct rect, the end-anchored text's right edge, the arc's end
    assert s.viewbox_cropped(text, plan) == []
    text, plan = _plan(body.replace('width="400" height="400" fill="#EFE3C2"', 'width="500" height="400" fill="#EFE3C2"'), viewbox="0 0 500 400")
    assert s.viewbox_cropped(text, plan) == ["right margin is 110 px of empty parchment - crop the viewBox to ~25 px"]
    assert s.viewbox_cropped("<svg>" + PRECINCT + "</svg>", plan) == ["no viewBox on the sheet"]
    assert s.ink_bounds("<svg><rect x=1></svg>", plan) is None  # not XML
    empty = pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT, "precinct")))
    assert s.ink_bounds('<svg viewBox="0 0 400 400"><rect x="0" y="0" width="400" height="400" fill="url(#court-earth)" id="precinct"/></svg>', empty, 400 * 400) is None
    assert s.viewbox_cropped('<svg viewBox="0 0 400 400"><rect x="0" y="0" width="400" height="400" fill="url(#court-earth)" id="precinct"/></svg>', empty) == ["nothing drawn to crop to"]


def test_path_points_take_absolute_commands_only() -> None:
    xs, ys = s._path_points("M 10 20 l 5 5 L 30 40 C 1 2 3 4 50 60 T 70 80 H 90 V 100 A 1 1 0 0 0 110 120 Z")
    assert (max(xs), max(ys)) == (110.0, 120.0) and (min(xs), min(ys)) == (1.0, 2.0)
    assert s._path_points("m 1 2 q 3 4 5 6") == ([], [])


# --- coverage_band / perimeter_hugging ---


def test_coverage_band_and_hugging_floor_read_the_grids() -> None:
    _, plan = _plan(_rect(20, 20, 360, 130, BLDG))  # 36% built, hugging the north wall
    assert s.coverage_band(plan) == [] and s.perimeter_hugging(plan) == []
    _, plan = _plan(_rect(20, 20, 360, 200, BLDG))  # 56%
    assert "coverage is 56%" in s.coverage_band(plan)[0]
    _, plan = _plan(_rect(20, 20, 60, 60, BLDG))  # 3%
    assert "coverage is 3%" in s.coverage_band(plan)[0]
    # the fix it names (feature 433 D3): never a smaller wall to hide slack, the envelope following a research-sized house
    assert "never shrink the envelope to hide slack" in s.coverage_band(plan)[0]
    assert "a wall moves in only when a house drawn at the record's size leaves the sheet under the band" in s.coverage_band(plan)[0]
    assert "DEVIATION recorded on 0116's drawing page" in s.coverage_band(plan)[0]
    _, plan = _plan(_rect(120, 120, 160, 160, BLDG))  # an island in the center
    assert "of building footprint lies within 25 ft" in s.perimeter_hugging(plan)[0]


# --- gate_widths ---


def _wall(*gaps: tuple[float, float]) -> str:
    """A south wall from x=20 to 380 at y=380 with openings between the given x spans, 9 px stroke."""
    xs = [20.0]
    segs = []
    for a, b in gaps:
        segs.append((xs[-1], a))
        xs.append(b)
    segs.append((xs[-1], 380.0))
    lines = "".join(f'<line x1="{a}" y1="380" x2="{b}" y2="380"/>' for a, b in segs)
    return f'<g stroke="#2D2A24" stroke-width="9">{lines}</g>'


def test_gate_widths_accept_a_passage_and_refuse_a_slit_or_a_structure_width() -> None:
    _, plan = _plan(_wall((100, 140)))  # 40 px = 13.3 ft, less the caps
    assert s.gate_widths(plan) == []
    _, plan = _plan(_wall((100, 110)))
    assert "too narrow" in s.gate_widths(plan)[0]
    _, plan = _plan(_wall((100, 170)))  # 70 px ~ 20 ft, nothing standing in it
    assert "a structure's width" in s.gate_widths(plan)[0]
    _, plan = _plan(_wall((100, 170)), _rect(95, 360, 80, 40, BLDG))  # a structure spans the break (Ubame's parley room)
    assert s.gate_widths(plan) == []


def test_gate_widths_on_a_vertical_wall() -> None:
    wall = '<g stroke="#2D2A24" stroke-width="9"><line x1="380" y1="20" x2="380" y2="100"/><line x1="380" y1="170" x2="380" y2="380"/></g>'
    _, plan = _plan(wall)
    assert "a structure's width" in s.gate_widths(plan)[0]
    _, plan = _plan(wall, _rect(360, 95, 40, 80, BLDG))
    assert s.gate_widths(plan) == []


# --- two_court_zoning ---


# the divider broken by its middle gate, x 191..209 (6 ft)
DIVIDER = '<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="200" x2="191" y2="200"/><line x1="209" y1="200" x2="380" y2="200"/></g>'
SEALED = '<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="200" x2="380" y2="200"/></g>'
SAND_SOUTH = _rect(100, 250, 200, 60, "url(#oshirasu-sand)")
SAND_NORTH = _rect(100, 60, 200, 60, "url(#oshirasu-sand)")


def test_two_court_zoning_wants_a_divider_a_court_and_a_gate_on_the_same_side() -> None:
    _, plan = _plan(_wall((180, 220)), DIVIDER, SAND_SOUTH)
    assert s.two_court_zoning(plan) == []
    _, plan = _plan(_wall((180, 220)), DIVIDER, SAND_NORTH)
    assert "far side of the divider" in s.two_court_zoning(plan)[0]
    _, plan = _plan(_wall((180, 220)), SAND_SOUTH)
    assert "no court divider" in s.two_court_zoning(plan)[0]
    _, plan = _plan(_wall((180, 220)), DIVIDER)
    assert "no hearing court" in s.two_court_zoning(plan)[0]
    _, plan = _plan(DIVIDER, SAND_SOUTH)
    assert "no gate opening" in s.two_court_zoning(plan)[0]
    vertical = '<g stroke="#3F3A30" stroke-width="6"><line x1="200" y1="20" x2="200" y2="180"/><line x1="200" y1="200" x2="200" y2="380"/></g>'
    _, plan = _plan(_wall((180, 220)), vertical, SAND_NORTH)
    assert s.two_court_zoning(plan) == []


def test_two_court_zoning_wants_a_gate_in_the_divider() -> None:
    """Feature 267 pass 3: the placer's draft drew its divider unbroken, the house sealed from the office. A divider
    needs a passage of at least GATE_MIN_FT; a hairline break is not one."""
    _, plan = _plan(_wall((180, 220)), SEALED, SAND_SOUTH)
    assert "no gate" in s.two_court_zoning(plan)[0]
    narrow = '<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="200" x2="199" y2="200"/><line x1="203" y1="200" x2="380" y2="200"/></g>'
    _, plan = _plan(_wall((180, 220)), narrow, SAND_SOUTH)
    assert "no gate" in s.two_court_zoning(plan)[0]
    _, plan = _plan(_wall((180, 220)), DIVIDER, SAND_SOUTH)
    assert s.divider_gates_ft(plan) == [6.0]


@pytest.mark.parametrize(("w", "h", "inside"), [(30, 15, True), (15, 30, True), (50, 15, False)])
def test_band_holds_is_reachable_from_the_declaration(w: float, h: float, inside: bool) -> None:
    from l7r.diagram.buildings.types import Band

    assert Band(w=(20.0, 40.0), h=(10.0, 20.0)).holds(w, h) is inside


# --- the country shrine's checks, on the synthetic sheet and its variations ---

_FIX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "fixtures")


def _shrine() -> tuple[str, pa.ParsedPlan]:
    with open(os.path.join(_FIX, "shrine-synthetic.svg"), encoding="utf-8") as fh:
        text = fh.read()
    return text, pa.parse_svg(text)


def test_the_synthetic_shrine_passes_its_four_checks() -> None:
    text, plan = _shrine()
    assert s.sanctuary_on_axis(plan) == [] and s.arch_on_approach(plan) == [] and s.well_clear_of_arch(plan) == [] and s.no_precinct_enclosure(text, plan) == []
    assert plan.by_id("hall")[0].ident == "hall" and not plan.by_id("hall")[0].precinct


def test_shrine_checks_name_a_missing_declaration() -> None:
    text, _ = _shrine()
    bare = pa.parse_svg(text.replace('id="approach"', "").replace('id="arch"', ""))
    assert "declares no approach / arch" in s.sanctuary_on_axis(bare)[0]
    assert "declares no approach / arch" in s.arch_on_approach(bare)[0]
    assert "declares no approach / arch" in s.well_clear_of_arch(bare)[0]
    no_well = pa.parse_svg(text.replace('fill="#9C8C70"', 'fill="#000001"').replace('id="well"', ""))
    assert "no well on the sheet" in s.well_clear_of_arch(no_well)[0]


def test_sanctuary_in_front_of_the_hall_and_a_horizontal_axis() -> None:
    text, _ = _shrine()
    front = pa.parse_svg(text.replace('<rect x="190" y="100" width="20" height="20"', '<rect x="190" y="320" width="20" height="20"'))
    assert any("BEHIND the hall" in f for f in s.sanctuary_on_axis(front))
    # rotate the composition: an approach running east-west, the sanctuary west of the hall
    wide = (
        text.replace('<rect x="185" y="270" width="30" height="200" fill="none" id="approach"/>', '<rect x="260" y="180" width="100" height="30" fill="none" id="approach"/>')
        .replace('<rect x="170" y="458" width="60" height="24" fill="none" id="arch"/>', '<rect x="340" y="170" width="24" height="60" fill="none" id="arch"/>')
        .replace('<rect x="190" y="100" width="20" height="20"', '<rect x="100" y="185" width="20" height="20"')
    )
    assert s.sanctuary_on_axis(pa.parse_svg(wide)) == []
    off = pa.parse_svg(wide.replace('<rect x="100" y="185" width="20" height="20"', '<rect x="100" y="120" width="20" height="20"'))
    assert any("off the approach axis" in f for f in s.sanctuary_on_axis(off))


def test_arch_inside_the_precinct_and_a_wall_on_the_boundary() -> None:
    text, _ = _shrine()
    inside = pa.parse_svg(text.replace('<rect x="170" y="458" width="60" height="24" fill="none" id="arch"/>', '<rect x="170" y="300" width="60" height="24" fill="none" id="arch"/>'))
    findings = s.arch_on_approach(inside)
    assert any("inside the precinct" in f for f in findings) and not any("straddle" in f for f in findings)
    walled = text.replace(
        '<g id="fence" stroke="#7A6A4A" stroke-width="2" fill="none">',
        '<g id="fence" stroke="#7A6A4A" stroke-width="2" fill="none"><g stroke="#2D2A24" stroke-width="9"><line x1="40" y1="70" x2="360" y2="70"/></g>',
    )
    assert any("compound wall stroke" in f for f in s.no_precinct_enclosure(walled, pa.parse_svg(walled)))
    interior_wall = text.replace('<rect x="240" y="350"', '<g stroke="#2D2A24" stroke-width="9"><line x1="100" y1="250" x2="130" y2="250"/></g><rect x="240" y="330"')
    assert s.no_precinct_enclosure(interior_wall, pa.parse_svg(interior_wall)) == []  # a wall stroke away from the boundary is not the precinct's edge


def test_a_fence_ringing_the_precinct_is_reported_and_one_ringing_the_sanctuary_alone_is_not() -> None:
    """Feature 268 (D7): a village shrine's ground is unenclosed - its arch and its wood mark it. The
    synthetic sheet's fence rings the sanctuary alone (a richer shrine's donation) and passes; the same
    fence carried round the whole precinct takes in the hall and is reported."""
    text, plan = _shrine()
    assert s.no_precinct_enclosure(text, plan) == []
    ring = '<g id="fence" stroke="#7A6A4A" stroke-width="2" fill="none"><line x1="40" y1="70" x2="360" y2="70"/><line x1="40" y1="70" x2="40" y2="470"/><line x1="360" y1="70" x2="360" y2="470"/><line x1="40" y1="470" x2="360" y2="470"/></g>'
    fenced = text.replace(text[text.index('<g id="fence"') : text.index("</g>", text.index('<g id="fence"')) + 4], ring)
    assert any("a fence rings the precinct" in f for f in s.no_precinct_enclosure(fenced, pa.parse_svg(fenced)))


# --- the tag pairing and the program checks (labels.py) ---


def _text(x: float, y: float, s: str, size: int = 11, kind: str = "") -> str:
    tag = f' data-kind="{kind}"' if kind else ""
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}"{tag}>{s}</text>'


def _kinded(kind: str, *bodies: str) -> str:
    return f'<g data-kind="{kind}">' + "".join(bodies) + "</g>"


def test_a_footprint_is_the_largest_structure_its_kind_tags_and_ground_has_none() -> None:
    """Feature 286 (D7): the pairing reads the sheet's tags, never where a caption stands. A building's own parts carry
    its tag and are smaller than it; a kind drawn only as ground has no footprint; an untagged rect names nothing."""
    _, plan = _plan(
        _kinded("hall", _rect(40, 40, 200, 100, BLDG), _rect(60, 60, 30, 20, "#E8D2A8")),  # the hall and its porch strip
        _rect(260, 40, 60, 60, BLDG),  # untagged
        _kinded("court", _rect(40, 200, 100, 100, "url(#court-earth)")),
    )
    hall = L.footprint(plan, "hall")
    assert hall is not None and (hall.w, hall.h) == (200.0, 100.0), "the building, not its strip"
    assert L.footprint(plan, "court") is None and L.footprint(plan, "shed") is None


def test_program_and_band_checks_over_a_tiny_declaration() -> None:
    types = _bt.parse_types(
        [
            {
                "tier": "huts",
                "title": "Huts",
                "program": "Hut",
                "hand_drawn": True,
                "checks": [],
                "required": [
                    {"id": "hut", "label": "^hut$", "band_ft": {"w": [10, 20], "h": [10, 20]}, "class": "guess", "why": "a hut"},
                    {"id": "yard", "label": "^yard$", "band_ft": {}, "class": "guess", "why": "ground"},
                    {"id": "shed", "label": "^shed$", "band_ft": {"area": [50, 200]}, "optional": True, "class": "guess", "why": "a shed"},
                    {"id": "loft", "label": "^loft$", "band_ft": {"w": [5, 8], "h": [5, 8]}, "forms": {"one roof": None}, "class": "guess", "why": "a loft"},
                ],
            }
        ]
    )[0]
    _, plan = _plan(_kinded("hut", _rect(40, 40, 45, 45, BLDG), _text(62, 66, "hut")), _text(200, 300, "yard"), _text(62, 300, "loft"))
    assert L.check_program(plan, types, None) == []  # loft is labeled (on open ground), shed optional
    assert L.check_program(plan, types, "one roof") == []
    assert "no `hut`" in L.check_program(pa.parse_svg(_svg(PRECINCT)), types, None)[0]
    assert L.check_bands(plan, types, None) == []  # 15 x 15 ft in band; yard presence-only; loft untagged, nothing to measure
    _, big = _plan(_kinded("hut", _rect(40, 40, 90, 45, BLDG)), _text(300, 300, "hut", kind="hut"), _kinded("shed", _rect(200, 200, 60, 60, BLDG), _text(230, 230, "shed")))
    findings = L.check_bands(big, types, None)
    assert any("`hut` (hut)" in f and "w 10-20 by h 10-20 ft" in f for f in findings), "measured by its tag, its caption 70 ft off"
    assert any("`shed`" in f and "area 50-200 sq ft" in f for f in findings)  # 20 x 20 ft = 400
    _, untagged = _plan(_rect(40, 40, 90, 45, BLDG), _text(85, 66, "hut"))
    assert L.check_bands(untagged, types, None) == [], "a caption standing on a footprint pairs with nothing: only a tag does"


def test_fence_check_ignores_a_court_divider_stroke() -> None:
    """A divider band is a wall band of another color; the fence check reasons only about the compound stroke."""
    text, plan = _plan('<g id="fence" stroke="#7A6A4A" stroke-width="2"><line x1="20" y1="20" x2="380" y2="20"/></g>' + DIVIDER)
    assert s.no_precinct_enclosure(text, plan) == []


# --- trees overlap nothing (feature 257) ---

_CANOPY = '<g fill="#7A8C5C"><circle cx="{x}" cy="{y}" r="{r}"/></g>'


def test_a_tree_on_open_ground_is_fine_and_one_on_anything_else_is_named() -> None:
    _, plan = _plan(
        _rect(0, 0, 400, 400, "url(#court-earth)", "precinct"),
        _rect(100, 100, 60, 40, "#DDB87A", "hall"),
        '<g id="fence" stroke="#7A6A4A" fill="none"><line x1="20" y1="300" x2="380" y2="300"/></g>',
        '<text x="300" y="60" font-size="10">a label</text>',
        _CANOPY.format(x=40, y=40, r=15),  # on the gravel
        _CANOPY.format(x=95, y=120, r=15),  # 10 px into the hall
        _CANOPY.format(x=200, y=305, r=15),  # across the fence line
        _CANOPY.format(x=305, y=57, r=15),  # over a caption: the placer's to avoid, not a finding
    )
    findings = s.trees_overlap(plan)
    assert not [f for f in findings if "svg(40,40)" in f]
    assert any("svg(95,120)" in f and "into a building" in f for f in findings)
    assert any("svg(200,305)" in f and "into the fence" in f for f in findings)
    assert not [f for f in findings if "svg(305,57)" in f], "a caption under a canopy is the placer's to avoid, not a check's (feature 286)"


def test_crowns_may_overlap_but_a_tree_is_not_drawn_on_another() -> None:
    """Feature 270 (the GM 2026-09-27: "tree crowns may overlap, I never said they couldn't"): crowns overlapping each
    other are a closed canopy, not a finding; one tree drawn on top of another - trunks within a third of the smaller
    crown's radius, feature 257's "two lie on top of each other" - still is (the threshold a guess, research R2)."""
    _, plan = _plan(
        _rect(0, 0, 400, 400, "url(#court-earth)", "precinct"),
        _CANOPY.format(x=50, y=50, r=15),
        _CANOPY.format(x=65, y=50, r=15),  # half over the other: a closed canopy, fine
        _CANOPY.format(x=200, y=50, r=15),
        _CANOPY.format(x=203, y=50, r=15),  # trunks 3 px apart, inside a third of 15: a duplicated tree
    )
    findings = s.trees_overlap(plan)
    assert not [f for f in findings if "svg(50,50)" in f or "svg(65,50)" in f]
    assert len(findings) == 1 and "drawn on top of" in findings[0] and "svg(200,50)" in findings[0]


def test_a_tree_may_stand_on_a_garden_bed_and_over_no_glyph_or_tub() -> None:
    _, plan = _plan(
        _rect(0, 0, 400, 400, "url(#court-earth)", "precinct"),
        _rect(20, 20, 100, 100, "url(#garden-stipple)"),
        '<rect x="200" y="200" width="15" height="15" fill="#9C8C70" id="well"/><circle cx="207" cy="207" r="4" fill="#3A3A34"/>',
        '<g fill="#8FB0C6"><circle cx="300" cy="300" r="3.8"/></g>',
        _CANOPY.format(x=60, y=60, r=20),  # on the bed
        _CANOPY.format(x=212, y=195, r=14),  # over the well and its glyph
        _CANOPY.format(x=296, y=296, r=12),  # over the tub
    )
    findings = s.trees_overlap(plan)
    assert not [f for f in findings if "svg(60,60)" in f]
    assert any("svg(212,195)" in f for f in findings) and any("svg(296,296)" in f and "tub" in f for f in findings)


def _kind_types() -> _bt.BuildingType:
    return _bt.parse_types(
        [{"tier": "stores", "title": "Stores", "program": "Store", "hand_drawn": True, "checks": [], "required": [{"id": "store", "kind": "granary", "band_ft": {"w": [10, 20], "h": [10, 20]}}]}]
    )[0]


def test_a_kind_item_is_found_by_the_sheet_s_tag_not_by_its_label_text() -> None:
    """Feature 262 FR-003a: a program item that names a kind is on the sheet when an element carries that kind, and
    its band is measured on the largest structure tagged with that kind (feature 286) - whatever the label says."""
    types = _kind_types()
    _, plan = _plan('<g data-kind="granary">' + _rect(40, 40, 45, 45, BLDG) + _text(62, 66, "rice store") + "</g>")
    assert L.check_program(plan, types, None) == [] and L.check_bands(plan, types, None) == []
    _, untagged = _plan(_rect(40, 40, 45, 45, BLDG), _text(62, 66, "granary"))
    assert L.check_program(untagged, types, None) == ['no `store` on the sheet (an element tagged data-kind="granary", or an element marked id="store")']
    _, big = _plan('<g data-kind="granary">' + _rect(40, 40, 90, 45, BLDG) + _text(85, 66, "rice store") + "</g>")
    from l7r.diagram.interactive.compound_kinds import COMPOUND_CLASSES

    found = L.check_bands(big, types, None)
    assert len(found) == 1 and "`store` (granary) is 30 x 15 ft" in found[0] and "(per statement: " + " ".join(COMPOUND_CLASSES["granary"].guesses) in found[0]


def test_a_stroke_is_ink_half_its_width_either_side() -> None:
    """Feature 372 wave 103: a stroked road or line is ink out to half its stroke on each side of its centerline, so a wide
    road at a sheet's edge is not counted as an empty margin; an unstroked path keeps its points."""
    text, plan = _plan('<path d="M 20 385 L 380 385" stroke="#B89060" stroke-width="40"/>')
    assert s.ink_bounds(text, plan, 400 * 400)[3] == 405.0
    text, plan = _plan('<line x1="380" y1="385" x2="20" y2="385" stroke-width="40"/>')
    assert s.ink_bounds(text, plan, 400 * 400)[3] == 405.0
    text, plan = _plan('<path d="M 20 385 L 380 385" fill="#000" stroke="none" stroke-width="40"/>')
    assert s.ink_bounds(text, plan, 400 * 400)[3] == 385.0


def _one_roof(kitchen: tuple[float, float], rooms: tuple[float, float], vertical: bool = False) -> tuple[str, pa.ParsedPlan]:
    """A one-roof building 60 x 30 px (20 x 10 ft) with its kitchen and rooms as tagged parts at the given spans."""

    def part(kind: str, a: float, b: float) -> str:
        box = (100, 100 + a, 30, b - a) if vertical else (100 + a, 100, b - a, 30)
        return f'<g data-kind="{kind}" data-part-of="hall and dwelling"><rect x="{box[0]}" y="{box[1]}" width="{box[2]}" height="{box[3]}" fill="none"/></g>'

    hall = _rect(100, 100, 30, 60, BLDG, "hall") if vertical else _rect(100, 100, 60, 30, BLDG, "hall")
    body = f'<g data-kind="hall and dwelling">{hall}</g>' + part("kitchen", *kitchen) + part("the monk's rooms", *rooms)
    return _plan(body)


def test_the_hall_stands_at_an_end_of_the_one_roof() -> None:
    """0221's drawing page: the monk's dwelling is one end of the hall's own building - never the hall between its rooms."""
    text, plan = _one_roof((0, 12), (40, 60))
    assert any("between the dwelling's rooms" in f for f in s.hall_at_an_end(text, plan)), "rooms on both sides: the hall is in the middle"
    assert s.hall_at_an_end(*_one_roof((0, 12), (12, 30))) == [], "both parts at the west end: the hall at the east end"
    assert any("between" in f for f in s.hall_at_an_end(*_one_roof((0, 12), (40, 60), vertical=True))), "a building drawn north-south reads the same"
    assert s.hall_at_an_end(*_one_roof((0, 28), (32, 60))) == [], "a gap under 6 ft is a partition, not a hall"
    bare_text, bare = _plan(f'<g data-kind="hall and dwelling">{_rect(100, 100, 60, 30, BLDG, "hall")}</g>')
    assert s.hall_at_an_end(bare_text, bare) == [], "the two-buildings form tags no part of the hall's building"
    porch = '<g data-kind="genkan" data-part-of="hall and dwelling"><rect x="300" y="300" width="9" height="9" fill="none"/></g>'
    green_text, _ = _one_roof((0, 12), (12, 30))
    with_porch = green_text.replace("</svg>", porch + "</svg>")
    assert s.hall_at_an_end(with_porch, pa.parse_svg(with_porch)) == [], "a tagged part off the building is not one of its spans"
    no_hall = _plan(_rect(100, 100, 60, 30, BLDG))
    assert s.hall_at_an_end(*no_hall) == [], "no declared hall: sanctuary_on_axis names that"


def test_hoshigaoka_draws_its_hall_at_an_end_and_its_old_sheet_did_not() -> None:
    with open(os.path.join(_FIX, "hoshigaoka-hall-in-the-middle-red.svg"), encoding="utf-8") as fh:
        red = fh.read()
    assert s.hall_at_an_end(red, pa.parse_svg(red)), "the fixture is the sheet before wave 123"
    with open(os.path.join(os.path.dirname(_FIX), "..", "pool", "country-shrines", "hoshigaoka-shrine", "hoshigaoka-shrine.svg"), encoding="utf-8") as fh:
        sheet = fh.read()
    assert s.hall_at_an_end(sheet, pa.parse_svg(sheet)) == []


def test_a_compound_draws_one_shrine() -> None:
    """0218's drawing page: one modest shrine, however many a real office kept (feature 374 wave 123, Hayakawa)."""
    with open(os.path.join(_FIX, "hayakawa-two-shrines-red.svg"), encoding="utf-8") as fh:
        red = fh.read()
    assert s.one_compound_shrine(red) == ['2 compound shrines drawn - a compound draws one modest shrine; enshrine a second god in its hall, or declare its rolled own shrine data-form="own shrine"']
    rolled = red.replace('<!-- River-kami shrine -->\n  <g data-kind="compound shrine">', '<!-- River-kami shrine -->\n  <g data-kind="compound shrine" data-form="own shrine">')
    assert rolled != red and s.one_compound_shrine(rolled) == [], "a second kami's own shrine, where its roll says so, is declared and passes"
    with open(os.path.join(os.path.dirname(_FIX), "..", "pool", "magistracies", "hayakawa-magistracy", "hayakawa-magistracy.svg"), encoding="utf-8") as fh:
        assert s.one_compound_shrine(fh.read()) == [], "its arch, tagged a part of the shrine, is not a second shrine"


def test_a_stable_parts_its_length_into_one_ken_stalls() -> None:
    """0108's drawing page: a warrior's stall one bay, one ken (~6 ft) wide (feature 374 wave 126)."""

    def stable(lines: str, w: float = 84, h: float = 48) -> str:
        return _svg(f'<g data-kind="stables"><rect x="0" y="0" width="{w}" height="{h}" fill="#C9A57A" stroke="#6B4F2A"/>{lines}</g>')

    def cut(at: float, vertical: bool = True) -> str:
        return f'<line x1="{at}" y1="0" x2="{at}" y2="30"/>' if vertical else f'<line x1="0" y1="{at}" x2="30" y2="{at}"/>'

    assert s.stall_width(stable(cut(30) + cut(48) + cut(66))) == [], "a grooms' room and three 6 ft stalls"
    assert "9.3, 9.3, 9.3 ft" in s.stall_width(stable(cut(28) + cut(56)))[0], "three ~9.3 ft stalls: the old sheets'"
    assert "28.0 ft" in s.stall_width(stable(""))[0], "no partition: no stalls"
    tall = _svg('<g data-kind="stables"><rect x="0" y="0" width="48" height="84" fill="#C9A57A" stroke="#6B4F2A"/>' + cut(30, False) + cut(48, False) + cut(66, False) + "</g>")
    assert s.stall_width(tall) == [], "a stable drawn north-south reads the same"


def test_postern_approach_keeps_a_way_through_each_opening() -> None:
    """Feature 374 batch 4 (plan R4-2): the county draft's south postern was sealed by two buildings against the wall."""
    _, plan = _plan(_wall((100, 140)))
    assert s.postern_approach(plan) == []  # nothing near: clear
    _, plan = _plan(_wall((100, 140)), _rect(80, 340, 34, 34, BLDG), _rect(116, 340, 40, 34, BLDG))  # two blocks seal it, 2 px apart
    assert "seals the way through" in s.postern_approach(plan)[0]
    _, plan = _plan(_wall((100, 140)), _rect(80, 340, 34, 34, BLDG))  # one block leaves 26 px (~8.7 ft) clear
    assert s.postern_approach(plan) == []
    _, plan = _plan(_wall((100, 170)), _rect(95, 360, 80, 40, BLDG))  # a block straddling the wall's ink: the gap-fill idiom
    assert s.postern_approach(plan) == []
    vertical = '<g stroke="#2D2A24" stroke-width="9"><line x1="380" y1="20" x2="380" y2="100"/><line x1="380" y1="140" x2="380" y2="380"/></g>'
    _, plan = _plan(vertical, _rect(330, 95, 44, 50, BLDG))  # a vertical wall's opening, sealed on its inner face
    assert "seals the way through" in s.postern_approach(plan)[0]


def test_shrine_tree_asks_for_a_crown_beside_the_compound_shrine() -> None:
    """Feature 374 wave 130: 0218's drawing page sets the compound's shrine beside a tree."""
    hall = '<g data-kind="compound shrine"><rect x="100" y="100" width="54" height="42" fill="#C9876C"/></g>'

    def tree(cx: float, part_of: str = ' data-part-of="compound shrine"') -> str:
        return f'<g data-kind="sacred tree"{part_of} fill="#7A8C5C"><circle cx="{cx}" cy="121" r="30"/></g>'

    assert s.shrine_tree(_svg("")) == [], "no compound shrine: nothing asked"
    assert "no tree beside it" in s.shrine_tree(_svg(hall))[0]
    assert s.shrine_tree(_svg(hall, tree(190))) == [], "trunk 36 px (12 ft) east of the hall"
    assert "no tree beside it" in s.shrine_tree(_svg(hall, tree(220)))[0], "trunk 66 px (22 ft) off: not beside it"
    assert "no tree beside it" in s.shrine_tree(_svg(hall, tree(190, "")))[0], "a crown that is not the shrine's"


def test_well_gear_asks_every_tagged_well_for_its_gear() -> None:
    """Feature 374 wave 135: 0196's drawing page draws every well with a sweep or a pulley frame."""
    curb = '<rect x="100" y="100" width="22" height="22" fill="#9C8C70" data-kind="well"/>'
    lantern = '<rect x="10" y="10" width="10" height="8" fill="#9C8C70" data-kind="well"/>'  # under a curb's size
    basin = '<rect x="200" y="200" width="22" height="22" fill="#9C8C70" data-kind="basin"/>'
    assert s.well_gear(_svg(lantern, basin)) == [], "neither a lantern nor a basin is a well"
    assert "carries no lifting gear" in s.well_gear(_svg(curb))[0]
    gear = '<g data-kind="well" data-gear="sweep" data-at="111,111"><circle cx="124" cy="124" r="1.6"/></g>'
    assert s.well_gear(_svg(curb, gear)) == []
    far = '<g data-kind="well" data-gear="pulley frame" data-at="150,111"><circle cx="150" cy="111" r="1.6"/></g>'
    assert s.well_gear(_svg(curb, far)) != [], "a gear over another well"
    # plan W135-2: an indoor well hangs a beam pulley and has no roof; a roof is an outline on four posts
    kitchen = '<rect x="90" y="90" width="60" height="60" fill="#C9A57A" data-kind="kitchen"/>'
    beam = '<g data-kind="well" data-gear="beam pulley" data-at="111,111"><line x1="100" y1="111" x2="122" y2="111"/></g>'
    assert "stands indoors but draws a sweep" in s.well_gear(_svg(kitchen, curb, gear))[0]
    assert s.well_gear(_svg(kitchen, curb, beam)) == []
    assert "stands in the open but draws a beam pulley" in s.well_gear(_svg(curb, beam))[0]
    posts = "".join(f'<circle cx="{x}" cy="{y}" r="1.6"/>' for x in (96, 126) for y in (96, 126))
    roof = f'<g data-kind="well" data-roof="1" data-at="111,111"><rect x="96" y="96" width="30" height="30" fill="none"/>{posts}</g>'
    square = '<g data-kind="well" data-roof="1" data-at="111,111"><rect x="96" y="96" width="30" height="30" fill="#C7B084"/></g>'
    assert s.well_gear(_svg(curb, roof, gear)) == []
    assert "not an outline on four posts" in s.well_gear(_svg(square, curb, gear))[0]
    assert "draws a roof of its own" in s.well_gear(_svg(kitchen, curb, roof, beam))[0]
