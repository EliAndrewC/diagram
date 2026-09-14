# Tasks - 246 The finished-run guard sees the waiter

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
physical behind it.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code; the plan
      reviewed (MODE 4) before any tick
      research: rendering
      verify: DONE. spec-fidelity FAITHFUL at round 1 (one aside, not a finding); plan review MODE 4 CLEAR at round 1, 8 decisions all within, plan-review.json recorded by the subagent
- [x] T02 the guard: `judge_runs`, the stop branch's three outcomes, the root-keyed marker, the message
      (FR-001 to FR-005)
      research: rendering
      verify: DONE. finished-run-hooks.sh: judge_runs (root live makes judged tracked / watched / unwatched from /proc by pid - a claude ancestor, a loop naming the stdout file), the stop branch lets tracked and watched roots through with one context line each recorded permitted/tracked-run and permitted/waiter-armed, refuses only an unwatched detached root keyed on the ROOT pids, and the refusal names the run's own log and says a background-mode run needs no loop; a judge <clone> mode
- [x] T03 the suite's new cases on real processes (FR-006); `make hooks-test` green
      research: rendering
      verify: DONE. test-finished-run-hooks.sh 46 passed: 6b a claude-named stand-in harness (tracked, exit 0, context line, no refusal), 6c a detached run with a waiter on ANOTHER file refused with the loop prescribed on the run's own log and the needs-no-loop line, then a waiter on its log let through with the waiter named, 6d a two-phase make refused once and not again with p2 the live child, both new rules in the firing log; two fixture facts recorded in the suite (a process is reparented to init only when its parent exits; bash -c execs into its last command); make hooks-test green (3 suites, 21 unchanged, hooks area stamped)
- [x] T04 the record (FR-007): the header, the CLAUDE.md row, the future-work entry; SC-003 observed on this
      feature's own gate; land DIRECT
      research: rendering
      verify: DONE. the hook header, the CLAUDE.md row, future-work/cross-cutting.md (the lost-notification fallback, deferred until a lost notification is observed). SC-003 CANNOT be observed before landing: the session's hooks run from the mirror's /diagram/scripts, and on this feature's own hooks-test (started through the Bash tool's background mode) the MIRROR'S old rule refused the turn-end - the defect itself, observed one more time. The mechanical proof is the suite's 6b case; the live observation is taken after the push and appended below. Landing DIRECT
      SC-003 OBSERVED after landing (2026-09-14, this session): `make page-check` started through the Bash tool's background mode, the turn ended while it ran, no refusal - the guard log records `permitted/tracked-run` for that pid with the harness's task file as its output, and the harness's own completion notification followed
