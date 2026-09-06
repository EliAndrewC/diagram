# Tasks - 191 Refusals that tell the truth

Spec FAITHFUL at review round 3. Every task here is `research: rendering` - message text and a
guard's coverage, with no claim about how a place was built, farmed or lived in, so the three
physical-research boxes do not apply (constitution v2.12.0).

- [x] T01 `research: rendering` FR-000: investigate the gate slowdown; record in `research.md`.
      Delivered R1-R6. Outcome: NO code regression, and the two 800 s outliers remain UNEXPLAINED -
      three mechanisms tested and refuted (tooling-hash invalidation, roll-cache cold/warm,
      heterogeneous cores). Verified: an instrumented run, a per-core `taskset` benchmark, and a
      P-core-pinned suite run that refuted the core hypothesis rather than confirming it.
- [x] T02 `research: rendering` FR-001/002/003: `_invocation`'s ladder moves into `_Ladder.__doc__`,
      printed from it; `make reference` -> `make maps`; both durations gone; scope-lock vocabulary
      gone. Verified by rendering the refusal and reading it.
- [x] T03 `research: rendering` FR-004: `hamlet_floor`'s empty-path message moves to
      `_EmptyPath.__doc__` and names `make maps`. Verified by calling `check([])` and reading it.
- [x] T04 `research: rendering` FR-007: `Makefile`'s `_reference` failure path loses
      "(reference only under the lock)". Verified: the string is gone from the tree.
- [x] T05 `research: rendering` FR-005/006: `test_guard_message_durations.py` gains a Python half
      whose file set is DERIVED by AST (every engine `.py` that can print), and an extractor that
      reads printed literals plus docstrings whose `__doc__` reaches an output call. Verified: 6
      passed.
- [x] T06 `research: rendering` SC-003 both halves, by planting: a duration in a PRINTED docstring
      FIRES; `_invocation.py`'s module docstring - which contains both `make reference` and `~60 s`
      and is protected history - does NOT. Both asserted against the live file.
- [x] T07 `research: rendering` FR-008: every target named in a ladder ROW resolves as a make
      target. Recorded trap: the first regex fired on the message's own prose ("goes through a make
      target"), reporting `target` as missing - tightened to indented rows, comment at the point of
      change.
- [x] T08 `research: rendering` SC-004: `tests/tools/test_hamlet_floor.py` moved with the message.
- [x] T09 `research: rendering` SC-004: `make done` green, 100% coverage held.
