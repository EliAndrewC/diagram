# Research - 216 the floor as doctrine

## R1. The four sites, and what each needs

From 215's audit (`specs/215-the-floor-itself/research.md` R1): Woodland-shrink reaches 0 lines nothing else
does; Clamped 3 (`hamletgen/sink.py` 285-287, the pond-to-off-map fallback); Polder 19 0 alone (the two polders
together 3, all in `hamletgen/water.py`, two of them reached by either polder); the three seatings 10 together
(LaneOnly 4: `ways/route.py` 174-176, `ways/touch.py` 465; OneHouse 5: `hinterland/stages.py` 83,
`homesteads/wells.py` 311-314, `ways/web.py` 221; CloudOnly 0). A reference roll's stage times (perf snapshot,
seed 4): field 5.8 s, hinterland 8.0 s, windbreak 7.4 s of 24.4 s; homesteads 0.95 s. The seating tests read only
what the homestead pass decided, so a partial roll to that pass costs the field stage once (~6 s) and the three
seatings a second each, against three full rolls of ~24 s.

## R2. Measured after

(The feasibility probes, the census line and the gate's time, the audit's output on the landed baseline.)
