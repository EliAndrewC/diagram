# 413-money-tooltip-on-the-record - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-24 -->
### T01 Approach

1. Goal: a reader hovering a marked amount in the record sees what it was worth (goods dollars, wage dollars, Rokugani coin) at
   its era's rates, from gm-assistant's table, and the build refuses a mark that cannot be converted.
2. Constraints: the table's rows and units; the asker's no-fallback answer (#14); the GM's withdrawal of the 25-year default
   (#14: "no numeric threshold in the record checks yet"); gm-assistant's `rokugani()` format; the record build's refusal
   machinery; 100% coverage of the new module.
3. Sources: the table, G (the GM's request through #14); no-fallback, G (the asker, #14, 2026-10-24); the withdrawal, G (the GM
   through #14, issuecomment-6386744961); the Rokugani format, G (gm-assistant's code, the canon's coins); the rounding tiers, O.
4. Holds: as written; a `data-paid` with no year is refused because the tooltip must name where and when the amount was paid
   (the borrowed line), not by any distance.
5. Order: the vendored copy, then the build's reading, then the box text.
6. Exits: (e) conform; (a) the rounding tiers are O and were set to reproduce the issue's worked example.
7. No search loop: a single pass over each fragment's tags.
8. Budget: an hour; it took about that.
9. Done: the money tests green and red without their changes; `make money-conversions CHECK=1` exits 0; `make record CHECK=1`.
10. n/a.
11. n/a.

<!-- plan-archive: archived 2026-10-24 -->
### T02 Approach

1. Goal: the box opens on hover over a marked amount, a line at a time, with the coin's glossary definition under it.
2. Constraints: the record's one hover box (`record.js`); no full-page browser test (GM 2026-09-07); the glossary's wrapping.
3. Sources: the box, O (the record's existing pattern for source labels); the no-browser-test rule, G (2026-09-07); the coin's
   definition beneath, G (the GM's "we don't just explain that this was the copper coin", #14).
4. Holds: as written; inside a note shown in the box, the conversion is the span's title (one box cannot hover over itself).
5. Order: after T01's box text.
6. Exits: (e) conform.
7. No search loop.
8. Budget: half an hour.
9. Done: a built page hovered headless (Playwright) shows the box with the conversion, the borrowed line, the coverage and the
   glossary line, white-space pre-line.
10. n/a.
11. n/a.

<!-- plan-archive: archived 2026-10-24 -->
### T03 Approach

1. Goal: every amount already in the record in a built era's coin is decided - marked with the era its author judges close
   enough, or passed over with its reason - so the tooltip lights where it should.
2. Constraints: FR-006 (record-wide); marking changes no visible words (no record check owed); the GM's withdrawal (no distance
   in years decides anything); gm-assistant's request to mark the Nakasendo fares (#13).
3. Sources: FR-006, G (the issue: "each money amount marked with its era"); the withdrawal, G; the fares, G (gm-assistant for the
   GM, #13 issuecomment-6386826304).
4. Holds: as written; a rate, a weight or an area unit is passed over with that reason, never marked.
5. Order: after T01 and T02, so each mark is checked by the build.
6. Exits: (e) conform.
7. No search loop: one sweep, one decision per amount or per fragment.
8. Budget: two hours.
9. Done: `make money-candidates CHECK=1` exits 0; `make record-owed` names nothing for the marking; `make record CHECK=1`.
10. n/a.
11. n/a.
<!-- plan-archive: archived 2026-10-24 -->
### T04 Approach

1. Goal: gm-assistant can verify the tooltip from the reply alone: how amounts are marked, the awaiting list, the refresh, how
   to check it.
2. Constraints: FR-007; the reply on #14 (issue-watch); the user-level rule that the asker closes the issue.
3. Sources: FR-007, G (the issue's "how diagram vendors the file ... and how amounts are marked are diagram's to decide" asks
   for the decision to be told); closing by the asker, G (the GM's user-level rule).
4. Holds: as written.
5. Order: after T01-T03 landed.
6. Exits: (e) conform.
7. No search loop.
8. Budget: a quarter of an hour.
9. Done: the comment's URL (issuecomment-6387466427).
10. n/a.
11. n/a.

<!-- plan-archive: archived 2026-10-24 -->
### T05 Approach

1. Goal: the feature closed - its report written and every task landed.
2. Constraints: `make feature-report F=413 WRITE=1`; the landing route.
3. Sources: the close procedure, G (CLAUDE.md, "A feature ends with make feature-report").
4. Holds: as written.
5. Order: last.
6. Exits: (e) conform.
7. No search loop.
8. Budget: a quarter of an hour.
9. Done: the report in `specs/413-money-tooltip-on-the-record/report.md`; T04 and T05 landed.
10. n/a.
11. n/a.
