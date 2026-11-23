# T371e handoff - session 1: write (cleanup)

- SECTION=0103 0009 0107

## Items

- E1 NARROWED (three departures from the brief: Nagoya is called "a castle garden", not a daimyo garden, because its PDF names no daimyo or Owari; "feature stones" dropped, as the papers say a stone on the tataki was probably set or moved in modern times; and a third registry key, `jawiki-tataki`, to gloss tataki from a cited source. The Shunjuen banks are not dated in the passages read, and the registry entry and Evidence comment say so rather than "undated") - 0103's findings now carry two excavated gardens, each said as the one garden it is: Shunjuen at Kani, the stroll garden of several ponds of the Chimura's lower residence (a hatamoto family; made 1756-65, remade c. 1804-28 with its pond enlarged), whose 2001-03 excavation found a near-vertical stone wall about 60 cm high thought to serve as the south pond's revetment, a laid earth floor 5-20 cm thick in that pond's bed, a neatly laid revetment and facing stones at another pond and the edging stones of the central pond; and the Ninomaru garden of Nagoya Castle (drawn in the Bunsei years, 1818-30), whose North pond had a tataki revetment and floor the excavators could not date. The line that a small residence's or an office's pond bank is not recorded stays. The absence `pond-bank-absence` (findings and drawing notes, identical) now names both excavations as read, drops Shunjuen from "unreadable", says "encyclopedia", and adds a pass line that the two describe only their own ponds; its conclusion is unchanged. The registry entry `ohno-2014-obata-ponds` now says it also gives the viewing ponds' 40-60 cm depth, a 2010s measurement of an undated survival (limits and Used for). The lantern kinds have their own glossary terms (Kasuga lantern, Enshū lantern, Oribe lantern, defined from the record's own words as named kinds told apart by their use); the findings and drawing pages now say "the Kasuga lantern ... the Oribe lantern" so the shrine-style tooltip no longer fires (no bare "Kasuga"/"Oribe" variant, which would hit the Kasuga shrine and Kasuga City pages). A new glossary term `tataki` (`"cased": true`, so it does not wrap the village name "Tataki" in another question's source), from a new cited note `jawiki-tataki`. The glossary matcher (`glossary.rs`) has the Kasuga-style term matching only "Kasuga-style"/"Kasuga-zukuri", so how bare "Kasuga" got the shrine tooltip was not reproduced; the pages now carry "Kasuga lantern", which longest-first matching gives the new term. The translated quotation in `kotobank-ishidoro` (both notes files) still says bare "the Kasuga" and was left as the translation.
- E2 DONE - 0009's drawing note `obata-1977-taue-2` now glosses Kichu and Kinan as "central and southern Wakayama", and the findings' opening cites `qimin-yaoshu-enwiki` for the manual's date of 544 (the opening's clause about the manual was shortened to "drains to firm the roots and again before ripening" to stay under 19,800; bullet 31 says it in full).
- E3 DONE - 0107: the drawing absence `kitchen-two-doors-absence` now says no page places a SMALL HOUSE's kitchen door on its doma, and its searched list adds JAANUS (katteguchi, shimodaidokoro), which places the great mansions' service kitchen door on its doma. "Who came in by the kitchen door?" now opens: at the great mansions, tradesmen (`jaanus-shimodaidokoro-door`); for a small house only modern pages say; no pre-1868 page says who came in by a small samurai house's kitchen door. The drawing's "Our plans draw the kitchen door but do not say who came in by it" says the same. The roof bullet's heading now ends "; so was a foot soldier's" and its body says "Beside these, the houses of the Kaga domain's foot soldiers (ashigaru)". Optional item done: `mlit-kaga-ashigaru` now links the PDF https://www.mlit.go.jp/tagengo-db/common/001559629.pdf, whose pdftotext text carries all three quoted passages verbatim.
  - Beyond the brief, flagged for the checks: the absence `kitchen-door-users-absence` (both notes files) had a visible pass line, "says who came in by the kitchen door", that JAANUS now contradicts, so it now reads "a small house's kitchen door". Its searched comment was NOT changed (JAANUS is cited on the page itself, not as part of that search). The findings Evidence comment adds the great mansions' tradesmen's entry.

## Notes a pop-up would rest on

- 0103: `kani-2004-shunjuen`, `kani-2004-shunjuen-banks`, `nagoya-ninomaru-banks`, `jawiki-tataki`, `pond-bank-absence`, `ohno-2014-obata-ponds`, `kotobank-ishidoro`
- 0009: `qimin-yaoshu-enwiki`, `obata-1977-taue-2`
- 0107: `jaanus-shimodaidokoro-door`, `kitchen-two-doors-absence`, `kitchen-door-users-absence`, `mlit-kaga-ashigaru`

## Files

- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.html
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.notes.html
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.originals.html (written by `make record`, the new notes' originals)
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.drawing.html
- research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.drawing.notes.html
- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.html
- research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.notes.html
- research/questions/0107-kitchens-daidokoro.html
- research/questions/0107-kitchens-daidokoro.notes.html
- research/questions/0107-kitchens-daidokoro.drawing.html
- research/questions/0107-kitchens-daidokoro.drawing.notes.html
- research/sources/010-works-cited/37320-mlit-kaga-ashigaru.html
- research/sources/010-works-cited/37360-ohno-2014-obata-ponds.html
- research/sources/010-works-cited/37370-kani-2004-shunjuen.html (new)
- research/sources/010-works-cited/37380-nagoya-ninomaru-2023.html (new)
- research/sources/010-works-cited/37390-jawiki-tataki.html (new)
- l7r/diagram/interactive/assets/glossary/28480-Kasuga lantern.json (new)
- l7r/diagram/interactive/assets/glossary/28490-Enshū lantern.json (new)
- l7r/diagram/interactive/assets/glossary/28500-Oribe lantern.json (new)
- l7r/diagram/interactive/assets/glossary/28510-tataki.json (new)
- l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt (rewritten by `make glossary`)
- specs/449-rust-codebase/briefs/t371e-handoff.md

## Registry keys reserved (3 of 10)

- `kani-2004-shunjuen` (period=premodern; region=japan; kind=scholarship)
- `nagoya-ninomaru-2023` (period=premodern; region=japan; kind=institutional)
- `jawiki-tataki` (period=premodern; region=japan; kind=reference)

Glossary keys reserved: Kasuga lantern, Enshū lantern, Oribe lantern, tataki.

## Searches and reads (all on the ledger)

- `make archive-find URL=` for the Shunjuen, Nagoya and MLIT PDFs: none held.
- Shunjuen PDF: the first downloads got nabunken's "busy" HTML page; a background retry fetched the PDF (40 MB), read with pdftotext (OCR layer). cited:kani-2004-shunjuen.
- Nagoya PDF: read with pdftotext. cited:nagoya-ninomaru-2023. It does NOT name the garden a daimyo's or the Owari domain's, so the page calls it Nagoya Castle's Ninomaru garden, "a castle garden"; the Bunsei drawing is matched in the papers to the gate and wall footings, not to the bank, and the page says only that the garden was drawn then. "Feature stones" was dropped: the papers say a stone on the tataki was probably set or moved in modern times.
- MLIT PDF: cited:mlit-kaga-ashigaru.
- Tataki gloss: `make archive-find TERMS="三和土"` (nothing usable); Kotobank https://kotobank.jp/word/%E4%B8%89%E5%92%8C%E5%9C%9F-74064 (rejected: serves the entry for 執事); web search "コトバンク 三和土 たたき 石灰 にがり"; ja.wiktionary 三和土 (nothing-found); ja.wikipedia 三和土 (cited:jawiki-tataki).

## Bytes after (wc -c of each findings page)

All figures are `wc -c` of the file; the brief's figures ran about 4 bytes above that.

- 0103: 13,080 (was about 11,500 of prose)
- 0009: 19,793, about 19,797 on the brief's count (cap for this item 19,800)
- 0107: 14,195
- `make question-sizes`: 0 questions over 20,000. `make record CHECK=1`: builds cleanly.

## Open

- None left undone. Checks owed (next session): the new and changed notes on 0103 (source-reader / quote-check / translation-check for the Shunjuen, Nagoya and tataki originals), source-applicability for the three new registry entries and the changed ohno and mlit entries, record-format on 0103, 0009 and 0107, and entry-drift for any pop-up resting on 0103's banks or 0107's kitchen door.
## Checks (session 2, t371e-checks)
CHECKED modal-triage all page-moved pop-ups - 37 TOUCHES (97 units sent on), rest triage: untouched - recorded with make modal-triaged
CHECKED source-applicability jawiki-tataki - r1 1 APPLICABLE-WITH-LIMITS, limits OVERSTATED; r2 limits HONEST - applied (limits sentence rewritten, via source-reader's EDIT)
CHECKED source-applicability kani-2004-shunjuen, mlit-kaga-ashigaru, nagoya-ninomaru-2023, ohno-2014-obata-ponds - each 1 APPLICABLE-WITH-LIMITS, limits HONEST, tags RIGHT - nothing
CHECKED source-reader 0103#jawiki-tataki - 3 claims, 2 READ, 1 CONTRADICTED (registry 'no date or place') - applied
CHECKED source-reader 0103#kani-2004-shunjuen, kani-2004-shunjuen-banks - 14 READ - nothing
CHECKED source-reader 0103#nagoya-ninomaru-banks - 6 READ - nothing
CHECKED source-reader 0107#mlit-kaga-ashigaru - 6 READ - nothing
CHECKED source-reader 0009#obata-1977-taue-2, -3, 0009.drawing#obata-1977-taue-2 - 3 READ - nothing
CHECKED quote-check 0009 (13 units) - 9 VERBATIM, 2 UNFETCHABLE (maff 403; all five maff passages hand-matched VERBATIM against the GM copy gm-copies/suitou-2.pdf after NFKC), 11 SUPPORTS, 1 JOINED-WRONG - applied (obata-1977-taue-2 separators, both notes files)
CHECKED quote-check 0103 (12 units) - 10 VERBATIM, 9 SUPPORTS, 1 PARTIAL, 3 JOINED-WRONG, 1 unfootnoted - applied ('a pond-and-stroll garden'; heading 'Two excavated gardens'; separators in kotobank-teien-banks, kotobank-teien-edo-banks, ohno-2014-obata-ponds)
CHECKED quote-check 0107 (28 units) - 21 VERBATIM, 21 SUPPORTS, 1 CLAIM-FROM-UNREAD - applied (kitchen-door-users-absence: Ukigumo and English-guide sub-passes dropped, both notes files)
CHECKED record-format 0009 - r1 and r2 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED record-format 0103 - r1 1 VOCABULARY (bittern); r2 0 - applied (glossary term bittern)
CHECKED record-format 0107 - r1 and r2 0 VOCABULARY, 0 SESSION NOTE, 0 HISTORY - nothing
CHECKED translation-check 0103 (33 pairs) - r1 and r2 33 FAITHFUL - nothing
CHANGED research/sources/010-works-cited/37390-jawiki-tataki.html
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.notes.html
CHANGED research/questions/0009-the-paddy-through-the-rice-year-flooding-draining-transplanting-and-after-the-harvest.drawing.notes.html
CHANGED research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.html
CHANGED research/questions/0103-ornamental-gardens-ponds-and-stone-lanterns-teien.notes.html
CHANGED research/questions/0107-kitchens-daidokoro.notes.html
CHANGED research/questions/0107-kitchens-daidokoro.drawing.notes.html
CHANGED l7r/diagram/interactive/assets/glossary/28520-bittern.json (new)
CHANGED l7r/diagram/interactive/assets/glossary.json and research/assets/glossary-variants.txt (make glossary)
OPEN pop-ups the triage named TOUCHES on these pages, owed their modal checks (not checked here): sheet/garden (0103 findings and drawing), sheet/door (0107), hamlet/paddy and choice/winter_crop--none (0009). Other pop-up units still owed on 0009/0103/0107 pages (hamlet/farmhouse, sheet/hearth, sheet/inner-court, sheet/kitchen, sheet/lanterns, sheet/residence, sheet/stone-lantern) are other builders'.
OPEN outside the change, 0009: 'Was the drain also confined to well-watered places' block cites horikawa-2011-nakaboshi for the prewar confinement, which only horikawa-2011-nakaboshi-6 quotes - add that note to the block (quote-check PARTIAL).
OPEN outside the change, 0103: kotobank-ishidoro (both notes files) joins its two passages with ' and ' not '; ' (JOINED-WRONG).
OPEN outside the change, 0107 drawing: 'Where the kamado stands is a knob between two forms.' - 'knob' is the engine's word; record-format suggests 'Our plans set the kamado in one of two places'.
OPEN advisory, 0107 kitchen-walls-absence comment calls the Kakunodate report 'Unreadable' for an HTTP 429; per the GM's 2026-09-07 ruling it belongs on the download list (make download-add), not unreadable.
OPEN optional, mlit-kaga-ashigaru registry entry says 'one domain's lowest warrior rank'; the source never ranks ashigaru - 'one domain's foot soldiers' would match it (source-reader note, no EDIT).
OPEN optional, kani-2004-shunjuen: the 1804-28 dates in passage #3 are Sawada's annotation in the report, not the family account; the entry's 'about' hedges it (source-reader note, no EDIT).
make record-owed after: no non-modal unit of 0009, 0103 or 0107 left unanswered; make record CHECK=1 clean; 0 questions over 20,000.
