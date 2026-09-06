# The GM's request, verbatim

2026-09-06. Feature 195 was complete and verified but could not land: the `done` ratchet was red at a
median of 522 s against a 520 s ceiling. The session diagnosed it, refuted two candidate causes
(41 newly-landed tests, which run in 3.4 s total; and roll-cache state, since both compared gates
were cold), showed that the last twelve green runs spread 379-895 s (2.4x), and put three options:
fix the ratchet to compare like with like, re-pin, or leave the feature unlanded. The GM:

> Separate medians for warm and cold seem like the correct solution, so yes please go with that,
> thanks.

## What the session had established before that instruction

- The gate's cost is **bimodal on roll-cache state** (feature 191's research.md, R7): a cold cache costs ~115 s
  more in the floor phase alone, and more again in the map-rolling tests.
- **A median over both populations describes neither.** Feature 191's research.md, R5 recorded this as a known
  limitation and deliberately left it to its own feature; this is that feature.
- The tell is already printed by every gate run: the reference line says `[HIT]` or `[MISS]`.
- The 400 s baseline the GM ratified is, on the evidence, the **WARM** figure - measured warm runs
  are 381 s and 398 s. Cold runs were never in its scope, which is why they cross it.


## Corrections to this file's own framing, after review round 1

The session-written section above originally cited `specs/192-the-gate-rolls-once/research.md`. That
file does not exist - R5 and R7 live in `specs/191-refusals-that-tell-the-truth/research.md`, and
feature 192's own spec cites 191 correctly. The GM's quoted sentence is untouched.

It also asserted a cold median of 546 over a set of runs (525, 546, 651) whose seconds appear nowhere
in the run log. The evidenced figure is **577** over 522, 544, 610, 651. Both errors ran in the same
direction - toward a lower, more permissive cold baseline - which is exactly why a session-pinned
calibration number owes its full sample.
