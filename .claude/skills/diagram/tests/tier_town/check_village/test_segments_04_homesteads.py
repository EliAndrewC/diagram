"""tier town tests split out of `tests.check_village.test_segments_04_homesteads` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from tests.check_village._builders import (
    bldg,
    f_only,
    manifest,
)


@pytest.mark.tiers("town")
def test_labels_clear_of_other_buildings_reads_the_tilted_quad():
    # the pre-tilt box [0..3] laps the merchant, but the -30 deg glyph run swings clear below it -
    # judged by its box the caption would false-flag; judged by its true quad it is clean
    M = manifest(meta={"scale": "town", "ftpx": 1, "W": 1000, "H": 1000}, buildings=[bldg(120, 106, kind="merchant", w=20, h=16)])
    M["labels"] = [[100, 100, 240, 112, 1, "stray caption", None, -30.0]]
    assert "labels_clear_of_other_buildings" not in f_only(M, "labels_clear_of_other_buildings")
    M["labels"] = [[100, 100, 240, 112, 1, "stray caption"]]  # the same record level DOES lap it
    assert "labels_clear_of_other_buildings" in f_only(M, "labels_clear_of_other_buildings")


@pytest.mark.tiers("city", "town")
def test_a_plural_granaries_caption_may_cover_its_own_stores():
    """'domain granaries' does not CONTAIN the group word 'granary', so the derived
    caption-permission rule alone could not permit the plural captions the wharf complexes
    carry - the synonym branch does (GM 2026-08-09, the singular/plural label question).
    Tested at CITY scale because labels_clear_of_other_buildings runs in the town/city block;
    the control proves the granaries pair is actually judged, not skipped."""
    M = {
        "meta": {"scale": "city", "W": 1000, "H": 1000},
        "granaries": [{"x": 550, "y": 560, "w": 40, "h": 24, "rot": 0, "label": "domain granaries"}],
        "labels": [[480, 550, 640, 566, 5, "domain granaries"]],
    }
    assert "labels_clear_of_other_buildings" not in f_only(M, "labels_clear_of_other_buildings")
    M["labels"] = [[480, 550, 640, 566, 5, "flophouse row"]]  # a foreign caption on the stores still fires
    assert "labels_clear_of_other_buildings" in f_only(M, "labels_clear_of_other_buildings")
