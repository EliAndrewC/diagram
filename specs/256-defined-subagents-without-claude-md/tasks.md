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
