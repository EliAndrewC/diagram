# Research: making the roll cache portable

The measurements that satisfied the GM's condition are in [`request.md`](request.md). This file is
what the investigation and the implementation turned up.

## R1 - the prize, measured in a throwaway clone at main's tip

| | cold | warm |
|---|---|---|
| `make reference` | 30 s | 1 s |
| the map-rolling gate tests (63) | 122 s | 21 s |

~2 minutes per clone, against the 21 s testmon bar the GM set. And the paired finding that made this
a feature rather than a `cp`: **a warm cache copied into a clone that had never rolled produced a
MISS** - confirmed by measurement and explained by the code.

## R2 - and the testmon database, which stays put

The GM asked directly whether the 21 s is "actually just what's per clone" or is re-paid "every third
run". Measured: touching the MOST depended-on engine module in the tree (`hamletgen/ways.py`, 79 of
2,394 recorded test executions) costs `make quick` **10 s** against **4 s** warm - not 25 s. testmon
re-runs only the tests that executed the changed code, so the cold cost is one-time construction.

The GM's conclusion follows and is implemented by doing nothing: the database is not synced and not
committed.

## R3 - the two mechanisms that made the cache unportable, one of them dangerous

1. **Recorded functions were keyed by absolute path.** `key_for` builds `funcs_wanted` from the
   dependency filenames and looks each up while walking `engine_files()` of the current tree. Across
   roots nothing matches, every per-function part drops silently out of the key, and the recomputed
   key cannot equal the stored one.
2. **Recorded data files were HASHED BY READING the absolute path.** This is the sharp one. In a
   copied cache that path points at the PRODUCING clone's file, which still exists on this machine.
   Today the absolute path is embedded in the key string, so the key differs and the entry misses -
   safe. But a naive fix that merely shortened the path strings would have started hashing the wrong
   tree's data while matching this tree's key. The implementation therefore carries the recorded form
   in the key STRING and reads the bytes from what that form resolves to HERE.

**A dependency outside the skill root stays absolute** - fonts, installed packages, the notes mount.
They have no meaningful root-relative form, they are the same files for every clone on this machine,
and sibling portability is the only portability this feature needs.

## R4 - the producer problem, which decided the shape of FR-003

Main has no `.gencache` and cannot acquire one: building it means running the tests, and main is
never a workspace - the one sanctioned write there is render-sync. So the GM's original framing
("the main checkout could refresh that cache") cannot be implemented as stated, and the seed comes
from a sibling clone at the same commit instead. Nothing is trusted: a seeded entry faces exactly the
same key check as one the clone built itself, so a seed from the wrong commit simply misses.

## R5 - the proof, end to end

In a clone that had never rolled, seeded from a sibling:

| step | seeded | cold | warm |
|---|---|---|---|
| the reference settlement | **HIT, 5 s** | 30 s | 1 s |
| the 63 map-rolling gate tests | **28 s** | 122 s | 21 s |
| after changing ONE engine function | **MISS, 29 s** | - | - |

A cold clone's ~152 s becomes ~33 s.

**The first attempt at this measurement reported 156 s - worse than cold - and was published before
it was checked.** The cause was this clone's own cache: bumping `FORMAT_VERSION` invalidated all 119
of its format-1 entries, only the reference roll had been rebuilt, and so the seed was junk that the
probe clone had to read, discard and re-roll through. The gate then rebuilt the cache in full (120
entries, all format 2) and the re-run gave the numbers above. Two lessons, and the second is the
uncomfortable one: a cache measurement is only valid against a cache in the format under test, and a
number should not reach the GM before the run that produced it has been sanity-checked.

## R6 - five fixtures that proved nothing, in one session

Every one reported success, or a clean failure, while testing something other than what it claimed.
They are listed together because the pattern is the finding:

1. **The first roll-cache probe copied the cache AFTER a roll**, into a directory that already
   existed, so `cp -r` nested it and the "HIT" was the probe clone's own entry. It measured nothing
   about portability, and it nearly went into a report as evidence that the cache WAS portable.
2. **A discard fixture asked the hook about the wrong repository** - a process inherits `PWD` from
   its parent's environment, not from the spawn's `cwd=`.
3. **A review-gate fixture passed the range as an environment variable** when the script takes it as
   `$1`, so the gate diffed nothing and all four cases "passed".
4. **A key-comparison check used `gencache.py` itself**, which is excluded from the engine set, so
   neither side of the comparison had a per-function part and two different inputs keyed identically.
5. **A cross-root test built its fake file list with the PATCHED `_rel`**, which returned absolute
   paths, and `Path(other) / <absolute>` discards the base - so the "other root" was the original
   tree.

The lesson is the project's own rule for guards, applied one level up: **prove the fixture can fail.**
A measurement that cannot fail is worth less than no measurement, because it reports success.

**Sources:** this session's probes and suites; `l7r/diagram/pipeline/gencache.py`.
