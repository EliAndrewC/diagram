# Tasks - 227 the homestead's envelope first, and the page from the code

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review FAITHFUL; research R1
      research: rendering
      verify: DONE. spec-fidelity round 1 CHANGES REQUIRED (the gardens condition as a criterion, Steps mandatory on every stage, D4 both directions), round 2 FAITHFUL 2026-09-12; R1 the probe split written
- [x] T02 FR-001 the envelope-first nucleated placer, with its tests; `make map` Inashiro
      research: rendering
      verify: DONE. settlement/rolling/place.py _place_bundle_nucleated: the union envelope, then each configuration's own box (_envelope_blocked, nine points against the boundary, the placed boxes) and the parts' rules once (_parts_fit); tests/settlement/test_rolling.py 53 green; make map Inashiro 15/15, 0.09 s
- [x] T03 FR-002 the seat at its standoff and the one computed move; the spiral and the slides retired
      research: rendering
      verify: DONE. the front row's standoff computed per chord (seats.py _front_row_from_chains: the wall rule + tilt slack + the house's half-extent along the normal, a second rung for a yard the paddy faces); the one computed move per configuration (the measured overlap, away from the neighbor); _slide_nuc, the spiral and _spiral_rings retired; the ranks behind the front row proposed behind the standing houses (stages.py)
- [x] T04 FR-003 the counts; the pool; the cohort
      research: rendering
      verify: DONE. meta.seat_search counts positions (rectangles), parts, front, rounds; the pool re-rolled 5/5 with every quota on the first roll (rects per house 16-37 against 113-387); make cohort N=48 48/48 with households_seated; R2 written
- [x] T05 FR-004 the page from the docstrings and the declared steps, the boundary on the homesteads plate, the notes retired, the tests
      research: rendering
      verify: DONE. tools/placement_stages.py writes the page from each stage's DOCSTRING and the functions its Steps: section names (93 step cards over 18 stages), the notes JSON retired into the docstrings it described, the site boundary drawn over the homesteads plate, the plates rendered in parallel, the web's deferred ways counted as ink; tests/tools/test_placement_stages.py holds every stage to a docstring and a resolvable Steps list
- [x] T06 FR-005 the landing re-plates the page; R2; `make done`; the settlement-review
      research: rendering
      verify: DONE. render_cache.replate_page re-plates the page from the landing's render step when the engine fingerprint moves (a docstring moves it - the fingerprint is over bytes), with its test; R2 written from the final pool; make done green 2026-09-12 (56 s, 100% coverage); make cohort N=48 48/48; settlement-review two passes then a verification pass - PASS, all five fixes landed, no invariant broken; perf band 0 after the bookend was re-taken at the reviewed commit
- [x] T08 FR-008 the lane-end rule fixed test-first, with a reader on every shipped hamlet
      research: rendering
      verify: DONE. the lane-end rule fixed test-first: the red tests (end_serves reads arrival at a steading, arrival is tighter than the reach bar, the trim keeps a tread at the dooryard) then one shared body end_serves + steading_footprints, STEADING_ARRIVAL_FT derived from the clip, the straggler trim and the late web pass on the gate's bar with keep; a pool-wide reader over every committed manifest; all five maps clean by the placer's own predicate, cohort 48/48, R3 written
- [x] T09 FR-009 the guard adds the proof of life, and stops refusing the wait that has one
      research: rendering
      verify: DONE. no-poll adds the proof-of-life clause to a permitted file wait (scripts/_writer-alive.sh, the kernel's open-file table and the mtime, never a process pattern) and stops refusing a wait that carries one; the output-file rule made per-part so the feature-165 boundary does not move; 74/74 in scripts/test-no-poll-hooks.sh including the helper's four answers and the shape that was refused on 2026-09-12; R4 written with oom_kill 36
- [x] T10 FR-007 a plate after every step that laid ink, with its cost measured
      research: rendering
      verify: DONE. a plate after every step that laid ink: 23 step plates beside the 14 stage plates, decided in the order the ink landed (the field's hem, paddies, source and ditches in turn), the deep copy moved into the plate worker so 37 plates cost less wall clock than 14 did (R5: 38 s, 6.0 MB); one step plate is unrenderable and the page says why
- [x] T11 the amended spec re-reviewed, the pool and the cohort re-run, `make done`, the settlement-review
      research: rendering
      verify: DONE. the amended spec re-reviewed (round 1 CHANGES REQUIRED on four items, round 2 FAITHFUL); pool re-rolled and clean by the placer's own predicate, cohort 48/48, make done green at 100% coverage, perf band 0 (-23.5%); settlement-review of both moved maps - Inashiro PASS on the lane delta with two notes errors fixed, Kashikawa PASS with no errors, its stale copse count fixed and its rule-level question measured over the pool and recorded
- [x] T07 FR-006 the GM's acceptance of the page after their rounds in the clone
      verify: ACCEPTED by the GM 2026-09-13, in their own words: "I also accept the Hamlet placement HTML
      page that I believe was the last item in the spec hit feature that requires my explicit approval. So
      you can go ahead and mark that off such that when you are done with your current round of work, then
      it can all merge back into the main checkout." Offered with the complete render set present, as
      FR-006 requires: every pool map carries its .png, the five hamlets their .html, and the page itself
      re-plated from the current code (dev/placement-stages/hamlet-placement.html, 39 plates).
      research: rendering
