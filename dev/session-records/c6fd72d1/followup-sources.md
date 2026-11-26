# Feature 449 follow-ups T252-T404: who files them (read-only measurement)

Source: lines "lands before T158" in specs/449-rust-codebase/tasks.md (open) and tasks-done.md (closed), T252 on.
115 lines: 90 closed, 25 open (T374, T375, T378, T380, T383, T384, T386-T404). The first is T254, the last T404.
Numbers T252, T253, T259-T261, T263-T265, T269, T273-T301 have no such line. Read = the line's own words;
the check, kind and in/outside labels were assigned by me from the first ~400 characters of each line, so all of
them are partly (inferred). Outside = the line says OUTSIDE/outside, "PASS sheet" or "nitpick" (keyword, read).
Kinds: D = map or tool defect (wrong drawing, misreading check, crash, flake), R = record or claim restatement,
Q = research question (a pass owed), W = notes or pop-up wording fix.

## 1. Counts
By check (primary finder): building-review 29; impl-drift 24; builder's own observation (incl. lines that name
no check, "found by 449 Txxx") 15; quote-check 9; modal-depiction 6; size-audit 6; modal-form 5; other
(check sessions, page-session leftovers) 5; modal-research 4; research-pass 4; record-format 3; glyph-check 3;
translation-check 1; round arbiter 1. claims-triage, modal-triage, source-reader as primary: 0 (source-reader
appears only as a co-named check on T319 and T344).
By in/outside: outside 43, on the change 72 (inferred from keywords; 37% outside).
By kind: R 44; D 41; Q 17; W 13. Closed: R 37, D 30, Q 11, W 12. Open: D 11, R 7, Q 6, W 1.
Cross, check x kind (D/R/Q/W), then outside count:
- building-review 18/0/8/3, out 13
- impl-drift 7/17/0/0, out 14
- builder-observed 7/7/0/1, out 0
- quote-check 0/9/0/0, out 6
- modal-depiction 1/1/1/3, out 2
- size-audit 4/1/1/0, out 2
- modal-form 0/0/3/2, out 1
- other 0/3/1/1, out 2
- modal-research 0/1/0/3, out 1
- research-pass 2/1/1/0, out 1
- record-format 0/2/1/0, out 1
- glyph-check 1/1/1/0, out 0
- translation-check 0/1/0/0; round arbiter 1/0/0/0 (T377, a tool fault it ruled)
Kind x outside: D 11 of 41 outside; R 23 of 44; Q 8 of 17; W 1 of 13. Restatements are the outside-heavy kind
(52% of R are outside against 27% of D).

## 2. Filings per day (date in each line's parenthetical; 4 undated lines placed by their bundle, inferred)
- 2026-11-22: 78 lines (T254-T272, T302-T372, 4 of them undated and placed here, inferred)
- 2026-11-23: 37 lines (T363, T368-T371, T373-T404; undated T390 placed here, inferred)
Nothing earlier or later: 115 lines in two days. The 22nd carried T302-T372, 71 lines in one day (inferred from dates).

## 3. Cascade (a follow-up filed by the round that closed an earlier follow-up)
Of the 115, 41 name an earlier follow-up number as the bundle, landing, round or task that found them
("the T302 bundle", "after T329", "filed by T340"): 21 on the 22nd, 20 on the 23rd. 65 name at least one
earlier follow-up number anywhere (weaker test). Excluding T254-T272 and T302-T311 (their parents T197, T285,
T289 are below T252), 41 of ~92 later lines is 45% strong (inferred), 71% weak. Largest parents (lines naming
them as the bundle): T371 and T383 bundles (T392-T402, 8 lines), T330 (T344, T345, T347, T350, T363, T371),
T302 (T318-T325, 7), T342 (T362, T364-T367), T312 (T314, T320, T329, T330, T334). The cascade has depth:
T312 -> T330 -> T363 -> T371 -> T392/T393/T394/T396/T399/T400 (inferred from the lines' own references).
The one measured loop: T328 (road bands removed) -> T342 (drawing page still says it) -> T362/T364-T367.

## 4. Top five checks, defect against restatement
1. building-review 29: 18 D (62%), 0 R, 8 Q, 3 W; 13 outside.
2. impl-drift 24: 7 D (29%), 17 R (71%); 14 outside. The restatement engine.
3. builder's own observation 15: 7 D, 7 R, 1 W; none outside (all are on what the builder just did).
4. quote-check 9: all R (100%); 6 outside.
5. tied at 6: size-audit (4 D, 1 R, 1 Q) and modal-depiction (1 D, 1 R, 1 Q, 3 W).
Top five (six with the tie) = 89 of 115 lines (77%). Across all 115: defects 41 (36%), restatements 44 (38%),
research questions 17 (15%), wording 13 (11%). Of the checks that file defects, building-review and
size-audit are the main sources (22 of 41 D); impl-drift and quote-check together file 26 of 44 R.

## Caveats
- "Outside" is a keyword read; T330, T305, T363 mix kinds in one line (labeled by main clause).
- Open lines T374-T404 are all dated the 23rd: that day's 37 are still mostly unworked (open 25 of 37).
- No line names claims-triage; source-reader / glyph-check are rare finders. The bundle number is read where a
  line writes "the Txxx bundle's ..." only.
