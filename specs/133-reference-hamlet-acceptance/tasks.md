# Tasks: The Reference Hamlet Is Accepted by the GM (133)

Checked off only when verified on Inashiro. Every task from T10 on is the GM's, verbatim, one at a
time, and carries its clock (plan.md "The task clock"). The skeleton phase (T01-T04) is NOT
measured - the GM's instruction.

## Phase 0 - the skeleton (not measured)

- [x] T01 `spec-fidelity` review of this skeleton: round 1 one change (no route promise), round 2 FAITHFUL - recorded in spec.md
- [x] T02 the would-have-dispatched trail (FR-004): `runlog.write_would_have` + `would_have_report` (inside `remote_spend_report`, so `make ci-status` and `make audit` show it); written from `ci/__main__.py` (remote-off refusals of check/image, LOCAL-GATED merges whose verdict is `REFUSE(remote-enabled)` = would have DISPATCHED) and from the Makefile's `REMOTE_OK` via `ci remote-ok`; entirely in `ci/` + Makefile so the skeleton's delta stays DIRECT; tests in `tests/ci/test_runlog.py` + `test_main.py`; `make quick` green
- [x] T03 the doctrine (FR-007): constitution v2.3.0 "Iteration wall-clock is the cost" (the GM's words), root CLAUDE.md iteration heading, skill CLAUDE.md "The goal all of this serves", SKILL.md "The working rule behind the tooling"
- [x] T04 skeleton pushed to main at 8b796dcb (route DIRECT, observed - the delta was specs, docs, ci/, Makefile, tests); a fresh session's clone carries it. `.specify/feature.json` is gitignored: the fresh session must point it at `specs/133-reference-hamlet-acceptance` (or export SPECIFY_FEATURE) before its first task, so the gated route knows the feature

- [x] T05 (unmeasured, the GM's ruling FR-006): a feature in progress lands nothing on either route - derived active feature, spec-directory-only exception; `sync-with-main.sh` + test 7d (fires on DIRECT, on GATED, via the pointer; quiet when every task is ticked and for the claim). Note: this guard cannot itself reach main while 133 is open - it lives in this clone (`reference-testing`), which the fresh session should reuse by taking the same name

## Phase 1 - the GM's tasks, one at a time (measured)

_(appended as the GM names them; each entry: the GM's words verbatim, then `given | done | elapsed | runs:` and a `note:` only if the time was out of proportion)_
_(from T11 on, each entry also carries its cycle plan before work starts - `scaffold:` / `measure:` / `verify:` per the tasks template - so the round-trip cost T10 paid (~30 of 57 min) is designed out at the task, not remembered)_

- [ ] T10 **sunlight for the gardens and threshing yards** - the GM (2026-08-25): *"there is not enough space for sunlight to hit the gardens and thrashing yards. I could have sworn that we had a documented minimum amount of space. that, for example, the threshing yard in front of the farmhouse needs to have In order to receive enough sunlight every day. Yet I see a number of threshing yards in the reference hamlet which are directly north of a farmhouse. Thus, that farmhouse will have its shade blocking the threshing yard. Similarly, The Windbreak Forest, which is to the left, which is to say the left of the farmhouses in the reference hamlet, is so close to the gardens or at least so close to some of the gardens that I do not believe that those gardens would get sufficient sunlight. Therefore, we should update both our placement algorithm such that when we are placing a new farmhouse, we place it a certain minimum distance away from other farmhouses such that it will not block the threshing guard. and then the same thing is true when we are placing the windbreak for us. We place the windbreak for us after all farmhouses are complete, so we should enforce at placement time a certain minimum distance. We can then separately have automated checks, which confirm that our placement algorithm has done this correctly. This seems relatively straightforward to me because the order in which we are doing things should make this fairly easy. We are essentially just increasing the minimum distance for the placement that we are already doing. Therefore, I do not expect this to be difficult. However, it is possible that there is some aspect that I am missing or some subtle interaction that we will run into."*
  `given 2026-08-25T22:43Z | done 2026-08-25T23:55Z (make done green, 3669 passed; settlement-review: sun rules confirmed on every plot, needs-work on the belt being off-page - a conflict between the 2026-07-20 frame ruling and this lane, the GM's to settle; recorded in research/homesteads.md). GM 2026-08-26 chose to open the frame at the belt's inner face (option A): `windbreak_face` (median of the per-band front row - the first cut used the single most protruding clump and the reviewer sent it back) + `crop_boxes` + `crop_hugs_content` + `village_grove(face_margin=)`; ~45 min over two rounds; `make done` green x2, settlement-review PASS; committed 0dfb0f6b
  note: measured first - the yard rule already held (min 42 ft); the beds (7 of 16 shaded) and the belt (8 ft off) had no rule. The belt lane was priced at 75 ft (15 m stand) and declined to 50 ft (10 m working belt) because the frame does not open for the windbreak (GM 2026-07-20) - at 75 the belt dropped to 38 clumps with a hole. Time went to: one research pass (~5 min, parallel), the segment-name/fixture-order conventions (2 cycles), and `make map REF_OK=1` stalling on an interactive prompt (8 min) - the tooling lesson: after a red reference, `make maps` is the regen route, never an override

- [ ] T11 **plank bridges over the irrigation channels** - the GM (2026-08-26): *"My next issue with the reference Hamlet map is that I think there should probably be planck bridges over the irrigated channels in a few places. Right? Or are these two narrow for that? They don't look too narrow. Is it intentional that they're missing or an oversight? Please add them if they should be there in the appropriate places."*
      given 2026-08-26T04:28Z | done - | elapsed - | runs: -
      scaffold: none new - `channel_footbridges` + `long_ditches_have_a_footbridge` + `worth_planking` already exist; the question is the 3.0 ft stride threshold (a session's 2026-08-17 call, not a GM ruling)
      measure: research first (Principle XII); then count planks per ditch role on the regenerated Inashiro from the manifest
      verify: `make maps` (reference scope) once; `settlement-review` on the plank placement

## Phase 9 - acceptance

- [ ] T90 the would-have-dispatched audit (FR-005): every entry in the period, and for each whether it should have run; each "no" names a tooling change
- [ ] T99 **the GM accepts the current state of Inashiro** - tickable only on the GM's explicit word, recorded here verbatim
