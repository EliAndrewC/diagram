"""Feature 287, M9: the acceptance sweep (SC-003). Every map of the pool and cohort seeds 1-48, rolled plain and again under
feature 284's two withdrawn levers applied as probes (A* in the router, `astarcmp/astar.txt`; the field search's saturation
probe, `b3cmp/b3_fit.py.txt`), each finished manifest asked EVERY rule predicate there is:

- `hamletgen.ways.law.violations(M)` - every lane rule, by name (`law:<rule>`);
- `waterfields.ring_rules.ring_violations` over every recorded plot ring, with the RingContext the gate tests build from the
  field's own design cell, the grain (`2 / ftpx`), its supply and collector strokes, the field ponds and the grave islands
  (`ring:<rule>`, counted in rings);
- `overlap.matrix.matrix_violations` - every forbidden overlap (M8's one predicate, `matrix:<key_a>/<key_b>`);
- `belt_law.reading_of(M)` - the windbreak's judged depth and its holes, as `settle_the_belt` reads them (`belt:thin`,
  `belt:holes`);
- the roll's own verdict: every declared household seated (`roll:unseated`) and every farmhouse on the way network
  (`roll:farmhouses_reach_a_way`);
- every finished-map test the census (`census.json`, kind `map-rule`) lists, called on this manifest: its
  manifest-reading fixtures resolved against this map, its `gen` / `manifest` path pointed at this map written to a
  scratch file (`test:<module>::<test>`). A test still in the tree runs as it stands; a test feature 287 RETIRED runs as
  its body stood at `BASE`, the commit the baseline sweep was taken at (the same rule the baseline measured, read from
  git), and is ALSO read through the engine predicate that replaced it where that predicate reads a finished manifest
  (`ENGINE`: the lane law, the ring rules, the overlap matrix, the roll's seating - `engine:<module>::<test>`, failing
  when any of its predicates fails). A retired test whose rule has no manifest-level predicate (the placer decides it on
  candidates, research R8 names which) is read by its `BASE` body alone.

A test the harness cannot yet run on a given manifest - it rolls its own spec, reads a fixture no module defines, or regenerates
a pool generator - is listed under `cannot_run` with why; later phases move those predicates into the engine and they join the
sweep. A test that stops on its own non-vacuity assertion (the map carries no such feature) or skips is not a failure and is
recorded as `vacuous` / `skipped`; an exception other than an assertion is `errors`.

The roll's own re-rolls are counted by wrapping the driver's `build` (one call per attempt) and `unreached_houses` (one
entry per verdict: the houses no lane reached), beside the households seated against those declared. Feature 287 removed
the re-roll (FR-002: `generate` builds once), so both count one per map; a second would be a re-roll.

    make spec-harness SPEC=specs/287-placer-guarantees/sweep OUT=<json>
"""

from __future__ import annotations

import collections
import importlib
import inspect
import json
import multiprocessing as mp
import os
import re
import tempfile
import time
import traceback
import types
from pathlib import Path
from typing import Any

BASE = "cc39f599a"
"""The commit `baseline.json` was taken at (287 T08): a census test retired since is run as its body stood there."""
ROOT = Path(__file__).resolve().parents[4]
SKILL = Path(__file__).resolve().parents[1]
OUT = Path(os.environ.get("HARNESS_OUT") or "/tmp/sweep-287.json")
CENSUS = ROOT / "specs/287-placer-guarantees/census.json"
ASTAR = ROOT / "specs/284-fourth-hotspot-pass/astarcmp/astar.txt"
B3_FIT = ROOT / "specs/284-fourth-hotspot-pass/b3cmp/b3_fit.py.txt"
COHORT = int(os.environ.get("SWEEP_COHORT") or 48)
WORKERS = int(os.environ.get("SWEEP_WORKERS") or 10)

PATH_PARAMS = {"gen", "manifest"}
"""A test parameter that names a shipped map's file: the harness hands it this map's scratch file."""

NOT_ON_A_MANIFEST = {
    "tests/full/test_villages.py::test_village_passes_gate": "regenerates each pool generator and gates the result; the sweep's own rolls are the maps",
}
"""Tests whose signature would resolve but whose body does not read the map it is handed."""

VACUOUS = re.compile(
    r"non-vacuity|judge[sd]? nothing|would (judge|pass|skip)|judged nothing|nothing to judge|vacuous|so this rule|so every rule"
    r"|\b(drew|dug|laid|painted|recorded|declares|carved|seated|planted) no\b|nothing could",
    re.I,
)
"""A test's own guard against passing on nothing - the map carries none of what the rule is about (a comb rule on a polder,
a pond rule on a map with no pond). A test that reads a manifest key the map does not carry is counted the same way."""

GRAVE_RADIUS = 6.0
"""`field_graves` records a mound's center and no size; its drawn ellipse is never smaller than 9 x 6 px
(`settlement/fields/features.py:_plot_grave_island`) and the disc the carve cuts round is wider still (the mound plus
`GRAVE_BANK_PX`), so a 6 px disc lies inside every mound and a ring it hits is a true hit. Since W28 the plots are carved
round the mound (`carve_around_grave`), so `ring:grave` is a rule the sweep expects to hold."""

ENGINE: dict[str, tuple[str, ...]] = {
    # the lane law (`hamletgen/ways/law.py`, research R8's `settle_*` placers ask it)
    "tests/hamletgen/test_pool_261.py::test_every_way_across_the_brook_is_bridged": ("law:unbridged",),
    "tests/hamletgen/test_pool_261.py::test_a_way_reaches_the_field": ("law:field_unreached",),
    "tests/hamletgen/test_pool_261.py::test_the_ways_cross_the_brook_only_at_fords_and_never_over_and_back": ("law:husks", "law:doubled_tails", "law:over_and_back", "law:off_ford"),
    "tests/hamletgen/test_pool_261.py::test_every_way_out_crosses_the_brook_at_most_once": ("law:way_outs",),
    "tests/hamletgen/test_pool_261.py::test_no_lane_ends_in_a_hook": ("law:hooks",),
    "tests/hamletgen/test_pool_261.py::test_every_lane_crosses_a_drawn_channel_square": ("law:oblique_channel",),
    "tests/hamletgen/test_pool_261.py::test_every_lane_crosses_the_brook_square": ("law:oblique_brook",),
    "tests/hamletgen/test_pool_261.py::test_no_lane_end_is_served_only_by_the_way_it_left": ("law:dangling_ends",),
    "tests/gate/test_crossings_and_cover.py::test_every_deck_is_long_enough_to_land_on_dry_ground": ("law:short_decks", "law:undeckable"),
    "tests/gate/test_crossings_and_cover.py::test_every_plank_crosses_a_supply_ditch_and_never_the_collector": ("law:planks",),
    "tests/gate/test_lane_network.py::test_every_lane_belongs_to_one_network": ("law:networks",),
    "tests/gate/test_lane_network.py::test_every_shipped_hamlets_lanes_are_one_network_at_the_ink_tolerance": ("law:networks",),
    "tests/gate/test_lane_network.py::test_no_lane_doubles_back_or_kinks": ("law:bends",),
    "tests/gate/test_lane_network.py::test_no_two_lanes_meet_end_to_end_in_a_fold_and_no_lane_ends_in_a_hook": ("law:folded_joints", "law:hooks"),
    "tests/gate/test_lane_network.py::test_every_lane_end_reaches_something_worth_walking_to": ("law:dangling_ends",),
    "tests/gate/test_lane_network.py::test_every_shipped_hamlets_lane_ends_reach_something": ("law:dangling_ends",),
    "tests/gate/test_lane_network.py::test_a_lane_does_not_break_mid_run": ("law:breaks_mid_run",),
    "tests/gate/test_lane_network.py::test_a_farmhouse_discharges_one_lane_end_not_three": ("law:doorstep_ends",),
    "tests/gate/test_cohort_lane_rules.py::test_the_clean_cohort_seeds_bend_like_paths": ("law:bends",),
    "tests/soak/test_seed_43_kink.py::test_seed_43_still_kinks_round_a_house_corner": ("law:bends",),
    "tests/soak/test_polder_fall_0.py::test_the_polder_s_lanes_bend_like_paths": ("law:bends",),
    # the ring rules (`waterfields/ring_rules.py`, held by `seams/close.py:hold_ring_rules`)
    "tests/gate/test_bunds_and_dikes.py::test_no_bund_is_drawn_down_the_middle_of_a_supply_channel": ("ring:stroke",),
    "tests/gate/test_bunds_and_dikes.py::test_no_bund_is_drawn_across_the_collector": ("ring:collector",),
    "tests/gate/test_paddy_fabric.py::test_no_basin_tapers_to_a_point": ("ring:needle",),
    "tests/gate/test_paddy_fabric.py::test_a_flooded_plot_reads_as_a_basin_and_not_as_a_pond": ("ring:needle",),
    "tests/gate/test_paddy_fabric.py::test_no_shipped_hamlet_has_a_basin_tapering_to_a_point": ("ring:needle",),
    "tests/gate/test_paddy_fabric.py::test_no_basin_is_too_small_to_be_worth_its_own_bund": ("ring:area",),
    "tests/gate/test_paddy_fabric.py::test_a_bund_does_not_build_a_flight_of_steps": ("ring:steps",),
    "tests/gate/test_paddy_fabric.py::test_every_recorded_plot_ring_is_a_simple_polygon": ("ring:crossing",),
    "tests/gate/test_water_junctions.py::test_a_field_pond_is_sunk_into_one_plot": ("ring:pond",),
    # the windbreak (`settlement/homestead_parts/belt_law.py`, `settle_the_belt`)
    "tests/hamletgen/test_pool_wind.py::test_every_pool_belt_keeps_its_depth_across_its_windward_face": ("belt:thin",),
    # the overlap matrix (`overlap/registry.py`, M8)
    "tests/gate/test_no_feature_overlaps.py::test_the_comb_hamlet_draws_no_forbidden_overlap": ("matrix:*",),
    "tests/gate/test_no_feature_overlaps.py::test_the_polder_hamlet_draws_no_forbidden_overlap": ("matrix:*",),
    # the roll's seating (`homesteads/stages.py:seat_every_household`, `SiteRefused`)
    "tests/gate/test_generator_contracts.py::test_every_declared_household_is_seated": ("roll:unseated",),
    "tests/soak/test_polder_fall_0.py::test_the_polder_seats_its_households_and_lands_its_acreage": ("roll:unseated",),
    "tests/soak/test_seatings.py::test_lane_frontage_seats_the_hamlet_when_the_field_row_offers_nothing": ("roll:unseated",),
    "tests/soak/test_seatings.py::test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_rows_offer_nothing": ("roll:unseated",),
}
"""Each retired census test whose rule an engine predicate reads off a finished manifest, with the predicate(s) - the
names the sweep counts them under. A `*` matches every key of its family."""


SUPERSEDED = {
    "tests/gate/test_no_feature_overlaps.py::test_no_pond_fixture_stands_on_its_ponds_sluice": "superseded by feature 280 M57 (merged into 287): no per-pond sluice is drawn, so the rule has no subject and its constant `SLUICE_CLEAR_FT` is gone (research R8)",
}
"""Retired census tests whose rule no longer has a subject on any map, by a recorded ruling: listed, not run."""


def _fall(M: dict[str, Any]) -> tuple[float, float]:
    import math

    a = math.radians(float((M.get("meta") or {}).get("down_deg") or 0.0))
    return (math.cos(a), math.sin(a))


def _nearest_on(p: Any, poly: Any) -> tuple[int, float]:
    """(index of the segment of `poly` nearest `p`, its distance)."""
    import math

    best = (0, math.inf)
    for i in range(len(poly) - 1):
        (ax, ay), (bx, by) = poly[i][:2], poly[i + 1][:2]
        dx, dy = bx - ax, by - ay
        t = 0.0 if not (dx or dy) else max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - ay) * dy) / (dx * dx + dy * dy)))
        d = math.hypot(p[0] - ax - t * dx, p[1] - ay - t * dy)
        if d < best[1]:
            best = (i, d)
    return best


def restated_runoff(M: dict[str, Any]) -> str | None:
    """`test_the_runoff_leaves_the_outfall_downhill` with the retired body's two misreadings corrected, the rule unchanged
    (the runoff leaves the outfall downhill): the SINK pond is judged only where the pond is the drainage's
    (`meta.pond_role == "drainage"` or a channel from the drain ending on it) - the retired body read a polder's header
    reservoir, the source above the field, as a sink; and a brook passing the outfall is judged by its OWN direction
    (a stream's record runs source to mouth: its mouth must lie downhill of where it passes the outfall) - the retired body
    took the brook's far end by distance, which on a feed brook passing the outfall is its source."""
    drains = [d for d in (M.get("field_ditches") or []) if d.get("role") == "drain"]
    if not drains:
        return None
    fx, fy = _fall(M)
    out = drains[0]["poly"][-1]
    sink = M.get("pond")
    to_pond = any((c.get("frm") or {}).get("kind") == "drain" and (c.get("to") or {}).get("kind") == "pond" for c in M.get("channels") or [])
    if sink and ((M.get("meta") or {}).get("pond_role") == "drainage" or to_pond) and (sink[0] - out[0]) * fx + (sink[1] - out[1]) * fy <= 0:
        return f"the sink pond at {sink[:2]} sits uphill of the outfall {out}"
    for c in M.get("channels") or []:
        if (c.get("frm") or {}).get("kind") == "drain" and len(c.get("poly") or []) >= 2 and _nearest_on(out, c["poly"])[1] < 60.0:
            a, b = c["poly"][0], c["poly"][-1]
            if (b[0] - a[0]) * fx + (b[1] - a[1]) * fy <= 0:
                return f"the drain run climbs from the outfall ({a} -> {b})"
    for st in M.get("streams") or []:
        poly = st.get("poly") or []
        if len(poly) < 2:
            continue
        i, d = _nearest_on(out, poly)
        if d < 60.0:
            q, mouth = poly[i + 1], poly[-1]
            if mouth is not q and (mouth[0] - q[0]) * fx + (mouth[1] - q[1]) * fy <= 0:
                return f"the brook passing the outfall runs on uphill ({q} -> its mouth {mouth})"
    return None


def restated_copse_reach(M: dict[str, Any]) -> str | None:
    """`test_the_copse_stands_within_reach_of_what_it_is_named_for` as woods W25 restated it (research R8): a household's
    reserved share of the wood floor stands by its house on EITHER siting, so on an against-the-belt map a crown may be
    within `COPSE_BELT_REACH_FT` of a belt crown or within `COPSE_HOUSE_REACH_FT` of a farmhouse (the union: the manifest
    does not mark which crowns are reserved seats once re-seated); on a dooryard map, of a farmhouse, as before."""
    import math

    from l7r.diagram.hamletgen.consts import COPSE_BELT_REACH_FT, COPSE_HOUSE_REACH_FT

    groves = {g["role"]: g for g in M.get("village_groves", [])}
    if "copse" not in groves or not groves["copse"].get("clumps"):
        return None
    houses = [(h["x"], h["y"]) for h in M["houses"]]
    belt = (groves.get("windbreak") or {}).get("clumps", []) + (groves.get("windbreak") or {}).get("clumps_offpage", [])

    def near(c: Any, pts: Any, reach: float) -> bool:
        return any(math.hypot(c[0] - q[0], c[1] - q[1]) <= reach + 1.0 for q in pts)

    if (M.get("meta") or {}).get("copse_siting") == "against_the_belt":
        far = [c for c in groves["copse"]["clumps"] if not near(c, belt, COPSE_BELT_REACH_FT) and not near(c, houses, COPSE_HOUSE_REACH_FT)]
    else:
        far = [c for c in groves["copse"]["clumps"] if not near(c, houses, COPSE_HOUSE_REACH_FT)]
    return f"{len(far)} copse crowns stand beyond reach of both the belt and every farmhouse" if far else None


RESTATED = {
    "tests/gate/test_water_flow.py::test_the_runoff_leaves_the_outfall_downhill": restated_runoff,
    "tests/hamletgen/test_pool_261.py::test_the_copse_stands_within_reach_of_what_it_is_named_for": restated_copse_reach,
}
"""Retired census tests whose BASE body the sweep does not count, with the predicate it counts instead: the rule
restated by a recorded decision (the copse, W25), or the retired body's measurement corrected (the runoff). The BASE body
still runs and its verdict is kept beside it (`base_messages`), so the difference is on the record."""


# ---- the maps -------------------------------------------------------------------------------------------------------


def pool_specs() -> dict[str, dict[str, Any]]:
    """Every pool hamlet's brief, read from its committed generator's literal HamletSpec arguments."""
    out = {}
    for gen in sorted((SKILL / "pool" / "hamlets").glob("*/*.gen.py")):
        m = re.search(r"HamletSpec\((.*?)\)\s*,\s*out_base", gen.read_text(), re.S)
        assert m, f"no HamletSpec literal in {gen}"
        out[gen.name.removesuffix(".gen.py")] = eval(f"dict({m.group(1)})")  # noqa: S307 - our own committed generator's literal arguments
    return out


def all_specs() -> dict[str, Any]:
    from l7r.diagram.hamletgen.driver import cohort_specs

    specs: dict[str, Any] = dict(pool_specs())
    for sp in cohort_specs(COHORT, first_seed=1):
        specs[f"cohort-{sp.seed:02d}"] = sp
    return specs


# ---- the probes -----------------------------------------------------------------------------------------------------


def apply_probes() -> None:
    """Feature 284's A* router and saturation-probe field search, swapped in for this process (neither ships)."""
    from l7r.diagram.hamletgen.water import fit
    from l7r.diagram.hamletgen.ways import route

    ns: dict[str, Any] = {}
    exec(compile(ASTAR.read_text(), "astar.txt", "exec"), vars(route) | ns, ns)  # noqa: S102 - the lever as 284 left it
    astar = ns["lattice_search"]

    def lattice_search(start, goal, nx, ny, is_free, in_band, toll, cell, free=None, band=None):  # noqa: ANN001, ANN202, ARG001
        # 287 perf (b7b88b9e1) hands the search the caller's two verdict memos, `free` and `band`, read before `is_free` /
        # `in_band` are asked; those two callbacks fill the same memos, so the probe (written before the memos existed)
        # takes them and asks the callbacks - the same verdicts, the same A* search 284 withdrew (R11)
        return astar(start, goal, nx, ny, is_free, in_band, toll, cell)

    route.lattice_search = lattice_search
    mod = types.ModuleType("l7r.diagram.hamletgen.water.b3_fit")
    mod.__package__ = "l7r.diagram.hamletgen.water"
    exec(compile(B3_FIT.read_text(), "b3_fit.py", "exec"), mod.__dict__)  # noqa: S102 - the lever's own fit.py
    fit._fit_at_aspect = mod._fit_at_aspect


# ---- the census's finished-map tests ----------------------------------------------------------------------------------


def _fixture_fn(obj: Any) -> Any:
    """The function under a pytest fixture definition, or None when `obj` is not one."""
    if type(obj).__name__ != "FixtureFunctionDefinition" and not hasattr(obj, "_pytestfixturefunction"):
        return None
    get = getattr(obj, "_get_wrapped_function", None)
    return get() if get else getattr(obj, "__wrapped__", None)


def _resolvable(mod: types.ModuleType, name: str, seen: frozenset[str] = frozenset()) -> str | None:
    """Why fixture/parameter `name` of `mod` cannot be fed this map, or None when it can."""
    if name in PATH_PARAMS:
        return None
    fn = _fixture_fn(getattr(mod, name, None))
    if fn is None:
        return f"parameter `{name}` is no fixture of its module (a conftest or parametrized spec the harness does not roll)"
    if name in seen:
        return f"fixture `{name}` is circular"
    params = list(inspect.signature(fn).parameters)
    if not params and "rolled_map(" not in inspect.getsource(fn):
        return f"fixture `{name}` builds its own input (it is not a rolled map the harness can stand in for)"
    for p in params:
        why = _resolvable(mod, p, seen | {name})
        if why:
            return why
    return None


_BASE_MODULES: dict[str, Any] = {}


def base_module(path: str, rev: str = BASE) -> types.ModuleType:
    """The test module at `path` as it stood at `rev`, imported under its own package (so its relative imports and its
    `tests.gate._pool` reads resolve against today's tree) as `<package>.<name>__<rev>`. Its source is registered with
    `linecache`, so `inspect.getsource` reads that body, not today's file."""
    import linecache
    import subprocess
    import sys

    key = f"{path}@{rev}"
    if key in _BASE_MODULES:
        if isinstance(_BASE_MODULES[key], Exception):
            raise _BASE_MODULES[key]
        return _BASE_MODULES[key]
    try:
        src = subprocess.run(["git", "-C", str(SKILL), "show", f"{rev}:.claude/skills/diagram/{path}"], capture_output=True, text=True, check=True).stdout
        pkg = str(Path(path).parent).replace("/", ".")
        name = f"{pkg}.{Path(path).stem}__{re.sub(r'[^0-9A-Za-z]', '_', rev)}"
        fname = f"<{rev}>/{path}"
        linecache.cache[fname] = (len(src), None, src.splitlines(keepends=True), fname)
        mod = types.ModuleType(name)
        mod.__package__ = pkg
        mod.__file__ = fname
        sys.modules[name] = mod
        exec(compile(src, fname, "exec"), mod.__dict__)  # noqa: S102 - this repository's own test module, read from git
    except Exception as e:  # noqa: BLE001 - recorded, and reported per test
        _BASE_MODULES[key] = e
        raise
    _BASE_MODULES[key] = mod
    return mod


def retired_at(path: str, fname: str) -> str:
    """The commit a retired test last stood at: the parent of the commit (after `BASE`) that removed `def <fname>(` from
    `path` - its body as feature 287 left it, after FR-003 made the test and its placer read one predicate."""
    import subprocess

    out = subprocess.run(
        ["git", "-C", str(SKILL), "log", "--format=%h", "-S", f"def {fname}(", f"{BASE}..HEAD", "--", f":(top).claude/skills/diagram/{path}"],
        capture_output=True, text=True, check=True,
    ).stdout.split()
    return f"{out[0]}^" if out else BASE


BASE_TWIN: dict[str, tuple[str, str]] = {}
"""Each retired test whose last body is not its `BASE` body: the `BASE` twin, run beside it so a difference in verdict is on
the record (`base_messages`)."""


def census_tests() -> tuple[list[tuple[str, str, str]], dict[str, str]]:
    """The census's map-rule tests split into those the harness runs (`(nodeid, module, function)`) and those it cannot,
    with why. A test still in the tree is today's; a retired one is its `BASE` body (`base_module`)."""
    rows = [r for r in json.loads(CENSUS.read_text()) if r["kind"] == "map-rule"]
    runnable, cannot = [], {}
    for r in rows:
        nodeid = r["test"]
        path, fname = nodeid.split("::")
        if nodeid in NOT_ON_A_MANIFEST:
            cannot[nodeid] = NOT_ON_A_MANIFEST[nodeid]
            continue
        if nodeid in SUPERSEDED:
            cannot[nodeid] = SUPERSEDED[nodeid]
            continue
        modname = path.removesuffix(".py").replace("/", ".")
        fn = None
        if (SKILL / path).exists():
            try:
                mod = importlib.import_module(modname)
            except Exception as e:  # noqa: BLE001 - a module that will not import is reported, not fatal
                cannot[nodeid] = f"module does not import: {type(e).__name__}: {e}"
                continue
            fn = getattr(mod, fname, None)
        if fn is None:  # retired by feature 287: its body as it last stood, and its BASE body beside it
            rev = retired_at(path, fname)
            try:
                mod = base_module(path, rev)
            except Exception as e:  # noqa: BLE001
                cannot[nodeid] = f"retired, and its module at {rev} does not import: {type(e).__name__}: {str(e)[:160]}"
                continue
            modname = mod.__name__
            fn = getattr(mod, fname, None)
            if rev != BASE:
                try:
                    twin = base_module(path, BASE)
                    if getattr(twin, fname, None) is not None and inspect.getsource(getattr(twin, fname)) != inspect.getsource(fn):
                        BASE_TWIN[nodeid] = (twin.__name__, fname)
                except Exception:  # noqa: BLE001, S110 - the twin is a record, not a verdict
                    pass
        if fn is None:
            cannot[nodeid] = "no such test function in its module (nor where it was retired)"
            continue
        params = list(inspect.signature(fn).parameters)
        if not params:
            cannot[nodeid] = "takes no map: it rolls or reads its own"
            continue
        why = next((w for p in params if (w := _resolvable(mod, p))), None)
        if why:
            cannot[nodeid] = why
            continue
        runnable.append((nodeid, modname, fname))
    return runnable, cannot


def _resolve(
    mod: types.ModuleType,
    name: str,
    rolled: tuple[Any, dict[str, Any]],
    path: str,
    cache: dict[str, Any],
) -> Any:
    """Fixture/parameter `name` for this map: a path parameter is the scratch file, a fixture taking nothing runs its own body
    with `_pool.rolled_map` answering this map's `(plan, manifest)` pair (some such fixtures derive from the roll - the
    captions' `labels` - so the pair itself is not a stand-in), any other fixture is its own function called on what it
    depends on."""
    if name in cache:
        return cache[name]
    if name == "gen":
        val: Any = path.removesuffix(".json") + ".gen.py"
    elif name == "manifest":
        val = path
    else:
        fn = _fixture_fn(getattr(mod, name))
        params = list(inspect.signature(fn).parameters)
        if not params:  # it rolls through `_pool.rolled_map`: that is pointed at this map, and the fixture's own body runs on it
            from tests.gate import _pool

            _pool.rolled_map = lambda *_a, **_k: rolled
            if hasattr(mod, "rolled_map"):
                mod.rolled_map = _pool.rolled_map
            val = fn()
            if inspect.isgenerator(val):
                val = next(val)
        else:
            val = fn(*[_resolve(mod, p, rolled, path, cache) for p in params])
            if inspect.isgenerator(val):
                val = next(val)
    cache[name] = val
    return val


def run_test(modname: str, fname: str, rolled: tuple[Any, dict[str, Any]], path: str) -> tuple[str, str]:
    """`(outcome, message)` of one census test on this map: pass, fail, vacuous, skipped or error.

    A module whose `SPEC` names the brief its rolled fixture stands for has it rebound to THIS map's brief, so a test that
    reads the brief (`seated N of SPEC.households`) judges the map against what it asked for."""
    import pytest

    from l7r.diagram.hamletgen.plan import HamletSpec

    mod = importlib.import_module(modname)
    if isinstance(getattr(mod, "SPEC", None), HamletSpec):
        mod.SPEC = rolled[0].spec  # type: ignore[attr-defined]
    fn = getattr(mod, fname)
    try:
        fn(*[_resolve(mod, p, rolled, path, {}) for p in inspect.signature(fn).parameters])
    except AssertionError as e:
        msg = str(e).split("\n")[0][:300]
        return ("vacuous" if VACUOUS.search(msg) else "fail"), msg
    except pytest.skip.Exception as e:
        return "skipped", str(e)[:200]
    except pytest.fail.Exception as e:
        msg = str(e).split("\n")[0][:300]
        return ("vacuous" if VACUOUS.search(msg) else "fail"), msg
    except KeyError as e:
        if e.args and isinstance(e.args[0], str) and e.args[0] not in rolled[1]:
            return "vacuous", f"the map records no `{e.args[0]}`"
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return "error", f"KeyError: {e} ({Path(tb.filename).name}:{tb.lineno})"
    except (Exception, SystemExit, pytest.xfail.Exception) as e:  # noqa: BLE001 - a test that cannot read this map is reported, not fatal (a BaseException escaping a pool worker hangs `pool.map`)
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return (
            "error",
            f"{type(e).__name__}: {str(e)[:200]} ({Path(tb.filename).name}:{tb.lineno})",
        )
    return "pass", ""


# ---- the engine's predicates ----------------------------------------------------------------------------------------


def _count(v: Any) -> int:
    if isinstance(v, bool):
        return int(v)
    if isinstance(v, int | float):
        return int(v) or 1
    try:
        return len(v)
    except TypeError:
        return 1


def law_failures(M: dict[str, Any]) -> tuple[dict[str, int], dict[str, str]]:
    """Every lane rule the map breaks with its count, and the rules that raised on it."""
    from l7r.diagram.hamletgen.ways import law

    out, errs = {}, {}
    for name, rule in law.LAW.items():
        try:
            v = rule(M)
        except Exception as e:  # noqa: BLE001
            errs[f"law:{name}"] = f"{type(e).__name__}: {str(e)[:200]}"
            continue
        if v:
            out[f"law:{name}"] = _count(v)
    return out, errs


def ring_failures(M: dict[str, Any]) -> tuple[dict[str, int], int]:
    """How many recorded plot rings break each ring rule, and how many rings were judged."""
    from l7r.diagram.waterfields.ring_rules import (
        RingContext,
        collector_strokes,
        ring_violations,
        supply_strokes,
    )

    g = 2.0 / float((M.get("meta") or {}).get("ftpx") or 1.0)  # the engine's grain, as test_a_bund_does_not_build_a_flight_of_steps
    ponds = [(float(p["x"]), float(p["y"]), float(p["rx"]), float(p["ry"])) for p in M.get("field_ponds") or []]
    graves = [(float(p["x"]), float(p["y"]), GRAVE_RADIUS) for p in M.get("field_graves") or []]
    ditches = M.get("field_ditches") or []
    counts: collections.Counter[str] = collections.Counter()
    judged = 0
    for f in M.get("fields") or []:
        rings = f.get("plot_rings") or []
        if not rings:
            continue
        name = f.get("name")
        ctx = RingContext(
            cell=float(f["cell"]) if f.get("cell") else None,
            g=g,
            supplies=supply_strokes([d for d in ditches if d.get("role") in ("main", "branch") and d.get("field") == name]),
            drains=collector_strokes([d for d in ditches if d.get("role") == "drain" and d.get("field") == name]),
            ponds=ponds,
            graves=graves,
        )
        for ring in rings:
            if len(ring) < 3:
                continue
            judged += 1
            for rule in ring_violations(ring, ctx):
                counts[f"ring:{rule}"] += 1
    return dict(counts), judged


# ---- one map --------------------------------------------------------------------------------------------------------


def matrix_failures(M: dict[str, Any]) -> dict[str, int]:
    """Every forbidden overlap on the map (`overlap.matrix.matrix_violations`, M8's one predicate), by the pair of keys."""
    from l7r.diagram.overlap.matrix import matrix_violations

    return dict(collections.Counter(f"matrix:{a}/{b}" for a, b, _x, _y in matrix_violations(M)))


def belt_failures(M: dict[str, Any]) -> dict[str, int]:
    """The windbreak read as its placer reads it (`belt_law.reading_of`): the judged 40 ft stretches shallower than the
    record's minimum (`belt:thin`, W16) and the holes across the wind (`belt:holes`, W17) - `settle_the_belt`'s own two
    predicates."""
    from l7r.diagram.settlement.homestead_parts.belt_law import reading_of

    rd = reading_of(M)
    if rd is None:
        return {}
    out = {"belt:thin": len(rd.thin()), "belt:holes": len(rd.holes())}
    return {k: v for k, v in out.items() if v}


def engine_verdicts(failing: dict[str, int]) -> dict[str, list[str]]:
    """Each retired census test (`ENGINE`) with the predicates of its that fail on this map - empty when it holds."""
    out = {}
    for nodeid, keys in ENGINE.items():
        hit = [k for k in failing if any(k == q or (q.endswith("*") and k.startswith(q[:-1])) for q in keys)]
        out[nodeid] = sorted(hit)
    return out


def one(job: tuple[str, Any, str, list[tuple[str, str, str]]]) -> dict[str, Any]:
    """`one_map`, never raising: an exception (a BaseException too) that left a pool worker would leave `pool.map` waiting
    for a result that never comes."""
    try:
        return one_map(job)
    except BaseException as e:  # noqa: BLE001
        return {"map": job[0], "pass": job[2], "roll_error": f"harness: {type(e).__name__}: {str(e)[:300]}\n{traceback.format_exc()[-1500:]}"}


def one_map(job: tuple[str, Any, str, list[tuple[str, str, str]]]) -> dict[str, Any]:
    key, kw, pass_, tests = job
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec

    per_attempt: list[int] = []
    builds: list[int] = []
    real, real_build = driver.unreached_houses, driver.build

    def counted(M: Any) -> Any:
        got = real(M)
        per_attempt.append(len(got))
        return got

    def counted_build(*a: Any, **k: Any) -> Any:
        builds.append(1)
        return real_build(*a, **k)

    driver.unreached_houses = counted
    driver.build = counted_build
    if pass_ == "probes":
        apply_probes()
    row: dict[str, Any] = {"map": key, "pass": pass_}
    t = time.perf_counter()
    try:
        rep = driver.generate(
            HamletSpec(**kw) if isinstance(kw, dict) else kw,
            out_base=None,
            render=False,
        )
    except Exception as e:  # noqa: BLE001 - a roll that raises is a row of the sweep, not the end of it
        row.update(
            roll_error=f"{type(e).__name__}: {str(e)[:300]}",
            roll_trace=[f"{Path(f.filename).name}:{f.lineno} {f.name}" for f in traceback.extract_tb(e.__traceback__)[-12:]],
            builds=len(builds),
            s=round(time.perf_counter() - t, 1),
        )
        return row
    roll_s = time.perf_counter() - t
    M = rep.manifest or {}
    failing, errors = law_failures(M)
    rings, judged = ring_failures(M)
    failing.update(rings)
    try:
        failing.update(belt_failures(M))
    except Exception as e:  # noqa: BLE001
        errors["belt"] = f"{type(e).__name__}: {str(e)[:200]}"
    try:
        failing.update(matrix_failures(M))
    except Exception as e:  # noqa: BLE001
        errors["matrix"] = f"{type(e).__name__}: {str(e)[:200]}"
    households, seated = int(rep.plan.spec.households), int(rep.plan.placed)
    if seated < households:
        failing["roll:unseated"] = households - seated
    for f in rep.failures:
        failing[f"roll:{f.split('[')[0]}"] = 1
    vacuous, skipped, messages, base_messages = {}, {}, {}, {}
    with tempfile.TemporaryDirectory() as tmp:
        path = os.path.join(tmp, f"{key}.json")
        Path(path).write_text(json.dumps(M))
        Path(path.removesuffix(".json") + ".gen.py").write_text("# the sweep's scratch stand-in for a pool generator\n")
        from tests.gate import _pool

        _pool.obtain = lambda gen: gen.removesuffix(".gen.py") + ".json"
        rolled = (rep.plan, M)
        for nodeid, modname, fname in tests:
            outcome, msg = run_test(modname, fname, rolled, path)
            name = f"test:{nodeid.removeprefix('tests/')}"
            if nodeid in BASE_TWIN:
                t_out, t_msg = run_test(*BASE_TWIN[nodeid], rolled, path)
                if t_out != outcome:
                    base_messages[f"{name} (at {BASE})"] = f"{t_out}: {t_msg}"
            if nodeid in RESTATED:
                base_messages[name] = f"{outcome}: {msg}"
                try:
                    why = RESTATED[nodeid](M)
                    outcome, msg = ("fail", why) if why else ("pass", "")
                except Exception as e:  # noqa: BLE001
                    outcome, msg = "error", f"restated: {type(e).__name__}: {str(e)[:200]}"
            if outcome == "fail":
                failing[name] = 1
                messages[name] = msg
            elif outcome == "vacuous":
                vacuous[name] = msg
            elif outcome == "skipped":
                skipped[name] = msg
            elif outcome == "error":
                errors[name] = msg
    meta = M.get("meta") or {}
    row.update(
        failing=dict(sorted(failing.items())),
        engine={k: v for k, v in engine_verdicts(failing).items() if v},
        messages=messages,
        base_messages=base_messages,
        vacuous=vacuous,
        skipped=skipped,
        errors=errors,
        rings_judged=judged,
        builds=len(builds),
        per_attempt_unreached=per_attempt,
        roll_failures=list(rep.failures),
        households=households,
        seated=seated,
        d12=bool(meta.get("kosatsuba_d12")),
        woodland_offsheet=meta.get("woodland_offsheet"),
        woodland_parcels=sum(1 for c in M.get("commons") or [] if c.get("role") == "woodland" and c.get("poly")),
        roll_s=round(roll_s, 1),
        s=round(time.perf_counter() - t, 1),
    )
    return row


def summarize(rows: list[dict[str, Any]], cannot: dict[str, str]) -> dict[str, Any]:
    """Per pass: each failing rule with the maps it fails on and its total count; the re-rolls; the unseated households;
    each retired test's engine predicates; the maps reaching plan D12's terminal."""
    out: dict[str, Any] = {}
    for pass_ in ("plain", "probes"):
        rs = [r for r in rows if r["pass"] == pass_]
        by_rule: dict[str, dict[str, Any]] = {}
        errs: collections.Counter[str] = collections.Counter()
        vac: collections.Counter[str] = collections.Counter()
        eng: collections.Counter[str] = collections.Counter()
        for r in rs:
            for rule, n in r.get("failing", {}).items():
                e = by_rule.setdefault(rule, {"maps": 0, "count": 0})
                e["maps"] += 1
                e["count"] += n
            errs.update(r.get("errors", {}).keys())
            vac.update(r.get("vacuous", {}).keys())
            eng.update(r.get("engine", {}).keys())
        out[pass_] = {
            "maps": len(rs),
            "roll_errors": {r["map"]: r["roll_error"] for r in rs if "roll_error" in r},
            "maps_clean": sum(1 for r in rs if "roll_error" not in r and not r.get("failing")),
            "rules": dict(sorted(by_rule.items(), key=lambda kv: (-kv[1]["maps"], kv[0]))),
            "rerolled_maps": sum(1 for r in rs if r.get("builds", 1) > 1 or len(r.get("per_attempt_unreached", [0])) > 1),
            "extra_builds": sum(max(0, r.get("builds", 1) - 1) for r in rs),
            "verdicts_per_map": sorted({len(r.get("per_attempt_unreached", [])) for r in rs if "roll_error" not in r}),
            "unseated": {r["map"]: r["households"] - r["seated"] for r in rs if r.get("seated", 0) < r.get("households", 0)},
            "engine_failing": dict(eng),
            "d12_maps": [r["map"] for r in rs if r.get("d12")],
            "woodland_offsheet_maps": [r["map"] for r in rs if r.get("woodland_offsheet")],
            "vacuous": dict(vac),
            "errors": dict(errs),
        }
    out["cannot_run"] = cannot
    return out


def test_sweep() -> None:
    from l7r.diagram.hamletgen.ways import law

    tests, cannot = census_tests()
    specs = all_specs()
    jobs = [(k, kw, p, tests) for k, kw in specs.items() for p in ("plain", "probes")]
    with mp.get_context("fork").Pool(WORKERS, maxtasksperchild=1) as pool:
        rows = []
        with open(f"{OUT}.progress", "w") as prog:  # one line per finished map, for a watcher (pytest holds stdout)
            for row in pool.imap_unordered(one, jobs, chunksize=1):
                rows.append(row)
                prog.write(f"{len(rows)}/{len(jobs)} {row['map']} {row['pass']} {row.get('s')} s failing={sorted(row.get('failing', {}))} {row.get('roll_error', '')[:200]}\n")
                prog.flush()
        rows.sort(key=lambda r: (r["map"], r["pass"]))
    OUT.write_text(
        json.dumps(
            {
                "runs": {
                    "law": sorted(law.LAW),
                    "ring": "waterfields.ring_rules.ring_violations over every plot ring (needle, crossing, arrowhead, area, steps, stroke, collector, pond, grave; W26 width and W27 dart recorded, not asked)",
                    "matrix": "overlap.matrix.matrix_violations",
                    "belt": "settlement.homestead_parts.belt_law.reading_of(M).thin() / .holes()",
                    "roll": "households seated against declared; the driver's farmhouses_reach_a_way verdict; builds per roll",
                    "tests": [t[0] for t in tests],
                    "base": BASE,
                    "retired_at": {n: m for n, m, _f in tests if "__" in m},
                    "base_twins": sorted(BASE_TWIN),
                    "engine": ENGINE,
                    "restated": {k: (v.__doc__ or "").split("\n")[0] for k, v in RESTATED.items()},
                    "superseded": SUPERSEDED,
                },
                "summary": summarize(rows, cannot),
                "maps": rows,
            },
            indent=1,
        )
    )
