# Tasks - 252 an ad-hoc agent dispatch names its model, or is refused

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering` - tooling.

- [ ] T01 `scripts/agent-model-hooks.sh`, `scripts/agent-model-rule.txt`, `scripts/test-agent-model-hooks.sh`
      (FR-001 to FR-003)
      research: rendering
- [ ] T02 wired in `.claude/settings.json`; the firing-log row; root `CLAUDE.md` and `docs/guards.md` rows (FR-004)
      research: rendering
- [ ] T03 `make hooks-test` and `make quick` green; the suite goes red with the refusal branch deleted; land
      DIRECT (SC-003)
      research: rendering
