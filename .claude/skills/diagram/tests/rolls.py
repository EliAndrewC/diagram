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
- `InProcess`: a test module allowed to roll IN THE WORKER rather than in a child - the in-process half of the
  child-equality proof; a `stub=True` module runs STAND-IN stages and rolls no map (the stage tests, and since
  feature 214 the perf tests) - its records are reported and bounded (`rollverdict.STUB_MAX_S`), never counted.

THE NUMBER (feature 216, GM 2026-09-08: *"the make done tests are trying to minimize the number of map rolls and are
doing only what is strictly necessary in order to reach one hundred percent code coverage"*): TWO rows since feature
217, two rolls on a warm gate, no duplicates, every row carrying engine lines nothing else reaches.
A test that rolls more than that belongs in `tests/soak/`, the tier above the gate, which no ordinary run collects.

A ROLL EARNS ITS LINES, AND THE GATE MEASURES IT (feature 217, GM 2026-09-08 - GUARD_EDIT_OK: feature 217, the roster
is a guard file now and this paragraph is the process it guards: *"if a new map roll is added, then that causes a test
failure or something Unless we prove in some way that we have consulted the project guidelines and made a justification,
done an audit"*). The census verdict computes, for every rostered roll, the engine lines its coverage context reaches
that NO other context of the run reaches, prints the count and the lines on every gate, and FAILS a `Roll` or
`Duplicate` whose set is empty - zero means the roll can be removed with 100% kept, so under constitution VI it must
be. So before adding a row: run `make roll-audit` (the same arithmetic off the last baseline); if the lines it would
earn are few, write them as unit tests of the placer instead; if the test asserts behavior rather than lines, it belongs
in `tests/soak/`; and if a roll is still needed, record the audit in the feature's research.md and point the row's
`audit=` at that section - `tests/test_rolls.py` checks it exists and carries the audit's output. This file is a GUARD
(`scripts/guard-file-hooks.sh`, both routes): an edit needs GUARD_EDIT_OK with a reason in the diff, and a change here
makes the next gate a FULL run so the new row is judged against every context of the suite. A `PoolGen` row is the one
kind the verdict prints and never fails: a shipped map is the GM's exhibit decision, rolled cold only.
Feature 215 had reached the packing record's nine; 216 traded the rest for unit tests and one shared partial roll. The reference and Kuwabata are read from the POOL's
maps (the sweep rolls them cold, serves them warm; `tests/gate/_pool.py`), so the reference's one roll is the
immune experiment's perturbed one; the re-roll loop runs on stand-in stages; the fan-out's pool child runs a
stub producer; the child-equality proof is retired; the cache round trip runs on the sweep's entry. Seed 43 stays
for its kink, which did not reproduce synthetically (specs/215 research R2). The audit that found all of this -
the engine lines each roll alone reaches, off the gate's own coverage baseline - is `specs/215-the-floor-itself/
census/unique_lines.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

from l7r.diagram.hamletgen import HamletSpec


# GUARD_EDIT_OK: feature 217 - a row POINTS AT THE AUDIT that justified it (GM 2026-09-08: a roll is added only after
# "we prove in some way that we have consulted the project guidelines and made a justification, done an audit"). The
# reason string is still here for the reader; the `audit` is the research section that RECORDS the `make roll-audit`
# run, and `tests/test_rolls.py` proves it exists and carries the audit's output. The census verdict then judges what
# the row claims: a rostered roll that reaches no engine line no other context reaches FAILS the gate.
@dataclass(frozen=True)
class Roll:
    spec: HamletSpec
    carries: str  # the unique coverage or emergent condition - the reason this roll exists
    rolled_by: str  # where the roll is requested from (the mechanism; the tests that read it need not be listed)
    audit: str = ""  # specs/NNN-<slug>/research.md#R<k> - the section recording the audit that justified this row (feature 217)

    @property
    def key(self) -> tuple[str, int]:
        return (self.spec.name, self.spec.seed)


@dataclass(frozen=True)
class Duplicate:
    key: tuple[str, int]
    test: str  # the requesting test's nodeid, or a prefix of it
    mechanism: str
    reason: str
    audit: str = ""  # as on a Roll: a second roll is judged on its own context and owes the same pointer (feature 217)


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


# THE COVERAGE ROLLS, shared by name (feature 214): the plain `roll:<spec>` subjects every reader can share - the
# ratchet, the lane rules, the fan-out, the child-equality proof and the hamlet floor all read these.
REFERENCE = HamletSpec(name="Inashiro", seed=4, households=15, down_deg=90, water_sink="pond", fixtures_min={"shrine": 1})  # THE POOL'S BRIEF (feature 215 D1)
KUWABATA = HamletSpec(name="Kuwabata", seed=21, households=16, down_deg=90, field_archetype="mulberry_dike_fishpond", pond_layout="mosaic", dike_crop="mulberry")
POLDER_FALL_0 = HamletSpec(name="Polder", seed=12, households=16, field_archetype="polder_grid", down_deg=0)
COVERAGE: tuple[HamletSpec, ...] = (REFERENCE, KUWABATA, POLDER_FALL_0)  # Polder 19 left at feature 216: no line of its own (215 R1)
# THE SEATINGS' PARTIAL ROLL left the gate in feature 217 (GUARD_EDIT_OK: feature 217 - its one unique line is a unit test,
# tests/hamletgen/homesteads/test_seats.py, and the three seating behavior tests roll it in tests/soak/test_seatings.py).

ROLLS: tuple[Roll, ...] = (
    # THE REFERENCE AND THE POOL
    # THE REFERENCE IS THE POOL'S MAP (feature 215): every gate reader takes it from the sweep's entry (`tests/gate/_pool.py`),
    # so the gate's only roll of it is the immune experiment's PERTURBED roll - one extra draw at every meta() against the
    # committed manifest. Kuwabata is read the same way and has no roll row at all: it is a `PoolGen` below.
    Roll(
        REFERENCE,
        "the immune experiment (GM 2026-08-08): one extra random draw at meta() must not move the map - the perturbed roll cannot be served and is compared with the pool's committed manifest; the gate's fifteen readers of the reference read that manifest",
        "rollcache._perturbed_manifest in a child (full/test_villages); the clean side is pool/hamlets/inashiro/inashiro.json through gate_obtain",
        audit="specs/216-the-floor-as-doctrine/research.md#R2",  # GUARD_EDIT_OK: feature 217 - 17 lines only this roll reaches, all the perturbation machinery
    ),
    Roll(
        POLDER_FALL_0,
        "the polder grid at fall 0: 13 unique lines; the reservoir that must WALK back from the crop (an emergent condition - seeds 8, 19, 22 clear first try)",
        "rollcache.hamlet - one shared child roll",
        audit="specs/216-the-floor-as-doctrine/research.md#R2",  # GUARD_EDIT_OK: feature 217 - 21 lines only the polder fixture reaches (comb fields, water.py)
    ),
    # (GUARD_EDIT_OK: feature 217 - the seatings' row left: its one unique line, the connector skip in `lane_frontage`, is
    #  tests/hamletgen/homesteads/test_seats.py, and the three behavior tests roll their partial state in tests/soak/.)
)

DUPLICATES: tuple[Duplicate, ...] = ()  # none since feature 215: the fan-out's pool child runs a stub producer, the child-equality proof is retired, the cache round trip runs on the sweep's entry

POOL_GENS: tuple[PoolGen, ...] = (
    PoolGen(("Inashiro", 4), "pool/hamlets/inashiro/inashiro.gen.py", "THE REFERENCE: the gate's fifteen readers take this map (feature 215); the brief is the tests' REFERENCE exactly"),
    PoolGen(("Kuwabata", 21), "pool/hamlets/kuwabata/kuwabata.gen.py", "the dike-pond archetype: the gate's readers take this map (feature 215); the brief is the tests' KUWABATA exactly"),
    PoolGen(("Kashikawa", 3), "pool/hamlets/kashikawa/kashikawa.gen.py", "the largest hamlet; the immune experiment moved off it onto the reference (feature 215 D5)"),
    PoolGen(("Sawada", 6), "pool/hamlets/sawada/sawada.gen.py", "a pool-only hamlet: 19 households, fall 225, off-map sink"),
    PoolGen(("Mizuguchi", 23), "pool/hamlets/mizuguchi/mizuguchi.gen.py", "a pool-only hamlet: 12 households, fall 0, a pond"),
)

IN_PROCESS: tuple[InProcess, ...] = (
    InProcess("tests/tools/test_perf_snapshot.py", "stand-in stages under a deterministic clock: the tool's behavior, not a map's time (feature 214)", stub=True),
    InProcess("tests/tools/test_perf_profile.py", "stand-in stages under a deterministic clock: the tool's behavior, not a map's time (feature 214)", stub=True),
    InProcess("tests/tools/test_placement_stages.py", "stand-in stages; rolls no map (milliseconds)", stub=True),
    InProcess("tests/hamletgen/test_driver.py", "stand-in stages: the stage-profile and roll-scope tests roll no map (milliseconds)", stub=True),
    InProcess("tests/gate/hamletgen/test_driver.py", "stand-in stages: the re-roll loop's decisions (feature 215) roll no map; the ratchet reads the pool's maps", stub=True),
)


def by_key() -> dict[tuple[str, int], Roll]:
    return {r.key: r for r in ROLLS}
