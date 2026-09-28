# Research - feature 282

The research itself is on the record: `research/homesteads/025-what-lay-in-the-work-yard-at-harvest---straw-mats-over-the-whole-floor.html`
and `research/homesteads/505-did-a-village-put-its-drying-racks-by-the-houses-by-custom-or-because-of-its-weather.html`
(their sources, checks and reader reports as run 2026-09-28). This file holds only what the spec measures.

## R1 - the yard glyph as drawn before this feature

Observed 2026-09-28; method: read from `_draw_threshing_yard` in `settlement/homestead_parts/yards.py` at commit
c13a6ebe6 - one mat `<rect x="-7" y="-6" width="14" height="9">` at the yard's center in the local frame, whatever the
yard's size (14 by 9 map px, 14 by 9 ft at a hamlet's 1 ft to the px), and a rack of two rails and three posts across
the yard's full width at `h / 2 - 3`, its local south edge.

## R2 - the sun corridor

Not a measurement of this feature: the `39 ft` of clear ground south of a yard is research homesteads 030's derived figure
(the shadow of a `20 ft` ridge at 9:00 and 15:00 in the tenth month at 38 N), quoted here because FR-006 and SC-002 keep
the rack out of it.

## R3 - the pool's yard sizes

Observed 2026-09-28; method: `w` and `h` of every `threshing_yards` record in `pool/hamlets/inashiro/inashiro.json`
before regeneration - fifteen yards from 20 by 14 ft to 47 by 32 ft, so a full cover of 3 by 6 ft mats is about 15 to 84
mats; the mat band of FR-004 is sized against that range.

## R4 - the gap, and the yards that cannot hold a third at it

Observed 2026-09-28; method: the regenerated pool manifests' `threshing_yards` (`w`, `h`, `mats`, `rack`) after the lattice
search (at each gap of `2`, `1.5` and `1 ft`, the lattice as wide as the inset allows and one column and one row narrower,
each tried centered and pushed half and all the way to either side of its slack; each corner held `1 ft` inside the drawn
outline and each mat's outline `0.1 ft` clear of its neighbors'). The narrower steps were tried and read as paving in the
settlement-reviews: edge to edge (rounds 2 and 3), and `0.5 ft` (rounds 4 to 6). At `1 ft`, 9 yards of the four rice maps
fall one or two mats short of a third of a full cover - inashiro 20 x 14 ft 4 of 6, kashikawa 22 x 15 ft 6 of 7, kashikawa 22 x 15 ft 6 of 7, kashikawa 27 x 19 ft 9 of 10, sawada 24 x 16 ft 7 of 8 (rack), sawada 31 x 22 ft 12 of 13 (rack), sawada 22 x 15 ft 6 of 7 (rack), sawada 25 x 17 ft 8 of 9 (rack), sawada 20 x 14 ft 5 of 6 (rack) -
the pulled-in corners of their outlines, or the rack, leaving no room for the last mat at that gap. The fewest any yard
draws is 4 (Inashiro's `20 x 14 ft`).
