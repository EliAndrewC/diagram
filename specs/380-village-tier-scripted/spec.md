# Feature Specification: when villages are scripted - what we know it must do

**Status**: Filed - the village tier's placeholder (2026-10-10): every item known to be owed when villages become scripted, carried here word for word. Not exhaustive: what that work finds is added here, never filed as a village-only feature of its own (`make speckit-todo CHECK=1` refuses one and names this feature).

**Approved**: the GM, 2026-10-10, "I agree with your approach, so please do it."

**Affects**: village

**Input**: the GM, 2026-10-10 (request.md, verbatim): *"I think that all of the things that are owed when we implement villages should be consolidated into a single spec kit feature ... that feature should not be exhaustive, because we are not saying in advance what will happen as part of that scripting ... but that is the placeholder feature for anything that we come up with that we realize needs to happen when villages become scripted. And then the same thing applies to towns. And then the same thing applies to provincial cities."*

Rewriting this into a full spec, a plan and tasks is the work of whoever scripts the village tier (`/speckit-specify` on this directory, `docs/migration-plan.md` for the order); each carried item below becomes a requirement or is answered there.

## Carried items

Each was a filed feature of its own until 2026-10-10 and now reads `Superseded by 380`; its text is kept here as filed, headings demoted two levels.

### 350 - OPEN 2026-09-28: a village's funerary grounds (was feature 275, withdrawn), and the headman's gate

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-28, OWED AT CONVERSION: a village's funerary grounds (was feature 275, withdrawn), and the headman's gate", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: village

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

**History**: this work was feature 275 (`specs/275-village-burial-ground/`), which the GM withdrew on 2026-09-28 (its request.md: "The number stays spent; nothing is built under it"); it is filed under its own number here rather than reopening 275 (plan D5, the plan review of 2026-10-08).

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

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

### 351 - OPEN 2026-09-27: the village generator draws no shrine grove, sacred tree or basin

**Status**: Filed - from future-work/farming-communities.md, "OPEN 2026-09-27, OWED AT CONVERSION: the village generator draws no shrine grove, sacred tree or basin", 2026-10-08 (feature 330: the GM retired that directory; this is the entry as it stood)

**Affects**: village

**Input**: deferred work, filed by feature 330 when the GM retired it as a directory of its own listings (2026-10-08): *"Everything that is there should instead become an unimplemented spec kit feature."*

Rewriting this into a full spec, a plan and tasks is the work of whoever picks it up (`/speckit-specify` on this directory); until then `make speckit-todo` lists it as filed.

#### The entry, as filed

Feature 268 (the GM, 2026-09-27: "Add grove to map") put a grove, a roped sacred tree and a stone basin round
Hoshigaoka's shrine by hand, and the country-shrine program now says a village shrine's precinct holds its
grove, in the form its ground gives (research religion-and-death 124, 126, 129). No generator draws them: `rolling/roll.py`'s civic shrine lays the
hall, its arches at the 12 ft pitch and its well, nothing more. So converting Hoshigaoka (or any village) drops
them. Sketch: after `shrine_hall`, reserve a precinct outline from behind the shrine well to the outermost arch
(the register band of research 124 as its area), carve the clearing and the approach, then lay the WOOD in the
form of the program's knob 8, `grove form` (feature 279, research 129): read the hall's ground - at the foot of a
slope the candidates are `behind` / `behind and sides`, at the top with the approach climbing to it
`behind and sides` / `sides`, midway on an even slope all three slope forms, on a rise or flat paddy `all around` -
and roll between the candidates from the settlement's seed with equal weights; the wood's region is a smooth-noise outline about the form's base shape,
never a ruled box (the edge is its crowns' own where it meets scrub or slope; where a paddy-plain wood meets its
fields, its foot rolls the program's second grove knob - `field line` along the fields' straight edge, as a
photograph shows, or `ragged` - with equal weights). Fill the
region with the grove scatter the windbreak already uses (a `KeepoutGrid` of the clearing, the approach and the
well), carry the scrub into the precinct's open ground, then seat the sacred tree beside the approach and the
basin at the innermost arch, and the keeper's kitchen garden (a `gardens` entry) on the open ground nearest the
dwelling that gets its six hours (feature 283, `garden_sun`'s sun; Hoshigaoka's sheet draws it below the forecourt,
west of the approach). Measure: the region's area and canopy share, and feature 279's `STRAIGHT_RUN` on its
edge crowns (no four within 2 ft of one line), against the hand-drawn Hoshigaoka grove (form `behind and sides`, feature 279), and the `LONG_RUN` bar (no
stretch of edge 50 ft or longer within a crown's radius of one line).

## Later tiers

The capital has no placeholder yet (nothing is owed at it alone). Items above marked *Also owed at: capital* are confirmed when the capital is scripted; the first capital-only item becomes that tier's placeholder.

## Carried: from 357 (the modern-only sweep's frozen villages)

Moved word for word on 2026-10-10 (the GM, 2026-10-10: "Yes, please."); 357 keeps its hamlet items and points here.

- **The frozen villages' owed forms**: Hoshigaoka - M12 (the pond sized by command area), M65 and M81 (the sanctuary fence),
  M66 (the swept collars), M68 (a hamlet's own burial ground),
  M70 (the roofed pyre ground, platform and hut), M71 (six jizo at a cremation ground alone), M80 (the basin's roof,
  drawn plain, its roof a guess); Kikuta - M56, M58. (M50, M52, M53 and M64 were kept by the GM on 2026-09-29.)


## Carried: from 387 (found by the soak tier, 2026-10-18)

- **The village roll seats too few households**: `tests/soak/test_village_determinism.py` fails on origin/main (`72b93d15c`,
  measured 2026-10-18 in a detached worktree; method: `make soak`): `roll_village("R", households=18, ...)` on seed 7 seats 13
  houses where the test holds 15-19. The soak tier runs only by hand, so nothing caught it; it fails the same on main without feature 387, whose own soak equivalence ran beside it green.
  Owed: find which change dropped the seated count (`git bisect` on
  `make soak`), and either restore the seating or record why 13 of 18 is right.
