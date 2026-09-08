# Research - 216 the floor as doctrine

## R1. The four sites, and what each needs

From 215's audit (`specs/215-the-floor-itself/research.md` R1): Woodland-shrink reaches 0 lines nothing else
does; Clamped 3 (`hamletgen/sink.py` 285-287, the pond-to-off-map fallback); Polder 19 0 alone (the two polders
together 3, all in `hamletgen/water.py`, two of them reached by either polder); the three seatings TEN together
(LaneOnly 4: `ways/route.py` 174-176, `ways/touch.py` 465; OneHouse 5: `hinterland/stages.py` 83,
`homesteads/wells.py` 311-314, `ways/web.py` 221; CloudOnly alone 0; and one line two of the three share that nothing outside them reaches - the gate's floor names it). A reference roll's stage times (perf snapshot,
seed 4): field 5.8 s, hinterland 8.0 s, windbreak 7.4 s of 24.4 s; homesteads 0.95 s. The seating tests read only
what the homestead pass decided, so a partial roll to that pass costs the field stage once (~6 s) and the three
seatings a second each, against three full rolls of ~24 s.

**The probes (2026-09-08, before implementation).** The woodland band cannot be swept on the pool's loaded manifest
(`open_ground_patches` needs the field stage's plan state: `min() of an empty sequence`), so it runs on the hinterland
unit tests' stub site, which does return parcels. The three seatings on copies of one partial roll: the LINEAR seed-5
state (prefix to the homestead pass 3.3 s) holds the cloud's assertions (10 placed, `cluster_seeding` cloud, the
shape honored) and LaneOnly's and OneHouse's counts, but the frontage offers 0 seats until the TRACK stage has drawn
the connector - so each variant runs the homestead pass and the track (about a second each). The nucleated seed-7
state (prefix 11 s) offers no connector seats at all, so the linear one is the base.

## R2. Measured after

(The feasibility probes, the census line and the gate's time, the audit's output on the landed baseline.)
