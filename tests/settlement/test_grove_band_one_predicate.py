"""A fixture in a grove band is judged by ONE body, `grove_rules.fixture_on_band` (feature 417 T17, D17; FR-006): the audit,
the sty's placer, the field pit's placer and the bundle fit all ask it, so the placing and the check cannot disagree."""

from __future__ import annotations

import re

from l7r.diagram.settlement.homestead_parts import grove_rules

_INLINE_BOX = re.compile(r"abs\([^)]*\)\s*<\s*\([^)]*\+[^)]*\)\s*/\s*2")


def test_a_box_already_turned_is_asked_with_no_turn_of_its_own():
    band = {"x": 0.0, "y": 0.0, "w": 10.0, "h": 10.0}
    assert grove_rules.fixture_on_band({"x": 9.0, "y": 0.0, "w": 9.0, "h": 2.0}, band)
    assert not grove_rules.fixture_on_band({"x": 9.5, "y": 0.0, "w": 9.0, "h": 2.0}, band), "strict: touching is clear"
