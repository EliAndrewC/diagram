#!/usr/bin/env python3
"""The gate's first phase - the cheap checks that turned feature 372's gates red, in seconds, before the expensive ones
(feature 375, FR-004, plan D14).

WHY. Measured from 372's wave 106 (2026-10-10): its gate went red about six times, every cause one a cheap check finds - a file
edited mid-gate, `building-programs.md` stale twice, stub pointers in found rows, two untested lines. Each red cost a gate run.
So `make done` begins here and stops here on a failure:

1. THE DERIVED FILES regenerated - `make docs`, `make building-programs`, `make glossary` - and any that moved named, to commit;
2. THE RECORD builds (`make record CHECK=1`) and its pointers resolve (`check-research-pointers.py`);
3. THE QUICK TIER (`make quick FROM_PREFLIGHT=1`: lint, types, spec-lint on the delta, the file-size bar, house style, the unit
   tests - its TIME not judged here: a green but slow quick after a merge of main stopped a gate whose tests all passed);
4. THE CHANGED ENGINE LINES covered - the quick tree run once more with coverage over just the engine files the delta changed,
   and every changed line it leaves unrun named. A line in a module OFF the hamlet path (no rolled map reaches it; the path
   is `tools/claims.scope`, the import graph of hamlet generation) stops the preflight: only a unit test can cover it, and
   the gate's 100% floor would refuse it minutes later. A line ON the path may be reached only by a rolled map, which the
   preflight does not roll, so it is reported and left to the gate (the floor judges it there) - UNLESS the last green gate's
   coverage (`<git dir>/gate-baseline/`) shows that line, as the baseline had it, reached by no test but those the quick tier
   runs: then no roll reaches it either, and the preflight stops on it. The lines judged are every line of a FUNCTION the delta
   changed, not only its changed lines (feature 405 T40, D14: T14 reworked the one unit test that reached an unchanged line,
   `sweeps.py:738`; the preflight passed and the gate's floor failed 5.7 minutes in).

And THE TREE HELD STILL: the gate hashes every tracked file that differs from HEAD (and HEAD itself) when it starts and again
before it reports green, and a difference fails it, naming the file - 372's wave 106 went red once on a file edited mid-gate,
and a green run over a tree that moved under it vouches for nothing.

    preflight.py [--root DIR] [--skip-quick]
    preflight.py --tree-snap FILE | --tree-check FILE
"""

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
import time
from collections.abc import Callable
from pathlib import Path

sys.dont_write_bytecode = True
DERIVED = ("docs", "building-programs", "glossary")
_HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)


def run(cmd: list[str], root: Path, quiet: bool = True) -> int:
    r = subprocess.run(cmd, cwd=root, capture_output=quiet, text=True, check=False)
    if r.returncode and quiet:
        sys.stdout.write((r.stdout or "")[-3000:] + (r.stderr or "")[-3000:])
    return r.returncode


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


#: tracked files the gate itself writes, measured on a gate run (feature 375 T23) - never a moved file of the session's
GATE_WRITES: frozenset[str] = frozenset()


def tree(root: Path) -> dict[str, str]:
    """HEAD and every tracked file that differs from it, by content hash."""
    out = {"HEAD": git(root, "rev-parse", "HEAD").strip()}
    paths = [p for p in git(root, "diff", "--name-only", "HEAD").splitlines() if p and p not in GATE_WRITES]
    if paths:
        # -w: each blob is kept, so a later check can read what the file held and judge the change (405 T41, D15)
        r = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin-paths"], input="\n".join(paths), capture_output=True,
                           text=True, check=False)
        out.update(zip(paths, (r.stdout.split() if r.returncode == 0 else ["?"] * len(paths)), strict=False))
    return out


#: the records the claims round writes, which no phase of the gate reads (405 T41, D15) - beside the active feature's own
RECORDS = frozenset({"dev/claims-index.json", "dev/claims-pages.json", "dev/review-ledger.md"})
FEATURE_RECORDS = ("found.jsonl", "arbiter.jsonl", "claims-carried.jsonl", "tasks.md")
#: the landing cohort's records: a NEW one is a run beside the gate committing its result (405 T48, D21) - no test reads the real
#: directory (each uses a temporary tree); an existing one changed is seen
COHORT_LOG = "dev/cohort-log/"


def _stamp() -> object:
    """`gate-stamp.py`, by path (its name has a hyphen): the semantic id the gate's own key is built on."""
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("gate_stamp", Path(__file__).resolve().parent / "gate-stamp.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def active_records(root: Path) -> set[str]:
    """The claims round's record files of the active feature (`.specify/feature.json`)."""
    try:
        fd = str(json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", "")).rstrip("/")
    except (OSError, ValueError):
        return set()
    return {f"{fd}/{n}" for n in FEATURE_RECORDS} if fd else set()


def unseen(root: Path, path: str, old: bytes | None, new: bytes | None) -> bool:
    """Is a change of `path` from `old` to `new` (None: absent) one the gate does not see (405 T41, D15)? The same bytes; one of
    the claims round's records; or a `.py` file outside the byte-hashed areas (`page`, `browser`) whose semantic id - the AST
    with docstrings stripped, the gate's own key - is unchanged: a claim docstring, a comment."""
    if old == new or path in RECORDS or path in active_records(root):
        return True
    if old is None and path.startswith(COHORT_LOG) and path.endswith(".json"):  # 405 T48 (D21): the landing cohort's new record
        return True
    if not path.endswith(".py") or old is None or new is None:
        return False
    gs = _stamp()
    if any(gs._matches(path, *gs.AREAS[a]) for a in gs.RAW_AREAS if a in gs.AREAS):  # type: ignore[attr-defined]  # noqa: SLF001
        return False
    # ...AND NO STATEMENT MOVED A LINE (405 batch 7): coverage records lines, so a docstring one line longer above code the gate
    # ran voided its report - street.py's `return n` read as missed one line below where it ran (a false red)
    return gs.semantic_bytes(old, path) == gs.semantic_bytes(new, path) and stmt_lines(old) == stmt_lines(new)  # type: ignore[attr-defined]


def stmt_lines(data: bytes) -> list[int] | None:
    """The line every statement of a Python source starts on - what a coverage record is keyed by; None where it does not parse."""
    try:
        tree = ast.parse(data)
    except (SyntaxError, ValueError):
        return None
    return [n.lineno for n in ast.walk(tree) if isinstance(n, ast.stmt)]


def blob(root: Path, spec: str) -> bytes | None:
    """A blob's bytes (`<sha>` or `<commit>:<path>`), or None when there is none."""
    r = subprocess.run(["git", "-C", str(root), "cat-file", "-p", spec], capture_output=True, check=False)
    return r.stdout if r.returncode == 0 else None


def seen_moves(root: Path, before: dict[str, str], after: dict[str, str]) -> list[str]:
    """`tree_moved`, less every change the gate does not see (`unseen`) - across a HEAD move too, which a commit holding only
    such changes makes (405 T41, D15: the claims round's commits while the gate runs). "HEAD" stays when its move cannot be read."""
    moved = tree_moved(before, after)
    if not moved:
        return []
    bh, ah = before.get("HEAD", ""), after.get("HEAD", "")
    paths = {m for m in moved if m != "HEAD"}
    if bh != ah:
        diff = subprocess.run(["git", "-C", str(root), "diff", "--name-only", bh, ah], capture_output=True, text=True, check=False)
        if diff.returncode:
            return sorted(paths | {"HEAD"})
        paths |= {x for x in diff.stdout.splitlines() if x}
    return sorted(p for p in paths if not unseen(root, p, blob(root, before.get(p) or f"{bh}:{p}"), blob(root, after.get(p) or f"{ah}:{p}")))


def tree_moved(before: dict[str, str], after: dict[str, str]) -> list[str]:
    return sorted(k for k in set(before) | set(after) if before.get(k) != after.get(k))


#: what a pool map's roll writes beside its generator (feature 385 T87, plan D108)
_MAP_OUTPUTS = (".json", ".png", ".svg", ".html", ".webp")


def rolled_outputs(root: Path, census: Path) -> set[str]:
    """The map outputs (beside each `.gen.py`) of every pool map the gate's own run rolled, by its roll census (feature 385 T87,
    plan D108; T10's gate rolled Kuwabata and then failed on its own `kuwabata.json` as a tree move)."""
    out: set[str] = set()
    try:
        lines = census.read_text(encoding="utf-8").splitlines()
    except OSError:
        return out
    for line in lines:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        gen = Path(str(r.get("gen") or "")) if r.get("kind") == "roll" and r.get("gen") else None
        if gen is None or not gen.name.endswith(".gen.py"):
            continue
        stem = gen.name[: -len(".gen.py")]
        try:
            rel = gen.resolve().parent.relative_to(root.resolve())
        except ValueError:
            continue
        out |= {f"{rel.as_posix()}/{stem}{ext}" for ext in _MAP_OUTPUTS}
    return out


def stray_probes(root: Path) -> list[str]:
    """Probe test files a diagnosis left in the tree (`tests/**/test_zz_probe*.py`): each runs in the full suite and can turn it
    red on its own, and the round arbiter found four in pytest's failure list on red-gate@2026-10-17T17:21:08Z (feature 385,
    its tooling fix) - so the gate refuses to start while any stands."""
    return sorted(str(p.relative_to(root)) for p in (root / "tests").rglob("test_zz_probe*.py"))


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=".")
    ap.add_argument("--skip-quick", action="store_true", help="the quick tier already ran (a test of the other steps)")
    ap.add_argument("--workers", default=os.environ.get("XDIST_WORKERS", "4"))
    ap.add_argument("--tree-snap", default="")
    ap.add_argument("--tree-check", default="")
    ap.add_argument("--census", default="", help="the roll census the gate wrote (default <root>/.git/roll-census.jsonl)")
    ap.add_argument("--would-write", default="", help="with --tree-check: exit 0 when writing PATH (to --content's bytes) is unseen by the gate")
    ap.add_argument("--content", default="", help="the file holding the bytes --would-write would write")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--no-coverage", action="store_true", help="end after the quick tier: the gate's own floor judges the changed lines (405 T47, D25)")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    if a.would_write and a.tree_check:  # the gate-write guard's question for an Edit or a Write (405 T41, D15)
        try:
            snap = json.loads(Path(a.tree_check).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return 1
        rel = a.would_write
        new = Path(a.content).read_bytes() if a.content else None
        return 0 if unseen(root, rel, blob(root, snap.get(rel) or f"{snap.get('HEAD', '')}:{rel}"), new) else 1
    if a.tree_snap:
        Path(a.tree_snap).write_text(json.dumps(tree(root)), encoding="utf-8")
        return 0
    if a.tree_check:
        try:
            before = json.loads(Path(a.tree_check).read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return 0
        moved = seen_moves(root, before, tree(root))
        rerolled = sorted(set(moved) & rolled_outputs(root, Path(a.census) if a.census else root / ".git" / "roll-census.jsonl"))
        moved = [m for m in moved if m not in rerolled]
        if rerolled:
            print("preflight: re-rolled by the gate - commit them (feature 385 T87):\n  " + "\n  ".join(rerolled))
        if moved and a.quiet:
            return 1
        if moved:
            print("GATE NOT GREEN: the tree moved while the gate ran - it vouches for none of it (feature 375 FR-004):\n  "
                  + "\n  ".join("HEAD (a commit or a checkout)" if m == "HEAD" else m for m in moved))
            return 1
        return 0
    if probes := stray_probes(root):
        print("preflight: probe test files are left in the tree - delete them; the gate stops here (feature 385):\n  " + "\n  ".join(probes))
        return 1
    t0 = time.monotonic()
    marks: list[tuple[str, float]] = []

    def mark(step: str) -> None:
        marks.append((step, time.monotonic()))

    before = git(root, "status", "--porcelain")
    for target in DERIVED:
        if run(["make", "--no-print-directory", target], root):
            print(f"preflight: `make {target}` failed - the gate stops here (feature 375 FR-004)")
            return 1
    mark("derived")
    moved = sorted(set(git(root, "status", "--porcelain").splitlines()) - set(before.splitlines()))
    moved = [m for m in moved if m[3:].strip()]
    if moved:
        print("preflight: regenerated, commit them with the change:\n  " + "\n  ".join(m[3:] for m in moved))
    for cmd, what in ((["make", "--no-print-directory", "record", "CHECK=1"], "the record does not build"),
                      ([sys.executable, "scripts/gates/check-research-pointers.py", str(root)], "a research pointer does not resolve")):
        if run(cmd, root):
            print(f"preflight: {what} - the gate stops here (feature 375 FR-004)")
            return 1
    mark("record and pointers")
    if not a.skip_quick and run(["make", "--no-print-directory", "quick", "FROM_PREFLIGHT=1"], root, quiet=False):
        print("preflight: `make quick` failed - the gate stops here (feature 375 FR-004)")
        return 1
    mark("quick")
    # THE COVERAGE STEP IS make preflight's, NOT THE GATE'S (405 T47, D25): 98-107 s of every gate, and in the whole transcript
    # record it refused about twice, once wrongly - the gate's own 100% floor judges the same lines a few minutes later
    off, on = ({}, {}) if a.no_coverage else coverage_step(root, changed_lines(root), a.workers)
    if not a.no_coverage:
        mark("coverage of the changed lines")
    prev = t0
    steps = []
    for step, t in marks:
        steps.append(f"{step} {t - prev:.0f} s")
        prev = t
    print("preflight: " + ", ".join(steps))
    for f, ls in sorted(on.items()):
        print(f"preflight: {f} lines {ls[:12]} - no quick test runs them; a rolled map or a test the quick tier skips may (the gate's floor judges)")
    if off:
        for f, ls in sorted(off.items()):
            print(f"preflight: {f} lines {ls[:12]} - in a changed function, run by no quick test, and reached by no roll (off the hamlet path, or only unit tests reached it at the last green gate): only a unit test covers them")
        print("preflight: the gate stops here - the 100% floor would refuse these minutes from now (feature 375 FR-004)")
        return 1
    print(f"preflight: clean in {time.monotonic() - t0:.0f} s")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    raise SystemExit(usage_log.exited("preflight", main()))
