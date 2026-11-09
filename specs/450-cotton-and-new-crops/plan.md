# Implementation Plan: when cotton and other cash crops spread (feature 450, diagram#22)

**Spec**: `spec.md` | **Request**: `request.md` | **Date**: 2026-11-08

## Summary

A research-record feature answering the issue's four questions from five search passes (`passes/a-japan-cotton.md`,
`b-china-cotton.md`, `c-species-india-korea.md`, `d-tobacco-potatoes.md`, `e-tomato-spread-factors.md`). Five write sessions, each
followed by a check-and-apply session, one after another in this clone (`/diagram/.clones/diagram-research`): one queue rather than
431's two clones, because the sources overlap (Kawakatsu, Tanimoto, Zurndorfer, Pelliot, Laufer, Li Xinsheng) and sequential sessions
reserve and reuse a registry key without two sessions naming it twice. Questions 1 and 2 go first, each pair landed on its own, as
the issue orders them. Then the reply on #22. No code, map or canon change.

## Technical Context

- **The passes are leads, not citations**: each write session reads every passage on its page before citing it, through `make
  archive-find` and `make source-pages`.
- **URLs in the passes that are wrong**: pass C prints an English Wikipedia URL beside two archived copies (Tanimoto, archive
  42/4288c884928c; Bishop, af/afb75ffbad3a). The write session takes the source's URL from `make archive-find`, never those.
- **Pass E's three PDFs** (Isono's Keio table, Crosby ch. 5 at Warwick, MAFF Kyushu) were refused by `make source-pages` as having no
  text layer and read by pdftotext, so the session that cites one reads it the same way and gives it to the checks with `IMAGES=` or
  an archive copy.
- **Marked drafts and readings through another work**: Zurndorfer's GEHN papers and Pomeranz 1998 are cited with their headers said;
  Tanimoto as 0312 and 0313 cite it; Nagahara through Yajima and Tanimoto, never as Nagahara; Ho through Crosby; Mazumdar through
  a blog is not cited as Mazumdar.
- **The question count and the write cap**: ten new questions (D1 1, D2 1, D3 2, D4 3, D5 3; each crop its own, so question 3 cannot pass 20,000 bytes of prose).
  Each write takes at most four questions and ten registry keys; `make reserve`'s eleventh key sends the rest to a continuation brief.

## Performance bookends

N/A: no generator change.

## Constitution Check

- I-XI: N/A. XII: the question tasks are `research: physical` with their five boxes. XIII: `make record CHECK=1` and the record tests
  stay green. XVI: built as the spec's FRs.

## D1 - Japan's cotton (issue question 1; FR-001, FR-002, FR-005, FR-006, FR-007)

A new money question, its title asking when cotton became ordinary clothing in Japan. The spec's Japan findings, the five stages in
order each with a verdict; what it replaced and how fast; by region (the cold north against the Kinai) and by class, low-ranking samurai
against peasants and townsmen, with sumptuary rules labeled as ceilings; the GM's direct question answered by region; the two canon
quotations beside it. Per the spec's User Story 1 scenario 2, the six files the request lists (0261, 0274, 0313, 0209, 0006, 0020) are each
named by file where they bear, with 0312 in addition; none is repeated. 0006 and 0020 are named again in D4's crop questions.

## D2 - China's cotton (issue question 1; FR-001, FR-002, FR-005, FR-006, FR-007)

A new money question, its title asking when cotton became ordinary clothing in China, of the same shape as D1, with the frontier and the
Yangzi as separate stages, and the state's part. Points at D1.

## D3 - the species, and India and Korea (issue question 2; FR-001, FR-002, FR-005, FR-006, FR-007)

Two new money questions: one asking whether cotton was a New World crop, which species grew where before 1492 and when the American
kinds came (four countries, each with date and importance, with the GM's point on the 100 years answered); one on when cotton became
ordinary in India and in Korea, with the same five dated stages as question 1 for each country, each carrying one of the four verdicts (India's import stage included, the 19th century's factory cloth searched), and Korea's role, if any, in cotton reaching
Japan, the cloth and the plant each with its verdict. Point at D1 and D2.

## D4 - tobacco, sweet potato, white potato (issue question 3; FR-001, FR-002, FR-005, FR-006, FR-007)

Three new money questions, one per plant, each with per-country dated stages and the lag, China and Japan first; loose plant words kept
as the spec's edge case says. Tobacco's states the canon quotation beside it.

## D5 - the tomato, what set the pace, and the Tokugawa restrictions (issue questions 3 and 4; FR-001, FR-002, FR-005, FR-006, FR-007)

Three new money questions: the tomato per country with the lag and the GM's two positions tested; what historians say made a crop spread
quickly or slowly, with author and crops; whether the Tokugawa restrictions stopped new crops, with the arrivals before and after.

## D6 - the implementation check and the reply (FR-001, FR-003, FR-004)

`implementation-check.md` holds each new question's line (`no code implements it`, with the search). The reply on #22 gives, figure by
figure, the fragment file and the verdict, and what is still open: the unread works the passes name (Nagahara 2004 and Takebe direct,
Hauser, Chao, Dietrich, Xu Xinwu, Ho, Mazumdar, Benedict), and each SILENT. Beside the history the reply states the two canon quotations: cotton is
absent from `setting/l7r.md`'s list of cash crops and named as an ordinary low-tariff good. Anything for the GM goes through
`escalation-check` first, and nothing here edits the canon.

The `make done` route: every delta here is a record edit, so `make land` takes the record's checks; a claims-gate refusal on owed Rust
claims of another feature is taken up when it is seen on a landing.

<!-- plan-archive: T01 to T01 moved to plan-done.md, 2026-11-09 (feature 375 FR-044) -->
### T02 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D2; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T03 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D3; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T04 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D4; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T05 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D5; FR-001, FR-002, FR-005, FR-006, FR-007.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002, SC-003.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a

### T06 Approach (checklist part A)

1. **The goal, in the world.** n/a
2. **The constraints.** D6; FR-001, FR-003, FR-004.
3. **Where each comes from.** The FRs above, from `request.md`.
4. **Do they describe the world here?** Yes.
5. **The order.** n/a
6. **The exits.** Green: landed. Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`.
7. **The search smell.** None.
8. **The budget.** One landing.
9. **Done, measured.** SC-001, SC-002.
10. **Before moving a constant.** n/a
11. **Before fitting things into room.** n/a
