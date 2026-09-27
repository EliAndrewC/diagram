# Handoff - feature 250, page `fields`, session 1 -> session 2

Pages saved for the checks: `/tmp/l7r-check/fields-pages` (MANIFEST.txt); `15b-kyushu-fukushima-utf8.txt` is a
re-decoded copy of `15-*` (Shift-JIS), a student report, not cited.

## Changed questions

- SECTION=070 (Where does a field's water come from, and how is it shared out?)
- SECTION=110 (Plot sizes, pond sizing and acreage from population)
- SECTION=160 (Where dry (hatake) crops go - the topographic catena)

## New or changed registry keys

- KEY=zakkoku-jawiki (new, 9320)
- KEY=zakkoku-kotobank (new, 9330; the Yamakawa Nihonshi Shojiten entry on the kotobank page)
- KEY=bungotakada-tagoshi (new, 9340)
- KEY=satoyama-jawiki (changed: `Used for:` adds the fields use)

## FR-002 items

- 110 "coarse grain fills part of the diet" - CITATION: `zakkoku-jawiki` + `zakkoku-kotobank` (the jawiki page says more -
  outside Edo coarse grain was the staple itself; the gloss says so).
- 070 "The network is sparse: a village digs the minimum" - rewritten into two parts. "The old form passes water from
  paddy to paddy over the bund (tagoshi) rather than down a ditch to each" - CITATION `bungotakada-tagoshi`. "That the
  network is therefore sparse, a village digging the minimum, is this page's own reading" - ABSENCE
  (`where-does-a-fields-water-come-from-and-how-is-it-shared-out-3`). The source-reader found nothing read saying few
  ditches, and flagged that the Bungotakada village keeps many weirs (now in the registry limits).
- 160 "coppice woodland (satoyama) crowns the hills above" - the source-reader found the placement NOT-FOUND and "coppice"
  CONTRADICTED for early-modern satoyama in general (ja.wikipedia: most had become red pine, grass or bare hill). The
  sentence is rewritten to what the pages say: satoyama on the slopes around the village, sometimes sharing them with
  dry plots (`satoyama-enwiki-2`, the border-zone definition), broadleaf coppice on a 10-20 year cut, most of it red
  pine, grass or bare hill by the early modern period (`satoyama-jawiki`, three passages) - CITATION.

## FR-006 items

- 13 (azemichi ~2-5 ft) - LOCATED in 020 (paddy plots), the sentence ends "... the one readable figure being a 300-600
  mm crest for bunds built under modern consolidation." CONFIRMED: it carries `aze-jawiki`, whose gloss says the page
  calls the azemichi wide without a width; the 2-5 ft is labeled a guess in the sentence.
- 14 (pre-modern yield ~1.3 koku/tan) - LOCATED in 110, now "the assessed rate for middling paddy ~1.3 koku/tan (the
  middle-grade kokumori, a tax rate rather than a measured yield)". CONFIRMED: `kokumori-jawiki` (中田 1石3斗).
- 15 (Ming-Qing mu ~614 m2) - LOCATED in 120 (tract sizes), now "at the 614.4 m2 mu the 1915 law fixed on the Qing
  definition". CONFIRMED: `mu-land-enwiki` (its gloss: no page read gives a Ming figure).
- 31 (TOO-SHORT shitsuden / kanden quotes) - LOCATED in 190 (shitsuden), both quoted whole in the body with
  translations. CONFIRMED: `kotobank-shitsuden`, `kotobank-kanden`.

## Size cap

No question touched is over 20,000 bytes (`scripts/check-question-size.py` clean); nothing split.

## Open

- The 160 rewrite changes a section body: session 2 should expect `_entry_owed.py` to name any modal written from 160
  (and from 070, 110), for an `entry-drift` check.
- The canon (`make canon`, one call) has Rokugan peasants growing wheat, barley, millet and soybeans beside rice
  (l7r.md "Crops and Farming Seasons"; RokuganHistory.md "Clan Organization and Function") - consistent with the
  coarse-grain sentence; no canon covers ditches or satoyama.
- The Shiga prefecture and farm ministry PDFs a search showed saying tagoshi districts have "hardly any channels"
  could not be read here (no PDF text tool; the Shiga URL returns 404). If session 2 can read the ministry PDF
  (https://www.maff.go.jp/j/nousin/noukan/tyotei/kizyun/attach/pdf/nougyouyousui_suiden-1.pdf), the absence note in
  070 could become a citation.
- Record tests (footnotes, citations, sources, record_format) green after `make record && make citations`.
