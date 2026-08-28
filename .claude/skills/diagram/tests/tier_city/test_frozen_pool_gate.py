"""THE FROZEN TOWN AND CITY EXHIBITS, GATED AS THEY STAND (feature 146).

The legacy pool is FROZEN: its nineteen hand-authored maps are never regenerated and never re-gated
(`pipeline/poolmaps.py`, the 2026-08-16 ruling). One consequence went unnoticed until this feature
measured it - **nothing at all runs the town and city half of the check battery**, because the only
maps at those scales are the frozen ones and no test gated them. Every city segment therefore looked
uncovered, and a check that never runs looks exactly like a check that passes.

This gates each frozen manifest AS IT STANDS - read-only, no regeneration, no `.gen.py` executed, so
the freeze is untouched - and pins the failures each one carries. Those failures are the post-freeze
rules the map predates, which is the documented and expected state; the pin is what makes them a
LEDGER rather than a silence. A map that starts failing something new, or stops failing something
pinned, fails here by name.

It lives in `tests/tier_city/` so the hamlet-scoped quick suite does not collect it, and it costs
about a second a map because a gate over an existing manifest rolls nothing.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from l7r.diagram import check_village

HERE = pathlib.Path(__file__).resolve().parents[2]

# Measured 2026-08-28. Each entry is what that exhibit fails against TODAY's battery: the rules that
# arrived after the freeze. `delivery_ditches_taper` and `tree_crowns_not_subsumed` are universal -
# every exhibit predates both - and the town-tier trio (`comb_supply_commands_both_flanks`,
# `farmhouses_shed_separately`, the bund and stream rules) are the scripted tier's later doctrine.
FROZEN_EXPECTED: dict[str, list[str]] = {
    "provincial-cities/minami.json": ["delivery_ditches_taper", "tree_crowns_not_subsumed"],
    "provincial-cities/nagahara.json": ["delivery_ditches_taper", "tree_crowns_not_subsumed"],
    "provincial-cities/tango.json": ["delivery_ditches_taper", "tree_crowns_not_subsumed", "waivers_are_live"],
    "towns/hirameki.json": [
        "comb_supply_commands_both_flanks",
        "delivery_ditches_taper",
        "farmhouses_shed_separately",
        "paddy_bunds_clear_the_collector",
        "streams_avoid_fields",
        "tree_crowns_not_subsumed",
    ],
    "towns/hoshizora.json": [
        "comb_supply_commands_both_flanks",
        "delivery_ditches_taper",
        "dry_plots_clear_of_paddies",
        "farmhouses_shed_separately",
        "tree_crowns_not_subsumed",
        "waivers_are_live",
    ],
    "towns/ubame.json": [
        "comb_supply_commands_both_flanks",
        "delivery_ditches_taper",
        "farmhouses_shed_separately",
        "lanes_form_one_network",
        "tree_crowns_not_subsumed",
        "waivers_are_live",
    ],
}


@pytest.mark.tiers("town", "city")
@pytest.mark.parametrize("rel", sorted(FROZEN_EXPECTED))
def test_a_frozen_exhibit_fails_exactly_what_it_is_pinned_to_fail(rel: str) -> None:
    path = HERE / "pool" / rel
    manifest = json.loads(path.read_text(encoding="utf-8"))
    got = sorted(check_village.gate(manifest, verbose=False))
    want = FROZEN_EXPECTED[rel]
    assert got == want, f"{rel}: new={sorted(set(got) - set(want))} gone={sorted(set(want) - set(got))}"


@pytest.mark.tiers("town", "city")
def test_the_exhibits_are_read_only_here() -> None:
    """The freeze is the point: this module opens manifests and never writes one, and never runs a gen.

    Asserted on the module's own AST rather than its text, so the guard cannot be satisfied - or broken -
    by a mention of the forbidden name in a comment or in this assertion itself."""
    import ast

    tree = ast.parse(pathlib.Path(__file__).read_text(encoding="utf-8"))
    calls = {n.func.attr for n in ast.walk(tree) if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute)}
    assert "write_text" not in calls and "write_bytes" not in calls and "run" not in calls
