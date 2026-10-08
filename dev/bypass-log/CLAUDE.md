# `bypass-log/` - every attempt to run the expensive path, and what came of it

One JSON file per attempt: target, outcome (permitted / cancelled / refused), the written
reason, and the commit. Read it with `make audit`; never edit or delete an entry to make the history look better.

A directory and not one file, for the reason (and the GM's 2026-08-24 ruling) in
[`../perf-log/CLAUDE.md`](../perf-log/CLAUDE.md); each entry goes in `<YYYY-MM>/`, for the reason in
[`../run-log/CLAUDE.md`](../run-log/CLAUDE.md). The question both logs answer, and the GM's words asking it, are there too.

## What the outcomes are for

`permitted` / `cancelled` / `refused`. Without `outcome` a session that read the warning and backed
out is indistinguishable from one that never tried, and the log cannot answer the question it exists
for. **A rising count of `cancelled` is the early signal that the cheap path has stopped being
sufficient** - at which point the answer is to make the fast path better, not to keep refusing.

An audit trail records a decision; it does not make one: the 2026-08-24 audit found 3 of 5 pre-guard bypasses
unjustified, all recorded and none stopped, because the override could be supplied on the command line and skipped the
prompt. Don't let an override skip the prompt.
