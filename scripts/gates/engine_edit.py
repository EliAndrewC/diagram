#!/usr/bin/env python3
# TOOL_RECORD: asked only by the engine-freeze guard, which records each refusal in the guard log (feature 449 T018)
"""Is this edit an ENGINE edit, and more than a docstring? The two questions the engine-freeze guard asks Python (feature 449 T018).

The guard is `rust/guard/src/guards/engine_freeze_hooks.rs`, and it asks this only once a map review or a roll is live, so an
ordinary edit starts no Python. The answers belong to what this reads: `l7r/diagram/ci/delta.py` `is_engine`, the one list of engine
paths, and `gate-stamp.py` `semantic_bytes`, the AST identity a review is recorded against (feature 426).

Usage: engine_edit.py < {"root", "path", "tool", "tool_input"}  ->  exits 0 for an engine edit that must wait, 1 otherwise.
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _is_engine(root: str, rel: str) -> bool:
    path = os.path.join(root, "l7r", "diagram", "ci", "delta.py")
    if not os.path.isfile(path):
        return False  # not a diagram tree
    spec = importlib.util.spec_from_file_location("_l7r_delta", path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod  # a dataclass resolves its module by name
    spec.loader.exec_module(mod)
    return bool(mod.is_engine(rel))


def docstring_only(rel: str, path: str, ti: dict, tool: str) -> bool:
    """Does the edit change only docstrings and comments of a `.py` file - its semantic id, the AST with docstrings stripped
    (`gate-stamp.py` `semantic_bytes`, what the engine key a review is recorded against hashes since feature 426), the same?
    Then no review's verdict can move, and the edit passes (the GM, 2026-10-27: "We should change the rule to allow docstring
    edits during a run, since those don't affect things"). Never in the byte-hashed areas (`RAW_AREAS`: the interactive page's
    class docstrings ARE the modal text a review reads), and never for a NotebookEdit or a file that cannot be read."""
    if not rel.endswith(".py") or tool not in ("Edit", "Write"):
        return False
    try:
        with open(path, "rb") as f:
            old = f.read()
    except OSError:
        return False
    if tool == "Write":
        new = str(ti.get("content") or "")
    else:
        cur, o, n = old.decode("utf-8", "replace"), str(ti.get("old_string") or ""), str(ti.get("new_string") or "")
        if o not in cur:
            return False
        new = cur.replace(o, n) if ti.get("replace_all") else cur.replace(o, n, 1)
    spec = importlib.util.spec_from_file_location("gate_stamp", os.path.join(HERE, "gate-stamp.py"))
    if spec is None or spec.loader is None:
        return False
    gs = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(gs)
        if any(gs._matches(rel, *gs.AREAS[a]) for a in gs.RAW_AREAS if a in gs.AREAS):  # noqa: SLF001
            return False
        return bool(gs.semantic_bytes(old, rel) == gs.semantic_bytes(new.encode("utf-8"), rel))
    except Exception:  # noqa: BLE001 - a guard that cannot judge refuses as before
        return False


def main() -> int:
    q = json.load(sys.stdin)
    root, path = q["root"], q["path"]
    rel = os.path.relpath(os.path.realpath(path), os.path.realpath(root))
    must_wait = not rel.startswith("..") and _is_engine(root, rel) and not docstring_only(rel, path, q["tool_input"], q["tool"])
    return 0 if must_wait else 1


if __name__ == "__main__":
    sys.exit(main())
