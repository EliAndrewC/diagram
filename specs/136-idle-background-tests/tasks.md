# Tasks: Idle Sessions Run the Expensive Tests in the Background (136)

Checked off only when verified (the hooks-test and quick targets). Every task classified per
constitution v2.12.0; all are `research: procedure` (no physical claim is made).

- [x] T01 spec written from the GM's verbatim request; `spec-fidelity` review (constitution XVI) - verdict recorded in spec.md Status
- [x] T02 the guard script `scripts/idle-tests-hooks.sh`: `stop` arms (state file + detached timer, no-op if armed), `prompt` disarms and prints the last verdict, `timer` waits (stagger, suspend restart, lock + deferral, give-up), runs the idle-tests target, records `dev/idle-log/`; never in main; seams only in a fixture
- [x] T03 the companion `scripts/test-idle-tests-hooks.sh` (FR-007): arm/disarm, stagger band + determinism, suspend restart, lock exclusion + deferral, record + surfacing, never-in-main, seams refused outside a fixture, session-gone exit; proven to FIRE by breaking each rule once
- [x] T04 wiring: `.claude/settings.json` Stop + UserPromptSubmit; Makefile `idle-tests` target (= the maps target); `dev/idle-log/CLAUDE.md`
- [x] T05 doctrine: root CLAUDE.md guard-table row + iteration bullet; `docs/iteration-loop.md`; skill `dev/switches.md` (the lock's cost now has a nightly look); the constitution unchanged
- [ ] T06 hooks-test green (16 suites, 2026-08-28 01:1xZ) and quick green - DONE; one real arming observed on this session - PENDING THE LANDING: the harness reads the hook wiring from main's `.claude/settings.json` and `/diagram/scripts/`, so the Stop hook cannot fire from a clone; observed on the first turn after the push, recorded here
- [ ] T07 push (DIRECT route: scripts + docs + config; a green hooks-test stamp) - after T99: the GM chose the review path ("I will review the decisions that you made when the feature is Nearly complete"), so the landing follows the acceptance
- [ ] T99 **the GM accepts the decisions D1-D7** (plan.md) - tickable only on the GM's explicit word, recorded here verbatim
