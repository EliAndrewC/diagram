# Implementation Plan: money foundation research (feature 390)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-18

## Summary

A research-record feature: four new questions in the money section (land price against yield, unskilled wages, the
koku of rice, the Kyoto basket), each from a research pass already run (`passes/`), written and checked in fresh page
sessions, answered on EliAndrewC/diagram#1. No code, map or canon change.

## Technical Context

- **The record.** The edits are made by fresh page sessions from briefs: `make page-session BRIEF="briefs/w1-write.md
  briefs/w1-check.md"`. There is one write session for the four questions (the cap is four) and one check-and-apply
  session. Up to ten new registry keys are expected (Bassino & Ma; Saito 2003; Allen et al.; the land and koku sources).
  Past ten, the write session's continuation brief takes the rest.
- **The passes.** `passes/q1-land.md`, `q2-wages.md`, `q3-koku.md` and `q4-basket.md` hold each pass's verbatim passages
  and URLs. They are leads; the write session reads each passage on its page before citing it. A PDF that `make
  source-pages` cannot read is read from a local download, archived, and cited at its public URL.
- **The section.** The first money question homes in `contents.json#money`, so the write session deletes its `awaiting`
  line (feature 389) in the same commit.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A - no map, glyph, pool content or kanji beyond quoted originals; quoted Japanese and Chinese follow the record's
  translation form.
- XII: every question task is `research: physical` with its five boxes.
- XIII: `make record CHECK=1` and the record tests stay green.
- XVI: built as the spec's FRs and acceptance scenarios.

## D1 - the four questions (FR-001, FR-002; scenarios 1-4)

Each is a new question, `make reserve KIND=question KEY=<heading id>`, tagged `subject=money`. Settings and levels:
- **Land:** `setting=countryside`, `level=counts-and-measurements`.
- **Wages:** `setting=countryside,city`, `level=counts-and-measurements`.
- **The koku:** `setting=countryside`, `level=foundational`.
- **The basket:** `setting=city`, `level=counts-and-measurements`.

Each question has no drawing page. Its heading is the question a reader would ask:
- "What did farmland sell for, against what it yielded?"
- "What did an unskilled laborer earn?"
- "How much rice was a koku?"
- "What did a Kyoto laborer's year of goods cost?"

Each answers every clause of its acceptance scenario, with a verdict per figure the request names. The comparisons the
asker gave beside each question are stated as the asker's figures and set against the evidence:
- the canon's ~50-koku farm and its interest rates;
- the 2017 working wage figures;
- `budgets.md` and `l7r.md` on the koku;
- the 2017 basket snapshot.

The GM's canon itself is quoted only where a comparison needs it, and never corrected on the page.

## D2 - the canon contradictions go to the GM (FR-005; edge case 2)

Where a finding contradicts `l7r.md` or `budgets.md` (for example the 40-gallon koku against `budgets.md`'s ~180 L), the
question states the history. The issue answer flags the contradiction, through `escalation-check`, for the GM to decide.

## D3 - the implementation check (FR-004)

`implementation-check.md` gets one line per question:
`- NNNN: no code implements it - consumed by gm-assistant's money skill; searched: grep -rn '<terms>' l7r pool`.

## D4 - the answer (FR-005)

A comment on EliAndrewC/diagram#1 gives, per question, the fragment FILE, the verdict per figure, what is open, and each
contradiction with canon flagged for the GM (D2). The asker lists the 2017 basket snapshot as Q4's canon, so a source
figure that differs from it is flagged for the GM the same way.

## T - the order

1. W1: write the four questions, then check them (the page sessions).
2. The implementation check.
3. The issue answer.
4. Report and land; `sync-with-main.sh done` (no engine code: the direct route).
