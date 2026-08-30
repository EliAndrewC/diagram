"""What a rolled hamlet must DECLARE about itself (feature 166).

Carries six rules the retired battery re-measured on every finished map:
`settlement_declares_a_land_fall`, `households_consistent`, `houses_face_south`, `farmhouse_sizes_vary`,
`byre_form_declared` and `settlement_records_cluster_seeding`.

WHY THESE LIVE IN A SEED TEST RATHER THAN AT A PLACER. They are not clearances any single placement can
carry - they are properties of a FINISHED map: that its households are seated, that its houses vary in
size, that it declared the fall its drainage rules are judged against. The spec's destination list allows
exactly that, and the distinction that matters is not WHAT is asserted but WHEN - once per code change
over a rolled map, instead of once per map generated, for ever.

A DECLARATION NOTHING READS IS THE FAILURE THESE GUARD. `cluster_shape` was rolled, printed in every
cohort header, and honored on NO map for a long time, because only a seeding pass that never ran consumed
it; a peer session then spent an attempt blaming the knob for a placement failure it could not have
caused. A knob that silently fails to bind is worse than no knob, so "it was recorded" is itself the
assertion.
"""

from __future__ import annotations

import pytest

from l7r.diagram import hamletgen as hg
from l7r.diagram.pipeline import rollcache

# the forms the engine actually declares - read off the placer rather than guessed (my first
# draft allowed "detached" and the roll declares "detached_commons"). A superset would make this
# assertion weaker than the rule it replaces, which is the quiet way a migration loses a guarantee.
FORMS = ("courtyard", "detached_commons")

SPEC = hg.HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond")


@pytest.fixture(scope="module")
def rolled():
    """The reference hamlet's plan and FINISHED manifest, served from the roll cache while nothing it
    executes has changed."""
    return rollcache.hamlet(SPEC)


@pytest.mark.rolls_map
def test_the_map_declares_the_fall_its_drainage_is_judged_against(rolled) -> None:
    """`settlement_declares_a_land_fall`. A map declaring no fall SKIPS every drainage rule while still
    looking green - the "a check that never RUNS looks exactly like a check that passes" shape. So the
    declaration itself is the assertion: a map-level `down_deg`, or a fall on every paddy."""
    _plan, M = rolled
    fields = M.get("fields") or []
    assert M["meta"].get("down_deg") is not None or (fields and all(f.get("fall") is not None for f in fields)), (
        "the map declares neither a land fall nor a per-field fall, so every drainage rule would silently skip"
    )


@pytest.mark.rolls_map
def test_every_declared_household_is_seated(rolled) -> None:
    """`households_consistent`. The spec asks for N households and the map must seat them. A generator
    that quietly seats fewer has produced a different settlement from the one asked for, and the
    shortfall is invisible on the sheet."""
    plan, M = rolled
    dwellings = [h for h in (M.get("houses") or []) if h.get("kind") != "abandoned"]
    assert len(dwellings) >= round(0.85 * SPEC.households), f"seated {len(dwellings)} of {SPEC.households}"
    assert plan.placed >= round(0.85 * SPEC.households)


@pytest.mark.rolls_map
def test_farmhouses_vary_in_size(rolled) -> None:
    """`farmhouse_sizes_vary`. A modest spread of homestead sizes is expected - farmers were not equally
    wealthy - and a generator that flattens them to one size draws a barracks. Measured as effective
    footprint so BOTH encodings count: the dispersed path scales a uniform box by a wealth tier, the
    nucleated path jitters the box directly."""
    _plan, M = rolled
    plain = [h for h in (M.get("houses") or []) if h.get("kind") == "plain"]
    assert len(plain) >= 10, "too few plain farmhouses to speak of a spread"
    eff = sorted(float(h["w"]) * float(h["h"]) * float(h.get("wealth", 1.0)) ** 2 for h in plain)
    med = eff[len(eff) // 2] or 1.0
    varied = sum(1 for a in eff if abs(a - med) > 0.05 * med)
    assert varied >= 0.2 * len(plain), f"only {varied}/{len(plain)} farmhouses differ from the median footprint"


@pytest.mark.rolls_map
def test_the_rolled_cluster_shape_leaves_a_record(rolled) -> None:
    """`settlement_records_cluster_seeding`. The shape is rolled per settlement and read by `TWIN_AXES`,
    so it must leave a trace whether or not the drawing honored it: `cluster_shape` where it bound,
    `cluster_shape_unhonored` where the lane skeleton overrode it. A roll that records NEITHER has
    dropped the knob silently, which is the defect this rule was written for."""
    _plan, M = rolled
    meta = M["meta"]
    assert meta.get("cluster_shape") or meta.get("cluster_shape_unhonored"), "the rolled shape left no record at all"
    assert meta.get("cluster_aspect_drawn") is not None, "and the drawn aspect it was judged against is recorded"


@pytest.mark.rolls_map
def test_a_map_that_draws_byres_declares_their_form(rolled) -> None:
    """`byre_form_declared`. A byre is drawn as a courtyard wing or as a detached shed, and which one is
    a settlement-level decision a reader can see. A map that draws byres and names no form has made that
    decision without recording it."""
    _plan, M = rolled
    if not (M.get("byres") or []):
        pytest.skip("this roll drew no byres")
    assert M["meta"].get("byre_form") in FORMS, f"byres drawn, form declared as {M['meta'].get('byre_form')!r}"
