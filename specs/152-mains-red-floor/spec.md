# Feature Specification: main's red floor, and the coverage picture

**Feature**: 152-mains-red-floor
**Created**: 2026-08-29
**Status**: DRAFT - awaiting `spec-fidelity` before implementation

## What the GM asked for

Two things, in order. **First** fix main's floor being red - the GM said "the thirty lines that are not
yours", naming what feature 149 ledgered rather than absorbed. **Then** report on coverage generally, because
the 100% floors were narrowed while the project was still backfilling tests, and the GM wants to decide
whether to go back to enforcing 100% everywhere. They have not looked at the numbers recently and want them
before deciding.

## What is actually red (measured 2026-08-29 after syncing main, so larger than "thirty lines")

The GM's figure came from feature 149's ledger. Since then two peer features (150, 151) landed, and the
honest count is bigger. Reporting it rather than quietly fixing to the smaller number:

- **THREE FAILING TESTS**, none of them coverage: `test_village_passes_gate` fails for **sawada** and
  **kashikawa**, both on `houses_clear_of_lanes` - one farmhouse each standing on a lane tread, at
  (1826, 2438) and (2136, 2762) - and for **kuwabata**, which takes 49.4 s CPU against a 45 s budget.
- **44 uncovered lines** on the hamlet path across 13 modules, against a floor that demands 100%.

**Why main can be red at all, which is the finding under the finding.** The push gate is `make done`, and
`make done` DEFERS the coverage floors and runs only the reference map - the pool sweep and the floors are
`make done FULL=1` only. So a change can pass everything the push checks and still leave a pool map failing
its own gate and the floor red. Nothing lied; nothing was looked at.

## Requirements *(mandatory)*

- **FR-001** The three failing tests MUST pass: both maps clear of `houses_clear_of_lanes`, and kuwabata
  inside its CPU budget or the budget deliberately and visibly raised with the reason.
- **FR-002** The hamlet-path floor MUST be at 100% with no parked lines and no coverage pragma added to
  reach it. Where a line is genuinely unreachable, it is DELETED with its proof, not excused.
- **FR-003** A map fixed under FR-001 MUST be fixed at its cause. A house on a lane is a PLACER defect; a
  re-roll that moves the house without explaining why is not a fix, and the record must say which it was.
- **FR-004** Every fix MUST identify whose change introduced it, so the report to the GM distinguishes a
  defect from a design choice made by a session that is no longer running.
- **FR-005** The coverage REPORT owed to the GM must cover every level the project enforces or could
  enforce - the hamlet path, `settlement/`, the global floor, and the packages currently exempt - each with
  its number, what it would cost to bring to 100%, and what is standing in the way. It is a report for a
  DECISION, so it must state the options and their prices, not recommend one and hide the rest.
- **FR-006** No map may be changed to pass a check without the change being reviewed by `settlement-review`,
  the standing rule for a Mode B map.

## Success Criteria *(mandatory)*

- **SC-001** `make done FULL=1` is green: every test passes and every enforced floor holds.
- **SC-002** The hamlet-path floor is 100% with `PARKED` empty.
- **SC-003** The coverage report is delivered with a number for every level and the price of closing each.
- **SC-004** The gap that let main go red is named to the GM with the options for closing it. Whether to
  close it is the GM's call, not this feature's.

## Decisions Recorded

Any line deleted as unreachable, any budget raised, and any map re-rolled rather than repaired carries its
reasoning at the point of change.

## Assumptions

- The GM's "thirty lines" is their recollection of 149's ledger, not a scope limit; the real count is 44 plus
  three failing tests, and fixing what is red is the evident intent.
- The report is for a decision the GM will make, so it stops at options and prices.
