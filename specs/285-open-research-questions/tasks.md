# Tasks - feature 285, the open research questions, derived from the record

Spec: [`spec.md`](spec.md). Plan: [`plan.md`](plan.md) (D1-D7).

- [x] T01 The collector `scripts/_open_questions.py`: question fragments and notes (D1, D2), the three routes to a map feature (D3), the guesses outside the record (D7), the report with its counts (D4) (FR-001-FR-005, FR-007)
      research: rendering
      verify: DONE. DONE. scripts/_open_questions.py: fragments and notes (comments stripped, GUESS or GUESSES per sentence, absence notes with their claim, settled marked), the three routes to a map feature, the guesses outside the record (logs skipped), counts first; R4: 403 questions, 139 guess sentences, 580 absences, 122 lines outside, 2.0 s
- [x] T02 `make open-questions` in the skill's Makefile (D4; FR-001)
      research: rendering
      verify: DONE. DONE. make open-questions in the skill's Makefile (help in lower case so it does not list itself)
- [x] T03 Tests `tests/tooling/test_open_questions.py` on plain inputs and on the real record; timed (D5, D6; FR-006, SC-001-SC-004)
      research: rendering
      verify: DONE. DONE. tests/tooling/test_open_questions.py, 8 passing: plain-input fixtures for every item kind and route, the rewrite removing one item, and the real tree (rack length through 505, the postern in compound.py, all 149 labels listed, under 10 s)
