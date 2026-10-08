# What a test costs, and the levers that do and do not move it

**Load this file when:** you are making the gate or a test cheaper, deciding whether a test may roll a map, reading a
timing off this box, or a target got slower and you are about to say why.

Split out of [`loop.md`](loop.md); the dated measurements behind each rule are in the specs named, and the gate's
live costs are `make audit` and `scripts/_gatecost.py <target>`, never a figure typed here.

## Reading a timing on this box

**The cores are not the same speed** (measured 2026-08-31). The GM ruled out the obvious answer first: *"I thought
that our parallelization was actually letting us use different CPUs ... xdist dispatches to workers, which are
actually different processes so that the global interpreter lock isn't an issue."* Right - the GIL is not involved.
The host (an Intel Core Ultra 7 155H, 22 logical CPUs) has P-cores (cpu0-11), E-cores (cpu12-19) and LP-E cores
(cpu20-21), and the same roll pinned with `taskset` took 15.7 s on a P-core and 32.1 s on an LP-E core - more than
the clock ratio, so IPC differs too. A batch's wall time is set by its SLOWEST worker. So:

1. **A test that "got slower" may simply have landed on a slower core.** Re-run it before believing a regression,
   and prefer a pinned or repeated measurement over a single reading.
2. **Adding workers has diminishing and then NEGATIVE returns here**: the marginal worker goes to a slower core
   while the fast ones gain a hyperthread sibling.
3. **It says nothing about CodeBuild**, whose vCPUs are homogeneous; do not carry a parallel-scaling conclusion from
   this laptop to the build.

**The method, when a timing matters: idle box, `taskset` to pin, and say which core class you pinned to.** An
unpinned single reading on this hardware carries a 2x uncertainty band.

**Suite-level timings cannot be read from single runs**: the run-to-run spread (several sessions gate at once) is
wider than most savings. Measure the FILE (`make test-file`, or the per-file CPU in `make durations N=3000`), where
the numbers are clean, and take a median of at least three runs before claiming anything about the suite. And
before bisecting seeds for a slow run, ask `make durations` - it names the slow test in one run.

## What moves the wall and what does not

- **On N workers, a CPU reduction moves the wall only if it shortens the longest item.** A slow-test list is worth
  far less than its headline suggests.
- **Collection is xdist process orchestration, not imports** (feature 135's directory split already took module
  import to ~12% of startup). Don't split `tests/` again for startup.
- **The worker count is a courtesy to the other sessions, not a tuning knob.** A few more workers measured a
  fraction of a second faster, inside the noise, by taking cores from peers (GM 2026-08-26: *"the laptop runs
  several sessions at once"*). `XDIST_WORKERS` in the Makefile is the one definition.
- **Map rolls do not parallelize on this box** (measured 2026-08-31): a roll is single-threaded, and
  rolls run side by side slow each other by memory bandwidth and page cache, not CPU. `-n 1` beat `-n 8` on the
  heaviest file. Scheduling work, `--dist` tuning and more workers are worthless for a roll-bound phase; only fewer
  or cheaper rolls help.
- **One expensive construction repeated is the usual shape of a slow test file.** Build the subject once and hand
  out a deepcopy (a `build_comb` costs ~270x its deepcopy) - and always a deepcopy when a downstream step mutates
  the subject (`draw_comb_field` rewrites the net it is given), or one test's draw changes what the next builds on,
  as an ordering-dependent failure.
- **A per-process cache shares almost nothing under `--dist worksteal`.** `functools.lru_cache` and a module-level
  dict help only when two tests reading the same subject land on the SAME worker, which they usually do not; both
  attempts CUT CPU AND RAISED WALL. Only a disk-backed cache keyed on the engine (`pipeline/rollcache.py`) shares
  across workers.
- **The roll cache is bypassed where the coverage floors are judged** (`L7R_TESTS_FULL`, `rollcache.FULL_ENV`): a
  served roll executes none of the code. Any "optimization" that restores serving there buys its speed by not
  running the code the floors exist to check.

## The gate rolls only what 100% coverage strictly needs

The doctrine (feature 216, constitution VI; GM: *"Not only should we do that here, we should always do that for the
make done tests"*): a test that rolls more belongs in the tier above the gate (`tests/soak/`, `make soak`), which no
ordinary run collects. Since features 216-219 the gate rolls no map of its own: its coverage is the shipped
generators (rolled cold when their key moved, served warm with their coverage replayed) and unit tests.

**The count is a gate, not a memory, because it drifted.** A week after a packing pass measured a floor of 8-9 rolls,
a census found 37 (feature 213). The GM: *"we definitely had this solved at one point, and then the problem just came
back on its own. So that is usually a sign that something about our testing procedures is bad."* So
[`tests/rolls.py`](../tests/rolls.py) is the roster - one row per spec with what it uniquely carries - and the gate's
census at `driver.roll_scope`, judged by `ci/rollverdict.py`, fails a second roll of a spec, an unrostered roll, a
stale row, or a rostered roll that reaches no line of its own. `make roll-audit` answers, per roll, the engine lines
nothing else reaches.

**A roll that exists for what a TEST does, rather than for lines nothing else reaches, is a roll to question**
(feature 214; GM: *"is it ACTUALLY the case ... and not just some assertions we could add onto the existing tests
where that same hamlet was already rolled elsewhere?!"*). The assertions almost always fit on a roll already made.

### Asking whether two rolls can be one

The GM's question is not subsumption (is X's coverage inside the union of the others) but PACKING: *"do there exist
two or more hamlets ... which could be combined into a single hamlet while exercising all of the branches that all
of the tests need."* Subsumption cannot see a merge, because two hamlets can each carry unique lines and still be
mergeable. The method:

- **Record what each roll's tests REQUIRE**, not what its spec happens to set, split in two: DECLARED knobs
  (archetype, form, households - one value per dimension, so requirements from different dimensions pack for free)
  and EMERGENT conditions ("the reservoir must have to walk" - these pin a seed, and two share a hamlet only if some
  seed satisfies both).
- **Test a candidate merge by rolling it and running every assertion set against every map.** Do not reason about
  it; the probe is twenty lines.
- **An assertion matrix is necessary and not sufficient: read WHY the seed was chosen.** A seed picked to force a
  path (a reservoir that must walk) is load-bearing however green the matrix looks - another seed passes its
  assertion without ever exercising the mechanism, and a rule that never runs looks exactly like a rule that passes.
- **Measure the merge, do not model it.** Three coverage predictions in the 2026-08-31 packing pass were all
  overturned by one FULL run each, in both directions: "unique among the maps" is not "covered only by this map",
  because another TEST may reach the line.
- **A roll that reaches a guard but never the branch beneath it is paying map prices for unit-test work.** Cover the
  branch with a unit test on a module-level function instead.
- **Line coverage is weaker than branch coverage**: a zero is a candidate, never a verdict; read the test before
  touching it. And `set(a) | set(b) - rest` is `a | (b - rest)` - the wrong one reads plausible.

## Levers measured and withdrawn - do not re-try

- **Shrinking a test's `plan.envelope` to shrink its fan**: the canvas clamps a saturated fan, not the envelope; the
  plot count (`plot_across`, `row_step`) is the lever (feature 158; `lessons.md`).
- **`COVERAGE_CORE=sysmon`**: slower here than the C tracer (feature 158; `lessons.md`).
- **Pinning the suite to the P-cores**: slower, because the workers then share hyperthreads (feature 191, `specs/191-refusals-that-tell-the-truth/research.md`).
- **Raising the worker count or tuning `--dist` for the roll phase**: see above (2026-08-31).
