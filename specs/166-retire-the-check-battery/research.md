# Research: the baseline, and what the migration is measured against

## R1 - the constitution XIII baseline and the opening perf bookend (T01)

Taken 2026-08-30 on UNMODIFIED code in a detached worktree (`git worktree add --detach /tmp/base166 HEAD`
at `11692b03`), never a stash:

    /tmp/base166/.claude/skills/diagram $ make done
    2786 passed, 2 skipped in 160.07s   -> green

    $ make perf LABEL=166-start
    total 121.3s  median 26.8s  worst 46.8s   (seeds 4, 25, 39, 47)

Zero pre-existing failures, so there is no ledger to carry and every failure after this point is this
feature's.

**Both numbers are higher than feature 163's baseline the same day** (2753 tests, 95.5 s total perf), and
the reason is that main moved: peer sessions landed features 164 and 165 in between. The bookend pair is
still valid because both halves are taken against THIS base, which is what `perf_snapshot` compares on -
but it is worth recording, because a reader comparing 163's numbers to 166's across the session would
otherwise read a 27% perf increase that this feature did not cause and that nothing regressed.

**Sources:** none - a measurement of this repository.

## R2 - the accept-criterion change did not move a map (T05)

`make maps` after T03, with every hamlet genuinely REGENERATED rather than served from cache
(inashiro 30.5 s, kashikawa 45.3 s, kuwabata 40.2 s, mizuguchi 20.6 s, sawada 50.6 s; exit 0), then
`git status` over `pool/`:

    (empty)

**All five live hamlets are byte-identical after the ladder's accept criterion changed from the gate's
whole failure list to the reach count.**

**What this does and does not prove**, stated precisely because the temptation is to read it as more than
it is. It proves the change moved none of the five maps we ship. It does NOT prove the two criteria are
equivalent in general - they are not, and the difference is exactly the case the old one was built for: a
re-roll that fixes reach while breaking something else. On these five seeds that case never arose, either
because no re-roll was rejected or because the two measures agreed. A wider seed set (the tripwire seeds,
a cohort) would exercise it harder.

That is acceptable and was the requirement: FR-002 asks for the difference to be DIAGNOSED, not prevented,
because the GM's standing ruling is that maps may move. Here there is no difference to diagnose. If a
future seed does move, the cause is already written down at the point of change in `driver.py`.

**Sources:** none - a measurement of this repository.

## R3 - `finish` places nothing and moves nothing, so 87 checks were attributed to the wrong owner

Feature 163's R10b left this open: 75% of the battery's "a later stage changed my input" evidence rested
on the single `finish` stage, and whether that stage genuinely MOVES features or merely writes them out
decided how much of the battery was really placer-guaranteed. T06 made it urgent - the destination ledger
put **87 of 127** placer-owned checks under `finish`, which is not a batch, it is the whole job.

**Measured by snapshotting the manifest either side of `finish`, on three maps across both archetypes**
(Inashiro seed 4 nucleated, Polder seed 19, a second nucleated at seed 31):

| | Inashiro 4 | Polder 19 | seed 31 |
|---|---|---|---|
| lists that GREW (a feature placed) | **NONE** | **NONE** | **NONE** |
| records whose GEOMETRY moved | **NONE** | **NONE** | **NONE** |
| annotation-only fields touched | `z`, `bedz`, `sheenz`, `keepout_chords` | same | same |

`finish` adds 8 keys on the reference map and every one is bookkeeping - `ink_classes`,
`unclassed_ink`, `unregistered_classes`, the `*_zmin`/`*_zmax` draw-order bounds, `field_chains`. It
mutates 5 and the mutations are `z` on lanes, `bedz`/`sheenz` on water, and a derived `keepout_chords`
index. **Sixty-four keys it does not touch at all.** Not one record's `pts`, `poly`, `outline`, `x`, `y`,
`w`, `h`, `rot` or `parts` differs before and after.

**So `finish` is a draw-order annotator and a serializer, not a placer**, and "last changed at finish" is
an artifact of z-order bookkeeping. The 87 checks it appeared to own are owned by whichever stage PLACED
their inputs.

**Two consequences.**

1. The destination ledger is re-keyed on the stage that PLACES each input, not the stage that last touches
   it. The migration batches only mean something under that keying.
2. **The GM's prediction is confirmed and feature 163's headline was wrong.** 163 reported 11 checks as
   "placer bug" against 116 to "fold into a trial-and-error placer", and the fold bucket's evidence was
   three-quarters this stage. It was bookkeeping. The GM said *"I'd be really, really surprised if our win
   is actually only eleven checks"*, and the surprise was warranted.

The honest note on scope: the checks that read what `finish` genuinely CREATES - `all_ink_is_ruled_on` and
its neighbors, reading `unclassed_ink` / `unregistered_classes` - are still owned by `finish`, because
those keys do not exist before it runs. That is a handful, not 87, and they are the ink-classification
completeness ratchets that T14 sends to static tests anyway.

**Sources:** none - a measurement of this repository.

## R11 - T22: THE COVERAGE FLOORS, MEASURED RATHER THAN ASSUMED

The FULL run reports the hamlet-path floor at **99.28%**, ~90 lines across 11 modules, and
`perf_review.py` at 98%. T22's bar is that a floor is RE-DERIVED, never lowered - so the question is
which of those lines this feature cost. Answered by measurement, in four parts.

### 1. The coverage carriers I deleted were ALREADY DEAD

`tests/full/test_coverage_carriers.py` replayed eight frozen pool maps through the whole gate. In the
BASELINE worktree at `95847698` (the commit before this feature, battery intact) **all eight fail with
`FileNotFoundError`**: they read `pool/<tier>/<name>.json`, and feature 161 moved every map into a
per-map folder under `legacy-hand-authored-pool/`. They had been dead since that landed.

**So deleting the file cost no coverage at all**, because it was providing none. This is the same
"path patterns outside the walk" failure as the two flat `*.gen.py` literals, three files over.

### 2. `perf_review.py`'s two branches WERE a real loss - and are re-derived

Lines 69-70 (`_records`' corrupt-file skip) and 89 (`pairs`' label filter) lost their only reader with
the carriers. Both are re-derived as real tests in `tests/tools/test_perf_review.py`, not exempted:
`make cov-file` now reports 167 statements, 0 missed, 100%.

### 3. The hamlet-path floor's ~90 lines are NOT this feature's

The other deletion that could have cost coverage is `tests/check_village/`. Probed directly, in the
baseline worktree, against the two largest blocks in the floor's missing set:

| probe | result |
|---|---|
| `test_common_geometry.py` vs `settlement/_geom/primitives.py` | 11% - **108-125 listed as Missing** |
| `test_driver_and_fixtures.py` (runs every check) vs `settlement/_knobs.py` | 38% - **562-602 and 725-758 listed as Missing** |

The battery's own broadest test was not the reader for those lines either. The floor gap predates this
feature, which is consistent with the fourth finding.

### 4. `make done FULL=1` HAS NEVER BEEN GREEN in the recorded history

Four FULL-scope runs exist in `dev/run-log/`: one on 2026-08-25 (five days before this feature) and the
three this feature ran. **None is green.** The FULL-only floors have not been satisfied by any recorded
run, so treating today's number as a regression from today's change would be wrong.

### What is therefore owed, and to whom

- **This feature owes nothing further on coverage**: the one real loss is re-derived, and no floor was
  lowered. The `--omit` list swapped `check_village/` for `overlap/`, which is the deleted package's
  successor holding the same taxonomy - a rename, not a widening.
- **Somebody owes the FULL gate a feature.** Bringing it green means ~90 hamlet-path lines, the four
  `ci/` modules and `switches.py` (whose `tooling` tests are deselected when the stamp is fresh, so
  their lines go uncovered without anything being deleted), and the stale-path class feature 161 left
  behind. That is a tooling feature, not part of retiring a check battery, and it is recorded here
  rather than smuggled into this one.
