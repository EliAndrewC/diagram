# Research: what the mechanism has to key on (feature 149)

Phase 0. Four of the five questions are settled by reading the tree; R1 is settled by an experiment during
implementation, and carries a fallback so it cannot block the feature (constitution XV).

## R1. Does this harness deliver a PreToolUse event for the Agent tool, and what does it carry?

**Settled from the documentation, 2026-08-29 - not by experiment, because the experiment is not available
to a session: the hooks that actually run come from MAIN's `.claude/settings.json`, and main is never a
workspace. A temporary logging matcher would have meant editing main.**

- The matcher is **`Agent`** (the tool name for a subagent dispatch), and a `PreToolUse` hook on it CAN
  refuse the call: exit 2, or `permissionDecision: deny`, exactly as for Bash. The refusal reaches the
  model the same way.
- The **shape of `tool_input` for a dispatch is NOT documented** - whether it carries `subagent_type`, the
  prompt and a description is unspecified. So the guard does not read a named field: it serializes the
  whole `tool_input` and looks for `settlement-review` in it. That is robust to whatever the schema turns
  out to be, and `scripts/test-pair-hooks.sh` drives it with the shape we believe it has.
- `Stop` fires for the main session; `SubagentStop` exists for the subagent's own end. The pairing uses
  `Stop` only, and refuses ONCE per content key, so it can never loop.
- Hooks are read from the session's own settings (project + user, merged). A clone's
  `.claude/settings.json` is not read while the session's cwd is the main checkout - which is why this
  guard, like every other guard here, only goes live when it lands in main. Its logic is proven before
  then by the test companion, which drives the script with synthetic stdin.

`.claude/settings.json` registers PreToolUse matchers for `Edit|Write|NotebookEdit`, `Read|Grep|Glob|Bash`
and `Bash`. Nothing here matches a subagent dispatch today, so whether the matcher accepts `Agent` (and
whether `tool_input` carries `subagent_type` and `prompt`) is unverified. The experiment is cheap: register
a matcher that logs its stdin, dispatch a trivial agent, read the log.

- **If it fires**: the guard refuses a `settlement-review` dispatch there (FR-012), and WRITES the review
  record as a side effect, so the record is produced by doing the right thing rather than being another
  thing to remember.
- **If it does not fire** (fallback): FR-012 is enforced one step later, at the `Stop` hook - a turn that
  dispatched a review with no gate running or freshly green is refused once, with the same message and the
  same override. The pairing still holds; only the moment of refusal moves. The fallback is recorded in
  the guard's header so the next session knows which half is in force.

## R2. How does a guard know a settlement-review is PENDING?

**Settled.** `scripts/agent-stall-hooks.sh` already answers this: its `scan <subagents-dir> [min]` reads
`~/.claude/projects/<cwd>/<session>/subagents/agent-*.jsonl` and prints one line per agent -
`finished | pending | stale`, its idle seconds and its last tool. The pairing guard reuses that scanner
rather than writing a second one, and identifies WHICH agent by grepping the transcript for the agent type
and the map name. `agent-stall-hooks.sh` also documents the failure this must survive: an agent whose
transcript ends on a tool_result and never moves again.

## R3. Unattended runs: the idle timer cannot dispatch a review

**Settled - through the override, not around it.** `make idle-tests` (feature 136) runs the whole gate from
a detached timer with no session attached, so there is nobody to dispatch a review. That is exactly the
one-sided case the GM's own escape covers: the idle runner supplies `PAIR_OK` with a fixed reason ("idle
run: no session attached to dispatch a review") and the bypass log carries it like any other. It is NOT an
exemption in the guard - the spec's FR-011 is unconditional, and an exemption is the shape spec-fidelity
struck in round 1.

## R4. What is "the same content"?

**Settled.** `.git/verification-state.json` already carries `engine_key` - the hash of every `.py` under the
skill outside `tests/` and `ci/`, plus pool gens and manifests, each hashed as its docstring-stripped AST
(`scripts/gate-stamp.py` `semantic_bytes`, feature 132). The gate writes it on success; the same key can be
computed on demand for the working tree. The pairing keys on it, so:

- a review is "fresh" for a gate run when its record carries the same `engine_key`;
- a comment-only or docs-only edit does not change the key, so a review taken minutes ago still counts;
- the key is the project's own definition of "the content the gate verified" - the guard invents nothing.

## R5. Which maps does the pairing name?

**Settled.** The maps whose manifests differ from `HEAD` in the clone (`git diff --name-only` over
`pool/**/*.json`). That is the same signal `review-gate.sh` uses at push time to demand a `.notes.md`
entry beside a re-rolled map, so the two guards agree on what "a changed map" means.

## Prior art this feature deliberately reuses

| need | existing thing | why not a new one |
|---|---|---|
| is an agent pending / stale | `agent-stall-hooks.sh pending` | one scanner, one failure model |
| what content was verified | `.git/verification-state.json` `engine_key` | the gate's own key; a second definition would drift |
| where an override is recorded | `dev/bypass-log/*.json` | the audit already reads it |
| how a guard is tested | `scripts/test-*.sh` + `make hooks-test` | constitution XVIII |
| what a changed map is | `review-gate.sh`'s manifest diff | the push-time guard must agree with the gate-time one |
