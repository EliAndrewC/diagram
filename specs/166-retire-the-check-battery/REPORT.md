# Feature 166 - what was done, and what it cost

## The request

> *"we have placement algorithms, which in theory should not be buggy, but then the automated checks
> essentially catch bugs as they slip through and then fix them on the maps ... if a check catches
> something, that just means that our placement algorithm is bugged."*

and, after the first census came back with a smaller answer than expected:

> *"I'd be really, really surprised if our win is actually only eleven checks ... can you describe to
> me a single category of automated check which should still exist?"*

No category survived that question. The GM then said: *"Go ahead and implement that. Get rid of check
village."*

## What is gone

| | |
|---|---|
| `l7r/diagram/check_village/` | 1,371 segments, 18,830 lines |
| `tests/check_village/` + the two tier copies | the negative-fixture suites |
| `pool/regressions/` | 107 frozen bad manifests |
| tools | `check_census`, `firing_census`, `make_regressions`, `site_justice`, `new_check` |
| Makefile targets | `gate-manifest`, `regressions`, `new-check`, `site-justice`, `check-census`, `firing-census`, `firing-census-suite` |
| **total** | **339,536 lines across 215 files** |

## What survived, and why each

- **`l7r/diagram/overlap/`** - the overlap taxonomy and matrix, MOVED into the engine. It is not a
  check: it is the engine's own classification of which features may share ground, and keeping it
  inside the battery meant the placer's doctrine was stored in the thing that audited the placer.
  102 classified keys; 27 modules re-pointed.
- **All 142 rules**, each re-homed as a placer unit test, a seed test on a cached roll, a static test,
  or a recorded DROP. `migration-record.md` is the ledger - 145 rows, verified mechanically: the live
  pin minus the names the table covers is empty.
- **Mode A's automated checks**, untouched and explicitly protected in the docs, on the GM's own
  instruction: a compound plan is placed by a person, so there is no placer to fix.

## The one behavioral change to the engine

`generate()` no longer gates. A roll's self-report is `farmhouses_reach_a_way` and nothing else - the
one property no placer can promise in advance, because reachability depends on fabric that does not
exist when the seats are chosen. No manifest moved: `make verify` reports *"maps whose manifest
changed: none"*.

## Four things worth the GM's attention

1. **A stale pin, found and verified before deletion.** `COHORT_BASELINE` held seed 24 against
   `paddy_bunds_clear_the_supply_channels`. Rolled it and put it through the battery one last time:
   EMPTY verdict. The defect had been fixed and the pin went on excusing a seed that no longer needed
   it - the exact "STALE PIN ... Blocking" case `baseline_verdict` exists to catch, unnoticed because
   the 24-seed cohort runs only under FULL and the idle runs.

2. **My first draft of the supply-bank test was WEAKER than the rule it replaced.** It sampled ring
   corners and fired on the centerline; the rule walks each edge at a 3 px step and fires at the band
   plus the abutment. Caught by reading the retired predicate rather than its name, which is why every
   row of the ledger was earned that way.

3. **Two unit slips, both caught by measuring rather than re-reading.** `theta` on a dry plot is in
   RADIANS (compared in degrees it called all 24 adjacent pairs identical and nearly reported a defect
   that is not there); a notice board's `rot` is PARALLEL to the way it faces, not perpendicular. Both
   corrections are recorded in the tests, not just fixed.

4. **A rule asserted against the wrong map passes on an empty list for ever.**
   `field_ditches_reach_source_and_sink` judges laterals, and only Kuwabata lays any - 6 of them, every
   tip within 0.16 px of its trunk. Asserted against Inashiro it would have been silent for ever. The
   test rolls Kuwabata and says why.

## What this changed about the loop, measured

The battery ran INSIDE every roll - `generate()` gated the manifest it had just finished - so every map
the project has ever produced paid for it. The bookends say what that cost:

| | 166-start | 166-end | |
|---|---|---|---|
| seed 4 | 46.8s | 14.0s | **-70.1%** |
| seed 25 | 28.2s | 15.7s | -44.3% |
| seed 39 | 21.0s | 12.7s | -39.5% |
| seed 47 | 25.3s | 15.3s | -39.5% |
| **total** | **121.3s** | **57.7s** | **-52.4%** |

Band 0: no increase on the total or on any seed, so the review ladder owes nothing. **Generation is
twice as fast**, and the reference-scope gate is 36 s.

That number is the GM's own argument arriving as arithmetic: the checks were not free insurance running
beside the generator, they were half of what the generator cost, re-establishing on every map a set of
facts the placers already guarantee.

## What is NOT done, and is the GM's call

- The town, city and capital tiers have no scripted generator, so their rules were dropped rather than
  migrated. When a tier converts, its rules belong to its generator's tests - not to a restored battery.
- `pool/legacy-hand-authored-pool/`'s 18 frozen exhibits were never gated by this path and are
  unaffected.
