# Feature 436 - the GM's request, verbatim

The GM, 2026-10-27, after the session explained what `make perf-ab` runs (two worktrees, the full snapshot alternated A, B,
A, B; "perf AB" in his dictation is `make perf-ab`):

> Okay, that makes sense. With that being said, are we always running everything when we do a make perf AB? Because it seems like a thing that we would want to do most of the time is do a much more targeted version of this. Like in our current effort, we are trying to optimize the Forty Homestead Hamlet case. So might it make sense to be able to run the performance A-B tests for a single Hamlet seed 6 times, and then iterate on that before doing the larger make perf AB? That, in general, should be our pattern when we are doing this kind of performance testing, because what you described sounds like it will take quite a long time to run, which makes our iteration very expensive, and we are trying to figure out how to make our iteration cheap. So if we can test a refactor first by doing the quick version, and perhaps even by enforcing that we do the quick version first, then we could move on to running a larger subset of the tests and seeds. But if we find ourselves running everything with a lot of seeds before we have done A/B testing on just a single seed, then that means that we are doing the inefficient version, and our makefile should probably actively prevent this in the same way that it prevents us from running our slow tests before we have run our quick tests, right?

Earlier in the same exchange, on adding CPU time beside wall time: "Yeah, I think adding CPU time beside wall time in make perf AB is good".

The session proposed (escalation-checked, kept whole):

- Three steps, cheapest first: quick, the default - one seed at one size, 6 runs per version (for the current work seed 25
  at 40 households); a subset - seeds and sizes chosen (`SEEDS=25,39 HOUSEHOLDS=20,40`); full - today's sweep (`FULL=1`).
- Quick first, enforced: a subset or full comparison refused unless a quick comparison of the same two engines (judged by
  the engine code, not the commit name) is on record; overridden only with a stated reason; it refuses a skipped step,
  never a timing.
- The order alternates: A then B, then B then A.
- CPU time beside wall time, each with its best and spread.
- The noise floor: an A/A run of the quick form taken once and printed beside each quick result.
- The checklist says: quick while iterating, then a subset or full run once before landing.

The GM:

> That sounds good. Please implement that. Thank you.
