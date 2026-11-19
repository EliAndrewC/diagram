# The generation cache - what it covers, what it cannot see, and its traps

**Load this file when:** The cache is behaving oddly, you changed how generation is driven, a coverage floor breached for no reason you can see, or you are about to test whether an edit invalidates an entry.

The short always-on version of each rule is in the engine index, [`l7r/diagram/CLAUDE.md`](../l7r/diagram/CLAUDE.md).

## What the key covers, and why the gate is allowed to trust it

The key covers the gen's bytes, the MODULE-LEVEL source of every engine module, the source of
every function that map actually EXECUTED, every non-source file the run opened, and the
interpreter/renderer versions - so an edit to any of the ~200 `settlement/` engine functions Minami
never runs leaves Minami cached, while an edit to one it does run, or to any module-level constant,
does not. `pipeline/gencache.py`'s docstring carries the soundness argument; `tests/pipeline/test_gencache.py` is the
demonstration, and every test there that asserts a HIT also regenerates and compares bytes, because
"the key did not move" proves nothing on its own.

**The gate RIDES the cache since 2026-08-16 (feature 026, GM decision reversing the 2026-08-08
"gate never reads the cache" rule).** The gate obtains each live map through `tests/gate/_pool.py`
(`obtain_full`, over `gencache.gate_obtain`): a verified HIT - key match plus stored generation coverage - restores the
artifacts, replays the entry's coverage data into the run (so the coverage floors stay honest),
and skips GENERATION only. Every test that reads the map still runs against whatever manifest was
served - checking is never cached. Any doubt at all - key moved, entry incomplete, no stored
coverage (an iteration-made entry), or `GATE_NO_CACHE=1` - regenerates in a coverage-recording
subprocess exactly as a cold run would. Why this is safe to trust, one line each: generation is
deterministic, so a sound key implies byte-identical output; the key covers the dependency surface
BELOW the Python-source horizon (`_deps_state`: installed distributions + renderer font bytes -
the PIL layout-engine incident class); and `tools/cache_audit.py` remains the standing empirical auditor
of the whole property. **After a dependency-level change** (a pip install/upgrade, a container
rebuild outside the lockfiles), run one bypassed sweep - `GATE_NO_CACHE=1 make done` - as
belt-and-suspenders for any channel the key cannot see.

**A DELETED MODULE STALES THE COVERAGE HALF OF EVERY ENTRY - handled automatically since 2026-08-17,
recorded because the SHAPE recurs.** A hit replays the entry's coverage into the gate's combine, and
coverage data is keyed by FILE PATH - so when a peer session's package split deletes
`settlement/civic_grounds.py` (one of six such splits in a fortnight) and you sync it in, every
entry built before that sync replays coverage measuring a file that is gone. `coverage report` dies
with `No source for code`, which the Makefile surfaces as **a coverage floor breaching**: a routine refactor in someone else's module, appearing in a clone that merely synced, as a
coverage regression in code this session never opened. It cost a full diagnosis once, including one
wrong guess (deleting `.coverage` does nothing - the data comes from the cache, not the last run).

`gate_obtain` now verifies that a stored coverage file still measures files that EXIST, and treats
anything else as a miss, so this resolves itself as a silent `REGENERATED`. No `GATE_NO_CACHE=1`
needed. Guard: `test_a_hit_is_refused_when_its_stored_coverage_names_a_file_that_is_gone`.

**The transferable half**: the key is right not to move here - generation is unaffected and the map
is correct - so a cache entry has TWO independently-perishable halves, and the artifact half staying
valid says nothing about the coverage half. When you add anything else to an entry, ask what makes
THAT part stale, because the key answers only for the bytes it was designed to protect. The contract's pinning tests are in
`tests/pipeline/test_gencache.py`; the decision's full reasoning in `specs/026-cache-backed-gate/`.

**No audit runs on the cache now.** `make cache-audit` - it perturbed an executed numeric literal in the engine, swept the
pool with the cache and again with `--no-cache`, and demanded identical artifacts, the empirical backstop for a key the gate
trusts - was deleted with the Python hamlet engine it mutated (feature 444 T39, ea5638968), and nothing has replaced it: a
change to the cache or to how generation is driven has no backstop but its own tests until feature 449 T221 rebuilds the
generation cache in Rust. The audit's design and the 2026-08-17 lesson on its
site selection (mutate only what the audited gens RUN; a mutation that moves no artifact is not a trial) are in git history,
at `ea5638968^:dev/cache.md`.

**Concurrency and container rebuilds are covered, and asserted rather than assumed.** A
`.gencache` lives beside the engine, so it is per-CLONE: concurrent writers are two runs in one
working tree, which necessarily generate from the same sources and (generation being deterministic)
produce identical bytes. `store` writes every file via temp-then-`os.replace` and publishes
meta.json LAST, so a concurrent reader sees a complete entry or none. The interpreter and resvg
versions are in the key, because a container rebuild changes what a map comes out as - the PIL
layout-engine incident rewrote 16 manifests with no code change behind it.

**THE TRAP, which cost three wrong conclusions in one session.** A miss REBUILDS the entry against
whatever the sources say at that moment. So if you edit a file, regenerate (correctly a miss), then
`git checkout` the edit away, the next run is a *legitimate* miss - the stored entry was built
against code that no longer exists. Testing "does an edit to X invalidate?" therefore needs the
baseline re-established (run until you see `CACHED`) before each trial, or the previous trial's
cleanup produces the miss and you conclude the cache is broken when it is working perfectly.
