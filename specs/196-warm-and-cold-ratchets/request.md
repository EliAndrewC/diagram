# The GM's request, verbatim

2026-09-06. Feature 195 was complete and verified but could not land: the `done` ratchet was red at a
median of 522 s against a 520 s ceiling. The session diagnosed it, refuted two candidate causes
(41 newly-landed tests, which run in 3.4 s total; and roll-cache state, since both compared gates
were cold), showed that the last twelve green runs spread 379-895 s (2.4x), and put three options:
fix the ratchet to compare like with like, re-pin, or leave the feature unlanded. The GM:

> Separate medians for warm and cold seem like the correct solution, so yes please go with that,
> thanks.

## What the session had established before that instruction

- The gate's cost is **bimodal on roll-cache state** (feature 192, R7): a cold cache costs ~115 s
  more in the floor phase alone, and more again in the map-rolling tests.
- **A median over both populations describes neither.** Feature 192 R5 recorded this as a known
  limitation and deliberately left it to its own feature; this is that feature.
- The tell is already printed by every gate run: the reference line says `[HIT]` or `[MISS]`.
- The 400 s baseline the GM ratified is, on the evidence, the **WARM** figure - measured warm runs
  are 381 s and 398 s. Cold runs were never in its scope, which is why they cross it.
