# Standing authorizations for the diagram project

The GM (Eli) has given **standing authorization for this project's review and verification
subagents**, every one defined in `.claude/agents/`: `building-review`, `claims-triage`,
`entry-drift`, `escalation-check`, `fix-check`, `glyph-check`, `impl-drift`, `intro-check`,
`modal-depiction`, `modal-form`, `modal-research`, `modal-triage`, `perf-audit`, `quote-check`, `record-format`,
`record-style`, `research-pass`, `round-arbiter`, `settlement-review`, `size-audit`, `source-applicability`, `source-filter`, `source-reader`,
`spec-fidelity`, `spec-fidelity-verify` and `translation-check`. When `CLAUDE.md`, a doc it points
to or a `make` target's output calls for one of them, invoke it with the Agent tool without asking first.
`perf-audit` (feature 129) is the ONLY agent that may pass `AS=perf-audit` to the review-record
commands, and never writes those records itself; since feature 375 amendment 5 a performance band is a FLAG to
mention when you report the landing, not a record owed, so it runs only for an investigation someone chooses. `round-arbiter` (feature 375) is the ONLY agent that may pass `AS=round-arbiter`
to `make arbiter-ruled`; a guard names it when a check passes its round cap or a tripwire fires. These are mandatory verification steps in `CLAUDE.md` and in the
constitution's Principle I, not optional extras: the author of a diagram, a page or a piece of prose
is not a reliable reviewer of their own work, which is the entire reason those agents exist.

This authorization is deliberately **narrow**. It does not extend to broad multi-agent fan-out, the
Workflow tool beyond the wave jobs below, or deep research - those still need an explicit request from the GM in the
conversation.

## Workflow, for waves of typed checks only

**Workflow is pre-authorized for recurring waves of typed agents** (the GM, 2026-10-17, feature 383 amendment 7). When a
documented job launches 4 or more agents of one of these definitions - WAVE JOBS: `source-applicability`, `quote-check`,
`settlement-review`, `entry-drift`, `modal-depiction`, `record-format`, `impl-drift`, `modal-research`, `building-review`,
`source-reader`, `glyph-check`, `modal-form`, `round-arbiter`, `claims-triage`, `modal-triage`, `translation-check` (the GM,
2026-10-26: "I also do pre-authorize the translation check as a wave job") - run them through the saved
`check-wave` workflow, without asking first:
`Workflow({name: "check-wave", args: {agentType: "<job>", units: [{label, prompt, then?: [{agentType, prompt}]}]}})`.
It sets `agentType` on every `agent()` call, staggers the launches by itself and wakes the main session once for the whole
wave instead of once per agent; each unit's prompt stays as short as a hand launch's. Two or three of a type stay plain Agent
calls in one message. This does not extend to new kinds of fan-out, general-purpose fleets or deep research, which still need
the GM's explicit request. `scripts/hooks/workflow-hooks.sh` holds every unit to the guards a hand launch meets.

## Why this file exists

Claude Code's default system prompt carries a line telling the session not to call the Agent tool
unless the user requested it. That is a reasonable default - it stops a session from spawning an
expensive fleet unprompted - but it sits ABOVE `CLAUDE.md` in the instruction hierarchy, so it
silently outranks this project's own mandate to run a review agent before declaring work done.

On 2026-07-27 that is exactly what happened: three provincial-city maps changed, the diagram's
`CLAUDE.md` required a `settlement-review` pass before a Mode B map shipped, and the session
skipped it because the system prompt said not to. Nothing was broken and nothing warned - the
mandate simply lost to a higher-priority instruction.

`--append-system-prompt` lands this text at the END of the system prompt, after that line, with the
same authority. That is why the fix lives here rather than in `CLAUDE.md`.

Loaded by the `claude()` shell wrapper that `scripts/container/setup-dev-env.sh` installs into
`~/.bashrc`. Edit the text here; the wrapper only reads it.
