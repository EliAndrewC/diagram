# Handoff - feature 269, group H2 (homesteads: siting), session 1

Written 2026-09-27. Nothing of H2 had been claimed by another session (`/diagram/.clones/RESEARCH-CLAIMS.md`, read first).

## Sections

- SECTION=homesteads/240
- SECTION=homesteads/300
- SECTION=homesteads/310

## New registry keys

- KEY=okayama-chikusanshi-shiyo
- KEY=agrinews-2023-tajima-maya
- KEY=ndl-crd-shakkogyu
- KEY=sakamoto-tsubaki-1985-omoya-muki

No new glossary terms (byre, dooryard, steading already have tooltips).

## Items

- B16 SILENT - no readable page puts a byre shared by several households on the village's common ground, or any byre at the village edge; what the record now attests instead is that the beast lived with its keeper: the cattle shed was mostly inside the house (Okayama; Mikata, Hyogo, about 4,000 such houses in the 1950s), more than 80% of beasts were their keepers' own (Bizen, mid-17th century), large owners lent cattle out to tenants, and a region short of oxen borrowed them from another for the plowing season - so the commons-vs-edge choice is NOT a knob - `byre_form`'s `detached_commons` placer should stop seating a byre beyond the last house (both of Inashiro's outliers, 109 ft and 89 ft out, are unsupported); the byre belongs in or against a homestead, owned or on loan; the commons form survives only as a labeled guess, and the 2026-08-18 coverage fix is moot for any byre seated in a homestead.
- B17 SILENT - no readable page says how far a village lane runs past its last house or whether it stops at the dooryard or runs on to the fields (absence note, searched 2026-09-27 in Japanese, Chinese and English) - nothing changes in kind: the trim stays a guess, and the record's rule is that a lane ends at the dooryard of the last house it serves or runs on to something visible (field path, bund, another way). Sawada's 85 ft and Kashikawa's 55-ft-from-the-wall ends read as defects under that rule, and whether "serving" is measured from the wall or the center, and how far, is a labeled guess.
- B18 CONTRADICTION-RESOLVED - homesteads/240 said no page measures the spread and drew up to 5 degrees; a count of the main houses of 27 Okinawan slope villages (Sakamoto and Tsubaki 1985) found 87% within the commonest of 16 compass points and its two neighbors (the neighbors arising where roads curve, a span of about 67 degrees), 11% turned a quarter turn to the right, 1% each left and back, and the flat villages of part 3 nearly the same (88/11/3/1) - the house rake should widen from 5 degrees to up to about 30 degrees either way about the village's common bearing (most much less, following the lane's curve; the distribution inside that range is calibrated liberty and a labeled guess), and about one house in ten should be turned a quarter turn, its yard and beds turning with it per the GM's 2026-09-26 ruling. The quarter-turned house is a new form the engine does not draw; put it to the GM with the rake change if a quarter-turned yard needs a ruling.

## Owed elsewhere

- **homesteads/060** (269's own page, not in H2's brief): its sentence "a team that is SHARED or hired stands where the borrowing household can walk to it, on the common ground among the homesteads", and "on a commons map, the commoner of the two", rest on note `may-a-byre-stand-beside-a-wellhead-3`, which says no source was ever cited. homesteads/300 now finds that no shared shed was found and that lent beasts went to a borrower. That sentence should be rewritten to point at 300 and drop "the commoner of the two". The byre modal(s) written from 060 then owe an entry-drift check.
- **homesteads/240's heading** still says "turned a little off due south". The id is kept so the `Entry:` tags still resolve. With a spread of up to about 30 degrees and quarter-turned houses, "a little" understates it. Renaming the heading owes the inbound `Entry:` tags.
- No correction is owed to 265, 267 or 268's sections.

## Left open

- `kotobank-umaya` (Heibonsha: an umaya is a free-standing building or a room in the house; Nipponica: Nanbu's in-house stables) supports 300 too. It is being defined in feature 267's clone (`diagram-buildings`, 9860, not yet on main), so `reserve-prefix.py` refused it here. Once 267 lands, 300 may add it for the free-standing outer stable.
- The Sakamoto and Tsubaki quotes come from the J-STAGE PDF's text layer, extracted with `pdftotext -layout` and saved at `/tmp/l7r-check/269-h2-pages/32.pdf.txt`. That layer spaces its characters and interleaves the two columns; the source-reader rejoined each sentence. `make source-pages` cannot read a PDF, so `make quote-verbatim` will likely report these notes as unverifiable, and the check session should use that saved text. Table 3's counts are garbled in the text layer, so only the percentages are cited.
- Pre-existing, not H2's: `scripts/check-question-size.py` reports homesteads/210 at 20,060 bytes with its notes, over the cap, and H2 did not touch it.
- The Iwamoto 2023 PDF (nohken.or.jp) was read through and says nothing on byre siting. It is named in 300's absence note, not registered.
