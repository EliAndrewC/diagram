# Feature 437 - the array geometry trial: what it found, and what it cost to find

For the GM (FR-006). Measured 2026-10-27, seed 25 at 40 households, the host shared with other sessions.

## What it found

1. **The shared geometry layer holds little of the time** (`research/share.md`). Across the four largest stages (homesteads,
   web, field, hinterland: 10.4 s under cProfile), the functions of `settlement/_geom/primitives.py` take 0.36 s of their own
   time - 3.5% (2.5%, 5.7%, 0.9%, 6.3%). Made free, they would save a few percent. The time has no hotspot: the largest
   single function in any of the four is 3.6% of its stage; the rest is hundreds of loops, `dict.get`, `min`/`max` and
   shapely's unions. T57's "two thirds of the calls are scalar comparisons" counted calls, not time.
2. **Asking the predicate as an array made its caller slower** (`research/spike.md`). In `seg_dist`'s hottest caller, the
   wood-share corridor test, the array form ran 2.3 times slower (the seat test alone) and 2.6 times slower (both uses, FR-002
   whole); the roll moved +2% and +3%, inside the quick form's -4% floor. Each call asks about ten seats: numpy's per-call
   cost is more than ten scalar distances, and the scalar loop's early exit is lost. Both spikes were set down and reverted.
3. **The extrapolation** (labeled: from one caller and one profile set): vectorizing the shared layer predicate by predicate
   cannot approach an order of magnitude - its ceiling is a few percent, and per call it costs more than it saves. An array
   form pays only where one call asks many candidates, which here means restructuring a search so it asks far fewer, larger
   questions - a change to the callers (how many candidates each search tries, and how it asks them), not to the predicates.
   That is where an order of magnitude would have to come from: the searches the profiles name as the largest self time -
   `boundary._samples`, `gap_ways.flood`, `route.lattice_search`, the fixture seats (`_first`, `within_reach_of`) - read with
   the plan template's "search smell" question.

## What it cost

From the GM's request to this report (the step log is partly reconstructed - `process-clock.md` marks which rows): the session's first command 20:54:02, this report 21:11 (about 17 minutes of wall
clock). `make feature-report F=437` splits the session's own time (from the event log):

| category | time |
|---|---|
| the session's own work and thinking | 9 min |
| waiting on spec reviews (verify rounds) | 4 min |
| waiting on background runs (profiles, A/Bs, call counts) | 2 min |
| tools and tests | 3 min |

Beside it, counted apart: the review agents' own time - spec-fidelity 3 min (1 pass), spec-fidelity-verify 7 min (2 passes),
the round arbiter 2 min - mostly overlapped with the session's work. The step-by-step log is `process-clock.md`.

| step | took | improvement it points at, and what it would save |
|---|---|---|
| spec and its review rounds (3 rounds and the arbiter) | about 12 min of reviewer time, 4 min waited | A TRIAL FORM: measure first under a one-paragraph brief, then write the spec on the fixed evidence and review it once. The rounds kept finding things because the evidence files (the clock, the spike) changed beside the spec, so each round read them a step behind (the arbiter's reading). About 8 min of review and 3 min of waiting a trial. |
| the clock log kept by hand | about 5 min, and one review round's findings | `make feature-report` already splits a feature's time from the event log; a step mark (`make clock STEP="..."`, an event the report reads) would replace the hand-kept table. About 5 min a feature that reports its time. |
| reading the profiles (two ad-hoc scripts) | about 3 min | A `make perf-share MODULE=<path> STAGES=<list>` reading the raw profiles already kept (`dev/perf-raw/`): a module's share of each stage and its callers. About 3 min an investigation, and the search space right the first time. |
| measurements: 6 profiles (29 s each), 2 quick A/Bs (38 s), 2 call counts (55-60 s) | about 5 min, mostly overlapped | `make phase-calls` counts the whole roll; `make perf-fanout STAGES=<stage>` already counts one stage's calls, so the trial should have used it - no build, about 40 s a count. |
| landing | none - the spikes were set down | Had a spike landed: `make done` (about 3 min), `make cohort-landing` (about 2 min), a claims round (about 1 min). None seen to cut for a trial. |

One process note: the spikes were written and measured before a plan was written - a trial set down by FR-005 never reached
one. For a trial that is the right order (measure, then decide), and the trial form above would make it the rule.
