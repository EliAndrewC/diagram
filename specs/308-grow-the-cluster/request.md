# Request (GM, 2026-10-02, verbatim)

After feature 306 (seat by packing) landed, the GM asked:

That's great work, and I'm glad that we've made it so much more efficient.  That said, can you explain a few things?  First, what do you mean by "which take 5–13 s because they still need 3–6 margins"?  What does "need 3-6 margins" mean in this context?  Second, why do we need up to 148 offers per house?  That still seems like a lot, doesn't it?  For that matter, it's fantastic that we went from over 100,000 checks on our largest call to "only" 2,624 but what are those checks and why are there so many of them?  Two adn a halfthousand checks is a lot of checks just to place a homestead.  Finally, and I think this is probably the most important, why did "growing outward from the houses already placed" fail?  I ask because that is the most intuitive placement algorithm to me.  Like, once you've placed the first house, you should notionally be able to compute the minimum distance needed to seat a second house, then place it in a direction, then repeat, with a little randomized jitter to the distance and direction so that it's not jhusgt an unrealistic grid, or something vaguely along those lines.  Why does that not work?

The session's answer (summarized): a "margin" is one side of the field the cluster may sit on; the seater seats every household
on the best one and, where it falls short, throws them all away and seats the next - the slow seeds lose 2-4 s per thrown-away
margin. The 148 offers a house count the thrown-away margins too (~25 a house on one margin); most offers are refused because no
straight path from the door to the access lanes clears what already stands, which the last pass learns only by asking. The 2,624
comparisons are not seating at all - `ways/street.py:joints_along`, the lane stage measuring each lane end against every short
segment of a street line, once per map. The grow-from-the-houses prototype (feature 306 research R3) was not a fair test: it
offered positions one house-box from a neighbor, which is exactly where the neighbor's door path and woodlot lie (refusals:
envelope 2,393, a reserved path under the house 2,372, no path 933, a reserved woodlot 708); it ran only as the last pass after
the front row and lattice had scattered 15-20 houses; and it ran on the too-small 104 ft band. A fair version: a footprint that
includes house, yard, garden, woodlot and the path out; grown from the first house with jittered direction and spacing; each new
house's path laid back to its neighbor's as it goes (reachability by construction); replacing the three seating passes; on the
162 ft band - prototyped outside the engine first.

"Want me to start that as the next feature?"

The GM's reply, verbatim:

Yes please.  And of course keep in mind the sunlight / shade requirements when computing minimum distance, since "contents of the homestead" is not the only thing which determines minimum distance, i.e. casting shade on a threshing yard also contributes.
