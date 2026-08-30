# Feature Specification: A Roll Cache a New Clone Can Use

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=167-portable-roll-cache`)

**Created**: 2026-08-30

**Status**: Draft - awaiting `spec-fidelity`

**Input**: [`request.md`](request.md), verbatim and unedited. That file is the authority for this
specification, and it records the two conditions the ruling sets and the measurements that answer
them.

## The feature, in one sentence

A fresh clone pays about two minutes re-rolling maps that another clone on the same machine has
already rolled from identical source, and it pays that because the roll cache records its
dependencies as ABSOLUTE paths - so this makes those records root-relative, which is the one change
that turns a copied cache from worthless into usable, and then seeds a new clone from a sibling that
already has one.

## Why this exists (the GM's words - `request.md` is the authority)

- *"if it looks like there are real savings above and beyond twenty one seconds once per clone, then
  please proceed with implementing it"*

Both conditions in that sentence were answered by measurement before this spec was written; the
numbers are in `request.md` and repeated below.

## What was measured

| | cold | warm | delta |
|---|---|---|---|
| `make reference` in a clone that has never rolled | **30 s** | 1 s | 29 s |
| the map-rolling gate tests (`-m rolls_map`, 63 tests) | **122 s** | 21 s | **101 s** |
| **a fresh clone, total** | | | **~2 min** |
| (`make quick`, the testmon database, for comparison) | 25 s | 4 s | 21 s |

And the finding that makes this a feature rather than a copy command: **a warm `.gencache` copied
into a clone that has never rolled produces a MISS.** Measured directly, and explained by the code -
`gencache.key_for` looks up each recorded function by its dependency FILENAME, which is stored
absolute, while it walks `engine_files()` of the CURRENT tree. The two never match across roots, so
every per-function part silently drops out of the key and the recomputed key cannot equal the stored
one. Re-keying a real entry with the paths rewritten to another clone's prefix gives a different key,
which is the same fact from the other side.

**That failure is in the safe direction and must stay that way**: a mismatched key MISSES and
re-rolls. It never serves a payload keyed to another tree's source. Nothing in this feature may
change that property.

## Scope, stated exactly

**IN scope**: how `l7r/diagram/pipeline/gencache.py` records and re-reads a dependency's path, the
matching read in `rollcache.py`, and a seeding step that gives a new clone a usable cache.

**OUT of scope**: what the key HASHES (every engine file's module hash, every recorded function's
source, the interpreter, the renderer, the dependency state and the format version all stay exactly
as they are); the testmon database, which the GM ruled stays per-clone; the pool render cache; any
change to when a roll is produced rather than served.

## Requirements

### FR-001 - a dependency record is root-relative

`gencache` records and re-reads every dependency path relative to the skill root, and resolves it
against the current root when computing a key. A cache produced in one checkout therefore yields the
SAME key in another checkout of identical source, and a DIFFERENT key the moment any recorded source
differs - which is what it already does within one checkout.

The format version is bumped, so every entry written by the old absolute-path format is ignored
rather than misread. Existing caches are not migrated: they simply miss once and are reproduced.

### FR-002 - the safe-direction property is preserved and PROVED

A key mismatch must continue to mean MISS-and-re-roll, never a served payload. The feature carries a
test that a cache produced from one source tree and read against a DIFFERENT source tree misses -
not merely that identical trees hit. A cache that hits when it should not is the only failure here
that could let the gate pass on code it did not test, and it is the reason this spec exists in
preference to a `cp` in a shell script.

### FR-003 - a new clone is seeded from a sibling that has one

Clone creation seeds `.gencache` from another clone on this machine whose HEAD is the same commit,
when one exists. If none exists the clone starts cold exactly as today - the seeding is an
optimization and never a precondition.

**Why a sibling and not main**: main has no `.gencache` at all (checked), and cannot acquire one -
building it means running the tests, and main is never a workspace. The one sanctioned write into
main's tree is render-sync. So the producer has to be a clone, and every clone already is one.

### FR-004 - the seeding cannot make a clone wrong

A seeded cache is subject to exactly the same key check as one the clone built itself: every entry is
validated against the current tree's sources on use. Seeding therefore cannot change any verdict, only
how long it takes to reach it. A seed from a sibling at a DIFFERENT commit is simply not taken.

## Success Criteria

- **SC-001**: a `.gencache` copied from another clone into a clone that has never rolled produces a HIT for the reference settlement, and `make reference` costs ~1 s instead of 30 s.
- **SC-002**: the same copy, into a clone whose engine source differs by one function, produces a MISS for the rolls that executed that function.
- **SC-003**: a cache written by the previous (absolute-path) format is ignored rather than misread.
- **SC-004**: a new clone with no sibling at its commit starts cold and behaves exactly as today.
- **SC-005**: `make done` is green, and the map-rolling gate tests give the same verdicts as before this change - the cache decides only whether a roll is produced or served, never what it contains.

## Decisions Recorded

| decision | class | where |
|---|---|---|
| make dependency records root-relative | measured (a copied cache misses; ~2 min per clone at stake) | FR-001 |
| the mismatch direction stays MISS, and is proved by a test | the only failure that could let the gate pass on untested code | FR-002 |
| seed from a sibling clone, not from main | main has no cache and may never build one - it is never a workspace | FR-003 |
| the testmon database is NOT synced or committed | the GM's own conclusion, on the measurement that it is 21 s once per clone | `request.md` |
