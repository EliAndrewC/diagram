# Handoff - feature 269, group H1 (homesteads: farmstead fixtures), session 1

Written 2026-09-27. Nothing of H1 had been claimed by another session (`/diagram/.clones/RESEARCH-CLAIMS.md`, read first).

## Sections

- SECTION=homesteads/210
- SECTION=homesteads/212
- SECTION=homesteads/214
- SECTION=homesteads/215
- SECTION=homesteads/218
- SECTION=homesteads/250

## New registry keys

- KEY=suzuki-1959-noson-benjo
- KEY=sugiura-1977-tohoku
- KEY=sato-1962-haichi
- KEY=suido-ishizue-kizuma
- KEY=mizu-no-bunka-11-furo
- KEY=water21-furo
- KEY=jataff-fuyu-kaki
- KEY=pfaf-kaki
- KEY=buck-1930-farm-economy

New glossary terms: `kizuma` (9520), `nodame` (9530, with the variants "field pit", "field pits").

## Items

- B10 KNOB - a 1959 survey puts the outdoor privy on more than 90% of farm households (the drawn 85-95% is now cited), prewar Tohoku villages range from 0 to 85%, and the record now holds four attested seats: under the eaves by the stable, a separate outhouse in the yard, the front yard (northern Miyagi), and a tub sunk in the barn; the size stays a GUESS with an absence note - the privy seat roll (back door .60 / gate .25 / stable .15, where the back door and gate are guesses) should roll among the four attested seats, keeping the sun-side preference of homesteads/220; the size is unchanged.
- B11 KNOB (the night-soil pit) / SILENT (the heap) - night soil was kept either in a tank beside the privy or in a field pit out by the fields or a road, the field pit on 2 of 83, 19 of 53 and 15 of 18 households in three villages; where the heap of stable manure stood in the yard is still found nowhere (absence note, searched 2026-09-27) - the manure kind's `pit` form should be seated either beside the privy or at a field edge or roadside, the field-edge share rolled per hamlet from almost none to most households; the heap's seat stays a labeled guess.
- B12 KNOB - the bath shed's attested seat is the front yard (northern Miyagi, a 1941 report via Sugiura 1977), a shed joined to the house by a corridor is a second attested form (Meiji, Oba Osamu), a bath indoors stood in the northeast corner (Sugiura 1973), and the shed's share ran from 0 to 80% village by village; the back wall or flank is a GUESS - seat the shed in the front yard beside the work yard or corridor-linked against the house (the back wall/flank only as fallback), and widen the share band from 0.20-0.45 to roll per hamlet between about 0 and 0.80.
- B13 CONTRADICTION-RESOLVED - Buck's 1921-25 survey of 2,866 Chinese farms found chickens on 82% of farms, more in east-central than north China, so the drawn 50-80% guess sits below the attested figure - raise the coop band to one centered near 0.82 (the record says higher in a wet-rice hamlet, lower in a dry-field one; the band's width is calibrated liberty); the 5 x 5 ft size and the flank seat stay guesses, now with an absence note.
- B14 KNOB - the persimmon is attested in the dooryard in front of the house ("every house", JATAFF; Shonai front yards of fruit trees, Sato 1962) and once behind the house; the flank the map draws is a GUESS; a grown persimmon is about 12 m by 7 m (PFAF), a crown of about 23 ft against the 18 ft drawn - seat the tree in front (at the work yard's edge where there is one) or behind, front likelier, and draw the crown about 23 ft across.
- B15 KNOB - three forms: a woodshed (Shonai; Boso-no-Mura; Sugiura's 0.76 sheds), a stack laid under the windbreak grove on its northwest (windward) side as a kizuma, sometimes roofed (Isawa; a small form at Yahaba), and the open stack against the house wall, which is still found on no page (absence note re-searched 2026-09-27) - roll the woodpile's form per hamlet among the three, the windbreak stack only where the homestead has a windbreak; the eaves stack stays a labeled guess.

## The modals quote shares the maps do not draw (`fc:2197`)

Read from the five live hamlets' manifests (`meta.farm_fixtures` against the seated `farm_fixtures` / `persimmons`), 2026-09-27. `farm_fixtures_unseated` is recorded only on Kuwabata (coop 1), so the other gaps are not seat refusals - the per-house roll lands far from the declared share, in both directions:

| map (houses) | kind | declared | expected | seated |
|---|---|---|---|---|
| Inashiro (15) | bath | 0.335 | 5.0 | 1 |
| Sawada (19) | bath | 0.412 | 7.8 | 11 |
| Sawada (19) | woodpile | 0.815 | 15.5 | 11 |
| Sawada (19) | manure | 0.448 | 8.5 | 5 |
| Kuwabata (16) | persimmon | 0.928 | 14.8 | 12 |
| Inashiro (15) | persimmon | 0.822 | 12.3 | 10 |
| Sawada (19) | persimmon | 0.900 | 17.1 | 13 |
| Sawada (19) | coop | 0.786 | 14.9 | 17 |
| Inashiro (15) | coop | 0.689 | 10.3 | 12 |

The modals that quote a share: `Bathhouse` ("about three farms in ten" - Sugiura's 0.29, while Inashiro draws 1 in 15 and Sawada 11 in 19), `HouseholdShrine` ("three to eight households in a hundred" - fine), and the record sections themselves ("drawn on 85-95% / 75-95% / 40-70% / 20-45% / 50-80% / 80-95% of homesteads"), which the woodpile, manure, bath and persimmon rows above contradict on at least one live map. Homesteads/210's "What the map does" counts for Inashiro were stale (12, 7, 7, 5, 3, 1, 8) and are corrected from the manifest (14, 14, 12, 9, 1, 1, 10).

## Left open

- The `Bathhouse` modal says where the shed stood "was found nowhere" - now drifted from homesteads/214 (entry-drift owed); `Woodpile`, `HenCoop`, `Persimmon` and `ManureHeap` may drift the same way once their sections are checked.
- Buck's page numbers: the Internet Archive OCR garbles the page markers; the two sentences sit on or near pp. 219-221, so the note gives no page.
- The PDF sources (Suzuki 1959, Sugiura 1973 and 1977, Sato 1962) were read from text layers extracted with pypdf, saved at `/tmp/l7r-check/269-h1-pages/30-33-*.pdf.txt`; `make source-pages` cannot read a PDF, so `make quote-verbatim` may report these notes as unverifiable against the fetched page - the check session should use those saved texts.
- No correction is owed to another feature's sections.
