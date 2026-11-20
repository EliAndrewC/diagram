# Contract - the refusals of FR-006 to FR-009 and FR-011

Each refusal (FR-012): checks its escape FIRST; refuses with a message naming the compliant command; records every firing and escape
in the guard log (`shared::log::fire`, `make guard-log GUARD=<name>`); has a red-first test - the check deleted, the test red - and a
quiet case on correct work. An escape is `TOKEN="<a reason of two words or more>"` in the command, read by `shared::escape`, or the
make-side `$(LOGESCAPE)` for a make variable.

| FR | where | fires on | passes | message names | escape |
|---|---|---|---|---|---|
| FR-006 a | `context_cap_hooks` (new guard), PreToolUse `*` | a builder's tool call with its context past `CONTEXT_CAP_TOKENS` | the Write of its handoff file; a defined agent; the main session; a builder under the cap | the handoff file's path, "write what is done and what is left there, then stop; the session dispatches a fresh builder with it" | `CONTEXT_OK` in a Bash command; for any tool, a permit the session grants, `make context-ok AID=<agent id> WHY="<reason>"` |
| FR-006 b | the same guard, PreToolUse `SendMessage` | a SendMessage to a builder past the cap, or whose task has landed | a SendMessage to a defined agent, or to a builder under the cap whose task is open | "dispatch a fresh builder with <handoff path>" (or "with the next task's brief") | `CONTEXT_OK` in the message's `summary` |
| FR-007 | `static_runs_hooks` (new guard), PreToolUse Bash | the third `make static` of a task since its start or last landing | the first two; any run after a landing; `make static FRESH=1 REASON=...` counts as a run | the crate-scoped checks for the crates the task's delta changes, `scripts/gates/l7r-gate.sh rust lint|test|cover --crate <dir>` and `make rust-test CRATE=<dir>`, and `make static` once before the landing | `STATIC_OK` |
| FR-008 a | `no_poll_hooks`, PreToolUse Bash | a job holding `make` or `cargo` put in the background with `&` (no `wait` in the command), or started under `nohup`, `setsid` or `disown` at a command position | the same command through the Bash tool's `run_in_background`; `cmd & wait $!`; a foreground make | "run it as the Bash call itself with run_in_background: true; its completion notice wakes you" | `DETACH_OK` |
| FR-008 b | `no_poll_hooks`, the POLL_OK path and the file-wait path | a main-session wait loop whose longest `sleep` is over `POLL_CHECK_S` | a loop sleeping 60 s or less; a subagent's wait; a wait with no loop | the same loop with every sleep at 60 s or less | `SLOW_POLL_OK` |
| FR-009 | `make decide`, `lint::refusal` | a found-and-left item deferring a defect with no reason it is not fixed here, no filed task id or no order ("lands before T<n>"); a fix naming a class (every writer, every form, every file of a kind) with no line, labeled `observed <date>, method: ...`, on how every instance was found | `none`; an item with all three; a class fix with its labeled line | the form, with an example line | `DEFER_FORM_OK` as a make variable of `make decide` |
| FR-011 b | `make task-add` | the new box or section fails a `make quick` check that passes with it withdrawn | a line quick passes; a red quick that stays red with the line withdrawn (reported, line kept) | the failing check's own output, and "the line was withdrawn" | `QUICK_OK` as a make variable of `make task-add` |

FR-011 a (`make land T="T1,T2"`) is a reading, not a refusal: commas are spaces.
