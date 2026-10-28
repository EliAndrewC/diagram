"""The docstring-blind code id: what a piece of Python DOES, without what it says about itself (feature 426, D2).

A `.py` file's id is its AST with every docstring dropped and no line or column attributes (`ast.dump`'s default), so a
comment, a docstring, a constant's claim string, a blank line or reformatting leaves it alone, and any token that runs moves
it. One definition, read three ways:

- `semantic_bytes` - a whole file, what `gate-stamp.py` beside it hashes for `make done` (it loads this module by path, stdlib
  only, because it runs inside the guards and must not import the engine package) and `ci/delta.py` through it; the engine's
  keys read it through `l7r/diagram/pipeline/codeid.py`, a shim that loads this file;
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
import re

_FUNCS = (ast.FunctionDef, ast.AsyncFunctionDef)
#: THE ENGINE PATHS of a landing - a delta with one owes the landing cohort (`l7r.diagram.ci.delta.is_engine`'s list, feature 132
#: FR-008). One definition, read by `scripts/land.py` and by the cohort's counter-only test (`cohort_known.counter_only`, feature
#: 446), so the two can never disagree about what a counter-only delta may leave unchecked
ENGINE = re.compile(r"^(l7r/.*\.py|pool/.*\.gen\.py|pool/.*\.json)$")


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


def _plain(v: ast.expr) -> bool:
    """A name, or an attribute chain on one (`self.ring`): read, never called."""
    return isinstance(v, ast.Name) or (isinstance(v, ast.Attribute) and _plain(v.value))


def _counter_value(v: ast.expr) -> bool:
    """A counter's increment, in the forms feature 446's FR-001 defines: a literal, a name,
    `len(<name or attribute>)`, `<name>.size`, `max(len(<name>) - <literal>, <literal>)`, or a product of these - nothing that
    calls engine code, so the block can do no more than add to a counter."""
    if isinstance(v, ast.Constant) or isinstance(v, ast.Name):
        return True
    if isinstance(v, ast.Attribute) and v.attr == "size" and isinstance(v.value, ast.Name):
        return True
    if isinstance(v, ast.BinOp) and isinstance(v.op, ast.Mult):
        return _counter_value(v.left) and _counter_value(v.right)
    if isinstance(v, ast.Call) and isinstance(v.func, ast.Name) and not v.keywords:
        if v.func.id == "len" and len(v.args) == 1:
            return _plain(v.args[0])
        if v.func.id == "max" and len(v.args) == 2 and isinstance(v.args[1], ast.Constant):
            d = v.args[0]
            return isinstance(d, ast.BinOp) and isinstance(d.op, ast.Sub) and isinstance(d.right, ast.Constant) and isinstance(d.left, ast.Call) and _counter_value(d.left)
    return False


def is_counter_block(s: ast.stmt) -> bool:
    """A COUNTER BLOCK (feature 446, FR-001): `if __debug__:` with no `else`, its body nothing but `OPS["<str>"] += / -= <value>`
    (`_counter_value`). Any other `if __debug__:` - an `else`, a call, a write elsewhere - is code: a cohort rolls without `-O`, so
    its body runs, and only a write to the counters is provably inert."""
    if not (isinstance(s, ast.If) and isinstance(s.test, ast.Name) and s.test.id == "__debug__" and not s.orelse and s.body):
        return False
    for b in s.body:
        if not (isinstance(b, ast.AugAssign) and isinstance(b.op, (ast.Add, ast.Sub)) and isinstance(b.target, ast.Subscript)):
            return False
        tgt = b.target
        if not (isinstance(tgt.value, ast.Name) and tgt.value.id == "OPS" and isinstance(tgt.slice, ast.Constant) and isinstance(tgt.slice.value, str)):
            return False
        if not _counter_value(b.value):
            return False
    return True


def strip_counters(tree: ast.AST) -> ast.AST:
    """`tree` with every counter block removed, in place (`is_counter_block`)."""
    for node in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            stmts = getattr(node, field, None)
            if isinstance(stmts, list):
                stmts[:] = [s for s in stmts if not is_counter_block(s)]
    return tree


def debug_free_bytes(data: bytes, name: str) -> bytes:
    """A `.py` file's semantic bytes (`semantic_bytes`) with every counter block removed; any other file, or one that does not
    parse, its bytes. Two versions are COUNTER-ONLY-EQUAL when these are equal (feature 446, FR-001)."""
    if not name.endswith(".py"):
        return data
    try:
        tree = ast.parse(data)
    except SyntaxError, ValueError:
        return data
    return ast.dump(strip_counters(strip_docstrings(tree))).encode()


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
