"""Feature 287, M9: the acceptance sweep (SC-003). Every map of the pool and cohort seeds 1-48, rolled plain and again under
feature 284's two withdrawn levers applied as probes (A* in the router, `astarcmp/astar.txt`; the field search's saturation
probe, `b3cmp/b3_fit.py.txt`), each finished manifest asked EVERY rule predicate there is:

- `hamletgen.ways.law.violations(M)` - every lane rule, by name (`law:<rule>`);
- `waterfields.ring_rules.ring_violations` over every recorded plot ring, with the RingContext the gate tests build from the
  field's own design cell, the grain (`2 / ftpx`), its supply and collector strokes, the field ponds and the grave islands
  (`ring:<rule>`, counted in rings);
- every finished-map test the census (`census.json`, kind `map-rule`) lists whose predicate still lives in a test module,
  called on this manifest: its manifest-reading fixtures resolved against this map, its `gen` / `manifest` path pointed at
  this map written to a scratch file (`test:<module>::<test>`).

A test the harness cannot yet run on a given manifest - it rolls its own spec, reads a fixture no module defines, or regenerates
a pool generator - is listed under `cannot_run` with why; later phases move those predicates into the engine and they join the
sweep. A test that stops on its own non-vacuity assertion (the map carries no such feature) or skips is not a failure and is
recorded as `vacuous` / `skipped`; an exception other than an assertion is `errors`.

The roll's own re-rolls are counted by wrapping the driver's `unreached_houses` (one entry per attempt: the houses no lane
reached), beside the Report's `attempt`, `rerolled_after` and the households seated against those declared.

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
(`settlement/fields/features.py:_plot_grave_island`), so a 6 px disc lies inside every mound and a ring it hits is a true
hit. The mounds are DRAWN OVER the lattice by a recorded convention, so `ring:grave` is expected to fire until W28 lands."""


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
    route.lattice_search = ns["lattice_search"]
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


def census_tests() -> tuple[list[tuple[str, str, str]], dict[str, str]]:
    """The census's map-rule tests split into those the harness runs (`(nodeid, module, function)`) and those it cannot yet,
    with why."""
    rows = [r for r in json.loads(CENSUS.read_text()) if r["kind"] == "map-rule"]
    runnable, cannot = [], {}
    for r in rows:
        nodeid = r["test"]
        path, fname = nodeid.split("::")
        if nodeid in NOT_ON_A_MANIFEST:
            cannot[nodeid] = NOT_ON_A_MANIFEST[nodeid]
            continue
        if not (SKILL / path).exists():
            cannot[nodeid] = "the census's module is not in the tree"
            continue
        modname = path.removesuffix(".py").replace("/", ".")
        try:
            mod = importlib.import_module(modname)
        except Exception as e:  # noqa: BLE001 - a module that will not import is reported, not fatal
            cannot[nodeid] = f"module does not import: {type(e).__name__}: {e}"
            continue
        fn = getattr(mod, fname, None)
        if fn is None:
            cannot[nodeid] = "no such test function in its module"
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
    """Fixture/parameter `name` for this map: a path parameter is the scratch file, a fixture taking nothing is the rolled
    `(plan, manifest)` pair (every such fixture in a map-rule module is `_pool.rolled_map(<spec>)`), any other fixture is its
    own function called on what it depends on."""
    if name in cache:
        return cache[name]
    if name == "gen":
        val: Any = path.removesuffix(".json") + ".gen.py"
    elif name == "manifest":
        val = path
    else:
        fn = _fixture_fn(getattr(mod, name))
        params = list(inspect.signature(fn).parameters)
        if not params:
            val = rolled
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
    except KeyError as e:
        if e.args and isinstance(e.args[0], str) and e.args[0] not in rolled[1]:
            return "vacuous", f"the map records no `{e.args[0]}`"
        tb = traceback.extract_tb(e.__traceback__)[-1]
        return "error", f"KeyError: {e} ({Path(tb.filename).name}:{tb.lineno})"
    except Exception as e:  # noqa: BLE001 - a test that cannot read this map is reported, not fatal
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


def one(job: tuple[str, Any, str, list[tuple[str, str, str]]]) -> dict[str, Any]:
    key, kw, pass_, tests = job
    from l7r.diagram.hamletgen import driver
    from l7r.diagram.hamletgen.plan import HamletSpec

    per_attempt: list[int] = []
    real = driver.unreached_houses

    def counted(M: Any) -> Any:
        got = real(M)
        per_attempt.append(len(got))
        return got

    driver.unreached_houses = counted
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
            s=round(time.perf_counter() - t, 1),
        )
        return row
    roll_s = time.perf_counter() - t
    M = rep.manifest or {}
    failing, errors = law_failures(M)
    rings, judged = ring_failures(M)
    failing.update(rings)
    vacuous, skipped, messages = {}, {}, {}
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
            if outcome == "fail":
                failing[name] = 1
                messages[name] = msg
            elif outcome == "vacuous":
                vacuous[name] = msg
            elif outcome == "skipped":
                skipped[name] = msg
            elif outcome == "error":
                errors[name] = msg
    row.update(
        failing=dict(sorted(failing.items())),
        messages=messages,
        vacuous=vacuous,
        skipped=skipped,
        errors=errors,
        rings_judged=judged,
        attempt=rep.attempt,
        per_attempt_unreached=per_attempt,
        rerolled_after=list(rep.rerolled_after),
        roll_failures=list(rep.failures),
        households=int(rep.plan.spec.households),
        seated=int(rep.plan.placed),
        roll_s=round(roll_s, 1),
        s=round(time.perf_counter() - t, 1),
    )
    return row


def summarize(rows: list[dict[str, Any]], cannot: dict[str, str]) -> dict[str, Any]:
    """Per pass: each failing rule with the maps it fails on and its total count; the re-rolls; the unseated households."""
    out: dict[str, Any] = {}
    for pass_ in ("plain", "probes"):
        rs = [r for r in rows if r["pass"] == pass_]
        by_rule: dict[str, dict[str, Any]] = {}
        errs: collections.Counter[str] = collections.Counter()
        for r in rs:
            for rule, n in r.get("failing", {}).items():
                e = by_rule.setdefault(rule, {"maps": 0, "count": 0})
                e["maps"] += 1
                e["count"] += n
            errs.update(r.get("errors", {}).keys())
        out[pass_] = {
            "maps": len(rs),
            "roll_errors": [r["map"] for r in rs if "roll_error" in r],
            "maps_clean": sum(1 for r in rs if "roll_error" not in r and not r.get("failing")),
            "rules": dict(sorted(by_rule.items(), key=lambda kv: (-kv[1]["maps"], kv[0]))),
            "rerolled_maps": sum(1 for r in rs if r.get("attempt", 1) > 1),
            "extra_attempts": sum(r.get("attempt", 1) - 1 for r in rs),
            "unseated": {r["map"]: r["households"] - r["seated"] for r in rs if r.get("seated", 0) < r.get("households", 0)},
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
        rows = pool.map(one, jobs, chunksize=1)
    OUT.write_text(
        json.dumps(
            {
                "runs": {
                    "law": sorted(law.LAW),
                    "ring": "waterfields.ring_rules.ring_violations over every plot ring (needle, crossing, arrowhead, area, dart, steps, width, stroke, collector, pond, grave)",
                    "tests": [t[0] for t in tests],
                },
                "summary": summarize(rows, cannot),
                "maps": rows,
            },
            indent=1,
        )
    )
