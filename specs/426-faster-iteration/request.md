# The GM's request (verbatim), 2026-10-26

Asked after the session's step-back on why feature 417's tasks took 40 min to nearly 2 h each.

## The step-back he asked for

> Okay, that sounds good.  But this does seem to be taking a while, longer than I would expect TBH.  So how about you finish whatever task you're in the middle of and then we step back and talk about how long each of these is taking and why.  And then maybe we'll figure out some process improvements together that will speed things up.

## On the repeated cohort runs

> Explain this: `Each roll of the landing seeds takes 2-4 min and the fresh block 3-5 min. I ran them 3-5 times per task: each step off alone, all together, a confirmation in the clone, and the landing itself.`  This makes it sound like we're repeating ourselves witrh duplicated runs where we could rely on the previous one having passed and skipped a lot of work.
>
> For that matter: if we're trying to fix failing seeds, then it sounds like we're rerunning ALL seeds every time we roll the landing seeds.  Which seems backwards.  We should do the pytest thing where when rerunning failed tests we start with the failing seeds and if those are still failing then only run them.  And we should have a test mode where we stop after the first failing seed without running the others, right?  That way, we don't waste so much time rerunning passing seeds while iterating on nonpassing onesw.  And if a seed passes during development and the code doesn't change, then it should be skipped on the next run, e.g. if we run the seeds locally and hthen do a `make landing` then we doin't want to rerun them if the code didn't change since last time, right?

## The approval

> Yes please.  I want your first 3 proposed fixes from your previous message plus this improvement.  I also thought we were already omitting docstrings when hashing code, so please look for any other places where we're failing to strip docstrings when we should and fix those too as part of this.

"Your first 3 proposed fixes" are, from the session's step-back message:

1. Make `make land` stop waiting when the claims gate refuses for a reason waiting can't fix (measured: T50's landing waited the full 20 minutes twice).
2. One probe command for every task: switch a step off, run the landing seeds, the fresh block and the pool, and print each seed's result and each changed field against HEAD, with HEAD's results for a block stored once instead of re-rolled.
3. A plan-section template that already carries the exit wording and a table of each step measured alone, which the plan reviews kept asking for.

"This improvement" is the session's answer to the second message: the docstring-free cache key, and the cohort modes FAILED_FIRST, LAST_FAILED and EXITFIRST with stored HEAD results.

## The GM's standing instructions that bear on found work (verbatim, his user-level `~/.claude/CLAUDE.md`, "Working habits")

> - **Fix bugs you find**, pre-existing or not, in the work at hand, and report them. Don't ask first.
> - **Tooling, not remembering.** Never offer "I'll remember to run X". Close a process gap in a hook,
>   gate or script, and recommend the automatic option.

T10 is such a gap, found in this feature's own work: a commit made while `make cache-audit` ran (T03's verification) carried
the audit's perturbed engine file (335cfa840, restored by a7e46883b).
