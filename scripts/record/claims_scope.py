"""Which open claims findings a Rust stage's landing answers for (feature 444 FR-021 as amended 2026-11-01, the round arbiter on
ask:444-T16-fr021-scope-2 and spec-fidelity's exception check after it).

The GM, 2026-10-31 (amendment 6): "we should require that every Rust stage end its initial implementation with zero open claims".
The stage's claims are those of its OWN code, and of what it runs on:

- its Rust under `rust/` that the delta changes - every finding in such a file;
- the Python under `l7r/` the delta adds or changes - a finding counts where the delta adds or changes a line of its UNIT (a
  function, a method, a module's constant with its docstring); lines the delta deletes take their claims with them;
- any Python unit the stage's seam reads at run time (a constant, a knob or a helper it imports - not an import made only for type
  checking), whether or not the delta changes a line of it: these are the claims that govern the stage (`request.md` section 3
  step 1). The Rust reads the Python only through what the seam passes it, so the seam's imports are its reads too.

Every other open finding in a file the delta changes - a unit of a file it touches only to delete dead code, an unchanged unit of
a file it edits - belongs to the open-claims feature (the GM 2026-10-27: the claims still open in the Python code base are that
feature's) and is FILED as its row in the same landing (`file_left`), never refused.

WHY NOT EVERY FINDING IN A CHANGED FILE (the rule before the amendment): it held the field's landing to 26 old findings on code the
Rust never reads - a farmhouse plan knob, a roof knob, the dike band's widths - in shared files the port touched only to delete
what it left dead, which pushed that deletion into a separate landing against FR-005 (old code deleted in the phase's own landing).
"""

from __future__ import annotations

import ast
import json
import re
import subprocess
import sys
import time
from pathlib import Path

FINDING = re.compile(r"^\s+([A-Z][A-Z-]+)\s+(\S[^:]*?)::(\S+?)#")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", re.M)
#: the open-claims feature (the GM, 2026-10-26: the feature that fixes claims findings; `claims_carry.CLAIMS_FEATURE`)
CLAIMS_FEATURE_DIR = "specs/405-engine-findings-from-385"


def changed_lines(diff: str) -> list[tuple[int, int]]:
    """The new-side line ranges a `git diff -U0` changes; a pure deletion is the line it sits after, so the unit it cut into
    still counts as changed."""
    out = []
    for m in HUNK.finditer(diff):
        a, n = int(m.group(1)), int(m.group(2) or 1)
        out.append((a, a + n - 1) if n else (a, a))
    return out


def units(text: str) -> dict[str, tuple[int, int]]:
    """Each unit of a module and its lines: a top-level function or class (decorators included), a method as `Class.name`, and a
    module-level constant with the docstring under it."""
    body = ast.parse(text).body
    out: dict[str, tuple[int, int]] = {}
    for i, n in enumerate(body):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            start = n.decorator_list[0].lineno if n.decorator_list else n.lineno
            out[n.name] = (start, n.end_lineno or n.lineno)
            if isinstance(n, ast.ClassDef):
                for m in n.body:
                    if isinstance(m, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        s = m.decorator_list[0].lineno if m.decorator_list else m.lineno
                        out[f"{n.name}.{m.name}"] = (s, m.end_lineno or m.lineno)
        elif isinstance(n, (ast.Assign, ast.AnnAssign)):
            nxt = body[i + 1] if i + 1 < len(body) else None
            doc = isinstance(nxt, ast.Expr) and isinstance(nxt.value, ast.Constant) and isinstance(nxt.value.value, str)
            end = (nxt.end_lineno if doc and nxt else n.end_lineno) or n.lineno
            for t in n.targets if isinstance(n, ast.Assign) else [n.target]:
                if isinstance(t, ast.Name):
                    out[t.id] = (n.lineno, end)
    return out


def _module_file(root: Path, dotted: str) -> Path | None:
    p = root / Path(*dotted.split("."))
    return p.with_suffix(".py") if p.with_suffix(".py").is_file() else p / "__init__.py" if (p / "__init__.py").is_file() else None


def _definer(root: Path, mod: str, name: str, seen: frozenset[str] = frozenset()) -> Path | None:
    """The file whose unit `name` is, imported from `mod`: the module itself, or the module it re-exports the name from."""
    f = _module_file(root, mod)
    if f is None or mod in seen:
        return None
    tree = ast.parse(f.read_text(encoding="utf-8"))
    if name in units(f.read_text(encoding="utf-8")):
        return f
    for imp, n, _a in _top_imports(root, f, tree):
        if _a == name and (q := _definer(root, imp, n, seen | {mod})):
            return q
    return None


def _top_imports(root: Path, path: Path, tree: ast.Module) -> list[tuple[str, str, str]]:
    """The module's run-time `from M import n as a` of `l7r` names, as (M, n, a): its top level only, so an import under `if
    TYPE_CHECKING:` (read by no running code) is not one."""
    pkg = path.relative_to(root).parts[:-1]
    out = []
    for n in tree.body:
        if isinstance(n, ast.ImportFrom):
            base = ".".join(pkg[: len(pkg) - n.level + 1]) if n.level else ""
            mod = ".".join(x for x in (base, n.module or "") if x)
            if mod.startswith("l7r."):
                out += [(mod, a.name, a.asname or a.name) for a in n.names]
    return out


def read_units(root: Path, seam: list[Path]) -> set[str]:
    """`path::unit` of every Python unit the stage's seam imports at run time."""
    out = set()
    for p in seam:
        for mod, name, _a in _top_imports(root, p, ast.parse(p.read_text(encoding="utf-8"))):
            if (f := _definer(root, mod, name)) is not None:
                out.add(f"{f.relative_to(root).as_posix()}::{name}")
    return out


def split(root: Path, report: str, changed: list[str], seam: list[Path], diff_of) -> tuple[list[str], list[str]]:  # noqa: ANN001 - diff_of: path -> its `git diff -U0`
    """The open findings the landing answers for, and the rest in the files it changes, each a report line."""
    reads = read_units(root, seam)
    ranges: dict[str, list[tuple[int, int]]] = {}
    spans: dict[str, dict[str, tuple[int, int]]] = {}
    own, left = [], []
    for ln in report.splitlines():
        if not (m := FINDING.match(ln)):
            continue
        path, qual = m.group(2), m.group(3)
        head = qual.split(".")[0]
        if f"{path}::{head}" in reads or f"{path}::{qual}" in reads:
            own.append(ln.strip())
            continue
        if path not in changed:
            continue
        if path.startswith("rust/"):
            own.append(ln.strip())
            continue
        if path not in spans:
            f = root / path
            spans[path] = units(f.read_text(encoding="utf-8")) if f.is_file() else {}
            ranges[path] = changed_lines(diff_of(path))
        span = spans[path].get(qual) or spans[path].get(head)
        hit = span is not None and any(a <= span[1] and b >= span[0] for a, b in ranges[path])
        (own if hit else left).append(ln.strip())
    return own, left


def file_left(root: Path, task: str, left: list[str]) -> int:
    """Each finding the landing does not answer for, filed as an open row of the open-claims feature's `found.jsonl`, once."""
    path = root / CLAIMS_FEATURE_DIR / "found.jsonl"
    have = {json.loads(x).get("finding") for x in path.read_text(encoding="utf-8").splitlines() if x.strip()} if path.is_file() else set()
    new = [ln for ln in left if ln not in have]
    if new:
        when = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        with path.open("a", encoding="utf-8") as fh:
            for ln in new:
                m = FINDING.match("  " + ln)
                row = {"check": "impl-drift", "file": m.group(2) if m else "?", "block": m.group(3) if m else "?", "finding": ln, "status": "open", "utc": when, "from": f"feature 444 {task}'s landing (FR-021: not the stage's own code)"}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(new)


def git_diff(root: Path, path: str) -> str:
    return subprocess.run(["git", "-C", str(root), "diff", "-U0", "origin/main...HEAD", "--", path], capture_output=True, text=True).stdout


if __name__ == "__main__":  # pragma: no cover - the landing calls `split`; this prints it for a session
    sys.exit(0)
