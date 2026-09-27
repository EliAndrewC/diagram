# The GM's request (verbatim, 2026-09-26)

<!-- SOURCE: GM NOTES -->

Asked while looking at the Kashikawa map:

> I am looking at the map of Kashikawa. My big question is about the windbreak forest, which I thought was supposed to be to the north and west because of the direction of the winds for the geographic region. But this one is to the east and the south, so it's basically the opposite. But I don't see any, any explanation for that. Is this just a bug in the map generator?

and, after the session explained that the generator reads the wind off each map's slope and then renames
it after wherever the cluster came to rest, and proposed making the northwest the default with a local
override only where a map declares one:

> Yes, please implement that entire spec kit feature with only when declared as the default, and none of our maps should have this declared at the present time. So it should be fixed everywhere for now.

<!-- /SOURCE -->

## What the session had proposed (the "entire spec kit feature" the GM accepted)

- Northwest becomes the default windward side, and the seat search places the village with its back to
  the northwest instead of renaming the wind afterward.
- Local terrain overrides northwest only under a rule we can state - the GM chose: only where a map
  DECLARES a local wind. Today it happens silently on every map.
- When a map does depart from northwest, the windbreak pop-up says so and gives the reason.
- The record's false "northwest by default" sentence gets corrected.

## The GM's rulings on the placement defects (verbatim, 2026-09-26 and 2026-09-27)

<!-- SOURCE: GM NOTES -->

Asked whether Kashikawa should drop its declared brook flank, keep its houses across the brook, or declare a local
wind, and whether the reference hamlet Inashiro may be re-seeded:

> I do not want to route around deficiencies in our placement algorithm.  If we ever ended up with findings like "our research shows that farmhouses were literally never on X side of their common fields" then that's one things, but if we find instead that our placement algorithm ends up not making it possible to lay out a known-to-be-valid settlement configuration then we should fix the placement algorithm instead.  Which situation is this?

Told that it was the second - the record puts a settlement's own small channel through the middle of the place, and
the brook strike-out is labeled in the engine as "a GUESS ... what this engine can draw" because no way crosses the
brook - and that the fix is to let ways cross the brook with a plank footbridge:

> Yes that's fine, please add that to feature 261 and then do all of the work, not stopping until you have it complete and working.  Let me know when you're done and it's landed on main.

<!-- /SOURCE -->
