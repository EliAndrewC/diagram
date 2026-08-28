# Research: placement against a few segments (feature 140)

## R1 - what placement was testing against (the census, 2026-08-28)

Instrumented on unmodified code (feature 138's engine). The homestead fit does NOT test individual
paddies or scatter strokes: `field_polys` is ONE polygon per field (the envelope, 49-73 vertices), the
145 crop plots are consulted only by `_hard_clear` (bbox-gated, ~0.5 s), and the scrub / trees / bamboo
never enter placement. On the seed-19 polder one entry in `block_polys` was the perimeter dike's drawn
band - **2,880 vertices** - and `_rect_hits` ran `point_in_poly` on it 25,223 times: 8 of the roll's
~24 s. The reference has no such polygon (fit 1.3 s). The hinterland scatter's 1.3 million
`point_in_poly` calls are its SAMPLE count against 4-62-vertex outlines, not many shapes per sample.

## R2 - how many chords the real outlines need

`simplify_ring` (Douglas-Peucker on a closed ring), then the chords whose outward normal faces the
planned cluster seat:

| map | outline | whole ring, eps 3 / 6 / 10 | facing the cluster, eps 6 | eps 3 (the engine's) |
|---|---|---|---|---|
| reference (Inashiro) | 73 | 26 / 18 / 11 | 5 chords, 1 chain (6 vertices) | 8-9 chords |
| seed-19 polder field | 49 | 34 / 26 / 14 | 7 chords, 2 chains | 9 |
| seed-19 polder dike crest | 144 | 35 / 22 / 16 (eps 4 / 8 / 12) | closed ring: 22 chords at eps 8 | |
| cohort 41 / cloud 7 / lane 5 | 84 / 48 / 59 | | 6 / 4 / 5 chords | |

The GM's *"fewer than ten vertices for the reference hamlet"* holds at the engine's tolerance.

## R3 - the tolerance, chosen by the gate

With the houses re-seated against the chains, the reference's lane web is fragile to the seats moving:
at 3 px the reference is CLEAN; at 4 px it fails `lanes_bend_like_paths`; at 6 px that and
`lanes_form_one_network`; at 8 px `captions_clear_the_ways_they_stand_on`. That is a property of the
lane web (feature 137 / the peer's 139 residue - `lanes_bend_like_paths`, 7 of 48 cohort seeds), not of
the chords, and it is the kind of thing feature 141's audit should weigh. 3 px it is
(`FIELD_KEEPOUT_EPS`); the dike ring's 8 px (`DIKE_KEEPOUT_EPS`) never touched a verdict.

Two lessons paid for on the way: (1) outward normals by a CENTROID test are wrong inside a concave
pocket - one chord vertex of a wobbly test ring escaped its own keep-out until the normals came from
the ring's winding; (2) the gate must measure THE PLACER'S OWN chains, recorded flat at finish
(`M["field_chains"]`) - rebuilding them from the manifest's rounded outline let Mizuguchi pass placement
and fail `houses_clear_of_paddies`. A mitered INWARD offset folds at a reflex corner, so the ring's inner
edge uses plain normals plus tolerance.

## R4 - the numbers, and what moved

| | before (138) | after |
|---|---|---|
| seed-19 polder `stage_homesteads` | 9.2 s | **1.9 s** |
| seed-19 polder roll, solo | 24.3 s | **~17 s** |
| reference roll, solo | 15.2 s | ~16.5 s (its fit was 1.3 s; the difference is noise and `stage_hinterland`) |
| the reference through the gate | CLEAN | CLEAN (8-9 chords) |
| live pool after the merge of feature 137 | inashiro clean; kashikawa red (overlap + network); sawada red (title + network); mizuguchi red (windbreak) on main's committed manifests | inashiro clean; **mizuguchi clean**; kashikawa and sawada red on `lanes_bend_like_paths` only - the peer's 139 T05 residue class, individually diagnosed as the same lane-web bends the splice fixes leave (constitution XIII: a rotated residue, named) |

Every map moved (14-16 of 15-16 seats on the reference and the polder): the setback is now measured
from the chords, up to the tolerance farther out than from the outline (a DEVIATION under constitution
XII: legibility of the placement rule, 3 px = 3 ft at hamlet scale, recorded here and at
`rolling/fit.py::_field_chains`). Reviews of the moved maps: see tasks T07.
