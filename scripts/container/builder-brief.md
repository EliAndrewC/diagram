# The standing orders of a code builder's brief

Load this file when: you, the coordinating session, are about to dispatch a builder for a code task (feature 451 T237, the GM
2026-11-25: "sounds good please do that ASAP"). Paste the block below into the brief after the task's own text.

Why: on 2026-11-24/25 five 449 code builders and the 451 T218-T222 builder hit the 300k context cap and handed off, each
handoff costing a fresh builder 10 to 20 minutes of re-reading. One builder did the fix, the measurement sweep, the plan
section, the plan review AND the claims round. The claims round (agents, replies, re-bundles) is the part that runs it out.

Enforced (451 T237, `rust/guard/src/guards/context_cap_hooks/split.rs`): a builder whose brief holds a line opening
`STOP POINT` is refused a `claims-triage` or `impl-drift` dispatch (an Agent call, or a Workflow naming either), and its
context-cap handoff says it stops there; keep that line in every code builder's brief. A claims-round dispatch's prompt opens
`Run the claims round for feature ...` and is never held.

SIZING, before you write the brief (the GM 2026-11-25, pre-approving the talk's item 12; `docs/process-decisions.md`, "The
builders' context cap stays at 300k, builders stay, and briefs are sized"; audited as `dev/audits/builder-brief-sizing.md`):

- ONE task a builder.
- At most THREE jobs in a brief. A measurement or sweep, a build, a found defect's fix and written content each count as one.
- A task expected to edit more than about three files, or needing a measurement first, is SPLIT into builders that hand results
  along, a measuring agent first: its report (the figures, the paths, the commands) is the next builder's brief.
- A one-turn edit is yours, the coordinating session's, not a builder's.
- A builder's commit reaches the clone by `make carry FROM=<its worktree>` run in the clone (451 T292), never a hand `git cherry-pick`: `make land` refuses a carry-over left unfinished.
- TWO code builders at once, each in a REUSED worktree (its build cache warm); three or four at once only for batches that
  compile nothing (`docs/process-decisions.md`, "Two code builders at once"; `dev/audits/parallel-builder-count.md`).

Why: of 97 builders briefed since 2026-11-24, a brief of 4 or more jobs handed off 52% of the time against 16-22% at 1-3 jobs;
4 or more files edited, 39-45% against 22% at three or fewer; a brief that began with a measurement, 46% against 25%. A one-turn edit by the
coordinator costs about half a small builder's tokens (0.3-0.4M against 0.65M); past 5 minutes or several files it costs about
1.5M, so that work goes to a builder (`dev/measurements/2026-11-25/talk-measures/`, `m1b.txt` and `m2b.txt`). The three-job and three-file
limits are GUESS knobs set where the measured rate steps up.

The block's first line, `Blocks:` (451 T243, the GM 2026-11-25: "a minute should count as blocking. When something else is
waiting on it to be done before it can be started"), is written on the dispatch's event-log line and read by `make task-time`:
the task named is the one this builder's time blocks; with none, the builder's own task. A command takes the same clue as
`L7R_BLOCKS=<feature>:T<n>` (or `none`) before its `make`.

```
Blocks: <feature> T<n>   (the task whose next step waits on this work; `Blocks: none` if it runs beside other work)
STOP POINT. Your work ends when ALL of these hold, and not before:
 - the code is done, red-first, with 100% line coverage on new Rust;
 - `make closing-checks T=<task>` (run_in_background) is green on the final code;
 - the plan section is written, `make decide` passes, and spec-fidelity MODE 4 is CLEAR (`make plan-delta F=<n>`);
 - `make claims-triage` has run (it is mechanical) and you have NOT dispatched `claims-triage` or `impl-drift` yourself;
 - the Occasions line is written and `scripts/gates/l7r-gate.sh reviews owed --root "$PWD" --check-drawn` is silent.
Then report: what you built and measured, the claims you touched or restated (keys), what `make claims-owed` lists, and
the exact paths to commit. The coordinating session runs the claims round (the claims-triage agent, make claims-bundle,
impl-drift, make claims-checked) as its own dispatch; a DRIFTED fix: claim comes back to a small builder.
Prefix every scratch file you write with your task id (`t<n>-`): builders share one scratchpad (451 T271).
Do NOT stage, commit, land or push. Never rewrite history.
```
