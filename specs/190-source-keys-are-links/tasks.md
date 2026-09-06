# Tasks - feature 190

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Every task is `research: rendering` - a form change to the record (a link around a citation that already exists); no finding changes. T01c reads pages, but to record WHERE a document already cited can be read, not to decide anything about how a place was built.

- [x] T01 FR-001 to FR-004: the scripted sweep - every registry key in a research file, Sources paragraph or prose, becomes a link by the citation-line rule; dry-run counts first (459 sites; 418 document / 41 registry; 70 of 86 re-pointed)
      research: rendering
      verify: DONE. the dry run reproduced the spec: 459 sites, 418 -> the document, 41 -> the registry, 70 of 86 re-pointed; written by sweep190.py; the GM's example line homesteads.md:806 is a link to the paper (doi.org/10.1080/13467581.2021.1972810)
- [x] T01b FR-006 (i): the DERIVED surface (`surface190.py`: 356 candidates over 18 files, a verdict per candidate, fails on a missing one) - the 130 registered names wrapped in links by the citation-line rule; the 75 names recorded and left plain
      research: rendering
      verify: DONE. surface190.py: 356 candidates (35 keyless Sources paragraphs, 98 keyed ones naming a page in prose, 223 body lines), a verdict each, MISSING and STALE empty; 131 registered names linked (119 document / 12 registry), 75 recorded plain; the derivation masks the sweep's own links (5 artifact lines on the first apply)
- [x] T01c FR-006 (ii)/(iii): the `source-reader` passes (34 documents dispatched 2026-09-06 in three passes, all returned: 25 READ, 7 SUMMARY-ONLY, 2 NOT-FOUND; 6 more turned out registered - D7); READ -> a `SOURCES.md` entry + link; SUMMARY-ONLY -> an entry labeled so + a registry link; NOT-FOUND -> plain with "(URL not found 2026-09-06)"; the three corrections recorded in their entries and reported
      research: rendering
      verify: DONE. 34 documents in three reader passes: 25 READ -> entries, 7 SUMMARY-ONLY -> entries labeled so, 2 NOT-FOUND (Tonami institute 1996; the Kishu J-STAGE study) -> plain + '(URL not found 2026-09-06)'; 6 more found already registered by the percent-decoded URL check (D7); 32 entries appended; the 農業全書 year (1697), the FAO chapter name and the Fengshui-woodland figures recorded in their entries for the GM
- [x] T01d FR-006 (iv) / D9: the author-surname pass (`names190.py`, the index derived from the registry's person-pattern citation lines; 70 occurrences, a verdict each; first mention per section links)
      research: rendering
      verify: DONE. names190.py: 83 surnames derived from person-pattern citation lines (+ the kanji-line key rule), 70 occurrences, verdicts complete: 33 linked (27 document / 6 registry), 18 repeat, 10 coincidence, 2 pair, 6 already wrapped by T01b; 'Wang & Ochiai surveyed' links to the paper
- [x] T02 FR-005 / D6: the test in `tests/interactive/test_sources.py` - every key linked, the target by the citation-line rule (one classifier body, imported), no duplicate `### ` heading
      research: rendering
      verify: DONE. tests/interactive/test_sources.py: the classifier body (citation line, D5), every key linked with the right target (459 checked), no duplicate heading; RED on one unwrapped key (checked by hand on homesteads.md:806 and restored), green after; make quick 254 passed
- [x] T03 FR-006b: `research/CLAUDE.md` paragraph; README line reported
      research: rendering
      verify: DONE. research/CLAUDE.md 'Every reference is a link' section inserted before the page-side pointer; README.md line 44 (the entry template) is the GM's to edit
- [x] T04 push (research docs + a test: DIRECT, no gate owed); the answer to the GM with D1/D5 and the residue
      research: rendering
      verify: DONE. route DIRECT (research docs, a test, specs); pushed via sync-with-main.sh done; the GM's example line on GitHub is a link - verified after landing
