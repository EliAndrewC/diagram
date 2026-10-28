"""`scripts/record/claims_counters.py` - the claims triage's counter-only clear (feature 446, FR-003, plan D3).

A claim whose unit only GAINED counter blocks (`codeid.is_counter_block`: `if __debug__: OPS["..."] += <value>`, dropped
under `python -O`) since the version its check read is recorded cleared, with its new fingerprints, and bundled nowhere: the
work counters of feature 443 changed no code a roll runs, yet each one re-owed every claim of its unit a triage dispatch (455
claims triaged in 443's landings, two sent on, neither counter-only; measured 2026-10-28 from their `make claims-triaged` lines).

Cleared only when the recorded version is the MERGE BASE's (its unit there, read through the claims tool's own dump and the
current constant reads, fingerprints to the row's `code`) and the current unit is that version with counter blocks only added -
every counter block of the base standing unchanged, in its place. A counter that reads an in-scope constant, a counter removed,
moved or rewritten, a procedure section or a module unit: owed as before."""

from __future__ import annotations

import ast
import dataclasses
import datetime
import importlib.util
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent

#: what a claim cleared by this file records (FR-003)
CLEARED = "counter-only (feature 446)"
KINDS = ("function", "method", "class", "constant")


def _codeid() -> Any:  # noqa: ANN401 - `scripts/gates/codeid.py` by path (stdlib only), as `land.py` loads it
    cached = sys.modules.get("l7r_codeid")
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location("l7r_codeid", HERE.parent / "gates" / "codeid.py")
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["l7r_codeid"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def merge_base(root: Path) -> str | None:
    """The merge base of HEAD with origin/main, or None (no origin/main: nothing is cleared)."""
    p = subprocess.run(["git", "-C", str(root), "merge-base", "HEAD", "origin/main"], capture_output=True, text=True, check=False)
    return p.stdout.strip() or None if p.returncode == 0 else None


def _show(root: Path, ref: str, path: str) -> str | None:
    p = subprocess.run(["git", "-C", str(root), "show", f"{ref}:{path}"], capture_output=True, text=True, check=False)
    return p.stdout if p.returncode == 0 else None


def find(tree: ast.Module, qualname: str) -> ast.AST | None:
    """The function, method, class or module constant `qualname` names in `tree`, as the claims tool keys its units."""
    *outer, name = qualname.split(".")
    body: list[ast.stmt] = tree.body
    for part in outer:
        cls = next((s for s in body if isinstance(s, ast.ClassDef) and s.name == part), None)
        if cls is None:
            return None
        body = cls.body
    for s in body:
        if isinstance(s, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and s.name == name:
            return s
        if not outer and isinstance(s, ast.Assign) and [getattr(t, "id", None) for t in s.targets] == [name]:
            return s
        if not outer and isinstance(s, ast.AnnAssign) and getattr(s.target, "id", None) == name and s.value is not None:
            return s
    return None


def _blocks(node: ast.AST) -> list[ast.stmt]:
    cid = _codeid()
    return [s for sub in ast.walk(node) for f in ("body", "orelse", "finalbody") for s in getattr(sub, f, None) or [] if isinstance(s, ast.stmt) and cid.is_counter_block(s)]


def _drop_added(node: ast.AST, kept: Counter[str]) -> None:
    """Remove, in place, every counter block of `node` the base's `kept` blocks do not account for - so a base counter moved or
    rewritten leaves a difference and is owed."""
    cid = _codeid()
    for sub in ast.walk(node):
        for f in ("body", "orelse", "finalbody"):
            stmts = getattr(sub, f, None)
            if not isinstance(stmts, list):
                continue
            out = []
            for s in stmts:
                if isinstance(s, ast.stmt) and cid.is_counter_block(s):
                    d = ast.dump(s)
                    if kept[d] <= 0:
                        continue
                    kept[d] -= 1
                out.append(s)
            stmts[:] = out


def counter_only(cl: Any, root: Path, base: str, was: dict[str, Any], row: Any) -> bool:  # noqa: ANN401 - the claims tool, a Row
    """Is `row`'s unit the merge base's version, recorded by `was`, with counter blocks only added (FR-003)?"""
    unit = row.unit
    if unit.kind not in KINDS or unit.line_keyed or row.claim is None:
        return False
    src = _show(root, base, unit.path)
    if src is None:
        return False
    try:
        btree, ctree = ast.parse(src), ast.parse((root / unit.path).read_text(encoding="utf-8"))
    except SyntaxError, OSError:
        return False
    cl._strip_docstrings(btree)  # noqa: SLF001 - the claims tool's own stripping, so the base dump is the one it fingerprints
    cl._strip_docstrings(ctree)  # noqa: SLF001
    bnode, cnode = find(btree, unit.qualname), find(ctree, unit.qualname)
    if bnode is None or cnode is None:
        return False
    added = _blocks(cnode)
    read = {n.id for b in added for n in ast.walk(b) if isinstance(n, ast.Name)} | {n.attr for b in added for n in ast.walk(b) if isinstance(n, ast.Attribute)}
    if any(v.split("=", 1)[0] in read for v in unit.names):  # a counter reading an in-scope constant moves the core's reads
        return False
    vals = "\x1e".join(unit.names)
    if dataclasses.replace(unit, core=cl._sha(cl.nameless_dump(bnode) + "\x1d" + vals)).code(row.claim) != was.get("code"):  # noqa: SLF001
        return False  # the recorded version is not the base's (or a constant it reads changed)
    _drop_added(cnode, Counter(ast.dump(b) for b in _blocks(bnode)))
    return cl.nameless_dump(cnode) == cl.nameless_dump(bnode)


def clear(claims: Any, root: Path, cur: dict[str, Any], index: dict[str, dict[str, Any]], cmd: str) -> dict[str, dict[str, Any]]:  # noqa: ANN401 - `scripts/record/claims.py`
    """At `claims-owed` and `claims-triage`: the index with every claim owed a code triage only because counter blocks were
    added recorded cleared (`counter_only`), saved, and the count said; any other command, the index as it is."""
    if cmd not in ("owed", "triage"):
        return index
    keys = [k for k, why in claims.owed(cur, index, root / claims.QUESTIONS) if why == claims.CODE_TRIAGE]
    base = merge_base(root) if keys else None
    if base is None:
        return index
    cl = claims.engine(Path(claims.__file__).resolve().parents[2])
    today = datetime.date.today().isoformat()
    out = dict(index)
    done = [k for k in keys if k in index and counter_only(cl, root, base, index[k], cur[k])]
    for k in done:
        out[k] = {**out[k], "code": cur[k].code, "core": cur[k].unit.core, "body": claims.body_of(root, cur[k].unit), "triaged": today, "cleared": CLEARED}
        out[k].pop("triage", None)
    if done:
        claims.save_index(root / claims.INDEX, claims.live_rows(cur, out))
        print(f"claims-{cmd}: {len(done)} claim(s) cleared without a triage - their units only gained counter blocks (feature 446, FR-003)")
    return out
