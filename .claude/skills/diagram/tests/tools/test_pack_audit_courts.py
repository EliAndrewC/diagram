"""The pack audit's tub check and the ROOFED hearing court (feature 267 pass 3).

A roofed court's floor is a footprint to `tubs_in_buildings`: a tub under the roof is fed by no gutter. The building
review caught the placer's draft seating the office hall's tub inside its roofed hearing court; the check read only
buildings, so it passed. Kept apart from `test_pack_audit.py`, which is at the file-size bar; the gate-range tests moved here with it.
"""

from __future__ import annotations

import pytest

from l7r.diagram.tools import pack_audit as pa
from tests.tools.test_pack_audit import COURT, _rect, _svg, _wallgroup

_PRECINCT = '<rect x="0" y="0" width="300" height="300" fill="url(#court-earth)" id="precinct"/>'
_TUB = '<g fill="#8FB0C6"><circle cx="150" cy="150" r="4"/></g>'


def _plan(court: str) -> pa.ParsedPlan:
    return pa.parse_svg(f"<svg>{_PRECINCT}{court}{_TUB}</svg>")


def test_a_tub_inside_a_roofed_court_is_a_tub_in_a_building() -> None:
    roofed = '<rect x="100" y="100" width="120" height="90" fill="url(#oshirasu-sand)" stroke="#5A3F1E" stroke-width="2"/>'
    plan = _plan(roofed)
    assert [(r.x, r.y) for r in plan.roofed_courts] == [(100.0, 100.0)]
    hits = pa.tubs_in_buildings(plan)
    assert len(hits) == 1 and hits[0].into_ft > 1.0


def test_a_tub_on_an_open_court_is_not() -> None:
    """A court drawn with the thin open-ground edge is open sand - a tub standing on it is `fire_water_adrift`'s to judge."""
    open_court = '<rect x="100" y="100" width="120" height="90" fill="url(#oshirasu-sand)" stroke="#9C7A40" stroke-width="0.8"/>'
    plan = _plan(open_court)
    assert plan.roofed_courts == () and pa.tubs_in_buildings(plan) == []


def test_the_river_cobble_floor_is_roofed_too() -> None:
    cobbles = '<rect x="100" y="100" width="120" height="90" fill="url(#court-cobbles)" stroke="#5A3F1E" stroke-width="2"/>'
    assert len(pa.tubs_in_buildings(_plan(cobbles))) == 1


def test_a_wrapped_label_is_its_widest_line_by_its_lines() -> None:
    """A caption written one line per `<tspan x dy>` (as `seat_label` wraps one) is measured as a block - its widest
    line by its lines' height - not every line run together; INNER COURT in two lines read as one 10-letter line
    (feature 267)."""
    svg = f'<svg>{_PRECINCT}<text x="100" y="50" font-size="10" text-anchor="middle"><tspan x="100" dy="0">INNER</tspan><tspan x="100" dy="14">COURT</tspan></text></svg>'
    (lab,) = pa.parse_svg(svg).labels
    assert lab.text == "INNER COURT"
    assert lab.w == pytest.approx(5 * 10 * pa.CHAR_W_FRAC)
    assert lab.h == pytest.approx(10 + 14)


def test_a_quarter_turned_label_stands_on_its_end() -> None:
    """A river's name turned `rotate(90 px py)` along its band is measured upright: its bbox is the flat one turned
    about the pivot, not the flat one (feature 267: two names in one river read as overlapping)."""
    svg = f'<svg>{_PRECINCT}<text x="100" y="100" font-size="10" transform="rotate(90 100 100)">river</text><text x="100" y="200" font-size="10" transform="rotate(-90, 100, 200)">river</text></svg>'
    down, up = pa.parse_svg(svg).labels
    flat = 5 * 10 * pa.CHAR_W_FRAC
    assert (down.w, down.h) == (pytest.approx(10), pytest.approx(flat))
    assert down.y == pytest.approx(100)  # it runs DOWN from its pivot
    assert up.y2 == pytest.approx(200)  # and this one UP


def test_a_board_at_a_nagaya_mon_reads_its_passage_by_the_gate_posts() -> None:
    """Feature 267: a gate range IS the wall line, standing in a break wider than any gap counted as a gate, so the
    passage is found by the `main gate` posts - drawn in a filled group, with no fill of their own."""
    posts = '<g fill="#2D2A24" data-kind="main gate"><rect x="190" y="396" width="6" height="8"/><rect x="226" y="396" width="6" height="8"/></g>'
    board = '<rect x="240" y="420" width="21" height="9" fill="#E8D2A8" data-kind="notice board"/>'
    wide = _svg(_rect(0, 0, 400, 400, COURT), _wallgroup((0, 400, 100, 400), (300, 400, 400, 400)), posts, board)
    plan = pa.parse_svg(wide)
    assert len(plan.gate_posts) == 2, "the fill-less posts are read"
    assert pa.notice_board_adrift(plan) == [], "a board 7 ft off the passage is at the gate"
    far = wide.replace('x="240" y="420"', 'x="360" y="60"')
    assert pa.notice_board_adrift(pa.parse_svg(far)), "and one across the compound is still adrift"


def test_the_main_gate_passage_is_measured_between_its_posts() -> None:
    """Feature 267: the report's gate list carries the ceremonial passage even where it runs through a gate range."""
    posts = '<g fill="#2D2A24" data-kind="main gate"><rect x="190" y="396" width="6" height="8"/><rect x="232" y="396" width="6" height="8"/></g>'
    plan = pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), posts))
    assert pa.main_gate_passage_ft(plan) == pytest.approx(12.0)
    side = '<g data-kind="main gate"><rect x="396" y="100" width="8" height="6" fill="#2D2A24"/><rect x="396" y="142" width="8" height="6" fill="#2D2A24"/></g>'
    assert pa.main_gate_passage_ft(pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), side))) == pytest.approx(12.0), "a gate in a side wall"
    assert pa.main_gate_passage_ft(pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT)))) is None
    floored = posts.replace('</g>', '<rect x="196" y="380" width="36" height="42" fill="#C9A57A"/></g>')
    assert pa.main_gate_passage_ft(pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), floored))) == pytest.approx(12.0), "the passage floor in the group is not a post"


def test_the_report_names_the_main_gate_passage() -> None:
    posts = '<g fill="#2D2A24" data-kind="main gate"><rect x="190" y="396" width="6" height="8"/><rect x="232" y="396" width="6" height="8"/></g>'
    assert "the MAIN GATE's passage" in pa.format_report(pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), posts)))


def test_a_tagged_caption_is_measured_on_its_own_kind() -> None:
    """A caption the standard seats beside its building can stand nearer another: Ubame's INARI SHRINE, set left of the
    shrine, stood nearest a 6 x 5 ft privy. Tagged with its kind, it is paired with the structure of that kind."""
    shrine = '<g data-kind="compound shrine"><rect x="200" y="100" width="60" height="45" fill="#C9876C"/></g>'
    privy = '<rect x="120" y="100" width="18" height="14" fill="#7E726A" data-kind="latrine"/>'
    name = '<text x="150" y="95" font-size="11" data-kind="compound shrine">INARI SHRINE</text>'
    plan = pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), shrine, privy, name))
    (lab,) = [lb for lb in plan.labels if lb.text == "INARI SHRINE"]
    assert [(r.x, r.w) for r in pa.labels._of_its_kind(lab, plan)] == [(200.0, 60.0)]
    untagged = pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), shrine, privy, name.replace(' data-kind="compound shrine"', "")))
    assert len(pa.labels._of_its_kind(untagged.labels[0], untagged)) == len(untagged.structures), "untagged: any structure"
