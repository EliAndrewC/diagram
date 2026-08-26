"""tier city tests split out of `tests.check_village.test_segments_04_homesteads` (feature 133 T29, GM 2026-08-26): `make quick` collects
`tests/` minus the tier, gate and tooling trees, so these are neither imported nor collected while the scope is
locked to another tier; the gate collects everything. Helpers stay in the source module and are imported."""

import pytest

from l7r.diagram import check_village
from tests.check_village._builders import (
    f_only,
    manifest,
)


@pytest.mark.tiers("city")
def test_labels_clear_of_other_buildings_fires_on_a_caption_over_a_torii_arch():
    # GM 2026-07-27: an arch is "never covered by the 'temple of X' label" - and the hall's OWN
    # caption was the commonest offender, since caption and sando both want the ground at the front.
    # A torii is a bare [x, y, z] triple, so it needed its own branch in the victim builder; before
    # that it was classified and still checked nothing.
    M = {"meta": {"scale": "city", "ftpx": 3}, "labels": [[480, 552, 620, 566, 5, "Temple of Bishamon"]], "torii": [[500, 560, 1]]}
    assert "labels_clear_of_other_buildings" in f_only(M, "labels_clear_of_other_buildings")


@pytest.mark.tiers("city")
def test_theater_stage_caption_may_sit_on_its_precinct_but_not_on_the_town():
    """A stage caption is allowed onto TEMPLE ground, and nothing else it does not name.

    `theater_stage` sites the stage inside a temple/monastery precinct (and
    `theater_stage_by_temple` enforces it), so once the caption is seated by the standoff ladder
    against the stage's rotated extent, every seat within reach of its subject lands on precinct
    ground. Before this, correcting the rotation-blind caption offset simply moved Tango's caption
    off its own stage and onto a monk house, then onto a hall - a green map made worse by a fix.

    The second half is the part that matters: the allowance is scoped to `temple`, so a stage
    caption dumped on a merchant house still fires. An allowance nobody bounds is not a rule.
    """
    M = manifest(meta={"scale": "city", "ftpx": 3, "W": 2000, "H": 2000, "name": "Nowhere"})
    M["religious"] = [{"x": 500, "y": 500, "w": 300, "h": 300, "kind": "temple"}]
    M["labels"] = [[440, 480, 560, 492, 1, "theater stage"]]
    assert "labels_clear_of_other_buildings" not in check_village.gate(M, verbose=False)

    M["buildings"] = [{"x": 1200, "y": 1200, "w": 40, "h": 30, "kind": "merchant"}]
    M["labels"] = [[1180, 1190, 1240, 1202, 1, "theater stage"]]
    assert "labels_clear_of_other_buildings" in check_village.gate(M, verbose=False)
