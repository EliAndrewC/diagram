# Tasks: Files Stay at Human Scale, Enforced (feature 173)

Every task is `research: procedure` - this feature is about what the tooling checks of the
repository, and nothing in it concerns how a place was built, farmed or lived in. The GM's words,
including the census they pasted, are in [`request.md`](request.md); the measurements taken before
specifying are in [`research.md`](research.md).

## The check

- [x] T01 answer the GM's actual question first: IS the split manner prescribed?
      research: procedure
      verify: R1 - yes, one sentence of clause 13 plus **eighteen** worked package indexes, thirteen
      using the literal "look here when" wording and five routing under a different header. Reported
      as "present, and by example excellent; as instruction, one sentence"

- [x] T02 FR-001/FR-002: `scripts/check-file-scale.py` - 1,000 RAW lines, over the bar FAILS; every
      tracked or unignored `.py` except the frozen exhibits, other clones, `specs/` and the caches
      research: procedure
      verify: `tests/tooling/test_file_scale.py` - 1,000 passes and 1,001 fails; 1,001 lines of
      comment and blank still fails; the four exclusions are not scanned; a zero-file scan fails loudly

- [x] T03 FR-003: the refusal PRINTS the procedure - the obligation, the directory-module shape, the
      `CLAUDE.md` "look here when" index, a named exemplar, both carve-outs, the GM's own example
      research: procedure
      verify: `test_the_refusal_prints_the_procedure` asserts all eight; `test_the_refusal_states_no_duration`
      holds feature 171's rule

- [x] T04 FR-004: the carve-out is `FILE_SIZE_OK: <reason>` in the first 40 lines, 40+ characters,
      listed by `make audit`
      research: procedure
      verify: a justified file passes and is reported separately; a bare marker FAILS; a marker
      buried past line 40 FAILS. **It ships with zero files using it** - success criterion 7

- [x] T05 FR-005: wired into the skill Makefile's `lint` (so the gate reports before the map roll is
      paid for) and into `sync-with-main.sh` at push time (so the DIRECT route cannot land one either)
      research: procedure
      verify: `make lint` failed with the full message while `wip/shiro-daika.gen.py` was still over,
      and passes now; selftest runs first in both places, as `check-duplicate-defs.py` does

- [x] T06 FR-006: no new document - the message points at clause 13, `CLAUDE.md`'s "Files stay at
      human scale", and `settlement/structures/` as the worked exemplar
      research: procedure
      verify: scope REDUCTION made at spec review round 1; round 2 caught three places the cut
      document was still named and they were removed; round 3 returned FAITHFUL

## The ten refactors (FR-007)

- [x] T07 the mover: `specs/173/split_module.py` + `cuts.py` + `split_tests.py`, in the lineage of the
      fourteen retired splitters - `--analyze`, `--plan` (refuses a forward edge or a stale read),
      `--apply`
      research: procedure
      verify: it caught, before anything was written, that `ways.py`'s source order is not its
      dependency order, and that a rebound name straddling a cut in `shiro-daika.gen.py` needed
      checking rather than assuming

- [x] T08 `hamletgen/ways.py` 4,369 -> `ways/`, eleven layers bottom-up (the GM's worked example)
      research: procedure
      verify: acyclic on the first plan, largest module 552; 103 of 103 tests green

- [x] T09 `waterfields/seams.py`, `hamletgen/hinterland.py`, `hamletgen/homesteads.py`,
      `tools/pack_audit.py` -> packages
      research: procedure
      verify: each acyclic and under the bar; test_seams 42, test_hinterland 19, test_homesteads 17,
      test_pack_audit 91 - all green

- [x] T10 the three MIXIN files -> packages composing the original class name back
      research: procedure
      verify: `settlement/core.py`'s imports and base list untouched; `Settlement.__mro__` composes;
      test_water_ways 51, test_homestead_parts 39, test_structures 51 green

- [x] T11 `tests/hamletgen/test_ways.py` 1,541 -> `tests/hamletgen/ways/`, one file per submodule of
      its subject, the mapping DERIVED from which names each test exercises
      research: procedure
      verify: 103 of 103 green; the first vote counted only free reads and put 92 tests in two
      modules - counting attribute access as well distributed them across ten

- [x] T12 `wip/shiro-daika.gen.py` 1,592 -> `wip/shiro_daika/`, seven sequential parts + a 19-line
      driver. **The carve-out this spec first proposed for it was put to `spec-fidelity` and REJECTED**
      research: procedure
      verify: the map REGENERATED in 11.0 s - see T13, which is why that is the strong verification

- [x] T13 FIX A DEFECT FOUND WHILE WORKING (Principle XIV): the map's engine bootstrap looped forever
      research: procedure
      verify: it walked up looking for `settlement.py`, a package since feature 025 (2026-08-16), and
      `os.path.dirname("/")` is `"/"` - so it spun at the filesystem root. The map has been an
      INFINITE LOOP, not a failing script, for two weeks, which is how it went unnoticed: `make map`
      hangs with no output and no traceback (measured 2026-08-31: 45 minutes). It looks for the
      directory holding `l7r/diagram` now and RAISES at the root

- [x] T14 a `CLAUDE.md` index for each of the ten new packages, "look here when" per module
      research: procedure
      verify: generated from the cut table, so each line is the reasoning that CHOSE the cut, and the
      line counts are read off the files that landed; the eight parent indexes updated to point at
      the packages in the established phrasing

- [x] T15 the path literals outside the walk (the feature-161 lesson)
      research: procedure
      verify: swept `pyproject.toml`, `.gitignore`, `scripts/`, the Makefile and the guard fixtures
      for all ten old paths. One real hit: pyrefly's `project-includes` named
      `l7r/diagram/tools/pack_audit.py`, which would have silently stopped type-checking it.
      `make typecheck` green after: 0 errors

## The doctrine (FR-008)

- [x] T16 constitution v2.14.0 - clause 13 becomes GATED, both carve-outs intact, the v1.6.1 deferred
      TODO closed; `CLAUDE.md`'s mirror says GATED; file size leaves "Deliberately NOT enforced" for a
      row in the enforcement table; `make audit`'s blurb reports the carve-outs and asks the checker
      research: procedure
      verify: the old blurb said "five files already exceed it" against ten, and scanned `l7r tests`
      only - so `wip/` at 1,592 and all of `scripts/` were invisible to the report meant to catch this

## Verification (FR-009)

- [x] T17 no regressions, measured rather than remembered
      research: procedure
      verify: `make verify` reports **"maps whose manifest changed: none"** - the refactor moved no
      map. Gate + the paired independent review run together
