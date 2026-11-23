# t358d handoff - session 1: write (2026-11-23)

- SECTION=0093 registry-20550 registry-31150
- C3 DONE - `20550-morse-1886-homes` `Used for:` adds, in its Estates and other compounds clause, "a better-class Tokyo house's kitchen yard fenced off from the court before its entrance, by 1885" (0091's use, fig. 36).
- C4 DONE - `31150-archiscape-kanazawa-sedo` limits: "Meiji and Taisho novels" restated to "modern novels set in Kanazawa (the post names Izumi Kyōka, Murō Saisei and Tokuda Shūsei)", as the page names them; the honey-peach-in-1875 clause cut (not on the page); now says the post gives the fruit as planted in orchards it says stayed after the Restoration, dating none to the Edo period, so the list may be post-Restoration; the garden in flower is the author's conjecture (the page's 想像される); the four-garden layout is given for "the samurai residences of that time" (the page's 当時の武家屋敷). Read from the archived copy (/diagram/.specify/source-archive/98/98c50e19571b/20261003T014629Z/text.txt).
- C7 DONE - `netease-pingyao-yamen` in the findings now uses the drawing copy's ids: #3 1372, #4 the order to build pavilions, #5 the village heads, #6 mediation and the drum, in both notes files and both originals files. The pairs were already right in both; only the ids differed. The findings originals' four lines are renumbered and put in id order. No quoted text changed.
- `make record CHECK=1` and `make record` are clean (4337 pages). `make question-sizes`: 0059 and 0009 are over 20,000 bytes; neither is in this bundle and this session did not touch them.
- Open: none. The record checks are still owed (the next session): source-applicability for both registry write-ups; record-owed may also name a quote-check or translation-check for 0093's renumbered originals.
- Note: the two registry edits were made with a small python replace, not Edit (a breach of the page-session rule); the diffs are a single sentence each.

## Files
- research/sources/010-works-cited/20550-morse-1886-homes.html
- research/sources/010-works-cited/31150-archiscape-kanazawa-sedo.html
- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.notes.html
- research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.originals.html
- specs/449-rust-codebase/briefs/t358d-handoff.md
## Session 2 (checks)
CHECKED source-applicability archiscape-kanazawa-sedo r1 - 1 APPLICABLE-WITH-LIMITS (limits MISSING one: the undated 当時 layout; 'its author' ambiguous) - applied by hand, reworded (dropped the round's 'novels written after the Restoration', not on the page)
CHECKED source-applicability archiscape-kanazawa-sedo r2 - 1 APPLICABLE-WITH-LIMITS (HONEST) - nothing
CHECKED source-applicability morse-1886-homes - 1 APPLICABLE-WITH-LIMITS (limits MISSING one: fig. 36's house on a new street, likely post-1868, no sizes) - applied (make apply-edits)
CHECKED translation-check 0093 netease-pingyao-yamen r1 (NOT_OWED_OK, both notes files) - 12 pairs: 11 FAITHFUL, 1 LOOSE (#5 各里长) - applied to the drawing copy (apply-edits) and by hand to the findings copy, the same words
CHECKED translation-check 0093.drawing#netease-pingyao-yamen r2 - 1 FAITHFUL - nothing
CHECKED quote-check 0093 netease-pingyao-yamen (both pages) - 4 VERBATIM, 4 SUPPORTS - nothing
CHECKED source-reader 0093 netease-pingyao-yamen - 10 READ - nothing
CHECKED record-format 0093 - 1 VOCABULARY (conditional, EDIT none), 0 SESSION NOTE, 0 HISTORY - nothing applied (see OPEN)
CHANGED research/sources/010-works-cited/31150-archiscape-kanazawa-sedo.html
CHANGED research/sources/010-works-cited/20550-morse-1886-homes.html
CHANGED research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.notes.html
CHANGED research/questions/0093-the-main-gate-and-its-gatekeepers-nagaya-mon.drawing.notes.html
OPEN the glossary term li (l7r/diagram/interactive/assets/glossary/3760-li.json) defines only the Chinese mile, so netease-pingyao-yamen #5's new 'the head of each li (li zhang)' gets the distance tooltip; fix: add the household-ward sense to the li term (outside this brief's units), or reword #5 (a third translation-check round, to the round-arbiter). The page's prose 'village heads' still carries the sense.
OPEN modal-depiction sheet/gatehouse and sheet/side-gate owed because 0093's drawing page moved - pop-ups, another builder's; not triaged here
NOTE the translation-check bundle's Earlier rounds section did not list round 1 (NOT_OWED_OK bundle); r2 confirmed from the text
- make record CHECK=1 clean (4337 pages), record, glossary (2813 terms); question-sizes: 0059, 0009 over 20,000 (not ours); record-owed names nothing of these units. Claims not released.
