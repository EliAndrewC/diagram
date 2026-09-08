# Research - 217 rolls earn their lines

## R1. The rule against the roster it was born on (2026-09-08)

The verdict's arithmetic, run through `make roll-census` over feature 216's last green census with the run's combined
coverage database, before any conversion:

    Inashiro seed=4: 1 roll(s) ... rostered; requested by test_a_map_is_immune_to_an_upstream_change_in_the_number_of_
        lines only this roll reaches: 17 - pipeline/rollcache.py:393,395,397,399-403,405-407,409,415,417-420
    Polder seed=12: 1 roll(s) ... rostered; requested by test_a_rolled_cohort_passes_the_whole_gate
        lines only this roll reaches: 10 - hamletgen/water.py:414,475,574; pipeline/rollcache.py:431,433-435,531,547-548
    Seatings seed=5: 1 roll(s), attempts 4 ... rostered; requested by test_the_cluster_seeds_cloud_still_seats_a_hamlet_when_the_r
        lines only this roll reaches: 0
    ROLL CENSUS FAILED:
      - Seatings seed=5 (...) reaches NO engine line that no other context reaches - constitution VI ...

Two things to read off it. The immune reference's seventeen lines are all the perturbation machinery (`extra_draws`,
`_perturbed_manifest`) - the roll is an emergent-condition test the GM ruled on in 2026-08-08, and under the rule as
accepted (zero, not a number) it passes; the doctrine's judgment about it is the GM's, and the printout is what makes
that judgment possible every gate. The seatings' zero is an artifact of a census written BEFORE the record carried its
context: the verdict fell back to the requesting test's `|run` context, while the roll's lines live under the FIXTURE's
(`fixture:tests/gate/hamletgen/test_homesteads.py::seatings`, one unique line by 216's audit). Read straight off the
database, that fixture's one line is `hamletgen/homesteads/seats.py:110` - the `continue` that skips a web lane, or a
lane of the other kind, in `lane_frontage`. A stub settlement with three lanes asks that in a millisecond
(`tests/hamletgen/homesteads/test_seats.py`), and with it in place the seatings' unique set is empty, which is why the
row converts (spec D2).

**The Polder roll's context is the fan-out's.** Under worksteal whichever test asks first makes the shared roll, so the
lines are attributed to that test's context - here `test_a_rolled_cohort_passes_the_whole_gate|run`, on another run
the lane-rules test's. The rule is indifferent to which: the set is the same roll's lines either way, and the unique
count is over contexts, not tests.

**Why the record carries the context rather than the verdict guessing it.** A roll requested from a fixture records
its lines under the fixture's context (feature 207's `fixture:<baseid>::<name>`); one requested from a test body under
`<nodeid>|run`. The verdict cannot tell which from the test id, so the child's environment - which already carries
`L7R_COV_CONTEXT` for the coverage label (feature 213) - is written onto the record. The `|run` fallback stays for a
census written before this feature.

## R2. Measured after (2026-09-08)

**The census verdict on the landed gate** - a COLD run (`gencache.py` changed, so every shipped generator re-rolled), which
is the case that matters for the `PoolGen` exclusion:

    roll census: 7 roll(s) of 6 spec(s); 11 request(s) served from a shared roll; roster 2 row(s)
      Inashiro seed=4: 2 roll(s), attempts 1, 1, 57s - rostered (+ the pool gen: its key moved); requested by test_the_cli_reports_a_single_hamlet, test_a_map_is_immune_to_an_upstream_change_in_the_number_of_
          lines only this roll reaches: 0 (the shipped generator's roll: printed, never judged)
          lines only this roll reaches: 17 - pipeline/rollcache.py:393,395,397,399-403,405-407,409,415,417-420
      Kashikawa seed=3: 1 roll(s), attempts 1, 37s - pool gen; requested by test_village_passes_gate[kashikawa.gen.py]
          lines only this roll reaches: 5 (the shipped generator's roll: printed, never judged) - hamletgen/ways/serve.py:109; hamletgen/ways/web.py:454,457; settlement/structures/fixtures/siting.py:221-222
      Kuwabata seed=21: 1 roll(s), attempts 1, 36s - pool gen; requested by test_the_polder_hamlet_draws_no_forbidden_overlap
          lines only this roll reaches: 21 (the shipped generator's roll: printed, never judged) - hamletgen/water.py:450-457,580; hamletgen/ways/clearance.py:173; settlement/fields/comb.py:516-518,520-526,534
      Mizuguchi seed=23: 1 roll(s), attempts 1, 16s - pool gen; requested by test_village_passes_gate[mizuguchi.gen.py]
          lines only this roll reaches: 11 (the shipped generator's roll: printed, never judged) - hamletgen/ways/serve.py:463; hamletgen/ways/sweeps.py:189; settlement/water_ways/lanes.py:198-204,210-211
      Polder seed=12: 1 roll(s), attempts 1, 63s - rostered; requested by test_a_polder_reservoir_backs_off_until_its_rim_clears_the_c
          lines only this roll reaches: 8 - hamletgen/water.py:414,475,574; pipeline/rollcache.py:431,433-435,531
      Sawada seed=6: 1 roll(s), attempts 1, 43s - pool gen; requested by test_village_passes_gate[sawada.gen.py]
          lines only this roll reaches: 11 (the shipped generator's roll: printed, never judged) - hamletgen/sink.py:168-169; hamletgen/ways/route.py:147-149; hamletgen/ways/touch.py:237,239; settlement/shrines_wells/byres.py:37,100; settlement/water_ways/lanes.py:207-208
      stand-in stage rolls (stub-excepted modules, no map): 19, 2.4s in all
      pool gen: Inashiro seed=4 (pool/hamlets/inashiro/inashiro.gen.py) - ROLLED this run: its cache key moved
      pool gen: Kashikawa seed=3 (pool/hamlets/kashikawa/kashikawa.gen.py) - ROLLED this run: its cache key moved
      pool gen: Kuwabata seed=21 (pool/hamlets/kuwabata/kuwabata.gen.py) - ROLLED this run: its cache key moved
      pool gen: Mizuguchi seed=23 (pool/hamlets/mizuguchi/mizuguchi.gen.py) - ROLLED this run: its cache key moved
      pool gen: Sawada seed=6 (pool/hamlets/sawada/sawada.gen.py) - ROLLED this run: its cache key moved

Read against the spec: the two rostered rolls are judged and pass (the immune reference 17 lines, the polder 8); the
five shipped generators are printed and never judged, INCLUDING the Inashiro cold roll that a gate module
(`test_the_cli_reports_a_single_hamlet`, reading the pool's map through `gate_obtain`) requested before the sweep did -
the mark on the child's record decides, not the requester. That Inashiro cold roll reaches 0 lines of its own on this
run, which the GM can now see every cold gate: the reference's coverage is carried by its rostered perturbed roll and the
other four pool maps. On a warm run the census reads 2 rolls of 2 specs (the shipped generators served from the gen
cache). SC-001 and SC-003 hold.

**The gate**: 192 s cold (the five pool re-rolls are the difference from 216's 143 s warm); pytest 146 s, 3459 passed, 2 skipped, 5 warnings in 146.09s (0:02:26);
the engine floor 23,307 statements at 100%, the hamlet-path floor 13,012 at 100%. The guard suites: `test-guard-file-hooks.sh`
36 of 36 (section 6 is this feature's), `test-make-only-hooks.sh` 74 of 74 (four roster cases), `hooks-test` 7 suites re-run
green on the first gate, then stamped.

**Three gate runs to green, each a finding**:

1. `tests/tooling/ci/test_main.py::test_remote_off_refusals_leave_would_have_entries` - a FLAKE unrelated to this feature,
   fixed under Principle XIV: a run-log entry's filename stamp read its seconds from `time.gmtime()` and its microseconds
   from a separate `time.time_ns()`, so an entry whose two reads straddled a second boundary sorted BEFORE one written
   earlier in that second (`ci-image` ahead of the `ci-check` refused before it). One clock read now (`runlog._stamp`),
   with a test on the boundary.
2. The rule fired on the Inashiro COLD roll: the pool generator was requested first by a gate module, so by requester it
   looked like the rostered roll and was judged (0 lines of its own -> red). The mechanism now marks the record
   (`_census.GEN_ENV`, set by `gate_obtain` and `run_gen_child` for the child), the verdict keys `PoolGen` on the mark
   with the requester prefix kept as the fallback for a census written before it. Spec FR-001a's exclusion held; what
   was wrong was how the verdict recognized the excluded kind.
3. Green, above.

**Found on the way, fixed**: an apostrophe inside the guard-file hook's single-quoted `python -c` program broke the whole
hook (every case of its suite red, 22 of 36) - the roster's Read-time context is written without one, and the suite
now proves both the roster's context and the generic one. A `make test-file ... | tail` chain's exit status is `tail`'s,
which let a red test commit and launch a gate once; `set -o pipefail` ahead of the chain.
