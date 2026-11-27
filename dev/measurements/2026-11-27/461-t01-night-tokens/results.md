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
- **Machine load.** The night's median load is T02's to read from `make sampler-report`. It is not in this record.

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
