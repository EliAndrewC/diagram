# Brief - feature 352, did a village lane ever run between a house and its own grove? Session 1: write

You are a FRESH session for the record edits of one feature. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`/diagram/.clones/diagram-research`); the project's CLAUDE.md files apply to
you, the research record's `CLAUDE.md` above all.

**What the GM asked** (2026-10-10, 2026-10-11): do the research a reviewer of feature 287's woods left owed, and record the
answer or its absence. A reviewer found dooryard-copse crowns whose nearest farmhouse stood across a lane; our maps keep
every lane off a household's reserved copse seats (feature 287, woods W25), but no research page asks whether a real village
lane or path ever ran between a farmhouse and its own homestead grove. Research features annotate the record; they change
no map and no code.

## Your items (one question; a new registry key only where a source is cited)

- **0036** (`research/questions/0036-groves-of-trees-around-farmhouses-yashikirin.*`):
  1. **The search.** The archive first (`make archive-find TERMS="..."`, one term per call, then each hit's archived text),
     then the web: in Chinese (the setting's first reference - a fengshui wood or a homestead grove behind a house, 屋后林,
     风水林, 宅旁林, and a lane or path, 巷, 路, 小道, running between them) and in Japanese (屋敷林, 居久根, 築地松, 散居,
     and 道, 小道, 路地 between a 主屋 and its 屋敷林), and in English (the scholarship on yashikirin, dispersed settlement and
     Chinese village fengshui woods) - the languages are where to look, not a limit. What you want: does any account or plan show a lane or path running
     between a farmhouse and its own grove (the grove on the far side of a way from its house), or say the grove stood
     against the house with no way between; and does any say a village way passed through a household's grove?
  2. **The record.** On the findings page (`.html`), under a heading a reader would ask (for example "Did a lane ever run
     between a farmhouse and its grove?"), state what you found, each assertion footnoted to a passage quoted verbatim from
     a page the reader can open (in English translation, marked as one), or - where the sources are silent - an absence
     note (`...-absence`) whose HTML comment names every search and archive term you ran. On the drawing page
     (`.drawing.html`), one sentence on how our maps settle it: a household's copse seats are reserved beside its house and
     kept free of lanes (feature 287, woods W25), so no lane runs through a household's own wood share; label it with the
     finding (attested, a guess, or a convention).

Keep the question under the 20,000-byte cap. Change nothing else, and edit no modal, sheet or code.

## The procedure (session 1: write)

1. Claims: `make research-claims Q="0036"`. If another session holds it, stop and say so in your handoff. Else
   `make research-claim Q="0036" FEATURE=352`.
2. Search as item 1 says; for each page you would cite, `make archive-find URL=<u>` first, then `make source-pages`, then
   the `source-reader` agent from a bundle on the passage. A new source takes `make reserve KIND=registry KEY=<k>` and its
   registry write-up.
3. Edit the fragments (never a built page), then `make record && make citations` and the record tests
   (`make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py"`).
   Commit with a message opening `352: `.
4. Write `specs/352-village-lane-ever-run-between-house/briefs/m1-handoff.md`: one `- SECTION=0036/<id>` line per changed
   heading, then a sentence naming what was found. Release the claim
   (`make research-claim Q="0036" FEATURE=352 STATUS=done`). Do not push. Your last message is one paragraph.
