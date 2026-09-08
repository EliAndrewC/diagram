# Feature 218 - the GM's request, verbatim (2026-09-08)

The session had measured a from-scratch roll of the reference hamlet (Inashiro, seed 4) at 36.2 s
wall clock - 23.7 s of placement, of which `stage_hinterland` took 8.1 s, `stage_windbreak` 7.3 s
and `stage_field` 5.4 s. The GM:

> So Eight point one seconds is a really long time, as is seven point three seconds, and five point
> four seconds. So I guess my question here is whether those things really actually need to take
> that long. For example, you're saying that the windbreak forest takes over seven seconds to
> render. Is that because we are doing some kind of overlap check every time we place an individual
> tree? And if so, are there ways in which those overlap checks could be made to be more efficient?
> For example, it used to be the case that it took a very long time to place our farmhouses. And the
> reason why it took so long was that we were doing an overlap check with essentially every part of
> the rice patty. But then we realized that we could actually just draw a line or a series of line
> segments between the farm fields and where we're replacing our farmhouses, and then we only needed
> to make sure that our farmhouses were on the correct side of that line, which is computationally
> much simpler. I wonder whether there is something similar that we could do with our windbreak
> forest placement. For example, suppose that we were to Start by drawing the outline of where the
> Windbreak Forest is going to be, and then we lay down all of the trees within that outline. If we
> do that, then the trees need only to not overlap with one another, which sounds much simpler and
> computationally easier than if we were to do something like make sure that every tree does not
> overlap with every farmhouse or something. Again, I'm not sure exactly where that time is going,
> but I know that seven seconds represents many billions of computations. And I believe that there
> is probably a simpler algorithm that we can enact, which will cut that time down significantly.
> Does that sound right to you? What do you think?

While the session profiled the three stages, the GM added:

> For what it's worth, I suspect that what I am describing is probably also true of the hinterland
> and the field. Though I understand that the field is a little more complicated because it does
> involve a lot of small shapes being created which are all derived from the branching of earthen
> bunds, etc. Though one imagines that there are algorithmic improvements that could be made, which
> might accomplish the same thing. However, I am much less certain about this for the fields than I
> am for the wooden break forest. So I do think that we should start there and perhaps limit
> ourselves to only the forests for now, and then we can take a look at the hinterland to see whether
> there is a similar thing happening with our grass strokes and scrub pines and such. because I do
> wonder whether there is something much, much simpler that we could do. which would take a fraction
> of a second rather than the many seconds that we are spending now.

The session reported the profile: the windbreak spends 77% of its time computing the distance from
each of 37,490 candidate clump positions to every edge of every crop polygon (7.2 million segment
distances); the marsh scatter rebuilds the entire watercourse segment list for most of its 27,383
points (73% of the hinterland stage); the field's time is in closing the comb's seams, a different
shape. It recommended one feature for the windbreak and the hinterland, with byte-identical
manifests as the acceptance test. The GM:

> Yes. Please claim that feature, which should include both the windbreak and the hinterland. then
> proceed with implementing that from start to finish. I will be interested to know how long the make
> done tests take when we are finished. I believe that we currently only roll 3 Maps. So these tests
> might not be significantly faster, but I will still be curious to know how our performance is
> affected. Also, if nothing else, then this should become our standard practice for laying out this
> type of thing in the future. This will matter more and more as we build larger maps. For example,
> our provincial city maps were taking hours to lay out by hand, and while a scripted process will be
> faster once we eventually get to that We will need to take care to make sure that We do not have
> literally every item on the map checking for overlap with literally every other item. or anything
> silly like that. Obviously, this is not something that we can mechanically enforce at this exact
> time, but we can make sure that our project guidelines and perhaps even our spec kit constitution
> is upgraded to talk about the importance of all features which involve overlapping and overlap
> checking within a map or diagram performing an efficient version of that check so that we do not
> spend tens of seconds on things which could be performed in a fraction of a second if we are more
> sensible about how we do it. I do not believe that it is appropriate at this time to include any
> new subagent checks. But in the future, it could potentially be the case that any code which
> involves overlaps or overlap checking gets reviewed by a subagent to ensure that we are not doing
> anything silly, like what we are doing right now. and that we therefore implement the smart version
> that we are currently going to change into during this spec kit feature, which you are about to
> implement start to finish. Thanks a bunch. Please proceed.

While the session was converting the hinterland's scatters (the windbreak already at 0.5 s and the
reference hamlet regenerating byte-identical after each step), the GM added two messages:

> For what it's worth, just to be clear, the results do not need to be bite identical to what we
> were doing before. It is okay if the hinterlands lay out their glyphs a little bit differently or
> if the trees of the windbreak forests show up in a slightly different place. It is absolutely not
> required that the changes that we are making here result in bite identical output or even in the
> things being placed in exactly the same manner as long as they still follow our general rules, and
> the maps end up looking more or less the same.

> In particular, if we are able to gain additional performance benefits at the cost of having the
> maps look a little bit different than that is okay so long as nothing ends up overlapping, which
> isn't supposed to overlap, etcetera.
