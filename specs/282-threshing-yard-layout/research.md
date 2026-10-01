# Research - feature 282

The research itself is on the record: `research/contents.json#homesteads`
and `research/contents.json#homesteads`
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

Observed 2026-09-28; method: the regenerated pool manifests' `threshing_yards` (`w`, `h`, `mats`, `rack`, the outline to a
thousandth of a px) after the lattice search - at each gap of `2`, `1.5` and `1 ft`, the lattice as wide and as deep as the
yard allows and one column and one row fewer, at every offset on a quarter-foot grid; and, where the `1 ft` gap still falls
short of a third, solved exactly with no step anywhere: every spot's fit is a set of linear conditions on the lattice's
origin (each corner inside the outline moved in by the `1 ft` clearance, the mat clear of the rack), the seated count is
constant between their lines, and every crossing of two of them is tried, each region's set confirmed at its centroid and, where the rack's keep-out cuts a region so its centroid may fall outside it, a hair to each side of every crossing.
Checked by an oracle that shares no grid with it (every lattice origin on a `0.02 ft` grid anchored `0.01 ft` off,
`tests/hamletgen/test_pool_282.py`), which also finds the two yards the quarter-foot search alone left short. The narrower
steps were tried and read as paving in the settlement-reviews: edge to edge (rounds 2 and 3), and `0.5 ft` (rounds 4 to 6).
At `1 ft`, 6 yards of the four rice maps fall one or two mats short of a third of a full cover - inashiro 20 x 14 ft 4 of 6, kashikawa 22 x 15 ft 6 of 7, kashikawa 22 x 15 ft 6 of 7, sawada 24 x 16 ft 7 of 8 (rack), sawada 22 x 15 ft 6 of 7 (rack), sawada 25 x 17 ft 8 of 9 (rack) -
no lattice at that gap seating more. The fewest any yard draws is 4 (Inashiro's `20 x 14 ft`).
