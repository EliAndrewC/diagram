#!/usr/bin/env python3
"""The door of the gate's first phase to what reads Python and pytest (feature 449 T071, `ask:449-T071-scope`): the phase and the tree check are the Rust
gate's (`l7r-gate preflight`, `rust/gate/src/preflight.rs`); this file goes in phase 4, in the commit that removes pytest.

THE CHANGED ENGINE LINES covered - the quick tree run once more with coverage over just the engine files the delta changed, and every changed line it leaves
unrun named. A line in a module OFF the hamlet path (no rolled map reaches it; the path is `tools/claims.scope`, the import graph of hamlet generation) stops
the preflight: only a unit test can cover it, and the gate's 100% floor would refuse it minutes later. A line ON the path may be reached only by a rolled map,
which the preflight does not roll, so it is reported and left to the gate (the floor judges it there) - UNLESS the last green gate's coverage
(`<git dir>/gate-baseline/`) shows that line, as the baseline had it, reached by no test but those the quick tier runs: then no roll reaches it either, and the
preflight stops on it. The lines judged are every line of a FUNCTION the delta changed, not only its changed lines (feature 405 T40, D14: T14 reworked the one
unit test that reached an unchanged line, `sweeps.py:738`; the preflight passed and the gate's floor failed 5.7 minutes in).

    preflight.py --cover --root DIR --workers N     {"off": {file: [lines]}, "on": {...}}   (only `make preflight` asks)
    preflight.py --same-py --root DIR               stdin `<name>\\t<old file>\\t<new file>` lines; 1 or 0 per line
"""

# TOOL_RECORD: `l7r-gate preflight` records each run; this door is its helper
from __future__ import annotations

import argparse
import ast
import difflib
import json
import os
import re
import sqlite3
import subprocess
import sys
import tempfile
from collections.abc import Callable
from pathlib import Path

sys.dont_write_bytecode = True
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)


def git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else ""


def base(root: Path) -> str:
    return git(root, "merge-base", "HEAD", "origin/main").strip() or git(root, "rev-parse", "HEAD").strip()


def changed_lines(root: Path, widen: bool = True) -> dict[str, set[int]]:
    """Engine `.py` files the delta changed (against the merge base, working tree included), with the lines it added or changed."""
    out: dict[str, set[int]] = {}
    diff = git(root, "diff", "-U0", base(root), "--", "l7r")
    for chunk in re.split(r"^diff --git ", diff, flags=re.M)[1:]:
        m = re.search(r"^\+\+\+ b/(\S+\.py)$", chunk, re.M)
        if not m:
            continue
        lines = out.setdefault(m.group(1), set())
        for h in _HUNK.finditer(chunk):
            start, n = int(h.group(1)), int(h.group(2) or 1)
            lines.update(range(start, start + n))
    # `ci/` is not engine code (feature 132 FR-025: a ci-only change is DIRECT) and its tests are tooling tests, which the quick
    # tier never runs - so its lines are the gate's to judge, not the preflight's
    out = {f: ls for f, ls in out.items() if ls and not f.startswith("l7r/diagram/ci/")}
    for f, ls in out.items() if widen else ():  # ...and every line of a function the delta changed (405 T40, D14)
        try:
            text = (root / f).read_text(encoding="utf-8")
        except OSError:
            continue
        for lo, hi in function_spans(text):
            if any(lo <= n <= hi for n in ls):
                ls.update(range(lo, hi + 1))
    return out


def function_spans(text: str) -> list[tuple[int, int]]:
    """(first, last) line of every function and method in `text`; none when it does not parse."""
    try:
        tree = ast.parse(text)
    except (SyntaxError, ValueError):
        return []
    return [(n.lineno, n.end_lineno or n.lineno) for n in ast.walk(tree) if isinstance(n, ast.FunctionDef | ast.AsyncFunctionDef)]


def test_key(context: str) -> str | None:
    """A coverage context as `<dotted module[.Class]>::<test name>` - a junit testcase's `classname::name` - or None for one that
    names no test (a fixture's, the empty one), which may be a roll's and so counts as reaching beyond the quick tier."""
    s = context.split("|", 1)[0]
    if not s or s.startswith("fixture:") or "::" not in s:
        return None
    parts = s.split("::")
    name = parts[-1].split("@", 1)[0]
    return ".".join([parts[0].removesuffix(".py").replace("/", "."), *parts[1:-1]]) + "::" + name


def quick_ids(junit: Path) -> set[str]:
    """The tests a quick run ran, as `classname::name`, from its junit report."""
    import xml.etree.ElementTree as ET  # noqa: PLC0415, N817, S405 - our own pytest's report

    if not junit.is_file():
        return set()
    return {f"{c.get('classname')}::{c.get('name')}" for c in ET.parse(junit).getroot().iter("testcase")}  # noqa: S314


def base_line(base_text: str, text: str, line: int) -> int | None:
    """`line` of `text` as the same line of `base_text`, or None when the delta changed it (difflib's equal blocks)."""
    sm = difflib.SequenceMatcher(None, base_text.split("\n"), text.split("\n"), autojunk=False)
    for a, b, n in sm.get_matching_blocks():
        if b < line <= b + n:
            return a + line - b
    return None


def _by_baseline(root: Path, gaps: dict[str, list[int]], judge: Callable[[int, str, str, list[tuple[str, set[int]]]], bool]) -> dict[str, list[int]]:
    """The lines of `gaps` that `judge(line, base_text, text, hits)` picks, read against the last green gate's baseline
    (`<git dir>/gate-baseline/`: each file's blob in `manifest.json`, what reached each line in `coverage.db`). A file the
    baseline cannot speak for is left out."""
    g = git(root, "rev-parse", "--absolute-git-dir").strip()
    base = Path(g) / "gate-baseline" if g else None
    if base is None or not (base / "coverage.db").is_file() or not (base / "manifest.json").is_file():
        return {}
    blobs = json.loads((base / "manifest.json").read_text(encoding="utf-8")).get("engine", {})
    out: dict[str, list[int]] = {}
    with sqlite3.connect(base / "coverage.db") as db:
        from coverage.numbits import numbits_to_nums  # noqa: PLC0415

        ctx = dict(db.execute("SELECT id, context FROM context"))
        files = dict(db.execute("SELECT path, id FROM file"))
        for f, lines in gaps.items():
            fid = next((i for p, i in files.items() if p.endswith("/" + f)), None)
            base_text = git(root, "cat-file", "-p", blobs[f]) if f in blobs else ""
            if fid is None or not base_text:
                continue
            text = (root / f).read_text(encoding="utf-8")
            hits = [(ctx[c], set(numbits_to_nums(nb))) for c, nb in db.execute("SELECT context_id, numbits FROM line_bits WHERE file_id = ?", (fid,))]
            out.update({f: picked} if (picked := [n for n in lines if judge(n, base_text, text, hits)]) else {})
    return out


def unit_only(root: Path, gaps: dict[str, list[int]], quick: set[str]) -> dict[str, list[int]]:
    """Of `gaps` (lines the quick run left unrun), those that map to a baseline line the last green gate reached by NO test but
    the quick tier's (405 T40, D14). A line the delta changed has no baseline line and is left out (the gate judges it)."""

    def judge(line: int, base_text: str, text: str, hits: list[tuple[str, set[int]]]) -> bool:
        bl = base_line(base_text, text, line)
        return bl is not None and all((k := test_key(c)) is not None and k in quick for c, ns in hits if bl in ns)

    return _by_baseline(root, gaps, judge)


def gate_reached(root: Path, gaps: dict[str, list[int]], quick: set[str]) -> dict[str, list[int]]:
    """Of `gaps`, the lines whose FUNCTION the last green gate reached through a test outside the quick tier - a pool sweep,
    a gate or full test - so the gate runs it again and its floor judges the line (T42's landing: `gencache.gate_obtain`, run
    by the pool sweep, was refused for a changed line no quick test runs)."""

    def judge(line: int, base_text: str, text: str, hits: list[tuple[str, set[int]]]) -> bool:
        span = next(((lo, hi) for lo, hi in sorted(function_spans(text), key=lambda s: s[1] - s[0]) if lo <= line <= hi), None)
        if span is None:
            return False
        mapped = {b for n in range(span[0], span[1] + 1) if (b := base_line(base_text, text, n)) is not None}
        return any((k := test_key(c)) is None or k not in quick for c, ns in hits if ns & mapped)

    return _by_baseline(root, gaps, judge)


def uncovered(cov: dict, changed: dict[str, set[int]]) -> dict[str, list[int]]:
    """Each changed file's changed lines that coverage counted as statements and no quick test ran."""
    out = {}
    files = cov.get("files", {})
    for f, lines in changed.items():
        data = files.get(f) or next((v for k, v in files.items() if k.endswith(f)), None)
        missing = sorted(set((data or {}).get("missing_lines", [])) & lines) if data else []
        if missing:
            out[f] = missing
    return out


def hamlet_path(root: Path) -> set[str]:
    """The engine files hamlet generation imports, directly or through others (`tools/claims.scope`)."""
    sys.path.insert(0, str(root))
    from l7r.diagram.tools import claims  # noqa: PLC0415

    return {str(p.relative_to(root)) for p in claims.scope(root).values()}


def outside_quick(root: Path) -> set[str]:
    """Engine files a test OUTSIDE the quick tier reaches - a `tooling`-marked module under `tests/tools/`, or a town or city
    tier test, whether or not a quick test reaches the file too - found by the mirrored layout (`tests/<tree>/a/test_b.py` tests `l7r/diagram/a/b.py`). A line only
    those reach is the gate's to judge (the plan review of amendment 2: `citybudget.py`'s lines 358 and 432, the audits)."""
    out: set[str] = set()
    tests = list((root / "tests" / "tier_town").rglob("test_*.py")) + list((root / "tests" / "tier_city").rglob("test_*.py"))
    tests += [t for t in (root / "tests" / "tools").glob("test_*.py") if "pytestmark = pytest.mark.tooling" in t.read_text(encoding="utf-8")]
    for t in tests:
        rel = t.relative_to(root / "tests").parts[1:] if t.parts[-2] != "tools" or "tier_" in str(t) else ("tools", t.name)
        stem = Path(*rel[:-1], rel[-1][len("test_"):-len(".py")])
        for cand in (Path("l7r/diagram") / f"{stem}.py", Path("l7r/diagram") / stem / "__init__.py"):
            if (root / cand).is_file():
                out.add(str(cand))
        if (root / "l7r/diagram" / stem).is_dir():
            out.update(str(f.relative_to(root)) for f in (root / "l7r/diagram" / stem).rglob("*.py"))
    return out


def coverage_step(root: Path, changed: dict[str, set[int]], workers: str) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """(off-path uncovered lines, on-path uncovered lines) from one quick-tree run with coverage over the changed files."""
    if not changed:
        return {}, {}
    mods = sorted({f[:-3].replace("/", ".").removesuffix(".__init__") for f in changed})
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "cov.json"
        cmd = [sys.executable, "-m", "pytest", "-q", "-n", workers, "--dist", "worksteal", "-p", "no:cacheprovider",
               "-m", "not rolls_map and not tooling", "--no-cov-on-fail", f"--cov-report=json:{report}", f"--junitxml={Path(tmp) / 'quick.xml'}",
               *[f"--cov={m}" for m in mods], "tests", "--ignore=tests/tier_town", "--ignore=tests/tier_city",
               "--ignore=tests/gate", "--ignore=tests/full", "--ignore=tests/tooling"]
        env = {**os.environ, "COVERAGE_FILE": str(Path(tmp) / ".coverage")}
        subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False, env=env)
        cov = json.loads(report.read_text(encoding="utf-8")) if report.is_file() else {}
        quick = quick_ids(Path(tmp) / "quick.xml")
    gaps = uncovered(cov, changed)
    path = (hamlet_path(root) | outside_quick(root)) if gaps else set()  # where a test the quick tier skips may reach a line
    return split_gaps(root, gaps, path, quick)


def split_gaps(root: Path, gaps: dict[str, list[int]], path: set[str], quick: set[str]) -> tuple[dict[str, list[int]], dict[str, list[int]]]:
    """(the lines that stop the preflight, the lines left to the gate) of `gaps`, the lines the quick run left unrun.

    A CHANGED line keeps the old rule - off the hamlet path it stops the preflight, on it the gate judges - unless its function
    is one the last green gate reached through a test outside the quick tier (`gate_reached`): the gate judges that one too. An UNCHANGED line of
    a changed function is judged by the last green gate's evidence alone, wherever it is (405 T40, D14): reached there by
    quick-tier tests only, no roll reaches it now either and the floor will refuse it; otherwise it is not this step's to name."""
    strict = changed_lines(root, widen=False)
    mine = {f: [n for n in v if n in strict.get(f, set())] for f, v in gaps.items()}
    off = {f: v for f, v in mine.items() if v and f not in path}
    on = {f: v for f, v in mine.items() if v and f in path}
    for f, ls in gate_reached(root, off, quick).items():  # ...off the path, but in a function the gate's own tests run
        off[f] = [n for n in off[f] if n not in ls]
        on[f] = sorted(set(on.get(f, [])) | set(ls))
    off = {f: v for f, v in off.items() if v}
    ask = {f: [n for n in v if f in path or n not in strict.get(f, set())] for f, v in gaps.items()}
    for f, ls in unit_only(root, {f: v for f, v in ask.items() if v}, quick).items():
        off[f] = sorted(set(off.get(f, [])) | set(ls))
        on[f] = [n for n in on.get(f, []) if n not in ls]
    return off, {f: v for f, v in on.items() if v}


def _codeid() -> object:
    """`codeid.py`, by path: the semantic id the gate's own key is built on."""
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("l7r_codeid", Path(__file__).resolve().parent / "codeid.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def stmt_lines(data: bytes) -> list[int] | None:
    """The line every statement of a Python source starts on - what a coverage record is keyed by; None where it does not parse."""
    try:
        tree = ast.parse(data)
    except (SyntaxError, ValueError):
        return None
    return [n.lineno for n in ast.walk(tree) if isinstance(n, ast.stmt)]


def same_program(old: bytes, new: bytes, name: str) -> bool:
    """A `.py` file's two versions the same but for what the gate does not see: its semantic id - the AST with docstrings stripped, the gate's own key - and,
    as coverage records lines, every statement's line (405 batch 7: a docstring one line longer voided a report)."""
    codeid = _codeid()
    return codeid.semantic_bytes(old, name) == codeid.semantic_bytes(new, name) and stmt_lines(old) == stmt_lines(new)  # type: ignore[attr-defined]


def same_lines(text: str) -> str:
    """The answer to `--same-py`'s lines, one 1 or 0 each."""
    out = []
    for line in text.splitlines():
        name, old, new = line.split("\t")
        out.append("1" if same_program(Path(old).read_bytes(), Path(new).read_bytes(), name) else "0")
    return "".join(f"{v}\n" for v in out)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--workers", default=os.environ.get("XDIST_WORKERS", "4"))
    ap.add_argument("--cover", action="store_true")
    ap.add_argument("--same-py", action="store_true")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if a.same_py:
        sys.stdout.write(same_lines(sys.stdin.read()))
        return 0
    if a.cover:
        off, on = coverage_step(root, changed_lines(root), a.workers)
        print(json.dumps({"off": off, "on": on}))
        return 0
    ap.error("--cover or --same-py")
    return 2


if __name__ == "__main__":
    sys.exit(main())
