# `idle-log/` - what the idle runs found

One JSON file per idle run (feature 136): when, session, commit, target, rc, wall seconds, suspends
detected during the wait, deferrals (the lock or a running make), the failing checks, the log path.
Written by `scripts/idle-tests-hooks.sh timer` after an idle session's staggered wait; the next
prompt's hook prints the newest record once, and the session ACTS on a red - a red here is a
regression found on the night it was made, which is the whole point.

A directory and not one file, for the reason [`../run-log/CLAUDE.md`](../run-log/CLAUDE.md)
records twice: several clones append at once and disjoint new files never conflict. Never edit or
delete an entry; a record is the measurement, not a report to tidy.
