# Tasks: feature 149 - the coverage floor's flaky verdict

Every task is `research: rendering`. No GM acceptance task, by their instruction (*"No need for me approving
as a separate task"*).

- [x] T01 the GM's request verbatim; spec carrying 147's eliminations so they are not re-derived; `spec-fidelity` round 1 (3 changes) and round 2
- [x] T02 FR-001 the CAUSE established by measurement, not by hypothesis: all four scripted hamlets' cache entries carried `meta.json` written at 05:19 beside `coverage.data` from 04:52 - a fresh key advertising stale coverage. `store()` publishes a new key on every call but only the gate's miss path passes coverage, so any other regeneration path (`make maps`, the iteration regen) left the old data behind, and `gate_obtain` replayed it. Coverage is a set of LINE NUMBERS: replayed after the source moved, it marks the wrong lines
- [x] T03 FR-005 a stale replay made IMPOSSIBLE, not unlikely: coverage is dropped when an entry is re-stored without it, AND stamped with the key it was recorded under, so an entry poisoned before this landed heals itself (no stamp -> not replayed -> regenerated once)
- [x] T04 FR-007 the regression test, proved to FIRE by deleting the fix and watching it go red
- [x] T05 FR-003 the park removed - both the `hinterland.py` pragma and the `PARKED` entry
- [ ] T06 FR-002/FR-006 the floor's verdict and the sweep's cost measured on consecutive runs, recorded
- [ ] T07 landed on main
