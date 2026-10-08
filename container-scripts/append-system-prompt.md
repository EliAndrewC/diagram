# Standing authorizations for the diagram project

The GM (Eli) has given **standing authorization for this project's review and verification
subagents**, every one defined in `.claude/agents/`: `building-review`, `effort-grader`,
`entry-drift`, `escalation-check`, `fix-check`, `glyph-check`, `impl-drift`, `intro-check`,
`modal-depiction`, `modal-form`, `modal-research`, `perf-audit`, `quote-check`, `record-format`,
`record-style`, `settlement-review`, `size-audit`, `source-applicability`, `source-reader`,
`spec-fidelity`, `spec-fidelity-verify` and `translation-check`. When `CLAUDE.md`, a doc it points
to or a `make` target's output calls for one of them, invoke it with the Agent tool without asking first.
`perf-audit` (feature 129) is the ONLY agent that may pass `AS=perf-audit` to the review-record
commands; the main session launches it whenever a performance band of 1 or more is reported, and
never writes those records itself. These are mandatory verification steps in `CLAUDE.md` and in the
constitution's Principle I, not optional extras: the author of a diagram, a page or a piece of prose
is not a reliable reviewer of their own work, which is the entire reason those agents exist.

This authorization is deliberately **narrow**. It does not extend to broad multi-agent fan-out, the
Workflow tool, or deep research - those still need an explicit request from the GM in the
conversation.

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

Loaded by the `claude()` shell wrapper that `container-scripts/setup-dev-env.sh` installs into
`~/.bashrc`. Edit the text here; the wrapper only reads it.
