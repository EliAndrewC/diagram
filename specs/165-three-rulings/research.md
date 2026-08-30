# Research: implementing the three rulings

The evidence for the rulings themselves is feature 164's `research.md` R3, R4 and R5, and is not
repeated here. What follows is what the IMPLEMENTATION turned up - every item found by building the
thing rather than by reading it, and every one caught by a fixture rather than by review.

## R1 - the claim test had the same hole the ruling was closing

The first cut of FR-003 called a delta a NUMBER CLAIM when three things held: everything changed sits
under one `specs/NNN-slug/` directory, nothing outside `specs/`, and every changed path is an
ADDITION. That is not enough, and the suite proved it: **adding only `tasks.md` to a spec directory
that already exists in main satisfies all three** - and that is the IMPLEMENTATION push, the one that
owes a verdict.

Fixed by requiring that `spec.md` ITSELF be among the additions. A claim creates the spec; anything
later does not.

## R2 - the exemption opened a hole one step removed from itself, which nobody had asked about

Check 1 judged only the specs whose `spec.md` appeared in the delta. With the claim exemption in
place that leaves a route: claim the number with an unreviewed spec (exempt, correctly), then push
the implementation, whose delta touches the code and `tasks.md` but never `spec.md` again - and the
verdict is never required at all.

`spec-fidelity` had reasoned only about the claim push itself, where it was right: no implementation
can hide in a delta that is one new spec directory. The hole is in the NEXT push.

Closed by judging the feature DIRECTORY rather than the file: any delta touching `specs/NNN-*/`
brings that feature's `spec.md` under the check. The claim stays exempt; every later push for that
feature carries the requirement with it.

**This is recorded rather than quietly fixed** because it slightly widens what check 1 examines, and
the GM ruled on the exemption, not on this. It refuses strictly more than before, never less, and the
suite carries the case.

## R3 - three fixtures that could not fail

Each of these passed while proving nothing, and each was caught by a result that was too good:

1. **The discard fixture asked the hook about the wrong repository.** It spawned the hook with
   `cwd=<fixture>`, but the hook reads `$PWD`, and a process inherits `PWD` from its parent's
   ENVIRONMENT rather than from the spawn's `cwd=`. The hook was answering about `/diagram` while the
   fixture believed it was answering about a temporary repo with a real merge conflict in it.
2. **The review-gate fixture passed its range as an environment variable** when the script takes it
   as `$1`. The gate fell back to `origin/main..HEAD`, a fresh repo has no origin, so the diff was
   empty and all four cases "passed" - including the three that must be refused.
3. **Two review-gate fixtures put the "pre-existing" spec on the work branch**, so it was an ADDITION
   over `main..HEAD` - which is the claim shape they were supposed to be distinguished from. They
   were rebuilt with the spec in the base commit.

The shared lesson is the project's own rule for guards, applied to fixtures: prove it FIRES. A
fixture that cannot fail is worth less than no fixture, because it reports success.

## R4 - three existing vectors were testing the exemption, not the requirement

`test-review-gate.sh` had three cases asserting that a spec with no verdict is refused, and each
committed the spec ALONE. After the ruling that shape IS the number claim, so as written they would
have been asserting the exemption while claiming to assert the requirement. They now ship the spec
alongside another file, which is what shipping a spec means, and the property they exist for is
unchanged and still proved.

Converting a guard inverts its own vectors - the same finding as feature 164's R8, met again.

## R5 - the apostrophe, for the second feature running

`discard-hooks.sh` carries its parser inside a shell single-quoted string, so an apostrophe in a
COMMENT ends the program and the hook dies with a syntax error. Feature 164 lost a cycle to this in
`house-style-hooks.sh`; feature 165 lost one here. A note now sits at the point of change in both.

**Sources:** this session's own implementation and the suites named above.
