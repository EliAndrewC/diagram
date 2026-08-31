# `ways/` - the lane web, the track and what makes a path legal

Split from the 4,369-line `ways.py` by feature 173 (constitution Principle X clause 13 - the cost being managed is context-window tokens, and the bar is now GATED by `scripts/check-file-scale.py`). **Load only the file the task calls for**; this index is the map.

Its modules are LAYERS, emitted bottom-up: every cross-module reference points backwards, so the package cannot have an import cycle. **The monolith's source order was not its dependency order** - the stage entry points stood at the top and the primitives they call stood below - which is why the cut is by subject rather than by line range.

## Look here when

| file | look here when |
|---|---|
| `geom.py` (316) | point and segment math on a bare polyline - lengths, turns, crossings, nearest-thing queries, and the two pushes that move a point off something |
| `checks.py` (190) | the questions asked ABOUT a finished network - which houses are unreached, which lanes share a tread, where a way crosses crop or water it should not |
| `clearance.py` (449) | may a way BE here - the clear-run scan, the clip, the span and touch tests, the bend/nub judgments, and `may_write`, the guard every rewrite passes |
| `route.py` (220) | the router itself: `_route` finds a way round hard ground, `_unjog` straightens what it found, `_ease_corner` rounds the corners it leaves |
| `fabric.py` (428) | the settlement fabric a way must respect - the homestead polygons, the margin frame, the fabric-collision probes, and `_draw_web`, the single place a web lane is committed to the map |
| `sweeps.py` (536) | the passes that REMOVE or REPAIR after the web is laid - doubled remnants, steading fouls, end nubs, necked routes, debris, collinear breaks, orphaned pieces |
| `touch.py` (445) | how a lane end meets the network - the whole junction-touching pass and the piece-joining it falls back on |
| `smooth.py` (341) | the smoothing pass and the connectivity accounting that decides whether a smoothed lane may be committed |
| `serve.py` (552) | getting a way to a house that has none - laying one web lane, and the straggler search that runs when the ordinary passes left someone unserved |
| `web.py` (545) | STAGE: the lane web - `stage_web` and the skeleton it starts from. Read this first to see the order the passes above run in |
| `track.py` (522) | STAGE: the track and the seat - the connector out of the frame, the cluster gateway, and the thread through the fabric |
| `__init__.py` | the composed surface only - the re-exports that keep every existing importer working. Never add logic here |
