# Tasks - feature 196

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

- [x] T01 FR-001: the research pass - Opus readers over Chinese/English surveys, Hong Kong fung shui woods, Korean/Japanese analogues; candidates with URL, readability, verbatim figures
      research: physical
      - [x] research pass (five Opus readers 2026-09-07: English scholarship + analogues, Hong Kong, mainland Chinese x2 - the first stalled on a Chinese host and was relaunched with one attempt per host, the second ran out of search budget; the GM's five downloads; verdicts in the session transcript and findings.md)
      - [x] source-reader confirmed (the readers returned verbatim passages with page or section; the AFCD Annex arithmetic recomputed independently by the session and again by the quote-check)
      - [x] recorded and cited (vegetation.html fengshui section: eight new footnotes fn-69 to fn-77, seven registry entries, roster complete)
      - [x] quote-check confirmed (four Opus rounds, 2026-09-07: round 1 over the whole section - 12 VERBATIM, 1 DIFFERS fixed, 3 NOT-READABLE fixed (wrong article ids), 5 PARTIAL glosses closed; round 2 - 24 passages VERBATIM, 4 place-name PARTIALs closed with one more quoted clause each; round 3 read a stale file; round 4 fresh - every quotation VERBATIM, every footnote SUPPORTS, the one PARTIAL gloss trimmed)
      verify: DONE. Hong Kong AFCD NCSC 9/06 (115 woods, GIS areas) is the one large measured distribution; Korea (Park 2013, Kweon and Youn 2021) the water-mouth analogue; the mainland passes surfaced only unread leads (listed in findings.md)
- [x] T02 FR-002 / FR-003: the fengshui-forest section rewritten from the findings under the 195 rule; registry entries; quote-check over every new footnote
      research: physical
      - [x] research pass (T01)
      - [x] source-reader confirmed (T01)
      - [x] recorded and cited (the section states each figure with a quoted footnote or labels it GUESS; test_footnotes/test_sources/test_page green)
      - [x] quote-check confirmed (T01)
      verify: DONE. round 1 of the Opus quote-check: 12 VERBATIM, 1 DIFFERS (Coggins wording - fixed to the page's), 3 NOT-READABLE (two ScienceDirect links carried the wrong article ids - re-pointed to the pages the GM saved), 5 PARTIAL glosses (each now carries the quote it rested on or the claim was dropped); round 2 over the changed footnotes recorded below
- [x] T03 FR-005: the `Windbreak` and `Copse` explanations and labels brought level with the record (docstrings; the `label` field and its snapshot if the label changes); nothing drawn changes
      research: rendering
      verify: DONE. Windbreak's Why/Note say what the record says (two groves per village, the Hong Kong median, the belt in the upper half of the band, the guesses named); label stays accurate (the size band is measured); Copse unchanged (it cites no size; its Note already says the ground it takes is nowhere given); no drawn size, knob or geometry touched (git diff: no l7r/ file but greenery.py docstring); make page-check green
- [x] T04 FR-004 / FR-006: papers the container could not read reported to the GM during the pass and read from the copies that arrive; findings.md (ranges by type, distance from the drawn sizes, XII's ladder, the download list); push; the answer to the GM
      research: rendering
      verify: DONE. the five-paper download list went to the GM mid-pass (2026-09-07) and all five arrived (one full OA paper, four public excerpts) and were read before the section was written; findings.md carries the ranges by type, the distance table, XII's ladder (back grove: keep; water-mouth and trees: stay GUESS, no knob) and the unread leads; route DIRECT (research HTML, a docstring - page-check green - specs); pushed by sync-with-main.sh done
