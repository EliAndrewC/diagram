# 461 T10: phase 1 measured on the real work since it landed (US2, SC-002, FR-010)

Load this file when: you need phase 1's after figures (the builder's own hand-in, T05-T08, T43, T44), or you are writing phase
5's comparison of refusals before a gate.

Measured 2026-11-27 by the 461 T10 builder, in diagram-backlog-t271 at 7c0cfca73c, read-only over the clone's records. Nothing in
the engine or the tooling changed.

## What was run

From the tree's root, with `D=dev/measurements/2026-11-27/461-t10-phase1`:

    python3 -I $D/phase1.py extract 2026-11-27T19:00:00Z 2026-11-27T23:03:20Z $D/kept --transcripts ~/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/subagents > $D/output-extract.txt
    python3 -I $D/phase1.py figures 2026-11-27T19:57:00Z 2026-11-27T23:03:20Z --kept $D/kept > $D/output-1957-2303.txt
    python3 -I $D/phase1.py figures 2026-11-27T21:06:47Z 2026-11-27T23:03:20Z --kept $D/kept > $D/output-2106-2303.txt
    python3 -I $D/phase1.py figures 2026-11-27T19:57:00Z 2026-11-27T23:03:20Z > $D/output-1957-2303-live.txt

- **The script.** `phase1.py` reuses `night-figures.py` (461 T02) for the landings, the pool replay and the load, so the after
  figures are counted exactly as the night's were.
- **The kept extracts.** `kept/` holds the pool log to 23:03:20Z, every `make builder-done` tool call (its time, agent, task,
  call id), what the hand-ins ran (Phase rows by second and step), the `make land` rows and the sampler's counts. It holds no
  content but each refused call's reason lines. The figures re-derive from it once the sampler's file rotates.
- **Live against kept.** The live run gives the same figures as the kept run, apart from the transcript outcomes, which only
  the extract reads (observed 2026-11-27, method: `diff` of `output-1957-2303.txt` and `output-1957-2303-live.txt`).

## The windows

- **The main window: 19:57:00Z to 23:03:20Z, 3.11 h.** It opens just after T08 and T43 landed (their `make land` end row is
  19:56:47Z, commit 51c70fb786). It closes just before this task's own take at 23:03:28Z. The first hand-in a builder ran
  itself was T44's, at 20:17:02Z.
- **The second window: 21:06:47Z to 23:03:20Z, 1.94 h.** It opens after T44 landed (21:06:46Z), so it is the one in which a
  build half and a measurement could hand in too. This is the brief's "about 21:00Z".
- **Before the window.** Three `"handed_in": true` rows fall before 19:57Z, 19:41Z to 19:53Z (T43's own, 451 T528/T529 and
  T513/T514). The coordinator ran all three, so they are not counted. The pool log has 30 such rows in all.

## The figures, 19:57Z to 23:03Z, with 21:06Z beside them

| figure | 19:57Z to 23:03Z | 21:06Z to 23:03Z |
|---|---|---|
| hand-ins (pool `done` rows, all `"handed_in": true`) | 27 | 22 |
| of them run by a builder / by the coordinator | 27 / 0 | 22 / 0 |
| distinct tasks or bundles handed in | 22 | 18 |
| `make builder-done` calls by builders | 34 | 28 |
| calls that handed nothing in | 7 (21% of calls), on 7 of 23 tasks | 6 (21%), on 6 of 19 tasks |
| of those: a conflict / a first-pass refusal (transcripts) | 4 / 3 | 3 / 3 |
| conflicts resolved by the builder that met them | 3 of 4 (the 4th by a fresh builder) | 3 of 3 |
| coverage steps run at a hand-in | 0 | 0 |
| landing attempts | 7 | 4 |
| landed (tasks landed) | 5 (19) | 3 (10) |
| refused before a gate | 0 | 0 |
| gate red | 2 | 1 |
| gate green, refused at the tick or push | 0 | 0 |
| trees held, time-weighted (FR-010; the lane's tree left out) | 2.94 | 3.02 |
| median load | 9.4 on 22 cores (0.43x) | 10.3 (0.47x) |

All of these are observed 2026-11-27, method: `output-1957-2303.txt` and `output-2106-2303.txt`. Every hand-in in either
window was run by a builder.

- **More than one hand-in per task.** These are successive builders of one task, not refusals. 461 T12 was handed in three
  times: its build half, its closing half and a coverage repair. 461 T14 and T20 were each handed in twice, by a build half
  and a closing half. 451 T537 was handed in twice, by a closing half and a coverage repair (observed 2026-11-27, method: the
  agents' descriptions in the transcripts' `.meta.json`).
- **What the hand-ins ran.** The Phase rows written under `make builder-done` are all map steps: 110 cached, 35 generate, 30
  page and 30 render. There is no `rust cover-build` or `cover-run` row, so no hand-in ran coverage, as SC-002 asks (observed
  2026-11-27, method: `output-1957-2303.txt`, the line "what the hand-ins ran").

## Refused at hand-in, and why

The logs alone show only that a call handed nothing in. A call counts as a hand-in where a pool `done` row of its task falls
from 5 s before its start to 60 s after it returned; each done row goes to the latest such call. A call with no done row
handed nothing in. The logs cannot tell a refusal from a conflict. The event log's tool rows carry no exit code for a
foreground call, and the pool log writes nothing on a refused or conflicted hand-in.

The why comes from a second source: the call's own tool result in the subagent transcripts, found by its call id. The
outcome is classified, and only the reason lines are kept. These are the seven calls that handed nothing in, observed
2026-11-27, method: the transcripts, through `phase1.py extract --transcripts`:

| call | task | outcome | what it named | then |
|---|---|---|---|---|
| 20:28:08Z | 451 T531 (fix) | conflict | 6 paths by hand (rust/gate/crates/measure/...), 1 by rule | the builder wrote a handoff; a fresh closing half resolved it and handed in at 20:37:10Z |
| 21:22:24Z | 461 T17 | first-pass refusal | a review pass with no ledger row, with `make ledger-owed WRITE=` | the same builder answered it and handed in at 21:23:21Z |
| 21:26:17Z | 461 T12 (closing half) | conflict | `specs/461-landing-lane/tasks.md` by hand, plan-review.json by rule | the same builder, at 21:27:29Z |
| 21:49:55Z | 461 T14 (build half) | conflict | `rust/gate/crates/lane/src/runner/tests.rs` by hand, plan.md and tasks.md by rule | the same builder, at 21:53:08Z |
| 22:06:03Z | 451 T537 (build half) | first-pass refusal | "this tick would close the feature": 451 has no report.md (`make feature-report`), and a ledger row is owed | its closing half handed in on the same tree at 22:44:14Z |
| 22:26:49Z | 461 T15 (build half) | conflict | 2 paths by hand (rust/gate/crates/lane/...), rust/gate/CLAUDE.md by rule | the same builder, at 22:34:45Z |
| 22:58:26Z | 462 T371 (fix) | first-pass refusal | 462's plan blocks changed since their CLEAR review, with `make plan-delta` | still open at 23:03:20Z; the tree is held |

- **The fixing command.** Every refusal named the command that answers it, and every conflict named its paths, the `git add`
  to run and the rerun. That is SC-002's "refused at hand-in with its fixing command" on real work.
- **Who answered.** The coordinator answered none of the seven. Five were answered by the builder that met them, in 57 s to
  8 min. One was a handoff to a fresh builder (T531, six paths by hand). One was the build half's feature-close ask, which its
  closing half answered.
- **Filed: T60.** A build half cannot answer the feature-close ask: it is not the closing half's tick. T44 puts off a build
  half's plan asks by its kind, but not this one. T60 puts it off as T44 does the plan asks, and the landing still asks it.

## Landings refused before a gate, against the night

| window | attempts | refused before a gate | rate | trees held | median load |
|---|---|---|---|---|---|
| the night, 04:30Z to 14:29Z (461 T02) | 39 | 17 | 44% | 3.19 | 14.1 (0.64x) |
| the night, 02:00Z to 15:00Z (the update note's span) | 50 | 19 | 38% | 3.34 to 14:29Z | 12.6 (0.57x) to 14:29Z |
| phase 1, 19:57Z to 23:03Z | 7 | 0 | 0% | 2.94 | 9.4 (0.43x) |
| phase 1, 21:06Z to 23:03Z | 4 | 0 | 0% | 3.02 | 10.3 (0.47x) |

The night's rows are from `461-t01-night-tokens/results.md` (observed 2026-11-27, method: 461 T02's `night-figures.py`). The
phase 1 rows are observed 2026-11-27, method: `output-1957-2303.txt` and `output-2106-2303.txt`.

- **What the after figure shows.** None of the seven attempts was refused before its gate. Each landing's first pass met
  work its builder had already answered at hand-in. The three refusals and four conflicts above are the same kind of refusal
  the night met at landing (ledger row, plan review owed), now met and answered at hand-in.
- **The sample is small.** If the night's 44% had held, seven attempts with no refusal would come about 1.7% of the time
  (0.56^7). US2's GUESS bar is under a quarter of the night's rate, about 11%. Seven attempts cannot show the true rate is
  under 11%: at exactly 11%, no refusal in seven comes about 44% of the time (0.89^7). So the result agrees with US2's
  "well under", but does not establish it.
- **The gate's own reds.** Two of the seven were gate red: T44/T11/T13 at 21:02:50Z, and the nine-task batch at 22:41:34Z.
  The 451 landings' gate rows of 0 s are the gate step's own rows, which `night-figures.py` reads as a gate that ran.
- **Where the landings ran.** All seven ran in the session's clone. None ran in the lane's tree, which the pool log adopted
  as `lane` at 21:08:09Z.

## Concurrency (FR-010), and why this is not a like window

- **The figures.** 2.94 trees held, time-weighted, over the main window and 3.02 over the second, against the night's 3.19.
  The tree-hours were 9.12: t269 92%, t271 90%, t270 83% and b1 29%. The median load was 9.4 (0.43x) and 10.3 (0.47x),
  against the night's 14.1 (0.64x) (observed 2026-11-27, method: the outputs' concurrency section).
- **Not a like window.** It fails two of the likeness test's three knobs: its 3.11 h wall span is short of 8 h, and its load
  is below 10.6. Every comparison above is therefore stated with both windows' concurrency, as FR-010 asks. None is a
  before-and-after of like windows.
- **The lane's tree.** From 21:08:09Z the pool log has an `adopt` of `/diagram/.clones/diagram-backlog-land` with detail
  `lane`, never released. `night-figures.py`'s replay counts it as a held tree, which gives 3.55 over the main window. The
  sampler's `held` lists `lane` in 215 samples, which gives its mean of 3.18. With the lane left out, the sampler and the
  replay agree on 848 of 1,065 samples and differ by one in the rest: `lane` in 215 and a hand-in second (461 T51) in 1
  (observed 2026-11-27, method: a one-off comparison of each sample's `held` list with the replay's holds at its time).
- **Filed: T59.** Phase 5's like window (T31) would otherwise read about one tree high. T59 leaves the lane tree out, or
  counts it apart, in both places, and lands before T31.

## The one real hand-in: this task's own

The task line asks for "this feature's next task handed in through `make builder-done`". That is this task's own hand-in, a
measurement's under T44's rule: no plan stub is asked, and the record under `dev/measurements/` stands in for the section.
Its outcome cannot be in the record it commits. The builder's report gives it, with the done ref and the next dispatch the
command printed.
