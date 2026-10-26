# T08's measurements: the ground cover family (US4)

**Load this file when:** you check what T08 removed, or re-measure it.

Seed 39 at 40 households, observed 2026-10-26 (method: `make perf-fanout STAGES="hinterland windbreak" HOT=20000`; the start is
`dev/perf-log/20261026T213327Z-fanout-427-T08-start.txt`, every stage; the end `dev/perf-log/20261026T215756Z-fanout-427-T08g.txt`).

| chain (`research/hotspots-pairwise.md` "Ground cover") | what changed | before | after |
|---|---|---|---|
| `household_bamboo` -> `strip_refused` -> `stand_spares_seats` | a loop with no `abs` call a seat | 213,100 (its generator) | gone |
| `close_belt_gaps` -> `GroveBlocks.inside` -> `RingIndex.inside` | a column's 33 depths asked at once (`GroveBlocks.inside_many`); the ring's shapes built once; an outline shapely reads as invalid counted as arrays | 97,488 | under 20,000 (gone from the gap fill) |
| `close_belt_gaps` -> `too_near` | a loop, not `any()` over a generator | 64,545 | gone |
| `convex_hull` -> `cross` | the turn test inline | 90,187 | gone |
| `belt.fouled` -> `edge_within` / `inside` | every vertex at once: `inside_many` and one shapely ring distance a crop | 65,000 (`near` 63,120) | gone |
| `belt_law` `uv` / `bin` / `_near` | written inline over the crowns and the ways; `_near` once a bin | 32,609 / 28,243 / 25,506 | under 20,000 |
| `woods._crown_seat_clear` | a loop, no `max` a crown | 55,656 | gone |
| `groves.py:590` (the persimmons a clump reads) | read once while `canopy_frozen` holds | 37,515 | gone |
| `stages.py:493` (each copse clump's nearest house) | one numpy pass | 37,515 | gone |
| `_draw_grove` -> `_canopy_keepouts` | the buildings and wellheads read once while `canopy_frozen` holds | 556,320 `dict.get`, 182,085 `hypot` | gone |
| `past_the_lanes`, `far_envelope` (the belt's lanes and its far face) | each column and sample one numpy mask | 486,200 and 114,240 `abs` | gone |
| `_crown_covers`, `parts_hit` | the gaps and the ring's box written out, no `abs`/`max`/`min` | 210k and 250k builtins | gone |

`math.atan2` / `math.degrees` (27k, n^4.5 from 1.2k) stand: small, and no chain of 50,000.

The stages at 40 households: hinterland 5,468,426 -> 3,416,188, windbreak 2,796,372 -> 1,313,513; at 20, 3,022,637 -> 1,958,026 and
1,126,185 -> 681,460. Every pool manifest unchanged against HEAD after every step (`make maps-moved`).

One step measured worse and was fixed before it stood: batching the gap fill's columns first raised the hinterland stage
(3.59M -> 4.17M) because `RingIndex.inside_many` built its polygon and two buffers on every call; the shapes are now built
once an index and prepared.

Also in the change: a fixture that finds no seat is named by its kind (`lay_fixtures`; impl-drift's aside on T12 - every kind
raised the privy's 48 ft words).
