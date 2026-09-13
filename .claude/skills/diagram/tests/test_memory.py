"""`_memory.trim_heap` (feature 210): glibc's freed arenas go back to the kernel when a roll ends."""

from __future__ import annotations

import ast
import ctypes
import pathlib

import pytest

from l7r.diagram import _memory

ROOT = pathlib.Path(__file__).resolve().parents[1]


def test_trim_runs_here_and_reports_it() -> None:
    assert _memory.trim_heap() is True


def test_trim_is_a_courtesy_never_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    """A platform without glibc, or a libc without the symbol, gets False - a roll must never go red over
    a memory courtesy."""

    def no_libc(_name: str) -> object:
        raise OSError("no libc.so.6 here")

    monkeypatch.setattr(ctypes, "CDLL", no_libc)
    assert _memory.trim_heap() is False

    class NoSymbol:
        def __getattr__(self, name: str) -> object:
            raise AttributeError(name)

    monkeypatch.setattr(ctypes, "CDLL", lambda _name: NoSymbol())
    assert _memory.trim_heap() is False


# ---- feature 237: what a worker LOADS, which is most of what a gate costs ------------------------------------------


HEAVY = ("shapely", "numpy", "PIL")  # 21.7, 17.9 and 2.3 MiB a worker - the three that are worth deferring


def test_no_engine_module_imports_a_heavy_library_at_import_time() -> None:
    """The surface is DERIVED, never a list in a spec (feature 237, FR-010 for shapely; numpy and PIL added
    at the GM's request on 2026-09-13, the same deferral for the two tools that hold them).

    `shapely` costs 16.3 MiB with the numpy it pulls in, and a module-level import made all ten gate workers
    pay it to COLLECT the package, whichever one ran the geometry. Each module that needs it binds the names
    through its own `_load_shapely()` on first use instead. A hand-kept list is how the requirement first
    said eight sites when the code had seven, so this asks the tree: an `import shapely` outside a function
    body is the thing that must not come back.
    """
    offenders = []
    for path in sorted((ROOT / "l7r").rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        inside = {id(n) for fn in ast.walk(tree) if isinstance(fn, (ast.FunctionDef, ast.AsyncFunctionDef)) for n in ast.walk(fn)}
        for node in ast.walk(tree):
            if id(node) in inside or not isinstance(node, (ast.Import, ast.ImportFrom)):
                continue
            heavy = (isinstance(node, ast.ImportFrom) and (node.module or "").startswith(HEAVY)) or (isinstance(node, ast.Import) and any(a.name.startswith(HEAVY) for a in node.names))
            if heavy and not _under_type_checking(tree, node):
                offenders.append(f"{path.relative_to(ROOT)}:{node.lineno}")
    assert not offenders, f"a heavy library is imported at import time in {offenders} - bind it in a loader instead, as `_load_shapely` / `_load_arrays` do (feature 237)"


def _under_type_checking(tree: ast.Module, target: ast.stmt) -> bool:
    """A `TYPE_CHECKING` guard costs nothing at run time: those imports never execute."""
    return any(isinstance(node, ast.If) and "TYPE_CHECKING" in ast.dump(node.test) and any(target is s for s in node.body) for node in ast.walk(tree))


def test_importing_the_whole_engine_does_not_load_shapely_but_building_geometry_does() -> None:
    """Asked of the PROCESS rather than of the source, in a child so this run's own imports cannot answer it.

    The first half is what the ten workers pay at collection; the second is the proof the deferral still
    WORKS rather than merely hiding the import (SC-005).
    """
    import subprocess
    import sys

    probe = (
        "import importlib, pathlib, sys\n"  # noqa: ERA001 - the probe text continues below
        f"root = pathlib.Path({str(ROOT)!r})\n"
        "sys.path.insert(0, str(root))\n"
        "for p in sorted((root / 'l7r').rglob('*.py')):\n"
        "    m = str(p.relative_to(root)).removesuffix('.py').replace('/', '.').removesuffix('.__init__')\n"
        "    if '.ci' in f'.{m}' or 'pack_audit' in m:\n"
        "        continue\n"
        "    try:\n"
        "        importlib.import_module(m)\n"
        "    except BaseException:\n"
        "        pass\n"
        "print('after imports:', 'shapely' in sys.modules)\n"
        "from l7r.diagram.waterfields.seams.geoms import PlotGeoms\n"
        "PlotGeoms([{'poly': [(0.0, 0.0), (10.0, 0.0), (10.0, 10.0)]}]).geom(0)\n"
        "print('after geometry:', 'shapely' in sys.modules)\n"
    )
    out = subprocess.run([sys.executable, "-c", probe], capture_output=True, text=True, check=True).stdout
    assert "after imports: False" in out, f"the engine still pulls shapely in at import time:\n{out}"
    assert "after geometry: True" in out, f"the lazy binding did not load it when used:\n{out}"
