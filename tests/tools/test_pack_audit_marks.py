"""The three marks feature 335 holds hand sheets to (`tools/pack_audit/marks_drawn.py`): the landing steps cut into the
revetment (research 0176), a door wholly inside its building flush to its wall (research 0117's drawing page), and a
torii drawn in plan (docs/buildings.md). Each is also held to a red fixture by `test_registry.py`."""

from __future__ import annotations

from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import marks_drawn as md

COURT = '<rect x="0" y="0" width="400" height="400" fill="url(#court-earth)" id="precinct"/>'
HALL = '<rect x="100" y="100" width="120" height="60" fill="#C9A57A" stroke="#6B4F2A" stroke-width="1.5"/>'


def _svg(*body: str) -> str:
    return "<svg>" + COURT + "".join(body) + "</svg>"


def _door(x: float, y: float, w: float = 18, h: float = 6) -> str:
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="#B89868" stroke="#6B4F2A" stroke-width="0.8" data-kind="door"/>'


def _landing(steps_x: float, steps_w: float, river_x: float) -> str:
    return (
        f'<g data-kind="river"><rect x="{river_x}" y="0" width="100" height="400" fill="#9CB4C8"/></g>'
        '<rect x="200" y="0" width="8" height="400" fill="#9C9484" data-kind="revetment"/>'
        f'<g data-kind="dock" data-id="landing-steps"><rect x="{steps_x}" y="100" width="{steps_w}" height="46" fill="#B8B0A0"/></g>'
    )


def test_steps_past_the_rivers_face_are_found_on_either_bank() -> None:
    east = md.steps_past_revetment(_landing(194, 26, 206))  # river east of the revetment; the flight ends at 220, face 208
    assert len(east) == 1 and abs(east[0].past_ft - 4.0) < 1e-9
    west = md.steps_past_revetment(_landing(188, 26, 50))  # river west: the face is the revetment's west edge, 200
    assert len(west) == 1 and abs(west[0].past_ft - 4.0) < 1e-9


def test_steps_notched_into_the_revetment_pass() -> None:
    assert md.steps_past_revetment(_landing(194, 14, 206)) == []


def test_a_sheet_without_a_landing_or_its_parts_has_nothing_to_judge() -> None:
    assert md.steps_past_revetment("<svg/>") == []
    no_rect = _landing(194, 26, 206).replace('<rect x="194" y="100" width="26" height="46" fill="#B8B0A0"/>', "")
    assert md.steps_past_revetment(no_rect) == []
    bad = _landing(194, 26, 206).replace('x="194"', 'x="a"')
    assert md.steps_past_revetment(bad) == []


def test_a_rect_tagged_by_its_group_or_itself_and_none() -> None:
    assert md._tagged_rect('<g data-kind="river"><rect x="1" y="2" width="3" height="4"/></g>', "river") == (1, 2, 4, 6)
    assert md._tagged_rect('<rect x="1" y="2" width="3" height="4" data-kind="river"/>', "river") == (1, 2, 4, 6)
    assert md._tagged_rect('<g data-kind="river"><path d="M 0 0"/></g>', "river") is None
    assert md._tagged_rect("<svg/>", "river") is None


def test_a_door_inside_flush_passes_and_one_outside_or_floating_is_found() -> None:
    flush = pa.parse_svg(_svg(HALL, _door(150, 154)))  # inside, its south edge on the wall at y 160
    assert md.doors_off_their_walls(flush) == []
    outside = md.doors_off_their_walls(pa.parse_svg(_svg(HALL, _door(150, 160))))  # a slab below the wall
    assert [d.how for d in outside] == ["outside"]
    across = md.doors_off_their_walls(pa.parse_svg(_svg(HALL, _door(150, 157))))  # straddling the wall line
    assert [d.how for d in across] == ["outside"]
    floating = md.doors_off_their_walls(pa.parse_svg(_svg(HALL, _door(150, 140))))  # inside, 14 px off every wall
    assert [d.how for d in floating] == ["floating"]


def test_a_torii_without_its_arch_rect_is_a_silhouette() -> None:
    plan_form = '<g data-kind="torii"><rect x="0" y="0" width="45" height="6" fill="none" id="arch"/></g>'
    silhouette = '\n<g data-kind="torii" stroke="#A03020"><line x1="0" y1="0" x2="36" y2="0"/></g>'
    assert md.arches_not_in_plan(plan_form) == []
    assert md.arches_not_in_plan(plan_form + silhouette) == [2]
