"""A fixture in a grove band is judged by ONE body, `grove_rules.fixture_on_band` (feature 417 T17, D17; FR-006): the audit,
the sty's placer, the field pit's placer and the bundle fit all ask it, so the placing and the check cannot disagree."""

from __future__ import annotations

import inspect
import re

from l7r.diagram.hamletgen.homesteads import fixtures, sties
from l7r.diagram.settlement.homestead_parts import grove_rules
from l7r.diagram.settlement.rolling import fit

_INLINE_BOX = re.compile(r"abs\([^)]*\)\s*<\s*\([^)]*\+[^)]*\)\s*/\s*2")


def test_every_placer_of_a_fixture_asks_the_check_s_own_predicate():
    for mod in (fixtures, fit, sties):
        assert mod.fixture_on_band is grove_rules.fixture_on_band, f"{mod.__name__} asks another body"
    assert "fixture_on_band" in inspect.getsource(fixtures._flexible_clear)
    assert "fixture_on_band" in inspect.getsource(fit.BundleFitMixin._fixtures_in_bands)


def test_no_placer_keeps_its_own_copy_of_the_box_overlap():
    assert not _INLINE_BOX.search(inspect.getsource(fixtures._flexible_clear))
    assert not _INLINE_BOX.search(inspect.getsource(fit.BundleFitMixin._fixtures_in_bands))


def test_a_box_already_turned_is_asked_with_no_turn_of_its_own():
    band = {"x": 0.0, "y": 0.0, "w": 10.0, "h": 10.0}
    assert grove_rules.fixture_on_band({"x": 9.0, "y": 0.0, "w": 9.0, "h": 2.0}, band)
    assert not grove_rules.fixture_on_band({"x": 9.5, "y": 0.0, "w": 9.0, "h": 2.0}, band), "strict: touching is clear"
