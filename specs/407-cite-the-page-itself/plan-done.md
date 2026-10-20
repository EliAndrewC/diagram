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

<!-- plan-archive: archived 2026-10-20 -->
### T02 Approach

1. Goal: each Morisada, Gamble and Bochum footnote opens the page or spreadsheet its passage is printed on.
2. Constraints: test_sources (may_link); quote-check READABLE, VERBATIM, SUPPORTS on the linked page; the round cap.
3. Sources: the links G (the GM, 2026-10-19); the checks G (constitution XII, features 194-195); a note links the koma its
   passage begins on O (ours, where a passage runs over two koma).
4. Holds: a note whose passages sit on different pages of different files is split by page, so each link carries its
   passage (0275's Bochum note).
5. Order: re-point, then check on page images and row dumps (the agents cannot run the NDL viewer or decode .xls), then fix.
6. Exits: (e) conform, with (b) a split where one link cannot carry a note's passages.
7. No search loop.
8. Budget: an hour, with two check rounds.
9. Done: every re-pointed note READABLE, VERBATIM and SUPPORTS on its page; make record-owed 0 unanswered.
10. n/a.
11. n/a.

<!-- plan-archive: archived 2026-10-20 -->
### T03 Approach

1. Goal: the feature lands on main with its report.
2. Constraints: the review gate, the ledger, page-check and hooks-test before the push.
3. Sources: all G (CLAUDE.md's stop-work procedure).
4. Holds as written.
5. Order: report, tick, gates, land, then the note on #9.
6. Exits: (e) conform.
7. No search loop.
8. Budget: 15 minutes.
9. Done: the push lands; origin/main carries 407.
10. n/a.
11. n/a.

