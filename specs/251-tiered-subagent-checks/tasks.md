# Tasks - 251 subagent checks tiered by model and effort, the mechanical parts in scripts

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling, nothing
physical behind it.

- [x] T01 the census: `scripts/_agent_census.py`, `make agent-census`, its test module; the first run
      recorded in `research.md` R1 and `measurements.json` (`--until` makes it re-runnable by `make figures`); R2
      confirmed on a real transcript (FR-001)
      research: rendering
      verify: DONE. make agent-census reads 1,160 recorded runs; usage folded per message id at its maximum (R2 verified on a real transcript: 5 then 262 output tokens on one id); --until makes it re-runnable and make figures re-ran it with 0 moved counts; R1 and measurements.json carry the census; tests/tooling/test_agent_census.py 11 passed
- [x] T02 the tier table in `tests/test_agent_models.py` and `model:` + `effort:` in every agent file,
      each file's description and Model paragraph restated to the present ruling (FR-002, FR-007)
      research: rendering
      verify: DONE. tests/test_agent_models.py holds TIERS and 7 tests pass: every agent file pins model and effort, none inherits, each agrees with the table, a file with no row fails; all twelve agent files restated to the present ruling
- [x] T03 `scripts/_quote_verbatim.py`, `make quote-verbatim`, its test module with offline fixtures -
      the seeded hyphen-for-dash and spelling differences report DIFFERS, the exact quote VERBATIM
      (FR-003, SC-002)
      research: rendering
      verify: DONE. scripts/_quote_verbatim.py + make quote-verbatim [NOTES=]; tests/tooling/test_quote_verbatim.py 16 passed offline - a hyphen for the source's dash and an American spelling each report DIFFERS with the page's text, the exact quote VERBATIM (SC-002); live on ways.html it found a wrong comma character and two paraphrases quoted as passages
- [x] T04 `quote-check` rewritten around the script's report, output format unchanged; the
      run-the-script-first rule in `research/CLAUDE.md`, root `CLAUDE.md`, `docs/research-doctrine.md`
      (FR-004)
      research: rendering
      verify: DONE. quote-check.md rewritten around the script's report, verdict vocabulary and Output untouched; the run-the-script-first rule is in root CLAUDE.md, research/CLAUDE.md and docs/research-doctrine.md
- [x] T05 `scripts/_record_prepass.py`, `make record-prepass`, its test module; `record-format` gains
      step 0 (FR-005)
      research: rendering
      verify: DONE. scripts/_record_prepass.py + make record-prepass [SECTION=]; record-format.md gains step 0; tests pass on a fixture and on the real ways.html (make sure is not a make target; a linked code span is a source key)
- [x] T06 `scripts/_size_table.py`, `make size-table`, its test module; `size-audit` Method step 1
      starts from the table (FR-006)
      research: rendering
      verify: DONE. scripts/_size_table.py + make size-table; on hayakawa-magistracy.svg 82 rects, 7 wall gaps with the 3 ft wall inherited from its group; a rotation is flagged not applied; size-audit.md Method step 1 starts from the table
- [x] T07 `.claude/agents/spec-fidelity-verify.md`; `_hm_review_round.py` admits either type and routes
      a rewritten round to the twin; new suite cases; the authorized list; the routing itself was proven
      by probe before this task (research R4) (FR-008)
      research: rendering
      verify: DONE. spec-fidelity-verify.md exists; _hm_review_round.py admits either type and sets subagent_type on the rewrite; test-review-round-hooks.sh 49 passed incl. the new section 9; routing proven by probe BEFORE this task (R4: reply I AM PROBE-B, meta agentType probe-b); append-system-prompt.md lists the twin
- [x] T08 the seeded-fault runs, R5 filled, any agent that missed stepped back up and re-run, the
      table, the file and FR-002 moved together (FR-011, SC-004, SC-005)
      research: rendering
      verify: DONE. seventeen seeded runs scored in R5 against the recorded replies: quote-check, entry-drift and escalation-check held at opus/medium; record-format and source-reader on sonnet and the twin at medium each MISSED a recorded finding and went back to opus/high, table + file + FR-002 together; trimmed and not re-run at the stepped-back tier by the GM's instructions of 2026-09-19 (request.md messages four and five)
- [x] T09 the record: root `CLAUDE.md`, `docs/spec-kit-and-reviews.md`, `docs/research-doctrine.md`,
      `docs/guards.md`, `docs/efficiency-tooling.md`, `research/CLAUDE.md`, the memory file; the ad-hoc
      rule stated, R1's inherit count recorded (FR-010, FR-012)
      research: rendering
      verify: DONE. root CLAUDE.md, docs/spec-kit-and-reviews.md, docs/research-doctrine.md, docs/guards.md, docs/efficiency-tooling.md, research/CLAUDE.md state the tiers that passed and the ad-hoc rule with R1's count (72 no-model runs, 62 on Fable); docs/make-targets.html regenerated, test_make_docs green
- [x] T10 `make hooks-test` and `make quick` green; land DIRECT (SC-006)
      research: rendering
      verify: DONE. make hooks-test green (3 suites run, 22 unchanged) and make quick clean on 2026-09-19; nothing under l7r/ or pool/ changed (git diff --stat confirms), so the delta routes DIRECT
