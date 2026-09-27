# Handoff - feature 250, page `cities/government`, session 1 -> session 2

Saved pages: `/tmp/l7r-check/cities-government-pages/a` (ja 稲荷神社, en Inari shrine, kotobank 人宿) and `/b`
(en Daimyo, ja 廃藩置県, ja 大名, en Abolition of the han system, ja 藩校). One `source-reader` read all three items.

## Changed questions

- SECTION=020 - "The vermilion shed is an Inari form": **citation**, new note `inari-jinja-jawiki` (vermilion on
  shrine buildings and torii symbolizes Inari; the gloss says the page speaks of no wayside shed). The absence note
  after the sentence is unchanged.
- SECTION=070 - "~260 domains": **citation**. Rewritten as "nearly every domain had one [hanko-jawiki-4] - of the
  261 domains still standing when they were abolished in 1871 [han-abolition-enwiki]". The source-reader found no
  count for late Edo itself (ja 廃藩置県 gives 274 daimyo in 1869; en Daimyo gives ~200, not cited); the gloss says
  the figure is a round order of size.
- SECTION=080 - "hired out of the merchant quarter through labor brokers": **citation**, after a rewrite. No page
  says the brokers were in the merchant quarter (source-reader: NOT-FOUND). The sentence now says what kotobank 人宿
  supports: "hired for wages from peasant and townsman households, more and more through placement brokers, a trade
  that grew up with the cities" [kotobank-hitoyado]. The `buke-hokonin-wiki-4` gloss no longer refers to the removed
  phrase.
- SECTION=081 - NEW, split from 080 to bring it back under the size cap (it reached 21,059 bytes):
  "How was a samurai household's live-in staff hired?". It holds the hiring sentence and its five notes
  (`buke-hokonin-wiki-2`, `kotobank-degawari`, `kotobank-hitoyado`, `buke-hokonin-wiki-3`, `buke-hokonin-wiki-4`,
  moved verbatim). 080 now points to it and has dropped `kotobank-degawari` from its roster. The clause "so a castle
  town's servant population is partly recruited from the chonin-chi" now stands as its own sentence, still on
  `buke-hokonin-wiki-3`. 080 is 15,587 bytes and 081 is 6,450.

## New or changed registry keys

- KEY=inari-jinja-jawiki (new, 9270)
- KEY=han-abolition-enwiki (new, 9280)
- KEY=kotobank-hitoyado (new, 9290)
- KEY=kotobank-degawari (changed: a doubled phrase in "Why it applies" removed)

## FR-006

- none owed.

## Open, for session 2

- quote-check and record-format on SECTION=020, 070, 080 and 081. Run source-applicability on the three new keys
  and the changed one.
- The body of 080 changed and 081 is new. If a class's `Entry:` names 080, `scripts/_entry_owed.py` will name it
  for `entry-drift`.
- `make record` and `make citations` ran, and the four named test files pass (257). The size check is clean.
