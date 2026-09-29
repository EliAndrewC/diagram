# Brief - feature 269, group W1 (water kinds): finish the check that was never committed

You are a FRESH session. The W1 check sessions applied source-applicability edits to the water registry entries
(`research/sources/010-works-cited/10490-*` to `10600-*`) and to `research/water/070-*` and its notes, and to the
farm-ditch crossing question, but never committed them; since then `make test-file` fails two tests on water.html
(notes 44 and 46). Work in `/diagram/.clones/diagram-supplemental`; the research record's CLAUDE.md applies.

1. `git -C <clone> status --short` and `git -C <clone> diff` on the water and registry files ONLY (other groups' files
   may be in the tree; leave them alone).
2. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
   Fix what fails on water (read the two notes the failures name and the registry entries they cite; a half-applied
   edit is finished, not reverted, where the diff shows what it meant). Re-run the four tests until they pass.
3. Commit ONLY the water and water-registry files, with `269 W1 check: the source-applicability edits committed, water
   notes 44 and 46 fixed`. Do not push.
4. Append one line to `specs/269-research-backfill/briefs/w1-checks.md` saying what was fixed. Your last message is one
   sentence.
