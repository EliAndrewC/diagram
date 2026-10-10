# Feature Specification: OPEN 2026-09-28: a village's funerary grounds (was feature 275, withdrawn), and the headman's gate

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-28, OWED AT CONVERSION: a village's funerary grounds (was feature 275, withdrawn), and the headman's gate", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Owed at**: village

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

**History**: this work was feature 275 (`specs/275-village-burial-ground/`), which the GM withdrew on 2026-09-28 (its request.md: "The number stays spent; nothing is built under it"); it is filed under its own number here rather than reopening 275 (plan D5, the plan review of 2026-10-08).

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

## The entry, as filed

The GM, 2026-09-28: *"we just want to make sure that [when] we make village maps scripted that we do the correct
things in the scripted generation."* So the village's own burial ground is not a feature of its own now; it is owed by
the village tier's scripted generator when that is built (migration-plan step 5), with the rest of a village's
funerary grounds. The design, already researched:
- **The GM's ruling of 2026-09-27** (0226, 530): a village has a cremation ground and a hamlet none;
  the country monk lives in the main village and serves its district; within its district the village alone keeps the
  shrine, the headsman's house and the cremation ground.
- **The cremation ground**: already drawn by the roller's village tier (`_roll_civic` -> `_roll_cremation`, feature 273):
  530's `cremation_seat` knob, the shared `edge_seat`, six jizo, the ragged off-center glyph (feature 272). The village
  generator reuses it.
- **The burial ground**: 0236's knob (in the shrine or temple yard, or a ground of its own apart;
  even odds; a hilltop shrine always apart) and 270's siting (a ground apart downstream, beyond the last house,
  within ~650 ft of the middle of the houses); sized by 160's rule in the population served (the village's own
  households plus those of its hamlets, whose dead lie in the village's ground - `hamletgen/burial.py`, feature 280 M68);
  seated through `settlement/civic_grounds/edge_seat.py`. The cremation ground's "beside_burial" form then has something
  to stand beside. **A way reaches it**: no generator connects a graveyard at any tier today, and the record says a path
  was there (religion-and-death 140: at the seventh-day festival of the dead "the graves and the paths to the graves are
  cleaned", ndl-crd-nanukabon; 190 gives the pyre "a minor funeral path"). Register the ground's edge nearest the houses as
  a way target (`plan.way_targets`, feature 287 H36 - built, with no producer left since the hamlet's own ground was
  retired) so the web lays a footpath spur to it.
- **The wayside stones** (520: one to three at each place a road or lane enters a hamlet or village; a wayside-hall knob
  at even odds; Hoshigaoka's hand edit of feature 272 has them at the south lane's entry): put `boundary_marker` stones
  (unlabeled) beside each lane where it passes `BOUNDARY_STONE_CLEAR_FT` beyond the last house. The hamlet's own stones are
  the entry under feature 280 below; one placer can serve both tiers.
Hand-rolled village maps are not edited for any of this (the GM, 2026-09-28).

**The headman's gate (269 B19, the GM's ruling of 2026-09-28).** The scripted village MUST gate the headman's house.
The GM: *"As for the headsman's gate, Yes, absolutely, we should have that. ... I don't want you to update the
hand-drawn maps with this, but I do want it recorded in the research, and I do want it to be the case that when we
begin scripting our village generation ... we should absolutely make sure that the village headsman's house is gated
if that was a headsman's right."* It was: the one headman's plot read has a nagayamon (research/questions/0030-the-headmans-house-and-the-rich-farmers-homestead-shoya-gono.html, 520;
`specs/269-research-backfill/rulings-2026-09-28.md`). Measurement: `settlement/rolling/place.py` `headman()` draws a
92 x 56 ft house and no gate on every hand-rolled village. Mechanism: nothing in the roller knows a gate. Sketch: the
village generator seats the headman's house with a nagayamon on its road face as part of the plot, reserved with the
house, so a lane arrives at the gate rather than at the wall.

**The rest of 269's village rows (outcomes.md section 3), owed at the same conversion:**
- **Tax rice (B19)**: today the tax rice is taken to be in the headman's kura; the record allows either the
  headman's kura or a village gogura among the houses. Mechanism: no storehouse placer exists at the village tier.
  Sketch: a knob `tax_store` headman_kura / gogura, the gogura seated among the houses (`gogura-kotobank` gives the
  siting).
- **The cluster's spacing (B19)**: no house more than ~650 ft from the next. Measurement: no village is scripted, so
  nothing holds it. Sketch: the village's cluster seating asks a nearest-house test per candidate from the placed
  index, and the gate checks the largest gap.
- **The headman's house size (B19)**: 92 x 56 ft is about four times a farmhouse; the record reads 2 to 2.5 times,
  about 65-75 x 40 ft, a labeled guess. Sketch: the village generator takes the record's figure as `headman()`'s default.
- **The dosojin (B20)**: the entrance stone is a guess today; the record puts a dosojin by the road at the
  village's entrance. Sketch: seat it through `edge_seat` at the road's crossing of the village edge.
