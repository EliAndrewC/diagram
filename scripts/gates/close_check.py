#!/usr/bin/env python3
"""No route closes a feature without its report and its carried measurements (feature 375, FR-009, FR-014; plan D13).

WHY. The GM, 2026-10-10: the post-mortem table is the last step of every feature, and *"anything that requires someone to just
remember to do the right thing is not tenable"*. A feature closes three ways - its last `make tick`, a status line turned
`Done` (or `Superseded by`, `Withdrawn`), `make gm-reviewed` - and each asks this one check, as does the push for every
feature the delta touches that reads closed. Two things are owed:

- `specs/NNN-*/report.md`, written by `make feature-report F=NNN WRITE=1` (FR-009: every feature gets one, however small);
- every measurement another feature's spec CARRIED to it (`Carried: SC-nnn -> NNN <key>`, FR-014) present as a key of its
  `measurements.json` - so a success criterion measured in a later feature cannot be dropped by forgetting it.

A feature already closed when this check landed is not asked (`closed-before-375.txt`, written at that commit from what
`make speckit-todo` read closed - never a number range: 372 and 374 were open, and are asked).

    close_check.py <feature dir>        the reasons it may not close, one a line (none: it may)
    close_check.py --push <range>       the same, for every touched feature that reads closed
    close_check.py --carries            every carry, with whether it is met
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.dont_write_bytecode = True  # the push runs this in fixture trees whose `git status` must stay clean
GRANDFATHERED = Path(__file__).resolve().parent / "closed-before-375.txt"
_CARRY = re.compile(r"`?Carried:\s*(SC-\d+)\s*->\s*(\d+)\s+([\w.-]+)`?")


def carries(specs: Path) -> list[tuple[str, str, str, str]]:
    """(declaring feature, SC, carrying feature number, key) for every `Carried:` line in any spec."""
    out = []
    for spec in sorted(specs.glob("*/spec.md")):
        for sc, num, key in _CARRY.findall(spec.read_text(encoding="utf-8", errors="replace")):
            out.append((spec.parent.name, sc, num, key))
    return out


def grandfathered() -> set[str]:
    return set(GRANDFATHERED.read_text(encoding="utf-8").split()) if GRANDFATHERED.is_file() else set()


def reasons(d: Path, specs: Path | None = None) -> list[str]:
    """Why the feature `d` may not close: no report, or a carried key missing from its measurements.json."""
    if d.name in grandfathered():
        return []
    out = []
    if not (d / "report.md").is_file():
        out.append(f"{d.name} has no report.md - `make feature-report F={int(d.name.split('-')[0])} WRITE=1` writes it (FR-009)")
    try:
        have = set(json.loads((d / "measurements.json").read_text(encoding="utf-8")))
    except (OSError, ValueError):
        have = set()
    num = d.name.split("-", 1)[0].lstrip("0")
    for decl, sc, n, key in carries(specs or d.parent):
        if n.lstrip("0") == num and key not in have:
            out.append(f"{decl}'s {sc} is carried here and `{key}` is not in {d.name}/measurements.json (FR-014)")
    # GUARD_EDIT_OK: feature 378 FR-004 - a new closing requirement, the GM 2026-10-10: a `research record` feature closes
    # only once each question it changed is cited by a checked `Research:` claim or recorded as implemented nowhere
    out += _impl_check().missing(d, d.resolve().parents[1])  # the repository holding `specs/<d>`
    hold = _arbiter().fix_hold(d)  # feature 379 FR-004: no feature closes around an open arbiter tooling fix
    return out + ([hold] if hold else [])


def _arbiter():  # noqa: ANN202 - scripts/hooks/lib/hm_arbiter.py by path
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("hm_arbiter", ROOT / "scripts" / "hooks" / "lib" / "hm_arbiter.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _impl_check():  # noqa: ANN202 - scripts/record/impl_check.py by path (the gates and the record are siblings)
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("impl_check", ROOT / "scripts" / "record" / "impl_check.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _todo():  # noqa: ANN202 - speckit-todo.py by path (a hyphenated script), one state rule
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("speckit_todo", ROOT / "scripts" / "speckit-todo.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["speckit_todo"] = mod
    spec.loader.exec_module(mod)
    return mod


def push_reasons(root: Path, rng: str) -> list[str]:
    """Every touched feature that reads closed (its tasks all ticked, or a closing status word) and may not close."""
    sys.path.insert(0, str(ROOT / "scripts" / "gates"))
    import plan_gate  # noqa: PLC0415

    todo = _todo()
    out = []
    for name in plan_gate.touched_features(root, rng):
        d = root / name
        if d.is_dir() and todo.feature(d).state == "closed":
            out += reasons(d, root / "specs")
    return out


def write_grandfathered(specs: Path) -> int:
    """The features closed when this check lands - the only ones it does not ask (plan D13). Run once, at that commit."""
    todo = _todo()
    names = sorted(f.name for f in todo.features(specs) if f.state == "closed")
    GRANDFATHERED.write_text("\n".join(names) + "\n", encoding="utf-8")
    return len(names)


def main(argv: list[str]) -> int:
    root = Path(".").resolve()
    if argv[:1] == ["--push"]:
        found = push_reasons(root, argv[1] if len(argv) > 1 else "origin/main...HEAD")
    elif argv[:1] == ["--carries"]:
        for decl, sc, n, key in carries(root / "specs"):
            print(f"{decl} {sc} -> {n} `{key}`")
        return 0
    elif argv[:1] == ["--write-grandfathered"]:
        print(f"close-check: {write_grandfathered(root / 'specs')} feature(s) closed before the check")
        return 0
    elif len(argv) == 1:
        found = reasons(Path(argv[0]).resolve())
    else:
        print(__doc__.split("\n\n")[-1], file=sys.stderr)
        return 2
    for f in found:
        print(f)
    return 1 if found else 0


if __name__ == "__main__":
    sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parents[1] / "hooks" / "lib"))
    sys.dont_write_bytecode = True  # a record leaves no __pycache__ in the worktree (feature 406)
    import usage_log  # noqa: E402 - feature 406 T03 (D162): every refusing check records its run

    raise SystemExit(usage_log.exited("close_check", main(sys.argv[1:])))
