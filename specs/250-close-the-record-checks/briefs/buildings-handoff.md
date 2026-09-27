# Handoff - feature 250, page `buildings` (T02), session 1 -> session 2

Saved pages: `/tmp/l7r-check/buildings-pages` (MANIFEST.txt; `34-nagaokakyo-hurusatofile13.pdf` is the Nagaokakyo
leaflet, read with a text layer). One `source-reader` pass covered every item (13 claims: 6 READ, 7 NOT-FOUND, 0
CONTRADICTED). No item was a claim about the setting, so no `make canon` call was needed. No question is over the size cap.

## Changed questions

- SECTION=010 (administrative-culture-is-japan-first-for-compound-interiors)
- SECTION=070 (a-compound-wall-is-a-building-not-a-boundary-line) - notes only
- SECTION=150 (the-granary-holds-grain-not-just-rice)
- SECTION=170 (fire-water-is-distributed-to-the-halls-not-the-kura)
- SECTION=210 (a-dojo-is-a-city-institution-county-training-is-courtyard-keiko)

## New or changed registry keys

- KEY=thepaper-menhai (new, 9770)
- KEY=nta-nengu-nonyu (new, 9780)
- KEY=nagaokakyo-nengu-jono (new, 9790)
- KEY=daikan-jawiki (new, 9800)
- KEY=xuli-zhwiki (changed: `Used for` line only)

## FR-002 items

| item | section | form | note key(s) |
|---|---|---|---|
| soybean bales / horse fodder | 150 | citation + absence (reworded: a tenth of the tax reckoned in soybeans near Kyoto, paid in silver, is cited; the bales in kind and the fodder motive keep an absence note) | `nagaokakyo-nengu-jono`, `the-granary-holds-grain-not-just-rice` |
| Chinese mixed-grain granaries | 150 | absence | `the-granary-holds-grain-not-just-rice-2` |
| men-hai "gate-sea" | 170 | citation (hedged as the source hedges it, "it is said"; gloss corrected to "the sea before the gate") | `thepaper-menhai` |
| daikansho had NO bugeijo | 210 | absence; the scope paragraph's duplicate absence wording trimmed to point at the note | `a-dojo-is-a-city-institution-county-training-is-courtyard-keiko-4` |
| archive in the yamen | 010 | absence (covers the granary too - neither is on a page read) | `administrative-culture-is-japan-first-for-compound-interiors` |
| jail scale | 010 | citation (Chinese side: Neixiang prison, twenty-plus rooms, three divisions, walled) + absence (Japanese side: no daikansho jail size on any page) | `neixiang-yamen-zhwiki-7`, `administrative-culture-is-japan-first-for-compound-interiors-2` |
| clerk counts | 010 | citation, both sides | `daikan-jawiki`, `xuli-zhwiki-2` |
| eaves nearly touching | 070 | absence - the existing note's search extended (2026-09-27: 犬走り, 塀 (城郭), 築地塀) and now names the eaves | `a-compound-wall-is-a-building-not-a-boundary-line` |

Also fixed where found (constitution XIV), same section 150: the "~30-40% of tax came as coin" absence note became a
citation, `nta-nengu-nonyu` (the NTA page gives 3-4 tenths, naming no region, so "empire-wide" was dropped from the
prose; the old search is kept in an HTML comment). The freed key `the-granary-holds-grain-not-just-rice` now holds the
soybean absence note - session 2 should read it as a rewritten note, not an unchanged one.

The xuli quote is from the article's own traditional-character source text (checked against `action=raw`), not the
zh-cn rendering the saved page holds.

## FR-006 items

- none

## Open

- SECTION=040 (not one of this page's items): note `neixiang-yamen-zhwiki-6` quotes the Neixiang prison as 130 x 70
  zhang, which the source-reader flagged as implausible (~430 x 230 m for a "small courtyard") - probably a unit error on
  the page. The quote is verbatim; whether the 040 prose leans on the figure should be looked at when 040 is next checked.
- Leads not opened: Takarazuka city history 「三分一銀納・十分一大豆銀納制の定着」
  (https://adeac.jp/takarazuka-city/text-list/d100020/ht201680) for the soybean share; a Ctrip travelogue
  (https://gs.ctrip.com/html5/you/travels/2295/4103688.html) that may name Neixiang's archive (架阁库). Neither would
  change a form above unless it names soybean bales in kind or an archive outright.
