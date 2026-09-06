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
- [x] T09 `research: rendering` SC-001 CLOSED on a post-FR-007 COLD run - **floor phase 114.0 s**
      against SC-001's predicted ~115 s, on a genuinely cold cache (`[MISS]` reference line), gate
      green at exit 0, **88 modules** on the hamlet path (unchanged - the floor measures the same set
      it did before) and 22,992 statements at 100%. The arc, all three cold: **401.6 s -> 175.3 s**
      (FR-001) **-> 114.0 s** (FR-007).
      **TICKED ONCE BEFORE IT HAD RUN, and unticked at review round 5 - the error is worth keeping.**
      A task is ticked on VERIFICATION, not on launch; the run I ticked it for short-circuited in 0 s
      as `already-verified` and rolled nothing, which is exactly the single-digit-seconds shape of the
      "a dry run granted a push" defect fixed earlier the same day.
      **INSTRUMENT, all three elements** - the first two I reasoned out, the third I missed:
      (a) NOT `GATE_NO_CACHE=1`: it disables the storing FR-001 adds, so it measures the UNFIXED
          configuration; (b) it also forces every pool map to regenerate, so it is wrong on a second
          axis; (c) empty `.gencache/rolls` for a cold ROLL cache with a warm pool cache - the state
          a real post-engine-change gate is in - **AND** remove `.git/verification-state.json`,
          because the gate's short-circuit is keyed on engine content and an emptied cache does not
          re-open it.
- [x] T10 `research: rendering` Constitution XIV, found while fixing T01's ruff failure and fixed in
      this feature rather than filed: two `:` documentation lines inside Makefile recipes used
      BACKTICKS inside double quotes, so `/bin/sh` executed them. Line 117 printed
      `lint: not found` / `static: not found` on every `make done` since feature 185; line 713 would
      have run `ci-check` the same way had that recipe been reached. Both single-quoted, which reads
      the same to a human and is inert to the shell. Censused rather than spot-fixed: 89 `: "..."`
      documentation lines in the skill Makefile, **zero** now containing a backtick, and zero in the
      root Makefile; the three backticks left in the file are inside `#` comments, where they are
      inert - two of them comments about this very hazard. Deliberately NOT a requirement: the GM's
      request does not mention it, and promoting a found defect to an FR would make the spec claim
      scope it was never given.
