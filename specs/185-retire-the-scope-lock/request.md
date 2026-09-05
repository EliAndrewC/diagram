# The GM's request, verbatim

2026-09-05, in the make-target naming conversation:

> I agree that make lint is valid But I also agree that it should be renamed to make static, so
> please do that.

and, in the same message:

> And yes, please go ahead and retire the concept of the scope lock and the scope unlock, i.e.
> retiring both the concept and the specific make targets.

## What prompted each

**`lint` -> `static`.** The naming audit (feature 184) found that `lint` is not linting: it is
`ruff check --fix` plus three custom guards (duplicate-defs, file-scale, stale-dirs). `format` is
whitespace alone. The audit recorded that the split is correct and the NAME is what misleads, and
declined the rename as out of scope; the GM then asked for it directly.

**The scope lock.** The GM's reasoning, from the same conversation:

> for the scope lock and the scope unlock, Do we actually need that anymore? those also look like
> holdovers from when we had fifteen minutes worth of tests and were just desperately trying to get
> those numbers down.

That is accurate. The lock was built for the reference-hamlet iteration period, when the gate was
slow and multi-map rolls had to be deferred out of it. Feature 174 ended that: the gate runs the
whole suite, always, in about five minutes. The scope has been UNLOCKED since 2026-08-27 - nine days
at the time of the request.

**It also closes the terminology question the GM raised**, since `SWEEP_OK` is the scope-lock check
and `switches.py` is where a locked scope is described as one where *"every sweep refuses"*:

> In terms of the cohort map, are we now using cohort and SOAP and sweep to all mean the same thing?
> I find that confusing and would like to standardize on a single term.

Retiring the lock retires the word. What remains is `cohort` (a set of seeds) and `soak` (the tier
that would run them) - two terms for two different things, down from three.
