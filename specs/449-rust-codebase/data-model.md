# Feature 449 - data model

## The piece

The unit replaced (spec, Key Entities): one guard, one tool or one engine package, with its tests and the make targets that run it.

| field | what it is |
|---|---|
| name | the guard's file stem (`pair-hooks`), the tool's make target, the package's path |
| phase | 1-4 (FR-001) |
| python | the files it replaces: its `.py`, its shell, its inline sites (both censuses) |
| replay | the cases its verdicts are held to: a guard's suite (`tests/hooks/test-<guard>.sh`), a tool's tests and its recorded outputs |
| rust | the crate and module that replace it |
| state | `python` -> `replayed` (every case passes against the Rust) -> `switched` (the Python deleted, its settings entry or make recipe moved, in one commit) |

A piece is never both: from `switched` its Python is gone (FR-003).

## The decider (phase 1)

One guard's check: a function of the parsed hook input and the facts it asks for, returning an answer.

| field | what it is |
|---|---|
| guard | the guard's name, as the guard log and the escape tokens name it |
| events | the hook events it decides (PreToolUse, PostToolUse, UserPromptSubmit, Stop, ...) |
| matcher | the tools it takes, as today's settings entry's matcher |
| order | its place in the fixed order (plan D2) |
| facts | the shared reads it needs (D6): clone, session name, transcript's GM messages, a git answer |

## The answer

What a decider returns, and what the merge makes of them (contracts/guard-protocol.md).

| kind | today's form | merged |
|---|---|---|
| allow | exit 0, no output | - |
| refuse | exit 2, the reason on stderr | every refusal's reason, in order; the event exits 2 |
| rewrite | `hookSpecificOutput.updatedInput` | applied in order, each decider after it seeing the rewritten input |
| notice | `hookSpecificOutput.additionalContext` | joined in order |
| stop-block | `decision: "block"`, `reason` (Stop, SubagentStop) | every reason joined; blocks |

## The verdict replay

A piece's recorded cases run against the Python and the Rust (spec, Key Entities): for a guard, its suite's cases, each an input and
its expected exit code and output. A case whose expected verdict changes is a Constitution XIV fix, named in its commit (FR-002).
