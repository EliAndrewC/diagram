# Feature 174 - the GM's request, verbatim

Asked at the end of feature 173, while a coverage question from a peer session was still being
measured. The GM's instruction, in full:

> Sounds great. Thanks. When you are done with that, I think the time has come to begin once again
> enforcing one hundred percent code coverage. I think that right now, we have some ratchets
> somewhere that enforce less than one hundred percent, but I think we want to enforce one hundred
> percent coverage in whatever the relevant place is. I guess our quick tests probably would not be
> able to enforce one hundred percent code coverage because the entire point of them is that they
> are testing most things, and in particular, are testing the things most commonly needed to be
> tested while doing iterative development. But that this is less than one hundred percent of our
> code However, I believe that make done is close to one hundred percent coverage, and at this
> point, should probably be moved back up to one hundred percent with the standard `fail_under =
> 100` configuration option set so that in the future, we literally cannot complete our make done in
> order to merge back into main, and there will no longer be any mechanism by which this can be
> accomplished. We turned this off because we were doing a large refactor, and we didn't even know
> which of our code would remain, and thus it seemed pointless to run lengthy unit tests on code
> that was perhaps about to be deleted. However, at this point, I think that we have stabilized our
> foundation for hamlet generation enough that we can go back to one hundred percent coverage and
> maintain one hundred percent code coverage for the remainder of this project for all time going
> forward. Go ahead and finish what you're working on now and then get the code coverage back up to
> one hundred percent when that is done.

## What the GM stated, separated into instruction and premise

**The instruction** (not in question):
- enforce 100% coverage again, in whatever the right place is;
- `fail_under = 100`, so a run below it CANNOT complete and there is no mechanism to land anyway;
- `make quick` is explicitly EXEMPT - they named that themselves and gave the reason;
- maintain it from here on.

**The premises, which this feature must check rather than inherit** (the feature-172 precedent: a
GM's stated reason that the measurement does not support is recorded, not quietly adopted):
- *"I believe that make done is close to one hundred percent coverage"*;
- *"We turned this off because we were doing a large refactor, and we didn't even know which of our
  code would remain"*;
- *"we have stabilized our foundation for hamlet generation enough"*.

The first two are checkable against the Makefile's own recorded reasons and against a measured run,
and `research.md` does that before any floor is moved.
