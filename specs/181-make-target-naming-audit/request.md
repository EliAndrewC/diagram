# The GM's request, verbatim

2026-09-05, after the AWS repoint and the soak-suite work:

> Now I am wondering whether all of the refactoring that we have been doing has perhaps made our make
> target names and their arguments somewhat obsolete and confusing. For example, 'make full' probably
> doesn't make sense as a name when there is a notion of a sleep, which is more expansive than what
> "full" is doing, which means that having something like "FULL=1" or `make full` which are actually
> not running all of the tests is just confusing. Now something like make quick tests is what it
> sounds like, and so that is a name which does not need to change. However, I would like you to look
> at all of the makefile targets and then look at their actual names and different arguments that they
> can take such as FULL=1 or whatever and then do an audit on which names still actually make sense
> and are what they sound like as opposed to being confusing given all the refactoring that we have
> been doing.

Then, on the audit's findings:

> Yes. Please go ahead and make changes for the four findings that you have. Your proposed changes do
> sound good, so please go with that.

And on the redundancies the audit surfaced:

> Okay. Yes. We should get rid of the redundancies so go ahead and do that now.

## What the audit found

Five items. The first four were approved as a batch; the fifth is the redundancy above.

1. **`sweep` collided with an established term.** `SWEEP_OK` and `switches.py` already use *sweep*
   for a run that rolls many MAPS - what the scope lock refuses. The soak suite, added hours earlier,
   had been named `sweep`, putting a target of that name three lines from `$(SWEEP_OK)`, the guard
   asserting a target is NOT one.
2. **The gate banner stated something false.** Since feature 174 a plain `make done` runs the SAME
   TESTS as `FULL=1`; the banner said FULL "also rolls the other pool maps".
3. **`test-full` advertised "EVERY test, nothing deselected"**, false once `tests/soak/` was deselected.
4. **Two `ci-*` help lines described pre-repoint behavior** - a remote run is `make soak` now.
5. **`tripwire` was `maps` with a help line that could not be true** - the redundancy.
