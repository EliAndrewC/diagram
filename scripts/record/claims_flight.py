"""A claims check IN FLIGHT, seen rather than inferred (feature 426, D1).

`make claims-bundle` and `make claims-triage` mark the bundle they build as in flight; `make claims-checked` and `make
claims-triaged` clear it when its reply is recorded. `make land` waits for a claims round only while a live mark stands:
inferred from "the gate says a claim is owed", it waited its whole claims wait (`land.CLAIMS_WAIT_S`) for a check nobody had
dispatched (feature 417 T50's landing, twice). A mark older than the wait is stale - an agent that died, a bundle abandoned -
and is ignored. The marks live under the clone's common git directory, so a linked worktree and its clone share them.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import time
from pathlib import Path

MAX_AGE_S = 1200.0
"""A mark older than this is stale: the landing's own claims wait (`scripts/land.py` `CLAIMS_WAIT_S`), past which it would have
stopped waiting anyway."""


def _dir(root: Path) -> Path:
    p = subprocess.run(["git", "-C", str(root), "rev-parse", "--git-common-dir"], capture_output=True, text=True, check=False)
    common = Path(p.stdout.strip()) if p.returncode == 0 and p.stdout.strip() else root / ".git"
    return (common if common.is_absolute() else root / common) / "claims-in-flight"


def _name(bundle: Path) -> str:
    return hashlib.sha256(str(Path(bundle).resolve()).encode()).hexdigest()[:16] + ".json"


def mark(root: Path, bundle: Path) -> None:
    """`bundle` is in flight: built, its check about to be dispatched."""
    d = _dir(root)
    d.mkdir(parents=True, exist_ok=True)
    (d / _name(bundle)).write_text(json.dumps({"bundle": str(Path(bundle).resolve()), "at": time.time()}), encoding="utf-8")


def clear(root: Path, bundle: Path) -> None:
    """`bundle`'s reply is recorded: no longer in flight."""
    (_dir(root) / _name(bundle)).unlink(missing_ok=True)


def live(root: Path, now: float | None = None) -> list[str]:
    """The bundles in flight now - marked within `MAX_AGE_S` and not cleared."""
    d = _dir(root)
    now = time.time() if now is None else now
    out = []
    for f in sorted(d.glob("*.json")) if d.is_dir() else []:
        try:
            rec = json.loads(f.read_text(encoding="utf-8"))
        except OSError, ValueError:
            continue
        if now - float(rec.get("at", 0)) <= MAX_AGE_S:
            out.append(str(rec.get("bundle", f.name)))
    return out
