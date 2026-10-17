# Feature 385 T03 - D17 (the side-by-side merge) and seed 49: the measured matrix (2026-10-17)

## What T03 fixed and keeps (measured)
- Seeds 17, 21, 40, 45 (the four T03 owns) pass `make cohort N=1`.
  Causes:
  - A household's way was held 7 ft off its OWN garden fence (17, 21, 40). Fixed by `fabric.owned_gardens`, a DEVIATION on 0246's drawing page.
  - A way drawn by the reach was dropped by the network rule before any join could reach it (21's second cause). Fixed by the join steps after the reach, in `settle.STEPS` and the last resort.
  - The sty placer and the grove check read different boxes (45). Fixed by the shared `grove_rules.fixture_on_band`.
- D16: a refused roll keeps its manifest, and refusals name their rule.
- A cohort WITHOUT the merge read 59/60, the one refusal seed 49 - but it was `N=54` and rolled no seed past 54 (see below).
- Seed 49 is refused at HEAD too (a detached worktree), so it is pre-existing.

## D17, the merge, as tried (all saved in the scratchpad, d17/)
1. REACH inside `tails.along_tail` (20 ft): the reference map (Inashiro) refused a farmhouse, then a tree lane breaking
   `doubled_tails` the settle may not cut. So the law and the merge were split (plan re-decide, CLEAR).
2. The merge as its own settle step (`side.settle_side_by_side`), the later way cut to a T at its far end, written only where
   `Lawful` admits it and nothing is stranded, the household's corridor kept in step (`set_corridor`), a way that joined the
   cut stretch carried onto the way (`reseat_on_way` at REACH), REACH 25 ft calibrated on F1-F3 (18-25 ft):
   - Inashiro F1, F2 and F3 all merge (lane 14 ends on lane 8's start; lane 15 carried).
   - Seed 49 passes.
   - BUT the 60-seed cohort: 58/66. Seeds 7, 24, 37, 51, 52 and 57, which pass without the merge, are refused. Most are
     farmhouses unreached once later settle passes act on the new junctions; two are new lane knots and one a needle loop.
3. Seed 49's second cause is D17's own shape: its root household's way ran 18 ft beside the skeleton and ended unjoined. The
   network rule dropped it with the three ways hanging from it.

## The question
T03's plan (D22) does not let a task close with an exit no task of the feature owns. D17's merge, done, regresses six seeds.
Not done, it leaves Inashiro's F1-F3 (the glyph-check's NEEDS-WORK, accepted 2026-10-17 and carried to T03) and seed 49 as they
stand at HEAD. Which route: (a) land T03's seed fixes with D17 and seed 49 carried, as their own measured task of this feature,
to a later task (the merge needs the later settle passes made aware of the junctions it creates, which is not T03's four seeds);
(b) keep T03 open until the merge passes the cohort; (c) another the arbiter names.

## The confirming cohort (about 22:00, what would land: the seed fixes, no merge) - `.git/cohort60-t03c.log`
63/66. Refused: seed 49 (4 farmhouses and the field unreached), seed 55 (lane_knots, 1), seed 57 (lane_knots, 4).
At HEAD (a detached worktree): seed 55 fails lane_knots with the SAME knot; seed 57 fails lane_knots (1 knot); seed 49 is
refused. So nothing newly fails; 17, 21, 40 and 45 are fixed; 49, 55 and 57 are pre-existing (57's one knot is four now).
(The earlier run read 59/60 with only 49 refused: it was `N=54` and never rolled 55-60 - a cohort's count is not its seed set.)

## The question, restated
Land T03 as its seed fixes (the four, no regression against HEAD), with D17's merge (saved, measured: F1-F3 merged and seed 49
fixed, but six seeds regressed) and the three pre-existing failures (49, 55, 57 - lane knots and an unjoined way, T01's lane
law) carried as ONE later task of this feature - or keep T03 open until all of it passes?

## The pool (`make maps SCOPE=all`, about 22:00, the code that would land - the route offered changes no code)
maps clean. One map changed: Kashikawa, one touch lane (lane 9) straightened from 3 points to 2 - it no longer bends round
its own household's garden fence. Every other pool map CACHED or regenerated unchanged.

## The hour-6 condition: seed 57 bisected (22:06-22:20 UTC, `make cohort N=1 SEED=57`)
HEAD: 1 lane knot (lanes 3/6, refused by `needle_joins`). With T03's three changes: 4.
- Own-garden removed: 3.
- Join order removed: 2.
- The sty predicate removed: 4 (it adds none).
- The join order kept ONLY in the last resort's passes (the settle's own rounds back as at HEAD): 2. Seeds 17, 21, 40 and 45 still
  pass. That form is what T03 now carries.
- The remaining +1 knot: lanes 1/13, ends 21.6 ft apart. `settle_knots`' gather of lane 13 is refused by `needle_loops`: the join
  would close a sliver between two ways - the side-by-side family the carried task (D17's merge) owns. It comes with the
  own-garden change, which fixes seeds 17, 21 and 40.
Pool (`make maps SCOPE=all`, the narrowed code): maps clean; Kashikawa lane 9 straightened, as before.

## The claims gate at landing (23:15 UTC): three findings read as introduced
All three are on code T03 did not change in behavior; the 0246 drawing-page edit (the own-garden DEVIATION) re-owed their checks:
- `settle.py::theirs` DRIFTED: `own` takes every house within 80 ft of either end, so a neighbor's garden at a lane's junction
  end loses the 7 ft fence gap 0246 keeps from another household's garden. A real pre-existing defect; fixing it moves maps
  (a cohort-measured change, the lane law's own territory).
- `settle.py::Lawful.fault#no doubled tail` DRIFTED: 0081's 20 degrees against the code's 15 - the known gap already carried to
  T12 (the side-by-side family).
- `clearance.py::_clear_link` CANNOT-TELL: the bundle lacked `link_survives`, which its answer depends on.
The pool rolls clean on this code (maps clean, Kashikawa lane 9 straightened) and the cohort is as measured above.
