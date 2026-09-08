# Research - 215 the floor itself

## R1. The audit: what each of the sixteen rolls reaches that nothing else does

Method: the last green gate's coverage baseline (`.git/gate-baseline/coverage.db`, feature 214's landing)
carries one coverage context per fixture and per test phase, and since feature 213 a roll child's lines land
under its requester's context. For every rolling context, the engine lines executed under NO other context
of the whole suite (unit tests included) were counted - "if this roll went, which lines would lose all
coverage". Script: `census/unique_lines.py`.

| roll (warm gate) | lines only it reaches | where |
|---|---|---|
| Inashiro 4, the gate's shared roll | **0** | the pool sweep's `inashiro.gen.py` child covers every one |
| Kuwabata 21, the gate's shared roll | **0** | the pool sweep's `kuwabata.gen.py` child |
| Polder 12 | 1 (the two polders together: 3) | `hamletgen/water.py` 414 |
| Polder 19 | 0 alone | |
| CloudOnly 7 | 0 (the three seatings together: 10) | |
| LaneOnly 5 | 4 | `ways/route.py` 174-176, `ways/touch.py` 465 |
| OneHouse 5 | 5 | `hinterland/stages.py` 83, `homesteads/wells.py` 311-314, `ways/web.py` 221 |
| Clamped 23 | 3 | `hamletgen/sink.py` 285-287 |
| Woodland-shrink 4 | **0** | the ladder's lines are covered by the settlement unit tests |
| Retry 4 | 1 | `driver.py` 366 (the re-roll loop) |
| NoHelp 4 | 3 | `driver.py` 368, 369, 377 |
| Cohort-43 | 8 | `ways/touch.py` 43, 365-368, 447, 463; `waterfields/carve.py` 558 |
| Kashikawa 3, the immune test's perturbed roll | 1 | `pipeline/gencache.py` 332 (the perturbation itself) |
| the fan-out's pool child (Inashiro) | 0 | |
| the child-equality proof's in-process roll (Inashiro) | 0 | |
| the cache round trip's gen (Inashiro) | 0 | |
| the pool sweep, cold only: Sawada 7, Mizuguchi 1, Inashiro 0, Kuwabata 0, Kashikawa 0 | | `ways/route.py`, `shrines_wells/byres.py`, `water_ways/lanes.py`; `ways/sweeps.py` 189 |

So by COVERAGE alone the floor is the pool sweep: every other roll's unique lines together are about thirty,
each of them a direct unit test away. What the rolls carry beyond coverage is a BEHAVIOR asserted on a map:
the gate's fifteen modules assert on the reference, the polder tests on the polders, the emergent-condition
tests on the condition their patch creates. Those assertions need a map; they do not need a roll of their own
where a map that already exists carries the same content.

**What the GM's two questions get.**

*The three duplicates* - none needs a roll:
- the fan-out's pool child proves `ProcessPoolExecutor.map(generate, specs)` returns the serial result; the
  pool MECHANICS (the branch, the ordering, the pickling) hold on a stub producer run through the same pool,
  and the "a map is a pure function of its spec" half is the immune test's claim, asserted there;
- the child-equality proof compared a child roll with an in-process roll to show the child's environment
  does not change the map; since every roll is a child now and the shipped maps are made by children too,
  the property that matters is child == child, which the immune test asserts (perturbed child against the
  sweep's child). Retired, with the toy-level child tests kept where they live;
- the cache round trip regenerates the reference to store, wipe and restore it; the sweep has already
  produced (or served) the same map, so the round trip runs on that entry's artifacts and its recorded
  dependencies: store into a scratch cache, wipe, load, bytes match, no roll.

*The specs* - two of the thirteen are the POOL's maps rolled a second time under a spec of their own:
the gate's Inashiro and Kuwabata. The pool sweep already rolls both (cold) or serves both (warm) with a
coverage child of their own, and their manifests are on disk. The gate's tests can read those. That needs
the reference's brief aligned with the pool's (`fixtures_min={'shrine': 1}` - the GM: *"I don't care
whether the Inashiro reference has a different fixture from the brief, so that's fine"*) and the ratchet's
verdict carried in the manifest's meta rather than only in the in-memory Report. Kashikawa exists only as
the immune subject, and its perturbed roll can be a perturbed roll of the reference against the pool's
committed manifest. Retry and NoHelp exercise the re-roll loop's control flow, which holds on stand-in
stages exactly as the stage-profile tests do - the loop's four lines are theirs and nothing about a real
map is asserted by them beyond the loop's decisions. Seed 43's eight lines are unit tests; its kink is the
one thing that may still need the seed, and only a synthetic reproduction settles that.

**The count after, warm:** Polder 12, Polder 19, CloudOnly, LaneOnly, OneHouse, Clamped, Woodland-shrink,
the perturbed reference, and seed 43 unless its kink reproduces synthetically: **9 rolls of 9 specs** (8 of
8 if it does) - the packing record's floor. Cold adds the five pool gens, which are the shipped maps. The
further cuts the audit shows and this feature does NOT take, each a behavior traded for a unit test and
therefore the GM's call: Woodland-shrink (0 unique lines: the ladder is unit-covered, the roll adds "on a
real site"), Clamped (3 lines), Polder 19 (0 alone; the fall-90 form and the keep-out assertion), and the
three seatings sharing one partial roll (the stages run once to the seating pass, the state copied, three
patched seatings) - together another 4 rolls, to 4-5.

## R2. Measured after

(The census line and the gate's time, at the end.)
