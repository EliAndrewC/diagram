"""A generated Mode A sheet, brought up to date before a test reads it.

WHY (2026-09-26, feature 250's recovery session): a generated exception's svg is gitignored, and the tests
generated it only when it was ABSENT. A clone whose copy predated feature 262's `data-kind` tags kept reading the
old sheet, and `program_complete` failed there while it passed on a fresh checkout of the same commit - a stale
artifact that looked exactly like a regression. So the sheet is regenerated when it is missing OR older than its
generator or any engine module, under a lock, so that two workers never read a sheet the other is writing.
"""

from __future__ import annotations

import fcntl
import functools
import os
import subprocess
import sys
from collections.abc import Callable

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENGINE = os.path.join(SKILL, "l7r", "diagram")


@functools.cache
def newest_engine_mtime(root: str = ENGINE) -> float:
    """The latest modification time of any engine module - a sheet older than it may predate the code that draws it."""
    newest = 0.0
    for dirpath, dirnames, files in os.walk(root):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for f in files:
            if f.endswith(".py"):
                newest = max(newest, os.path.getmtime(os.path.join(dirpath, f)))
    return newest


def is_stale(svg: str, gen: str, engine_mtime: float) -> bool:
    """True when the sheet is missing or older than its generator or the engine."""
    return not os.path.isfile(svg) or os.path.getmtime(svg) < max(os.path.getmtime(gen), engine_mtime)


def fresh(svg: str, gen: str, generated: bool, engine_mtime: float | None = None, run: Callable[..., object] = subprocess.run) -> str:
    """The sheet's path, regenerated first when it is a declared generated exception and stale.

    A hand-drawn sheet is never regenerated - it has no generator that writes it, and it is committed."""
    if not generated:
        return svg
    mtime = newest_engine_mtime() if engine_mtime is None else engine_mtime
    if not is_stale(svg, gen, mtime):
        return svg
    with open(svg + ".lock", "w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if is_stale(svg, gen, mtime):  # another worker may have regenerated it while this one waited
            run([sys.executable, gen], check=True, env={**os.environ, "DIAGRAM_SKIP_RENDER": "1"}, cwd=SKILL)
    return svg
