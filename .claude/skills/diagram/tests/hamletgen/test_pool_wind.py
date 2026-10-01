"""The pool's hamlets take the regional northwest wind, and their windbreaks stand on it (feature 261).

The GM, looking at Kashikawa's belt on the south and east: *"which I thought was supposed to be to the north and
west because of the direction of the winds for the geographic region ... Is this just a bug in the map
generator?"* - and, on the fix: *"none of our maps should have this declared at the present time. So it should be
fixed everywhere for now."* So every scripted hamlet in the pool declares no wind, records the northwest as the
region's, seats its cluster with its back to it, and has its belt on the cluster's northwest side.

These read the SHIPPED manifests and generators: the GM's ruling on the pool's content, which no placer owns.

FEATURE 287 RETIRED THE BELT'S TESTS (specs/287-placer-guarantees/research.md R8), each now decided where the belt is
planted, with a unit test on the violating case: its bearing on the wind and its hook (`stands.py:trim_to_the_wind`,
which plants no belt where no crown stands in the wind's quarter), its seat's back to the wind and every household seated
(`hamletgen/cluster.py:seat_cluster`, `homesteads/stages.py`), and its depth - the judged stretches deepened or the belt
ended (`belt_law.py:settle_the_belt`), and a belt no stretch of which is judged judged whole where it stands off the page
(`BeltReading.off_the_page`).
"""

from __future__ import annotations

import glob
import json
import os
import re

import pytest

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
GENS = sorted(glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.gen.py")))


def _manifest(gen: str) -> dict:
    with open(gen.removesuffix(".gen.py") + ".json", encoding="utf-8") as fh:
        return json.load(fh)


def _belted(gen: str) -> dict:
    """The manifest of a map that draws a village belt: a nucleated one. Where every farm carries its own grove - the
    dispersed and linear forms (feature 291) - the grove IS the shelter and no village belt is drawn (research/vegetation/020,
    "The per-farmstead belt is the DISPERSED settlement's answer"; `hinterland/belt.belt_polygon`)."""
    m = _manifest(gen)
    if m["meta"].get("settlement_form", "nucleated") != "nucleated":
        pytest.skip(f"a {m['meta']['settlement_form']} map: its farms carry their own groves, no village belt")
    return m


def test_the_pool_has_scripted_hamlets_to_judge() -> None:
    assert len(GENS) >= 5, "non-vacuity: the five scripted hamlets"


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_no_pool_hamlet_declares_a_wind(gen: str) -> None:
    """FR-005: a local wind is a declaration, and the GM ruled that no map carries one at present."""
    with open(gen, encoding="utf-8") as fh:
        src = fh.read()
    assert "HamletSpec(" in src
    assert not re.search(r"\bwindward\s*=", src), f"{os.path.basename(gen)} declares a wind"


@pytest.mark.parametrize("gen", GENS, ids=lambda g: os.path.basename(g).removesuffix(".gen.py"))
def test_every_pool_hamlet_records_the_regional_northwest(gen: str) -> None:
    """FR-006: with no wind declared, the map takes the region's - the northwest - and says so (the first clause of the
    belt test feature 287 retired; the belt's bearing on it is the planter's, `stands.py:trim_to_the_wind`)."""
    meta = _manifest(gen)["meta"]
    assert (meta["windward"], meta["wind_source"]) == ("NW", "regional")
