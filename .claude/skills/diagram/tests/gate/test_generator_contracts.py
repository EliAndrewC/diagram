"""What a rolled hamlet must DECLARE about itself (feature 166): what is left of it after feature 287.

Feature 166 carried six rules here that the retired battery re-measured on every finished map. Feature 287 guaranteed
them at the placers and retired their finished-map tests (specs/287-placer-guarantees/research.md R8): the fall is
always resolved (`hamletgen/plan.py:plan_site`), every household is seated or the site refused
(`hamletgen/homesteads/stages.py:seat_every_household`, `SiteRefused`), the footprints spread by the size ladder
(`settlement/houses.py`, `rolling/lot.py`), and the cluster shape is declared from the drawing
(`stages.py:declare_cluster_shape`) - each with a unit test on the violating case.

KEPT, because no unit test guards it: `byre_form_declared`. `shrines_wells/byres.py:draft_byres` writes the form before
any byre is drawn, by construction, but no unit test asserts `meta.byre_form`.
"""

from __future__ import annotations

import pytest

from tests import rolls
from tests.gate import _pool

# the forms the engine actually declares - read off the placer rather than guessed (my first
# draft allowed "detached" and the roll declares "detached_commons"). A superset would make this
# assertion weaker than the rule it replaces, which is the quiet way a migration loses a guarantee.
FORMS = ("courtyard", "yard_shed", "detached_commons")  # 269 B16: the inner stable, the outer stable, the rare shared shed

SPEC = rolls.REFERENCE  # the pool's brief (feature 215)


@pytest.fixture(scope="module")
def rolled():
    """The reference hamlet's plan and FINISHED manifest, served from the roll cache while nothing it
    executes has changed."""
    return _pool.rolled_map(SPEC)


@pytest.mark.rolls_map
def test_a_map_that_draws_byres_declares_their_form(rolled) -> None:
    """`byre_form_declared`. A byre is drawn as a courtyard wing or as a detached shed, and which one is
    a settlement-level decision a reader can see. A map that draws byres and names no form has made that
    decision without recording it."""
    _plan, M = rolled
    assert M.get("byres"), "the reference roll drew no byre, so this rule would judge nothing"
    assert M["meta"].get("byre_form") in FORMS, f"byres drawn, form declared as {M['meta'].get('byre_form')!r}"
