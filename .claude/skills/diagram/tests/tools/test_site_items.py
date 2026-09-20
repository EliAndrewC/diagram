"""Site items (feature 257, plan D6): a program item whose presence follows the declared map."""

from __future__ import annotations

import pytest

from l7r.diagram.buildings import types as bt
from l7r.diagram.tools import pack_audit as pa
from l7r.diagram.tools.pack_audit import labels as L


def _type(**item_extra: object) -> bt.BuildingType:
    raw = [
        {
            "tier": "t",
            "title": "T",
            "program": "T",
            "hand_drawn": True,
            "checks": [],
            "required": [
                {"id": "hall", "label": "^hall", "band_ft": {}, "class": "guess", "why": "w"},
                {"id": "grove", "label": "grove", "band_ft": {}, "class": "guess", "why": "w", **item_extra},
            ],
        }
    ]
    return bt.parse_types(raw)[0]


def test_the_site_attribute_is_parsed_and_a_bad_one_refused() -> None:
    t = _type(site="tree")
    assert [i.site for i in t.required] == [None, "tree"]
    with pytest.raises(ValueError, match="site names a correspondence class"):
        _type(site="")
    with pytest.raises(ValueError, match="site names a correspondence class"):
        _type(site=3)


def test_a_site_item_is_asked_for_only_where_the_map_shows_its_class() -> None:
    plan = pa.parse_svg('<svg><rect x="0" y="0" width="100" height="100" fill="url(#court-earth)" id="precinct"/><text x="10" y="10">hall</text></svg>')
    t = _type(site="tree")
    assert L.check_program(plan, t, None) == ["no `grove` on the sheet (a label matching /grove/, or an element marked id=\"grove\")"]  # no declaration: required
    assert L.check_program(plan, t, None, {"tree": True}) == ["no `grove` on the sheet (a label matching /grove/, or an element marked id=\"grove\")"]
    assert L.check_program(plan, t, None, {"tree": False}) == []
    assert L.check_program(plan, t, None, {}) == []
    assert L.check_program(plan, _type(), None, {"tree": False}) == ["no `grove` on the sheet (a label matching /grove/, or an element marked id=\"grove\")"]  # not a site item


def test_the_declared_shrine_marks_its_grove_and_burial_ground_as_site_items() -> None:
    shrine = bt.by_tier("country-shrines")
    assert shrine is not None
    sites = {i.id: i.site for i in shrine.required if i.site}
    assert sites == {"grove": "tree", "burial_ground": "burial_ground"}
