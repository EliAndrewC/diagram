# Feature Specification: a mechanical cap on function length, held at the gate

**Status**: Filed - 2026-10-08, found while closing feature 111

**Affects**: tooling

**Input**: the GM, closing feature 111 (2026-10-08, verbatim): *"You can close feature 111 because we've replaced
"decompose for readability" with a mechanical cap on function length and file length."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this
directory); until then `make speckit-todo` lists it as filed.

## What exists and what does not

The FILE cap exists and is gated: a Python file past 1,000 raw lines fails `lint` and both push routes
(`scripts/gates/check-file-scale.py`, feature 173). The FUNCTION cap does not: constitution Principle X clause 12 says a
function "past a few hundred logical statements is suspect; past ~1,000 it is a defect unless an inline annotation
justifies why it must remain one body", measured in logic units (statements and expressions, never raw lines), and its
Sync Impact Report carries "clause 12's deferred expression-counting gate check" as a deferred TODO. Nothing enforces it
today: no ruff statement rule (`PLR0915`), no gate script, no test.

This feature builds that check - the logic-unit count of clause 12, its thresholds and its inline-justification escape -
at the gate beside the file cap, so the ruling that closed feature 111 rests on a cap that is actually held.
