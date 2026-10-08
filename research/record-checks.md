# Which record check is owed, and when it is answered

**Load this file when:** a change to the record is about to be pushed and you need to know which checks it owes, how to
record a check's answer, or why the push refused it (`entry-gate.sh`, `claims-gate.sh`, `_entry_owed.py`).

How a check is dispatched (on a bundle, `make check-bundle`) is in [`CLAUDE.md`](CLAUDE.md), "Checking"; why each rule
holds is in [`../docs/research-record-rules.md`](../docs/research-record-rules.md).

## Owed by the words that changed (GM 2026-10-02, feature 311)

A check is owed only where the words it reads changed - *"it would be a waste of time and tokens for us to add the kind of
paragraph that I just explained and then rerun all of the other subagent checks"* - and owed means it runs: *"not just do
the correct thing, to kind of enforce us doing the correct thing."* So `make record-owed` names every unit a delta owes,
against main:

| what changed | owes |
|---|---|
| a question's heading | `intro-check` |
| its intro | `intro-check`, `record-format` |
| a note | `source-reader`, `quote-check` on it, `record-format` |
| a reworded block carrying notes | `quote-check` on those notes |
| new unmarked prose | `quote-check`'s unfootnoted reading |
| a registry write-up | `source-applicability` |
| a translated pair | `translation-check` (`make translation-owed`) |
| a section a modal was written from | `entry-drift` (below) |

Only WORDS count: a comment, a tag marker, markup or a re-wrap owes nothing, and a move or a merge owes nothing either.
`make check-bundle` refuses a bundle for a check nothing owes, and holds a `quote-check` to the owed notes; the dispatch
hook refuses a check its bundle's MANIFEST does not owe. When a check returns: `make record-checked CHECK=<check>
BUNDLE=<dir> RESULT="<counts>"`. The push (`scripts/entry-gate.sh`) refuses a unit with no answer at the content pushed. A
fix that applies a check's findings is owed its second round; a `NOT_OWED_OK`, `CHECK_NOT_OWED_OK`, `RECORD_CHECKS_OK` or
`REASON=` goes to the audit with its reason.

## A question's findings changing owes the CODE's claims too (feature 316)

The engine and the Mode A procedures cite the record claim by claim (`Research:` docstring lines, `<!-- Research: ... -->`
in a procedure). `make claims-owed` names every claim whose cited question's findings (its words less its intro) moved,
and the push (`scripts/claims-gate.sh`) refuses it until `impl-drift` has judged it (`make claims-bundle`, then `make
claims-checked`); a page edit re-owes only the claims resting on the blocks it changed, the rest go through one `make
claims-triage` (feature 318). `make claims-report` lists every claim out of step and every UNRESEARCHED decision - the open
research on the code's side.

## When a section a modal was written FROM moves (GM 2026-09-12, feature 234)

A modal IS its `Kind` class's docstring (`interactive/classes/`), written from the section its `Entry:` names.
`scripts/_entry_owed.py` names every class whose section's FINDINGS changed while its prose did not (its words, less the
intro: feature 311); the push refuses until each pair is answered - an `entry-drift` check and a rewrite of what it calls
DRIFTED (`make record-checked CHECK=entry-drift ...` when it returns IN-STEP), or one recorded
`ENTRY_DRIFT_OK="<what moved, and why no modal is now wrong>"`. `record-format` and `quote-check` are NOT this check:
neither opens a modal.
