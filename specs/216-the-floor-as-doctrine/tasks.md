# Tasks - 216 the floor as doctrine

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md). All `research: rendering`.

- [x] T01 spec-fidelity review of `spec.md` against `request.md` - FAITHFUL before any code
      research: rendering
      verify: DONE. DONE. FAITHFUL at round 3 of 5: round 1 deleted the conditional second partial roll, itemized FR-005 d, set the amendment to 2.23.0; round 2 sent seed 43 (no coverage line) to the CI tier's tree under the clause itself and settled the woodland site on the stub. The tree is tests/ci_tier/ (the reviewer's aside: tests/ci/ would read as the tests of l7r/diagram/ci)
- [x] T02 `make roll-audit`: the tool, its tests, the target, the audit's pointer (FR-001)
      research: rendering
      verify: DONE. make roll-audit: tools/roll_audit.py + 4 tests, the target, OPERATIONS row; ran on the 2026-09-08 baseline (output in R2); found its own root one level short
- [x] T03 the woodland band on the pool's map; the clamp decision as a unit test; the polder tests on Polder 12 (FR-002 a-c)
      research: rendering
      verify: DONE. woodland band sweeps the hinterland stub site (test_hinterland.py); clamp decision is a unit test (test_sink.py); both polder-19 tests read POLDER_FALL_0; hamlet_floor subjects = Inashiro, Kuwabata, Polder 12
- [x] T04 the seatings' partial roll in a child; the nine lines as unit tests (FR-002 d)
      research: rendering
      verify: DONE. roll_seatings child (prefix + 3 variants, one roster row, shared across workers - keyed_to share=True after the census caught a double roll); the nine lines + four more are unit tests (route/touch/web/serve/hinterland/sink/driver)
- [x] T05 the doctrine: constitution 2.22.0, root CLAUDE.md, tests/CLAUDE.md, dev/loop.md (FR-003)
      research: rendering
      verify: DONE. constitution 2.23.0 VI clause + footer, root CLAUDE.md bullet, tests/CLAUDE.md, tests/soak/CLAUDE.md, dev/loop.md; docs/make-targets.html regenerated
- [x] T06 the roster, `make done` green, the census read (SC-001), R2, `make roll-audit` on the landed baseline, land (FR-004, FR-005)
      research: rendering
      verify: DONE. roster 3 rows; make done green 143 s (pytest 123 s, 3,471 passed, both floors 100%); census 3 rolls of 3 specs, 11 served (SC-001); make roll-audit ran on the saved baseline (R2); landing follows
