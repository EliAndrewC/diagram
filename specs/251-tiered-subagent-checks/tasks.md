# Tasks - 251 subagent checks tiered by model and effort, the mechanical parts in scripts

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
physical behind it.

- [ ] T01 the census: `scripts/_agent_census.py`, `make agent-census`, its test module; the first run
      recorded in `research.md` R1 and `measurements.json` (`--until` makes it re-runnable by `make figures`); R2
      confirmed on a real transcript (FR-001)
      research: rendering
- [ ] T02 the tier table in `tests/test_agent_models.py` and `model:` + `effort:` in every agent file,
      each file's description and Model paragraph restated to the present ruling (FR-002, FR-007)
      research: rendering
- [ ] T03 `scripts/_quote_verbatim.py`, `make quote-verbatim`, its test module with offline fixtures -
      the seeded hyphen-for-dash and spelling differences report DIFFERS, the exact quote VERBATIM
      (FR-003, SC-002)
      research: rendering
- [ ] T04 `quote-check` rewritten around the script's report, output format unchanged; the
      run-the-script-first rule in `research/CLAUDE.md`, root `CLAUDE.md`, `docs/research-doctrine.md`
      (FR-004)
      research: rendering
- [ ] T05 `scripts/_record_prepass.py`, `make record-prepass`, its test module; `record-format` gains
      step 0 (FR-005)
      research: rendering
- [ ] T06 `scripts/_size_table.py`, `make size-table`, its test module; `size-audit` Method step 1
      starts from the table (FR-006)
      research: rendering
- [ ] T07 `.claude/agents/spec-fidelity-verify.md`; `_hm_review_round.py` admits either type and routes
      a rewritten round to the twin; new suite cases; the authorized list; the routing itself was proven
      by probe before this task (research R4) (FR-008)
      research: rendering
- [ ] T08 the seeded-fault runs, R5 filled, any agent that missed stepped back up and re-run, the
      table, the file and FR-002 moved together (FR-011, SC-004, SC-005)
      research: rendering
- [ ] T09 the record: root `CLAUDE.md`, `docs/spec-kit-and-reviews.md`, `docs/research-doctrine.md`,
      `docs/guards.md`, `docs/efficiency-tooling.md`, `research/CLAUDE.md`, the memory file; the ad-hoc
      rule stated, R1's inherit count recorded (FR-010, FR-012)
      research: rendering
- [ ] T10 `make hooks-test` and `make quick` green; land DIRECT (SC-006)
      research: rendering
