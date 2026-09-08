# Research - 214 pack the roster

## R1. The ten rolls that were "a test's mechanism", adjudicated one by one

The claim under test is the session's own: *"roughly half of the 21 exist for coverage and half because a
test's behavior needs a roll of its own"*. The GM asked whether that is ACTUALLY so. Per site, what the
test proves and what it needs:

| roster rows | the test | what it proves | needs its own full roll? |
|---|---|---|---|
| Cohort-41, 42, 44 | `test_a_rolled_cohort_passes_the_whole_gate`, the lane rules over the clean seeds | every rolled map seats its households, lands its acreage, passes the gate; lanes bend like paths | NO - the assertions read `rollcache.report/hamlet(spec)` and hold on the coverage rolls (the probe below); seed 42 is the gate's single longest roll (three attempts, 170-240 s) |
| Cohort-43 | the strict xfail `test_seed_43_still_kinks_round_a_house_corner` | the one open defect (research R2b of feature 166) stays visible | YES - none of the four coverage maps kinks (the probe); it is an emergent condition like the other five, and dropping it would hide an open defect |
| Kashikawa 3 | the immune test | one extra random draw at `meta()` moves nothing | the PERTURBED roll is the experiment and cannot be served, so one roll stays. The clean side is ALREADY the pool sweep's shared gen-cache entry (the spec-fidelity reviewer's round-1 aside), so this test is in the shared-roll form today; moving it to the reference would save no roll and lose the off-map sink and fall-315 stages. Unchanged |
| Clitest 9 | `test_the_cli_reports_a_single_hamlet` | `main()` parses its arguments into a spec, calls `generate`, writes the artifacts, prints the report | NO - with `generate` patched to serve the shared roll (and write the artifacts from its manifest) the wiring is proven for zero rolls; `generate` itself is proven by every other roll |
| Childroll 3 | `test_the_child_rolls_the_same_hamlet_as_the_worker_would` | a child roll equals an in-process roll | the in-process half must roll in the worker (it IS the comparison); the child half is the shared roll, and the spec is the reference - the distinct spec goes, one in-worker roll stays as a stated duplicate |
| Inashiro 6 | `perf_snapshot.measure` timed stage by stage | the tool times every stage and records what was asked beside what landed | NO - stand-in stages under a deterministic clock (the stage-profile tests' own pattern, `tests/hamletgen/test_driver.py`) prove the same for milliseconds; the real seeds belong to `make perf-gate` |
| Inashiro 5, 7 | `perf_profile.profile_stage` | one stage profiled, the ones before it timed plainly and reported apart | NO - the same stand-in stages, named so `water_frame` and `sink` resolve |

**The probe** (`census/probe-2026-09-08.json`, run through the roll cache on the landed engine): the four
plain coverage rolls each seat every household, land within 15% of their target acreage (3%, 8%, 6%, 6%) and
pass the gate with no failures - the cohort ratchet's assertions hold on them unchanged. Kinks: none of the
four; seed 43 alone carries its kink at (991, 188), exactly as measured on 2026-08-30. Seeds 41, 42 and 44
are clean of everything, so nothing they carried is lost.

**The count after, in the packing record's unit (distinct specs a gate rolls).** The record measured 11 on
2026-08-31 and NINE after the two merges that section made; the nine are today's coverage set unchanged:
Inashiro 4, Kuwabata 21, Polder 12, Polder 19, CloudOnly, LaneOnly, OneHouse, Clamped, Woodland-shrink. To
those: Retry and NoHelp (the re-roll loop's own lines, added after the record), Cohort-43 (the open defect's
only carrier) and Kashikawa 3 (the immune experiment's perturbed roll): **13 distinct specs**. Rolls on a warm
full gate: the 13 plus three duplicates of the reference (the fan-out's pool child, the child-equality test's
in-process half, the cache round trip's gen): **16**, against 24 before and 37 at the start of feature 213.
And the single longest roll in the suite (seed 42, three attempts) is gone.

## R2. Measured after (2026-09-08)

The green gate's census: **16 rolls of 13 specs, 34 requests served from a shared roll** - SC-001 exactly, the
three duplicates all of the reference (Kashikawa's clean side served from the gen cache). The pytest phase
**204 s** and the whole `make done` **222 s** on six workers, against 313-336 s and 333-418 s for the full gates
of feature 213 the day before: the packing removed a third of the test phase, most of it seed 42's three
attempts. Before 213: 37 rolls of 14 specs and a 541 s median.

**Two things the first gate of this feature found.** Six engine lines were reached by the cohort seeds and by
nothing else - `frame.py` (the popped board's ink blanked; a verge refused because its nearest way runs across),
`homesteads/bamboo.py` (a strip on a dry plot, on a watercourse), `water_ways/_helpers.py` (a vertex consumed by
the pull-back) - so the packing record's "seeds 41-44 carry no unique lines" no longer held; each is now a direct
unit test of the function beside the tests that already existed for it, which is what constitution X asks for
in the first place. And the reference rolled TWICE in one gate seconds apart: `tests/pipeline/test_rollcache.py`
calls `rollcache.reset_shared()` ten times, and that removes the RUN SHARE DIRECTORY - under the gate's own
xdist id, so every reset wiped the payloads sibling workers had placed. The toy fixture gives those tests a run
store of their own now. Both were invisible until the census counted; both would have stayed so.
