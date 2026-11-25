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
Do NOT stage, commit, land or push. Never rewrite history.
```
