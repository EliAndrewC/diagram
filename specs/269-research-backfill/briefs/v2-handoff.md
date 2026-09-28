# Handoff - feature 269, group V2 (vegetation: groves and margins), session 1

Written 2026-09-27. Pages saved to `/tmp/l7r-check/269-v2-pages` (MANIFEST.txt; the `p3N.pdf.txt` files are pdftotext of
the PDFs listed in `pdf-urls.txt`). One `source-reader` pass over 23 claims: 22 READ, 1 NOT-FOUND (the width of an opening
in a windbreak), 0 CONTRADICTED. No item had been claimed by another session.

## Sections

- SECTION=vegetation/260
- SECTION=vegetation/270
- SECTION=vegetation/280
- SECTION=vegetation/290
- SECTION=vegetation/010
- SECTION=vegetation/030
- SECTION=vegetation/050
- SECTION=vegetation/090
- SECTION=vegetation/110
- SECTION=vegetation/120
- SECTION=vegetation/150
- SECTION=vegetation/154

## Keys

- KEY=sendai-igune-modelplan
- KEY=udworks-igune
- KEY=furusato-ikiru-tsuijimatsu
- KEY=biwahaku-hageyama-2024
- KEY=rinya-meiji-chisan
- KEY=fan-2003-forest-floods
- KEY=kayabun-kayabuki
- KEY=biwako-visitors-yoshi-hiire
- KEY=hiroshima-keihan-manual
- KEY=nonoichi-keihanritsu

Existing registry entries whose write-ups changed (their "Used for", and takehara's limits): `takehara-2004-yashikirin`,
`tonami-yashikirin-haichi`, `satoyama-jawiki`, `ohmi-yoshi`.

## Items

B29 ACCURATE (share SILENT) - vegetation/260: a farmstead's grove carried bamboo as one of its own plants. On the Tonami plain the stands were once many (madake, moso and two smaller bamboos) and were mixed among cedar, hackberry and alder from the west round to the north of the house; Sendai's igune plan puts bamboo in the bare lower part of the tall evergreens to stop the wind. No page gives a share, so the share is a guess (an absence note). 150 and 154 now point to it, and 154's "no page puts it on the N/W side" is corrected: the wind side is read, not guessed - the grove mixes in `settlement/homestead_parts/groves.py` should give the WINDBREAK mix a small nonzero bamboo share (`b_th` is 0.0 in both mixes, so no grove clump draws a culm - the `fc:2113` note), drawn low in the gaps between crowns and along the grove's edge; the dooryard mix can stay at 0. `hamletgen/homesteads/bamboo.py:21`'s side roll (back 0.45 / shed 0.30 / wind 0.15 / side 0.10) under-weights the wind side, which is now the one attested side besides the storehouses; the orchestrator should raise `wind` and restate the docstring's "summary-only" wording (the N+W side is read on `tonami-yashikirin-haichi` and `yashikirin-jawiki`). HOUSEHOLD_BAMBOO_PREVALENCE = 0.6 stays a labeled guess.

B30 KNOB (with a correction) - vegetation/270: a windbreak was NOT one kind of tree in a row. The Japanese farmstead grove was led by one planted tree (cedar at every homestead and dominant in three regions; black pine at Izumo), planted in rows, but held 9-18 kinds of tree per homestead; only the Izumo clipped pine wall is close to a single species, and it is a one-house form. The Chinese village grove behind a village was a mixed evergreen broadleaf wood (~47 species a patch). So `fc:1397`'s "typically one tall species in a row" is wrong, and its fix (a darker, taller, ranked crown treatment for the belt) is right for ONE of two forms: the village belt should roll per settlement between (1) conifer-led - darker, taller crowns in rank on the windward side with lesser broadleaf crowns among them (an interpolation to village scale, labeled so) - and (2) mixed broadleaf, like the woods around it. The conifer share within form (1) is a guess (absence note); today's windbreak mix is 38% conifer in the copse's crown vocabulary. That knob, and a crown treatment for form (1), are engine work with a settlement-review.

B31 mixed - one line per sub-item:
- water-mouth grove size: SILENT - split out of 010 into its own question vegetation/290 (010 was 24 KB, over the size cap once touched); a fresh Chinese and English search found no measured water-mouth grove; ~0.1-0.5 ha stays a guess between the Korean figures - no change to the generator.
- how far the hillside was stripped (050): ACCURATE - Japan's village hills had mostly become red pine, grass hill or bare hill by the early modern period; an 1894 estimate put 70% of the land counted as forest as bare; one Omi village's common hill was cut bare by brush cutting, with over 80% of its fuel bought in by early Meiji; the Qing "shed people" cleared China's hill forests. The unsourced "thousand years... masson pine and China fir" sentence and its absence note are gone (two glossary terms, `China fir` and `masson pine`, were deleted because nothing uses them now). The map's open scrub with a few scraggly pines is the middle of the attested range (calibrated liberty) - no change to the generator; a harsher map could be barer.
- crop margin (090): SILENT on a width, with a new finding: the uncropped bund and slope face are 2.8% of a flat paddy district and 9.5% of hilly Hiroshima's, with slope faces in mountain paddies sometimes larger than the flooded area. The 6 ft is now stated as a flat-ground figure - where a map draws terraced paddies, the kept-cut margin below a field is the whole riser and wider than 6 ft; the generator does not yet distinguish, and the width on terraces is not set by any source (left open).
- bank margin (110): SILENT - the absence note carries the 2026-09-27 search; no change.
- reed mowing (120): ACCURATE - new vegetation/280: reed and thatch grass were cut every year from common thatch fields, wetlands among them, and the cutting and burning held them back from forest; Lake Biwa's reed was cut in winter and burned in spring. 120's "unsourced" label is replaced by a pointer. That a farming village cut its OWN marsh this way is an interpolation, labeled so. The managed-toe form the map draws is supported; the alder-willow carr form stays recorded and unbuilt - no change.
- width of a gap in the belt (030): SILENT - an absence note now sits on the "no source gives a width" sentence (Hokkaido's windbreak manual and Sendai's plan give none); the 30 ft stays a drawing convention - no change.

## Also fixed on the way (constitution XIV)

- vegetation/010: typed footnote numbers ("note 6", "notes 72 and 73", "note 77", "note 7", "note 2", "note 73") removed from the prose and the notes - footnote numbers are allocated at assembly.

## Left open, and why

- The record checks (quote-check, record-format, source-applicability, entry-drift) are owed on every section and key above; this session did not run them, per the brief.
- `make test-file` on the four record tests: 255 passed, 2 failed, both in `water.html` (notes 44 and 46 - an absence note with a key, a grounds reason not on the list). Those come from the W1 check-c work already uncommitted in this clone when this session began (water/070 and its keys), not from V2; they are that session's to finish.
- The Osaki igune leaflet (`osakikoudo.jp`, a PDF with no text layer) names bamboo among the igune's trees; it could not be read here. It is not cited.
- No correction is owed to a section another feature owns.
