# Quickstart - feature 451, how to see it working

## The retrospective (User Story 1)

```bash
make where-time F=451 SINCE=2026-11-21T14:00:00Z UNTIL=2026-11-22T04:00:00Z
make feature-report F=451
```

Read off, per task and in total: tests, compile, gate, land, review, background run, model; the wall clock on the critical path beside
the summed agent-minutes; the rework (refused landings, plan re-rounds); each agent's minutes and tokens under its task. "waiting on
work" should be under a tenth of the wall clock (SC-001).

## Each refusal (FR-012), red first

```bash
make rust-test CRATE=rust/guard          # the guard tests: each refusal's red fixture refused, its quiet case passing
make hooks-test                           # every guard's suite, each shard under about 20 s (SC-004)
make rust-test CRATE=rust/gate/crates/plan   # FR-009's five cases
make rust-test CRATE=rust/gate/crates/land   # T="T1,T2" lands both
make rust-test CRATE=rust/gate/crates/task   # task-add withdraws a red line
```

By hand, in a scratch clone:

- `(make static > /tmp/s.log 2>&1) &` in a Bash call: refused, naming `run_in_background`. The same `make static` with
  `run_in_background: true`: passes.
- A third `make static` after `make task-start F=451 T=T02` and two runs: refused, naming `l7r-gate.sh rust test --crate <dir>`;
  `STATIC_OK="a reason here" make static` passes and `make guard-log GUARD=static-runs` shows the escape.
- `make decide F=<n> T=<t>` on a section whose found-and-left line reads "the X is wrong, left": refused with the form.
- `make land F=<n> T="T1,T2" NOTE=...`: both tasks land.

## The event lines (FR-001 to FR-004)

```bash
tail -5 "$(git rev-parse --git-common-dir)/l7r-events/451-time-retro-and-efficiency.jsonl"   # the new BgEnd, Phase and cost lines
```
