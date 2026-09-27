# Handoff - feature 250, page `water` (T75), session 1 -> session 2

Saved pages: `/tmp/l7r-check/water-pages` (MANIFEST.txt). One source-reader pass over every item: 10 READ,
5 NOT-FOUND (every NOT-FOUND an absence that was being confirmed), 0 CONTRADICTED. No item is a claim about
the setting, so no canon call was made.

## Check these

- SECTION=010
- SECTION=120
- SECTION=130
- SECTION=170
- SECTION=220
- KEY=suzhou-enwiki (new: `research/sources/010-works-cited/9400-suzhou-enwiki.html`)

No question touched is over the 20,000-byte cap, and none of the over-cap questions (250, 150, 280) holds an
item, so nothing was split.

## FR-002

- **Ryogoku-gawa (130)** - CITATION. The name is on no page read (両国川 grepped on ja.wikipedia 隅田川: only
  両国橋 and similar), so it was dropped from the prose and replaced with the names the page does give, reach by
  reach: Miyato-gawa and Asakusa-gawa around Asakusa, Okawa below Azuma Bridge. `sumida-gawa-jawiki` gains the
  quote 「宮戸川（浅草付近における隅田川の旧称）」. The old absence note and the Sources-line comment are removed;
  `yodogawa-jawiki` moved to the Seta/Uji/Yodo clause it supports.
- **Suzhou's canal grid (170)** - CITATION + ABSENCE. "canal grid" is now "network of canals" (the page never
  calls the canals a grid); `suzhou-enwiki` quotes the network and its links to the countryside; the absence note
  (re-searched 2026-09-27) now sits on that clause for the part no page says - that field ditches drained into
  it. It had been on the night-soil clause, which is covered by `kotobank-shimogoe` at the end of its parenthesis.

## FR-006

- 8 (brook ~2 m, 010 table) - LOCATED. CONFIRMED: absence note `water-width-ladder---the-real-world-tiers`.
- 9 (town river ~20 m) - LOCATED. CONFIRMED: absence note `...-3`.
- 10 (Himeji-tier ~20-35 m) - LOCATED. CONFIRMED: `himeji-castle-jawiki`; the row now reads ~20-34 m / ~65-115x
  (the page's widest moat is 34 m).
- 11 (Osaka-tier) - LOCATED, now "up to ~90 m". CONFIRMED: `osaka-castle-jawiki`. Its multiple was fixed from
  ~250x to ~300x (90 / 0.3), and the stroke paragraph's "about 250 to 1" to "about 300 to 1" with it.
- 12 (tameike ~150-200 m) - LOCATED. CONFIRMED: absence note `...-4`.
- 13 (Himeji ~20 m, max 34.5) - rewritten in the Anchors paragraph as "12-34 m by circuit, the middle moat about
  20 m". CONFIRMED: `himeji-castle-jawiki-2` (all three circuits quoted).
- 35 (hucheng he, 120) - rewritten; worked as FR-002: CITATION. "commonly so: a Chinese seat ..." rested on
  Beijing alone, so the sentence now names Beijing and Edo: Beijing's moats fed from the Jade Spring hill and
  Baifu spring via the Chang River (new first quote in `beijing-chengchi-zhwiki-2`), Edo's outer moat made by
  moving the Hirakawa (`sotobori-jawiki-2`; "spiral" dropped - the page's word is の). zh.wikipedia 護城河 was
  read and says nothing on how moats were filled.
- 36 ("occasionally two", 220) - worked as FR-002: ABSENCE, new note
  `irrigation-topology---one-pond-outlet-that-branches-2` (searched 2026-09-27: the Kagawa page and ja ため池 name
  one intake, a sediment gate, a spillway and several plugs on one riser, never a second intake); "in this page's
  reading" dropped as the note now labels it. Nothing in the engine reads a two-outlet pond.

## Open

- 010's "about 1,700 to 1 once a reservoir is counted" was left as it is: the table's pond is 150-200 m and the
  anchors' 150-600 m, so the ratio depends on which is meant. It is not an item here; the quote-check may raise it.
- The Forbidden City NW-in / SE-out flush in 120 is still SUMMARY-ONLY (the section's own comment); not an item here.
- source-applicability is owed on the new `suzhou-enwiki` write-up.
