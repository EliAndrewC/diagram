"""SCRIPTED NEGATIVE FIXTURES (feature 141, GM 2026-08-28): a kept check is proved to fire on what the ENGINE
draws - a cached roll with one deliberate break - instead of on a frozen manifest from the hand-placement era.

The GM: *"If the thing which fixes the wrongness of the map is an update to our placement algorithm, then I
don't think that saving off that past map actually has value ... we can have one hundred percent unit test
coverage and have a unit test which asserts that things are now correct without saving off the old map."*
Here the roll is served from the roll cache (feature 135), the break is a few lines the reader can see, and
the check is run TARGETED (feature 022's `only=`), so each case costs milliseconds at the gate."""

from __future__ import annotations

import copy
from collections.abc import Callable
from typing import Any

import pytest

from l7r.diagram import check_village
from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

REFERENCE = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")
POLDER = hg.HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90)


def _fires(spec: hg.HamletSpec, check: str, mutate: Callable[[dict[str, Any]], None]) -> None:
    _plan, M = rollcache.hamlet(spec)
    M = copy.deepcopy(M)
    assert check not in check_village.gate(M, verbose=False, only={check}), f"{check} must be CLEAN on the unbroken roll, or the break proves nothing"
    mutate(M)
    assert check in check_village.gate(M, verbose=False, only={check}), f"{check} did not fire on the break"


@pytest.mark.rolls_map
def test_hamlet_has_kosatsuba_fires_when_the_board_is_gone() -> None:
    _fires(REFERENCE, "hamlet_has_kosatsuba", lambda M: M.__setitem__("kosatsuba", []))


@pytest.mark.rolls_map
def test_kosatsuba_by_the_road_fires_when_the_board_stands_in_the_paddy() -> None:
    def far_from_every_way(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        M["kosatsuba"][0]["x"], M["kosatsuba"][0]["y"] = (fx0 + fx1) / 2, (fy0 + fy1) / 2  # the middle of the paddy, no way within reach

    _fires(REFERENCE, "kosatsuba_by_the_road", far_from_every_way)


@pytest.mark.rolls_map
def test_structures_clear_of_dike_fires_when_a_house_stands_on_the_dike() -> None:
    def onto_the_dike(M: dict[str, Any]) -> None:
        crest = M["dikes"][0]["crest"]
        cx, cy = crest[len(crest) // 2]
        M["houses"][0]["x"], M["houses"][0]["y"] = float(cx), float(cy)

    _fires(POLDER, "structures_clear_of_dike", onto_the_dike)


@pytest.mark.rolls_map
def test_polder_dike_gapped_at_sluices_fires_when_the_gaps_are_forgotten() -> None:
    _fires(POLDER, "polder_dike_gapped_at_sluices", lambda M: M["dikes"][0].__setitem__("gaps", []))
