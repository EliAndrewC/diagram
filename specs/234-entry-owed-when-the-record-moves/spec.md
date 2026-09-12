# Feature 234 - the modal entry owed when the record moves

**Created**: 2026-09-12
**Status**: Draft
**Input**: the GM's message, verbatim, in `request.md`

## Summary

The GM asked, having just told a session to update the pigsty write-up on the map page: would that have
happened on its own? It would not, and the GM's conclusion - "that should be another fix to the project
guidelines and what have you" - is this feature.

What a modal says about a feature IS the docstring of its `Kind` class (feature 189), and that prose is
written FROM a research section which the class names in its `Entry:` tag. Two things are missing
between the two:

1. **Nothing checks the pointer still lands.** A class must carry an `Entry:` naming a `research/` file
   and that is all `test_an_entry_is_complete` asserts. `research_questions()` resolves the heading by
   prefix at page-write time and returns `[]` for a heading that no longer exists - silently. The
   consequence is a "See references" list that quietly goes empty on a map modal. `research/CLAUDE.md`
   already states the rule in prose - "a rename must fix its inbound links ... and the class entries in
   `interactive/classes.py` that quote the heading" - with no mechanism behind it. MEASURED 2026-09-12:
   a deliberately broken heading returns `[]` and no test fails.
2. **Nothing notices when the section's CONTENT moves under the entry.** Rewrite a research section -
   new findings, a changed label, a number corrected - and every modal written from it keeps its old
   prose, agreeing with itself. This is the failure the project already has a name for: a stale literal
   agrees with itself.

## Functional requirements

**FR-001** A new script MUST answer, for the working delta against the merge base with `origin/main`,
which feature classes' modal prose may now be stale: every class whose `Entry:` names a research
section whose BODY changed in that delta, and whose own docstring did NOT change in the same delta.
It MUST be modeled on `scripts/_review_owed.py` - the same "ask git, never cache" shape, printing one
class key per line, empty when nothing is owed, with a `--why` form printing the ruling.

**FR-002** The answer MUST be asked FRESH at every decision point rather than cached, for the same
reason `_review_owed.py` is: a phase of the run can move a file between the run's start and the turn's
end.

**FR-003** At the GATE the answer MUST be REPORTED and MUST NOT block - free, and it teaches before it
costs anything (the "TEACH FIRST, FREE" rung of this project's guard ladder).

**FR-004** At PUSH time the answer MUST REFUSE, naming each class, the section that moved, and the file
and line of the docstring to rewrite. It stays a refusal rather than a rewrite because the compliant
action is prose only the session can write - the same reasoning that keeps `make-only`'s `guard-write`
and `guard-file`'s no-marker branches refusals.

**FR-005** The refusal MUST have an escape token carrying a REASON of at least two words and eight
characters, through `_hookmatch.py escape_reason` like every other escape, recorded to the guard log
with a rule slug. The legitimate case it exists for: a research edit that does not bear on the modal's
prose (a footnote added, a typo fixed, a citation re-pointed).

**FR-006** A class's `Entry:` heading MUST resolve to at least one research question, enforced by a
gate test. A deliberately silent entry stays legal in the form `fallow` already uses - `research/
fields.html (no dedicated entry - recorded as silent)` - and that carve-out MUST be recognized
explicitly rather than by the absence of a match, so that a BROKEN heading and a DELIBERATELY silent
one cannot be confused.

**FR-007** Both checks MUST be proven to FIRE: a test that removes the mechanism, or breaks a heading,
and goes red. A no-op MUST refuse - per the project's own "a stale literal agrees with itself" note,
matching by shape rather than by a hardcoded literal that would drift with its target.

**FR-008** The rule MUST be written into `research/CLAUDE.md` beside the prose rule it gives teeth to,
and into `interactive/classes/CLAUDE.md` where "Writing an entry" is documented. The root `CLAUDE.md`
guard table MUST gain a row, since that table is the enumeration of what is enforced and where.

**FR-009** The guard MUST NOT fire on correct work. A research edit whose sections are named by no class
entry, and a class docstring edited in the same delta as its section, both stay quiet. This is the
project's own bar for whether a rule may be gated at all.

## Success criteria

**SC-001** With feature 233's research edits in the tree and its `PigSty` docstring left untouched, the
script names `pig sty`. With the docstring rewritten, it is silent.

**SC-002** Breaking any class's `Entry:` heading turns the gate red, naming the class.

**SC-003** Changing `fallow`'s deliberately silent entry to a broken heading turns the gate red - the
carve-out does not swallow the rule.

**SC-004** A delta touching only research sections no class names produces no report and no refusal.

**SC-005** `make hooks-test` green, `make done` green.

## Decisions recorded

**D1 - report at the gate, refuse at the push.** The two-stage shape is the ladder feature 164
established: teach where it is free, refuse where the cost is real. A refusal at the gate would spend a
round trip on every research edit.

**D2 - refuse rather than rewrite.** A guard that can produce the compliant command should produce it
(feature 164). This one cannot: the compliant output is a rewritten explanation, which requires reading
what the research now says. Stated here so the next audit does not reopen it.

**D3 - the unit is the SECTION, not the file.** A research page holds many questions and a class names
one or a few. Keying on the file would fire on every edit to a large page and train sessions to escape
it, which is the failure mode the "deliberately NOT enforced" list exists to prevent.

**D4 - the check is content-derived, never a stored hash.** No table of "the entry was current as of
this text" is kept anywhere: such a table is exactly the stale literal that agrees with itself. git is
the record.

## Out of scope

- Judging whether a rewritten modal entry is GOOD. That is `record-format` and `quote-check`, which
  already run on changed entries; this feature only ensures the rewrite is not silently skipped.
- The research pages' own prose, and any backfill of entries currently out of step with their sections.
  The check names them going forward; a sweep of the existing 51 is its own work and is NOT begun here.
  If the first run names classes other than `pig sty`, that list is REPORTED to the GM rather than
  quietly fixed under this feature.

## Review history

(to be filled by the `spec-fidelity` rounds)
