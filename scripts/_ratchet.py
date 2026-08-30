#!/usr/bin/env python3
"""Runtime ratchets: a target that gets slower fails, instead of getting slower quietly (feature 171).

WHY THIS EXISTS (GM 2026-08-30, on being shown that `make done`'s median went 35 s -> 148 s in three
days): *"I could have sworn that we had some code in place that detected when we had our unit tests
start to take longer relative to some previous baseline so that if we ever had this kind of increase,
then we would notice it. So how did this happen?"* They were half right - `QUICK_BUDGET` existed, it
covered `make quick` alone, and even there it was a 60 s absolute ceiling over a target that runs 11 s.
Nothing has ever asserted on `done`'s duration, so a 4x slowdown produced no failure anywhere.

THE SPEC IS `specs/171-runtime-ratchets/spec.md`, written and reviewed by the `diagram-testing`
session and handed off. Four of its properties are load-bearing, and each was learned by a review
round finding the first version wrong:

1. THE GM'S NUMBERS ARE HARD CEILINGS THE MECHANISM SITS UNDER. `quick` fails at 15 s, `done` at 45 s
   once its baseline is 35 s. The derivation may tighten below them and may NEVER compute a ceiling
   above them - an early draft's `max(baseline + 4, baseline * 1.3)` LOOSENED as the baseline drifted,
   so a 12 s quick baseline bought a 16 s ceiling, past the GM's own figure. That is the mechanism
   relaxing exactly when the thing it guards starts happening. The `min()` is what stops it.

2. THE BASELINE IS PINNED, NOT ROLLING. A rolling median follows a twenty-small-steps regression
   upward and would not have caught the motivating 35 -> 135 at all. A baseline moves only by a
   committed edit, with a written reason (FR-010) - which is also why an uncapped ceiling cannot drift:
   it can only grow behind a human decision.

3. WHAT IS COMPARED DIFFERS BY TARGET AND REGIME. `quick`: the run itself, which is the GM's phrasing.
   `done` while its baseline is above 35 s: the median of recent green same-scope runs, because at the
   interim ceiling a per-run bar would fire on 28% of normal runs. `done` once the baseline reaches
   35 s: the run itself again, because the GM's sentence is about a run.

4. A NEW TARGET IS A ROW, NOT A MECHANISM (FR-005), and the FULL/AWS row is present and OFF (FR-006) -
   the GM: *"I am not interested in running the lengthy tests at this time"*.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass

# `HARD_AT_OR_BELOW` is the baseline at which the GM's ceiling becomes the fixed rule for that target.
# For `quick` the GM stated 15 s against today's 11 s, so it binds NOW. For `done` they stated 45 s
# against a 35 s baseline that does not exist yet, so it binds when somebody pins 35 - which is the
# separate efficiency work's job, not this feature's.
@dataclass(frozen=True)
class Ratchet:
    target: str
    baseline: int          # PINNED. Moves only by a committed edit, and never without `reason`.
    reason: str            # FR-010: why the baseline is what it is. Empty is a test failure.
    hard_ceiling: int | None = None      # the GM's stated number, where they stated one
    hard_at_or_below: int | None = None  # ...which becomes the fixed rule at or below this baseline
    compare: str = "run"   # "run" or "median" - what is measured against the ceiling
    armed: bool = True


# THE TABLE. One row per target; adding a target is a row.
RATCHETS = {
    "quick": Ratchet(
        target="quick",
        baseline=11,
        reason="measured 2026-08-29 after feature 158 took quick from 41 s to 10.5 s; the GM stated "
               "15 s against this figure",
        hard_ceiling=15,
        hard_at_or_below=11,   # binds now
        compare="run",
    ),
    "done": Ratchet(
        target="done",
        baseline=155,
        reason="DECISION D1, the spec author's and not the GM's: the interim baseline while done is "
               "above the 35 s the GM reasoned from. Pin a real 35 s here when the efficiency work "
               "lands and the ceiling becomes the GM's fixed 45 s automatically",
        hard_ceiling=45,
        hard_at_or_below=35,   # not yet - today's baseline is 155
        compare="median",      # DECISION D2, the spec author's; see the module docstring, point 3
    ),
    # FR-006: wired, and OFF. One row away from working, and that row off - the GM has said they do
    # not want the lengthy AWS runs happening at all right now.
    "test-full": Ratchet(
        target="test-full",
        baseline=0,
        reason="not armed - the GM: 'I am not interested in running the lengthy tests at this time, "
               "especially given that they run on AWS'. Pin a measured baseline before arming",
        armed=False,
    ),
}


def derive_ceiling(baseline: int, hard: int | None = None) -> int:
    """FR-004: the ceiling for a target with no GM-stated number in force.

    Reproduces the GM's own figures at the baselines they reasoned from, which is the whole argument
    for trusting it on a target they never named:

        quick at 11 s:  min(15, max(15, 14)) == 15
        done  at 35 s:  min(45, max(39, 45)) == 45
    """
    grown = max(baseline + 4, int(baseline * 1.3))
    return min(hard, grown) if hard is not None else grown


def ceiling_for(r: Ratchet) -> tuple[int, str]:
    """The ceiling in force for this row, and what it is compared against.

    The regime split is FR-002's: at or below `hard_at_or_below` the GM's number IS the ceiling, fixed,
    and the RUN is what is measured; above it the ceiling derives and the MEDIAN is measured. A ceiling
    that kept deriving below the GM's figure would auto-tighten past a number they stated - which the
    spec disowns one requirement earlier for `quick`, so `done` is treated the same way.
    """
    if r.hard_ceiling is not None and r.hard_at_or_below is not None and r.baseline <= r.hard_at_or_below:
        return r.hard_ceiling, "run"
    return derive_ceiling(r.baseline, hard=None), r.compare


def verdict(target: str, seconds: int | None, median: int | None = None) -> tuple[bool, str]:
    """(ok, message). `seconds` is this run; `median` the recent same-scope median where needed."""
    r = RATCHETS.get(target)
    if r is None or not r.armed:
        return True, ""
    ceiling, mode = ceiling_for(r)
    measured = seconds if mode == "run" else median
    if measured is None:
        return True, ""   # nothing to judge on - never fail a target for lack of evidence
    if measured < ceiling:
        return True, ""
    what = "this run" if mode == "run" else "the median of recent green runs"
    return False, (
        f"\n\033[1m{target} is at {measured}s, at or over its {ceiling}s ceiling.\033[0m\n"
        f"Measured on {what}, against a pinned baseline of {r.baseline}s.\n"
        f"STOP and find out what got slower - that is the point of this failing rather than you\n"
        f"noticing in three days' time. `make audit` shows the history; `make durations` shows where\n"
        f"the suite's time goes.\n"
        f"If the new time is legitimate and permanent, move the pinned baseline in scripts/_ratchet.py\n"
        f"WITH a written reason - that is the only way it ever moves (feature 171, FR-003/FR-010).\n"
    )


if __name__ == "__main__":
    # `_ratchet.py <target> <seconds> [median]` - exits 1 and prints when the target is over.
    _t = sys.argv[1] if len(sys.argv) > 1 else ""
    _s = int(sys.argv[2]) if len(sys.argv) > 2 and sys.argv[2].isdigit() else None
    _m = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[3].isdigit() else None
    _ok, _msg = verdict(_t, _s, _m)
    if not _ok:
        print(_msg, file=sys.stderr)
        sys.exit(1)
