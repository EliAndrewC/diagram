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
