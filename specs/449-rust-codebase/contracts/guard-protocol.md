# Contract - the guard protocol `l7r-guard` keeps

The Claude Code hook protocol as the repository's guards speak it today (research R3), kept exactly by the one binary that replaces them.

## Invocation

`scripts/hooks/l7r-guard.sh <event>` from `.claude/settings.json`, once per hook event, its matcher the union of the guards' matchers
for that event. The hook input JSON arrives on stdin. `CLAUDE_PROJECT_DIR` and the escape variables are read from the environment,
as today. `l7r-guard --only <guard> <event>` runs one guard's decider alone: the suites' entry point during phase 1 (research R4).

## Input

The fields the guards read today, each read once: `session_id`, `transcript_path`, `cwd`, `hook_event_name`, `tool_name`,
`tool_input` (with `command`, `file_path`, `content`, `old_string`, `new_string`, `subagent_type`, `prompt` as the tool carries them),
`tool_response` (PostToolUse), `prompt` (UserPromptSubmit), `stop_hook_active` (Stop).

## Output

| answer | stdout | stderr | exit |
|---|---|---|---|
| allow | nothing | nothing | 0 |
| refuse | nothing | every refusing guard's reason, in the fixed order, each as today's text | 2 |
| rewrite | `{"hookSpecificOutput": {"hookEventName": <event>, "updatedInput": <input after every rewrite>}}` | - | 0 |
| notice | `{"hookSpecificOutput": {"hookEventName": <event>, "additionalContext": <notices joined by a blank line>}}` | - | 0 |
| stop-block | `{"decision": "block", "reason": <reasons joined>}` | - | 0 |

A rewrite and notices together return one object carrying both. A refusal wins over every other answer: the event exits 2, and its
rewrites and notices are not returned.

## The guard log

Each refusal, escape and rewrite appends one line to the guard log in today's format (`scripts/hooks/lib/guardlog.sh`), so
`make audit` and `make guard-log GUARD=<name>` read the Rust guard's lines unchanged.

## Failing open

When the binary cannot be built or run, the wrapper exits 0 with a notice saying so and appends a guard-log line
(`guard=l7r-guard outcome=failed-open`); the GM's session is never locked out by a broken build (plan D7).
