"""One parse of each engine module per test process (feature 276, FR-001).

WHY. Four tests read every module's syntax tree - `test_memory`, `test_driver`, `test_package_surfaces`,
`test_water_ways` - and each parsed all ~266 modules itself and walked every node (1.0-1.5 million a test,
1.23-1.87 s each alone: specs/276 research R1). Parsed here once, keyed on the file's content (its mtime and
size, so an edit mid-session is a new parse, never a stale tree), a worker that runs two of them pays once.

A NEEDLE SKIPS A FILE WITHOUT PARSING IT, and only where the skip is provable: a test hands the literal its
property cannot exist without (`STAGES` for a loop over the stages, `del ` for a `del` statement), so a file
whose text lacks it holds nothing the walk could find. `PARSES` counts real parses - the shared-parse test
asserts it equals the number of distinct files read.
"""

from __future__ import annotations

import ast
from collections.abc import Iterable
from pathlib import Path

PARSES = 0
_TREES: dict[tuple[str, int, int], tuple[str, ast.Module]] = {}
_WALKS: dict[int, list[ast.AST]] = {}


def parsed(path: Path) -> tuple[str, ast.Module]:
    """The file's source and syntax tree, parsed at most once per content."""
    global PARSES  # the counter the shared-parse test reads is the point
    st = path.stat()
    key = (str(path), st.st_mtime_ns, st.st_size)
    hit = _TREES.get(key)
    if hit is None:
        source = path.read_text(encoding="utf-8")
        hit = (source, ast.parse(source))
        _TREES[key] = hit
        PARSES += 1
    return hit


def walked(tree: ast.AST) -> list[ast.AST]:
    """Every node of `tree`, in `ast.walk` order - walked once per tree."""
    nodes = _WALKS.get(id(tree))
    if nodes is None:
        nodes = list(ast.walk(tree))
        _WALKS[id(tree)] = nodes
    return nodes


def engine_modules(files: Iterable[Path], needles: tuple[str, ...] = (), skip_broken: bool = False) -> list[tuple[Path, str, ast.Module]]:
    """(path, source, tree) for each file whose text holds any of `needles` (all files when none is given).

    A file that fails to parse RAISES, as the scans always did, unless `skip_broken` - `test_package_surfaces`'s own
    choice, since it walks gen scripts that may be mid-edit."""
    out = []
    for path in files:
        if needles and not any(n in path.read_text(encoding="utf-8") for n in needles):
            continue
        try:
            source, tree = parsed(path)
        except SyntaxError:
            if not skip_broken:
                raise
            continue
        out.append((path, source, tree))
    return out


def module_level(tree: ast.Module) -> list[ast.AST]:
    """Every node NOT inside a function body - one walk that does not descend into a `def`.

    The same set `test_memory` built by walking every function and subtracting (nested functions walked once per
    enclosing function), without the repeat."""
    out: list[ast.AST] = []
    stack: list[ast.AST] = [tree]
    while stack:
        node = stack.pop()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        out.append(node)
        stack.extend(ast.iter_child_nodes(node))
    return out
