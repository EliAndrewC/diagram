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


DIVIDER = '<g stroke="#3F3A30" stroke-width="6"><line x1="20" y1="200" x2="380" y2="200"/></g>'
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
    assert "no sanded hearing court" in s.two_court_zoning(plan)[0]
    _, plan = _plan(DIVIDER, SAND_SOUTH)
    assert "no gate opening" in s.two_court_zoning(plan)[0]
    vertical = '<g stroke="#3F3A30" stroke-width="6"><line x1="200" y1="20" x2="200" y2="380"/></g>'
    _, plan = _plan(_wall((180, 220)), vertical, SAND_NORTH)
    assert s.two_court_zoning(plan) == []


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
    assert s.sanctuary_on_axis(plan) == [] and s.arch_on_approach(plan) == [] and s.well_clear_of_arch(plan) == [] and s.fence_not_wall(text, plan) == []
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
    assert any("compound wall stroke" in f for f in s.fence_not_wall(walled, pa.parse_svg(walled)))
    interior_wall = text.replace('<rect x="240" y="350"', '<g stroke="#2D2A24" stroke-width="9"><line x1="100" y1="250" x2="130" y2="250"/></g><rect x="240" y="330"')
    assert s.fence_not_wall(interior_wall, pa.parse_svg(interior_wall)) == []  # a wall stroke away from the boundary is not the fence's business


def test_a_group_label_matches_whole_words_only() -> None:
    """`dwelling` is not `well`: the orphan check found by the second type (feature 254)."""
    sheet = _svg(PRECINCT, '<text x="200" y="200" font-size="11">hall and dwelling</text>', _rect(300, 300, 22, 22, pa.WELL_FILL))
    assert pa.orphan_group_labels(pa.parse_svg(sheet)) == []
    sheet = _svg(PRECINCT, '<text x="60" y="60" font-size="11">the well</text>', _rect(300, 300, 22, 22, pa.WELL_FILL))
    assert len(pa.orphan_group_labels(pa.parse_svg(sheet))) == 1


# --- the label pairing and the program checks (labels.py) ---


def _text(x: float, y: float, s: str, size: int = 11) -> str:
    return f'<text x="{x}" y="{y}" text-anchor="middle" font-size="{size}">{s}</text>'


def test_structure_for_prefers_the_smallest_containing_footprint_then_the_nearest_within_reach() -> None:
    _, plan = _plan(_rect(40, 40, 200, 100, BLDG), _rect(60, 60, 30, 20, "#E8D2A8"), _text(75, 74, "porch"), _text(140, 130, "near"), _text(300, 300, "ground"))
    by = {lb.text: lb for lb in plan.labels}
    assert L.structure_for(by["porch"], plan.structures).w == 30.0  # the strip, not the block it lies in
    assert L.structure_for(by["near"], plan.structures).w == 200.0  # 30 px under the block's edge
    assert L.structure_for(by["ground"], plan.structures) is None  # far from every footprint
    assert L.nearest_label(0, 0, []) is None and L.nearest_label(0, 0, [(3.0, 4.0, "a")]) == ("a", 5.0)


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
    _, plan = _plan(_rect(40, 40, 45, 45, BLDG), _text(62, 66, "hut"), _text(200, 300, "yard"), _text(62, 300, "loft"))
    assert L.check_program(plan, types, None) == []  # loft is labeled (on open ground), shed optional
    assert L.check_program(plan, types, "one roof") == []
    assert "no `hut`" in L.check_program(pa.parse_svg(_svg(PRECINCT)), types, None)[0]
    assert L.check_bands(plan, types, None) == []  # 15 x 15 ft in band; yard presence-only; loft on ground skipped
    _, big = _plan(_rect(40, 40, 90, 45, BLDG), _text(85, 66, "hut"), _rect(200, 200, 60, 60, BLDG), _text(230, 230, "shed"))
    findings = L.check_bands(big, types, None)
    assert any("`hut`" in f and "w 10-20 by h 10-20 ft" in f for f in findings)
    assert any("`shed`" in f and "area 50-200 sq ft" in f for f in findings)  # 20 x 20 ft = 400
