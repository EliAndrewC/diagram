"""EQUIVALENCE: the lifted reach predicate agrees with the gate check it replaces (feature 166).

THIS TEST IS DESIGNED TO DIE. It compares `hamletgen.ways.unreached_houses` against
`farmhouses_reach_a_way`, so it can only run while the check still exists - and feature 166 deletes the
check. That is exactly why the migration order has the battery outliving its own replacements: the proof
that a lift is faithful is only available BEFORE the safety net goes. When the check is deleted, this file
goes with it, and what remains is `tests/hamletgen/test_unreached_houses.py`, which tests the predicate on
its own terms.

A green-on-green comparison would prove almost nothing (every live map passes, so both sides say "fine"),
so each map is also PERTURBED - one house dragged far off the web - and the two must agree on that too.
"""

from __future__ import annotations

import copy
import glob
import json
import os

import pytest

from l7r.diagram import check_village
from l7r.diagram.hamletgen.ways import unreached_houses

HERE = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MAPS = sorted(glob.glob(os.path.join(HERE, "pool", "hamlets", "*", "*.json")))


def _check_fires(M: dict) -> bool:
    return "farmhouses_reach_a_way" in check_village.gate(dict(M), verbose=False, only={"farmhouses_reach_a_way"})


@pytest.mark.parametrize("path", MAPS, ids=lambda p: os.path.basename(p).replace(".json", ""))
def test_predicate_and_check_agree_on_the_live_map(path):
    with open(path, encoding="utf-8") as fh:
        M = json.load(fh)
    assert bool(unreached_houses(M)) == _check_fires(M)


@pytest.mark.parametrize("path", MAPS, ids=lambda p: os.path.basename(p).replace(".json", ""))
def test_predicate_and_check_agree_when_a_house_is_dragged_off_the_web(path):
    """The half that has teeth: a green-on-green comparison agrees trivially."""
    with open(path, encoding="utf-8") as fh:
        M = json.load(fh)
    if not (M.get("houses") and M.get("lanes")):
        pytest.skip("no houses or no lanes to perturb")
    bad = copy.deepcopy(M)
    bad["houses"][0] = {**bad["houses"][0], "x": float(bad["houses"][0]["x"]) + 5000.0}
    assert _check_fires(bad), "the perturbation must make the CHECK fire, or this proves nothing"
    assert bool(unreached_houses(bad)) is True
    assert unreached_houses(bad)[0][:2] == (round(float(bad["houses"][0]["x"])), round(float(bad["houses"][0]["y"])))
