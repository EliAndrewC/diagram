"""THE INCREMENTAL GATE (feature 207, GM 2026-09-07): re-run only the tests a change can reach, and still
judge 100% coverage over the whole engine.

WHY. Since feature 174 a plain `make done` on ANY engine change ran the whole suite - eight to ten
minutes - because the 100% floor is measured over whatever ran, and a deselected test takes its coverage
with it. The GM: *"eight minutes is a long time, and I would really like to get that down"*, and *"a change
to something specific to one type of hamlet will cause all of the tests to run, including the core engine
tests?"* - it did. This module keeps the coverage of the last FULL green run PER TEST (coverage's dynamic
contexts, `--cov-context=test`), selects the tests whose recorded execution touched a changed file,
re-runs only those, and merges their fresh coverage over the kept coverage before the floors are judged.

THE ARGUMENT, so nobody has to rediscover it (spec research R4). Baseline B = the coverage data of the last
full green run, with contexts, plus a manifest of every file the gate exercises (raw git blob ids - RAW,
not the docstring-stripped id the short-circuit keys on, because a formatting-only edit moves LINE
NUMBERS and the baseline's line data for that file would then lie). Changed set C = files whose id differs,
plus added and removed files. A test is SELECTED when: any of its own contexts (`setup`/`run`/`teardown`)
executed a file in C; any FIXTURE in its closure executed a file in C (fixtures get their own contexts -
`selection.py` - because pytest-cov attributes a session fixture's setup to whichever test first asked
for it, and forty tests then read what that fixture built); its own test module changed; or the baseline
never saw it. A test outside that set executed no file in C, and the only way it could reach changed code
now is through a file that changed - which is in C, and it would have executed it. The suite is
deterministic (fixed seeds, no clock), so its baseline contexts are its true coverage. Import-time code is
the one exception to "reached through a changed file": a changed line that the baseline's import-time
context executed (a `def` line, a decorator, a module-level statement) changes what EVERY importer sees, so
that shape falls back to a full run rather than being reasoned about.

THE MERGE. A copy of B with (a) every changed or removed file dropped from every context, (b) every
context of a selected or deleted test dropped, and (c) every context of an affected fixture dropped -
affected transitively, since a fixture whose input fixture changed may itself behave differently - is
combined with the fresh run's data by union, and `coverage report --fail-under=100` plus the hamlet floor
judge the result. (b) is what makes a change that leaves a line of an UNCHANGED module unreachable fail:
the test that used to reach it re-runs and no longer does, and its old context is gone.

THE BASELINE IS THE LAST FULL RUN, NEVER A MERGED RESULT (spec D1): the selection grows as changes
accumulate between full runs, and a full run - a fallback, `INCREMENTAL=0`, `FULL=1` - resets it. Nothing
compounds. Fallbacks to FULL, each because file-level selection cannot see the dependency: no baseline; a
changed engine file that is not `.py` (a pool generator or manifest); a changed file under `tests/` that is
not a test module (`conftest.py`, `_scope.py`, a helper, `fixtures/`); the tooling hash moved; an
import-time line changed; or more than `FULL_FRACTION` of the suite selected (`selection.py` decides that
one, after collection). It lives under the clone's git directory - per clone, never in the tree.
"""

from __future__ import annotations

import difflib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from l7r.diagram.ci import state

#: Above this fraction of the collected suite the incremental run costs about what a full one does
#: (collection, the reference roll and the floors are fixed costs) and gives up the baseline refresh - so the
#: plugin runs everything and marks the run FULL. A knob with its reason; not a measured optimum (spec D3).
FULL_FRACTION = 0.6

BASELINE_DIR = "gate-baseline"
COVERAGE_DB = "coverage.db"
MANIFEST = "manifest.json"
TESTS = "tests.json"  # nodeid -> the fixture closure it requests; written by selection.py on the controller
GRAPH = "fixtures.json"  # fixture id -> its dependents; kept BESIDE the baseline because a restricted run sees only part of it (feature 237, FR-005)
# THE PATH A RESTRICTED RUN WITH NOTHING TO RUN IS GIVEN (feature 237, FR-002). An incremental plan can
# legitimately reach nothing - "nothing the baseline exercised has changed" - and the wrong answer there is to
# fall back to the trees, which pays the whole tree's collection (3.1 GiB measured, research R3/R10) to execute
# zero tests. pytest refuses a path that does not exist before any plugin runs, so the path must be REAL and
# hold no tests: `tests/__init__.py` collects nothing, the selection plugin still records its result, and the
# empty-selection-is-green branch in `GateSelection.pytest_sessionfinish` still turns exit 5 into 0.
NO_TESTS = "tests/__init__.py"
PLAN = "plan.json"  # written by `plan`, read by selection.py
RESULT = "result.json"  # written by selection.py after collection, read by `merge` / `save-baseline` / the Makefile
TEST_MODULE = "test_"


def baseline_dir(root: Path) -> Path:
    """`<git dir>/gate-baseline/` - beside the verification state, so a worktree gets its own."""
    return state._state_file(root).parent / BASELINE_DIR


# ---- the manifest -------------------------------------------------------------------------------------


def manifest(root: Path) -> dict[str, Any]:
    """Every file the gate exercises, by RAW blob id: gate-stamp's `diagram` area (engine `.py`, pool
    generators and manifests, `ci/`) and every file under the skill's `tests/`, plus the tooling hash."""
    from l7r.diagram.ci.delta import is_engine

    gs = state._gate_stamp(root)
    area, patterns = gs.AREAS["diagram"]
    listed = [
        p
        for p in subprocess.run(["git", "-C", str(root), "ls-files", "-co", "--exclude-standard", "--", area], capture_output=True, text=True, check=True).stdout.splitlines()
        if p.strip() and (root / p).is_file()
    ]
    # the stamp's area (every `.py` the gate exercises, `ci/` included) PLUS the route's engine files (the pool
    # generators and manifests, which the stamp's `*.py` pattern does not see) - a manifest edit is a fallback shape
    engine = sorted({str(p.relative_to(root)) for p in gs._area_files(root, area, patterns)} | {p for p in listed if is_engine(p)})
    tests = sorted(p for p in listed if p.startswith(f"{area}/tests/"))
    return {"engine": _blob_ids(root, engine), "tests": _blob_ids(root, tests), "tooling": state.tooling_hash(root)}


def _blob_ids(root: Path, paths: list[str]) -> dict[str, str]:
    """Raw ids from `git hash-object`, in one call - the CURRENT contents, tracked or not."""
    if not paths:
        return {}
    out = subprocess.run(["git", "-C", str(root), "hash-object", "--stdin-paths"], input="\n".join(paths) + "\n", capture_output=True, text=True, check=True).stdout.split()
    return dict(zip(paths, out, strict=True))


@dataclass(frozen=True)
class Changed:
    engine: tuple[str, ...]  # engine files whose bytes differ, added, or removed (repo-relative)
    removed: tuple[str, ...]  # the subset no longer in the tree
    test_modules: tuple[str, ...]  # `test_*.py` files under tests/ that differ, added, or removed
    other_tests: tuple[str, ...]  # any other changed file under tests/ - a fallback shape
    tooling_moved: bool


def changed(before: dict[str, Any], now: dict[str, Any]) -> Changed:
    def diff(key: str) -> list[str]:
        a, b = before.get(key, {}), now.get(key, {})
        return sorted(p for p in set(a) | set(b) if a.get(p) != b.get(p))

    eng = diff("engine")
    tests = diff("tests")
    is_module = lambda p: os.path.basename(p).startswith(TEST_MODULE) and p.endswith(".py")  # noqa: E731
    return Changed(
        engine=tuple(eng),
        removed=tuple(p for p in eng if p not in now.get("engine", {})),
        test_modules=tuple(p for p in tests if is_module(p)),
        other_tests=tuple(p for p in tests if not is_module(p)),
        tooling_moved=before.get("tooling") != now.get("tooling"),
    )


# ---- reading the baseline's contexts ------------------------------------------------------------------


SKILL_PREFIX = ".claude/skills/diagram/"  # nodeids are skill-relative; the manifest is repo-relative


def _marks(items: Any) -> str:
    """`?,?,?` - one placeholder per item, for an `in (...)` clause."""
    return ",".join("?" * len(items))


def contexts_touching(db: Path, root: Path, files: tuple[str, ...]) -> set[str]:
    """Every context name in the baseline coverage data that recorded ANY line of one of `files` (repo-relative)."""
    if not files:
        return set()
    absolute = {str(root / f) for f in files}
    con = sqlite3.connect(str(db))
    try:
        touched = con.execute(
            f"select distinct c.context from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id where f.path in ({_marks(absolute)})",
            sorted(absolute),
        ).fetchall()
    finally:
        con.close()
    return {r[0] for r in touched}


def import_time_lines(db: Path, root: Path, path: str) -> set[int]:
    """The lines of `path` the baseline's import-time context (the empty context) executed."""
    from coverage.numbits import numbits_to_nums

    con = sqlite3.connect(str(db))
    try:
        row = con.execute("select l.numbits from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id where f.path = ? and c.context = ''", (str(root / path),)).fetchone()
    finally:
        con.close()
    return set(numbits_to_nums(row[0])) if row else set()


def old_lines_changed(before_text: str, now_text: str) -> set[int]:
    """The OLD file's line numbers that a change deleted or replaced (1-based). A pure insertion changes
    no old line, and needs none: nothing old reaches new code except through a changed line."""
    out: set[int] = set()
    sm = difflib.SequenceMatcher(a=before_text.splitlines(), b=now_text.splitlines(), autojunk=False)
    for tag, i1, i2, _j1, _j2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            out.update(range(i1 + 1, i2 + 1))
    return out


def import_time_change(root: Path, db: Path, before: dict[str, Any], ch: Changed) -> str | None:
    """The first changed engine `.py` whose change touched a line the baseline executed at import, or None."""
    for path in ch.engine:
        if not path.endswith(".py") or path in ch.removed or path not in before.get("engine", {}):
            continue
        executed = import_time_lines(db, root, path)
        if not executed:
            continue
        old = subprocess.run(["git", "-C", str(root), "cat-file", "-p", before["engine"][path]], capture_output=True, text=True, check=True).stdout
        if old_lines_changed(old, (root / path).read_text(encoding="utf-8")) & executed:
            return path
    return None


# ---- the plan -------------------------------------------------------------------------------------------


@dataclass
class Plan:
    mode: str  # "full" | "incremental"
    reason: str
    changed_engine: list[str] = field(default_factory=list)
    changed_test_modules: list[str] = field(default_factory=list)
    affected_tests: list[str] = field(default_factory=list)  # baseline nodeids whose own contexts touched a changed file
    affected_fixtures: list[str] = field(default_factory=list)  # fixture names whose context touched a changed file (direct)
    baseline_tests: list[str] = field(default_factory=list)
    full_fraction: float = FULL_FRACTION  # the planner's knob; `over_the_fraction` applies it before the arguments are chosen
    paths: list[str] = field(default_factory=list)  # the test modules this run may reach - pytest's positional arguments (feature 237, FR-001)

    def dump(self) -> dict[str, Any]:
        return self.__dict__


def reachable_modules(affected_tests: list[str], changed_test_modules: list[str], affected_fixtures: list[str], closures: dict[str, list[str]]) -> list[str]:
    """The test modules an incremental run can reach, derived from the PLAN's own inputs - nothing collected.

    This is `keep_set`'s four rules projected onto modules, and it must be a SUPERSET of the modules
    `keep_set` will keep, or a test that should run is never collected (feature 237, FR-001):

      * a baseline test whose own context touched a changed file -> its module;
      * a changed test module -> itself, which also covers every NEW test, because adding a test changes
        its module and git therefore reports it;
      * a baseline test whose fixture closure holds a directly affected fixture -> its module. `keep_set`
        reads `affected_fixtures` directly rather than its transitive closure, so this does too.

    Nothing circular: the closures come from `tests.json`, written by the last FULL run.
    """
    mods = {n.split("::", 1)[0] for n in affected_tests} | set(changed_test_modules)
    if affected_fixtures:
        wanted = set(affected_fixtures)
        mods |= {nodeid.split("::", 1)[0] for nodeid, closure in closures.items() if wanted & set(closure)}
    return sorted(mods)


def over_the_fraction(pl: Plan, closures: dict[str, list[str]]) -> int:
    """How many BASELINE tests this plan reaches - the projection the `FULL_FRACTION` decision is made on.

    The decision used to be made after collection, in `selection.py`, where the real selection is known.
    Feature 237 moved it here because the gate now chooses pytest's ARGUMENTS from the plan: a run whose
    arguments were narrowed cannot then decide to run everything. Projecting over the baseline rather than
    over the collection is the one thing lost, and it can only UNDERCOUNT - by the tests that are new, which
    live in changed modules and are few - so a plan near the line runs incrementally instead of fully, which
    is the safe direction: incremental runs merge over the baseline, full runs replace it.
    """
    from l7r.diagram.ci.selection import keep_set  # local: selection imports this module, so a top-level import is a cycle

    return len(keep_set(pl.dump(), pl.baseline_tests, closures))


def existing(root: Path, modules: list[str]) -> list[str]:
    """Only the modules still on disk, because pytest dies on an argument that is not there.

    A DELETED test module reaches the plan by two routes - `changed()` reports a removed file as a changed
    one, and the baseline's contexts still name its tests - and pytest resolves its positional arguments
    before any plugin loads, so a stale path would exit 4 ("file or directory not found") and take the gate
    with it rather than running the tests that remain. Dropping it is right as well as safe: its tests no
    longer exist, and `stale_tests` already drops their contexts from the merge.
    """
    return [m for m in modules if (root / SKILL_PREFIX / m).is_file()]


def plan(root: Path, force_full: str | None = None) -> Plan:
    """Decide the mode before collection. Everything that needs the collected items is `selection.py`'s."""
    bdir = baseline_dir(root)
    db, man, tests = bdir / COVERAGE_DB, bdir / MANIFEST, bdir / TESTS
    if force_full:
        return Plan("full", force_full)
    if not (db.is_file() and man.is_file() and tests.is_file()):
        return Plan("full", "no baseline - this run records one")
    before = json.loads(man.read_text(encoding="utf-8"))
    ch = changed(before, manifest(root))
    if ch.other_tests:  # before the tooling rule: a conftest edit moves the tooling hash too, and the specific reason is the useful one
        return Plan("full", f"a non-module file under tests/ changed: {ch.other_tests[0]}" + (f" (+{len(ch.other_tests) - 1})" if len(ch.other_tests) > 1 else ""))
    if ch.tooling_moved:
        return Plan("full", "the tooling changed (Makefile, pyproject, lockfiles, scripts/)")
    non_py = [p for p in ch.engine if not p.endswith(".py")]
    if non_py:
        return Plan("full", f"an engine file that is not Python changed: {non_py[0]}")
    closures: dict[str, list[str]] = json.loads(tests.read_text(encoding="utf-8"))
    baseline_tests = sorted(closures)
    if not ch.engine and not ch.test_modules:
        return Plan("incremental", "nothing the baseline exercised has changed", [], [], [], [], baseline_tests, FULL_FRACTION, [])
    hit = import_time_change(root, db, before, ch)
    if hit:
        return Plan("full", f"a line executed at import time changed in {hit}")
    touched = contexts_touching(db, root, ch.engine)
    affected_tests = sorted({c.split("|", 1)[0] for c in touched if "|" in c and not c.startswith("fixture:")})
    affected_fixtures = sorted({c[len("fixture:") :].split("|", 1)[0] for c in touched if c.startswith("fixture:")})
    changed_modules = [m[len(SKILL_PREFIX) :] for m in ch.test_modules]
    pl = Plan(
        "incremental",
        f"{len(ch.engine)} engine file(s) and {len(ch.test_modules)} test module(s) changed",
        list(ch.engine),
        changed_modules,
        affected_tests,
        affected_fixtures,
        baseline_tests,
        FULL_FRACTION,
        existing(root, reachable_modules(affected_tests, changed_modules, affected_fixtures, closures)),
    )
    reached = over_the_fraction(pl, closures)
    if reached > FULL_FRACTION * len(baseline_tests):
        return Plan("full", f"{reached} of {len(baseline_tests)} baseline tests reached, over the {FULL_FRACTION:.0%} fraction - running everything and recording a baseline")
    return pl


# ---- the merge ------------------------------------------------------------------------------------------


def prune(db: Path, root: Path, drop_files: tuple[str, ...], drop_contexts: set[str]) -> None:
    """Delete, in place, every row for `drop_files` (repo-relative, any context) and every row of `drop_contexts`."""
    con = sqlite3.connect(str(db))
    try:
        if drop_files:
            absolute = sorted(str(root / f) for f in drop_files)
            con.execute(f"delete from line_bits where file_id in (select id from file where path in ({_marks(absolute)}))", absolute)
            con.execute(f"delete from arc where file_id in (select id from file where path in ({_marks(absolute)}))", absolute)
            con.execute(f"delete from tracer where file_id in (select id from file where path in ({_marks(absolute)}))", absolute)
            con.execute(f"delete from file where path in ({_marks(absolute)})", absolute)
        if drop_contexts:
            names = sorted(drop_contexts)
            for i in range(0, len(names), 500):
                chunk = names[i : i + 500]
                con.execute(f"delete from line_bits where context_id in (select id from context where context in ({_marks(chunk)}))", chunk)
                con.execute(f"delete from arc where context_id in (select id from context where context in ({_marks(chunk)}))", chunk)
        con.commit()
    finally:
        con.close()


def all_contexts(db: Path) -> list[str]:
    con = sqlite3.connect(str(db))
    try:
        return [r[0] for r in con.execute("select context from context").fetchall()]
    finally:
        con.close()


def fixture_closure(affected: list[str], dependents: dict[str, list[str]]) -> set[str]:
    """Every fixture that depends, transitively, on an affected one - `dependents` maps a fixture to the fixtures that request it."""
    out, todo = set(affected), list(affected)
    while todo:
        for d in dependents.get(todo.pop(), []):
            if d not in out:
                out.add(d)
                todo.append(d)
    return out


def merge(root: Path, fresh: Path, out: Path) -> dict[str, Any]:
    """The merged data file for the floors: the pruned baseline unioned with this run's data."""
    import coverage

    bdir = baseline_dir(root)
    result = json.loads((bdir / RESULT).read_text(encoding="utf-8"))
    pl = json.loads((bdir / PLAN).read_text(encoding="utf-8"))
    tmp = out.with_suffix(".merging")
    shutil.copyfile(bdir / COVERAGE_DB, tmp)
    gone = stale_tests(pl["baseline_tests"], result["collected"], pl["changed_test_modules"])
    # THE GRAPH IS THE BASELINE'S UNIONED WITH THIS RUN'S (feature 237, FR-005). This run's edges cover only
    # what it collected, and a restricted run collects a few modules - so a fixture whose upstream changed
    # would keep the stale contexts of every dependent defined elsewhere, and the floor would pass over them.
    # The same hole was already open for any `--ignore`d tree (`FULL_TREE_IGNORE`, `BROWSER_SKIP`), so this
    # fixes a defect that predates the restriction (Principle XIV).
    from l7r.diagram.ci.selection import merge_graphs

    gf = bdir / GRAPH
    known = json.loads(gf.read_text(encoding="utf-8")) if gf.is_file() else {}
    fixtures = fixture_closure(pl["affected_fixtures"], merge_graphs(known, result.get("fixture_dependents", {})))
    dead = set(result["selected"]) | gone
    drop = {c for c in all_contexts(tmp) if (c.split("|", 1)[0] in dead) or (c.startswith("fixture:") and c[len("fixture:") :] in fixtures)}
    prune(tmp, root, tuple(pl["changed_engine"]), drop)
    merged = coverage.CoverageData(str(tmp))
    merged.read()
    new = coverage.CoverageData(str(fresh))
    new.read()
    merged.update(new)
    merged.write()
    os.replace(tmp, out)
    return {"dropped_contexts": len(drop), "dropped_files": len(pl["changed_engine"]), "affected_fixtures": sorted(fixtures)}


def stale_tests(baseline: list[str], collected: list[str], changed_modules: list[str]) -> set[str]:
    """Baseline tests whose contexts must go: every test of a changed or removed module (they are all
    re-run or gone), and a test that VANISHED from an unchanged module that was collected - a parametrization
    the engine computes at collection time can shrink. A module not collected at all (an `--ignore`, the
    browser package under a fresh stamp) keeps its tests' contexts: nothing about them changed."""
    seen = set(collected)
    modules_collected = {n.split("::", 1)[0] for n in collected}
    out = set()
    for n in baseline:
        m = n.split("::", 1)[0]
        if m in changed_modules or (m in modules_collected and n not in seen):
            out.add(n)
    return out


def save_baseline(root: Path, fresh: Path) -> Path:
    """After a green FULL floor phase: this run's coverage data and the manifest become the baseline."""
    bdir = baseline_dir(root)
    bdir.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(fresh, bdir / COVERAGE_DB)
    (bdir / MANIFEST).write_text(json.dumps(manifest(root), indent=1), encoding="utf-8")
    for name in (TESTS, GRAPH):
        nxt = bdir / (name + ".next")
        if nxt.is_file():
            os.replace(nxt, bdir / name)
    return bdir


# ---- the command --------------------------------------------------------------------------------------


def main(argv: list[str], root: Path, skill: Path) -> int:
    """`plan [--full REASON]` | `merge` | `save-baseline` | `mode` - the Makefile's four calls."""
    bdir = baseline_dir(root)
    cmd = argv[0] if argv else ""
    if cmd == "plan":  # `plan [full REASON]` - a positional, because the ci parser owns `--full` (feature 130) and would eat the flag
        force = argv[2] if len(argv) > 2 and argv[1] == "full" else None
        pl = plan(root, force)
        bdir.mkdir(parents=True, exist_ok=True)
        (bdir / PLAN).write_text(json.dumps(pl.dump(), indent=1), encoding="utf-8")
        (bdir / RESULT).unlink(missing_ok=True)
        print(
            f"gate: {pl.mode.upper()} - {pl.reason}"
            + (f"; {len(pl.affected_tests)} test(s) and {len(pl.affected_fixtures)} fixture(s) touched the change" if pl.mode == "incremental" and pl.changed_engine else "")
        )
        return 0
    if cmd == "paths":  # the positional arguments pytest is given: the modules this run may reach (feature 237, FR-002)
        pf = bdir / PLAN
        pl = json.loads(pf.read_text(encoding="utf-8")) if pf.is_file() else {"mode": "full"}
        if pl.get("mode") != "incremental":
            return 0  # a full run is given the trees, exactly as before
        print(" ".join(pl.get("paths") or [NO_TESTS]))
        return 0
    if cmd == "where":  # the baseline directory, for the Makefile's L7R_GATE_SELECT
        print(bdir)
        return 0
    if cmd == "mode":  # what the run turned out to be, after collection: full | incremental
        res = bdir / RESULT
        print(json.loads(res.read_text(encoding="utf-8"))["mode"] if res.is_file() else "full")
        return 0
    if cmd == "selected":  # "k/n" for the run log; empty when the run was full
        res = bdir / RESULT
        r = json.loads(res.read_text(encoding="utf-8")) if res.is_file() else {}
        print(f"{len(r['selected'])}/{len(r['collected'])}" if r.get("mode") == "incremental" else "")
        return 0
    if cmd == "merge":
        res = bdir / RESULT
        if not res.is_file() or json.loads(res.read_text(encoding="utf-8"))["mode"] != "incremental":
            print("gate: full run - nothing to merge")
            return 0
        info = merge(root, skill / ".coverage", skill / ".coverage")
        print(f"gate: merged this run over the baseline ({info['dropped_contexts']} context(s) and {info['dropped_files']} changed file(s) re-measured)")
        return 0
    if cmd == "save-baseline":
        res = bdir / RESULT
        if res.is_file() and json.loads(res.read_text(encoding="utf-8"))["mode"] == "incremental":
            print("gate: incremental run - the baseline stays the last full run (spec D1)")
            return 0
        where = save_baseline(root, skill / ".coverage")
        print(f"gate: baseline saved under {where}")
        return 0
    print("usage: incremental plan [full REASON] | paths | where | mode | selected | merge | save-baseline", file=sys.stderr)
    return 2
