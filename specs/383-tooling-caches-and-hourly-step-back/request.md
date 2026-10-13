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
