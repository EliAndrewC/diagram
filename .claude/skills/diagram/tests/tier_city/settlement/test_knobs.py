"""tier city tests split out of `tests.settlement.test_knobs` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import settlement


@pytest.mark.tiers("city")
def test_wall_tower_spacing_px_scales_with_tier():
    """The per-city defense tier sets the max mural-tower spacing. siege = aimed-lethal bowshot
    (197 ft), >=2 everywhere, so spacing == range; garrison = full war-bow (328 ft), >=2, so the
    wider range; peaceful keeps only >=1 flanking tower within aimed-lethal range, so its spacing
    is DOUBLE (a tower every 2*197 ft - the sparser Xi'an crossfire). At 3 ft/px (city scale):"""
    ppf = 1.0 / 3.0  # px per ft
    assert settlement.wall_tower_spacing_px(ppf, "siege") == 197.0 * ppf
    assert settlement.wall_tower_spacing_px(ppf, "garrison") == 328.0 * ppf
    assert settlement.wall_tower_spacing_px(ppf, "peaceful") == 2 * 197.0 * ppf
    # siege is tighter than garrison; peaceful is the loosest
    assert settlement.wall_tower_spacing_px(ppf, "siege") < settlement.wall_tower_spacing_px(ppf, "garrison")
    assert settlement.wall_tower_spacing_px(ppf, "peaceful") > settlement.wall_tower_spacing_px(ppf, "garrison")
