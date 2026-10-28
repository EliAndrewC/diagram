# Feature 442 - the GM's request, verbatim

The GM, 2026-10-27, after trial 441's report (`specs/441-lattice-search-batched/report-trial.md`, "What the times point at")
listed four improvements - one shared reader for "this spec carries its verdict" that every gate imports; `sync-in` not
waiting behind the landing's render-sync; a spec-lint check that a rewritten requirement's criterion was touched in the same
edit; a measurement-only trial's review bundle carrying its commands' outputs:

> I don't think that JIT'ing is going to give us orders of magnitude.  If we're making tens of millions of function calls then THAT'S the issue, right?  I mean, I still have not heard a good explanation for why so many, which leads me to believe that we are doing extremely algorithmically inefficient things here.
>
> Thoise improvement sound worth doing in any case, so why don't you knock those out and then we'll talk about what might actually move the needle here.

("Thoise" is a typo for "Those".) The talk about what moves the needle follows this feature.
