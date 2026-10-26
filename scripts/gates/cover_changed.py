#!/usr/bin/env python3
"""cover_changed.py - the coverage floor asked of the engine modules a change touched, in seconds (the GM 2026-10-24).

    cover_changed.py [--base origin/main]      exit 1, naming each module and its uncovered lines; 0 when none

WHY. T135's landing ran `make done` for five minutes and failed on four lines of `knots.py` its own tests did not reach; the
gate's coverage floor is the only place coverage was asked. The GM: "we can check coverage in the specific files that changed,
and then that saves a lot of time."

WHAT IT ASKS (feature 430 T03, D3; the GM 2026-10-26, item 3: "on the changed modules, measured the way the full floor
measures them"). Every line of each engine module the change touched (`git diff` against the merge base with `--base`, the
working tree included) - not only the lines it added: on 2026-10-26 every line the coverage reds named was an EXISTING line
that lost its coverage, a test deleted with its caller or code moved behind a new branch, and the first form of this check,
which asked added lines alone, saw none of them (`specs/430-faster-landings/research.md` R1). The tests are the ones the
floor counts for those modules: every test the gate baseline's contexts show touching one (`incremental.contexts_touching`),
the changed test modules and the mirrored directory, less the map-rolling ones (`-m "not rolls_map"`: seconds, not minutes),
with the `tooling`-marked tests counted exactly when the floor counts them (`floor_markers`: forcing them in always, as the
first form did, counted new ones the floor did not - the sixth red, 9a157cc4b).

THE FLOOR'S CARRIED COVERAGE. A line this run leaves unrun is NOT named when the baseline shows it reached by a context this
run did not run (a roll, a reused tooling test, a fixture), of a test module unchanged since the baseline, and the line is
unchanged since the baseline (its old and new text
matched by `difflib`): the floor keeps that coverage the same way. With no baseline every test of the mirrored directory runs
and every line is asked.

WHAT IT CANNOT SEE, priced (feature 430 FR-009): a line a roll reached that the change stops a roll reaching is presumed still
reached; the gate's floor names it, as before. A line that loses its coverage in a module the change did NOT touch (a caller
changed or deleted) is outside "the changed modules" - 2 of the day's 6 reds were so; the gate names them. `make land` runs
this beside the gate and stops the gate the moment it refuses (`land.start_cover`); the escape is `COVER_OK="<reason>"`.
"""

from __future__ import annotations

import difflib
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT_OF_SCRIPT = Path(__file__).resolve().parents[2]
#: the engine modules this asks of: `l7r/**/*.py` (the gate's floor, `[tool.coverage.run]`)
ENGINE_PY = re.compile(r"^l7r/.*\.py$")
#: packages whose tests do not mirror them under `tests/` (the gate's own machinery is tested as tooling)
MIRRORS = {"l7r/diagram/ci/": "tests/tooling/ci"}
#: the marker expressions of the check's run: no map rolls (seconds, not minutes), and the tooling tests as the floor counts
#: them (`floor_markers`)
WITH_TOOLING = "not rolls_map and (tooling or not tooling)"
WITHOUT_TOOLING = "not rolls_map and not tooling"


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True).stdout


def changed_modules(root: Path, merge: str) -> list[str]:
    """The engine `.py` files that differ from `merge` (the working tree included) and still exist."""
    names = git(root, "diff", "--name-only", merge, "--", "l7r/").split() + git(root, "ls-files", "--others", "--exclude-standard", "--", "l7r/").split()
    return sorted({p for p in names if ENGINE_PY.match(p) and (root / p).is_file()})


def mirrored(root: Path, path: str) -> str:
    """The test directory that mirrors an engine module: `l7r/diagram/<pkg>/<mod>.py` -> `tests/<pkg>/`, climbing to the nearest
    one that exists; `tests` at worst; a package `MIRRORS` names, its own."""
    for prefix, tests in MIRRORS.items():
        if path.startswith(prefix) and (root / tests).is_dir():
            return tests
    rel = Path(path).relative_to("l7r/diagram") if path.startswith("l7r/diagram/") else Path(path).relative_to("l7r")
    d = Path("tests") / rel.parent
    while d != Path("tests") and not (root / d).is_dir():
        d = d.parent
    return str(d)


def tooling_unchanged(root: Path) -> bool:
    """`tests/conftest.py`'s own test: the tooling hash the last green `make done` recorded equals the current one."""
    from l7r.diagram.ci import state  # noqa: PLC0415

    try:
        rec = json.loads((root / state.STATE_FILE).read_text(encoding="utf-8"))
        return bool(rec.get("tooling")) and rec["tooling"] == state.tooling_hash(root)
    except Exception:  # noqa: BLE001 - any failure to decide means "run them", as conftest reads it
        return False


def floor_markers(root: Path, base: tuple[Path, dict] | None) -> str:
    """Whether the floor counts the `tooling`-marked tests, as the gate would run now: `tests/conftest.py` deselects them on a
    FULL plan (the gate passes the trees) whose tooling is unchanged since the last green gate, and keeps them on an incremental
    one (the gate passes test files, which conftest reads as asking for them). The sixth red of 2026-10-26 (9a157cc4b) was a
    full plan: the floor left new tooling-marked tests uncounted, which the first form of this check forced in."""
    from l7r.diagram.ci import incremental  # noqa: PLC0415

    old = os.environ.get("INCR_NO_CUTOFF")
    os.environ["INCR_NO_CUTOFF"] = "1"  # as `make land` plans the gate it runs (feature 415 T05)
    try:
        full = base is None or incremental.plan(root).mode == "full"
    finally:
        if old is None:
            os.environ.pop("INCR_NO_CUTOFF", None)
    return WITHOUT_TOOLING if full and tooling_unchanged(root) else WITH_TOOLING


def baseline(root: Path) -> tuple[Path, dict] | None:
    """The gate baseline's coverage database and manifest, or None (no green full run recorded in this tree)."""
    sys.path.insert(0, str(ROOT_OF_SCRIPT))  # the repository this script is in, not the tree it asks
    from l7r.diagram.ci import incremental  # noqa: PLC0415 - the gate's own reader of its baseline

    bdir = incremental.baseline_dir(root)
    db, man = bdir / incremental.COVERAGE_DB, bdir / incremental.MANIFEST
    if not (db.is_file() and man.is_file()):
        return None
    return db, json.loads(man.read_text(encoding="utf-8"))


def selected_tests(root: Path, modules: list[str], base: tuple[Path, dict] | None) -> list[str]:
    """The test files to run: the baseline's contexts touching `modules`, the changed test modules, the mirrored directories."""
    out = {mirrored(root, p) for p in modules}
    if base is not None:
        from l7r.diagram.ci import incremental  # noqa: PLC0415

        for ctx in incremental.contexts_touching(base[0], root, tuple(modules)):
            mod = ctx.split("::", 1)[0]
            if "|" in ctx and not ctx.startswith("fixture:") and (root / mod).is_file():
                out.add(mod)
    return sorted(out)


def unchanged_test(root: Path, module: str, manifest: dict) -> bool:
    """Is this test module the baseline's, byte for byte? A test the change deleted or edited carries nothing: the floor drops a
    deleted or selected test's contexts ("THE MERGE" (b), `incremental.py`), and 2026-10-26's reds were lines whose test went."""
    blob = manifest.get("tests", {}).get(module)
    if not blob or not (root / module).is_file():
        return False
    return git(root, "hash-object", module).strip() == blob


def carried(root: Path, path: str, base: tuple[Path, dict], ran: set[str]) -> set[int]:
    """The CURRENT line numbers of `path` the baseline shows reached by a context this run did not run, unchanged since."""
    import sqlite3  # noqa: PLC0415

    from coverage.numbits import numbits_to_nums  # noqa: PLC0415

    con = sqlite3.connect(str(base[0]))
    try:
        rows = con.execute(
            "select c.context, l.numbits from line_bits l join file f on f.id = l.file_id join context c on c.id = l.context_id where f.path = ?",
            (str(root / path),),
        ).fetchall()
    finally:
        con.close()
    old: set[int] = set()
    for ctx, bits in rows:
        node = ctx.split("|", 1)[0]
        if ctx and node not in ran and (ctx.startswith("fixture:") or unchanged_test(root, node.split("::", 1)[0], base[1])):
            old |= set(numbits_to_nums(bits))
    blob = base[1].get("engine", {}).get(path)
    before = subprocess.run(["git", "-C", str(root), "cat-file", "-p", blob], capture_output=True, text=True).stdout if blob else ""
    now = (root / path).read_text(encoding="utf-8")
    out: set[int] = set()
    sm = difflib.SequenceMatcher(a=before.splitlines(), b=now.splitlines(), autojunk=False)
    for tag, i1, i2, j1, _j2 in sm.get_opcodes():
        if tag == "equal":
            out |= {j1 + (n - i1) for n in range(i1 + 1, i2 + 1) if n in old}
    return out


def coverage_config(root: Path, data: Path, tmp: Path) -> Path:
    """`pyproject.toml`'s `[tool.coverage.*]` tables as a config file of the check's own, its data file in `tmp`."""
    import tomllib  # noqa: PLC0415

    tables = tomllib.loads((root / "pyproject.toml").read_text(encoding="utf-8")).get("tool", {}).get("coverage", {}) if (root / "pyproject.toml").is_file() else {}
    tables = {k: dict(v) for k, v in tables.items() if isinstance(v, dict)}
    tables.setdefault("run", {})["data_file"] = str(data)
    lines: list[str] = []
    for section, values in tables.items():
        lines.append(f"[{section}]")
        for key, value in values.items():
            lines.append(f"{key} =" + ("".join(f"\n    {v}" for v in value) if isinstance(value, list) else f" {value}"))
    rc = tmp / "coveragerc"
    rc.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return rc


def ran_tests(root: Path, junit: Path) -> set[str]:
    """The node ids of every test a JUnit report says ran - `tests.a.test_b.TestC` + `test_d[p]` read back as
    `tests/a/test_b.py::TestC::test_d[p]`, the module found as the longest dotted prefix that is a file."""
    import xml.etree.ElementTree as ET  # noqa: PLC0415

    if not junit.is_file():
        return set()
    out: set[str] = set()
    for case in ET.parse(junit).iter("testcase"):
        if case.find("skipped") is not None:
            continue
        parts = (case.get("classname") or "").split(".")
        for i in range(len(parts), 0, -1):
            if (root / Path(*parts[:i]).with_suffix(".py")).is_file():
                out.add("::".join([Path(*parts[:i]).with_suffix(".py").as_posix(), *parts[i:], case.get("name") or ""]))
                break
    return out


def uncovered(root: Path, modules: list[str], base: tuple[Path, dict] | None) -> dict[str, list[int]]:
    """Each changed module's lines the floor's tests leave unrun, less the floor's carried coverage."""
    sources = sorted({str(Path(p).parent) for p in modules})
    with tempfile.TemporaryDirectory() as tmp:
        report, data = Path(tmp) / "cover.json", Path(tmp) / ".coverage"
        junit = Path(tmp) / "ran.xml"
        # ...WHICH TESTS RAN, FROM A JUNIT REPORT, NOT `--cov-context=test` (the replay of 39ea51383: without the gate's own plugins
        # beside it, the context switch crashed an xdist worker, "no such table: context", every time)
        cmd = [sys.executable, "-m", "pytest", "-q", "-n", "4", "--dist", "worksteal", "-p", "no:cacheprovider", "-m", floor_markers(root, base), "--cov-fail-under=0", f"--junitxml={junit}"]
        cmd += [*(f"--cov={s}" for s in sources), f"--cov-report=json:{report}", *selected_tests(root, modules, base)]
        # ...ITS COVERAGE DATA IN ITS OWN DIRECTORY (feature 415 T05's third red gate): beside a landing's gate, in the same tree,
        # its run wrote `.coverage` files where the gate's workers wrote theirs, and the gate's data lost its tables. Named in a
        # config file of its own, NOT in `COVERAGE_FILE` (feature 430 T03's replay of 39ea51383): the environment reaches every
        # child, and the tooling tests that run coverage in a fixture clone found no `.coverage` of their own - 15 errors there
        cmd.insert(cmd.index("--cov-fail-under=0"), f"--cov-config={coverage_config(root, data, Path(tmp))}")
        done = subprocess.run(cmd, cwd=root, capture_output=True, text=True, env={k: v for k, v in os.environ.items() if k != "COVERAGE_FILE"})
        if not report.is_file():  # pytest wrote no report: say why, never pass silently
            raise RuntimeError("cover-changed: the tests wrote no coverage report - " + (done.stdout + done.stderr).strip()[-800:])
        files = json.loads(report.read_text(encoding="utf-8")).get("files", {})
        ran = ran_tests(root, junit) if base is not None else set()
    out = {}
    for path in modules:
        missing = set((files.get(path) or {}).get("missing_lines") or [])
        if base is not None and missing:
            missing -= carried(root, path, base, ran)
        if missing:
            out[path] = sorted(missing)
    return out


def main(argv: list[str]) -> int:
    base_ref = argv[argv.index("--base") + 1] if "--base" in argv else "origin/main"
    root = Path(git(Path.cwd(), "rev-parse", "--show-toplevel").strip() or ".")
    merge = git(root, "merge-base", base_ref, "HEAD").strip() or base_ref
    modules = changed_modules(root, merge)
    if not modules:
        return 0
    missing = uncovered(root, modules, baseline(root))
    for path, lines in missing.items():
        print(f"cover-changed: {path} - lines the floor's tests do not reach: {', '.join(map(str, lines))}")
    if missing:
        print(
            "cover-changed: a test for each, in the mirrored file, before the gate's five minutes find it (`make cover-changed` "
            "asks again in seconds); a line only a roll reaches, newly: COVER_OK=\"<reason>\""
        )
        return 1
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    sys.exit(usage_log.exited("cover_changed", main(sys.argv[1:])))
