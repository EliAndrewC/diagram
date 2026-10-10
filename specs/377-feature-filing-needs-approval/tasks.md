# Tasks - feature 377, no feature is filed without the GM's approval

Every task is tooling: nothing a map draws changes and no physical decision is made, so each is `research: rendering`.

## Occasions

- none: no map, sheet, glyph or placement changes

## Tasks

- [x] T01 The decider and the one definition of the line (plan D1-D4): `scripts/hooks/lib/hm_approval.py` - FIRST = 377, the line's regex, the three-word minimum, the GM's messages from the transcript (typed prompts, AskUserQuestion answers), NEW (HEAD, staged rename, slug)
      research: rendering
      verify: DONE. hm_approval.py: FIRST 377, the line regex, three-word minimum, typed prompts + mid-turn queued_command (human) + answered AskUserQuestion, NEW by HEAD/staged rename/departed slug; every branch exercised by the 29-case suite
- [x] T02 The guard (plan D5, D6, D8): `scripts/hooks/feature-approval-hooks.sh`, no escape, refusal naming the failed check and the exact line; registered in `.claude/settings.json` beside conflict-marker-hooks.sh
      research: rendering
      verify: DONE. feature-approval-hooks.sh, no escape, refusal names the failed check and the exact line; registered in .claude/settings.json beside conflict-marker-hooks.sh (JSON validated)
- [x] T03 The suite (FR-010, SC-001, SC-002): `tests/hooks/test-feature-approval-hooks.sh` over a real git tree and fixture transcripts - no line, short quote, foreign quote, the GM's quote at add and at commit, a sub-session's prompt (sdk) not counted, an isMeta notice not counted, an AskUserQuestion answer, a rename, an existing feature edited, a feature below 377, an unrelated commit; the refusal text pinned; the guard proven to fire by removing its call
      research: rendering
      verify: DONE. tests/hooks/test-feature-approval-hooks.sh 29/29 over a real git tree and fixture transcripts; make hooks-test green; fires only through the decider (stripped-hook case)
- [x] T04 The push backstop (plan D7, FR-004, SC-003): spec-lint check 6 importing FIRST and `form_problem` from hm_approval; a test in `tests/tooling/test_spec_lint.py`; a run over today's `specs/` reports nothing (SC-002)
      research: rendering
      verify: DONE. spec-lint check 6 imports FIRST/FORM/form_problem from hm_approval; test_spec_lint.py 42 passed incl. two check-6 tests; selftest ok; a run over every specs/ directory reports nothing (SC-002)
- [x] T05 The text (FR-007, FR-009, plan D8): CLAUDE.md's workflow bullet and guard-table row; `docs/spec-kit-and-reviews.md` and `docs/guards.md`; `make claim`'s printed reminder; `.claude/agents/spec-fidelity.md`'s subject check
      research: rendering
      verify: DONE. CLAUDE.md bullet + guard row (Defer work by filing a feature gone, SC-004); spec-kit-and-reviews.md and guards.md records; claim prints the approval line (test_claim_feature.py asserts it); spec-fidelity Mode 2 question 7
- [x] T06 Close: `make hooks-test` and the tooling tests green; landed
      research: rendering
      verify: DONE. make hooks-test green, tooling tests 85 passed, make quick clean; landed by the push that carries this tick
