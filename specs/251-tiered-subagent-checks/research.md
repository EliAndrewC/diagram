# Research - 251 subagent checks tiered by model and effort

## R1 - the census (task zero)

Taken 2026-09-19 with `make agent-census` over every recorded subagent run of this repository's
sessions that started before 2026-09-19 (1,160 runs; `python3 scripts/_agent_census.py --until 2026-09-19 --record ...` is the re-runnable form, keyed `census.*` in `measurements.json`). "Weight" prices a
run at Opus list rates (fresh input 6.25, cached input 0.5, output 25 per million - cache-creation's
1.25x applied to all fresh input, so a slight overstatement) purely to put the four token columns on
one scale; it is a relative weight, not a bill, and the GM's plan is not metered this way.

| agent | runs | turns/run | input/run | output/run | weight/run | total weight | output share | cached-input share |
|---|---|---|---|---|---|---|---|---|
| `general-purpose` (ad hoc) | 295 | 22 | 3.89 M | 25.8 k | 3.70 | 1,092 | 17% | 50% |
| `settlement-review` | 123 | 43 | 6.63 M | 44.1 k | 5.54 | 681 | 20% | 58% |
| `spec-fidelity` | 416 | 9 | 0.84 M | 11.8 k | 1.34 | 556 | 22% | 28% |
| `quote-check` | 65 | 14 | 3.50 M | 28.5 k | 3.96 | 257 | 18% | 41% |
| `source-reader` | 117 | 10 | 1.44 M | 21.8 k | 2.19 | 256 | 25% | 29% |
| `record-format` | 38 | 17 | 4.52 M | 36.7 k | 5.18 | 197 | 18% | 40% |
| `source-applicability` | 26 | 19 | 4.06 M | 28.6 k | 4.37 | 114 | 16% | 43% |
| `entry-drift` | 52 | 6 | 0.77 M | 5.7 k | 1.47 | 76 | 10% | 20% |
| `perf-audit` | 10 | 17 | 1.49 M | 18.6 k | 1.81 | 18 | 26% | 38% |
| `escalation-check` | 7 | 11 | 0.87 M | 9.8 k | 1.18 | 8 | 21% | 33% |

What it says:

1. **Output, thinking included, is 10-26% of what a check costs; input is the rest.** Roughly half of
   every agent's output is thinking. So an effort setting can move perhaps a tenth of a check's cost
   directly; its larger effect is through TURNS, because every turn re-reads the whole context
   (`settlement-review` averages 43 turns and 6.6 M input tokens a run). The model a check runs on moves
   all of it. This confirms the proposal's ordering: model first, turns second (the script pre-passes -
   fewer fetches and less page text in context), effort third.
2. **The largest consumer is the ad-hoc agent, not a named check**: 295 `general-purpose` runs at a
   total weight of 1,092. Of those, **72 were dispatched with no model and 62 of the 72 ran on Fable**
   (`claude-fable-5-1` x48, `claude-fable-5` x14) - the model the GM said is "simply not sufficiently
   available". Another 19 `settlement-review` runs ran on Fable from the period when that file said
   `inherit`. This is FR-010's measurement, and the figure that goes to the GM with the hook question.
3. **`record-format` is the second most expensive check per run** (5.18, above `quote-check`), which
   the proposal did not expect; its move to Sonnet with a pre-pass is worth more than it looked.
4. **`settlement-review` is the most expensive per run and second in total.** FR-009 leaves it on Opus
   at high by the GM-approved proposal; its row here is the baseline the deferred measurement needs.
5. **Does this reorder the work?** No task is removed and the order stands. The emphasis moves: the
   ad-hoc rule (FR-010) is worth more than any single named tier, and T09 says so where the rule is
   written.

The earlier rough pass, kept for R2's sake: a first pass
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
taking the first record (what `sort -u` did in the rough pass) reads an early `output_tokens`. Verified
2026-09-19 on a real transcript: message `msg_011Cepur7ass...` appears twice, its `thinking` block with
`output_tokens` 5 and its `tool_use` block with 262, the cached input identical on both. The rough pass
reported 24,528 output tokens for `quote-check`; folded correctly it is 1,854,079. **Alternative:** summing every
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

**Yes - proven 2026-09-19 by a probe, before FR-008 relies on it** (the plan review's round 1 refused
a deferred proof, rightly: the spec's Assumption says the plan verifies it first). A throwaway project
in the scratchpad held two agent files, `probe-a` and `probe-b` (each told to reply with its own name,
`probe-b` also pinning `effort: low`), and a PreToolUse hook on `Agent` returning
`updatedInput = tool_input + {subagent_type: "probe-b"}` for a dispatch of `probe-a`. A headless session
(`claude -p`, Claude Code 2.1.278) was told to dispatch `probe-a` once. The reply was `I AM PROBE-B`, and
the run's transcript meta reads `"agentType":"probe-b"`. So the harness runs the type the hook returns,
with that agent's own frontmatter. The spec's fallback is not needed.

**What the probe also showed: this session loads its agents and hooks from the MIRROR.** The session's
project directory is `/diagram`, its hooks are wired by absolute path (`/diagram/scripts/...`) and the
agent types it can dispatch are `/diagram/.claude/agents/`, so an agent file or a hook changed in the
CLONE is not what an Agent dispatch from this session runs until the change lands and the mirror
fast-forwards. A seeded run dispatched with the Agent tool would therefore test the OLD tier. The seeded
runs (R5) go through a headless session started in the clone instead - `claude -p --agent <name>` with
the clone as its working directory - which loads the clone's agent file, its `model:` and its `effort:`.

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
