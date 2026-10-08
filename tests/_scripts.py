"""Where a script lives, by name, for the tests that load one.

The GM had the flat scripts/ organized by purpose on 2026-10-08 (`scripts/CLAUDE.md`): the guards moved to
`scripts/hooks/`, their helpers to `scripts/hooks/lib/`, the gates, record, page, review and measurement tooling to their
own subdirectories, the guard suites to `tests/hooks/`, and a helper in a subdirectory lost its leading underscore. A
test names the script it loads; this finds it, so no test spells the directory a script happens to live in.
"""

from __future__ import annotations

import functools
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


@functools.cache
def _index() -> dict[str, Path]:
    found: dict[str, Path] = {}
    for base in (ROOT / "scripts", ROOT / "tests" / "hooks"):
        for p in base.rglob("*"):
            if p.is_file() and "__pycache__" not in p.parts:
                assert p.name not in found, f"two scripts named {p.name}: {found[p.name]} and {p}"
                found[p.name] = p
    return found


def script(name: str) -> Path:
    """The file a script NAME means: `record_owed`, `_record_owed`, `record_owed.py`, `check-entry-headings` or
    `clone-sync-hooks.sh` - a module stem, the pre-2026-10-08 underscore form, or a file name."""
    idx = _index()
    stem = name.lstrip("_")
    for cand in (name, stem, f"{stem}.py", f"{stem}.sh", f"{stem.replace('_', '-')}.py"):
        if cand in idx:
            return idx[cand]
    raise FileNotFoundError(f"no script named {name!r} under scripts/ or tests/hooks/")


def script_dir(name: str) -> str:
    """The directory to put on `sys.path` to import the script NAME flat (`import record_owed`)."""
    return str(script(name).parent)


GUARDS = ROOT / "scripts" / "hooks"
SUITES = ROOT / "tests" / "hooks"


def tree(pattern: str) -> list[Path]:
    """Every file matching `pattern` under scripts/ (any depth) and tests/hooks/ - the set one glob over the flat
    scripts/ directory covered before the move."""
    found = [*(ROOT / "scripts").rglob(pattern), *SUITES.glob(pattern)]
    return sorted(p for p in found if p.is_file() and "__pycache__" not in p.parts)


def script_dirs() -> list[str]:
    """Every directory a script lives in, for a test that imports several flat (`import hm_make`) the way the flat
    scripts/ on `sys.path` once let it."""
    return sorted({str(p.parent) for p in tree("*.py")})
