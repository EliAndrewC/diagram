# Feature 214 - the GM's request, verbatim (2026-09-08)

After feature 213 landed, the GM asked what the minimum number of hamlets for 100% coverage is and how many
the gate rolls now, was told "roughly half of the 21 exist for coverage and half because a test's behavior
needs a roll of its own", and replied:

> Yeah, so you say "Roughly half of the 21 exist for coverage and half because a test's behavior needs a
> roll of its own" then is it ACTUALLY The case that the test's behavior needs a roll of its own?  Like a
> full roll of a full hamlet, and not just some assertions we could add onto the existing tests where that
> same hamlet was already rolled elsewhere?!

The session went through the ten test by test (three truly need a roll: the immune test's perturbed roll,
the in-process half of the child-equality proof, possibly the seed-43 kink; the rest can read a shared
roll, run on stand-in stages, or patch `generate`) and offered to run it as a spec-kit feature. The GM:

> Yes please do that, thanks.  I believe we can get this back down to the number it was at before,
> especiually if we do the "shared roll" thing for most or all of these.

"The number it was at before" is the packing record of 2026-08-31 (`dev/loop.md`, "THE PACKING QUESTION"):
11 rolled, floor about 8-9.
