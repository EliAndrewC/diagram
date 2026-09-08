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

## R2. Measured after

(The census verdict's printout on the landed gate, the roll count, the gate time, the guard suites' counts.)
