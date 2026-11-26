# M11 - what the spec-kit task route adds over a direct tweak (measured 2026-11-26, read-only)

Tree: origin/main at 248d6f919f. Sources: the builders', reviewers' and coordinating session's transcripts
(~/.claude/projects/-diagram/c6fd72d1-.../), the session clone's event log (.git/l7r-events/451-*.jsonl),
`make task-time SINCE=72h` (the binary already built, L7R_GATE_STALE_OK=1; output m11-tt72.txt), git log on origin/main,
.git/land-tooling-steps.jsonl. Scripts: m11-decomp.py (+ m11-main.py), m11-timeline.py, m11-tt-small.py, m11-direct.py,
m11-direct-min.py.

## Selection
"Small" = the landing commit changes one to three source files outside specs/, dev/ and docs (a source file's own tests
file counted with it): 451 T252 (1), T263 (1), T267 (2 + tests), T268 (2 + tests), T269 (2 + tests), T270 (2 + tests),
T271 (1 + tests + one brief line), T272 (1 + tests + a hook suite) - n = 8, landed 2026-11-25 23:43Z to 2026-11-26 14:33Z.
All eight are tooling (guards, gate crates, hook suites); none is engine code or a research claim's code.
Out: T253 (40 files), T254+T255 and T256+T257 (one commit a pair: 26 and 15 files, git cannot split them), T258, T259,
T265, T250, T251 (wide or record work). Shown beside as "wider": T248 (4 files), T249 (8), T262 (7).
Anomalies kept in, flagged: T270's first landing ticked it without its code (the carry-over cherry-pick stood unfinished
on a tasks.md conflict; a second run pushed the code); T272's tick was reverted and redone and its landing re-run for an
owed ledger row; T252 ran no background closing-checks run in its builder (its f is 0.4 min; it is not a solo-run
control) and, with T271, has the route's own commands as its SUBJECT, so some of its code work is booked to f or d.

## Conventions
- Builder's clock: each gap between consecutive transcript lines is booked to the step of the line that ends it (the
  model's turn to the tool it calls, a tool's run to that tool, a stopped wait to the closing checks when they were in
  flight, else to what woke it). It sums to the builder's elapsed time. Booking a wait to f whenever f is in flight is a
  CONVENTION: it is what makes the plan review cost no wall clock here.
- Weighted tokens = fresh input + 0.1 cache read + 1.25 cache write + 5 output (the 2026-11-25 context-cap weights, assumed).
- The coordinator's turns are booked to a task only where a tool call NAMES it (or the turn follows its builder's wake);
  its text-only turns and turns naming more than three tasks are not booked - a lower bound.
- 2026-11-26's seven tasks ran two or three builders at once: the closing checks' minutes are inflated against a solo
  run, so f's share is high and c+d's share of the clock would be higher solo.

## The decomposition, medians over the 8 small tasks (ranges in Table 1)

| step | who | median min (clock) | share of builder clock | median weighted tokens (k) | a direct tweak |
|---|---|---|---|---|---|
| a filing (task-add, task-start, tasks.md line) | builder + coordinator | 0.2 + 0.0 (0.0-4.1) | 3% | 16 + 15 | SKIPS |
| b reading, writing and running code and tests | builder | 9.0 (5.0-15.5) | 24% | 491 | keeps |
| c the plan section | builder | 0.7 (0.5-1.1) | 2% | 52 | SKIPS |
| d make decide + plan review (MODE 4), re-rounds | builder; reviewers beside | 0.9 own (0.1-1.3 clean; 6.3 T271 is subject pollution, 6.9 T272 a wait with no identified waker); reviewers 2.8 machine min (0.9-9.3) | 5% | 55 + 98 reviewers | SKIPS |
| e claims steps | builder | 0.1 (0.0-0.3) | under 1% | 16 | keeps where the code carries claims (none did) |
| f closing checks (1-4 runs a task; a run 0.7-32.3 min, the longest of each task 15-32, T252 none) | builder waits | 28.8 (0.4-32.9) | 63% | 180 | keeps |
| g make land in the coordinator (gate, tick, push) | coordinator | 3.4 summed runs (0.8-6.0); 0.2 of its own turn | not on the builder's clock | 60 | keeps the gate and push; SKIPS the tick, the plan gate, the ledger rows a review owes (the second runs of T272 and T270: 1.3 and 2.1 min) |
| h coordinator: brief and dispatch / woken by the builder / commit, carry-over, worktree | coordinator | 0.1 / 0.2 / 0.2 | not on the builder's clock | 15 / 87 / 59 | keeps while a builder does it (the builder pattern's cost, agenda item 12); spec files are the carry-over's conflict surface (T269, T270: 226k and 102k tokens of conflict turns) |
| r the builder's report | builder | 0.4 | 1% | 89 | keeps while a builder does it |
| whole | | builder 42.9 (10.1-49.9); dispatch to landed 48; task-time 59 machine, 12 blocking | | 1,064 builder+reviewers; 342 coordinator (lower bound) | |

## Findings
1. On the clock the route's own steps (a + c + d) are about 2 minutes of the builder's 43 (5%), and the reviewer's 1-9
   machine minutes ran beside the closing checks: every wait a review ended was inside a closing-checks run. The
   counter-case is T268: its block arrived 2.4 min into the checks, the fix restarted them, and the checks ran four times
   (9.8, 15.1, 3.2, 0.7 min) - but that block was the one that changed the code.
2. In tokens the route is larger: filing 31k + plan section 52k + decide and review 153k = about 235k weighted a task,
   17% of the task's 1.4M (builder, reviewers, coordinator).
3. make task-time's own tables agree (Table 3): median 59 machine and 12 blocking minutes a small task; compile, tests,
   hook suites and gate 50% of machine minutes; plan review 6% (3.5 min) and 2% of blocking; the spec-kit step 1%.
4. Landing friction that only the task route has, 2 of 8: T272's landing re-run for an owed review ledger row and its
   tick reverted and redone; T270 ticked without its code over a tasks.md conflict (451 T292 was filed from it).

## What the plan review caught (11 rounds on the 8 small tasks; 4 more on the wider three)

| task | rounds | round 1 | class | changed the landed code? |
|---|---|---|---|---|
| T268 | BLOCKED, CLEAR | a script that ran, failed and printed nothing still got the empty "FAILED:" notice the task exists to fix | a real defect in the approach | YES - two source edits 10 s after the verdict, a test pinning it |
| T263 | BLOCKED, CLEAR | the census for sibling instances searched three patterns and could not see plain writes or other modes | a missing measurement | no - a wider search, the plan text restated, nothing found |
| T252 T267 T269 T270 T271 | CLEAR | - (T271: one non-blocking note on a grep's scope) | - | no |
| T272 | CLEAR, CLEAR | the second round was owed because the section moved after a closing-check fix | form (a re-round) | no |
| T248 (wider) | CLEAR, CLEAR | same: a re-round after test edits | form | no |
| T249 (wider) | CLEAR | - | - | no |
| T262 (wider) | no review agent booked to it | | | |

First round BLOCKED 2 of 8 (25%; 24.6% over the 301 tasks of dev/measurements/2026-11-25/reversals). Blocks that changed
the code that landed: 1 of 8 tasks. No block was on wording or on a found-and-left item's id. By timing (an inference:
an edit within a minute of a closing-checks notification), the closing checks forced a code or test edit in 4 of 8
(T268, T269, T271, T272).

## The direct route as it exists (Tables 4 and 5)
Since 2026-11-19: 1,608 commits on main, 218 of them ticks; 772 name no task, 630 of those are records only, and 27 touch
code-class files - 12 of them page sessions' glossary data. That leaves 15 commits = 10 taskless tooling changes: three
arbiter-ruled fixes, one make land-tooling landing (8 files; the one successful run in this clone's steps log: 344 s -
guard suites 154, checks 174, push 13), six plain fixes. Sizes: median 2 source files, 6-233 lines.
Minutes: first Edit to last commit 4, 5, 7 and 8 min for the four with a clean span (one more spans 181 min of other
work; five show no Edit event - shell edits). That is a LOWER BOUND and not like-for-like with the small tasks' 41 min
from first code edit to code commit: it leaves out the diagnosis (an arbiter's ruling had named the fix in three) and
the gate after the commit. The gate was not skipped: in each of the three windows with phase lines a make land ran its
gate phases (3-6 min), so these rode a landing. Two of the five timed changes needed follow-up commits for format, lint
or coverage (3 and 1). Comparability: weak - chosen because small and already diagnosed, mostly ruled on by the arbiter,
so not unreviewed.

## The estimated saving if a small task went direct
- Variant A, still built by a builder (skips a, c, d, the tick): about 2 min of the builder's clock (1-3), 3 reviewer
  machine minutes (1-9), about 235k weighted tokens (150-400k; 17%); wall clock 0-2 min where the review runs beside the
  checks, up to about 10 where a block or an owed ledger row re-runs checks or the landing (T268, T272), and the
  occasional landing accident (T270). Assumes the tweak runs the same closing checks and gate, as engine-code pushes do.
- Variant B, the coordinator makes the edit itself: also drops the brief, the wakes, the carry-over and the report (about
  250k more) - but that is the builder pattern's cost (agenda item 12), its turns are in a far larger context, and b and
  f would block the session. Not measured here.

## The risk given up
One small task in eight would have landed its own target defect in a path no test covered (T268) - the closing checks
were green on it. Across 449 and 451 the reversals measure classed 45 of 301 reviewed tasks' first blocks as a real
defect in the approach (15%).

## Not measurable from these records
The coordinator's text-only turns for a task (reports, reading a builder's reply); the GM's reading time; when a task
was filed (batch filings carry no per-task commit); the direct changes' diagnosis time and whether any regressed later;
a solo-run baseline for the closing checks; the value of the plan section as a record; the token weights are assumed.

## Which categories the data would and would not support routing directly (options, not a recommendation)
(i) Test-only flake fixes (T252, T263: the delta is one tests file): two tasks, one CLEAR and one block that changed no
code - the data supports a direct route here on risk, weakly (n=2), for about 2 minutes and 235k tokens each. (ii) Small
behavior changes to a guard or gate (T267-T272): the one code-changing catch sits here (1 of 6), on a path the tests did
not reach, and the review cost no wall clock beside the checks - the data does not support a bypass on risk, and offers
little time for it. (iii) Fixes an arbiter has ruled and tooling landed alone already go direct (10 since 2026-11-19),
still through the gate; 2 of 5 needed a follow-up commit. (iv) Engine code and research-claim code: no small sample
exists, so nothing here supports either way. (v) The route is not where a small task's time is: closing checks are 63%
of the clock and the route's own steps 5%; a route change buys tokens (17%), not minutes.

## Table 1 - the decomposition per task (m11-decomp.py; its g row is the BUILDER only - the coordinator lands, see its own table at the end and the land runs listed in the summary table above)

# m11: the builder's clock by step, per task (minutes; waits folded into the step waited on)

| task | builder elapsed | a | b | c | d | e | f | g | r | i | x | of it waits (b/d/e/f/g) | reviewers: n, machine min, verdicts |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T252 | 10.1 | 2.2 | 5.7 | 0.7 | 0.2 | 0.1 | 0.4 | 0.0 | 0.8 | 0.0 | 0.0 | f 0.3 | 1, 0.9, CLEAR |
| T263 | 42.9 | 4.1 | 15.5 | 1.0 | 0.1 | 0.2 | 21.8 | 0.0 | 0.3 | 0.0 | 0.0 | f 21.5 | 2, 9.3, BLOCKED/CLEAR |
| T267 | 43.8 | 0.0 | 8.4 | 0.6 | 1.3 | 0.1 | 31.6 | 0.0 | 0.4 | 1.3 | 0.0 | f 31.4 i 1.3 | 1, 1.5, CLEAR |
| T268 | 39.7 | 0.0 | 9.3 | 1.1 | 0.5 | 0.0 | 28.4 | 0.0 | 0.3 | 0.0 | 0.1 | f 27.7 | 2, 3.3, BLOCKED/CLEAR |
| T269 | 49.9 | 3.2 | 10.5 | 0.7 | 1.0 | 0.1 | 29.3 | 0.9 | 0.3 | 3.8 | 0.0 | f 28.9 i 3.8 | 1, 3.3, CLEAR |
| T270 | 43.9 | 0.3 | 8.8 | 0.5 | 0.7 | 0.3 | 32.9 | 0.0 | 0.3 | 0.0 | 0.0 | f 31.8 | 1, 2.7, CLEAR |
| T271 | 42.8 | 0.1 | 5.0 | 0.5 | 6.3 | 0.2 | 30.2 | 0.0 | 0.4 | 0.0 | 0.0 | f 30.0 | 1, 2.9, CLEAR |
| T272 | 41.9 | 0.1 | 11.0 | 0.8 | 6.9 | 0.1 | 22.6 | 0.0 | 0.4 | 0.0 | 0.0 | b 1.2 d 6.0 f 22.4 | 2, 1.9, CLEAR/CLEAR |
| T248 (wider) | 40.6 | 0.1 | 24.4 | 0.9 | 1.4 | 0.2 | 13.0 | 0.0 | 0.7 | 0.0 | 0.0 | f 12.5 | 2, 5.7, CLEAR/CLEAR |
| T249 (wider) | 31.6 | 0.1 | 23.1 | 0.3 | 0.9 | 0.3 | 6.6 | 0.0 | 0.3 | 0.0 | 0.0 |  | 1, 1.1, CLEAR |
| T262 (wider) | 28.6 | 2.5 | 18.2 | 1.3 | 0.9 | 0.1 | 5.4 | 0.0 | 0.3 | 0.0 | 0.0 | f 5.2 | 0, 0.0,  |

# weighted tokens (thousands) by step, builder; reviewers apart

| task | builder total | a | b | c | d | e | f | g | r | i | x | reviewers | builder raw total (k) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| T252 | 678 | 54 | 424 | 53 | 28 | 0 | 19 | 0 | 100 | 0 | 0 | 72 | 4215 |
| T263 | 918 | 55 | 506 | 76 | 29 | 17 | 174 | 0 | 62 | 0 | 0 | 189 | 4900 |
| T267 | 782 | 0 | 477 | 29 | 46 | 15 | 138 | 0 | 78 | 0 | 0 | 83 | 4221 |
| T268 | 1098 | 0 | 682 | 52 | 54 | 0 | 185 | 0 | 108 | 0 | 16 | 139 | 5792 |
| T269 | 1409 | 38 | 688 | 59 | 39 | 19 | 433 | 19 | 112 | 0 | 0 | 99 | 6673 |
| T270 | 789 | 16 | 381 | 30 | 30 | 18 | 254 | 0 | 61 | 0 | 0 | 76 | 4107 |
| T271 | 981 | 16 | 397 | 51 | 88 | 165 | 191 | 0 | 72 | 0 | 0 | 98 | 4203 |
| T272 | 930 | 13 | 548 | 45 | 44 | 15 | 30 | 0 | 236 | 0 | 0 | 119 | 4560 |
| T248 | 2066 | 21 | 1582 | 80 | 147 | 22 | 83 | 0 | 130 | 0 | 0 | 226 | 12971 |
| T249 | 1721 | 18 | 1367 | 47 | 82 | 37 | 141 | 0 | 30 | 0 | 0 | 82 | 12962 |
| T262 | 1025 | 47 | 596 | 68 | 239 | 17 | 17 | 0 | 40 | 0 | 0 | 0 | 5413 |

# medians over the 8 small tasks (T252 T263 T267 T268 T269 T270 T271 T272)

| step | median min | range | share of summed builder minutes | median weighted tok (k) | share of summed tokens |
|---|---|---|---|---|---|
| a filing/bookkeeping | 0.2 | 0.0-4.1 | 3% | 16 | 2% |
| b code+tests (read, write, run) | 9.0 | 5.0-15.5 | 24% | 491 | 48% |
| c plan section | 0.7 | 0.5-1.1 | 2% | 52 | 5% |
| d decide + plan review | 0.9 | 0.1-6.9 | 5% | 150 | 15% |
| e claims | 0.1 | 0.0-0.3 | 0% | 16 | 3% |
| f closing checks | 28.8 | 0.4-32.9 | 63% | 180 | 17% |
| g landing+commit | 0.0 | 0.0-0.9 | 0% | 0 | 0% |
| r builder report/handoff | 0.4 | 0.3-0.8 | 1% | 89 | 10% |
| i idle after its report (woken, nothing in flight) | 0.0 | 0.0-3.8 | 2% | 0 | 0% |
| x other/unmapped | 0.0 | 0.0-0.1 | 0% | 0 | 0% |
| builder elapsed | 42.9 | 10.1-49.9 | | 1064 | |

# background runs the builder waited on (step, kind, minutes) and waits by (what woke it, what the wait is booked to)

T252 d Agent 0.9 | waits: d->f 0.3
T263 d Agent 5.0; d Agent 4.4; f Bash 22.5 | waits: d->f 9.3, f->f 12.2
T267 d Agent 1.5; f Bash 30.4; f Bash 3.7 | waits: ?->i 1.3, ?->f 1.4, d->f 0.0, f->f 30.0
T268 d Agent 2.4; f Bash 9.8; d Agent 1.0; f Bash 15.1; f Bash 3.2; b Bash 0.9; f Bash 0.7 | waits: d->f 3.2, f->f 23.7, b->f 0.9
T269 d Agent 3.3; f Bash 28.8; f Bash 2.4 | waits: ?->i 3.8, d->f 3.3, ?->f 14.2, f->f 11.4
T270 f Bash 1.0; d Agent 2.8; f Bash 32.3 | waits: f->f 31.5, d->f 0.4
T271 d Agent 3.8; f Bash 13.9; f Bash 20.3 | waits: d->f 2.9, f->f 27.1
T272 b Bash 0.4; d Agent 1.1; f Bash 21.4; d Agent 1.0; f Bash 2.9 | waits: ?->b 1.0, b->b 0.3, ?->f 1.0, d->f 0.9, f->f 20.6, ?->d 6.0
T248 d Agent 1.2; f Bash 2.5; d Agent 4.6; f Bash 11.3; f Bash 0.8 | waits: d->f 4.7, f->f 7.8
T249  | waits: 
T262 f Bash 8.5 | waits: f->f 5.2

# landing, done and closing-check runs booked to each task in the event log (make, t0, minutes, exit, who)

T248 land 11-25T23:25:11 6.6 min exit 0 c6fd72d1-ab6c-473
T262 land 11-26T04:16:12 2.6 min exit 0 c6fd72d1-ab6c-473

# the coordinating session's own turns whose tool call names the task (minutes of the model turn / weighted tokens k / calls) - a call naming more than three tasks is left out, one naming two or three is split; the tool's own run is not in the minutes

| task | a filing | h brief+dispatch | h woken by its builder | h commit, carry-over, worktree | g landing | h other | sum min | sum tok k | make land background run(s), min |
|---|---|---|---|---|---|---|---|---|---|
| T252 | 0.1 / 36 / 1 | 0.3 / 152 / 2 | 0.2 / 79 / 1 | 0.0 / 0 / 0 | 0.1 / 37 / 1 | 0.0 / 0 / 0 | 0.5 | 303 | 6.5 |
| T263 | 0.1 / 46 / 1 | 0.6 / 125 / 2 | 0.1 / 93 / 1 | 0.2 / 120 / 2 | 0.1 / 20 / 1 | 0.0 / 0 / 0 | 1.1 | 406 | 2.0 2.8 |
| T267 | 0.1 / 30 / 1 | 0.3 / 35 / 1 | 0.2 / 74 / 3 | 0.2 / 59 / 2 | 0.0 / 0 / 0 | 0.0 / 0 / 0 | 0.7 | 197 | 2.9 |
| T268 | 0.0 / 0 / 0 | 0.1 / 15 / 1 | 0.2 / 175 / 5 | 0.7 / 127 / 4 | 0.2 / 63 / 2 | 0.0 / 0 / 0 | 1.1 | 381 | 1.3 6.1 |
| T269 | 0.0 / 0 / 0 | 0.1 / 14 / 1 | 0.3 / 163 / 4 | 0.1 / 56 / 2 | 0.2 / 99 / 2 | 0.4 / 226 / 6 | 1.3 | 610 | 11.1 1.9 |
| T270 | 0.2 / 67 / 2 | 0.1 / 14 / 1 | 0.2 / 82 / 2 | 0.0 / 14 / 1 | 0.6 / 221 / 5 | 0.3 / 102 / 4 | 1.4 | 500 | 2.2 1.2 |
| T271 | 0.0 / 0 / 0 | 0.1 / 14 / 1 | 0.1 / 78 / 2 | 0.2 / 59 / 2 | 0.2 / 64 / 2 | 0.1 / 29 / 2 | 0.6 | 244 | 4.8 |
| T272 | 0.0 / 0 / 0 | 0.1 / 15 / 1 | 0.1 / 138 / 4 | 0.2 / 77 / 3 | 0.2 / 57 / 2 | 0.0 / 0 / 0 | 0.6 | 288 | 3.3 1.3 |
| T248 | 0.0 / 0 / 0 | 0.2 / 41 / 2 | 0.3 / 206 / 3 | 0.7 / 355 / 6 | 0.9 / 381 / 7 | 0.2 / 65 / 1 | 2.2 | 1048 | 10.5 0.9 3.4 3.7 16.7 3.1 6.5 |
| T249 | 0.1 / 36 / 1 | 0.2 / 41 / 2 | 0.0 / 0 / 0 | 0.4 / 212 / 4 | 0.2 / 70 / 2 | 0.3 / 69 / 1 | 1.1 | 427 | 3.7 16.7 |
| T262 | 0.6 / 256 / 4 | 0.4 / 110 / 2 | 0.1 / 88 / 1 | 0.2 / 180 / 2 | 0.2 / 183 / 2 | 0.3 / 211 / 3 | 1.9 | 1081 | 1.2 2.6 2.0 2.2 |
| median of the small | 0.0 / 15 | 0.1 / 15 | 0.2 / 87 | 0.2 / 59 | 0.2 / 60 | 0.0 / 0 | 0.9 | 342 | |

## Table 2 - timeline (m11-timeline.py; the "filed" column is NOT MEASURED - only three tasks have a filing commit of their own, ignore it and its median)

| task | filed | builder start | first code edit | builder end | code commit | tick (landed) | filed->landed min | builder start->landed | first code edit->code commit | task-time: whole min / blocking |
|---|---|---|---|---|---|---|---|---|---|---|
| T252 | 25 23:20 | 25 23:33 | 25 23:37 | 25 23:42 | 25 23:43 | 25 23:43 | 24 | 11 | 6 | 15 / 11 |
| T263 | 26 04:20 | 26 04:23 | 26 04:29 | 26 05:06 | 26 05:48 | 26 05:51 | 91 | 88 | 79 | 61 / 20 |
| T267 | 26 07:51 | 26 07:06 | 26 07:08 | 26 07:49 | 26 07:50 | 26 07:53 | 2 | 47 | 42 | 52 / 3 |
| T268 | - | 26 12:39 | 26 12:40 | 26 13:19 | 26 13:21 | 26 13:27 | - | 48 | 40 | 107 / 53 |
| T269 | - | 26 13:37 | 26 13:40 | 26 14:26 | 26 14:31 | 26 14:33 | - | 56 | 51 | 78 / 38 |
| T270 | - | 26 13:37 | 26 13:39 | 26 14:21 | 26 14:28 | 26 14:27 | - | 50 | 49 | 55 / 5 |
| T271 | - | 26 13:37 | 26 13:42 | 26 14:19 | 26 14:20 | 26 14:25 | - | 48 | 38 | 56 / 6 |
| T272 | - | 26 12:39 | 26 12:44 | 26 13:21 | 26 13:15 | 26 13:20 | - | 40 | 32 | 87 / 12 |
| T248 | 25 20:43 | 25 22:44 | 25 22:53 | 25 23:24 | 25 23:25 | 25 23:31 | 168 | 47 | 32 | 57 / 39 |
| T249 | 25 23:20 | 25 22:44 | 25 22:49 | 25 23:15 | 25 23:16 | 25 23:19 | -1 | 35 | 27 | 61 / 35 |
| T262 | 26 03:42 | 26 03:43 | 26 03:49 | 26 04:12 | 26 04:16 | 26 04:22 | 39 | 38 | 27 | 139 / 70 |
| median, the 8 small | | | | | | | 24 (n=3) | 48 | 41 (n=8) | 59 / 12 |

## Table 3 - make task-time categories, the 8 small tasks (m11-tt-small.py)

| group (make task-time categories) | median machine min | share of the 8 tasks' machine min | median blocking min | share of blocking | per task: T252 T263 T267 T268 T269 T270 T271 T272 |
|---|---|---|---|---|---|
| f+g compile, tests, hook suites, gate | 38.5 | 50% | 1.0 | 9% | 1 27 41 38 40 40 39 31 |
| b/c builder model turns (code, plan text, commands) | 7.3 | 15% | 0.0 | 8% | 8 15 5 7 26 5 8 5 |
| waits | 0.0 | 10% | 0.8 | 31% | 0 0 0 50 0 0 0 1 |
| other: shell reads and file edits | 0.8 | 10% | 0.0 | 7% | 1 5 0 0 0 2 0 42 |
| d plan review (agents + commands) | 3.5 | 6% | 0.0 | 2% | 1 9 3 4 4 3 4 3 |
| h main session turns | 1.5 | 3% | 1.5 | 10% | 1 1 1 4 3 2 1 2 |
| g landing, git | 1.6 | 3% | 0.9 | 5% | 1 1 1 2 2 2 3 2 |
| a spec-kit step (task-add, task-start, decide) | 0.2 | 1% | 0.2 | 2% | 0 1 0 1 0 0 0 0 |
| other: Makefile targets the guard's table does not book | 0.0 | 0% | 0.0 | 1% | 1 0 0 0 1 0 0 0 |
| other: record builds and docs | 0.0 | 0% | 0.0 | 1% | 0 0 0 0 2 0 0 0 |
| other: map generation | 0.2 | 0% | 0.1 | 0% | 0 0 0 0 0 0 0 0 |
| e claims round | 0.1 | 0% | 0.0 | 0% | 0 0 0 0 0 0 0 0 |
| other: python3 | 0.1 | 0% | 0.0 | 0% | 0 0 0 0 0 0 0 0 |
| other: review: other commands | 0.0 | 0% | 0.0 | 0% | 0 0 0 0 0 0 0 0 |
| the GM | 0.0 | 0% | 0.0 | 21% | 0 0 0 0 0 0 0 0 |
| other: the GM's filter: agents (escalation-check) | 0.0 | 0% | 0.0 | 1% | 0 0 0 0 0 0 0 0 |
| all | 58.7 | 100% | 11.9 | 100% | 15 61 52 107 78 55 56 87 |

## Table 4 - taskless commits on main since 2026-11-19 (m11-direct.py; the glossary .json rows are page-session data, not tweaks)

commits since 2026-11-19: 1608 naming no task: 772 of those touching tooling/engine code files: 27
no-task commits by what they touch: [('record', 630), ('spec', 46), ('research+spec', 17), ('record+spec', 13), ('tooling', 11), ('record+research+spec', 10), ('research', 10), ('engine+record+research+spec', 5), ('doc', 5), ('doc+record+spec', 4), ('doc+spec', 3), ('engine+research+spec', 3)]
code-touching no-task commits: files median 2 max 24 lines median 31 max 320
a459fb6bbe 2026-11-26T02:07 {'record': 3, 'doc': 1, 'tooling': 1, 'spec': 3} lines 2 | process decision: two code builders at once in reused worktrees, three or four only for work that compiles nothing (the GM's pre-approval of 2026-11-2 | ['scripts/container/builder-brief.md']
10324503cc 2026-11-26T02:02 {'record': 1, 'engine': 5, 'research': 18, 'spec': 2} lines 64 | 451 page session P17, on the GM's question of 2026-11-26: 0156 records which side of the wall the debased households' quarters stood on (China both -  | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/29300-debased household.json', 'l7r/diagram/interactive/assets/glossary/29310-musician household.json', 'l7r/diagram/interactive/assets/glossary/29320-beggar household.json', 'l7r/diagram/interactive/assets/glossary/29330-music office.json']
6acb69f1e1 2026-11-26T00:48 {'record': 2, 'engine': 4, 'research': 14, 'spec': 3} lines 45 | 451 page session P16 and the GM's answer of 2026-11-26: 0173 counts the samurai country estates in a provincial city's 3,000 (his ruling of 2026-11-24 | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/29270-stewardship province.json', 'l7r/diagram/interactive/assets/glossary/29280-dynasty province.json', 'l7r/diagram/interactive/assets/glossary/29290-Unicorn Clan.json']
a5256e0dd5 2026-11-25T22:40 {'doc': 3, 'record': 3, 'tooling': 1} lines 15 | two process decisions closed on the GM's pre-approval (2026-11-25): a feature's first task may be built while its PLAN review runs once the spec is FA | ['scripts/container/builder-brief.md']
97d61e7343 2026-11-24T20:32 {'record': 3, 'engine': 1, 'research': 5, 'spec': 1} lines 2 | 454: C2 - quote-check reads the hand-moved words on 0344 and 0345; page labels, two Gao lines, the corrected checks report | ['l7r/diagram/interactive/assets/glossary/28960-coolie.json']
f9c4f52e53 2026-11-24T20:14 {'engine': 1} lines 82 | 454: the assembled glossary | ['l7r/diagram/interactive/assets/glossary.json']
866f28a072 2026-11-24T20:13 {'engine': 12, 'research': 17, 'spec': 1} lines 94 | 454: C2 round 1 - intro, quote, format, translation and applicability findings applied to 0344, 0345 and five write-ups; Morse p. 24 read on its image | ['l7r/diagram/interactive/assets/glossary/28910-chop.json', 'l7r/diagram/interactive/assets/glossary/28920-tea-factor.json', 'l7r/diagram/interactive/assets/glossary/28930-supercargo.json', 'l7r/diagram/interactive/assets/glossary/28940-Songluo.json', 'l7r/diagram/interactive/assets/glossary/28950-godown.json']
e0db6b1276 2026-11-24T18:05 {'tooling': 1} lines 6 | the footnote hold's test: its asserts on single lines, every line reached | ['rust/guard/shared/src/checks/handle/tests.rs']
bac0a34693 2026-11-24T18:01 {'tooling': 1} lines 20 | the footnote hold's fix written with no branch a test cannot reach | ['rust/guard/shared/src/checks/handle.rs']
e234fa56b3 2026-11-24T17:57 {'tooling': 1} lines 17 | the footnote hold's test formatted (rustfmt) | ['rust/guard/shared/src/checks/handle/tests.rs']
b598204378 2026-11-24T17:43 {'tooling': 2} lines 56 | checks: a refused dispatch keeps the footnote hold's trip (ruling ask:454-c1b-fixloop-retrip) | ['rust/guard/shared/src/checks/handle.rs', 'rust/guard/shared/src/checks/handle/tests.rs']
6152e19430 2026-11-24T17:24 {'engine': 5, 'research': 15, 'spec': 1} lines 58 | 454: C1b round one - the checks' edits applied on 0339, 0340, 0341 and 0343: the 1823 safflower loss is a little under 16 percent (24 is Iwata's trial | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/28860-four-blow.json', 'l7r/diagram/interactive/assets/glossary/28870-Michinoshima.json', 'l7r/diagram/interactive/assets/glossary/28880-Ryukyu-kan.json', 'l7r/diagram/interactive/assets/glossary/28890-domain notes.json']
b962680be5 2026-11-24T16:46 {'engine': 3, 'research': 16, 'spec': 2} lines 27 | 454: S1b - the corrections the checks left open: the Harima iron dated as an undated six-blow reckoning in a book of the Genbun years and its silver g | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/16670-shiso.json', 'l7r/diagram/interactive/assets/glossary/28850-Shiso district.json']
d63186cb79 2026-11-24T16:20 {'record': 3, 'engine': 5, 'research': 5, 'spec': 1} lines 32 | 454: C1 - the glossary's Sparrow term narrowed to the clan (it would have caught 0258's sparrow boards), wari and shiso widened to their other senses, | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/16670-shiso.json', 'l7r/diagram/interactive/assets/glossary/28630-Sparrow Clan.json', 'l7r/diagram/interactive/assets/glossary/28630-Sparrow.json', 'l7r/diagram/interactive/assets/glossary/28830-wari.json']
6ca7fde745 2026-11-24T15:49 {'engine': 24, 'other': 1, 'research': 33, 'spec': 1} lines 320 | 454: C1 round one - the checks' edits applied on 0339-0342 and 25 registry write-ups (intro-check, record-format, quote-check, translation-check, sour | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/28630-Sparrow.json', 'l7r/diagram/interactive/assets/glossary/28640-bar iron.json', 'l7r/diagram/interactive/assets/glossary/28650-Joshu.json', 'l7r/diagram/interactive/assets/glossary/28660-fixed courier house.json']
c3d8d57a36 2026-11-24T12:39 {'tooling': 1} lines 3 | apply-edits fix: the test's doc comment passes the doc lint | ['rust/guard/shared/src/checks/reply.rs']
926e10e593 2026-11-24T12:32 {'tooling': 1} lines 23 | apply-edits: the checks' contract line "EDIT: none - <why>" is no unread EDIT | ['rust/guard/shared/src/checks/reply.rs']
c55b2f649f 2026-11-24T12:13 {'record': 1, 'engine': 3, 'research': 14, 'spec': 3} lines 50 | 453: round 2 of the record checks - the hand fixes the checks asked for (the jail's bran and empty bales, pay by the man, the quoted headings), their  | ['l7r/diagram/interactive/assets/glossary.json', 'l7r/diagram/interactive/assets/glossary/20180-by-employment.json', 'l7r/diagram/interactive/assets/glossary/28590-Kwantung territory.json']
3f724f31c6 2026-11-24T11:58 {'engine': 4, 'research': 24} lines 31 | 453: round 1 of the record checks on 0335-0337 and their nineteen sources - the checks' own edits applied and recorded | ['l7r/diagram/interactive/assets/glossary/28550-guan.json', 'l7r/diagram/interactive/assets/glossary/28560-Karafuto.json', 'l7r/diagram/interactive/assets/glossary/28570-South Seas Agency.json', 'l7r/diagram/interactive/assets/glossary/28580-settlement price.json']
f7c105b4a0 2026-11-24T11:50 {'tooling': 8, 'record': 1} lines 149 | Tooling from diagram-backlog, landed alone mid-feature (make land-tooling, feature 379) | ['.claude/agents/building-review.md', '.claude/agents/impl-drift.md', '.claude/agents/intro-check.md', '.claude/agents/modal-depiction.md', '.claude/agents/quote-check.md']
a872b46eff 2026-11-24T07:32 {'tooling': 1} lines 1 | ignore *.profraw: coverage byproducts a test run leaves in the clone root, which blocked sync-with-main as uncommitted changes (2026-11-24) | ['.gitignore']
bce1e28014 2026-11-22T17:38 {'tooling': 9} lines 233 | 449 arbiter fix: the reversal tripwire holds only its own session | ['rust/guard/shared/src/checks/arbiter.rs', 'rust/guard/shared/src/checks/arbiter/tests.rs', 'rust/guard/shared/src/checks/handle.rs', 'rust/guard/shared/src/checks/rounds.rs', 'rust/guard/shared/src/checks/rounds/tests.rs']
38c3a1c8fa 2026-11-22T09:53 {'tooling': 2} lines 57 | 449: the plan archive keeps a bundle's block while any task it lists is open | ['rust/gate/crates/plan/src/plan/task.rs', 'rust/gate/crates/plan/src/plan/task/tests.rs']
6570db3de4 2026-11-22T09:35 {'doc': 1, 'tooling': 3} lines 95 | 449 arbiter fix: a review dispatch is refused while its paired gate reads red, PAIR_OK or not | ['rust/guard/src/guards/pair_hooks/review.rs', 'rust/guard/src/guards/pair_hooks/tests.rs', 'tests/hooks/test-pair-hooks.sh']
ee2f44fbc5 2026-11-22T09:05 {'tooling': 1} lines 9 | run-plausible's history test holds an incremental gate only to the floor the check itself holds it to | ['rust/gate/crates/checks/src/checks/run_plausible/tests.rs']
4ceb12ad0f 2026-11-22T08:53 {'tooling': 2} lines 10 | land-alone: the clone's review verdicts seeded into the landing worktree, as its kept check results are | ['rust/gate/crates/land/src/land/alone/tests.rs', 'scripts/land-alone.sh']
46af955365 2026-11-22T08:29 {'record': 2, 'tooling': 1} lines 6 | 449: the 20 owed claims checked IN-STEP by impl-drift (claims-owed names none); the bundle test's formatting | ['rust/gate/crates/plan/src/plan/lint/tests.rs']

## Table 5 - the taskless tooling changes, minutes (m11-direct-min.py)

| direct change | commits | code files | code lines | first edit -> last commit, min | follow-up commits (format, lint, coverage) | make targets its session ran in the span (count, summed min) |
|---|---|---|---|---|---|---|
| footnote hold keeps its trip (arbiter ruling ask:454-c1b-fixloop-retrip) | 4 | 2 | 99 | 5 | 3 | rust-format 2/0.0, rust-test 1/0.5, rust-cover 1/1.1, static 1/0.0, land 1/0.0 |
| apply-edits: "EDIT: none" is no unread EDIT | 2 | 1 | 26 | 8 | 1 | land 2/0.0, rust-lint 2/0.6, plan-verdict 1/0.1, rust-test 1/0.6, land-tooling 1/0.0, quick 1/0.0, static 1/0.0 |
| land-tooling: 8 agent/tooling files | 1 | 8 | 149 | no Edit event found (edited by a shell command, or another log) | 0 | |
| .gitignore *.profraw | 1 | 1 | 1 | no Edit event found (edited by a shell command, or another log) | 0 | |
| 449 arbiter fix: reversal tripwire holds its own session | 1 | 9 | 233 | no Edit event found (edited by a shell command, or another log) | 0 | |
| 449: plan archive keeps a bundle block | 1 | 2 | 57 | no Edit event found (edited by a shell command, or another log) | 0 | |
| 449 arbiter fix: review dispatch refused while gate red | 1 | 4 | 97 | 4 | 0 | rust-test 3/0.8, rust-cover 3/0.3, rust-lint 1/0.1, format 1/0.0, rust-format 1/0.4, hooks-test 1/0.0, arbiter-fix-done 1/0.0 |
| run-plausible history test floor | 1 | 1 | 9 | no Edit event found (edited by a shell command, or another log) | 0 | |
| land-alone seeds review verdicts | 1 | 2 | 10 | 181 | 0 | rust-test 41/22.3, decide 29/1.4, plan-verdict 23/0.3, format 21/1.5, map 21/1.1, claims-bundle 20/1.3, claims-owed 19/0.5, closing-checks 18/0.0 |
| bundle test formatting (with a claims record) | 1 | 1 | 6 | 7 | 0 | rust-test 6/1.5, plan-delta 2/0.1, plan-verdict 2/0.0, verify 2/0.1, arbiter-fix-done 1/0.0, claims-triage 1/0.0, claims-owed 1/0.0, claims-bundle 1/0.0 |

median first edit -> last commit: 7 min over 5 changes with Edit events (range 4-181)

## The coordinator make land runs, each task own (from the main transcript): T252 0.8; T263 2.8; T267 2.9; T268 6.0; T269 1.9; T270 1.8 + 2.1 (the code, left out); T271 4.8; T272 3.3 + 1.3 (owed ledger row). The runs column of the coordinator table above also lists neighbors named in the same command.
