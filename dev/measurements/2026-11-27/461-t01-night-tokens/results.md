# 461 T01: the night's tokens by actor and kind (plan D12, FR-006 and FR-007)

Load this file when: you need the before figure of feature 461's token cost, or you are writing phase 5's after figure.

Measured 2026-11-27 by the 461 T01 builder, while the night's transcripts were still on disk. Nothing in the engine or the
tooling changed.

## What was run

From the clone's root, with `D=dev/measurements/2026-11-27/461-t01-night-tokens`:

    python3 -I $D/night-tokens.py 2026-11-27T04:30:00Z 2026-11-27T14:29:00Z $D/task-time-0430-1429.txt > $D/output-0430-1429.txt
    python3 -I $D/night-tokens.py 2026-11-27T02:00:00Z 2026-11-27T14:29:00Z specs/461-landing-lane/baseline-task-time.txt $D/calls-0200-1429.tsv > $D/output-0200-1429.txt
    gzip -9 $D/calls-0200-1429.tsv

The outputs are `output-0430-1429.txt` and `output-0200-1429.txt`. The extract `calls-0200-1429.tsv.gz` holds one row per model
call of the wider window, with no content: its timestamp, agent, actor, agent type, booking, whether that booking landed,
its model, the four token kinds and the advisor's four. `task-time-0430-1429.txt` is the header and the 451 T512 table of
`make task-time SINCE=2026-11-27T04:30:00Z UNTIL=2026-11-27T14:29:00Z`, run in diagram-backlog-t271 at 054d48a41c. It is the
04:30Z window's list of landed tasks.

The script reads the coordinator's transcript (`c6fd72d1-...jsonl`) and every subagent transcript under its directory: 2,975
at the top level and 113 more in the workflow directories (observed 2026-11-27, method: `find -name '*.jsonl'` there). It would also count any other main-session transcript in the project directory as a page session.

- **Calls.** A call is one message id. A message is written as one record per content block, with its usage repeated. Across
  the window's 17,075 records, no two records of the same id carried different usage (observed 2026-11-27, method: every
  record of each id compared).
- **The four kinds.** They are the call's top-level usage, which equals the sum of its own `message` iterations. The advisor's
  `advisor_message` iterations are not part of that usage, so the script sums them in separate columns (observed 2026-11-27,
  method: a sample of advisor-bearing calls' iterations summed by hand).

### Re-deriving after the transcripts are gone

Sum the extract by actor, from a start time:

    zcat calls-0200-1429.tsv.gz | awk -F'\t' -v w0=2026-11-27T04:30 'NR>1 && $1>=w0 {o[$3]+=$8; r[$3]+=$10; n[$3]++} END {for (a in o) print a, n[a], o[a], r[a]}'

This reproduces every total below to within one builder call. In the 04:30Z window it gives 6,018 builder calls where the
script gives 6,019. The cause is one message whose records fall on both sides of 04:30:00. Each run dates a message by the
first of its records that falls in that run's window, so the two runs place this one differently.

## The figure: tokens per landed task by actor and kind, 04:30Z to 14:29Z (FR-006)

This is the window D12 uses for comparison. T512's transcript fill starts at 04:30Z. In this window 120 tasks landed,
according to the T512 table of `task-time-0430-1429.txt` (observed 2026-11-27, method: the output above).

| actor | transcripts | calls | output | fresh input | cache read | cache write | per landed task: output / cache read | advisor out / in |
|---|---|---|---|---|---|---|---|---|
| builders | 88 | 6,019 | 4.04M | 0.01M | 849.73M | 15.45M | 33.6k / 7.08M | 0.95M / 11.68M |
| repair builders | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 / 0 |
| review agents | 152 | 923 | 0.87M | 0.00M | 21.99M | 4.18M | 7.2k / 0.18M | 0.48M / 2.14M |
| the coordinator | 1 | 810 | 0.44M | 0.00M | 474.03M | 1.03M | 3.6k / 3.95M | none |
| page sessions | 0 | 0 | 0 | 0 | 0 | 0 | 0 / 0 | 0 / 0 |
| all | 241 | 7,752 | 5.34M | 0.02M | 1,345.74M | 20.66M | 44.5k / 11.21M | 1.43M / 13.83M |

Window totals divided by the 120 tasks landed come to 44.5k output, 0.14k fresh input, 11.21M cache read and 172k cache write
per task. The coordinator's share is 35.2% of the window's cache read and 8.2% of its output (observed 2026-11-27, method: the
table's totals divided).

The concurrency to read beside this figure (FR-010):

- **Trees.** Three trees were held, busy 93%, 98% and 83% of 02:00Z to 14:29Z (R3, `tree-idle.py`).
- **Machine load.** The night's median load is 14.1 on 22 cores over this window, with 3.19 trees held. Both are in T02's
  section below.

## The same over the spec's whole window, 02:00Z to 14:29Z

In this window 130 tasks landed (R3's `baseline-task-time.txt`).

| actor | transcripts | calls | output | fresh input | cache read | cache write | per landed task: output / cache read | advisor out / in |
|---|---|---|---|---|---|---|---|---|
| builders | 104 | 7,092 | 4.86M | 0.02M | 1,027.54M | 19.63M | 37.4k / 7.90M | 1.22M / 15.12M |
| review agents | 180 | 1,076 | 1.03M | 0.00M | 25.60M | 4.91M | 7.9k / 0.20M | 0.55M / 2.46M |
| the coordinator | 1 | 980 | 0.56M | 0.00M | 591.33M | 2.48M | 4.3k / 4.55M | none |
| all | 285 | 9,148 | 6.46M | 0.02M | 1,644.47M | 27.02M | 49.7k / 12.65M | 1.77M / 17.57M |

None of these 9,148 calls came from a repair builder or a page session (observed 2026-11-27, method: `output-0200-1429.txt`).

## What books to a task, and what does not

Every actor's total is the sum of three parts: booked to a landed task, booked to a task that did not land, and booked to no
task. The script prints this check for each actor, and it holds for all of them. These are the parts for 04:30Z on, output
and cache read (observed 2026-11-27, method: the output's reconciliation section):

- **Builders.** Landed 3.90M / 828.82M. Not landed 0.13M / 20.91M: 451 T507's measurement builder and T508's fix builder,
  both still running at 14:29Z.
- **Review agents.** Landed 0.81M / 20.23M. Not landed 0.01M / 0.20M. Unbooked 0.05M / 1.56M.
  - 131 agents booked through the builder that dispatched them: plan reviews and message checks, followed up the
    `parentAgentId` chain.
  - 5 agents booked by a description that names exactly one feature and task.
  - 16 coordinator-dispatched agents booked to no task: round arbiters, escalation checks, and reviews whose description
    names no single task.
- **The coordinator.** Everything unbooked: 0.44M / 474.03M. This agrees with 451 T513's finding that most coordinator calls
  book to no task.

### Per landed task, as booked

These are the builders and the agents booked to them.

- **Booking units.** The tokens book to 82 units, each a single task or a bundle (observed 2026-11-27, method: the output's
  per-task section). A bundle (`T479,T481`) books whole, as one unit, so the units cover more than 82 of the 120 tasks.
- **Tasks with no tokens.** A task built inside another task's builder, a task done as the coordinator's own edit, and the
  second task of a bundle book nothing.
- **Tokens per booked unit.** Output median 56.6k (total 4.71M). Cache read median 10.20M (total 849.04M). Cache write median
  220.6k (total 18.90M). Fresh input median 0.2k.
- **Task size beside it (FR-007).** From T512, counting lines added plus lines deleted: test lines median 97, total 16,549;
  non-test lines median 155, total 39,750. The totals count 69 shared rows more than once, because T512 counts a commit whole
  under every task it names.
- **Per-unit table.** Each unit's size and tokens are in `output-0430-1429.txt`.

All of these are observed 2026-11-27, method: the output's per-task section.

## Cross-checks

- **The per-task T512 booking (D12: a cross-check only).** Summed over its 120 rows, T512 books 5.62M output, 1,063.14M cache
  read and 21.87M cache write. The script books 4.71M, 849.04M and 18.90M to the same tasks. Over 02:00Z on, the figures are
  T512's 6.18M / 1,146.88M (R3's sums) against the script's 5.46M / 990.50M. T512 is the higher of the two for two reasons.
  It adds the coordinator's calls that it books to a task. It also counts a builder's whole transcript, including calls made
  before the window opened, while this script counts only calls inside the window. (Observed 2026-11-27, method: the outputs'
  cross-check sections.)
- **The coordinator against the update note.** The note gives 0.58M output and 616M cache read over 1,007 calls for 02:00Z to
  15:00Z. Over that span the script's dedupe gives 1,016 calls, 0.589M output and 624.7M cache read (observed 2026-11-27,
  method: a one-off run of the same dedupe with the end set to 15:00Z). The two agree within 1.5%.
- **T512's footer.** It gives 2,359 coordinator calls booked to no task and 1,308M cache read. That is a different count: it
  covers the calls of `make task-time`'s whole read-back, not only the window. It is not this record's figure.

- **A spot check of the per-task booking against T512.** Eight landed tasks whose first builder call came after 06:00Z were
  compared with T512's row times one minus its session share. Seven agree within 16% on output and 1% on cache read. The
  eighth, 451 T296, differs only because of bundle booking: this script books its bundle `T296,T297` as a unit of its own,
  where T512 books the bundle whole under each task (observed 2026-11-27, method: the extract summed by booking, beside the
  04:30Z T512 rows). So the script undercounts nothing, and the gap in the first cross-check has the causes stated there.

## Where the night's repairs sit

No repair builder ran, but repairs did happen. Main carries 10 repair commits between 06:38Z and 13:45Z (observed 2026-11-27,
method: `git log` over the window with its subjects searched for `repair`):

- **The batch-gate repairs.** Four `the batch gate's ... repair` commits.
- **Single-task repairs.** One `the nine-task gate's repair`, and five single-task `coverage repair before its gate` commits:
  T387, T492 and T495 together, T500, T490 and T363.

The coordinator made these in its own turns, by Bash edits and commits in the session clone, not through a repair builder
(observed 2026-11-27, method: its transcript's Bash calls naming `repair` from 09:00Z to 13:50Z). The night's repair cost is
therefore inside the coordinator's row. This record does not split it out. That cost is the "before" that D7's repair builder
replaces, so phase 5 should read it as part of the coordinator's 474.03M cache read, not as zero.

## Limits, stated wherever the figure is used

- **Concurrency over the headline window.** R3's tree-busy shares cover 02:00Z to 14:29Z. The 04:30Z window's own trees held
  and machine load are T02's to read from the pool log and the sampler, which stay on disk.

- **Classification.**
  - A builder is identified by its brief's `BUILDER-BRIEF <feature> <task>` marker. The one general-purpose agent without the
    marker in the window was identified by its description (`Fix: 451 T457 ...`).
  - A repair builder is identified only by its description (`Repair:` or `coverage repair`). Every brief quotes the rule "a
    builder whose JOB is a coverage repair", so classifying by the brief's words wrongly counted 451 T308's fix builder as a
    repair builder.
  - The night ran no repair builder and no page session. No other main-session transcript under `-diagram` has a call in the
    window (observed 2026-11-27, method: the script's other-sessions scan, and `find -newermt 2026-11-27T02:00:00Z` over
    `~/.claude/projects`, which found only an unrelated project's transcript).
- **Advisor calls.** Their tokens are given apart and are never in the four kinds. This follows T512, which also leaves them
  out.
- **Models.** Builders used Opus 5.5 for nearly all calls, Sonnet 5.5 for 24 and Fable 5.2 for 241. The coordinator used Opus
  5.5 for 934 calls and Fable 5.2 for 45. In the 04:30Z window every call was Opus or Sonnet (observed 2026-11-27, method: the
  outputs' model-mix lines). Tokens are not normalized across models.

# 461 T02: the rest of D12's figures, the night's concurrency and the likeness test (FR-006, FR-007, FR-010)

Measured 2026-11-27 by the 461 T02 builder, in diagram-backlog-t271 at eb205722a4. Nothing in the engine or the tooling changed.
The script is `night-figures.py`, a sibling of `night-tokens.py`: tokens stay there, everything else of D12's table is here.

## What was run

From the clone's root, with `D=dev/measurements/2026-11-27/461-t01-night-tokens`:

    python3 -I $D/night-figures.py extract 2026-11-27T02:00:00Z 2026-11-27T14:29:00Z $D/kept
    python3 -I $D/night-figures.py figures 2026-11-27T04:30:00Z 2026-11-27T14:29:00Z $D/task-time-0430-1429-at-eb2057.txt --kept $D/kept --json $D/ref-0430-1429.json > $D/output-figures-0430-1429.txt
    python3 -I $D/night-figures.py figures 2026-11-27T02:00:00Z 2026-11-27T14:29:00Z $D/task-time-0200-1429-at-eb2057.txt --kept $D/kept --json $D/ref-0200-1429.json > $D/output-figures-0200-1429.txt

- **The sources.** Three files under the common git directory: `builder-pool.log`, replayed from its first line;
  `l7r-events/*.jsonl`, the `make land` rows; and `l7r-events/samples/mem-samples*.jsonl`, the sampler's samples.
- **The kept extracts.** `kept/` holds no content: the pool log up to 14:29Z, the window's `make land` rows, and each sample's
  time, `load1`, cores and count of trees held. With `--kept`, the figures re-derive once the sampler's file has rotated (it
  starts a new file past 4 MiB or 12 hours). Both runs above read the extracts, and each run's output matches a live run's,
  apart from its source line (observed 2026-11-27, method: `diff` of the two runs).
- **The task-time cuts.** `task-time-0430-1429-at-eb2057.txt` and `task-time-0200-1429-at-eb2057.txt` are the header and the
  two window tables of `make task-time` over each window, both run at one time and one commit. The time matters more than the
  commit, for the reason under "Cross-blocking" below.

## The figures, 04:30Z to 14:29Z (the headline window), with 02:00Z beside it

| figure | 04:30Z to 14:29Z | 02:00Z to 14:29Z | source |
|---|---|---|---|
| tasks landed | 120 | 130 | the task-time header |
| tree-hours held (builder hours) | 31.80 | 41.75 | the pool log's held spans |
| landed per tree-hour held | 3.77 | 3.11 | the two above |
| cross-blocking (a task waited on a landing) | 53.7 min of 129.3 tasks' side blocking | 53.7 min of 164.5 | the task-time header, at eb205722a4 |
| landings' side blocking | 522.4 of 599.8 min | 569.1 of 772.5 min | the task-time header |
| landing attempts | 39 | 49 | the event log's `land` `end` rows |
| landed | 11 | 17 | the same rows, `landed` |
| refused before a gate | 17 | 19 | the attempts with no `gate` row in their span |
| gate red | 8 | 10 | the attempts whose `gate` row is non-zero |
| gate green, refused at the tick or push | 3 | 3 | the rest |
| trees held, time-weighted (FR-010) | 3.19 | 3.34 | the pool log |
| median load (FR-010) | 14.1 on 22 cores (0.64x) | 12.6 (0.57x) | the sampler's `load1` |

All of these are observed 2026-11-27, method: `output-figures-0430-1429.txt` and `output-figures-0200-1429.txt`.

- **The trees.** The pool held four trees, not three. Over the headline window t269 was held 95% of the time, t271 84%, t270
  82% and b1 58%. R3's 93/98/83% are `tree-idle.py`'s busy shares, where a builder ran, over the three trees. Tree-hours
  held are a different figure (observed 2026-11-27, method: the same outputs).
- **Trees held, checked.** The sampler's own `held` field gives a mean of 3.18 over the headline window and 3.34 over the whole
  window, against the replay's 3.19 and 3.34 (observed 2026-11-27, method: the outputs' cross-check line).
- **The load, checked.** The median `load1` is what `make sampler-report` prints for each window, 14.1 and 12.6 (observed
  2026-11-27, method: `make sampler-report SINCE= UNTIL=` over each window). The sampler had one gap over 120 s, 09:38:58Z to
  09:44:04Z, where it ended at its 12 hours and was restarted (observed 2026-11-27, method: `sampler.log`).
- **The refusals, checked.** Over the update note's own span, 02:00Z to 15:00Z on the live event log, the script gives 50
  attempts, 18 landed, 19 refused before a gate, 10 gates red and 3 refused after a green gate. That is the note's count
  exactly (observed 2026-11-27, method: a `figures` run with the end set to 15:00Z). So the before figure is re-derivable from
  the event log, not only the note's partly inferred count. The note's causes (plan review owed 6, audit entry 5, tripwire 4,
  ledger row 3, unclear 2) are not in the event log and stay the note's.
- **Which window an attempt counts in.** An attempt counts in the window where its `end` row falls.

## Cross-blocking moves after its window closes

The 02:00Z window's cross-blocking was 32.3 min in R3's `baseline-task-time.txt`, run at 7af15e21ab about 14:40Z. At
eb205722a4, run about 17:55Z, the same window gives 53.7 min, and its tasks' side blocking rises from 143.2 to 164.5 by the
same 21.4 min (observed 2026-11-27, method: both runs' headers).

- **The cause.** The row counts a pool tree free from a release to its NEXT handout. A tree freed inside the window and handed
  out only after the run is not counted at all. t271 was freed at 13:19:38Z and next taken at 17:31:55Z, and t270 was freed at
  13:47:10Z and next taken at 15:40:16Z. Neither handout had happened at 14:40Z (observed 2026-11-27, method: the pool log's
  take and release rows).
- **The size of it.** A per-tree sum of those spans during landings, while fewer than three trees were held, gives 25.2 min
  from spans whose next handout came after 14:40Z, against the 21.4 min rise. The rough sum overcounts, because it does not
  merge the trees second by second as the row does, so the two are consistent (observed 2026-11-27, method: a one-off replay of
  `kept/pool.jsonl.gz` against `kept/land.jsonl.gz`).
- **What this means for the record.** `baseline-task-time.txt` is kept as R3 took it, the before figure the task line names. Its
  32.3 min is not comparable to a later run. The cause is the pool log's growth after the window, not the commit, so a rerun
  at one commit does not fix it. Filed as T33 (an open free span clipped at the window's end, one rule for both windows),
  which lands before T31.
- **The night's 53.7 min can still move.** b1 was released at 10:20:43Z and has had no handout since (observed 2026-11-27,
  method: the pool log's last b1 rows, read about 18:00Z). Its free span is still open, so the row does not count it yet. Its
  next handout can add whatever of 10:20Z to 14:29Z it spent free during a landing while fewer than three trees were held.
- **No new cross-blocking in the first two and a half hours.** The headline window's 53.7 min equals the whole window's 53.7
  min, so all of it fell after 04:30Z (observed 2026-11-27, method: the two cuts' headers).

## The likeness test (D12; phase 5 reruns it)

    python3 -I $D/night-figures.py like $D/ref-0430-1429.json <W0> [<W1>] [--kept DIR] [--samples FILE ...]

- **The rule.** A window is LIKE the night when three things hold. Its wall span is at least `LIKE_MIN_H` hours (8). Its
  time-weighted trees held is within `LIKE_TREES_BAND` (0.5) of the night's 3.19. Its median load is within `LIKE_LOAD_BAND`
  (0.75 to 1.25) times the night's 14.1, that is 10.6 to 17.6.
- **The knobs.** All three are GUESS knobs (plan D12 and its knob table). They sit at the head of the script and are
  overridden from the environment.
- **The plan's silent point.** D12 says "eight hours or more of builder work". The plan does not say whether that is a wall
  span or tree-hours. The script takes the wall span and prints tree-hours beside it.
- **Given W0 only.** The script scans window ends from W0 + 8 h in 10-minute steps to the last sample, and prints the first LIKE
  window. Exit 0 means a window is LIKE, 1 that none is.
- **Shown both ways.** These are in `output-like.txt` (observed 2026-11-27, method: the five runs there):
  - The night against itself is LIKE.
  - 06:00Z to 14:29Z is LIKE: trees held 3.05, load 13.2.
  - 04:30Z to 11:30Z is NOT LIKE: its span is 7 h.
  - 2026-11-26T21:40Z to 2026-11-27T05:40Z is NOT LIKE: its load is 9.4.
  - From 09:45Z to the last sample (17:54Z) is NOT LIKE: trees held 2.06 and load 8.1.
  - The last two runs read the live sources, so they re-run only while the sampler's file holds those samples.
- **The reference.** `ref-0430-1429.json` is the night's reference: its trees held, load, and the task-time and landing figures.
  `ref-0200-1429.json` is the same over the whole window.

## For phase 5

- **The coordinator's repairs.** The night's repairs were the coordinator's own turns (T01, "Where the night's repairs sit"). A
  zero in the repair builders' row is not a zero repair cost.
- **Refusals before a gate.** The after figure is read from the same event-log rows, or from the lane log once D8 writes one.
  The two must be reconciled over one batch before they are compared.
- **Cross-blocking.** Read both windows after T33 lands, by the same tool. Before T33, a window's row is final only once every
  tree freed in it has been handed out again, and the after window undercounts if `make task-time` runs before that.
- **Finding the like window.** `like` with W0 alone holds W0 fixed and grows the end, so a quiet stretch just after W0 dilutes
  every later end. T31 steps W0 too: from phase 3's landing, by the same 10-minute steps, until a start gives a LIKE window.
- **Three trees or four.** D12's table, R3 and FR-010 say three trees. The pool held four, b1 included, and the likeness test
  reads trees held, not the count of trees.
