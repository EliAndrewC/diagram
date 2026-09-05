# Tasks - feature 182

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

- [x] T01 FR-001: sweep -> soak, everywhere
      research: procedure
      verify: DONE. Directory, target, doc, `norecursedirs`, `make_target`, `ci/CLAUDE.md` and both
      test suites. `make sweep` no longer resolves; `make soak` refuses on the empty suite
- [x] T02 FR-002: the gate banner
      research: procedure
      verify: DONE. It now reads "the whole suite: every pool map, seeds 41-44; `FULL=1` adds only
      the perf bookends" - and the gate printed exactly that on the run that verified this change
- [x] T03 FR-003: `test-full`'s help
      research: procedure
      verify: DONE - "the gate's whole test phase + all three coverage floors (everything except
      tests/soak/, which only `make soak` runs)"
- [x] T04 FR-004: the two `ci-*` help lines
      research: procedure
      verify: DONE. `ci-check` runs the SOAK suite; `ci-merge` says it is no longer a merge queue
- [x] T05 FR-005/a/b/c: retire `tripwire`
      research: procedure
      verify: DONE. Rule removed, off `.PHONY` (a phony name with no recipe still exits 0), registry
      names `maps`, `TRIPWIRE_SEEDS` kept. `make -n tripwire` fails; `make -n maps` works
- [x] T06 FR-006: records untouched
      research: procedure
      verify: DONE. `TARGET=tripwire` survives in `dispatch.py` and `test_cache.py` as accounts of
      builds that ran on 2026-08-31, and throughout `specs/`
- [x] T07 the gate green, the spec FAITHFUL, and the answer to the GM
      research: procedure
      verify: DONE. `make done` GREEN - 2,975 passed, **22,621 statements 0 uncovered 100%**,
      hamlet floor **12,449 / 0 / 100%**. spec-fidelity FAITHFUL at round 2. An earlier run of the
      SAME content reported 40 uncovered; a merge from main landed mid-collection and the re-run on
      the settled tree was clean, which is the diagnosis the reviewer declined to take on trust
