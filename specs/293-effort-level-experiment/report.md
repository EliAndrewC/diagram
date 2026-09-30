# Report - feature 293, the effort-level experiment (a pilot)

**A pilot at n = 1 per cell: every difference below is directional.** Opus 5.5 at `medium` against `xhigh`, one run per arm on
each of two real tasks, 2026-09-29/30. The results are specific to Opus 5.5 and this repository's tooling as of this date; re-run a
reduced version when either changes significantly.

## Outcome

| task type | quality | cost (`xhigh` / `medium`) | FR-011 outcome | the GM's ruling |
|---|---|---|---|---|
| research | the same, under the bar fixed before the key was opened (blind: both grader runs prefer `xhigh`, by 1 and 5 of 40, under the bar of 6; they DISAGREE on whether it is strongly better - run 1 no, run 2 yes; the GM, not blind: no noticeable difference) | total tokens 2.1x (output 2.4x), API time 2.2x, wall-clock 3.0x | **keep `medium`** (quality the same, cost over 1.25x) | no setting ruling: "I don't really find either of the research pages to be particularly noticeably better than the other" - a blind check asked for |
| implementation | `xhigh` better (the GM, not blind) | output tokens 2.3x, API time 3.0x, wall-clock 2.9x | **adopt `xhigh`** on quality (the GM prefers it, with its reason) | **keep `medium` as the default**; go higher "in cases where I believe that it will be necessary for the session to really go deep and take the initiative to do research and find semi-related bugs and fix them" |

**Recommendation:** keep `medium`, Opus 5.5's own default, as this repository's default effort for both task types. No setting
changes: `.claude/settings.local.json` needs no `effortLevel`, since `medium` is what a session gets without one. Raise it per session
(`/effort xhigh`, or `--effort xhigh` for a headless run) for implementation work where the GM wants the session to dig into the premise
and chase related defects. The GM read the research result as evidence that the project's subagent checks already hold a floor of
quality: both entries passed the same checks, and the difference that remained was one source found or missed.

**Expansion (FR-011):** every cost measure differs by more than 2x, which the rule marks as a big difference worth a further round (a
`high` arm, or a second run per cell). Proposed here, not started; the GM's ruling settles the default without it.

## The runs

| run | task | effort | output tokens (main + subagents) | cache read | cache write | input | API time | wall-clock* | tool calls (main + sub) | failed `make` | guard refusals | escalations | resumes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| e2 | research | `xhigh` | 228 k (154 k + 74 k) | 15.1 M | 0.61 M | 412 | 38 min | 90 min | 210 + 77 | 1 | 1 | 0 | 0 |
| e3 | research | `medium` | 96 k (54 k + 43 k) | 7.1 M | 0.36 M | 260 | 17 min | 30 min | 113 + 45 | 0 | 1 | 0 | 0 |
| e5 | implementation | `medium` | 479 k (181 k + 297 k) | 101 M | 2.4 M | 1,250 | 66 min | 107 min | 313 + 405 | 6 | 17 | 1 | 3 |
| e7 | implementation | `xhigh` | 1,103 k (598 k + 505 k) | 272 M | 4.3 M | 2,172 | 201 min | 307 min | 708 + 573 | 15 | 29 | 2 | 5 |

\* **Wall-clock is confounded by host load** (the GM's ruling: kept in the rule, known unreliable): the pauses a stalled session sat idle
are excluded, but CPU contention from the GM's other sessions during a run's gates and map rolls is not. API time (each session's
`duration_api_ms`) is the cleaner speed measure. The usage-limit share was not observable from inside a `-p` session. The API-equivalent
cost each session reported: e2 $12.5, e3 $6.0, e5 $30.8, e7 $106.4 - a scale, not a bill, on a subscription.

**Rework (hypothesis 1: lower effort shows up as more rework).** Not supported: `xhigh` did MORE rework in absolute terms on the
implementation task (15 failed `make` runs against 6, 29 refusals against 17, six review rounds against three), because it pursued more -
each fix of a defect its change exposed exposed the next. Per unit of work the two are close. On research both passed their checks with one
not-pass verdict each.

**Hypothesis 2 (effort matters most where checks are weakest - research).** Not supported at this size: on research the checks held both
entries to the same floor; the difference effort made was one source found, which changed one conclusion modestly.

## The controls, as measured

- **Effort**, read from every assistant record's `effort` field: every main-session message ran at its arm's level (e2 132/132 `xhigh`,
  e3 93/93 `medium`, e5 270 `medium`, e7 540 `xhigh`; 3 and 4 records carry no field). Every defined check agent ran at its pinned tier in
  both arms (source-reader and source-applicability `high`, quote-check and record-format `medium`, settlement-review `high`).
- **Ad-hoc judging at the session's effort:** 0 in every run.
- **Same start, same prompt:** every run started from `ec99356cf` with byte-identical prompts (hashes in `experiment.json`); task I's
  prompt and rubric were re-frozen once when the GM replaced the task, before its runs.
- **Sequential, under memory headroom:** no two runs overlapped; each launch was gated on the shared container cgroup's working set
  (research R5 D7); none was killed at the memory cap.

## Quality

**Research (blind, two `effort-grader` runs on Opus `high`; the key opened after both):** A = e2 (`xhigh`), B = e3 (`medium`).

| grader run | A (`xhigh`) | B (`medium`) | deficient? | strongly better? |
|---|---|---|---|---|
| 1 | 33 / 40 | 32 / 40 | no, neither | no - A better, "but not strongly" |
| 2 | 35 / 40 | 30 / 40 | no, neither | **yes, A** - "the difference changes what gets drawn"; how much: "moderately" |

The GM's two questions, answered by two runs (the GM: whether two runs match is what tells how reliable the result is): **they agree**
that neither entry is deficient and that A is the better one; **they disagree** on whether A is strongly better - run 1 no, run 2 yes. So
the result is not reliable on that point. Under the bar the GM approved before the key was opened (both runs prefer one entry, each by 6
of 40 or by 2 on the answer or citation criteria - here margins of 1 and 5, and gaps of 0 and 1 on those criteria), it is "no meaningful
difference". **What made the `xhigh` entry better:** it found a source the other missed - a surviving Kanazawa gate range whose
servants' room is two six-mat rooms behind one sliding door - and so concluded that Ubame's four-bays-one-door sheet is accurate as drawn
(the common-room form), where the `medium` entry would give every bay its own door, turning "a door per household" into "a door per bay"
against its own sources (households two or three bays wide). It also read the one scholarly paper (1790s domain plans), which the other
could not extract. **How much better:** modestly - the one-door case rests on a single thin tourism page for an undated, altered building,
"better supported and more honest, not proven" (grader run 2). Under the bar fixed before the key was opened (6 points, or 2 on the answer
or citation criteria): no meaningful difference. The `xhigh` entry landed (the higher mean), with the two small flaws both graders named
fixed (an inference labeled a guess; a trimmed quote's ellipsis) and re-checked clean by `record-format` and `quote-check`.

The grader ran as headless sessions with the `effort-grader` contract as the system prompt, on its pinned tier, because the session could
not dispatch an agent whose file exists only in the unlanded feature.

**Implementation (the GM, not blind, after the runs):** both solved the core task on every scripted hamlet with a green gate. `xhigh`
additionally researched the premise (a village record, Kakimochi, where the storehouses stood on the 2nd- and 3rd-largest houses, so
"exactly the largest" is labeled a deliberate deviation), dealt the share as a count with a stated tie rule, and ran six review rounds
chasing lane and thicket defects the re-pack exposed (48/48 cohort, against `medium`'s 8/8 cohort after three rounds).

## Defects found later (the implementation winner)

The GM chose to land `xhigh`'s version. At the landing, main had moved: feature 287 (placer guarantees) had rewritten the hamlet engine e7
changed (47 commits; the merge conflicted in 23 files), and feature 291 (grove sides) landed 143 more commits while the port ran. A port on
current main, by headless sessions at `medium` (counted apart from both arms, spec US4 AS3), took e7's core change and dropped what 287
made moot:

- **Ported:** the storehouse dealt by size (on 287's lots the size is known before the seat, so e7's hold-and-hand-back machinery was not
  needed), the storehouse's shape held to 18-27 ft at 1.5-1.8 to one, the bamboo thicket's fix, three lane-web repairs, the research
  (homesteads 120 and 430).
- **Dropped as moot on main:** the entrance framing, the joint zigzag re-route, the spur sweep, a coverage lift, a Kuwabata outlier.
- **Found at the landing:** a 32 ft dead-end lane stub at Inashiro's entrance (fixed); Sawada's shared ox sheds, two of four now past the
  120 ft reach where main had one (deferred to future-work with a sketch: lay each pocket during the seating).
- The port's gate: `make done` green, 100% coverage, the 48-seed cohort 48/48, two review rounds, all five maps PASS; then the merge of
  feature 291 (`outputs/I-port-handoff.md` records how it resolved).

**For the GM (from the port, through `escalation-check`):** (1) the storehouse annex's size is the Edo farm sheds' band (about 21-25 by
11-14 ft), labeled a deliberate deviation from the kura sizes read (about 15 by 18 and 12 by 18 ft); sizing it as the kura re-packs every
hamlet. (2) Sawada's sheds shipped as they are, the fix deferred.

## What went wrong, and what it cost

- **e1 void:** the launcher, run through `make`, exported make's variables into the run (`ARM=xhigh` named the arm; `MAKEFLAGS` broke two
  of its make calls). Fixed; re-run as e2.
- **e4 set aside:** task I's first pick (a footpath to the hamlet's burial ground) had lost its premise the day before the runs (feature
  280 M68 removed the hamlet's own burial ground). The pre-flight had checked the future-work entry, not the engine; it now checks the code.
  The GM replaced the task.
- **e6 void:** the headless session failed at launch ("No messages returned from query"); re-run as e7.
- **Stalls:** a headless session that ends its turn waiting on background work (a detached `make`, background review agents) is never
  woken - e5 three times, e7 five. Each was resumed with one fixed, arm-neutral message and the wait excluded as a pause; a watchdog did it
  after its two bugs were fixed (`bfs` rejects `find -newermt`; hook processes counted as work). **For any future headless work here: tell
  the session to run long commands and review agents in the foreground.**
- **Leaks checked and closed:** run clones first carried the feature directory and, through `git clone`, the session's later commits; e2
  and e3 never read either (their transcripts). From e5 on, a run clone holds the start commit alone.
- **Usage limit:** the port session stopped once at the session usage limit and was resumed after the reset.

## Interventions

Every one is a line in `interventions.md`: the refused launches and waits, the voids, the task replacement, the resumes, the memory
warnings during runs, the GM's cap and memwatch change (2026-09-30), the port and its merge.

## Caveats

- n = 1 per cell. The same effort level run twice can differ a lot (the handoff); the grader's two runs agreed in direction but differed
  by 4 points in margin.
- The GM's grading was not blind (the arms were known before the pages were read).
- Wall-clock is confounded by host load; API time and tokens are not.
- The thresholds (1.25x, 2x, the 6-point bar) are guesses fixed before the results, not measurements.
