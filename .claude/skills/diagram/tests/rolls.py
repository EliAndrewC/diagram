"""THE ROSTER OF ROLLED HAMLETS - the required process around rolling one more (feature 213, GM 2026-09-07).

The GM, on finding the gate rolling 37 hamlets where the packing record of 2026-08-31 (`dev/loop.md`, "THE
PACKING QUESTION") had measured 11 distinct and a floor of 8-9: *"we definitely had this solved at one point,
and then the problem just came back on its own ... I'm sure there is some manner by which we could program
our unit tests to never allow the same hamlet to be rolled twice within the tests and also to have some
required process around adding another hamlet that gets rolled, when we have already identified what we
believe to be the number that need to be rolled in order to get to one hundred percent code coverage."*

This file is that process. Every spec the gate may ROLL is listed here with WHY - the unique coverage or the
emergent condition it carries (from the packing record and the census of specs/213). The gate's census
(`_census.py`, written at `driver.roll_scope`) is checked against it after every test phase
(`ci/rollverdict.py`): a rolled spec absent from this roster fails the gate and says to add it HERE with its
reason; a spec rolled twice fails the gate naming both tests; on a full run an entry nothing rolled fails as
stale. So adding a rolling test means adding its row, and the row must say what the roll uniquely carries -
if it carries nothing another row does not, the answer is to reuse that row's roll, not to add one.

A spec is identified by NAME and SEED - what the GM means by "a hamlet". The households and knobs are shown
so a reader can see what the roll is, and `tests/test_rolls.py` proves no two rows share a key.

THREE KINDS OF ENTRY BESIDES A ROLL, each a stated exception the verdict prints rather than a hole:

- `Duplicate`: a site that must roll a rostered spec a SECOND time by its nature - the fan-out test's
  pool-child path (the mechanism under test; its serial half is served from the shared roll), the immune
  test's perturbed second roll (the equality of the two IS the assertion), the real-map cache round trip
  (the shipped gen's FILES are what round-trip, and the gate's spec roll writes none).
- `PoolGen`: a shipped generator the pool sweep runs through `gate_obtain`'s coverage child - only when its
  cache key moved (an engine change), served from the gen cache otherwise. Three of the five are the same
  (name, seed) as a rostered gate roll, so on a cold run the reference is rolled twice: once as a spec, once
  as the generator that ships it. Priced and left (spec D7): unifying the two would have the sweep read the
  spec roll's manifest instead of running the gen, and the gen script is the unit the sweep exists to run.
- `InProcess`: a test module allowed to roll IN THE WORKER rather than in a child. The perf tests time the
  stages where they run (each on a seed of its own, rostered); a `stub=True` module runs STAND-IN stages
  and rolls no map - its records are reported and bounded (`rollverdict.STUB_MAX_S`), never counted.
"""

from __future__ import annotations

from dataclasses import dataclass

from l7r.diagram.hamletgen import HamletSpec
from l7r.diagram.hamletgen.driver import cohort_specs


@dataclass(frozen=True)
class Roll:
    spec: HamletSpec
    carries: str  # the unique coverage or emergent condition - the reason this roll exists
    rolled_by: str  # where the roll is requested from (the mechanism; the tests that read it need not be listed)

    @property
    def key(self) -> tuple[str, int]:
        return (self.spec.name, self.spec.seed)


@dataclass(frozen=True)
class Duplicate:
    key: tuple[str, int]
    test: str  # the requesting test's nodeid, or a prefix of it
    mechanism: str
    reason: str


@dataclass(frozen=True)
class InProcess:
    module: str  # a test module path relative to `tests/`, or a prefix of one
    reason: str
    stub: bool = False  # True: stand-in stages, no map - the verdict reports and bounds its rolls instead of counting them


POOL_TEST = "tests/full/test_villages.py::test_village_passes_gate"


@dataclass(frozen=True)
class PoolGen:
    key: tuple[str, int]
    gen: str  # the shipped generator, relative to the skill root
    note: str
    test: str = POOL_TEST  # the one site that may roll it, once, when its key moved


COHORT = cohort_specs(4, first_seed=41)

ROLLS: tuple[Roll, ...] = (
    # THE REFERENCE AND THE POOL
    Roll(
        HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond"),
        "the reference hamlet: 66 lines nothing else reaches (the packing record); the valley-paddy archetype, a pond sink, the placard's basis",
        "rollcache.hamlet / report - one shared child roll; also the pool sweep's coverage child (gate_obtain) and the cache round-trip",
    ),
    Roll(
        HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry"),
        "the dike-pond archetype with the mosaic layout and mulberry: 7 lines the dikepond spec does not reach; the only live map with laterals",
        "rollcache.hamlet - one shared child roll",
    ),
    Roll(
        HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0),
        "the polder grid at fall 0: 13 unique lines; the reservoir that must WALK back from the crop (an emergent condition - seeds 8, 19, 22 clear first try)",
        "rollcache.hamlet - one shared child roll",
    ),
    Roll(
        HamletSpec(name="Polder", seed=19, households=16, field_archetype="polder_grid", down_deg=90),
        "the polder grid at fall 90: the inner splice-refusal branch of the web (one line, recorded as the weak ratio, kept)",
        "rollcache.hamlet - one shared child roll",
    ),
    # THE GATE COHORT - the contiguous range GATE_COHORT_EXPECTED and the seed-43 expected failure pin (spec FR-005)
    Roll(
        COHORT[0],
        "cohort seed 41: the ratchet's range; the lane-rule tests read it; the fan-out test compares the pool-child path against it",
        "rollcache.report / hamlet - one shared child roll (plus the fan-out's pool child: a stated Duplicate)",
    ),
    Roll(
        COHORT[1], "cohort seed 42: the ratchet's range; a map generate() re-rolls (3 attempts - the cost FR-005 accepts and the census reports)", "rollcache.report / hamlet - one shared child roll"
    ),
    Roll(COHORT[2], "cohort seed 43: the ratchet's range; the strict expected failure (the kink round a house corner)", "rollcache.report / hamlet - one shared child roll"),
    Roll(COHORT[3], "cohort seed 44: the ratchet's range", "rollcache.report / hamlet - one shared child roll"),
    # THE EMERGENT CONDITIONS - each pins a seed because some condition must HOLD, not because a knob is set
    Roll(
        HamletSpec(name="CloudOnly", seed=7, households=10),
        "both row passes silenced: the cloud must seat the hamlet alone (185 lines shared only with LaneOnly/OneHouse, and a different assertion)",
        "rollcache.keyed_to, a child roll (test_homesteads)",
    ),
    Roll(
        HamletSpec(name="LaneOnly", seed=5, households=10, settlement_form="linear"),
        "the field row silenced on a linear hamlet: the frontage pass must seat it",
        "rollcache.keyed_to, a child roll (test_homesteads)",
    ),
    Roll(
        HamletSpec(name="OneHouse", seed=5, households=10, settlement_form="linear"),
        "households cut to 1 after planning: the frontage pass must STOP once housed (the spec name sets the placard width, so it is a different map from LaneOnly)",
        "rollcache.keyed_to, a child roll (test_homesteads)",
    ),
    Roll(
        HamletSpec(name="Clamped", seed=23, households=12, water_sink="pond"),
        "a pond set-back the canvas cannot give: the fallback to draining off-map (28 unique lines)",
        "rollcache.keyed_to, a child roll (test_sink)",
    ),
    Roll(
        HamletSpec(name="Woodland-shrink", seed=4, households=10, down_deg=90),
        "the woodland shrink ladder walked on a real site (23 unique lines)",
        "rollcache.keyed_to, a child roll (test_woodland_shrink_147)",
    ),
    Roll(
        HamletSpec(name="Retry", seed=4, households=10),
        "the re-roll loop: a stranded farmhouse forbids its ground on the second attempt (2 attempts by design)",
        "rollcache.keyed_to, a child roll (gate test_driver)",
    ),
    Roll(HamletSpec(name="NoHelp", seed=4, households=10), "the re-roll loop: a re-roll that helps nothing is not kept (3 attempts by design)", "rollcache.keyed_to, a child roll (gate test_driver)"),
    # THE FULL TREE
    Roll(
        HamletSpec(name="Kashikawa", seed=3, households=20, down_deg=315, water_sink="offmap"),
        "the immune test: one extra random draw at meta() must not move the map (the largest pool hamlet)",
        "a gen run in a child with the perturbation (full/test_villages)",
    ),
    Roll(
        HamletSpec(name="Clitest", seed=9, households=11, down_deg=90, water_sink="offmap", windward="N"),
        "the CLI end to end: a seed that finishes on the first attempt (seed 8 took two - FR-005)",
        "hg.main -> generate, a child roll (full/hamletgen/test_driver)",
    ),
    Roll(
        HamletSpec(name="Childroll", seed=3, households=10),
        "feature 210's proof that the child rolls the same hamlet the worker would: rolled once in-process and once in a child, by design",
        "rollcache._roll_payload in-process and _hamlet_in_child (full/pipeline/test_rollcache_child)",
    ),
    # THE PERF TESTS - they time the stages where they run, so each rolls IN PROCESS a seed of its own (spec FR-007)
    Roll(
        HamletSpec(name="Inashiro", seed=6, households=15, down_deg=90, water_sink="pond"),
        "perf_snapshot.measure timed stage by stage: its own seed, so it is not a second roll of the reference",
        "tools/perf_snapshot.measure in the worker (tests/tools/test_perf_snapshot)",
    ),
    Roll(
        HamletSpec(name="Inashiro", seed=7, households=15, down_deg=90, water_sink="pond"),
        "perf_profile.profile_stage on the FIRST stage: stops after water_frame (milliseconds) - its own seed because the later-stage test rolls seed 5 in the same worker",
        "tools/perf_profile.profile_stage in the worker (tests/tools/test_perf_profile, the first-stage test)",
    ),
    Roll(
        HamletSpec(name="Inashiro", seed=5, households=15, down_deg=90, water_sink="pond"),
        "perf_profile.profile_stage on a LATER stage (sink): the stages before it timed plainly, the target profiled; stops there",
        "tools/perf_profile.profile_stage in the worker (tests/tools/test_perf_profile, the later-stage test)",
    ),
)

DUPLICATES: tuple[Duplicate, ...] = (
    Duplicate(
        ("Cohort-41", 41),
        "tests/full/hamletgen/test_driver.py::test_the_fan_out_agrees_with_the_serial_path",
        "cohort pool child (jobs=2)",
        "the pool-child path IS the mechanism under test; the serial half is served from the shared roll",
    ),
    Duplicate(
        ("Childroll", 3),
        "tests/full/pipeline/test_rollcache_child.py::test_the_child_rolls_the_same_hamlet_as_the_worker_would",
        "in-process against the child",
        "the equality of the two paths is the assertion",
    ),
    Duplicate(
        ("Kashikawa", 3),
        "tests/full/test_villages.py::test_a_map_is_immune_to_an_upstream_change_in_the_number_of_random_draws",
        "a second gen child with one extra random draw per meta()",
        "the equality of the plain and the perturbed roll IS the assertion",
    ),
    Duplicate(
        ("Inashiro", 4),
        "tests/full/pipeline/test_gencache.py::test_the_real_pool_round_trips_through_the_cache",
        "the shipped gen in a child, then store / wipe / restore",
        "the gen's FILES are what round-trip through the cache, and the gate's spec roll writes none; the cheapest scripted hamlet, once per run",
    ),
)

POOL_GENS: tuple[PoolGen, ...] = (
    PoolGen(
        ("Inashiro", 4),
        "pool/hamlets/inashiro/inashiro.gen.py",
        "the pool's brief adds fixtures_min={'shrine': 1}, which the gate's SPEC literals do not carry: the same (name, seed), a brief that differs by one forced fixture - recorded, the GM's to rule on (specs/213 R4)",
    ),
    PoolGen(("Kuwabata", 21), "pool/hamlets/kuwabata/kuwabata.gen.py", "the same brief as the gate's Kuwabata roll"),
    PoolGen(("Kashikawa", 3), "pool/hamlets/kashikawa/kashikawa.gen.py", "the same brief as the immune test's roll"),
    PoolGen(("Sawada", 6), "pool/hamlets/sawada/sawada.gen.py", "a pool-only hamlet: 19 households, fall 225, off-map sink"),
    PoolGen(("Mizuguchi", 23), "pool/hamlets/mizuguchi/mizuguchi.gen.py", "a pool-only hamlet: 12 households, fall 0, a pond"),
)

IN_PROCESS: tuple[InProcess, ...] = (
    InProcess("tests/tools/test_perf_snapshot.py", "times the stages where it runs"),
    InProcess("tests/tools/test_perf_profile.py", "profiles a stage where it runs"),
    InProcess("tests/tools/test_placement_stages.py", "stand-in stages; rolls no map (milliseconds)", stub=True),
    InProcess("tests/hamletgen/test_driver.py", "stand-in stages: the stage-profile and roll-scope tests roll no map (milliseconds)", stub=True),
    InProcess("tests/full/pipeline/test_rollcache_child.py", "the in-process half of the child-equality proof"),
)


def by_key() -> dict[tuple[str, int], Roll]:
    return {r.key: r for r in ROLLS}
