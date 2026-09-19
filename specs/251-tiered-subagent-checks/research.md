# Research - 251 subagent checks tiered by model and effort

## R1 - the census (task zero)

Taken 2026-09-19 with `make agent-census` over every recorded subagent run of this repository's
sessions that started before 2026-09-19 (1,160 runs; `python3 scripts/_agent_census.py --until 2026-09-19 --record ...` is the re-runnable form, keyed `census.*` in `measurements.json`). "Weight" prices a
run at Opus list rates (fresh input 6.25, cached input 0.5, output 25 per million - cache-creation's
1.25x applied to all fresh input, so a slight overstatement) purely to put the four token columns on
one scale; it is a relative weight, not a bill, and the GM's plan is not metered this way.

| agent | runs | turns/run | input/run | output/run | weight/run | total weight | output share (observed 2026-09-19; method: `make agent-census`) | cached-input share |
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

1. **Output, thinking included, is 10-26% of what a check costs (observed 2026-09-19; method: the census table above); input is the rest.** Roughly half of
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

## R5 - the seeded-fault runs (2026-09-19)

**Method.** Each case re-runs a RECORDED check under its new tier: the prompt the past session sent and the
reply the Opus agent gave are read from the run's transcript (`measure/seeded.py`), a detached worktree of
this clone at the last commit before the recorded run gives the agent the files that run read, the current
agent files are copied in, and the run is a headless session started in the worktree (`claude -p --agent
<name>`, hooks off - R4 says why it is not an Agent dispatch). The GM asked for the runs to stay small
(2026-09-19: *"redoing old work is only useful insofar as it does give us sensible measurements"*), so
the three large recorded runs were cut to slices: `quote-check` to 23 of a run's 102 notes (two slices, 17 + 6, in ONE run), `record-format`
to one scoped page and one section. Seventeen runs in all. "Weight" is R1's scale (Sonnet priced at its own
list rates); recorded figures are that run's own transcript, not the agent's mean.

| case | tier tested | recorded result (observed 2026-09-19; method: read from the run's transcript) | new result | verdict | turns rec -> new | input rec -> new | weight rec -> new |
|---|---|---|---|---|---|---|---|
| entry-drift farmhouse | opus / medium | DRIFTED | DRIFTED, same passage | hit | 7 -> 7 | 0.95 M -> 0.36 M | 1.65 -> 0.97 |
| entry-drift notice board | opus / medium | DRIFTED | DRIFTED | hit | 4 -> 5 | 0.52 M -> 0.36 M | 1.37 -> 0.99 |
| entry-drift well | opus / medium | DRIFTED | DRIFTED | hit | 4 -> 12 | 0.51 M -> 1.08 M | 1.34 -> 1.40 |
| entry-drift marsh (clean) | opus / medium | IN-STEP | IN-STEP | clean, no false alarm | 4 -> 9 | 0.43 M -> 0.58 M | 1.28 -> 1.06 |
| escalation-check 247 | opus / medium | 3 KEEP, 2 REWRITE, 1 CUT; the unverifiable "137" | same CUT, same "137", same missing fact; one REWRITE moved to KEEP | hit | 8 -> 24 | 0.65 M -> 0.62 M | 1.12 -> 1.07 |
| escalation-check 239 | opus / medium | 6 KEEP, 2 REWRITE, 3 CUT | all 3 CUTs cut, plus a 4th ("the figure check's first run found four real problems and one false positive" - the recorded run kept it, rewritten, as a measurement; cutting it is scored ONE OVER-CUT, the false-alarm kind for this agent); one KEEP moved to REWRITE; a stale SHA newly found (real: the draft's SHA was two commits behind) | hit, 1 over-cut | 6 -> 22 | 0.43 M -> 0.43 M | 0.86 -> 0.84 |
| escalation-check 242 | opus / medium | 3 KEEP, 1 REWRITE, 2 CUT | identical | hit | 14 -> 17 | 1.04 M -> 0.72 M | 1.31 -> 1.06 |
| spec-fidelity-verify 250 | opus / medium | CHANGES REQUIRED, 2 items | CHANGES REQUIRED, 1 item: the missing success criterion found, **the unrequested scope in FR-004 MISSED** | **MISS** | 7 -> 11 | 0.53 M -> 0.46 M | 1.01 -> 0.95 |
| spec-fidelity-verify c670 | opus / medium | NOT-REVIEWABLE (five unkeyed figures) | reviewed the substance instead | not scored: the twin's FIGURES rule had been narrowed to changed passages by this session's drafting; restored | 8 -> 16 | 0.65 M -> 1.14 M | 1.01 -> 1.75 |
| spec-fidelity-verify (clean) | opus / medium | FAITHFUL | FAITHFUL | clean | 3 -> 11 | 0.20 M -> 0.43 M | 0.54 -> 0.75 |
| source-reader 08-28 (25 claims) | **sonnet** / high | 1 CONTRADICTED (an exception clause the source does not carry) | the same clause noticed and the verdict given as "READ (partial)" | **MISS** (under-called) | 4 -> 12 | 0.14 M -> 0.05 M | 0.24 -> 0.17 |
| source-reader 08-29 | **sonnet** / high | CONTRADICTED, from the paper's full text | the paper never reached (403 on five hosts); CONTRADICTED reached from a second source | hit by another route | 15 -> 18 | 0.70 M -> 0.42 M | 0.28 -> 0.41 |
| source-reader 09-12 (clean) | **sonnet** / high | 3 READ, 2 NOT-FOUND, with two partial passages found (the pigsty dike's 5-10 m width; pond water on the dike vegetables) | both passages **MISSED**: NOT-FOUND for each; four sources read where the recorded run read seven | **MISS** (false NOT-FOUND) | 7 -> 8 | 0.48 M -> 0.09 M | 0.92 -> 0.14 |
| quote-check, 17 + 6 notes | opus / medium + the script | in the slice: DIFFERS fn-91, 92, 96, 103/108, 104; NOT-ON-PAGE fn-237; undisclosed PARTIAL fn-94, 95, 237 | every support finding hit (94, 95, 237); DIFFERS 92, 103, 104, 108, 237 from the script, **plus fn-98 and fn-105, which the recorded run missed**; fn-91 and fn-96 VERBATIM | hit (see below) | 37 -> 26 | 12.8 M (102 notes) -> 2.5 M (23 notes) | 10.47 -> 2.98 |
| record-format towns (scoped) | **sonnet** / medium + the pre-pass | one residual SESSION NOTE in prose, one HISTORY passage, `ward` | `ward` found; **the session note and the history passage MISSED** | **MISS** | 11 -> 30 | 2.1 M -> 4.7 M | 3.33 -> 1.77 |
| record-format one section | **sonnet** / medium + the pre-pass | 2 stray tags, a sentence contradicting its clause, a fetch-verdict phrase, `the frame`, `clump` | the tags and `the frame` found; **the contradiction, the fetch-verdict phrase and `clump` MISSED** | **MISS** | (27, two pages) -> 21 | (8.5 M) -> 2.8 M | (7.99) -> 1.35 |
| record-format ways (clean) | **sonnet** / medium + the pre-pass | - | no session note or history reported; ten glossary terms proposed | clean; the terms are proposals, not alarms | - -> 28 | - -> 2.5 M | - -> 1.15 |

**The `quote-check` row, which is the script's test as much as the agent's.** The recorded Opus run called
fn-91 DIFFERS - the page, it said, reads 「神田上水の給水順次」 where the note quotes 「神田上水による給水順次」. The
live page, fetched directly on 2026-09-19, carries 「神田上水による給水順次」: the quotation is exact and the
recorded DIFFERS was a false alarm (or the page changed in five days; the script's answer is the page's
present text either way). fn-96 (大阪 against 大坂) the script also reports VERBATIM; not independently
re-fetched. And the script found two real differences the recorded run passed over (fn-98, fn-105). That is
the proposal's claim measured: a model is the wrong instrument for a character comparison, in both directions.

**What stands and what went back** (FR-011; and the GM, 2026-09-19, on the ones that missed: *"then we can
look at what other experiments we need to run on the specific checks that failed or otherwise scored
poorly"* - so a tier that missed returns to its known-good tier, the recorded runs standing as that tier's
result, and no further tier was tried in this feature):

| agent | proposed | result | lands as |
|---|---|---|---|
| `quote-check` | opus / medium + script | every recorded finding hit; two new true ones; one recorded false alarm removed | **opus / medium + script** |
| `entry-drift` | opus / medium | 4 of 4 | **opus / medium** |
| `escalation-check` | opus / medium | 3 of 3 | **opus / medium** |
| `spec-fidelity-verify` | opus / medium | missed one of two findings on a recorded round | **opus / high** (the twin and its routing stay: a MODE 3-only contract about half the length of `spec-fidelity`'s) |
| `source-reader` | sonnet / high | one CONTRADICTED under-called, two passages missed | **opus / high** |
| `record-format` | sonnet / medium + pre-pass | the pattern-findable hit, the reading-only findings missed, on both cases | **opus / high + pre-pass** |

**What the runs say about EFFORT (SC-005).** Medium against the session's high moved turns, output and
weight in no consistent direction: `entry-drift` 5.64 -> 4.42 over four cases, `escalation-check` 3.29 ->
2.97 over three, the twin 2.56 -> 3.45. Several medium runs took MORE turns. One confound is unremoved: a
headless session is a main thread, not a subagent, and its fixed context differs. Read with R1 (output is
10-26% of a check - observed 2026-09-19; method: R1's census), the honest summary is that effort is a small lever and this sample cannot price it;
it costs nothing to keep where the findings held. The measured savings of this feature are the scripts'
(no fetches, no character comparison, a false alarm and two misses corrected) and the no-inherit rule's
(R1: 62 ad-hoc runs and 19 settlement reviews on Fable).

**Candidates for the follow-up the GM named, not run here:** Sonnet at HIGH effort for `record-format`
(medium was the tier tested, so the model and the effort are confounded there); Sonnet for `source-reader`
with a harder contract (a verdict word may not be softened; read every pointer given); `source-reader` and
`record-format` on Opus at MEDIUM; the twin at medium with the restored FIGURES rule; and Haiku or Sonnet
for an ad-hoc fetch-and-extract reader, which is the largest consumer in R1 and was not tested at all.

## R6 - an unset effort is the session's

Verified 2026-09-19 in the installed 2.1.278 binary: the subagent's request effort is read as the
definition's `effort`, else the session's layered effort; `~/.claude/settings.json` sets `effortLevel`
to `high`. So the agents pinned at `high` run as they did, and the ones pinned at `medium` are the
effort downgrades FR-011 tests. The agent-definition schema lists `low`, `medium`, `high`, `xhigh`,
`max`.
