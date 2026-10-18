#!/usr/bin/env python3
"""What a judged unit's code turns on, carried into its claims bundle as context (feature 385 T25, plan D47).

WHY. Measured on T05 (2026-10-18): the standoff claim on `_seat_households` came back CANNOT-TELL three rounds running, each for
the next layer of what it reads - `front_row` and `turn_the_seat` (imported from sibling modules), then `_front_row_from_chains`
and `install_site_boundary`, then `HOUSE_PADDY_GAP_FT` and `STANDOFF_SLACK_PX` (module constants). `claims.callees` carried
only the unit's own module's functions (feature 385, ask:t03-claims-at-landing). The round arbiter's fix on
ask:t05-old-drifts-at-landing: inline a unit's direct callees and every module-level constant they read, one level on.

WHAT IS FOLLOWED. For a claim whose label names a distance, gap or standoff (`DISTANCE`), the arbiter's words (`direct`): every
engine function the unit calls and every module constant it or they read, one level on, uncapped. For every claim, and beside
that (ours), (measured: two levels of every callee was 81 refs and 82 KB for `_seat_households`, and still three calls short
of `HOUSE_PADDY_GAP_FT`). A FIRST bundle (`callees`): the unit's own module's functions it calls, as before, and every module
constant the unit reads, imported ones included. A RE-BUNDLE of a claim last judged CANNOT-TELL (`chase`): every engine name its
note puts in backticks, resolved through the unit's imports, and breadth first through each function found the functions and
constants it calls or reads, within `CHASE_CHARS` - the round-2 note on the standoff (`front_row`, `turn_the_seat`) reaches
`_front_row_from_chains`, `STANDOFF_SLACK_PX` and `HOUSE_PADDY_GAP_FT` in 7.7 KB, the three rounds that followed in one. A name
from outside `l7r/` - the standard library, a third-party package - is never followed.
"""

from __future__ import annotations

import ast
import re
import textwrap
from pathlib import Path
from typing import Any


def _module_path(root: Path, here: str, mod: str | None, level: int) -> str | None:
    """The engine file `from <level dots><mod> import ...` in `here` names, or None outside `l7r/` or missing."""
    if level:
        base = Path(here).parent
        for _ in range(level - 1):
            base = base.parent
        parts = [*base.parts, *(mod.split(".") if mod else [])]
    elif mod and mod.startswith("l7r."):
        parts = mod.split(".")
    else:
        return None
    for cand in (Path(*parts).with_suffix(".py"), Path(*parts) / "__init__.py"):
        if cand.parts[:1] == ("l7r",) and (root / cand).is_file():
            return cand.as_posix()
    return None


def _defs(root: Path, path: str) -> tuple[set[str], set[str], dict[str, str]]:
    """(functions, ALL_CAPS constants, imported name -> its engine file) at module level of `path`."""
    try:
        tree = ast.parse((root / path).read_text(encoding="utf-8"))
    except (OSError, SyntaxError, ValueError):
        return set(), set(), {}
    funcs = {n.name for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
    consts: set[str] = set()
    imports: dict[str, str] = {}
    for n in tree.body:
        targets = n.targets if isinstance(n, ast.Assign) else [n.target] if isinstance(n, ast.AnnAssign) else []
        consts |= {t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper()}
        if isinstance(n, ast.ImportFrom):
            where = _module_path(root, path, n.module, n.level)
            if where:
                imports |= {(a.asname or a.name): where for a in n.names if a.name != "*"}
    return funcs, consts, imports


def _named(source: str) -> list[tuple[str, bool]]:
    """(name, called) for each call by bare name and each ALL_CAPS name read in `source`, in order of first use."""
    try:
        tree = ast.parse(textwrap.dedent(source))
    except SyntaxError:
        return []
    out: dict[str, bool] = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            out.setdefault(node.func.id, True)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load) and node.id.isupper():
            out.setdefault(node.id, False)
    return list(out.items())


def _refs(root: Path, path: str, source: str, own: str) -> list[str]:
    """`path::name` of each function or constant `source` (in module `path`) uses that the engine defines."""
    funcs, consts, imports = _defs(root, path)
    local: list[str] = []
    imported: list[str] = []
    for name, called in _named(source):
        if name == own:
            continue
        if (called and name in funcs) or (not called and name in consts):
            local.append(f"{path}::{name}")
        elif name in imports:
            f2, c2, _ = _defs(root, imports[name])
            if name in f2 or name in c2:
                imported.append(f"{imports[name]}::{name}")
    return local + imported


def constants(root: Path, unit: Any, source: str) -> list[str]:  # noqa: ANN401
    """The module constants `unit`'s own `source` reads - its module's and those it imports from the engine."""
    own = unit.qualname.split(".")[-1]
    return [r for r in _refs(root, unit.path, source, own) if r.rsplit("::", 1)[1].isupper()]


#: a claim whose label names a distance, gap or standoff (the arbiter's trigger on ask:t05-old-drifts-at-landing)
DISTANCE = re.compile(r"\b(?:distance|gaps?|standoff|apart|reach|clear of|off the|ft|feet)\b", re.I)


def direct(root: Path, unit: Any, source: str, context_source: Any, depth: int = 2) -> list[str]:  # noqa: ANN401
    """D47a: every engine function `unit` calls, its own module's and imported, and theirs, `depth` calls down, with every
    module constant any of them reads - uncapped. Two levels reach the call that reads the standoff's `HOUSE_PADDY_GAP_FT`
    (`_seat_households` -> `front_row` -> `_front_row_from_chains`), so its first bundle judges it (spec-fidelity, T25 round 2)."""
    own = unit.qualname.split(".")[-1]
    out: list[str] = []
    level = [(unit.path, own, source)]
    for _ in range(depth):
        nxt = []
        for path, name, src in level:
            for ref in _refs(root, path, src, name):
                if ref in out or ref.endswith(f"::{own}"):
                    continue
                out.append(ref)
                p2, _, n2 = ref.partition("::")
                if n2.isupper():
                    continue
                try:
                    nxt.append((p2, n2, context_source(root, ref)))
                except (OSError, SyntaxError, ValueError):
                    continue
        level = nxt
    for path, name, src in level:  # the constants the deepest calls read
        out += [r for r in _refs(root, path, src, name) if r.rsplit("::", 1)[1].isupper() and r not in out]
    return out


#: the most characters a CANNOT-TELL's chase adds to a bundle (D47b): the standoff's whole chain is about 9 KB
CHASE_CHARS = 30_000


def defined_in(root: Path, name: str) -> list[str]:
    """`path::name` for each engine module that defines `name` at module level (a function or a constant), at most three."""
    pat = re.compile(rf"^(?:def {re.escape(name)}\b|{re.escape(name)}\s*[:=])", re.M)
    hits = [f"{f.relative_to(root).as_posix()}::{name}" for f in sorted((root / "l7r").rglob("*.py")) if pat.search(f.read_text(encoding="utf-8"))]
    return hits[:3]


def chase(root: Path, path: str, names: list[str], context_source: Any, budget: int = CHASE_CHARS) -> list[str]:  # noqa: ANN401
    """Each engine name in `names` that module `path` defines or imports, and - breadth first, through every function found -
    the engine functions and constants each calls or reads, until `budget` characters (D47b: what a CANNOT-TELL asked for, and
    what that turns on, in one bundle)."""
    funcs, consts, imports = _defs(root, path)
    queue: list[str] = []
    for name in names:
        if name in funcs or name in consts:
            queue.append(f"{path}::{name}")
        elif name in imports:
            queue.append(f"{imports[name]}::{name}")
        else:  # a name the unit's module never sees (the standoff's `HOUSE_PADDY_GAP_FT`, read two calls down): where it is defined
            queue += defined_in(root, name)
    out: list[str] = []
    used = 0
    while queue:
        ref = queue.pop(0)
        if ref in out:
            continue
        try:
            src = context_source(root, ref)
        except (OSError, SyntaxError, ValueError):
            continue
        if used + len(src) > budget:
            break
        out.append(ref)
        used += len(src)
        p2, _, n2 = ref.partition("::")
        if not n2.isupper():
            queue += [r for r in _refs(root, p2, src, n2) if r not in out]
    return out


def callees(root: Path, unit: Any, source: str, limit: int) -> list[str]:  # noqa: ANN401
    """The first bundle's context (D47a): the unit's own module's functions it calls, at most `limit` (as before T25), then the
    module constants it reads - its module's and those it imports. Deeper layers come from `chase`, on what a CANNOT-TELL names."""
    own = unit.qualname.split(".")[-1]
    refs = _refs(root, unit.path, source, own)
    local_funcs = [r for r in refs if r.startswith(f"{unit.path}::") and not r.rsplit("::", 1)[1].isupper()][:limit]
    return local_funcs + [r for r in refs if r.rsplit("::", 1)[1].isupper()]
