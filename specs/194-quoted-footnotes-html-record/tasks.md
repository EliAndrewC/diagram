# Tasks - feature 194

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Part 1 and Part 3 are `research: rendering` (a citation form and a page form). Part 2's backfill is
`research: physical` in the constitution's sense - it reads sources about how places were built - and each
backfill task carries the three boxes.

- [x] T01 FR-001/FR-004 (runs AFTER T04 - the exemplar is authored in HTML): the footnote form and the mechanical test (`tests/interactive/test_footnotes.py`); a worked section footnoted by hand as the exemplar (the farmstead fixtures entry: the coop's sources, one footnote each)
      research: rendering
      verify: DONE. the mechanical test tests/interactive/test_footnotes.py (every reference resolves, every definition referenced with a key link and a quotation, every roster key quoted in its section - a section runs to the next heading of the same or a higher level; a second reference to one note carries no id); RED on the unconverted record (86 roster keys unquoted in 12 pages) and on a footnote without its key link (capitals fn-102), green after; the exemplar is the farmstead fixtures entry of homesteads.html - the coop's four sources each footnoted with their quote
- [x] T02 FR-003: the `quote-check` agent; run it on the exemplar section and record its verdicts
      research: rendering
      verify: DONE. .claude/agents/quote-check.md (Sonnet; VERBATIM/DIFFERS/NOT-ON-PAGE/UNFETCHABLE x SUPPORTS/PARTIAL/DOES-NOT-SUPPORT, per-section unfootnoted assertions; a dash-to-hyphen or British-to-American normalization by the house-style guard is not a difference); run over every page after the backfill - verdicts recorded under T06
- [x] T03 FR-005: the rule in `research/CLAUDE.md`, root `CLAUDE.md`, the constitution (XII, v2.17.0); README reported
      research: rendering
      verify: DONE. research/CLAUDE.md gains 'A reference QUOTES the passage it rests on' and 'The record IS HTML'; root CLAUDE.md's research bullet gains 'And QUOTE what you cite'; constitution v2.18.0 (Principle XII, QUOTE WHAT YOU CITE); tests/test_task_research_boxes.py learns the fourth box from feature 194 on; README.md line 44 and its link table are the GM's - reported
- [x] T04 FR-009/FR-010/FR-011: the one-time conversion of the 15 record files and the registry to hand-authored HTML (scripted, checked, `git mv`; the `.md` deleted); `research/assets/record.css` + `record.js` (the hover); README and CLAUDE.md not converted, the README's link table reported
      research: rendering
      verify: DONE. 16 files converted by convert191.py (python-markdown as a throwaway tool; the .md deleted by git mv; every heading id equals github_anchor - 553 sections re-read identically by the new parser; tables, links, SOURCE blocks and quotes checked per file; 30 links into settlements/ and the skill's buildings.md kept as .md); research/assets/record.css + record.js (hover, click-to-jump, Escape, viewport clamp); the 19 unbalanced links feature 190 wrote to URLs with parentheses repaired first
- [x] T05 FR-012/FR-013/FR-014: `sources.py` reads the HTML; `_ENTRY_FILE` and the 51 class entries name `.html`; the scripted pointer sweep by FR-013's resolution rule (the count recorded here) and its three-part test; the maps link locally; feature 190's link test and the roster tests on the HTML surface; the guards' scope checked; docs
      research: rendering
      verify: DONE. sources.py reads the pages (_parsed on <h2>/<h3> ids, the <p><strong>Sources:</strong> roster, SOURCES.html entries); _ENTRY_FILE and the 51 class entries + place.py name .html; RESEARCH_PAGES = ../../../research/ and RESEARCH_URL retired; sweep191.py by the resolution rule rewrote 574 tokens in 124 files (plus 3 on a second run) - the frozen manifests and the 189 fixture included; tests/interactive/test_record.py holds the three-part FR-013 test; the guards act on any edited text so .html is in scope; interactive/CLAUDE.md and research/CLAUDE.md pointers updated; make quick 432 passed
- [x] T06 FR-006/FR-007: the backfill, file by file (15 record files, one agent each), then `quote-check` over every file, then the fixes
      research: physical
      - [ ] research pass
      - [ ] source-reader confirmed
      - [ ] recorded and cited
      - [x] quote-check confirmed
      verify: DONE. 15 gather agents (one per record file, reports in the session scratchpad) -> 722 footnotes placed by applyquotes191.py; 15 finisher agents quoted or dropped the 86 roster keys left unquoted, made the readers' corrections (Shibata 7.3 m, Suganuma, Hikone 290,000, the rice share 25 percent, the tanning soak 'several days', the coppice cycle, Tabayashi 1987 ...), labeled unsourced assertions; then quote-check over every page (15 reports) and 9 repair agents acted on every DIFFERS / NOT-ON-PAGE / DOES-NOT-SUPPORT: 22 footnotes removed and their assertions labeled, quotes made verbatim, sub-pages named, misplaced markers moved, two sentences the finishers had noted but left standing corrected. Final: 780 footnotes on 15 pages, every roster key quoted in its section. research pass = the gather reports; source-reader confirmed = the readers' READ verdicts; recorded and cited = the footnotes; quote-check confirmed = the 15 check reports and the repairs. Residue: paywalled hosts (springer, sciencedirect, mdpi, wiley, tandfonline, jstor, baidu, zhihu) stay UNFETCHABLE in their footnotes with the registry's passage
- [x] T07 FR-008: the answer to the GM - contradictions found, the residue, D2's ruling; push (GATED: engine code)
      research: rendering
      verify: DONE. pushed on the GATED (local-gated) route after the green make done on the merged tree; the answer to the GM lists the contradictions the readers found, the residue, D2's ruling (the record converts; GitHub shows the pages as source), the guard's dash and spelling normalization inside quotes, and the renumber from 191 to 194 after a concurrent claim
