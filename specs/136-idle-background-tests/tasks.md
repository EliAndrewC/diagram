# Tasks: Idle Sessions Run the Expensive Tests in the Background (136)

Checked off only when verified (the hooks-test and quick targets). Every task classified per
constitution v2.12.0; all are `research: procedure` (no physical claim is made).

- [x] T01 spec written from the GM's verbatim request; `spec-fidelity` review (constitution XVI) - verdict recorded in spec.md Status
- [ ] T02 the guard script `scripts/idle-tests-hooks.sh`: `stop` arms (state file + detached timer, no-op if armed), `prompt` disarms and prints the last verdict, `timer` waits (stagger, suspend restart, lock + deferral, give-up), runs the idle-tests target, records `dev/idle-log/`; never in main; seams only in a fixture
- [ ] T03 the companion `scripts/test-idle-tests-hooks.sh` (FR-007): arm/disarm, stagger band + determinism, suspend restart, lock exclusion + deferral, record + surfacing, never-in-main, seams refused outside a fixture, session-gone exit; proven to FIRE by breaking each rule once
- [ ] T04 wiring: `.claude/settings.json` Stop + UserPromptSubmit; Makefile `idle-tests` target (= the maps target); `dev/idle-log/CLAUDE.md`
- [ ] T05 doctrine: root CLAUDE.md guard-table row + iteration bullet; `docs/iteration-loop.md`; skill `dev/switches.md` (the lock's cost now has a nightly look); the constitution unchanged
- [ ] T06 hooks-test green (the new companion in the roster), quick green; one real arming observed on this session (the state file after a Stop, the disarm at the next prompt)
- [ ] T07 push (DIRECT route: scripts + docs + config; a green hooks-test stamp)
- [ ] T99 **the GM accepts the decisions D1-D7** (plan.md) - tickable only on the GM's explicit word, recorded here verbatim
