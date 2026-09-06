# The GM's request, verbatim

2026-09-06, in reply to a report that two printed messages in engine Python still named
`make reference` after that rung was retired:

> Please proceed with those first 2 things: investigate the gate slowdown, fix the broken
> pinned messages (I assume by converting them to docstrings).  You can ignore the
> specs/189 is blocking pushes repo-wide issue, as I will have the other session handle that.

("pinned" is read as "printed" - the two items reported were printed messages.)

## The session's answer to the parenthetical, recorded because it DECLINES the GM's suggestion

Converting them to docstrings does not work, and the reason is mechanical rather than a
preference. Both are RUNTIME OUTPUT - `sys.stderr.write(...)` in `_invocation.guard()` and
`print(..., file=out)` in `hamlet_floor.check()`. A docstring is not printed, so converting
them would delete the messages instead of correcting them.

The appeal of the suggestion is real and worth stating: a docstring-only edit to engine Python
is NOT engine code for the push route (`ci/delta.py` compares each changed `.py` by the same
docstring-stripped AST that `gate-stamp` keys on), so it would have avoided a spec-kit feature.
Correcting printed text changes string literals, changes the AST, and therefore routes GATED -
which is why this feature exists rather than a two-line tweak.
