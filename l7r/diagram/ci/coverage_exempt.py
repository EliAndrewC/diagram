"""The engine code the Rust port replaces, exempt from the coverage floor (feature 448; the GM, 2026-11-02).

WHY. The GM: "We can relax that for the engine code at this pooint since that's going away, so long as we maintain it for our
other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc)." Feature 444 rebuilds
the hamlet stages in Rust one phase at a time and deletes each stage's Python at its landing; until then, keeping that Python at
100% cost session time on code with a known end.

THE RECORD is `dev/coverage-exempt.json`: each entry a file's `path`, the `stages` whose old code it is and its `why`. A file not
in it owes 100%, so a new module is held to the floor the day it lands. Every coverage floor reads the record through this module:
the gate's `coverage report --fail-under=100` (`omit`), the derived hamlet floor (`tools/hamlet_floor.py`) and `make
cover-changed` (`scripts/gates/cover_changed.py`, which `make land` runs). The exempt files are still measured; their unrun lines
print as information (`report`).

WHAT IS SLATED (plan D1): the Python of each stage's own files (`work_budget_bundle.stage_files` - the module defining
`stage_<name>` and its subpackage's siblings) for every stage not yet `accepted` in `dev/work-budget.json`. Not the files where a
stage's work is only counted today: tools, ci, pipeline, interactive, labels, overlap and settlement keep the floor.

A STALE ENTRY - its path gone, or every stage it names accepted (the Rust landed; what is left is the stage's thin door) - is no
longer exempt, and `report` refuses until `make coverage-exempt PRUNE=1` drops it, so the record shrinks as the port proceeds.

    python3 -m l7r.diagram.ci.coverage_exempt omit      the floored report's `--omit=...`, nothing when nothing is exempt
    python3 -m l7r.diagram.ci.coverage_exempt report    the exempt files' unrun lines, as information; exit 1 on a stale entry
    python3 -m l7r.diagram.ci.coverage_exempt list      the record; `--prune` drops its stale entries

The record was written once at feature 448's landing by `seeded`; it is edited by hand after (a phase's task adds what its
contract slates).
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import json
import re
import sys
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import IO, Any

ROOT = Path(__file__).resolve().parents[3]
RECORD = Path("dev") / "coverage-exempt.json"
BUDGETS = Path("dev") / "work-budget.json"
CURE = "make coverage-exempt PRUNE=1"
RULING = (
    "the GM, 2026-11-02: \"We can relax that for the engine code at this pooint since that's going away, so long as we maintain it "
    'for our other Python code not currently slated to be removed (tools, automated checks for hand-drawn maps, etc)."'
)


def load(root: Path = ROOT) -> dict[str, Any]:
    """The record; an empty one when the file is absent (then nothing is exempt)."""
    path = root / RECORD
    if not path.is_file():
        return {"ruling": RULING, "entries": []}
    return dict(json.loads(path.read_text(encoding="utf-8")))


def accepted(root: Path = ROOT) -> set[str]:
    """The stages whose Rust has landed: `accepted` in the work-budget record."""
    path = root / BUDGETS
    if not path.is_file():
        return set()
    stages = json.loads(path.read_text(encoding="utf-8")).get("stages") or {}
    return {name for name, row in stages.items() if (row or {}).get("status") == "accepted"}


def stale_why(root: Path, entry: dict[str, Any], done: set[str], reached: set[str] = frozenset()) -> str:  # type: ignore[assignment]
    """Why an entry is stale, or '' for a live one."""
    if not (root / entry["path"]).is_file():
        return "the file is gone"
    if entry["stages"] and set(entry["stages"]) <= done:
        return f"every stage it serves is accepted in Rust ({', '.join(entry['stages'])}); the thin door keeps the floor"
    if not entry["stages"] and entry["path"] in reached:
        return "code that stays Python now imports it, so it is no longer going away"
    return ""


def split(root: Path = ROOT, reach: bool = False) -> tuple[list[dict[str, Any]], list[tuple[dict[str, Any], str]]]:
    """The live entries, and the stale ones with why; `reach` also asks whether a whole-engine entry is reached (about 2 s)."""
    done = accepted(root)
    entries = load(root)["entries"]
    reached = reached_from_kept(root, {e["path"] for e in entries}) if reach and any(not e["stages"] for e in entries) else set()
    live: list[dict[str, Any]] = []
    stale: list[tuple[dict[str, Any], str]] = []
    for entry in entries:
        why = stale_why(root, entry, done, reached)
        if why:
            stale.append((entry, why))
        else:
            live.append(entry)
    return live, stale


#: the trees that stay Python whatever the port does (feature 448 FR-003): every module in them is a root of the reachability measure
KEPT_TREES = ("l7r/diagram/tools/", "l7r/diagram/ci/", "l7r/diagram/pipeline/", "l7r/diagram/interactive/", "l7r/diagram/labels/", "l7r/diagram/overlap/")


def _module_names(root: Path) -> dict[str, str]:
    """Dotted name -> repository-relative path, for every module under `l7r/` (a package by its `__init__.py`)."""
    out = {}
    for p in sorted((root / "l7r").rglob("*.py")):
        rel = p.relative_to(root).as_posix()
        out[rel[:-3].replace("/", ".").removesuffix(".__init__")] = rel
    return out


def _top_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for n in tree.body:
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(n.name)
        elif isinstance(n, ast.Assign):
            names |= {t.id for t in n.targets if isinstance(t, ast.Name)}
        elif isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name):
            names.add(n.target.id)
    return names


def import_graph(root: Path) -> tuple[dict[str, set[str]], set[str]]:
    """Each file's imports of engine modules (a name a package re-exports resolved to the module defining it), and the roots:
    every module of the kept trees, every module run as a program, and every file under `pool/` and `scripts/` that imports one."""
    mods = _module_names(root)
    trees: dict[str, ast.Module] = {}
    for rel in mods.values():
        with contextlib.suppress(SyntaxError):
            trees[rel] = ast.parse((root / rel).read_text(encoding="utf-8"))
    defs = {name: _top_names(trees[rel]) for name, rel in mods.items() if rel in trees}

    def definer(pkg: str, name: str) -> str:
        if not mods[pkg].endswith("__init__.py") or name in defs.get(pkg, ()):
            return pkg
        return next((definer(m, name) for m in mods if m.startswith(pkg + ".") and name in defs.get(m, ())), pkg)

    def targets(cur: str, node: ast.Import | ast.ImportFrom) -> list[str]:
        if isinstance(node, ast.Import):
            return [a.name for a in node.names if a.name in mods]
        base = node.module or ""
        if node.level:
            parts = cur.split(".") if mods.get(cur, "").endswith("__init__.py") else cur.split(".")[:-1]
            parts = parts[: len(parts) - (node.level - 1)]
            base = ".".join([*parts, base] if base else parts)
        return [f"{base}.{a.name}" if f"{base}.{a.name}" in mods else definer(base, a.name) for a in node.names if f"{base}.{a.name}" in mods or base in mods]

    imports: dict[str, set[str]] = {}

    def scan(rel: str, tree: ast.Module, cur: str) -> None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                imports.setdefault(rel, set()).update(mods[t] for t in targets(cur, node))

    for name, rel in mods.items():
        if rel in trees:
            scan(rel, trees[rel], name)
    roots = {rel for rel in mods.values() if rel.startswith(KEPT_TREES) or re.search(r"^if __name__ == .__main__.:", (root / rel).read_text(encoding="utf-8"), re.M)}
    for p in [*sorted((root / "pool").rglob("*.py")), *sorted((root / "scripts").rglob("*.py"))]:
        rel = p.relative_to(root).as_posix()
        with contextlib.suppress(SyntaxError, UnicodeDecodeError):
            scan(rel, ast.parse(p.read_text(encoding="utf-8")), "")
        if imports.get(rel):
            roots.add(rel)
    return imports, roots


def reached_from_kept(root: Path, slated: set[str]) -> set[str]:
    """The files reached by imports from the roots without passing through `slated` - importing a module runs its packages'
    `__init__.py` too - plus every slated file such a file imports directly."""
    imports, roots = import_graph(root)
    seen: set[str] = set()
    stack = sorted(r for r in roots if r not in slated)
    touched: set[str] = set()
    while stack:
        cur = stack.pop()
        if cur in seen:
            continue
        seen.add(cur)
        parts = cur.split("/")[:-1]
        inits = [f"{'/'.join(parts[:k])}/__init__.py" for k in range(2, len(parts) + 1)]
        for nxt in [*imports.get(cur, ()), *(i for i in inits if (root / i).is_file())]:
            if nxt in slated:
                touched.add(nxt)
            elif nxt not in seen:
                stack.append(nxt)
    return seen | touched


def exempt(root: Path = ROOT) -> set[str]:
    """The repository-relative paths exempt from the floor now: the live entries."""
    return {e["path"] for e in split(root)[0]}


def omit_arg(root: Path = ROOT) -> str:
    """`--omit=<p1>,<p2>,...` for `coverage report`, or '' when nothing is exempt."""
    paths = sorted(exempt(root))
    return f"--omit={','.join(paths)}" if paths else ""


def report(root: Path, missing_of: Callable[[str], Iterable[int]], out: IO[str] = sys.stdout) -> int:
    """Each exempt file's unrun lines as information, then every stale entry with its cure: 1 when there is one."""
    live, stale = split(root, reach=True)
    shown = 0
    for entry in live:
        lines = sorted(missing_of(entry["path"]))
        if lines:
            shown += 1
            print(f"coverage (information, feature 448 - slated for the Rust port): {entry['path']} - unrun lines: {_ranges(lines)}", file=out)
    if live:
        print(f"coverage: {len(live)} files slated for the Rust port are exempt from the floor ({shown} with unrun lines; dev/coverage-exempt.json)", file=out)
    for entry, why in stale:
        print(f"COVERAGE: dev/coverage-exempt.json names {entry['path']}, which is stale - {why}. Drop it: {CURE}", file=out)
    return 1 if stale else 0


def _ranges(lines: list[int]) -> str:
    """3, 4, 5, 9 -> '3-5, 9'."""
    runs: list[list[int]] = []
    for n in lines:
        if runs and n == runs[-1][1] + 1:
            runs[-1][1] = n
        else:
            runs.append([n, n])
    return ", ".join(f"{a}-{b}" if a != b else f"{a}" for a, b in runs)


def prune(root: Path = ROOT, out: IO[str] = sys.stdout) -> int:
    """Drop the stale entries and write the record; the count dropped."""
    record = load(root)
    live, stale = split(root, reach=True)
    for entry, why in stale:
        print(f"coverage-exempt: dropped {entry['path']} - {why}", file=out)
    record["entries"] = live
    write(root, record)
    return len(stale)


def write(root: Path, record: dict[str, Any]) -> None:
    (root / RECORD).write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")


def seeded(root: Path, stages: list[str], stage_files: Callable[[Path, str], list[Path]], dead: Iterable[str] = ()) -> dict[str, Any]:
    """The record the plan's rule gives (feature 448 D1): (a) each stage not accepted, its own Python files, each with every stage it
    serves; (b) `dead`, the modules the port leaves unreached (`specs/448-engine-coverage-relax/closure.py`), naming no stage."""
    done = accepted(root)
    served: dict[str, list[str]] = {}
    for stage in stages:
        if stage in done:
            continue
        for path in stage_files(root, stage):
            if path.suffix == ".py":
                served.setdefault(path.resolve().relative_to(root.resolve()).as_posix(), []).append(stage)
    entries = [{"path": p, "stages": s, "why": f"the old Python of {', '.join(s)} (feature 444's phase{'s' if len(s) > 1 else ''}), deleted at its Rust landing"} for p, s in sorted(served.items())]
    entries += [{"path": p, "stages": [], "why": "the whole-engine replacement: only slated code imports it, so the port leaves it dead"} for p in sorted(set(dead) - set(served))]
    rule = "feature 448 plan D1: (a) each unaccepted stage's own files (work_budget_bundle.stage_files); (b) the modules the port leaves unreached"
    return {"ruling": RULING, "rule": rule, "entries": sorted(entries, key=lambda e: e["path"])}


def _missing_from(data_file: str) -> Callable[[str], Iterable[int]]:
    import coverage

    cov = coverage.Coverage(data_file=data_file)
    cov.load()
    measured = set(cov.get_data().measured_files())

    def missing_of(path: str) -> Iterable[int]:
        full = str(ROOT / path)
        return cov.analysis2(full)[3] if full in measured else []

    return missing_of


def main(argv: list[str] | None = None, out: IO[str] = sys.stdout) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("command", choices=("omit", "report", "list"))
    ap.add_argument("--data", default=".coverage", help="the coverage data the report reads (default .coverage)")
    ap.add_argument("--prune", action="store_true", help="list: drop the stale entries")
    args = ap.parse_args(argv)
    if args.command == "omit":
        print(omit_arg(ROOT), file=out)
        return 0
    if args.command == "report":
        return report(ROOT, _missing_from(str(ROOT / args.data)), out)
    if args.prune:
        prune(ROOT, out)
    live, stale = split(ROOT, reach=True)
    for entry in live:
        print(f"{entry['path']}  ({', '.join(entry['stages'])})", file=out)
    for entry, why in stale:
        print(f"STALE {entry['path']} - {why}", file=out)
    print(f"coverage-exempt: {len(live)} exempt, {len(stale)} stale", file=out)
    return 0


if __name__ == "__main__":
    from l7r.diagram._invocation import guard

    guard("l7r.diagram.ci.coverage_exempt")
    sys.exit(main())
