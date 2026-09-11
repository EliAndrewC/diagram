# Feature 222 - the GM's request, verbatim (2026-09-11)

The session `diagram-performance` had profiled every pool hamlet end to end on 2026-09-10 (the record is
the last section of `.claude/skills/diagram/dev/performance.md`) and reported the ranked levers. The GM:

> I could have sworn we already put in the work to make the hinterlands code more efficient. Am I just
> completely misremembering that? like, I thought that we had previously done the work that you're
> describing. am I thinking of a different optimization, and you're saying that there's a further
> optimization to be done? Either way, it does sound like merging each blade group into one path would be
> a good idea. and also I am willing to at least try the lossy JPEG compression for the final image if
> that seems like it will gain us about four seconds. And, hey. If we don't like it or if the lossy
> nature means that it becomes blurry or otherwise bad, then we can always reverse it. Running the three
> renders concurrently instead of in sequence also seems good. and the title pocket scan index as well.
> So go ahead and make all of those changes. Thanks.

The session's answer to the first question (the GM is remembering feature 218, which indexed the
hinterland's SCATTER; the title-pocket scan and the bamboo seat scan are different functions in the same
stage) is in the conversation, not part of the request. The four items the GM approved are the request:

1. merging each blade group into one path;
2. lossy JPEG compression for the final image (the page's picture), if it gains about four seconds -
   reversible if it looks blurry or otherwise bad;
3. running the three renders concurrently instead of in sequence;
4. the title pocket scan index.

The session's proposal the GM approved, from the 2026-09-10 report:

> **Ranked levers**, seconds per regen: lossy WebP or RASTER_R 2 (-3 to -4); run the three renders
> concurrently instead of in sequence (-2 to -3, no output change); blades as one path and no off-map
> scatter (-1 per resvg pass, three passes); the title-pocket scan indexed (-8 on Kuwabata); bamboo on a
> grid (-3 on Sawada); the wells key (-0.5 to -1).
