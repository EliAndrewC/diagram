# Research: seat by packing

## R1. Prototype round 1: capacity by packing boxes (observed 2026-10-02, method: `prototype.py observe 40 47,25` - the engine's own seating, with the prediction computed where the exhaustive pass starts and logged beside what the margin seated)

(Observed 2026-10-02, method: as the heading.) The prediction - the households standing plus a greedy pack of the smallest
homestead envelope over the seats the exhaustive pass would offer, on the seat region's raster with every standing box painted
- is 213-305 on every margin of seeds 47 and 25 at 40 households, where the margins seat 15-40:

| seed 47, per margin | seated before the pass | predicted | seated |
|---|---|---|---|
| 16 margins | 11-18 | 220-305 | 15, 18, 20-33, 38, 40 (the 16th) |

**So the free ground is not what fills.** Within the field's reach the ground holds two hundred-odd homestead boxes; the
placer refuses most seats on it for other reasons. A pack of boxes cannot predict a margin's capacity; whatever limits it is a
rule the placer asks of a seat (R2 measures which). Predicting took 409 ms over seed 47's sixteen margins.
