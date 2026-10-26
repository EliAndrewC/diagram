"""The docstring-blind code id: what a piece of Python DOES, without what it says about itself (feature 426, D2).

A `.py` file's id is its AST with every docstring dropped and no line or column attributes (`ast.dump`'s default), so a
comment, a docstring, a constant's claim string, a blank line or reformatting leaves it alone, and any token that runs moves
it. One definition, read three ways:

- `semantic_bytes` - a whole file, what `scripts/gates/gate-stamp.py` hashes for `make done` (it loads this module by path,
  stdlib only, because it runs inside the guards and must not import the engine package) and `ci/delta.py` through it;
- `split_ids` - a module's top level and each function, what the roll and map key (`gencache.split_sources`) hashes per
  executed function;
- `strip_docstrings` - the rule itself, for a caller holding a tree.

WHY (GM 2026-08-26, feature 133 T11; feature 426): a record-the-why comment is REQUIRED at the point of change in this project
and the research claims live in docstrings, so a key that counted them re-ran the gate (until 133) and re-rolled every seed
through an edited function (until 426: feature 417's claims rounds re-rolled 54 seeds a relabel). Bytecode was priced and
declined: `co_consts` carries docstrings and the line table every comment's line shift. A file that does not parse is hashed as
its bytes - unparseable is still content.

What is CONTENT is not stripped here but by the caller choosing bytes: the interactive class registry's docstrings are the
modal text (`interactive/classes/_base.py` returns `cls.__doc__`), so `gencache` and `render_cache` key `interactive/` on its
bytes, as `gate-stamp`'s `RAW_AREAS` do.

Research: hashing plumbing - NONE
"""

from __future__ import annotations

import ast
import copy
import hashlib

_FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)


def strip_docstrings(tree: ast.AST, keep_module_docstring: bool = False) -> ast.AST:
    """`tree` with EVERY bare string statement removed, in place: a body's docstring and the claim string after a constant's
    assignment alike (feature 385 T57, the round arbiter's fix on hour:385-approach-checklist@20) - Python evaluates a bare
    string statement and discards it; no token of it runs. `keep_module_docstring` keeps a module's own docstring, for a
    script that prints it as its usage (feature 426: `ci/state.tooling_hash`)."""
    head = tree.body[0] if keep_module_docstring and isinstance(tree, ast.Module) and tree.body else None
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if s is head or not (isinstance(s, ast.Expr) and isinstance(s.value, ast.Constant) and isinstance(s.value.value, str))]
    return tree


def semantic_bytes(data: bytes, name: str, keep_module_docstring: bool = False) -> bytes:
    """What runs, for a `.py` file: its docstring-free AST dumped without attributes (its own module docstring kept with
    `keep_module_docstring`); any other file, or one that does not parse, its bytes verbatim."""
    if not name.endswith(".py"):
        return data
    try:
        tree = ast.parse(data)
    except SyntaxError, ValueError:
        return data
    return ast.dump(strip_docstrings(tree, keep_module_docstring)).encode()


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def split_ids(src: bytes) -> tuple[str, dict[str, str], set[str]] | None:
    """(the module's top-level id, {function qualname: its id}, {class qualnames}) for `src`, or None when it does not parse.

    A function's id is its own node's (decorators, signature and body, nested definitions included); the top level is the
    module with every function taken out, so a changed constant, import, class attribute or decorator-free class line moves it
    and a changed function body moves only that function - the split `gencache` always made, now blind to docstrings and
    comments."""
    try:
        tree = ast.parse(src)
    except SyntaxError, ValueError:
        return None
    strip_docstrings(tree)
    funcs: dict[str, str] = {}
    classes: set[str] = set()

    def walk(node: ast.AST, prefix: str) -> None:
        for child in ast.iter_child_nodes(node):
            if isinstance(child, _FUNCS):
                qual = f"{prefix}{child.name}"
                funcs[qual] = _sha(ast.dump(child).encode())
                walk(child, f"{qual}.")  # nested defs get their own entry AND stay in their parent's id
            elif isinstance(child, ast.ClassDef):
                classes.add(f"{prefix}{child.name}")
                walk(child, f"{prefix}{child.name}.")
            else:
                walk(child, prefix)

    walk(tree, "")
    top = copy.deepcopy(tree)
    for node in ast.walk(top):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if not isinstance(s, _FUNCS)]
    return _sha(ast.dump(top).encode()), funcs, classes
