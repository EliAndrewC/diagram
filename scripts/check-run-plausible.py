#!/usr/bin/env python3
"""Refuse to record a gate GREEN when the run finished too fast to have done the work.

WHY (found 2026-09-05, live in the tree): **a dry run was minting a push credential.** GNU make
executes `$(MAKE)` sub-invocations even under `-n`, so `make -n done` walks the `done` recipe, every
phase trivially "succeeds" without doing anything, and the recipe's closing `LOGRUN ... green` and
`$(STATE) green-local` lines then run FOR REAL. The result is a correctly-hashed green verification
record, written in about four seconds.

That record is the whole of what a push demands: `ci/state.py`'s `already_verified` asks only whether
a `GREEN_TARGETS` record's hash matches the current engine content. So parse-checking a Makefile edit
- an ordinary, sensible thing to do - authorized a push. Two such records exist in `dev/run-log/`
(2026-09-05 18:01:45 at 3 s and 18:07:40 at 4 s, against a day median of 382 s).

**And it was self-perpetuating**: every later `make done` saw a matching hash, short-circuited, and
RE-STAMPED the record with a fresh timestamp, so it never aged out. Two consecutive gates returned
instantly; the only way to force real work was to delete `.git/verification-state.json`.

THE FLOOR IS DERIVED, NOT INVENTED. A fixed number would be wrong in both directions: this gate's
median has ranged from 21 s to 587 s in two weeks (feature 135 took it to ~21 s warm; feature 174 put
it back over 300 s by making the coverage floors unconditional). So the floor comes from the SAME
pinned baseline feature 171's ratchet already uses - `scripts/_ratchet.py`'s `RATCHETS[target].baseline`
- which the GM ratified and which is re-pinned deliberately when a target's work changes. A ceiling
and a floor over one baseline is one number to maintain, not two.

TEN PERCENT, and why that is not arbitrary. The thing being excluded is a run that did NO work: a dry
run lands around 1% of baseline. A genuine warm run has never been below about 30% of its era's
baseline in 223 recorded green runs. Ten percent sits in the empty middle, and it is checked against
the whole history rather than chosen by taste - `tests/tooling/test_run_plausible.py` replays every
recorded green `done` and asserts the floor would have failed exactly the two known dry runs.

WHAT IT DOES NOT COVER, stated so nobody reads it as more than it is: a run that executes the phases
but has been subverted some other way. The floor is a smoke alarm for "nothing happened", not a proof
that the right thing happened. The 100% coverage floor and the phases themselves are what check that.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

FRACTION = 0.10  # of the target's pinned ratchet baseline
ABSOLUTE_MIN = 5  # seconds; a floor below this could not distinguish anything


def _baseline(target: str) -> int | None:
    """The pinned baseline `_ratchet.py` already keeps for this target, or None if it has no row."""
    here = Path(__file__).resolve().parent
    sys.path.insert(0, str(here))
    try:
        import _ratchet  # type: ignore[import-not-found]
    except Exception:
        return None
    finally:
        sys.path.pop(0)
    row = getattr(_ratchet, "RATCHETS", {}).get(target)
    return getattr(row, "baseline", None) if row is not None else None


def floor_for(target: str) -> int | None:
    b = _baseline(target)
    return None if not b else max(ABSOLUTE_MIN, int(b * FRACTION))


def dry_run(makeflags: str | None = None) -> bool:
    """Is this a `make -n` (or `--just-print`) invocation?

    The FIRST word of MAKEFLAGS carries the single-letter flags with no leading dash. Checking the
    whole string would false-positive on any variable whose name or value contains an `n` - and this
    gate is invoked with `REASON=`, `FILE=` and friends constantly, so that matters.
    """
    mf = os.environ.get("MAKEFLAGS", "") if makeflags is None else makeflags
    first = mf.split(" ", 1)[0] if mf else ""
    return "=" not in first and "n" in first


def check(target: str, seconds: float, makeflags: str | None = None) -> tuple[bool, str]:
    if dry_run(makeflags):
        return False, (
            f"REFUSED to record `{target}` green: this is a DRY RUN (`make -n`).\n"
            "  make executes $(MAKE) sub-invocations even under -n, so the recipe reaches its\n"
            "  recording lines having done no work. A dry run must not mint a push credential."
        )
    fl = floor_for(target)
    if fl is None:
        return True, ""
    if seconds < fl:
        return False, (
            f"REFUSED to record `{target}` green: it finished in {seconds:.0f}s, under the {fl}s floor.\n"
            f"  The floor is 10% of the pinned ratchet baseline for `{target}`, so it tracks the era\n"
            "  rather than a fixed number. A run this fast did not do the work, and a green record is\n"
            "  the whole of what a push demands. Nothing was recorded; run the gate for real."
        )
    return True, ""


def main(argv: list[str]) -> int:
    # `--reuse <target>`: the SHORT-CIRCUIT path, which re-stamps an existing record rather than
    # earning a new one. No duration floor applies there - 0 s is correct for a reuse - but the
    # dry-run refusal does, and it is the more important half: re-stamping is what kept the bogus
    # record from ever ageing out, so a `make -n done` could keep a false credential alive for ever.
    if len(argv) == 2 and argv[0] == "--reuse":
        if dry_run():
            print(
                f"\n\033[1mREFUSED to re-stamp `{argv[1]}`: this is a DRY RUN (`make -n`).\033[0m\n"
                "  A dry run must not refresh a verification record either - re-stamping is what\n"
                "  kept a bogus record alive across every later gate.\n",
                file=sys.stderr,
            )
            return 1
        return 0
    if len(argv) != 2:
        print("usage: check-run-plausible.py <target> <elapsed-seconds> | --reuse <target>", file=sys.stderr)
        return 2
    try:
        secs = float(argv[1])
    except ValueError:
        return 0  # an unparseable duration is not this guard's business
    ok, why = check(argv[0], secs)
    if not ok:
        print(f"\n\033[1m{why}\033[0m\n", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
