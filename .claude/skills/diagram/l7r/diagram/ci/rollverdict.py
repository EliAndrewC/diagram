"""The roll census's attribution and VERDICT (feature 213, GM 2026-09-07).

Two halves. The attribution half is called by the `-p` shim (`rollcensus.py`) inside each test worker:
`begin(nodeid)` puts the test's id and a fresh request id into the environment, `end()` takes them out, and
`rolls_first(items)` moves the map-rolling tests to the front of collection. The verdict half runs once,
after pytest, from the Makefile (`python3 -m l7r.diagram.ci rollcensus verdict`): it reads the census file
the engine wrote at its chokepoints (`_census.py`) and judges it against the roster (`tests/rolls.py`).

WHAT FAILS THE GATE, each named in the spec (FR-003):
  - a spec ROLLED more than once in the run - two distinct request ids, less the roster's stated
    Duplicates; a `generate` that re-rolls inside one request is ONE roll with N attempts, reported;
  - a rolled spec the roster does not list - the message says to add the row with its reason;
  - on a FULL run, a roster row nothing rolled - a stale roster is as wrong as a short one;
  - a render (a PNG or the page's raster) from a test that does not carry the `renders` marker;
  - a roll IN THE WORKER (the record's pid is the worker's) from a test module the roster does not except.
Many tests SERVED by one roll is the passing state - that is the whole point of the share.
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import uuid
from collections import defaultdict
from pathlib import Path
from typing import Any

from l7r.diagram import _census

MARKER = "renders"  # the marker a test OF rendering carries (registered in pyproject.toml)
STUB_SPEC_NAMES = ()  # none: a stub-stage roll is excused by its test module in the roster's IN_PROCESS, not by name


# ---------------------------------------------------------------------------------------------------
# attribution (in the worker)
# ---------------------------------------------------------------------------------------------------


def configure() -> None:
    os.environ[_census.WORKER_ENV] = str(os.getpid())


def begin(nodeid: str) -> None:
    os.environ[_census.TEST_ENV] = nodeid
    os.environ[_census.REQUEST_ENV] = uuid.uuid4().hex[:12]


def end() -> None:
    os.environ.pop(_census.TEST_ENV, None)
    os.environ.pop(_census.REQUEST_ENV, None)


def rolls_first(items: list[Any]) -> None:
    """The map-rolling tests (the `rolls_map` marker, which `tests/test_markers.py` proves every roller carries)
    to the front, in their collected order; everything else after, in its. Under worksteal the long rolls then
    start at t=0 rather than when a worker happens to reach their module (spec FR-010). And the tests OF
    rendering - the `renders` marker - are written beside the census, because the verdict runs after pytest
    and cannot ask a collected item for its markers then."""
    rolling = [it for it in items if it.get_closest_marker("rolls_map") is not None]
    rest = [it for it in items if it.get_closest_marker("rolls_map") is None]
    items[:] = rolling + rest
    path = os.environ.get(_census.ENV)
    if path:
        renders = sorted(it.nodeid for it in items if it.get_closest_marker(MARKER) is not None)
        with contextlib.suppress(OSError):
            Path(renders_file(path)).write_text("\n".join(renders) + "\n", encoding="utf-8")


def renders_file(census_path: str) -> str:
    return census_path + ".renders"


# ---------------------------------------------------------------------------------------------------
# the verdict (after pytest)
# ---------------------------------------------------------------------------------------------------


def read(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.is_file():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except ValueError:
            continue  # a half-written line from a killed child is not a verdict
    return rows


def _key(spec: dict[str, Any] | None) -> tuple[str, int] | None:
    if not spec or spec.get("name") is None or spec.get("seed") is None:
        return None
    return (str(spec["name"]), int(spec["seed"]))


def _module(nodeid: str | None) -> str:
    return (nodeid or "").split("::")[0]


def _excepted(nodeid: str | None, in_process: Any) -> bool:
    mod = _module(nodeid)
    return any(mod == e.module or mod.startswith(e.module) for e in in_process)


def judge(rows: list[dict[str, Any]], roster: Any, *, full: bool, renders_ok: set[str]) -> tuple[list[str], list[str]]:
    """`(failures, report_lines)` for one run's census against `roster` (the `tests.rolls` module).

    `renders_ok` is the set of test ids that carry the `renders` marker (the plugin cannot see markers
    at record time; the Makefile passes the file the collection wrote). A roll is a group of `roll`
    records sharing (spec key, request id): its attempts are the records, its test the first record's."""
    rolls: dict[tuple[tuple[str, int], str], list[dict[str, Any]]] = defaultdict(list)
    unnamed: list[dict[str, Any]] = []
    for r in rows:
        if r.get("kind") != "roll":
            continue
        key = _key(r.get("spec"))
        if key is None:
            unnamed.append(r)
            continue
        rolls[(key, str(r.get("request")))].append(r)
    by_spec: dict[tuple[str, int], list[list[dict[str, Any]]]] = defaultdict(list)
    for (key, _req), attempts in rolls.items():
        by_spec[key].append(attempts)
    rostered = roster.by_key()
    failures: list[str] = []
    lines: list[str] = []
    served = sum(1 for r in rows if r.get("kind") == "served")
    total = sum(len(v) for v in by_spec.values())
    lines.append(f"roll census: {total} roll(s) of {len(by_spec)} spec(s); {served} request(s) served from a shared roll; roster {len(rostered)} row(s)")
    for key in sorted(by_spec, key=lambda k: (k[0], k[1])):
        groups = by_spec[key]
        tests = sorted({str(g[0].get("test")) for g in groups})
        attempts = ", ".join(str(len(g)) for g in groups)
        secs = sum(float(r.get("dt") or 0) for g in groups for r in g)
        row = rostered.get(key)
        lines.append(f"  {key[0]} seed={key[1]}: {len(groups)} roll(s), attempts {attempts}, {secs:.0f}s - {'rostered' if row else 'NOT IN THE ROSTER'}; requested by {', '.join(t.split('::')[-1][:60] for t in tests)}")
        if row is None:
            failures.append(f"{key[0]} seed={key[1]} was rolled by {tests[0]} but is not in the roster: add a `Roll` to tests/rolls.py naming what this roll uniquely carries - or reuse a rostered roll")
        allowed_dups = [d for d in roster.DUPLICATES if d.key == key]
        extra = len(groups) - 1 - len([d for d in allowed_dups if any(str(g[0].get("test", "")).startswith(d.test) for g in groups)])
        if extra > 0:
            failures.append(f"{key[0]} seed={key[1]} was rolled {len(groups)} times in one run (by {', '.join(tests)}) - a spec is rolled ONCE per gate and shared; a site that must roll it again by its nature is a stated `Duplicate` in tests/rolls.py")
        for g in groups:
            first = g[0]
            if str(first.get("pid")) == str(first.get("worker")) and not _excepted(first.get("test"), roster.IN_PROCESS):
                failures.append(f"{key[0]} seed={key[1]} was rolled IN THE TEST WORKER by {first.get('test')} - every gate roll runs in a child (spec FR-007); a site that must roll in the worker is a stated `InProcess` exception in tests/rolls.py")
    if full:
        for key, row in sorted(rostered.items()):
            if key not in by_spec:
                failures.append(f"roster row {key[0]} seed={key[1]} ({row.rolled_by}) was not rolled by this full run - a stale row is as wrong as a missing one; remove it or roll it")
    for r in unnamed:
        if str(r.get("pid")) == str(r.get("worker")) and not _excepted(r.get("test"), roster.IN_PROCESS):
            failures.append(f"a roll with no spec ran in the test worker under {r.get('test')} - pass the spec to roll_scope, or except the module in tests/rolls.py")
    for r in rows:
        if r.get("kind") == "render" and str(r.get("test") or "") not in renders_ok:
            failures.append(f"{r.get('test')} rendered a {r.get('what')} - tests do not render (DIAGRAM_SKIP_RENDER is the suite's default); a test OF rendering carries the `renders` marker")
    for d in roster.DUPLICATES:
        lines.append(f"  stated duplicate: {d.key[0]} seed={d.key[1]} by {d.test.split('::')[-1][:60]} ({d.mechanism}) - {d.reason}")
    return failures, lines


def main(argv: list[str]) -> int:
    """`verdict [--full]` - the Makefile's call after the test phase; `--full` when the run was a full one,
    so a stale roster row counts."""
    if not argv or argv[0] != "verdict":
        print("usage: rollcensus verdict [--full]", file=sys.stderr)
        return 2
    path = os.environ.get(_census.ENV)
    if not path:
        print("rollcensus: L7R_ROLL_CENSUS is not set - no census to judge", file=sys.stderr)
        return 2
    rfile = Path(renders_file(path))
    renders_ok = {ln.strip() for ln in rfile.read_text(encoding="utf-8").splitlines() if ln.strip()} if rfile.is_file() else set()
    from tests import rolls  # the roster lives beside the tests it governs (spec D1)

    failures, lines = judge(read(Path(path)), rolls, full="--full" in argv, renders_ok=renders_ok)
    print("\n".join(lines))
    if failures:
        print("\nROLL CENSUS FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("roll census: green")
    return 0
