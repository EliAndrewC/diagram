# Implementation Plan: a money section of the research record (feature 389)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-18

## Summary

The record gains a `money` subject tag, a written request-and-answer protocol a diagram session loads before working a money
issue, the section itself declared as awaiting its first question, and a test that pins them. The section's `awaiting` is deleted with the first money question
(D2). No map or canon changes, and the one engine change is the record loader's (D2) (FR-005).

## Technical Context

The record's loader (`l7r/diagram/interactive/record/questions.py`, `contents.py`), `research/tags.json`,
`research/contents.json`, the rule files under `research/`. Tests: pytest through `make test-file` and `make quick`.

## Constitution Check

- I-IX, XI: N/A - no map, no glyph, no pool content, no setting prose, no kanji.
- X: ruff, ruff format, pyrefly, 100% coverage held; `contents.py` stays far under 1,000 lines and `idle_rules` under 100
  statements.
- XII: every task is `research: rendering` - nothing physical is decided; the questions that will decide prices come later as
  their own requests, each a physical task under its own feature.
- XIII: `make record CHECK=1` and `make quick` stay green.
- XVI: built as the spec's FRs; D2's ordering is a measured constraint, put to spec-fidelity with this plan.

## D1 - the tag (FR-001)

`research/tags.json` gains the subject `money`, "Money and prices": coinage, prices, wages, credit, land values and taxes
reckoned in money. Measured: with the tag added, `make record CHECK=1` builds cleanly (3,799 pages); a tag no question carries
is not refused.

## D2 - the section is declared now, `awaiting` its first question (FR-001, FR-002)

`make record CHECK=1` refuses a section whose rule takes no question: with the money section added and no question tagged,
it answered `contents.json section money: the clause {"primary": ["money"]} matches no question`; with `"takes": []` it
answered `takes nothing and holds nothing` (both measured 2026-10-18). The refusal stays for every other section, since it
catches a misspelled or dead rule. A section may instead carry `"awaiting": "<why>"`:
- `contents.py`: `Section.awaiting`, read from `contents.json`; `idle_rules` skips a section that is awaiting, and refuses
  its `awaiting` as stale once any of its clauses matches a question (`it holds a question now - delete its awaiting`).
- `research/contents.json`: the `money` section, after "Trades and services", taking `{"primary": "money"}`, with its
  `awaiting` line. The build already omits an empty section, so no page appears until a question does (measured: 3,799
  pages before and after).
- Declined: a placeholder question to hold the section open. It would be research no request asked for (spec-fidelity
  round 1, item 1).
- Declined: deferring the section to the first question's feature (plan review 1: FR-001 asks for the section now).

## D3 - the protocol (FR-003, FR-004)

A new rule file, `research/money-requests.md`, opening "Load this file when: you work a money research request". It holds:
- **A request carries** the question, the figure the skill needs from it, and the canon it must sit beside (with
  Japan-first or China-first when the asker says).
- **An answer returns** each question's fragment FILE, the verdict of each figure (ATTESTED, ATTESTED ONLY FOR, NOT
  ATTESTED, SILENT), and what is still open.
- **A contradiction with canon** is recorded as found and reported to the GM, who decides; no canon is changed.
- **The impl-check line**: `- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: <the grep>`.
- **The first money question's feature deletes the section's `awaiting` line** (D2).
- **Closing** follows the user-level "Working a GitHub issue" rule: the asker closes.

`research/CLAUDE.md`'s load table gains one row pointing at it.

## D4 - the test (SC-001, SC-002, SC-003)

`tests/interactive/test_money_section.py`, on the small fixture record (`tests/_flat_record.py`) and on the real one:
- A section `awaiting` its first question loads empty; without `awaiting`, the same empty rule is still refused.
- A question tagged only `money`, with no drawing page, makes the `awaiting` stale (refused); with it deleted, the question
  is homed in the money section.
- The real record has the `money` tag and section, and `research/money-requests.md` names the three parts of a request,
  the three of an answer, the impl-check line and the `awaiting` deletion; `research/CLAUDE.md`'s load table points at it.

## T01 - land

`make done`, then `scripts/sync-with-main.sh done`: D2 changes `contents.py`, so the route is GATED. `make impl-check F=389`:
the feature changes no question, so nothing is owed.
