"""The docstring-blind code id, for the engine's keys (feature 426, D2): `scripts/gates/codeid.py`, loaded by path.

The rule lives beside `gate-stamp.py` (where it always did): the gates and the guards load it by path from the scripts tree every
fixture repository copies whole, and this shim gives `gencache`, `render_cache` and `ci/` the same module. Its docstring holds
the why.

Research: hashing plumbing - NONE
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

_PATH = Path(__file__).resolve().parents[3] / "scripts" / "gates" / "codeid.py"


def _load():  # noqa: ANN202 - the module
    cached = sys.modules.get("l7r_codeid")
    if cached is not None:
        return cached
    spec = importlib.util.spec_from_file_location("l7r_codeid", _PATH)
    assert spec and spec.loader, f"cannot load {_PATH}"
    mod = importlib.util.module_from_spec(spec)
    sys.modules["l7r_codeid"] = mod
    spec.loader.exec_module(mod)
    return mod


_mod = _load()
semantic_bytes = _mod.semantic_bytes
split_ids = _mod.split_ids
strip_docstrings = _mod.strip_docstrings
