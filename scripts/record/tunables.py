"""The numbers that are OURS - every claim whose value no source states - listed for a fixing pass (feature 417 T28, D31).

WHY. The GM, 2026-10-25: "we need to avoid falling into the trap where we set a number arbitrarily and then end up going through
enormous iterations and difficulty to try to make that number work when the number is arbitrary and not an actual hard
requirement ... it's important that in our checklist-based iteration, as we try to fix things, that we have these kinds of
numbers marked." The claim grammar (`l7r/diagram/tools/claims.py`) already marks them: `GUESS` - searched, the record silent, a
value of our own; `UNRESEARCHED` - not yet searched; `CONVENTION` - a map drawing convention, chosen for the reader. A value
under any of the three is a GOAL and a knob (`docs/approach-checklist.md` part A item 3): a fixing pass may move it, and says so
where it does, rather than iterating to keep it.

DERIVED, NEVER KEPT BY HAND (constitution X clause 14): the list is read from the claims themselves each time, so a relabel is
the whole update.

    tunables.py [--path PREFIX] [--all] [--count] [--inline]

`--path` keeps the claims under one file or directory; `--all` keeps claims whose account names no figure too (by default only
those with a number); `--count` prints the counts by label alone. `--inline` lists instead every number written INSIDE a function
of the code that draws a map which its unit's claims never state (D31 (d)): a number no claim states is ours by default, a knob
like the rest - the audit's blind spot, found by walking the code each time rather than labeled by hand. Trivial numbers
(`TRIVIAL`: 0, 1, 2, halves, right angles, tiny epsilons) and subscripts are left out.
"""

from __future__ import annotations

import argparse
import ast
import re
import sys
from collections import Counter
from collections.abc import Iterable, Mapping, Sequence
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))

#: The labels whose value is ours, in the order a reader weighs them: searched and silent first.
OURS = ("GUESS", "UNRESEARCHED", "CONVENTION")
#: A figure in an account: a number, with or without a unit.
FIGURE = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")


def tunables(rows: Mapping[str, Any], path: str = "", figures_only: bool = True) -> list[tuple[str, str, str]]:
    """(label, key, account) for every claim of `rows` (`claims.current`) labeled one of `OURS`, under `path`, sorted by label
    then key; with `figures_only`, only those whose account names a figure."""
    out = []
    for key, row in rows.items():
        claim = row.claim
        if claim is None or claim.backing not in OURS or not key.startswith(path):
            continue
        if figures_only and not FIGURE.search(claim.account):
            continue
        out.append((claim.backing, key, claim.account))
    return sorted(out, key=lambda t: (OURS.index(t[0]), t[1]))


#: The code that draws a map, and the audit that grades a Mode A sheet (D31 (d)); the rest of `tools/`, and `ci/`, `pipeline/` and
#: `interactive/`, choose what is rolled or reported, or time a run - never whether a map passes.
MAP_CODE = (
    "l7r/diagram/tools/pack_audit/",
    "l7r/diagram/labels/",
    "l7r/diagram/compound",
    "l7r/diagram/well_gear.py",
    "rust/phases/src/",  # the hamlet stages, Rust since the Python engine's deletion (feature 444 T40); `rust/parked/` is claimed by nothing
)
#: Numbers too plain to be a decision: identities, halves, right and straight angles, and the epsilons of float tests.
TRIVIAL = frozenset({0, 1, 2, 3, 4, 10, 100, 90, 180, 360, 255, 0.5})


def _stated(value: float, text: str) -> bool:
    s = f"{value:g}"
    return re.search(rf"(?<![\d.]){re.escape(s)}(?![\d])", text) is not None


def _units(tree: ast.Module) -> list[ast.FunctionDef | ast.AsyncFunctionDef]:
    """The functions a claim can sit on: module-level functions and class methods (any depth of class); a function nested in
    another is not a unit - its numbers are its enclosing unit's (feature 417 T38), where its claims are written."""
    out: list[ast.FunctionDef | ast.AsyncFunctionDef] = []

    def visit(node: ast.AST) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                out.append(child)
            elif isinstance(child, ast.ClassDef):
                visit(child)

    visit(tree)
    return out


def unstated(source: str, unit_text: Mapping[str, str]) -> list[tuple[str, int, float]]:
    """(function, line, value) for every non-trivial number literal inside a unit of `source` (a function nested in it
    included) that the claims of that unit (`unit_text[unit name]`, their labels and accounts) never state; a subscript's
    index is not a decision."""
    out = []
    tree = ast.parse(source)
    for fn in _units(tree):
        text = unit_text.get(fn.name, "")
        index_nodes = {id(n) for sub in ast.walk(fn) if isinstance(sub, ast.Subscript) for n in ast.walk(sub.slice)}
        for node in ast.walk(fn):
            if not (isinstance(node, ast.Constant) and type(node.value) in (int, float)) or id(node) in index_nodes:
                continue
            v = node.value
            if v in TRIVIAL or abs(v) < 1e-3 or _stated(v, text):
                continue
            out.append((fn.name, node.lineno, v))
    return out


def render(found: Iterable[tuple[str, str, str]], count: bool = False) -> str:
    """The list (or its counts), with the line that says what it is for."""
    found = list(found)
    tally = Counter(label for label, _k, _a in found)
    head = "tunables: " + ", ".join(f"{lab} {tally[lab]}" for lab in OURS if tally[lab]) if found else "tunables: none"
    lines = [f"{head} - values no source states: a goal and a knob, never a target to defend (docs/approach-checklist.md A3)"]
    if not count:
        lines += [f"  {label:<12} {key} - {account}" for label, key, account in found]
    return "\n".join(lines)
