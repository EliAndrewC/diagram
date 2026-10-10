"""The fire-water tub at its building's door (feature 372 wave 106, research 0100: water kept at the entrance) - split from
test_pack_audit.py at the 1,000-line bar."""

from __future__ import annotations

from l7r.diagram.tools import pack_audit as pa

COURT = "url(#court-earth)"


def _rect(x: float, y: float, w: float, h: float, fill: str) -> str:
    mark = ' id="precinct"' if fill == COURT else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{mark}/>'


def _svg(*bodies: str) -> str:
    return "<svg>" + "".join(bodies) + "</svg>"


def _tubgroup(*circles: str) -> str:
    return f'<g fill="{pa.FIRE_WATER_FILL}" stroke="#3A5060" stroke-width="1">' + "".join(circles) + "</g>"


def test_a_tub_stands_by_a_door_of_the_building_it_serves() -> None:
    """Feature 372 wave 106 (research 0100, water kept at the entrance): a tub by its eaves is judged against the doors the
    sheet TAGS on that building's outline - not a hearth's dark rect, not an inner room's door - and one whose buildings
    draw no door is not judged."""
    from l7r.diagram import compound_parts as cp
    from l7r.diagram.tools.pack_audit import checks

    assert checks.tub_by_its_door is cp.tub_by_its_door
    door = '<rect x="96" y="40" width="4" height="18" fill="#4A3318" data-kind="door"/>'
    hearth = '<rect x="40" y="40" width="18" height="8" fill="#6B4030"/>'
    plan = pa.parse_svg(
        _svg(
            _rect(0, 0, 400, 400, COURT),
            _rect(0, 0, 100, 100, "#DDB87A"),
            door,
            hearth,
            _rect(200, 0, 60, 60, "#DDB87A"),
            _rect(200, 200, 100, 100, "#DDB87A"),
            '<rect x="240" y="240" width="8" height="8" fill="#4A3318" data-kind="door"/>',
            _tubgroup('<circle cx="106" cy="69" r="3.8"/>', '<circle cx="106" cy="5" r="3.8"/>', '<circle cx="264" cy="30" r="3.8"/>', '<circle cx="306" cy="210" r="3.8"/>'),
        )
    )
    off = pa.tubs_off_their_doors(plan)
    # the shed and the building with only an inner room's door tag no entrance: their tubs cannot be judged, so they fail
    assert [(t.x, t.y, round(t.door_ft, 1)) for t in off] == [(264, 30, float("inf")), (306, 210, float("inf")), (106, 5, 14.9)]
    outside = pa.parse_svg(
        _svg(
            _rect(0, 0, 400, 400, COURT),
            _rect(0, 0, 100, 100, "#DDB87A"),
            '<rect x="100" y="40" width="6" height="18" fill="#B89868" data-kind="door"/>',
            _tubgroup('<circle cx="108" cy="72" r="3.8"/>'),
        )
    )
    assert pa.tubs_off_their_doors(outside) == []  # a door drawn just outside its wall is still on it


def test_a_bath_tub_is_not_judged_and_a_declared_shoe_stone_is_an_entrance() -> None:
    """A bath is entered from its house, so its tub is not judged by a door even under another building's eaves; the
    reception's shoe stone, declared `id="shoe-stone"`, is its entrance (R07, research 0104)."""
    bath = '<g data-kind="bath"><rect x="200" y="0" width="40" height="30" fill="#C9A57A"/></g>'
    stone = '<rect id="shoe-stone" x="40" y="101" width="12" height="5" fill="#B8B0A0"/>'
    plan = pa.parse_svg(
        _svg(
            _rect(0, 0, 400, 400, COURT),
            _rect(0, 0, 100, 100, "#DDB87A"),
            stone,
            bath,
            _tubgroup('<circle cx="62" cy="108" r="3.8"/>', '<circle cx="220" cy="37" r="3.8"/>', '<circle cx="5" cy="108" r="3.8"/>'),
        )
    )
    assert [(t.x, t.y) for t in pa.tubs_off_their_doors(plan)] == [(5, 108)]  # 13 ft from the stone; the bath's passes


def test_the_registry_says_a_doorless_building_tags_no_door() -> None:
    from l7r.diagram.tools.pack_audit import registry as R

    plan = pa.parse_svg(_svg(_rect(0, 0, 400, 400, COURT), _rect(0, 0, 100, 100, "#DDB87A"), _tubgroup('<circle cx="106" cy="50" r="3.8"/>')))
    check = next(c for c in R.CHECKS if c.name == "tubs_off_their_doors")
    assert check.run(R.Context(plan, "", None, None, None)) == ["a fire-water tub at svg(106,50) stands at a building that tags no door"]
