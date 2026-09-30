# Feature 292 sweep - settlements G02 handoff (session 1: write)

## Households: how many live in a house, and under how many roofs (ie)

- SECTION=settlements/households-how-many-live-in-a-house-and-under-how-many-roofs-ie
- RENDERING=rendering/settlements/how-our-maps-count-and-draw-households
- OLD=research/settlements/035-how-many-lived-in-one-farmhouse-and-under-how-many-roofs.html research/settlements/020-how-many-inhabitants-does-a-maps-house-count-stand-for.html research/settlements/030-is-every-household-in-a-hamlet-actually-drawn.html
- MODALS=RetirementHouse

- BASE=fe55805e3

No folded section was held by another feature. Nothing was cut but the three Sources: rosters and 030's pointer paragraph to 035 (REMOVED comment in the research fragment); 020's "the setting's own budget notes" and 030's village-floor wording went into comments beside their rules in the rendering section. The two same-passage notes l7r-median-domain-20 (035) and l7r-median-domain-11 (020) became one note per page: -20 on the research page and -11 on the rendering page, whose href was corrected to `../../SOURCES.html` for the rendering page's depth. kotobank-inkyoya and nawata-sangiin-2006-3 are copied into both notes files because both fragments cite them. The absence note on the share of homesteads with a retirement house was converted to the new form in both pages (keys households-how-many-live-in-a-house-and-under-how-many-roofs-ie and how-our-maps-count-and-draw-households-3); its search dates from 2026-09-27, before homesteads 720's Kakimochi count of 1885 (8 of 16 households with a retirement house) was written, so the research section links to that count rather than claiming no village figure exists; a check may want the share bullet to cite it directly. homesteads/720 now links to the new section at its retirement-house count; homesteads/140 holds nothing about the retirement house, so it was left alone. The link in rendering/religion-and-death/160 and the code comments in dwellings.py, place.py, hamletgen/homesteads/stages.py and retirement.py were re-aimed; the classes_before_189 fixture has no RetirementHouse entry, so it was unchanged.
