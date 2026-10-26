# 424-record-intro-maps-money - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-25 -->
## T01 - the opening (FR-001, FR-002)

### T01 Approach (checklist part A)

1. **The goal, in the world.** A reader arriving at the record's home page is told first what the research is for - the maps and
   the money pages, each a link - before the whole-record link and the contents.
2. **The constraints.** Both URLs exactly as the GM gave them; the whole-record link kept, after the opening; the words in the
   record's data, not Python (Acceptance 3); nothing claimed the record does not do (Acceptance 4).
3. **Where each comes from.** O: `request.md`; the spec's FR-001 and FR-002.
4. **Do they describe the world here?** Yes: map modals link the record's questions (`interactive/sources.py`), and gm-assistant's
   money pages cite record questions (diagram#17, #18).
5. **The order.** Data and code with their tests, then the record build, then the gated landing.
6. **The exits.** None.
7. **The search smell.** None.
8. **The budget.** Minutes of code; one `make done`.
9. **Done, measured.** The record tests green; `make record CHECK=1` clean; `make done` green at the landing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** The opening is `contents.json`'s top-level `opening`, HTML text, read by `contents.load_opening` (absent: no opening; not
  a string: refused by name). Rendering: none.
- **D2** Its words: the maps (settlement maps and building plans whose features link the questions here) and the money pages
  (what things cost in Rokugan, read from Edo Japan and Qing China, citing the prices, wages and coin rates here), each linked;
  then one sentence on how a question answers (the quoted passages, and where history is silent or guessed). Rendering: none.
