# The GM's request, verbatim

Captured BEFORE `spec.md` was written, so the spec can be graded against the GM's own words rather
than against the author's summary of them (constitution XVI). Nothing here is edited - not the
punctuation, not the dictation artifacts. The house-style guard exempts this file for exactly that
reason.

## 2026-08-25, the request (session "Reference testing")

> Okay. I have some changes that I want to make. And for the current period, I would like to focus on getting our reference hamlet to be exactly right. and address all known issues with it and to not bother to run the larger set of tests. Because we know that those tests fail. I mean, some of them succeed, but we know that it is the case that a large number of our full test suite where we run, I think, currently something like forty eight different maps, which is something like some number of different maps with some number of different seeds per map. And we know that a lot of that fails. And so I don't think that there's value in running that full test suite while we are still iterating on only the reference map. because if we fix one thing on the reference map, but we know that other things are still wrong on the reference map, then trying to get everything else working is going to waste a lot of time relative to just getting a baseline set of stuff running. However, I think that right now, we have some merge gates where things don't make their way back into the main branch until all of those tests pass. Is that right? So is there a way to do this development effort? where I don't know in advance all of the stuff that we need to fix because I can point out a couple of things on the map right now, which I know are wrong. So is the correct thing to do to use SpecKit to define a feature that basically says get the reference map up to the point where Eli accepts it as the developer, and then we update the task list as we go? What is the idiomatic way to do this? In particular, I want to make sure that as we iterate, not only do we not run the full test suite, but we literally cannot because just telling you, please make sure not to run the full tests. In the past has frequently resulted in the full tests getting run, and that costs both time and actual money now that we are running on AWS. So can we perhaps have the first thing that we do to update the tooling to essentially disable AWS? That seems like something that would be good as a reusable setting anyway. such that if it is disabled, then we do not use it as a gate. and we do not dispatch to it while we are doing iteration. What do you think?

## The session's proposal, which the GM accepted

The session answered (summarized here - the proposal is the session's words, not the GM's, and is
recorded so the reviewer can see what "that" refers to in the acceptance below):

- two corrections: the merge gate (`make done`) is reference scope, not the 48-map run, so a red
  pool map does not block a landing; and a green local `make done` already pushes without a build
  when main added no engine code;
- **feature 132, two committed switches**: `make ci-off REASON=... / ci-on` - a tracked file, not
  an environment variable; when off, `ci-check` / `ci-merge` / `ci-image` refuse before any AWS
  call and the gated route degrades to LOCAL-GATED (merge the latest main into the clone, green
  local `make done` on the merged tree, push); and `make scope-lock reference / scope-unlock` -
  same file, second field; when locked, `make cohort`, `make done FULL=1`, `make maps SCOPE=all`,
  `test-full` refuse and name the unlock; only the reference hamlet rolls. Two separate axes. Both
  get the standard guard treatment (escape checked first, proven to fire, `hooks-test` companion);
- **feature 133, "the reference hamlet is accepted by the GM"**: tasks added as defects are
  pointed out; milestone push whenever every task is closed; spec-fidelity re-reviews each batch;
- two flags: pool regressions accumulate silently while locked and get found at unlock (a closing
  task of 133); each 133 push costs the 5.5-minute local `make done`.

## 2026-08-25, the acceptance

> Yes. That sounds like exactly what I want. Please proceed with that. Thanks.
