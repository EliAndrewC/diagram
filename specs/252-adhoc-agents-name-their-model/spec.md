# Feature 252 - an ad-hoc agent dispatch names its model, or is refused

**Status:** implemented 2026-09-19 - FAITHFUL at round 1, plan CLEAR; FR-003's carve-out ruled LEGITIMATE.

## Summary

The GM chose (`request.md`, 2026-09-19) a hook that REJECTS an ad-hoc agent dispatch carrying no model,
with a message that says the caller must name one and reiterates the rule for choosing, so that the
caller makes the choice. This feature builds that guard, its test companion and its record. No engine
code: the delta routes DIRECT.

## Functional requirements

**FR-001 - the refusal.** A new guard, `scripts/agent-model-hooks.sh pretool` (PreToolUse, matcher
`Agent`), refuses (exit 2, message on stderr) an Agent dispatch when BOTH hold: the dispatch's
`subagent_type` is AD HOC - no file `.claude/agents/<type>.md` exists for it in the session's clone (else
the repository the payload's working directory is in), which covers `general-purpose`, `claude`,
`Explore`, `Plan` and an omitted type - and its `tool_input` carries no `model`. A dispatch of a type
that HAS an agent file passes untouched: its file pins its tier and `tests/test_agent_models.py` holds it
to that. A dispatch that names any model passes untouched, whatever the model: the choice is the
caller's, which is the point of refusing rather than filling in.

**FR-002 - the message.** The refusal says, in this order: that an ad-hoc agent dispatched with no
`model` runs on the SESSION's model, which is how 62 ad-hoc runs landed on Fable (feature 251); that the
caller must re-send the same dispatch with a `model`; and the rule for choosing, in the words root
`CLAUDE.md` carries - `sonnet` to read, fetch, translate or extract; `opus` for anything that judges. It
names the compliant form (`model: "sonnet"` or `model: "opus"` on the Agent call). The model guidance in
the message is READ from one place the docs also state, so a later change to the rule (feature 251's
follow-up experiments may add a tier) is made once.

**FR-003 - `fork` passes, and says why.** A dispatch whose `subagent_type` is `fork` is not refused: a
fork always runs on its parent's model and the harness ignores a `model` on it (the Agent tool's own
description: *"always runs on your model - a `model` override is ignored"*), so a refusal would demand
a field that changes nothing. It is recorded (`permitted`/`fork-inherits`) so `make audit` shows how often
the session's model is spent this way.

**FR-004 - recorded, tested, wired, documented.** Every branch logs through `_guardlog.sh` with a rule
slug (`blocked`/`no-model`, `permitted`/`pinned-type`, `permitted`/`model-named`, `permitted`/`fork-inherits`).
`scripts/test-agent-model-hooks.sh` covers each branch plus a non-Agent tool and an omitted
`subagent_type`, and asserts the message carries both model names and the word `session`; `make
hooks-test` runs it and the guard census knows the new guard. The hook is wired in `.claude/settings.json`
beside the other Agent-matched guards. The root `CLAUDE.md` guard table and `docs/guards.md` gain its
row. There is no escape token: the compliant dispatch is always available, and it is one field.

## Success criteria

- **SC-001** (FR-001, FR-003) On the suite's payloads: a `general-purpose` dispatch with no model is
  refused; the same dispatch with `model: "sonnet"` passes; a `quote-check` dispatch with no model passes;
  a `fork` passes and is recorded.
- **SC-002** (FR-002) The refusal names `sonnet`, `opus`, the session's model and the re-send.
- **SC-003** (FR-004) `make hooks-test` and `make quick` are green with the guard wired, and deleting the
  refusal branch turns the suite red.

## Assumptions

- The harness passes `tool_input.model` to a PreToolUse hook exactly as the caller set it, and omits the
  key when the caller set none (the transcripts' dispatch metas show both shapes; feature 251 R1).
- A refusal costs one model round trip each time a session forgets; the message is the teaching, and
  the GM chose that cost over a silent default.

## Review history

- **Round 1 (2026-09-19) - FAITHFUL.** FR-003 (`fork` passes, recorded) was put to the reviewer as a MODE 1
  question and ruled LEGITIMATE: the harness discards a model on a fork, so the GM's message would be false as
  applied and there is no choice for the caller to make; the measured failure (72 no-model `general-purpose`
  runs, 62 on Fable) is untouched by it. Passing any named model, and having no escape token, were both ruled
  within the request. Aside taken: FR-003 now quotes the tool description. Aside noted: counting every ad-hoc
  type the no-model set is 83 runs, 67 on Fable; the spec's 62 is `general-purpose` alone and true as written.
