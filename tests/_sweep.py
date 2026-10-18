"""How many seeds a random-equivalence test sweeps: its own default, or `L7R_SWEEP_SEEDS` (`make sweep FILE=... SEEDS=N`).

The round arbiter's tooling fix on hour:387-scale-the-placement-loops@1: a session widening a sweep copied the tracked test to a
backup and edited its `range(...)` in place, five times in one hour - one slip and the widened or debug form is committed or
landed. A sweep is widened from the command line instead, and the file never changes."""

from __future__ import annotations

import os


def seeds(default: int) -> range:
    """`range(default)`, or `range(L7R_SWEEP_SEEDS)` when the sweep is widened."""
    return range(int(os.environ.get("L7R_SWEEP_SEEDS") or default))
