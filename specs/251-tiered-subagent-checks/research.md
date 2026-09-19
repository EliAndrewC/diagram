# Research - 251 subagent checks tiered by model and effort

## R1 - the census (task zero)

Filled by T01 from `make agent-census`; the rows also land in `measurements.json`. A first rough pass
with `jq` on 2026-09-19 (every project, output undercounted - see R2) ordered the consumers
`general-purpose` (363 runs), `spec-fidelity` (447), `settlement-review` (156), `source-reader` (117),
`quote-check` (65), `record-format` (38), `entry-drift` (52), `source-applicability` (26), and showed
cached input two orders of magnitude above output for every one of them: what a check costs is the
context it re-reads each turn, so the model a check runs on and the number of turns it takes move the
bill far more than its thinking does. That is why the script pre-passes (fewer turns, less page text in
context) sit beside the model changes, and it is the measured form of the proposal's "input-heavy
agents are moved by model choice, not by effort".

## R2 - one usage figure per message

**Decision:** usage is folded per `message.id` as the per-field maximum. **Why:** a transcript writes
one record per content block of an assistant message, each carrying the message's usage as it stood;
taking the first record (what `sort -u` did in the rough pass) reads an early `output_tokens`. T01
verifies the shape on a real transcript and records what it found here. **Alternative:** summing every
record - counts a message once per block.

## R3 - where the agent's name is a key

`grep -rn spec-fidelity scripts Makefile .claude/skills/diagram/Makefile .claude/settings.json
container-scripts` on 2026-09-19. Keyed on the dispatch TYPE: `scripts/_hm_review_round.py` (`AGENT`,
and `judge`'s first test). Keyed on the name as the PLAN reviewer's declaration, which stays
`spec-fidelity`: `scripts/_plan_gate.py` (`REVIEWER`), the `plan-verdict` target. A list of authorized
agents: `container-scripts/append-system-prompt.md`. Text only, not keys: `review-gate.sh` (greps the
spec for FAITHFUL beside one of several words), `plan-gate.sh`, `pair-hooks.sh`, `discard-hooks.sh`,
`_review_prereq.py`, `spec-lint.py`, the skill Makefile's comments. `escalation-hooks.sh`'s roster is
`settlement-review building-review size-audit` and does not hold the spec reviewer.
`previous_verdict` in `_hm_review_round.py` finds the last verdict by the feature directory the
transcript names, so a verdict returned by the twin is found as one returned by `spec-fidelity` is.

## R4 - does the harness honor a changed `subagent_type`?

The hook already returns the WHOLE tool input as `updatedInput` (`updated = dict(ti)`), with `prompt`
replaced, and the harness runs what it is given. Whether the type is honored is proven on this
feature's own next later round: the dispatch's transcript meta (`agentType`) says which agent ran.
Result recorded here by T07.

## R5 - the seeded-fault runs

Filled by T08: per downgraded agent, the artifacts (commit and path, or the recorded report), the
findings the recorded result had, hits, misses, new findings judged real or false, tokens for the run,
and the agent's per-run mean from R1.

## R6 - an unset effort is the session's

Verified 2026-09-19 in the installed 2.1.278 binary: the subagent's request effort is read as the
definition's `effort`, else the session's layered effort; `~/.claude/settings.json` sets `effortLevel`
to `high`. So the agents pinned at `high` run as they did, and the ones pinned at `medium` are the
effort downgrades FR-011 tests. The agent-definition schema lists `low`, `medium`, `high`, `xhigh`,
`max`.
