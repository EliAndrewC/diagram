# Feature 276 - the GM's request (session "Diagram (Inashiro)", 2026-09-28)

## The request, verbatim

> Yeah, but let's go ahead and do all of them, actually. Like... Yes, let's go ahead and make those test side fixes, but then I think as part of the same feature, you should just address all three hotspots in the engine that you have identified. So please proceed with that. And then let me know when it has landed on main. Thanks.

## What it answered - the GM's question, verbatim

> Yeah, I mean, I realize that because this stuff is run in parallel and we have a lot of CPU cores that cutting any one of these tests probably doesn't make much of a difference, but I'm basically just trying to figure out in general which of these represent a test itself being slow and which of them represent something about our algorithms being slow because when I see that something takes nearly four and a half seconds then my thinking is that there almost certainly must be a better way to do this because we're frankly just not dealing with data that's that big, you know? I mean, we have Hamlet maps with like 15 farmhouses on them and a few dozen rice paddies and like a few hundred trees. You know, that, that really shouldn't add up to four and a half seconds on a modern CPU core. Unless we're doing something very inefficient, which we very well may be. And so I'm less interested in optimizing specific tests as I am in getting to the root of these inefficiencies, because even though we have a fairly smooth development experience right now when we're only working on hamlets, then when we move on to larger settlements like cities with thousands of population, then it's just going to be a nightmare if we don't have efficient algorithms in place and such. So, like, just take a look at a high level at the most expensive stuff that we're doing, and then really take a critical eye at whether any of it could be made more efficient without any actual loss of fidelity. Now again, I don't even care if the maps themselves change in some way, like if our algorithm shifts slightly and then the maps are not bit for bit identical. That's fine because literally none of our maps are things that the specifics matter for in that sense. You know, none of them represent something that has been canonically established to be true within the setting. So it is completely okay for things to shift a bit as long as the underlying reality of what these settlements are generally like stays the same. So with all of that in mind, please take an analysis pass over what we're doing and figure out, hey, why does it take several seconds to run so many of these tests? And what can we do about it? I mean, the one second status recording step also seems worth cutting or dealing with. I'm not like 100% sure what's involved there and I would have to look at it, but yeah, I mean, I'm not saying no to that, but in addition to that, let's look at all this other stuff. Thanks.

## The analysis the GM said yes to (the session's reply, summarized; the one-second status step was fixed before this feature, commit on main 2026-09-28)

Test-side slowness (the test, not the engine):
- four tests (`tests/test_memory.py`, `tests/hamletgen/test_driver.py`, `tests/test_package_surfaces.py`,
  `tests/settlement/test_water_ways.py`) each re-parse ~264 engine modules and walk every AST node
  (1-1.5 million each, 2.3-6.6 s);
- the research-record tests (`tests/interactive/test_record.py`, `test_record_format.py`) re-scan the record per
  page and per term (544 regex scans 3.1 s; 15,473 whole-corpus `str.find`s 2.2 s; a Python loop over 8,118 files).

The three engine hotspots:
1. homestead placement is generate-and-test - `_place_bundle` walks a 157-offset spiral per house, rebuilding
   the bundle geometry and running the whole fit test per candidate (the rescue-rounds test: 304 attempts,
   46,781 candidates, 6.6 s for ~15 houses) - the one expected to explode at city density; proposed: a
   free-space index updated as houses land, answering the nearest fitting seat directly, the bundle shape
   built once per size and translated;
2. comb-field seam closing (`waterfields/seams`, `close_seams`) ~1 s per field, ~80% of a field build, spread
   over steps of hundreds of small per-polygon shapely calls with duplicated work (`_plant` computes
   `k.buffer(-half)` twice); proposed: batch with shapely 2's array operations, remove the duplicates, guard
   the grid a long thin pocket can produce (one test's map cut ~1,400 cells per pocket);
3. the track stage's `path_violations` re-scans static water and crop geometry per candidate path.
