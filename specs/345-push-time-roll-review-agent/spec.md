# Feature Specification: The push-time `roll-review` agent (deferred by feature 217, 2026-09-08)

**Status**: Filed - from future-work/cross-cutting.md, "The push-time `roll-review` agent (deferred by feature 217, 2026-09-08)", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: village - its own trigger: "if a village-tier feature lands rows" that should have been unit tests

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

**What it would be**: an independent Opus check on the perf-audit pattern (feature 129) that the push demands ONLY
when the delta adds a `Roll` or `Duplicate` row to `tests/rolls.py`. It is given the constitution VI clause, the diff,
and the census verdict's printout (the lines the new roll alone reaches) and answers one question: could these lines
be reached without a roll - by packing the assertion onto a roll already made, or as unit tests of the placer? Its
record is written only by the agent (`AS=roll-review`, honor-based like `perf-audit`; the bypass log records), and
`sync-with-main.sh` refuses the push without it.

**Why it is third in line** (the GM, 2026-09-08: *"I don't want to run a subagent check every single time we run our
unit tests"*): the rule and the two cheap layers act at zero token cost - the verdict fails a roll with no unique line,
the guard puts the doctrine in front of the session when it opens the roster, and the audit pointer makes the
justification an artifact. A row that passes the verdict has already proved it reaches lines nothing else does; what
the agent would add is an independent opinion on whether those lines could be unit tests, which is judgment the
session is told to exercise and the GM reads in the diff.

**When to build it**: if a village-tier feature lands rows that the GM, reading the diff, judges should have been unit
tests - that is the measurement that says the judgment layer is not holding.
