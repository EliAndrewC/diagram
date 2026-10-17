# Feature 383 - the GM's request

The GM, 2026-10-12, in the "diagram-performance" session, after the hourly check of the "Diagram backlog" session (feature
374) found the research pointer check spending 25.7 s per push and the session cut it to 4.7 s without a cache:

> Nice, that's really good. Now, I also wonder about caching for all of these different tools. So like the, the improvements that we're making for when we actually have to do the query are great, but we can compute a hash of the file within a tiny fraction of a second. And then I would assume that we could have like a cache that stores the previous values extracted from a file and the hash of the file at the time that they were extracted and then we could basically check and see whether or not those values were still valid and if they are then we just return them and then we don't even have to apply the regular expressions.
>
> Also, do we actually have 1.4 million lines of files that we are tracking that actually need to be checked in that way? because I know that we don't have 1.4 million lines of code. I can believe that we have 1.4 million lines of like research and research findings and all of that, but that also seems like something that we would not need to run like regular expression patterns over in order to extract stuff. I would think that we would store back references in a more standardized way that would not require that kind of janky parsing.
>
> In other words, what I'm basically saying is that it's great that we have made the performance improvements that we have made, but I know that we now have a bunch of different makefile targets that are basically going through our code and extracting references to things. Some of them are extracting things like references to spec kit features, and some of them are extracting things like references to research. And some of them are extracting things like references to glyph rendering conventions or whatever. but it sounds as if we are doing this in a way that we have made more efficient, but which still is not making use of a caching layer, and that if we made use of a caching layer, then I feel like it would not take nearly five seconds to do this kind of thing. I mean, you say that everything else was under 2.2 seconds, and that the research site's build check is 6.3 seconds. And those are times that I also think would probably not be what they are if we were employing a well-designed caching layer. Now I might be wrong, but before we kind of jump to any conclusions or lock in a decision or make any changes, then can you just tell me what you think about this?

The session proposed extracting per file, keyed by the file's git blob id and the extractor's own code, and offered to
measure what the push checks cost first. The GM:

> Yes, please run that measurement now. Thank you.

The measurement: the push's checks about 24 s (the record build check 7.5, the pointer check 4.7-5.9, the duplicate and
function-cap checks 1.9 and 1.7, the old-layout check 1.6, the conflict check 1.5, the ledger check 1.3, ten self-tests 0.9,
about 35 interpreter start-ups 0.9); the tracked lines specs 566k, dev 348k, code about 342k, research 134k. The GM:

> Yes, I do want that. I think it is also worth looking at the ledger check searching the session transcripts, The git searches in the old layout check, check-bundle and the review lookup, and the 35 separate Python startups, though I'm less sure what we could do about that last one.  But the first few seem doable. So for instance, we probably don't need to search the entire session transcript in order to do things if we are keeping track of how far back it is that our most recent search was for. Though you'll actually need to explain to me what the ledger check is and when it is run, because I'm not completely clear on it. And then same thing with the git searches in the old layout check. And then check-bundle and the review lookup - what are all of those? Once I understand them all better, then I might be able to offer better guidance about where to focus our efforts. Though I do eventually want one new feature for everything, including the content key cache and this other stuff.

The session explained each tool (what it is, when it runs, what it costs, what would fix it). The GM:

> Yes, we can definitely retire the old layout check because there are no clones using the old layout anymore. So we are just fine there.
>
> I don't think that I understand why the review lookup runs on so many different places instead of only when we land on main. Like, why are we comparing our stuff to main when we're not ready to land there?
>
> Although I agree that the combining all the different checks into one is lower impact, it does still seem worth doing. So I would like to see that done as part of this feature if that is doable.
>
> It sounds to me also as if we have found a whole bunch of issues by doing this kind of hourly check. So do you think it would make sense to convert the hourly check that we are doing here into something that like happens automatically? So like we already have the notion of like the glyph check being something that does not happen every time, but will happen about once per hour for sessions that last that long, or for features that last that long, I guess. So could we perhaps do the same thing with this kind of hourly arbiter? basically converting the check that we are doing now into something that every session does for itself if it has spent longer than an hour implementing a single feature, which I think can kind of reuse the same logic that the glyph check uses. So essentially, for longer running features, we will have a set of checks that we do, which previously was only the glyph check, I think, but now will be the glyph check and also this sanity check or stepping back and looking at the problem from above check or whatever we want to call it. What do you think about that? I realize it's slightly different than the particulars of this feature, but it does seem related to it in that these are the kinds of improvements that I might expect this sort of check to identify as possibly being desirable. What do you think about also incorporating that into this same feature?

The session answered: the review lookup compares against main because main is the fixed base for "everything this feature
has changed", and it runs at gate start, at a review dispatch and at every turn's end after a green gate because of the
feature 231/248 rule to review on a green gate; since 375 amendment 9 glyph-check is due only on the hour or at landing, so
it proposed asking only at the hourly checkpoint and at landing (keeping the dispatch check). It proposed the hourly
step-back as a defined agent dispatched on the same clock as glyph-check, from a mechanically built bundle, its loop and
packing findings binding like a round-arbiter ruling and its small tooling fixes open items as an arbiter's `tooling_fix`;
and one feature in three phases: (1) the caches and cheap fixes, the old-layout check retired, (2) the push checks in one
process, (3) the hourly step-back. The GM:

> Yes, please file it that way and then go ahead and work it start to finish. Thanks.

## Amendment 1 (2026-10-13, same session)

The session measured the make targets' times since the landing; `make land-tooling` was the longest a session waited on
regularly (median 133 s), and it offered to have it skip what the clone had already passed. The GM:

> Yes please we should definitely skip suites the clone already passed.
>
> And also, while I realize we don't run it very often, I feel like `quote-verbatim` would benefit from the same caching layer we implemented elsewhere, right?

The session found its own claim wrong in part: the guard suites already reuse a pass on identical inputs in the worktree
`land-tooling` builds (2026-10-12, f58e9df4e); the tooling test tree (1,784 tests, about 40 s) is what still runs whole every
time. It took the GM's words to cover that tree.

## Amendment 2 (2026-10-13, same session)

The session reported that the reuse of amendment 1 left 102 of the tooling tests' 175 test-seconds in files that always run
- they ask git about the repository (29 test-seconds, 6 more with ruff), start a Python process that drops the recording (28),
run a bash guard (16), or other programs (22) - and that a landing's other ~100 s had not been measured. The GM asked:

> But does that really mean that there is no smartly when we can skip such that it would be more difficult than a simple spec, and so we haven't tried? because this does seem like it's worth looking into to see whether that could be sped up by figuring even if it's a little bit more complicated. And hey, maybe it's just not feasible, that's fine, but it just seems worth looking at, you know?

The session proposed replaying each read-only git question and keeping the Python children's recording, and timing each step
of a landing first. The GM:

> Yes, please. So go ahead and do the savings that you've already measured, no matter what. And then, like you said, figure out where the rest of the 100 or so seconds goes. And then see what can be done there. And then go ahead and land whatever timing improvements you are able to figure out. Thanks.

## Amendment 3 (2026-10-17, same session)

The session listed what was still pending: the tooling test files that always run (about 5 s of wall time per landing), the
test runner's startup (about 4.5 s, mostly every worker collecting every test, including the files the reuse then skips),
the guard suites a landing reaches (narrower inputs, or the slow suites split), and the review agents' models (spec-fidelity,
glyph-check, impl-drift, building-review and the three modal checks never tried on Sonnet). The GM:

> I do think that the tooling tests that always run, which make up five seconds of wall time per landing, do seem worth addressing.

> I don't understand what you're telling me about guard suites. like what the potential improvement is. Is it that we would be able to optimize away running some of those when they haven't been modified? Because that in general seems worth doing.

The session proposed three items (the always-run files, not importing the test files a run will not run, measuring and
narrowing the guard suites; the fork server left out). The GM:

> I don't think that the fork server is worth it for the amount of gains in this case. If we were spending like 5 or 10 seconds loading all of the code that is in our dependencies, then that would be one thing, but that's a lot of plumbing to add just for one second of gains. Realistically, we'd probably spend a lot more time than we would save uh, debugging the various problems that would result from it and such. I also agree that the hot reload server is not worth it, though I am glad to know that there's an option there if we ever change our minds. However, I do really like the thing that you said about not importing tests that we are not planning on running. So I guess the quick tests, for instance, really could probably save a good percentage of their current runtime because we run a lot fewer tests there, right? And just in general, when we're doing targeted runs on things that have changed, then that does seem worth doing.

> If we have never tried spec fidelity or glyph check or implementation drift or building review. Or the three modal checks on Sonnet, then that is definitely 100% worth testing, and we should do that pretty much right away. I have checked and I cannot find any record of us having tried those, so I believe that you are correct, and my memory that we had tried other models everywhere was faulty. So thank you for looking that up and clarifying it.

> Thus, I accept your proposal. Of three things, but I would also like you to add a fourth thing, which is doing those measurements on cheaper models. In fact, I believe that Sonnet 5.5 is now available, which sounds perfect for this. If you don't have access to that one, then I can have you reopen the feature and then upgrade Claude Code and then launch a new session, which will have that model available.

## Amendment 4 (2026-10-17, same session)

The session listed the guard suites still run as one long serial run each (main-tree 58 s, no-poll 52 s, finished-run 40 s).
The GM:

> I think I do want a next round uh, for the guard suites running serially, so uh, splitting those up does seem good.

The session broke a landing's 30 s down: the tooling tests 18.6 s (the longest step; a whole-repository test alone 9.4 s,
another 4.8 s, and about 5 s of a fresh checkout's start-up), the push 9.4 s, the guard suites 2.8 s beside the tooling tests.
It asked whether to fold the two tooling-test items into the round. The GM (dictated; "sweet" is "suite"):

> Yes, I think that would be good, thanks. Because really, it sounds like what you're saying is that the tooling tests are where the bulk of that time went. So that does seem like we should try to optimize that specifically. So yes, please fold those two into the same round as the sweet splitting. and then go ahead and work that. Thanks.

## Amendment 5 (2026-10-17, same session)

The GM asked why test_lint_scope and test_sources re-run on every `make done`. The session found: the gate runs the whole
tooling tree whenever its tooling hash changes (any Makefile edit) with no per-test reuse, and that hash misses `scripts/`
subdirectories; in a landing, reuse is judged per FILE, so one test reading the real record makes every test in its file
re-run on any research edit. It proposed (1) the gate's tooling run reusing as a landing does, with the hash gap fixed, and (2)
reuse per test, with (3) code-only tests moved to fixtures case by case. The GM:

> Yes, please file it that way, and then do that work. Thanks.
