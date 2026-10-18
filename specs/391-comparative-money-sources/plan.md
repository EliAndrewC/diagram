# Implementation Plan: comparative money sources, and The Complete Servant (feature 391)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-10-18

## Summary

The record gains a COMPARATIVE category for money:
- the GM's rule, written into the research guidelines;
- a source KIND and a question SUBJECT that mark it where a reader meets it;
- a build refusal when a comparative source is cited outside a comparative question;
- a judgment for it in `source-applicability`.

Its first use is *The Complete Servant* (Adams, London, 1825):
- the text archived;
- gm-assistant's 25 extracted rows checked by an independent agent;
- the issue's items written as comparative questions in a page session, checked, and answered on EliAndrewC/diagram#2.

## Technical Context

- **The vocabulary.** `research/source-tags.json` (kind), `research/source-sections.json` (where works are listed),
  `research/tags.json` (subject) and `research/contents.json` (where questions are homed).
- **The build.** `l7r/diagram/interactive/record/site.py` `_works` is where each question page's cited keys meet the
  catalog's tags. It is an engine file, so the landing is GATED.
- **The contract.** `.claude/agents/source-applicability.md`. Its vocabulary block is derived by `make
  source-tags-contract`.
- **The record edits.** One write page session for the questions (three, under the cap of four), then one check session.
- **The text.** Project Gutenberg #69487, plain text at `https://www.gutenberg.org/ebooks/69487.txt.utf-8`. Gutenberg's
  text keeps no page numbers. The edition and page of each figure are taken from the scan it was made from (Internet
  Archive), named in the registry entry. Where a page cannot be read on the scan, the answer says so.

## Performance bookends

N/A: the build check adds one set lookup per cited key.

## Constitution Check

- I-XI: N/A - no map or glyph.
- X: ruff, ruff format, pyrefly and 100% coverage are held; `site.py` stays under 1,000 lines.
- XII: the question tasks are `research: physical` with their five boxes; the vocabulary, build, contract and guideline
  tasks are `research: rendering`.
- XIII: the record tests and `make done` are green.
- XVI: built as the spec's FRs.

## D1 - the vocabulary marks it (FR-002)

- **Source kind `comparative`** in `source-tags.json`: "A source on another society's money - its wages, prices and
  household budgets - read only as a yardstick players know from fiction (Austen, Dickens). It never sets a koku's value,
  a Rokugani price or wage, or anything on a map, and is cited only by a comparative money question." A comparative work
  carries it as its PRIMARY kind (`kind=comparative,primary`), so the works lists group it apart.
- **Works section** `works-comparative` in `source-sections.json`: "Comparative money sources", taking
  `{"kind": "comparative"}`, placed before `works-beyond-east-asia`. The first section that takes a work is its home.
- **Question subject `comparative`** in `tags.json` ("Comparative money: another society's wages and prices").
- **Questions section** `comparative-money` in `contents.json`, after `money`, taking `{"primary": "comparative"}`. Its
  description states the category and its limits. A comparative question is tagged `subject=comparative,money`.
- **The `europe` and `elsewhere` explanations** add: "...and, for money alone, as a comparative yardstick (the
  Comparative kind) - never as the setting's own figures." This keeps the tags agreeing with the category (FR-001).

## D2 - the build catches a misuse (FR-004)

In `site.py`, `_works` takes the question's tags. A cited key whose PRIMARY kind is `comparative`, on a question whose
subjects do not include `comparative`, is refused: "`<where>`: cites `<k>`, a comparative source - only a comparative
money question (subject `comparative`) may cite it (research/CLAUDE.md, Comparative money sources)." A test on the small
fixture record proves both the refusal and the pass, and that the comparative chip reaches the built page.

## D3 - the guidelines (FR-001)

`research/CLAUDE.md` gains a section, "Comparative money sources (GM 2026-10-18, feature 391)":
- **What it is.** A source on another society's money, not a cross-cultural method.
- **Why it exists.** The GM's words.
- **Its limits.** Money only; never a koku's value, a Rokugani price or wage, or a map; never cited for how a place was
  built, farmed or lived in; not sought out unless the GM asks for it or approves it.
- **How it is marked.** D1 and D2.

`research/money-requests.md` points at it. The full text with the GM's words verbatim goes in
`docs/research-record-rules.md` under the same heading.

## D4 - the source check judges it (FR-003)

`source-applicability.md` gains a paragraph. A work whose primary kind is `comparative` is judged on two things:
- whether it is a sound record of ITS OWN society's money: a source of the time, or scholarship on it;
- whether its write-up states the comparative limits.

It is not judged on whether it fits East Asia. Its verdict NOT-APPLICABLE is kept for a comparative source cited outside
a comparative question, or used as the basis of a Rokugani figure. `make source-tags-contract` re-derives the vocabulary
block.

## D5 - the source (FR-005)

A registry entry `adams-1825-complete-servant`:
- the citation line names the Gutenberg text and the scan;
- the two write-ups ("What it is" and "Why it applies, and its limits") state the comparative limits;
- tags `period=modern-preindustrial; region=europe; kind=comparative,primary`.

The text is archived (`make archive`).

## D6 - the extraction check (FR-005; SC-003)

gm-assistant's 25 `complete-servant` rows are copied from `ledger.jsonl` on gm-assistant `main` into the feature
directory (`extraction/rows.jsonl`, with the commit). A `source-reader` agent checks each row against the archived text:
- READ, MISQUOTED, WRONG-POST, WRONG-SECTION or NOT-FOUND, each with the passage;
- whether any wage line names the housekeeper or the house steward.

Its reply is kept as `extraction/check.md`.

## D7 - the questions (FR-006)

Written in a page session, each tagged `subject=comparative,money; setting=city; level=counts-and-measurements`, with no
drawing page. Each opens with an intro: a comparative question, read as a yardstick, never the setting's own figures.
- "What did a Regency English household pay its servants?" Wages by post, from the checked rows.
- "How did a Regency English household divide its income?" The expense table and the servants each income kept.
- "What did provisions and household goods cost in Regency England?" The book's prices verbatim with units; each item
  the asker named and the book does not price is SILENT.

## D8 - the answer (FR-007)

A comment on EliAndrewC/diagram#2: per question, the fragment FILE, the verdicts, and what is open; the extraction check's
result per row; the edition and page of each figure.

## T - the order

1. The vocabulary, build check and test (D1, D2).
2. The guidelines and contract (D3, D4).
3. The source and the archive (D5).
4. The extraction check (D6).
5. The questions: write, then check (D7).
6. The implementation check: a "no code implements it" line per question.
7. The answer (D8).
8. Report, `make done`, and land (GATED).
