# Tasks - 256 defined subagents launch without the root `CLAUDE.md` and the memory index

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing physical.

- [x] T01 the reading: each rule of the root and the two nested `CLAUDE.md` files put to each contract; the rules a check leans on moved into its contract; the table in `research.md` (FR-001)
      research: rendering
      verify: DONE. the rule-by-agent table over all three files in research R1; the moved rules in the twelve contracts
- [x] T02 `omitClaudeMd: true` in all twelve agent files (FR-002)
      research: rendering
      verify: DONE. omitClaudeMd true in all twelve agent files; the tier test green
- [x] T03 the proof: three cases, each with the field and without it; scored against the control; FR-004's second pair if a run misses (FR-003, FR-004)
      research: rendering
      verify: DONE. three cases clean against their controls - 17 turns and 1.82 with the field, 15 and 2.47 without; one leg discarded for a non-verbatim prompt and re-run; research R2
- [x] T04 a real defined agent's first-turn input, before and after (FR-006)
      research: rendering
      verify: DONE. entry-drift from /diagram - 20,435 tokens to 4,477; research R3
- [x] T05 the record: root `CLAUDE.md`, `docs/efficiency-tooling.md`, the three unproven agents and the seven not re-run named (FR-005, FR-006)
      research: rendering
      verify: DONE. root CLAUDE.md and docs/efficiency-tooling.md say it; the three unproven and the seven not re-run named in research R4
- [x] T06 `make hooks-test` and `make quick` green; land DIRECT
      research: rendering
      verify: DONE. make quick and make hooks-test green 2026-09-20; nothing under l7r/ or pool/ changed
- [x] T07 the tier test requires `omitClaudeMd: true` of every agent file; proven red on a file without it (FR-007)
      research: rendering
      verify: DONE. test_every_agent_launches_without_the_claude_md_files - 8 passed; proven red by removing the field from entry-drift (1 failed, naming it), green again restored
- [x] T08 both fidelity contracts distinguish enforcing what was asked from unrequested verification; the seeded round-1 run (FR-008)
      research: rendering
      verify: DONE. both fidelity contracts carry the GM's distinction, with the test-versus-guard wording sharpened after R6; the seeded proof kept the guard but so did the control, so SC-007 is recorded UNMET and accepted by the GM (Amendment 2, FR-012); research R7
- [x] T09 a make target wraps the scatter parse and `settlement-review` names it; the `(Tools: ...)` tails and the tier-table paths corrected (FR-009)
      research: rendering
      verify: DONE. make scatter-bases wraps the engine's parse (scripts/_scatter_bases.py, 4 tests; Sawada 20,713 blades) and settlement-review names it; the three (Tools: ...) tails cut; the tier table cited by its real path in seven contracts
- [x] T10 eight seeded pairs - entry-drift, escalation-check, quote-check, source-applicability, source-reader, spec-fidelity on recorded cases, building-review and size-audit on frozen defective sheets - scored; settlement-review and perf-audit priced for the GM; the tally restated (FR-010, FR-011)
      research: rendering
      verify: DONE. eight pairs scored finding by finding by an independent reader - variance in six, a one-sided loss in entry-drift (repaired by a moved rule, re-run DRIFTED) and in spec-fidelity (not settled, raised with the GM); settlement-review and perf-audit priced; the tally ten of twelve; research R6
- [ ] T11 `make hooks-test` and `make quick` green; land
      research: rendering
