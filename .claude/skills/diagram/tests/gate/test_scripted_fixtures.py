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


# ---- feature 146: a check nobody has proved fires is a check nobody has proved ------------------------------
# One deliberate, targeted break per check, on a cached roll. Each `mutate` is the smallest edit that makes the
# map wrong in exactly the way the check names - so a reader can see what the check is for, and the check's own
# failure branch is exercised (which is what the hamlet-path coverage floor was reporting, feature 146 class 2).


@pytest.mark.rolls_map
def test_households_consistent_fires_when_half_the_houses_vanish() -> None:
    _fires(REFERENCE, "households_consistent", lambda M: M.__setitem__("houses", M["houses"][: len(M["houses"]) // 3]))


@pytest.mark.rolls_map
def test_cluster_abuts_fields_fires_when_a_house_is_flung_far_from_the_field() -> None:
    def far_away(M: dict[str, Any]) -> None:
        fx0, fy0, fx1, fy1 = M["fields"][0]["bbox"]
        span = max(fx1 - fx0, fy1 - fy0)
        for h in M["houses"]:  # the whole cluster, so the check's cluster-radius term cannot absorb it
            h["x"], h["y"] = h["x"] - 4 * span, h["y"]

    _fires(REFERENCE, "cluster_abuts_fields", far_away)


@pytest.mark.rolls_map
def test_wells_among_dwellings_fires_when_a_well_stands_out_in_the_country() -> None:
    def out_in_the_open(M: dict[str, Any]) -> None:
        M["wells"][0]["x"] = M["wells"][0]["x"] + 4000.0

    _fires(REFERENCE, "wells_among_dwellings", out_in_the_open)


@pytest.mark.rolls_map
def test_ways_cross_water_on_a_deck_fires_when_a_lane_is_laid_down_the_channel() -> None:
    """Emptying `bridges` does NOT fire it on the reference - the hamlet's ways do not cross water at all, its
    footbridges plank the field channels. So the break is a lane laid ALONG a drawn channel, with no deck."""

    def down_the_channel(M: dict[str, Any]) -> None:
        pts = M["drawn_channels"][0]["pts"]
        M["lanes"].append({"pts": [list(p) for p in pts], "w": 5, "worn": True, "connector": False})
        M["bridges"] = []

    _fires(REFERENCE, "ways_cross_water_on_a_deck", down_the_channel)
