#!/usr/bin/env python3
"""Reserve the next glossary or registry-entry prefix under a host-wide lock - `make reserve KIND=... KEY=...`.

WHY (feature 265 FR-010, the GM 2026-09-27): two or three pages' research queues run at once, each in its own
session clone, and a new glossary file (`assets/glossary/NNNN-<term>.json`) or registry entry
(`research/sources/010-works-cited/NNNN-<key>.html`) takes its prefix as "the highest + 10". Two sessions reading
"the highest" at once take the same number - the collision feature 250 already met twice across a merge (a glossary
prefix main and a clone both used). So the prefix is allocated the way `make claim` allocates a feature number.

WHAT "NEXT" MEANS, read UNDER THE LOCK: 10 past the highest prefix held by
  1. the mirror's working tree         (main as this container last saw it)
  2. every clone under `<mirror>/.clones/` (the other sessions' and queues' unpushed files)
  3. the ledger `<mirror>/.specify/prefixes.jsonl` (a prefix reserved whose file is not visible yet)
THE RESERVATION IS THE FILE: a stub is written at the new path before the lock is released, so the next caller's scan
(source 2) sees it; the caller then fills it. The lock and the ledger sit under the mirror's `.specify/`, beside
`make claim`'s, gitignored.

THE KEY CAP (feature 274 D4; research R1: a write session's cost follows its turn count, and its keys drive its
turns). The page-session runner tells a WRITE session `L7R_PAGE_SESSION` (its id) and `L7R_KEY_CAP` (10); a check,
assertions, split or handover session is never told the cap. Every ledger row records the session. With both set, a
registry reservation past the cap for that session is refused with the continuation instructions - finish the
question in hand, write the unreached items to `$L7R_CONTINUE`, commit and stop - and the runner starts that brief
next in a fresh session. `KEY_CAP_OK='<reason>'` passes it, logged. Glossary terms are not capped.

WHAT IS LEFT HERE (feature 449 T145, phase 4's S2; the plan review's FR-003 ruling, ONE LIVE WRITER per shared file): the
reservation is `l7r-gate record reserve` (`rust/gate/crates/record/src/record/reserve.rs`, `make reserve`), the one writer of
`prefixes.jsonl` and the stubs. `uncited.py`, which loads this file by path until S3b ports it, keeps its one name, `reserve`, a
forwarder to that command (`ask:449-T86-door`), and `Refusal`, what it catches.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

GATE = Path(__file__).resolve().parent.parent / "gates" / "l7r-gate.sh"
#: The kinds a reservation takes - the Rust's `DIRS`. Named here because the command refuses another as argparse did (`make reserve`'s
#: words), where this function refused it in its own.
KINDS = ("glossary", "question", "registry", "uncited")


class Refusal(Exception):
    """A reservation refused (a key held, a cap reached, a kind or key not given): the command's own words."""


def reserve(kind: str, key: str, root: Path, mirror: Path | None = None, url: str = "", tags: str = "") -> Path:
    """The new file's path, its prefix reserved and a stub written, by `l7r-gate record reserve` (feature 449 T145). Its refusal
    (exit 2) is raised as `Refusal` with the command's words; anything else it raised, as `RuntimeError`. A registry entry
    reserved WITH a url is archived as it is cited, as `make reserve` does (no caller here passes one: `uncited.py` reserves
    `uncited` entries)."""
    if kind not in KINDS:
        raise Refusal(f"KIND must be one of {sorted(KINDS)}")
    cmd = [str(GATE), "record", "reserve", kind, key, "--root", str(root)]
    cmd += ["--mirror", str(mirror)] if mirror is not None else []
    cmd += ["--url", url] if url else []
    cmd += ["--tags", tags] if tags else []
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode == 2:
        raise Refusal(done.stderr.strip().removeprefix("reserve: "))
    if done.returncode:  # what the Rust raised, as the Python raised it (`sources.raised`)
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import sources  # noqa: PLC0415 - beside this file

        raise sources.raised(done.stderr)
    return Path(done.stdout.strip())
