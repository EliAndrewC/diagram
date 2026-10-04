# Feature 320 - no ways placed before the homesteads (GM, 2026-10-04, verbatim)

Context: after feature 318 landed, the session explained that two ways are fixed before any farmhouse is seated - the
EXIT STRIP (a straight line from the cluster's center outward, kept clear of houses and later drawn as the start of the
track out) and, on a brook map, the FIELD WAY (the hamlet's path to its field, its route chosen and reserved before
seating) - and that page 0081 says the maps "seat every farmhouse before they lay any lane". The GM had asked:

Can you explain what you mean about lanes being reserved before houses?  We reserve SPACE for them, but that's just a matter of making sure the farmhouses aren't literally packed so closely together that there's no room for a lane, which to my understanding is not even a deviation, since "there is enough room for a lane between farmhouses" is line with all of our research for the countryside, isn't it?  Am I missing something?  Why would we need to record a deviation when we're merely doing a placement algorithm ensuring that there is space for a thing we know was there historically.

and, after the explanation:

Ah, gotcha.  Yeah, we should eliminate both the exit strip and the field way as things placed in advance of the homesteads being placed, because the space we've already allocated can serve the same function.  Now I do agree that it's not a real deviation, but I also don't think it needs to exist.  If it makes things significantly faster somehow then we can keep it as an optimization, but TBH it sounds like a complication we don't need.

## Amendment 1 (2026-10-04)

The session asked how to proceed on Kuwabata's marsh edge (a pre-existing marsh-shaping flaw this feature exposed; options: waive and file it, or fix marsh ends first). The GM chose:

Fix marsh ends first

## Amendment 2 (2026-10-04)

After the glyph check found a nub at the track out's start, and the session explained that the track's first leg and the track itself were two separate direction decisions:

Gotcha.  Yeah, I do want that little nub fixed as part of 320 before it lands.  Before you make any more changes or do anything else, can you explain to me why/how that happens?

Yeah, before we lock in a decision or do anything else: why ARE we making two different decisions instead of doing it all at once at the end?

Please finish your work on this feature and then land it on the main branch.  Finishing your work should include collapsing the multiple decisions into a single decision regarding the lane, since we have determined the multiple stages to be a prior implementation detail rather than any kind of requirement.
