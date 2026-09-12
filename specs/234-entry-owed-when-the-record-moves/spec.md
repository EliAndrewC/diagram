# Feature 234 - the modal entry owed when the record moves

**Created**: 2026-09-12
**Status**: Draft (round 2 - the round-1 design was withdrawn, see Review history)
**Input**: the GM's message, verbatim, in `request.md`

## Summary

The GM asked, having just told a session to update the pigsty write-up on the map page: would that have
happened on its own? It would not. Their conclusion - "that should be another fix to the project
guidelines and what have you" - is this feature.

What a modal says about a feature IS the docstring of its `Kind` class (feature 189), written FROM a
research section the class names in its `Entry:` tag. Two things are missing between the two, and they
are NOT the same kind of problem - which is the whole design:

1. **A pointer that no longer lands is mechanically decidable.** `research_questions()` matches a
   heading by prefix and returns `[]` for one that no longer exists, silently; `test_an_entry_is_complete`
   asserts only `"research/" in fc.entry`. `research/CLAUDE.md` already requires a rename to fix its
   inbound class entries, in prose, with nothing behind it. A broken heading is never correct work, so
   this can be GATED.
2. **A modal whose prose has gone out of step with its section is a judgment about prose.** No
   git-derived rule can decide it. This is REPORTED and never refused.

The round-1 draft of this spec proposed a push-time refusal for (2) and was withdrawn on measurement:
replayed over the repository's own history, that rule would have fired on **30 of the last 32**
research-only commits, naming up to 41 classes at once, and every one of those 30 is a maintenance sweep
of the record - citations, translations, HTML-comment conversions - that changes no obligation on any
modal. `research.md` R2 carries the count. The root `CLAUDE.md` keeps a list of rules deliberately NOT
enforced precisely because "a guard that fires on correct work teaches a session to bypass every guard",
and this key would have earned its place on it.

## Functional requirements

### The report

**FR-001** A new script `scripts/_entry_owed.py` MUST answer, for the working delta against the merge
base with `origin/main`, which feature classes' modal prose MAY now be stale: every class whose `Entry:`
names a research section whose BODY changed in that delta, and whose own **explanation prose** did not
change in the same delta. It MUST be modeled on `scripts/_review_owed.py` - the same ask-git-never-cache
shape - printing one class key per line with the section that moved, empty when nothing is named, and a
`--why` form printing the ruling.

**FR-002** The exemption in FR-001 is keyed on the class's EXPLANATION prose - the `What:`, `Why:`,
`Note:` and `Caveat:` values - and NOT on the whole docstring. The docstring also carries the `Name:`,
`Covers:`, `Label:`, `Sources:` and `Entry:` data tags (feature 207), so a re-pointed `Entry:` or a
house-style correction would otherwise silence the check for that class while the prose a reader sees
stands untouched.

**FR-003** The answer MUST be asked FRESH at each decision point rather than cached, for the same reason
`_review_owed.py` is. The decision points are exactly two, and MUST be enumerated in the script's
docstring as feature 231 enumerates its three:
  1. `make page-check` - the target a research-page-plus-docstring delta actually owes;
  2. `scripts/sync-with-main.sh` at push time.

**FR-004** At BOTH decision points the answer MUST be REPORTED and MUST NOT block. Not at the gate, not
at the push, not with an escape token - there is nothing to escape, because nothing refuses. Naming a
pair costs a session one line of reading; refusing on it would spend a round trip on work that is
correct 30 times in 32.

**FR-005** The report MUST be actionable without further lookup: per class, the class key, the research
file and heading that moved, and the file and line of the docstring whose prose to re-read.

**FR-006** `make done` MUST NOT be the reporting channel. It exits at its short-circuit (skill
`Makefile:122`) before any phase runs when engine content is unchanged, and a research-page edit plus a
class docstring is not engine content (features 188, 189, 207) - so a report there would be vacuous for
the exact delta this feature exists for, shipping green and never printing once.

### The gated half

**FR-007** A class's `Entry:` heading MUST resolve to at least one research question, enforced by a gate
test naming the class that fails. This fires on exactly the thing it names and is never correct work,
which is what qualifies it to be gated at all (the bar the root `CLAUDE.md` sets in its
"Deliberately NOT enforced" note).

**FR-008** A deliberately silent entry MUST stay legal in the form `fallow` already uses -
`research/fields.html (no dedicated entry - recorded as silent)` - and MUST be recognized EXPLICITLY
rather than by the absence of a match, so a broken heading and a declared silence cannot be confused.

**FR-009** FR-007 is PROPHYLACTIC and the spec records it as such: measured 2026-09-12, **0 of 51**
entries are broken today (50 resolve, 1 is the declared silence). It gives teeth to a rule
`research/CLAUDE.md` already states in prose; it is not a fix to a live defect, and a later audit must
not read it as one.

### Proving they work

**FR-010** Both checks MUST be proven to FIRE: a test that breaks a heading and goes red, and a test
that constructs a delta and asserts the script names the class. The matching MUST be by SHAPE rather
than against a hardcoded literal that would drift with its target.

**FR-011** Restating the project's "a stale literal agrees with itself" note as a testable obligation: a
test MUST fail if the script's matching surface matches NOTHING - so a check that has silently stopped
matching (a renamed tag, a changed docstring format, a moved research directory) cannot pass by being
vacuously quiet.

### The guidelines the GM asked for

**FR-012** The rule MUST be written into `research/CLAUDE.md` beside the prose rule it gives teeth to,
and into `interactive/classes/CLAUDE.md` where "Writing an entry" is documented: when a section a class
was written from moves, the session re-reads that modal against it and either rewrites the prose or
records why it did not change. The root `CLAUDE.md` guard table MUST gain a row, that table being the
enumeration of what is enforced and where - the row stating plainly that the staleness half REPORTS and
the heading half GATES.

**FR-013** The guideline MUST route the judgment where this project already routes judgment about
reader-facing prose: to a subagent on Opus. A named pair is a reason to run `record-format` (and
`quote-check` where the assertions moved) over the changed entry, which the standing rules already
require of a changed research entry - the report's contribution is that the session KNOWS to.

## Success criteria

**SC-001** Over a CONSTRUCTED delta in a fixture repository - a research section's body changed, a class
naming it left alone - the script names that class, its section and its docstring line. (It must be a
constructed delta: feature 233 lands its research edit and its docstring rewrite together, so the real
tree will correctly say nothing.)

**SC-002** Over the same fixture with the class's `What:`/`Why:` prose also changed, the script is
silent; with only its `Entry:` tag changed, the script still names it (FR-002).

**SC-003** Breaking any class's `Entry:` heading turns the gate red, naming the class.

**SC-004** Changing `fallow`'s declared silence into a broken heading turns the gate red - the carve-out
does not swallow the rule.

**SC-005** A delta touching only research sections no class entry names produces no report.

**SC-006** Deleting the script's matching surface turns FR-011's test red rather than producing a quiet
pass.

**SC-007** `make hooks-test` green, `make done` green, `make page-check` green.

## Decisions recorded

**D1 - REPORT, never refuse.** The round-1 design refused at push. Withdrawn on the measurement in
`research.md` R2: 30 of 32, up to 41 classes at a time, all correct work. Recorded here rather than
silently dropped, because the next session to notice this seam will have the same idea.

**D2 - the split between what is gated and what is reported is the design.** A heading that does not
resolve is decidable and never correct; a modal that has drifted from its section is a judgment about
prose. Putting both behind one mechanism is what made the first draft wrong.

**D3 - the unit is the SECTION, not the file.** File-level keying would fire on every edit to a large
page. It does not rescue the staleness key from R2 - the sections classes name ARE the busy ones - but
it is still the right unit for the report, which should name the section a reader would look at.

**D4 - content-derived, never a stored hash.** No table of "this entry was current as of this text" is
kept: such a table is exactly the stale literal that agrees with itself. git is the record.

**D5 - no escape token.** Nothing refuses, so nothing needs escaping. Stated because every other guard
in this repository has one and its absence would otherwise read as an oversight.

## Out of scope

- Judging whether a rewritten modal entry is GOOD - that is `record-format` and `quote-check`.
- Backfilling entries currently out of step with their sections. The check is DELTA-based against the
  merge base and cannot surface historic drift at all; the first run's delta is feature 233's edits, so
  it will name what 233 touched and nothing else. An empty result is therefore NOT evidence that the 51
  entries are in step, and the spec says so here so nobody later reads it as such. A sweep of the 51 is
  its own work, wants the GM's call, and is not begun here.

## Review history

**Round 1** (`spec-fidelity`, 2026-09-12): verdict CHANGES REQUIRED, nine items. The central one killed
the design: the reviewer replayed the proposed push-time refusal over the repository's own history and
found it would fire on 30 of the last 32 research-only commits, naming up to 41 classes at a time, all
of them correct maintenance work on the record - and noted that the draft contradicted itself, FR-009
asserting it would not fire on correct work while FR-005 named that same work as its escape's purpose.
The refusal is withdrawn (D1) and the measurement recorded (`research.md` R2). Also taken: the gate is
not a reporting channel because `make done` short-circuits before any phase on this delta shape (FR-006,
`research.md` R3); the exemption is narrowed from the whole docstring to the explanation prose (FR-002);
the decision points are enumerated (FR-003); "a no-op must refuse" is restated as a testable obligation
(FR-011); SC-001 is restated over a constructed delta, its original premise being about to become
impossible once 233 lands its research edit and docstring together; FR-007's zero-current-violations
status is disclosed (FR-009); and the "Out of scope" bullet no longer implies the first run could
surface the existing backlog. The reviewer's closing aside - that the reliable half of this seam is a
judgment the project already routes to an agent - is taken as FR-013.
