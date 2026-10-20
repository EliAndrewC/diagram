# 407-cite-the-page-itself - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-19 -->
### T01 Approach

1. Goal: a reader clicking a Morisada, Gamble or spreadsheet footnote lands on the page or file the passage is on.
2. Constraints: test_sources' first-URL rule (feature 190); feature 195's readable-page rule; the GM's 2026-10-19 rulings.
3. Sources: first-URL rule G (feature 190, "Any reference ... should be a link to that external document"); the new
   permission G (2026-10-19, quoted in request.md); notes-only and citation-line-only O (spec-fidelity round 1's scope).
4. The rule holds: a works section or roster has no single page, so the first URL stays right there.
5. Order: rule and test first, then the notes, then their checks.
6. Exits: (b) a principled exception for the keys the GM named and for spreadsheets - chosen; (e) conform - rejected,
   the GM ruled.
7. No search or packing loop.
8. Budget: 30 minutes for T01.
9. Done: test_a_note_may_link_its_page_or_spreadsheet_and_nothing_else green; the record tests green with the notes
   re-pointed (they failed on the Bochum xls link before, feature 404's landing).
10. n/a: no constant moved.
11. n/a: nothing fitted into room.

