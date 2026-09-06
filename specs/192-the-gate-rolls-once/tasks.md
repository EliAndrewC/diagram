# Tasks - 192 The gate rolls once

All `research: rendering` - gate mechanics and a coverage-floor subject list, with no claim about
how a place was built, farmed or lived in, so the three physical-research boxes do not apply.

- [x] T01 `research: rendering` FR-001/003/004: `_stores_under_bypass` + the FULL bypass falls
      through to the store tail. Scoped to `L7R_TESTS_FULL` and `report:` subjects; `GATE_NO_CACHE`
      untouched. Verified: 16 rollcache tests.
- [x] T02 `research: rendering` FR-002/SC-002: no roll is SERVED under FULL - the second FULL call
      still returns `BYPASS-STORED`, not `HIT`. Asserted.
- [x] T03 `research: rendering` SC-003: the both-bypasses assertion SPLIT rather than deleted -
      FULL stores, `GATE_NO_CACHE` does not, `GATE_NO_CACHE` wins when both are set, and a
      non-`report:` subject stores nothing. Four new cases.
- [x] T04 `research: rendering` SC-001. FR-001's half is MEASURED on an instrumented cold gate: the
      post-pytest floor gap fell **401.6 s -> 175.3 s**, total 803 s -> 610 s. That run PREDATES
      FR-007 (its floor wrote a Polder 8 record at 13:37:26), so it measures four-of-seven removed;
      the five-removed figure is closed by T09. The floor reports **88 modules** either way, and the
      seven- and eight-subject unions were verified SET-IDENTICAL, not merely equal in size - which is
      the sentence the safety claim needs.
- [x] T05 `research: rendering` FR-006: the `done` ratchet re-pinned 310 -> 400 s, the GM's own
      figure, reason resting on 191 R7 and recording that this session's earlier re-pin was reverted.
- [x] T06 `research: rendering` FR-007: `Polder seed=8` dropped, plus all four places the removal
      makes wrong - the test's count, two prose claims in `hamlet_floor.py` (one already false), and
      the Makefile comment. Verified: 8 hamlet-floor tests.
- [x] T07 `research: rendering` FR-008: `report_deps` delegates to `_produce_and_store`; the store
      exists in ONE body, as its docstring claims.
- [x] T08 `research: rendering` SC-004: `make done` green, 100% coverage held.
- [x] T09 `research: rendering` SC-001 closed on a post-FR-007 COLD run. Instrument note: the right
      instrument is an EMPTIED `.gencache/rolls`, not `GATE_NO_CACHE=1` - that flag also disables the
      storing FR-001 adds, so it would measure the unfixed configuration and read as a regression.
