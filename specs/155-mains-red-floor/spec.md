# Feature Specification: main's red floor, and the coverage picture

**Feature**: 155-mains-red-floor
**Created**: 2026-08-29
**Status**: `spec-fidelity` round 1 returned CHANGES REQUIRED (4); all four applied, round 2 pending.

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
  inside its CPU budget or the budget deliberately and visibly raised with the reason. **THE AUTHORITY IS NOT
  THE GM'S REQUEST**, which asked about the coverage floor: it is constitution Principle XIV (GM 2026-08-17) -
  a defect found in the course of other work is fixed IN that work - and these were found while measuring the
  floor. The report owes the GM that distinction plainly: what they asked for, what was found beside it, and
  under which rule it was fixed.
- **FR-002** The floor is reached BY TESTS. No `# pragma: no cover` is added and `PARKED` stays empty. A
  hamlet-path line that only a NON-HAMLET tier reaches is put to the GM under the disposition
  `specs/145-hamlet-rolls-and-floor/spec.md` FR-002 already set - session-authored and `spec-fidelity`
  FAITHFUL, so binding as a project requirement but NOT as GM speech: *"no engine code is deleted to make the
  floor green ... that specific case is put to the GM"*. (An earlier draft of this line credited those words
  to the GM personally. They are 145's spec text; the GM's own words on the subject are *"eventually, we will
  just go back to one hundred percent code coverage everywhere"*. In this project italics mean verbatim GM
  writing, so the misattribution would have had a future session believe the GM ruled it at a terminal.) Deletion is available only for a
  line proved dead on EVERY path, with the proof recorded. (The first draft said an unreachable line is
  simply deleted, which reversed a standing GM ruling this session had forgotten.)
- **FR-003** A map fixed under FR-001 MUST be fixed at its cause. A house on a lane is a PLACER defect; a
  re-roll that moves the house without explaining why is not a fix, and the record must say which it was.
- **FR-004** Every fix MUST identify whose change introduced it, so the report to the GM distinguishes a
  defect from a design choice made by a session that is no longer running.
- **FR-005** The coverage REPORT owed to the GM must cover every level the project enforces or could
  enforce - the hamlet path, `settlement/`, the global floor, and the packages currently exempt - each with
  its number, what it would cost to bring to 100%, and what is standing in the way. It is a report for a
  DECISION: every option is stated with its price and none is omitted or subordinated. The report MAY carry
  this session's recommendation, provided it does not displace or abbreviate the full option set - the GM
  asked for the numbers and the basis, and forbade nothing.
- **FR-006** No map may be changed to pass a check without the change being reviewed by `settlement-review`,
  the standing rule for a Mode B map.

## Success Criteria *(mandatory)*

- **SC-001** `make done FULL=1` is green: every test passes and every enforced floor holds.
- **SC-002** The hamlet-path floor is 100% with `PARKED` empty.
- **SC-003** The coverage report is delivered with a number for every level and the price of closing each,
  and its numbers are measured AFTER the FR-001/FR-002 fixes have landed. The GM sequenced this twice -
  *"After you do this, then tell me"* and *"first fix main's floor being red and then report"* - and the order
  changes the answer: the hamlet path reads 44 lines short before the fix and 100% after. The pre-fix state is
  reported as history, never as the current number.
- **SC-004** The gap that let main go red is named to the GM with the options for closing it. Whether to
  close it is the GM's call, not this feature's.

## Decisions Recorded

Any line deleted as unreachable, any budget raised, and any map re-rolled rather than repaired carries its
reasoning at the point of change.

## Assumptions

- The GM's "thirty lines" is their recollection of 149's ledger, not a scope limit: "fix main's floor being
  red" names a STATE, and the state is 44 lines. That much needs no further authority. The three failing tests
  are NOT the floor and are fixed under the found-defect rule instead (FR-001), which the report says out loud
  rather than folding them into what was asked.
- The report is for a decision the GM will make, so it stops at options and prices.
