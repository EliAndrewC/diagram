# Handoff - feature 269, group F1 (fields: paddy kinds), session 1: research and write

Written 2026-09-27. No F1 item had been claimed by another session (`/diagram/.clones/RESEARCH-CLAIMS.md`, read first;
269's line now names F1). The saved pages are in `/tmp/l7r-check/269-f1-pages` (`p1-`/`p2-`/`p3-` are pdftotext of
the three PDFs; p2 is an old scan whose text layer spaces every character). One `source-reader` read all 24 claims:
24 READ, 0 NOT-FOUND, 0 CONTRADICTED. Four needed narrower wording and three a flag, and all seven were applied as
written: 60.9%, not "about 60%"; the drain of over 20 days "seen", not recommended (and left out of the prose); the
Kubota timing is for tractors (left out); the hiki-guwa's two descriptions (only the hoe and the Nogu benriron line
cited); the alternate-year dispute disclosed; nucleation dated apart from the Kamakura stabilizing; Sato's view given
as his opinion. Canon: `make canon` (fallow, bund, levee, paddy, land survey, drain) found `budgets.md` "Total rice
production": an established paddy can be cropped continuously, and only about a third of rice-suitable land is under
wet paddy in any year because Rokugan is labor-limited. Section 250 uses it.

## Sections

- SECTION=fields/250
- SECTION=fields/260
- SECTION=fields/270
- SECTION=fields/020
- SECTION=fields/030
- SECTION=vegetation/090
- SECTION=homesteads/100

## New registry keys

- KEY=kotobank-kataarashi-nipponica
- KEY=kotobank-kataarashi-yamakawa
- KEY=koden-jawiki
- KEY=nishitani-2023-chusei-nogyo
- KEY=mizkan-2005-sato-kyuko
- KEY=kato-1999-ittanbu-kukaku
- KEY=smtrc-2019-nawanobi
- KEY=kotobank-aze-sekai-daihyakka
- KEY=kigosai-azenuri
- KEY=kubota-azenuri-kuwa
- KEY=horikawa-2011-nakaboshi
- KEY=doyoboshi-jawiki

Glossary: `azemichi` rewritten (its "two to five feet across" was stated as fact and is now labeled a guess, with
the dividing bund at one to two feet). `nakaboshi` rewritten (midsummer; before modern times only where water was
plentiful) and given the variant `doyoboshi`. No new term was added (see "Left open").

## Items

- B01 KNOB - fields/250: in the Heian and early medieval period much paddy lay out of crop in a given year. The late-Heian cropped share was 60.9%, and Oyama estate in 1102 worked 44 of 89 cho, with 26 resting. The resting plot (kataarashi, nenko) lay scattered among the cropped plots, never in a block, and was grazed in common. It rested for short water or thin soil. It went as the land was stabilized from the Kamakura period on, in nucleated villages and, on one historian's view, with the early modern land surveys. The two forms are settled paddy (no plot rests) and unsettled paddy (a few whole plots rest, scattered). The setting's canon, which needs no rest for the soil, sides with settled paddy. - `Fallow` / `fallow_patches`: the current "blighted sub-region inside a field" with red X marks (`settlement/fields/paddy.py` `_fallow_patch`) matches neither form. Per settlement, roll settled (most maps: no fallow drawn) against unsettled, with the weight a labeled guess. An unsettled map rests a few WHOLE basins inside their own bunds, never a patch within one. They are scattered, not adjacent, drawn as grass (grazed) and not as blight. They favor the tail of the water's run (guess), and their count is calibrated liberty (a few plots; the 1102 estate's near-third is the upper bound). The `Fallow` docstring's "Some dry ground rested between crops ... that is a guess" and `Entry: ... (no dedicated entry - recorded as silent)` should be rewritten from fields/250 and pointed at it (label: accurate for the form, guess for the share and the placement). Its "See references" will then show a question, where today `fallow` is the one class with none.
- B02 ACCURATE (dividing bund) / SILENT (walking bund) - fields/260: the dividing bund reads at one to two shaku. That is 2 shaku in Nishikimi's 1869 replanning at Inazato (Gifu), whose farm roads and ditches were 1 ken, and 1 shaku in an Edo land-survey allowance (a weak, unsourced column). The modern standard is 30 cm. No page gives a walking bund's width, so the 2-5 ft azemichi stays a guess, now held between the 2-shaku bund and the 1-ken road. Azenuri is cited: weeds stripped and kneaded mud plastered on before transplanting, a late-spring task in haiku, hand work with the hoe. fields/020's "no source for the azenuri timing" is gone. - Nothing the generator draws changes: `AZE_FT = 1.5` sits inside the read range, and the walking bund's 2-5 ft (and vegetation/090's ~3 ft) stay labeled guesses. homesteads/100's 6 ft floor now rests on a read bund width. Its path and eave parts are still guesses, and the number is unchanged.
- B03 ACCURATE - fields/270: a 2011 NIRE review (citing Nagata 1964) says Edo-period farm books describe the mid-season drain. So it was done in some places by the Edo period at the latest, as doyoboshi at the summer doyo, for about a week. Before the war it was confined to regions with plentiful water, and by 1966 59% of paddy was drained, the commonest reason for not draining being poor water. fields/030's "GUESS until a period source carries it" now points to 270. - Nothing drawn changes: the map shows one moment with its paddies flooded. If a map is ever set in midsummer, the drain is a knob tied to water supply (water-rich drained, water-short flooded).

## Owed elsewhere, and left open

- **Modals owed an entry-drift check** (their sections' bodies moved): whatever class's `Entry:` names fields/020 (paddy, bund), fields/030 (the paddy's depth caveat), vegetation/090 (crop margin) and homesteads/100 (the farmhouse set-back). The `Fallow` class owes a rewrite (B01 above), not only a drift check.
- **The glossary prefix space is full.** Every multiple of ten from 0010 to 9990 is taken. `/diagram/.clones/.tools/reserve-prefix.py glossary` then hands out 10000 and 10010, which `glossary_source.py` (`_NAMED = ^(\d{4})-`) refuses, so `make glossary` fails. I deleted the two stubs (kataarashi, kenchi). Their prefixes stay in the mirror's `.specify/prefixes.jsonl` ledger as unused reservations. The prose defines kataarashi where it is used and says "land survey" in place of kenchi. Adding a glossary term needs an engine change (five-digit prefixes, or a renumbering sweep) before any session can add one. That is not this group's to make.
- **homesteads/210** (269's own page, not F1's) is 20,060 bytes with its notes, over the 20,000 cap in `scripts/check-question-size.py`. F1 did not touch it; it owes a split.
- No correction is owed to 265, 267 or 268's sections.
