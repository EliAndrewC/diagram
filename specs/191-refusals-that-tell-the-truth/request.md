# The GM's request, verbatim

2026-09-06, in reply to a report that two printed messages in engine Python still named
`make reference` after that rung was retired:

> Please proceed with those first 2 things: investigate the gate slowdown, fix the broken
> pinned messages (I assume by converting them to docstrings).  You can ignore the
> specs/189 is blocking pushes repo-wide issue, as I will have the other session handle that.

("pinned" is read as "printed" - the two items reported were printed messages.)

Then, when this session's first draft declined the parenthetical:

> What do you mean that docstrings are not printed? They are printed if you print them. You can
> absolutely make something a docstring and then access it at runtime in order to print it. Why
> not do that?

## The decision: the GM's suggestion is ADOPTED. The session's first answer was WRONG.

This section replaces a first draft that declined the suggestion on the ground that *"a docstring
is not printed"*. That was wrong, the GM corrected it directly, and the correction is kept visible
here rather than quietly deleted, because this file is what a future session reads to learn what
was decided.

**Why it was wrong.** `__doc__` is an ordinary attribute available at runtime; printing it prints
the text. The claim was only ever true of a docstring that nothing prints. This repository had
ALREADY established the pattern the GM was pointing at, the previous evening: feature 189 made
`cls.__doc__` the displayed prose (`interactive/classes/_base.py:207`), and
`interactive/classes/CLAUDE.md` states *"The explanation IS the docstring"*.

**What it buys, measured rather than asserted.** `gate-stamp.semantic_bytes` hashes each `.py` as
its docstring-STRIPPED AST, so once the message text lives in a docstring, every future correction
to it is AST-identical: it routes DIRECT and owes no spec-kit feature. Verified on synthetic pairs -
a docstring-only edit yields the same key, a string-literal edit does not. That is exactly the rot
that made this feature necessary, so the suggestion fixes the class of problem and not just the
instance.

**The saving is PER FILE, not a general property of docstrings** (corrected after review round 2,
which is the form of this claim that survives measurement):

- it HOLDS for `l7r/diagram/_invocation.py` and `l7r/diagram/tools/hamlet_floor.py`, which fall in
  gate-stamp's `diagram` area - and `RAW_AREAS == frozenset({"page"})`, so that area is hashed by
  the semantic id and its docstrings are stripped;
- it does NOT hold for `interactive/classes/*.py`, which feature 189 deliberately ADDED to
  `RAW_AREAS` so that page prose in a docstring still keys the gate.

So "put it in a docstring and it stops keying the gate" is a fact about an area's hashing policy,
not about docstrings. Both files this feature touches are in the area where it holds.

**One residue of the original objection survives, narrowed to what it can support.**
`_invocation`'s message is a TEMPLATE - three runtime interpolations (`{operation}`, `{_reason()}`,
`{target}`) plus ANSI escapes - so only the STATIC ladder moves into a docstring and the
interpolated header stays an f-string. `hamlet_floor.check()`'s message is one static line, where
the objection never applied at all.
