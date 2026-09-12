# Feature 235 - plan

**Spec**: [`spec.md`](spec.md), ACCEPTED (`spec-fidelity` FAITHFUL at round 5 of a counter the GM reset).

## Constitution check

| principle | how this feature meets it |
|---|---|
| XII (the record's citation rules) | this feature AMENDS it: Principle XII says the footnote test "holds the two footnote forms", and after this there are three. A MINOR bump, the GM's words of 2026-09-12 recorded as the ruling |
| XIV (fix defects where you find them) | two session-addressed sentences in reader-facing text (FR-007), and a registry header still stating the rule feature 195 superseded, both found while doing this and both fixed here |
| XVI (build what was asked; reviewed by someone else) | five rounds on a reset counter, FAITHFUL. Three of them found factual clauses built on descriptions rather than on the pages |
| XVII (a README is the GM's) | `research/README.md` states the same binary and is OFFERED a correction, not given one |
| VI (verification before done) | `make page-check` and `make done` green |
| X clause 5 (100% coverage) | the census is a new tool under `l7r/`, so it owes 100% the day it lands |

## The order, and why

**The four surfaces first, because one of them would reject the new form.** `quote-check` reports a
footnote with no key and no link as an assertion with no usable citation, and the footnote test's consumer
demands a key, a link and a quotation from anything that is not an absence note. Writing a grounds note into
the record before teaching those two would turn the gate red and look like the feature failing rather than
the checkers not knowing the vocabulary.

1. The constitution's Principle XII, with its version bump.
2. `research/CLAUDE.md`, which is what the next session writing an entry reads.
3. `tests/interactive/test_footnotes.py` - the classifier AND the consumer.
4. `.claude/agents/quote-check.md`.

**Then the census**, because SC-003 needs it run BEFORE the record changes as well as after, and because
every footnote number quoted in this whole body of work was built by hand and three of those hand-built
tables were wrong.

**Then the notes**, one at a time, each re-read at its page. One converts, three are argued, fourteen stay.

**Last the two defects** and the closing report with the README correction offered.

## What this feature must not do, and the guard for each

- **Move a research question out of the backlog.** FR-003 forbids it, `record-format` judges it, and the
  three unexemplified reasons are barred from use here entirely (SC-004b).
- **Delete a footnote.** FR-007 was rewritten precisely because an earlier draft would have deleted two,
  which is the GM's complaint inverted.
- **Run against a moving record.** Feature 232's writers are changing the same pages right now, which is why
  SC-003 measures this feature's own delta on one tree rather than the global count.

## Risks

- **The census disagrees with the hand counts.** Expected, and it is the point; where they differ the tool
  is right and the prose is corrected.
- **A page a 232 writer is editing is also one of the eighteen.** Sequenced: the notes are done after the
  writers report, not beside them.
- **`record-format` has a new duty and no worked example.** Its first run on a grounds note is the test of
  the duty as much as of the note.
