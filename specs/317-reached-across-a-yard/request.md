# Request (GM, 2026-10-02, verbatim)

After feature 314, the session recommended laying the lanes first and seating the houses along them. The GM declined it (recorded
at `dev/placement.md`, "THE HOMESTEADS COME FIRST") and added:

Now there is a `Diagram (Inashiro)` session, which is the only other session currently running, which has been involved in bug fixes of this type. So if there are some outstanding bugs or things on main, then you should please coordinate with that other session to make sure that you don't both end up fixing the same thing. But I do want all known bugs to be fixed.

Then, while the session was recording that ruling:

Now, can we also definitively say that a network of village lanes definitely reached every house and that it was not instead the case that sometimes people would basically just cut through their neighbor's yard to get to the farm fields or whatever? I mean, if that is what the research bears out, then we should go with it. I just want to make sure that we did not accidentally impose a strict requirement, which is causing us to disregard optimizations that we know work in order to meet a requirement that is not actually a requirement and is not based on our research. Because that is a mistake that we have made before, so I want to make sure that that's not what we're doing here.

The session's research pass (2026-10-02, a sonnet agent; scratch copies in the session's scratchpad, `wig.txt` is Wigmore) found no
source stating as a rule that every house in a clustered village was reached by a lane, and found customary rights of passage over
a neighbor's land for landlocked plots in Wigmore, *Materials for the Study of Private Law in Old Japan* (1892), Part V §3 and §10
(https://archive.org/details/materialsforstu00japagoog) - in at least five provinces, mostly not marked rural or urban, one entry
(Kaga, towns) naming a house.

## Amendment (GM, 2026-10-03, verbatim)

The session explained the band-3 perf cell (seed 25 at 40 households, +21.6%: the passage proving at each tight seat that no
routed path reached the tree) and named two levers. The GM:

So here is my ruling on the shared lane stuff:

> A follow-up redesign of the path search, sharing one map of what's reachable across searches instead of searching from scratch each time. The perf audit estimates it might save about half of the extra time. It's a feature-sized job.

Yes, definitely do this.

> A cheaper test for "no way of its own": straight and round-the-house paths only, no routing search. Faster, but it's a guess, and it would seat some households across a yard when a routed path actually existed.

Yes do this too, we don'y need to be rigorous because people cut through their neighbors yards all the time.

To clarify the second point: cutting through a neighbor's yard is not some kind of huge deal that needs to be rigorously avoided at all costs.  Frankly, even if there IS a lane you might do it anyway if it was faster or more direct.
