# 196 - Warm and cold ratchets

**Status**: draft, round 3
**Request**: [request.md](request.md) (the GM's words, verbatim)
**Rests on**: `specs/191-refusals-that-tell-the-truth/research.md` R5 and R7 (192's `research.md` does
not exist; the round-1 draft cited it and was wrong)

## Why

`make done`'s cost is bimodal on ROLL-CACHE STATE, and the ratchet medians over both populations, so
the number it judges describes neither. **The run log records no cache state today** - that is what
FR-001 adds - so the classification below comes from this session's own instrumented gate logs, where
the `[HIT]`/`[MISS]` line was captured:

| cache | runs (seconds as the run log records them) | how classified |
|---|---|---|
| **warm** (`[HIT]`) | 379 | this session's instrumented gate log |
| **cold** (`[MISS]`) | 522, 544, 610, 651 | this session's instrumented gate logs |
| **cold, INFERRED** | 549 (2026-09-06 13:50) | this session's own run on `b24f4fef`, taken between a cold 610 and a warm 379 while `hamlet_floor`/`scatter_audit` were being edited - a roll-cache invalidation. No `[HIT]`/`[MISS]` was captured, so this is inference, labeled as such |
| **not usable** | 388, 549 (09-05), 620 | 388 and the older 549 are other sessions' runs (added by `6d91e96e1` and `f8e932fa9`); **620 is `"result": "failed: test-full"`**, so it is outside every median by construction |

**Cold median 549, ceiling 713.**

**THIS POPULATION HAS NOW BEEN CORRECTED THREE TIMES, EVERY TIME IN THE PERMISSIVE DIRECTION, and
that is the reason the number is disclosed as session-pinned rather than presented as measured**:
round 1 wrote "525, 546, 651" (seconds in no run log) and called their median 550 (it is 546); round 2
wrote 577 over four runs, missing the 549 that belongs in the set and wrongly counting 388, another
session's run, as evidenced warm. Each error made the bar looser. The warm class rests on a SINGLE
evidenced run (379) against the GM's ratified 400.

The last twelve green runs spread **379-895 s (2.4x)**. Against that, a single median crossed a 520 s
ceiling by 2 s and blocked a landing whose own delta REMOVED eight tests. Two candidate causes were
tested and refuted - 41 newly-landed tests (3.4 s total) and cache state (both compared gates were
cold) - so the ratchet was not detecting a regression.

**The 400 s baseline the GM ratified is the WARM figure**, and the one warm run this session can
evidence (379 s) agrees with it. That is a sample of ONE, which is why FR-003 leaves 400 alone rather
than re-deriving it.

**WHAT THIS DOES NOT FIX, disclosed because the research this feature cites says it.** R5 records a
**2.2x hardware-driven variance independent of cache state** (P/E cores, self-contention) and warns
that a `compare="median"` ratchet *"will fire on an unlucky cluster with no regression present"*.
Post-192 a cold floor phase costs ~114 s, which cannot produce a 379-895 spread on its own. So the
split addresses the cache-state component ONLY; contention variance survives it, and the same
"no regression" diagnosis loop can recur inside a class. If it does, that is the next feature, not
evidence that this one failed.

## Requirements

- **FR-001** A run-log entry records the roll-cache state: `warm`, `cold`, or the field absent when
  unknown. The tell already exists - `_reference` prints `[HIT]`/`[MISS]` - so this captures a fact
  the run already established.
- **FR-002** `_gatecost.median_seconds` can be asked for one class. An entry with no cache field is
  excluded from a class query: it cannot be classified, and guessing would put cold runs in the warm
  population, which is the defect being fixed. **The class filter is applied BEFORE the `RECENT = 25`
  slice**, so "recent" means the last 25 runs OF THAT CLASS; filtering after the slice would give a
  sample that shrinks as the other class gets busier.
- **FR-003** `_ratchet` carries a baseline per class and judges a run against its own class:
  **warm 400 s** and **cold 549 s** (ceilings derive as today, x1.3: 520 s and 713 s).
  - **`baseline` MUST NOT DISAPPEAR.** `scripts/check-run-plausible.py` reads
    `RATCHETS[target].baseline` via `getattr(..., None)` to derive the dry-run floor at 10%, and
    `check()` returns OK when that floor is `None` - so replacing the field with two new ones
    silently switches off the guard added on 2026-09-05 after a `make -n done` minted a push
    credential. `baseline` stays and remains the WARM figure; the cold one is additive.
  - **549 is a number THIS SESSION measured and pinned**, not one the GM ratified. Feature 192's
    FR-006 requires saying so, after this session pinned 385 from a fresh median (`e5283ca9`) and
    reverted it (`07bcdfa2`). If a fuller sample moves it materially it goes back to the GM.
  - **Each class carries its OWN written reason** (feature 171 FR-010). `test_ratchets.py:107`
    asserts `r.reason` per ROW, so a second baseline would inherit a reason that is not about it and
    the test would still pass - the property would be gone while the test stayed green.
- **FR-004 - BELOW SAMPLE, THE GUARD STAYS LIVE.** This is where the round-1 draft failed and the
  failure is recorded because it is the whole risk of this feature. That draft said an unjudgeable
  run PASSES; measured, **0 of 507 existing entries carry the cache field**, so both classes start
  empty and `make done`'s ratchet would have passed unconditionally for hours to over a week - the
  guard whose motivating failure was a 4x slowdown going unnoticed, switched off by the feature
  claiming to repair it. Instead: while a class has fewer than **5** runs, the RUN ITSELF is judged
  against that class's ceiling - so nothing is unjudged, no backfill is needed, and no population is
  mixed. Once the class reaches 5 the median takes over, which is feature 171's regime for this
  target. Where the class is UNKNOWN rather than merely below sample, the next bullet governs.
  - **AN UNKNOWN-CLASS RUN IS JUDGED AGAINST THE WARM (STRICTER) CEILING, never passed.** The round-2
    draft claimed *"the run's class is always known"*, which contradicted FR-001's "absent when
    unknown" one screen earlier - and the contradiction was load-bearing: `REF_OK` (`Makefile:132`)
    skips `_reference` entirely, so no `[HIT]`/`[MISS]` exists, yet the gate still reaches `LOGRUN
    green` and the ratchet. An unknown class with no rule is round-1's defect arriving by a side
    door. `REF_OK` has zero recorded uses, which is exactly the shape feature 169 warns about: an
    escape nobody was thinking about silently switching off a second guard.
  - **FR-004 SUSPENDS A GM-RATIFIED DECISION for the first five runs of a class, and says so.**
    `_ratchet.py`'s `done` row records `compare="median"` as *"D2, RATIFIED BY THE GM 2026-08-30"*,
    on the measured ground that *"a per-run bar would fire on 28% of NORMAL runs"*. What makes a
    per-run bar tolerable here is the split itself: **0 of the 5 cold runs exceed 713, and the 1
    evidenced warm run does not exceed 520**. The 28% figure was measured over a MIXED population,
    which is the thing this feature removes.
- **FR-005** The GM's hard ceilings are untouched: `hard_ceiling=45` at `hard_at_or_below=35`.
  **The WARM baseline drives that trigger** - the 35 s regime is one where the gate rolls nothing
  expensive, so it is the warm figure that could ever reach it.
- **FR-006** Tests: the existing ratchet suite keeps passing AND gains cases for the split - a cold
  run judged against the cold ceiling, a warm run against the warm one, an unclassified entry
  excluded from a class median, the below-sample path judging the RUN (not passing), and a per-class
  reason assertion that fails if a class has none.
- **FR-007 - the search space, for BOTH the `baseline` field and the CLASS.** A census that stops at
  `_ratchet.py` is this project's recurring failure, and the class has a longer chain than the field:
  an implementation can satisfy every other FR and still never get the class as far as the ratchet.
  - `baseline`: `scripts/check-run-plausible.py` (reads it via `getattr`),
    `tests/tooling/test_run_plausible.py:78`, `tests/tooling/test_ratchets.py:76,78`.
  - the CLASS: `LOGRUN` (`Makefile:785`) and its FOUR invocation sites - 118 (`already-verified`),
    129 and 146 (`failed:`), 161 (green); the first three run WITHOUT `_reference` and must not emit
    a class. `Makefile:171-172`, where the class must reach BOTH `_gatecost.py` and `_ratchet.py` -
    the single most load-bearing edit, because missing it makes the whole feature inert.
    `_gatecost.py`'s `__main__` slice `median_seconds(*sys.argv[1:3])`, which needs a third
    positional. Two callers that must keep working CLASSLESS: `scripts/make-only-hooks.sh:81` and
    `Makefile:661` (`make audit`). And `tests/tooling/test_ratchets.py:141-171`, whose fixture entries
    carry no cache field and which asserts the classless median still returns 100.

## Decisions Recorded

- **D1 - the cache state is CAPTURED, not inferred, and the marker is PER-RUN.** `_reference` prints
  the verdict; it writes it where the run-log line can read it. **The marker must be cleared at the
  gate's `T0`**: `REF_FIRST` (`Makefile:307`) runs `_reference` from other targets too, so a marker
  left by a 10:00 `make maps` could classify an 11:00 gate. Under FR-004 that no longer merely skews
  a median - it decides which ceiling judges the run, so absent must mean absent and never inherited. Priced alternative: re-deriving it at log time by asking the
  roll cache again - a second source of truth, answering for the wrong moment.
- **D2 - unclassified entries are EXCLUDED, not defaulted.** Defaulting to `warm` would drop every
  historical cold run into the warm population and recreate the defect; defaulting to `cold` would
  loosen the warm bar. Excluding cannot lie. **This is affordable only because of FR-004**: with the
  round-1 draft's below-sample rule, excluding meant disarming.
- **D3 - a run is excluded from the cold baseline when ITS OWN TREE lacks feature 192's
  `_stores_under_bypass`**, not by timestamp. Four runs are excluded on that rule: **803, 806, 873**
  (pre-fix), and **895** - which post-dates the fix by six hours on the clock but ran from a
  191-session clone (`536dbf56`) whose tree did not carry it. The round-1 draft said "the 804 s run";
  there is no 804 in the log, and a timestamp rule would have admitted the 895.
- **D4 - this does NOT re-pin the warm baseline.** 400 s stands; measured warm runs agree with it.
- **D5 - the warm class rests on ONE evidenced run, and per-run judging makes that SHARPER, not
  safer.** The round-2 draft claimed below-sample judging made a mis-set warm baseline "survivable";
  the opposite is true - if a warm run genuinely costs 549 s, a per-run bar at 520 fails it on the
  FIRST such run, sooner and harder than a median over five would. That is the correct behavior and
  the honest statement of it is FR-003's own rule: if the warm figure turns out wrong, 400 goes back
  to the GM. It is their ratified number and this feature does not move it.

## Out of scope

- The gate's COST (feature 192's territory) and the contention variance R5 records.
- Other ratchet rows. `quick` rolls no map, so it has no cache regime.
- **A run that FAILS the ratchet is still logged `green` before the ratchet runs**, so it feeds the
  median that failed it. Feature 192 recorded this deliberately; it carries over unchanged and now
  matters per class. Not changed here.

## Success Criteria

- **SC-001** A cold `make done` is judged against the cold ceiling and a warm one against the warm
  ceiling, from the FIRST run after landing - by the run itself while the class is below sample, by
  the class median once it reaches 5. The run-log entry records which class it was.
- **SC-002** The below-sample path JUDGES rather than passes - proven by a test that a run over its
  class ceiling fails while that class holds fewer than 5 runs. This is the path that could have
  disarmed the guard, so it is asserted rather than assumed.
- **SC-003** An entry with no cache field never enters a class-specific median - proven by a test.
- **SC-004** `RATCHETS["done"].baseline` still exists and `check-run-plausible.py`'s dry-run floor is
  still derived from it - proven by a test, because losing it restores the 2026-09-05 defect.
- **SC-005** *Expected consequence, not an acceptance test* (the form feature 192's SC-005 used):
  feature 195's 651 s cold run is under the 713 s cold ceiling, so the split should let it land. It
  is stated to be checked, not to be achieved - a criterion that REQUIRES a particular landing is the
  pressure that bends a calibration number, which is how the round-1 draft's 550 came about.
- **SC-006** `make done` green, 100% coverage held, `make hooks-test` green.

## Review history

- **Round 1 (`spec-fidelity`): CHANGES REQUIRED**, twelve items, all accepted - and the verdict was
  right on the substance. **The draft would have DISARMED the ratchet**: 0 of 507 run-log entries
  carry a cache field, so both classes start empty and its below-sample rule passed everything, for
  hours to over a week. Its SC-004 said feature 195 would pass *because* 651 < 715 when it would have
  passed because nothing judged it - the reverse-engineered-outcome shape the review was asked to
  hunt for. The cold baseline's evidence was wrong (seconds that appear in no log, a median that was
  not the median, five of eight relevant runs) and too LOW: 577, not 550. The citation pointed at a
  `research.md` that does not exist; the Why claimed the run log records cache state one screen above
  the requirement that adds it; D3 excluded "the 804 s run", which is not in the log, on a timestamp
  rule that would have admitted the 895 s run whose tree lacks the fix; the per-row `reason` test
  would have passed with the property gone; and the search space missed
  `scripts/check-run-plausible.py`, whose dry-run floor reads the very field being changed. The
  reviewer also supplied the fix adopted in FR-004 - judge the RUN against its class ceiling while
  the class is below sample - which keeps the guard live from the first run and needs no backfill.
- **Round 2 (`spec-fidelity`): CHANGES REQUIRED**, seven items, all accepted. Two were substantive
  and both are failures of MY evidence rather than of the design. (1) **FR-004's "the run's class is
  always known" was false and contradicted FR-001**: `REF_OK` skips `_reference`, so an unknown-class
  run reached the ratchet with no rule - round-1's disarmament by a side door. Now judged against the
  warm ceiling, with the marker required to be cleared at `T0` so a stale one cannot classify a later
  gate. (2) **The population was wrong for the third time**: 620 is not green and cannot enter any
  median; the 09-06 549 is THIS session's run, not another's, and belongs in the cold set; and 388,
  which I counted as evidenced warm, is feature 194's session's run. Cold median 549 and ceiling 713,
  not 577/750 - loose by ~37 s. The reviewer also caught that FR-004 suspends the GM's ratified
  `compare="median"` without naming it, that D5's mitigation was backwards, and that the search space
  covered the `baseline` field but not the CLASS chain, which is the part that would have made the
  feature inert.
- **Round 3**: pending.
