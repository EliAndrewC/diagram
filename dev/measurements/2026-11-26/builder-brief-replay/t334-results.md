# The builder-brief guard and command replayed over a day's dispatches (feature 451 T334, measured 2026-11-26)

Method: every `Agent` tool call of the coordinating session's transcript dated 2026-11-26 UTC (`t334-extract.py` writes them as
`t334-dispatches.json`, not kept here: it holds the prompts whole), each piped as a PreToolUse input through the built guard by its
suite link `tests/hooks/builder-brief-hooks.sh`, with `GUARD_LOG_DIR` and `CLONE_MAIN` in scratch (`t334-replay.py`; its rows, one a
dispatch - time, agent type, verdict, description - are `t334-replay.tsv`). The fixture pool is the 18 trees the day's prompts name,
all free: the real pool existed only from about 14:34Z and who held each tree at each moment is not recoverable, so the
`tree-not-held` rule could not be replayed. `t334-replay2.py` prepends a true marker to five briefs' real prompts for the guard's
measurement rule. The command's sizing was run on a scratch fixture repository holding the real `tasks.md` and `tasks-done.md`, with
`L7R_BUILDER_POOL=0` so no tree was taken.

It covers the coordinating session's own dispatches only. A builder's own Agent calls were not replayed, and a builder sent from a
Workflow script's `agent()` call is not seen by the guard at all (it matches the Agent tool).

## The day's 110 dispatches through the guard

| verdict | count | which |
|---|---|---|
| refused, no marker | 56 | every one a builder's dispatch into a pool tree, T334's own build brief among them |
| refused, any other rule | 0 | none carried a marker |
| passed, defined agents | 36 | spec-fidelity 10, escalation-check 7, impl-drift 6, round-arbiter 4, spec-fidelity-verify 3, quote-check 2, record-format 2, research-pass 1, source-applicability 1 |
| passed, ad-hoc, no pool tree named | 17 | measuring agents, and builders that worked in the clone itself (T259, T250 batches 3, 5, 7 and 8, "Close agenda items 6 and 12") |
| passed, the claims round | 1 | "Claims round for 449 T417", which names a tree and is exempt by its opening words |
| a dispatch that is no builder's, refused | 0 | the escape would have been needed 0 times |

## The five oversized briefs, given a truthful caller

| task | the call | the command | the guard, with that marker on the real prompt |
|---|---|---|---|
| T285 (three jobs of a mechanism's size) | `KIND=fix JOBS=3` | REFUSED: its line names a new mechanism ("a guard refuses") | - |
| T285 | `KIND=build-half JOBS=3` | sized | passes |
| T298 (four jobs) | `JOBS=4`, any kind | REFUSED: at most 3 jobs | a marker of `JOBS=4` is refused too |
| T316 (measure, then build a background step) | `KIND=fix JOBS=2` | passes: "a background step" is no phrase of the test, and today's Makefile defines the targets its line names | - |
| T316 | `KIND=measurement JOBS=2 MEASURES=<n>` | passes | passes: the brief orders its build as `(1) MEASURE ... (2) ...`, a numbered list the narrow rule does not read |
| T308 (a measurement and a build) | `KIND=fix JOBS=2` | passes | - |
| T308 | `KIND=measurement JOBS=2` | passes | refused, but on its `Job 1 (a measurement, ...)` line, by a word of the thing measured: the rule's known false-positive form |
| T315 (one job: seven crates, eight levers) | `KIND=measurement MEASURES=7` (or 15) | REFUSED: at most 6 things | passes |

Beyond "no marker", sizing takes 3 of the 5 from the caller's own words (T285 as a fix, T298, T315). T316 and T308 - a measurement
and a build briefed as two jobs - are caught by nothing reliable; the detectors were not tuned until they fired (filed as 451 T354).
A sixth brief of the day, T347's (measure then fix, 21:14Z), is the form the guard's measurement rule was written from: with a
`KIND=measurement` marker it is refused on its line "Job 2, only if job 1 shows a safe rule: build it in slot.rs's callers".

## The guard's suite, red first

`tests/hooks/test-builder-brief-hooks.sh`, 27 cases: with the guard's branch removed (`decide` returning at its prefilter) 14 passed
and 13 failed; restored, 27 passed and 0 failed.
