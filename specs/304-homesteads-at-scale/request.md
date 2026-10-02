# Request (GM, 2026-10-01, verbatim)

The GM's question:

If we wanted to improve the performance of our scripted hamlet generation, what do you think is a good next step, given the current state of things?  I'd like to move on to scripted generation of villages soon, but first I want to make sure there's no more low hanging fruit when it comes to performance.

The session's answer (summarized): at the reference hamlet's size (15 households) the stages total 2.6-3.8 s after feature 302,
no stage over about a second, and 297 measured those levers' ceiling at about 1.14x. The household count is where it goes wrong:
a scratch probe lifting the 10-20 band on the reference spec (seeds 4 and 25) measured the stage total at 1.8-2.1 s for 10
households, 4.1-8.3 s for 20, 13-15 s for 40; at 80 the field refused (`FieldRefused`, one fan cannot land 104 acres). The
homesteads stage is the superlinear one (0.4-0.5 -> 1.5-5.0 -> 7.1-7.7 s; 4x the houses, ~16x the time); the field, web and
hinterland grow roughly linearly. Profiled at 40 households (seed 25): `seat_the_rest` made 3,774 `try_place` calls to seat 40
houses (~70% of the stage), each refused seat paying the corridor search, layouts and fixtures; `AccessTree.targets`
(`settlement/rolling/access.py`) measures and sorts every corridor point per door (30,000 calls, the tree growing with the
houses - quadratic); the standing-ground clearance scans called `seg_dist` 1.8 million times. cProfile roughly doubled the
stage, so the proportions want the wall-clock sampler. Proposed: (1) a scaling bookend timing the reference at 10/20/40
households beside the 15-household one, so a village-size regression cannot land unseen; (2) index `targets` and the
standing-ground scans (output-identical, the safest lever); (3) stop offering seats that cannot work - update the seat region
as houses land, or build the line-of-sight reach region 297 priced and did not build (may move maps, which is allowed). The
field's refusal at 80 households was noted as a village-design question, not performance.

"Want me to claim this as a spec-kit feature and start with the scaling benchmark?"

The GM's reply, verbatim:

Yes please.
