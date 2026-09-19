# Tasks - 252 an ad-hoc agent dispatch names its model, or is refused

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling.

- [x] T01 `scripts/agent-model-hooks.sh`, `scripts/agent-model-rule.txt`, `scripts/test-agent-model-hooks.sh`
      (FR-001 to FR-003)
      research: rendering
      verify: DONE. agent-model-hooks.sh + agent-model-rule.txt + test-agent-model-hooks.sh: 20 passed - refusals (general-purpose, omitted type, Explore, empty model), passes (named model incl. fable, pinned type, fork recorded, Bash, broken payload), the message carries both models, the session and the re-send; an empty model once shifted the fields and passed - fixed with a unit separator
- [x] T02 wired in `.claude/settings.json`; the firing-log row; root `CLAUDE.md` and `docs/guards.md` rows (FR-004)
      research: rendering
      verify: DONE. wired first in the Agent matcher of .claude/settings.json; tests/tooling/test_guard_firing_log.py gains three rows and passes (46); root CLAUDE.md table row and docs/guards.md row added
- [x] T03 `make hooks-test` and `make quick` green; the suite goes red with the refusal branch deleted; land
      DIRECT (SC-003)
      research: rendering
      verify: DONE. make hooks-test green and make quick clean on 2026-09-19; the suite run against a mutant copy with the refusal removed went red (16 passed, 4 failed) and green against the real guard (20 passed)
