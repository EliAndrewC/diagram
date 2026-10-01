# Feature 301 - research (measurements behind the plan)

Every figure here is a one-shot observation, dated, with its method.

## R1 - what the in-memory assembly costs

Observed 2026-10-01; method: `time make record CHECK=1` in the clone (assembles all 38 pages and their citations
pages in memory and compares): 1.15 s wall; `make citations CHECK=1` 0.43 s. A reader that assembles on demand
pays about a second once per process, which is what lets every reader leave the built files.

## R2 - who reads a built page today

Observed 2026-10-01; method: grep over the engine, `scripts/` and `tests/` for reads of `research/<page>.html`,
`research/citations/`, `SOURCES.html`, `record_pages`, `research_pages`, `_parsed`. Engine: `interactive/sources.py`
(modal questions, sources, registry), `interactive/citations.py` (`derive` reads the citations page and the
registry from disk), `record/store.py` (`check`, `write_pages`, page enumeration by `os.listdir`). Scripts:
`_quote_verbatim.py`, `_record_prepass.py` (the registry keys), `_entry_owed.py` (git diff of page files and
`sources._parsed`), `_hm_record.py` (the merge driver for page files), `gate-stamp.py` (the browser key's path
patterns). Tests: about 20 files under `tests/interactive/` and `tests/tools/`. Most scripts already read
fragments (`_check_bundle.py`, `_sources.py`, `_translation_owed.py`, `_open_questions.py`).

## R3 - why the navigation is data, not markup

Observed 2026-10-01; method: arithmetic over the record's counts. The registry holds 920 entries; a sidebar
expanding the registry on each of its 920 small pages at ~90 bytes a link is 920 x 920 x 90 B, about 76 MB of
repeated markup per build. One `nav.js` holding the tree once is about 0.2 MB.

## R4 - a note can be written beside another question of its page

Observed 2026-10-01; method: reading `record/store.py` (`read_notes` merges every question's notes file of a page,
and `write_notes_fragments` placed each note beside the question that FIRST cited it). A later question citing the
same note finds it in the earlier question's notes file, so a small page's notes are looked up in its page's
merged notes, not in its own notes file alone.

## R5 - the pointers

Observed 2026-10-01; method: `git grep -ohE "research/[a-zA-Z/-]+\.html|SOURCES\.html"` outside `research/`:
2,507 occurrences in ~430 tracked files (specs 186 files, engine Python 116, other docs and skill files 66, tests
43, scripts 11, JSON 7, docs 3). `Entry:` lines: 162 in 14 files. The heading ids of the 473 questions are unique
across the record (no basename repeats among the question fragments).

## R6 - the history

Observed 2026-10-01; method: `du -sh` on `/diagram/.git` (236 MB, 36 packs, 17 MB loose); a scratch `git clone
--mirror` then `git gc --aggressive --prune=now` (102 MB); the same mirror after `git filter-branch` removing every
assembled-output path from all history, then the same gc (85 MB, an upper bound - it also removed the pre-258
versions, which were the hand-written source). Commits touching the assembled paths: 1,198 since `0fef1e6f3`
(feature 258 stages 1-2), 155 before.
