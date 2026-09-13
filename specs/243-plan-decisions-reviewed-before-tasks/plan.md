# Feature 243 - plan

**Spec**: `spec.md` (under initial review) | **Research**: `research.md`

## Shape

One module holds every decision the gate makes, and three thin callers use it:

| piece | what it does |
|---|---|
| `scripts/_plan_gate.py` | `owed(spec_dir)` -> the (rule, reason) a feature may not tick for, or nothing; `ticked(tasks_text)`; `tick_permitted(spec_dir, root, escape)`, the whole tick-time decision including the escape; `derive_verdict(decisions)`; `record(spec_dir, review, declared)`; `touched_features(root, rng)` and `push_owed`; a CLI with `owed`, `push <range>` and `record` |
| `scripts/tick-task.py` | calls `tick_permitted()` on the resolved spec directory before `tick()`, and refuses with its message (FR-001, FR-005, FR-008) |
| `scripts/plan-gate.sh` | the push refusal, run by `sync-with-main.sh` directly after `review-gate.sh` (FR-007), on the shape of `entry-gate.sh`: escape first, reason floor, guard log and `dev/bypass-log/` entry, then `_plan_gate.py push` |
| `make plan-verdict F=<feature> FILE=<json> AS=spec-fidelity` | writes `plan-review.json` from the reviewer's JSON, declining without `AS=spec-fidelity` (FR-006) |

Around them: the plan-review mode in `.claude/agents/spec-fidelity.md` (FR-009), the first task in
`.specify/templates/tasks-template.md` (FR-010), `PLAN_REVIEW_OK` classified in the escape census of
`tests/tooling/test_guard_firing_log.py`, a row in the root `CLAUDE.md` guard table, and `make docs` for
the new target.

## Plan decisions

**P1 - the digest is SHA-256 of `plan.md`'s bytes, taken by the reviewer when it begins reading.** The
reviewer's JSON carries `plan_sha256`; `make plan-verdict` refuses when it no longer matches `plan.md`.
That is FR-004 applied at the moment of recording as well as at tick time: a plan edited while the
review ran was not the plan the review read.

**P2 - the verdict is derived, never taken from the reviewer's input.** `record` computes CLEAR or
BLOCKED from the rulings as FR-003 defines them, and refuses an input whose own `verdict` disagrees, so
a typo cannot record CLEAR over a NOT LEGITIMATE ruling. A narrowing decision with no ruling, a within
decision carrying one, or an unknown class is refused. A plan whose decisions the spec already settles
records an empty list and CLEAR.

**P3 - the record's form.** `plan-review.json`:
`{"feature", "plan_sha256", "reviewed" (date), "declared", "decisions": [{"id", "summary", "class":
"within" or "narrowing", "ruling": "LEGITIMATE" or "NOT LEGITIMATE" (narrowing only), "why"}],
"verdict"}`. An `id` is the plan's own label where it has one, otherwise the reviewer's.

**P4 - a ticked task is a column-0 `- [x] ` line in `tasks.md`, either case of x.** That is the line
`make tick` writes and the line a hand edit produces. An indented research box is part of its task, not
a task, so it is not counted.

**P5 - the push reads the pushed content, not the working tree.** `touched_features` takes the
`specs/NNN-*/` directories from `git diff --name-only <range>`, the same derivation `review-gate.sh`
check 1 uses, and reads `tasks.md`, `plan.md` and `plan-review.json` at `HEAD` through `git show`. The
push lands HEAD, so HEAD is what is judged.

**P6 - the escape.** `PLAN_REVIEW_OK` is read from the environment in both places, which a mention in a
command cannot set (the census class `environment`, like `REVIEW_GATE_OK`). The `tick` target exports
it so `make tick ... PLAN_REVIEW_OK="<reason>"` reaches the script. The reason floor is
`_hm_escape.py reason-ok`; both escapes record to the guard log (rule `plan-review-ok`) and to
`dev/bypass-log/`, which `make audit` reads. Each refusal records its own rule: `plan-missing`,
`plan-review-missing`, `plan-review-stale`, `plan-review-blocked`.

**P7 - tests.** `tests/tooling/test_plan_gate.py` drives the module with temporary spec directories
and a temporary git repository: each `owed()` reason, `record`'s refusals and its derived verdict, the
`AS=` decline, `touched_features` over a real range, and `tick-task.py main()` refusing and then
ticking. `scripts/test-plan-gate.sh` is the push script's companion suite (constitution XVIII), driving
it against a fixture repository with an isolated `GUARD_LOG_DIR` and removing any bypass-log entry it
creates. Every refusal is proven by mutation: break it, watch the test go red, restore (SC-008).

**P8 - this feature's own tasks.** The plan-review agent file edit does not reach an agent launched by
type in the same session (the harness gotcha in `docs/spec-kit-and-reviews.md`), so this plan's review
is dispatched with the mode's instructions in the prompt. It runs on this plan once the spec is
FAITHFUL, while implementation proceeds beside it. Its JSON is recorded through `make plan-verdict`
once that target exists, provided this plan has not changed; if it has, it is reviewed again. No task
is ticked before the gate and the record exist, so every tick passes through the gate (SC-009).

## Constitution check

- XVI: the spec is under independent review against `request.md`; this plan is reviewed under the mode
  it adds before its tasks are ticked.
- XVIII: the new push script has a companion suite that `make hooks-test` runs; the tick refusal is
  tested in `tests/tooling/`.
- X clause 13: `_plan_gate.py` and both test files stay far under 1,000 lines.
- Escapes (features 169, 170): environment-read, reason required, recorded, classified in the census.
