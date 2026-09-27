# Handoff - feature 250, page `cities/fabric` (T55), session 1 of 2

Written 2026-09-26. Checks NOT run, nothing ticked, nothing pushed.

## Changed questions

- `SECTION=040` (where does the Imperial road run through a city) - item 2
- `SECTION=050` (what lines the Imperial road) - item 3
- `SECTION=140` (how did a dense wooden city watch for fire) - SPLIT; keeps the tower, the walled/open line, whose watch, dispersal, conventions and the rule
- `SECTION=143` (why does an unwalled seat draw no fire tower) - NEW, split from 140: the jin'ya-town paragraph and the "what an unwalled seat draws instead" decision, with their ten notes (the old absence note `how-did-a-dense-wooden-city-watch-for-fire-3` is now keyed `why-does-an-unwalled-seat-draw-no-fire-tower`, text unchanged)
- `SECTION=146` (did a Chinese city watch for fire the same way) - NEW, split from 140: the Kaifeng/Wanping paragraph with its two notes, and item 1

What each part relies on from the others: 143 and 146 each rely on 140 only for the line between the walled city and the open town (a link, no restated evidence); 140 points at both in one sentence and relies on neither for any claim.

## New registry keys

- `KEY=l7r-budgets` (`sources/010-works-cited/9300-l7r-budgets.html`) - the GM's `budgets.md`, canon; linked `../../SOURCES.html#l7r-budgets` from the notes, `../SOURCES.html#l7r-budgets` from the rosters
- `KEY=xiancheng-zhwiki` (`sources/010-works-cited/9310-xiancheng-zhwiki.html`) - zh.wikipedia 县城, read by source-reader 2026-09-26

## Items (FR-002)

1. "A Chinese county seat was walled in any case..." (now in 146) - **CITATION** `xiancheng-zhwiki`. The sentence was an overclaim and is rewritten: walls discouraged inland under the Song, an estimated two-thirds and more of county seats walled by the late Ming, the great majority by the end of the Qing. The join to 140 is a link.
2. "An Imperial road is Imperial property ... the city maintains." (040) - **CITATION** (canon) `l7r-budgets`, `l7r-budgets-2` + **GROUNDS** (`this project's decision`). The notes never call the road Imperial property and say nothing of the stretch inside the walls (source-reader grepped the whole file), so the sentence now says what the notes do say (upkeep funded from the central treasury; the domain's own roads kept by daimyo, governors, magistrates) and labels the city-street reading as this record's decision.
3. "...merchant and artisan households are about a quarter..., the highest commercial share of any tier" (050) - **CITATION** (canon) `l7r-budgets-3`. Rewritten: the capital has the same 25% (so not "the highest"), and the notes never count artisans as merchants, so "and artisan" is dropped; now "the same share as a domain capital's and two and a half times a town's".

## FR-006

- none on this page.

## Open

- A modal whose `Entry:` names 140 for the jin'ya/unwalled-seat or Chinese material now finds it in 143/146; `scripts/_entry_owed.py` should name any such pair at push - session 2 should run it.
- Two paragraphs of 140 were removed with a line-deleting `sed` rather than `Edit`: the house-style hook rewrote "gaol" to "jail" inside the Edit's match text, so no Edit could match them. In 143 the word is now "jail" (paraphrase, not a quotation).
