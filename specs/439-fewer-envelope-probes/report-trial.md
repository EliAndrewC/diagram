# Trial 439 - fewer envelope probes: what it found, and what it cost (with feature 438, the tooling it used)

For the GM, as feature 437's report was laid out. Wall clock UTC from commit times (`git log --format=%cI`), the review agents'
reported durations, and the runs' own clocks; `make feature-report F=438` / `F=439` for the split. A WAIT is time spent on a
review, a gate or a roll; "overlapped" means work went on beside it.

## What it found

- The growth's seat search builds 803 full envelopes for 40 houses at seed 25, 40 households - 22% of the homesteads stage
  under cProfile; 95% serve seats never used. A perfect screen would save about 10.6% of the roll (measured ceiling,
  `research/funnel.md`); no cheap test predicts the placer's refusals.
- The spike on the search's re-rolls (each settle from the widest reach seen) halved the envelopes and cut its own stage 11%
  under cProfile - and made the roll 17% slower, because the wider seating more than doubled the web's work
  (`research/spike2.md`). Set down and reverted.
- The lesson for the next search trial: a change to how a search tries candidates changes the settlement every later stage
  works on, so it is judged on the whole roll (`make perf-ab`) and the stages after it (`make perf-fanout`), never its own stage.
  Feature 437's other named searches and the "fewer, larger questions" form remain untried.

## What it cost

### Feature 438 - the trial form and `make perf-share` (21:16:26 to 22:05:17, 49 min)

`make feature-report F=438`: tools 23 min (the landings' gates), thinking 15 min, quick tests 5 min, spec reviews 5 min waited,
other subagents 3 min.

| # | step | start | end | took | kind |
|---|---|---|---|---|---|
| 1 | claim, request, spec | 21:16:26 | 21:16:56 | 30 s | work |
| 2 | spec review, round 1 (CHANGES REQUIRED, 4 items) | ~21:17 | ~21:21:30 | 270 s | WAIT (overlapped: perf-share and the template drafted) |
| 3 | round 1 applied; a stale-terms false positive re-dispatched | ~21:21:30 | 21:22:07 | ~40 s | work |
| 4 | spec review, round 2 (FAITHFUL) | 21:22:07 | ~21:23 | 43 s | WAIT |
| 5 | plan and tasks; a figure label the plan check asked | ~21:23 | 21:23:33 | ~30 s | work |
| 6 | plan review (CLEAR) and the two tasks' preflights (CLEAR) | 21:23:33 | ~21:26 | 70 s + 35 s | WAIT (overlapped: T01 built) |
| 7 | T01: perf-share, the size in the profile name, tests, the real run | ~21:23:33 | 21:24:47 | ~1.2 min | work |
| 8 | T02: the template, make trial, the gate's clause and its 4 cases, the docs; quick re-run once (its 15 s ceiling under load) | 21:25:01 | 21:37:45 | 12.7 min | work |
| 9 | claims round (impl-drift x2) | 21:37:45 | 21:38:59 | 1.2 min | WAIT |
| 10 | landing 1: make done, the landing cohort - then refused at its end on a claim never dispatched | 21:39:01 | ~21:58 | ~19 min | WAIT, wasted |
| 11 | the claim checked, a comment fixed, landing 2 | ~21:58 | 22:05:17 | ~7 min | WAIT |

Work about 17 min, waits about 32 min - 19 of them the landing that ran to its end before refusing.

### Trial 439 (22:05:50 to 22:24:28, about 19 min)

`make feature-report F=439` before the review: thinking 4 min, tools 1 min.

| # | step | start | end | took | kind |
|---|---|---|---|---|---|
| 1 | target read off 437's profile, `make trial`, the brief (the approval guard refused once: the template's placeholder approval line) | 22:05:50 | 22:07:22 | 1.5 min | work |
| 2 | measured: perf-share (1 s); a 40-household roll for its counters - `make hamlet` refuses the size, a cohort keeps no counters (two dead ends, 13 s); the funnel from the profile's call counts; spike 1, the refusals by reason (profile 29 s) | 22:07:22 | 22:10:32 | 3.2 min | work, WAIT 43 s |
| 3 | evidence, the pushes (unreviewed, as the trial form allows), the first verdict | 22:10:32 | 22:11:12 | 40 s | work |
| 4 | the one review (CHANGES REQUIRED: the verdict did not follow the rule, the ceiling a guess, the time missing) | 22:11:12 | ~22:15:30 | 260 s | WAIT |
| 5 | the ceiling measured; spike 2 and its measurement (perf-ab 37 s, profile 8 s, two fanouts 20 s each) | ~22:15:30 | 22:18:00 | 2.5 min | work, WAIT ~1.5 min |
| 6 | evidence, verdict and this report written | 22:18:00 | 22:19:30 | 1.5 min | work |
| 7 | the review's second round (CHANGES REQUIRED, one wording item), the rewording, the round arbiter's accept | 22:19:52 | 22:24:28 | 202 s + 37 s | WAIT, work ~1 min |

Work about 9 min, waits about 10 min (the two review rounds and the arbiter about 8.3 min of them). Against feature 437 (17 min, three spec rounds and an arbiter ruling before any verdict),
the trial form let the evidence be pushed as it was measured, with no review until the end.

## What the times point at

| step | improvement, and what it would save |
|---|---|
| 438 #10 (19 min) | `make land` asks the claims gate's "owed, none in flight" BEFORE the gate runs, not after it: a claim no one has dispatched cannot come while the gate runs. About 19 min each time it happens (it happened here through my slip; the tool would have caught it at once). |
| 439 #4 and #7 (260 s, then a round) | The trial's one review found the verdict did not follow the brief's rule - the author misread their own rule. The template could ask for the verdict as "the branch taken, and the measurement that took it", so the brief states it and the review checks it. About one review round (4 min) a trial. |
| 439 #2 (dead ends, a counting spike) | A 40-household roll's seat counters on record: `make perf-profile` could write `meta.seat_search` into its `.placed.json` beside the counts it already writes. About 2 min and a spike a seating trial. |
| 439 #5 (two fanouts, a worktree) | `make perf-ab` could print each stage's time beside the total (its worker already has them): the +17% would have named the web at once. About 1 min a trial, and the cause seen in the same table. |
| 438 #8 and 439 #1 (snags) | `make trial APPROVED="<the GM's words>"` writes the approval line, so the approval guard does not refuse the brief's first commit (30 s); the stale-terms guard skips lines the same diff rewrote (two false positives this session, 30 s each); quick's 15 s ceiling failed twice under load (about 1 min each). |
