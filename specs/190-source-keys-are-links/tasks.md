# Tasks - feature 190

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md).

Every task is `research: rendering` - a form change to the record (a link around a citation that already exists); no finding changes. T01c reads pages, but to record WHERE a document already cited can be read, not to decide anything about how a place was built.

- [ ] T01 FR-001 to FR-004: the scripted sweep - every registry key in a research file, Sources paragraph or prose, becomes a link by the citation-line rule; dry-run counts first (459 sites; 418 document / 41 registry; 70 of 86 re-pointed)
      research: rendering
      verify: the dry-run counts match the spec; `git diff --stat` touches only research files; the GM's example line (`wang-ochiai-2022`) is a link to the paper
- [ ] T01b FR-006 (i): the DERIVED surface (`surface190.py`: 356 candidates over 18 files, a verdict per candidate, fails on a missing one) - the 130 registered names wrapped in links by the citation-line rule; the 75 names recorded and left plain
      research: rendering
      verify: the script's counts equal the spec's; MISSING and STALE both empty; a spot check of a keyed-paragraph name (326-woods) and a body name (an Okayama museum)
- [ ] T01c FR-006 (ii)/(iii): the `source-reader` passes (32 documents dispatched 2026-09-06, all returned: 24 READ, 6 SUMMARY-ONLY, 2 NOT-FOUND; 6 more turned out registered - D7); READ -> a `SOURCES.md` entry + link; SUMMARY-ONLY -> an entry labeled so + a registry link; NOT-FOUND -> plain with "(URL not found 2026-09-06)"; the three corrections recorded in their entries and reported
      research: rendering
      verify: every one of the 32 has a verdict recorded; no new entry duplicates an existing URL (percent-decoded check) recorded; no URL written that was not fetched
- [ ] T02 FR-005 / D6: the test in `tests/interactive/test_sources.py` - every key linked, the target by the citation-line rule (one classifier body, imported), no duplicate `### ` heading
      research: rendering
      verify: green on the swept tree; red when one key is unwrapped and when a heading is duplicated (checked by hand, then restored)
- [ ] T03 FR-006b: `research/CLAUDE.md` paragraph; README line reported
      research: rendering
      verify: read back
- [ ] T04 push (research docs + a test: DIRECT, no gate owed); the answer to the GM with D1/D5 and the residue
      research: rendering
      verify: `make quick ALL=1` clean; landed; the GM's example line on GitHub is a link
