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

Observed 2026-10-01; method: the first build's counts (`ls research/site/sources | wc -l`: 2,127 registry entries,
not the 920 `record/fragments.py` names - that count dates from feature 258) and arithmetic. A sidebar expanding the
registry on each of its 2,127 small pages at ~90 bytes a link is 2,127 x 2,127 x 90 B, about 400 MB of repeated
markup per build. One `nav.js` holding the tree once measured 0.19 MB.

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

## R7 - the landed specs' pointers

Observed 2026-10-01; method: `git grep -lE "research/[a-zA-Z/-]+\.html|SOURCES\.html" -- specs/` less the request
files, then `scripts/spec-lint.py` run on each directory found. 38 landed spec directories carry old-form pointers;
14 of them fail `spec-lint` today (194, 195, 196, 202, 205, 209, 211, 227, 229, 230, 232, 233, 234, 254 - from 2 to
62 findings each, about 250 in all), every finding a rule added after the feature landed (a figure with no
measurement key, a requirement no success criterion names). The push lints every spec directory its delta touches,
with no escape, and also runs the review gate (a FAITHFUL verdict in `spec.md`) and the plan gate (the recorded
plan hash) over them - so rewriting their pointers would mean re-writing fourteen landed specs to today's rules. The
GM chose (2026-10-01) to sweep them and narrow the lint to what a push changes in a spec directory that existed before
it (spec FR-027).

## R8 - the glossary hover on the single page

Observed 2026-10-01; method: Playwright (Chromium) opening `research/site/all.html` from disk, time to the load event
(the deferred scripts run before it), then `document.querySelectorAll('span.gl').length`. The page as first built,
without the glossary: 6.66 s, 0 terms wrapped. A copy with the glossary loaded and every term wrapped at load: 10.79 s,
66,794 terms wrapped - 4.1 s more. With the wrap made lazy (a heading's run, and each note of the Citations part,
wrapped when within 2,000 px of the view): 3.2-3.5 s to load (warm cache; the 6.66 s and 10.79 s runs above were the session's first loads of the page, so part of that gap is the cold cache, and the eager wrap's own cost is the 4.1 s between the two runs taken under the same conditions), 519 terms wrapped at the top, 15,970
after jumping to the middle, 110 in the "Rice paddies and their plots (suiden)" question after scrolling to it.

## R9 - every container mounts the host's ~/.claude

Observed 2026-10-01; method: the host-diagnostics client (`podman-diag ps`, then `podman-diag inspect <name>` for
each running container's mount destinations). Four containers run - claude-diagram, claude-character-sheet,
claude-gm-assistant, claude-bank - and every one mounts `/home/agent/.claude` and `/home/agent/.claude.json` from the
host, so the user-level hook in `~/.claude/hooks/` and its registration in `~/.claude/settings.json` reach each of
them (spec FR-024). gm-assistant's `launch-container.sh` mounts it unless `--no-claude` is given; none of the four was
launched that way. The hook exits silently where `python3` is absent, so a container without it sees no hook error.

## R10 - tripwire seed 33 fails on main as well (pre-existing, ledgered)

Observed 2026-10-01; method: `make maps` in the clone (reference map clean, then the tripwire seeds), then the same
`make maps` in a detached worktree at main's tip (`git worktree add --detach ... origin/main`, constitution XIII). Both
stop at the same refusal: `Tripwire-33 (seed 33): no margin seats its households inside a cluster shape's band`
(`hamletgen/homesteads/stages.py` `seat_every_household`). Feature 301 changes no placement code, and the failure is
the same on main's tip, so it is pre-existing and ledgered here, not fixed under this feature. The pool itself was
regenerated with `make maps SCOPE=all`.

**Fixed 2026-10-01 (observed 2026-10-01; method: `make hamlet` on seed 33 with the houses read from its seating, then the same roll after the fix), after the feature landed, at the GM's request** ("I would indeed like that tripwire seed 33 to be
fixed, even if it was from a pre-existing failure on main"). Measured: seed 33 rolls the linear form (a row village), and
every margin seated all ten households in one straight row about 260 ft apart. `cluster_aspect` measured the houses'
CENTERS, so the row read about 0.2 ft deep and 2,345:1. Two causes, both fixed. (1) The measure: a row is one homestead
deep, so both extents are floored at `BUNDLE_PITCH` (`hamletgen/homesteads/seats.py`). (2) The band: the row then reads
23:1, still past the elongated cluster's 12:1 ceiling, but the research gives a row of ten farms 5:1 to 22:1 (frontage
54-240 ft, `research/questions/0033-row-villages-resson.html`), and `row_rules` governs a row. So the cluster band is
not applied to the linear form (`drawn_in_band`, `hamletgen/homesteads/stages.py`). Seed 33 now rolls OK at 10/10.
Observed and not changed: the row's 260 ft spacing is slightly above the researched 240 ft maximum frontage.
