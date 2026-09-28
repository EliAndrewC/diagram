# 271 V3 handoff - fields: bunds, crops and field features (session 1: research and write)

Written 2026-09-27 in clone diagram-research-2. One source-reader pass over 33 claims (29 READ, 4 NOT-FOUND); every
citation below rests on a READ passage. Saved pages: `/tmp/l7r-check/271-v3-pages/` (MANIFEST.txt). No item was
claimed by another session since the brief was written.

## Sections

- SECTION=fields/010
- SECTION=fields/022
- SECTION=fields/050
- SECTION=fields/100
- SECTION=fields/400
- SECTION=fields/410

## New registry keys

- KEY=suido-ishizue-kochi-seiri
- KEY=fukui-kenshi-noji
- KEY=soba-jawiki
- KEY=awa-jawiki
- KEY=kibi-jawiki
- KEY=omugi-jawiki
- KEY=hakubaku-omugi-ichinen
- KEY=maruyanagi-daizu-hatake
- KEY=kagawa-tameike-data
- KEY=inamino-saraike
- KEY=kikka-monsho-jawiki
- KEY=kiku-jawiki
- KEY=toshima-somei
- KEY=sugamo-kikumatsuri
- KEY=katsushika-horikiri
- KEY=mboso-hana
- KEY=chinagate-tongxiang

Existing keys newly cited on these sections: `aze-jawiki`, `jori-jawiki`, `tameike-jawiki`, `bungotakada-tagoshi`.

## Items

- A05 SILENT (with a CONTRADICTION raised) - fields/022 now cites that a bund commonly stands on the owners'
  boundary, has no fixed form outside modern works and is re-plastered every year (Edo calendar: early to late
  May), and that early-modern plots were narrow and irregular; nothing readable speaks to a bund that jogs sideways,
  so the no-jog rule and the corner-slump reasoning stay labeled guesses with dated absence notes. The same source
  says western Japan kept the regular jori grid widely up to Meiji - a second, ruled FORM of paddy fabric - so the
  generator's jog repair is unaffected, but the pool draws only the wavering fabric; a jori-ruled plain is an
  attested KNOB the engine does not roll (future-work, not a defect in any map).
- A07 ACCURATE - fields/100 now cites that the bund between a paddy and the ditch beside it is a named kind (溝畔),
  with the boundary sometimes at its paddy-side foot or water line, so the lowest bund runs WITH the drain on its
  bank; the "bund across the drain dams it" half is a grounds note; old paddies passed water paddy to paddy
  (tagoshi) where modern ones feed from a canal into a drain - no change to what the generator draws (the hem already
  runs parallel to the collector).
- A15 ACCURATE (heights, colors, seasons) / SILENT (sowing in rows) - new fields/400 gives each crop's height,
  color and months from botany and the Japanese crop year (barley green in winter, gold in May, cut by June; millet
  150 cm to 2 m, yellow drooping heads in autumn; buckwheat 60-130 cm, white to red flowers, 70-80 days; soybean a
  bush near 80 cm that yellows before harvest); no page describes how a pre-modern dry field was sown, so the
  furrow texture in fields/050 and fields/400 is labeled a guess. For the generator: the maps are high summer, yet
  `DRY_CROPS` (waterfields/palette.py) paints barley tan-gold (May) and millet ochre (October) beside July paddy;
  by the calendar a high-summer barley plot is stubble, bare or under soybean, millet is green and tall, and only
  buckwheat can be in flower (white). Whether to keep one season or each crop's recognizable color is an open
  drawing choice for the GM - recorded as open on fields/400, not made.
- A18 SILENT (the rates) - fields/010 now cites where a pond among paddy comes from (the plains "dish pond" dug
  into hollows or even converted farmland; household ponds about 10 m square), how many ponds Japan has, and
  Kagawa as the densest pond country (12,187 ponds, half under 1,000 t); nothing readable gives a rate per field or
  per village, and nothing speaks of rocks left in paddy, so the engine's rates (pond 0.55 on low ground; rocks on
  every terrace field, half of ribbon fields, 1-3 each) stay disclosed guesses - no change; pond frequency is a
  degree (calibrated liberty), not a knob.
- A27 B125 DEVIATION + ACCURATE + SILENT - new fields/410: the chrysanthemum is the imperial emblem by custom since
  Go-Toba and an offering flower, but nothing read describes a planted field kept for a court, so Hirameki's
  Imperial field is recorded as the setting's deliberate deviation; flowers WERE grown for the market in nursery
  villages on Edo's edge (Somei, Sugamo, Horikiri) and sent in from Boso, and chrysanthemums were a Chinese medicinal
  field crop (Tongxiang), but every case is a great city's edge, none is for a shrine, and no plot size is given -
  so an ordinary town's ring grows no flower plots and Hirameki's ~220 x 340 ft field is a labeled guess. No map
  change.

## Corrections owed to other owners

- fields/020 (feature 269): it frames the straight rectangular plot as the modern consolidation artifact. The
  `suido-ishizue-kochi-seiri` page says 「西日本では、条里地割など明治期までの整形区画が広く分布していた」 - regular
  jori plots were widespread in western Japan up to Meiji. 020 should say the ruled grid is modern EXCEPT where the
  jori division survived, and cite it (fields/022 now does, as `suido-ishizue-kochi-seiri-2`).
- fields/180 (feature 269): its furrow direction rests on ridge tillage; this pass found no page describing how a
  pre-modern Japanese dry field was sown (absence note on fields/050 and fields/400). Worth a look when 180 is checked.

## Left open

- Two image-only PDFs added to the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` (entries 256, 257):
  Kimura's 「植木屋考」 (J-STAGE) and the Shinjuku Gyoen 「江戸菊花壇」 leaflet - either could give a flower plot's
  size or the court's chrysanthemum beds.
- The Edo farming manuals (農業全書 and others) would settle the dry-crop sowing question; no readable full text
  was found.
- Entry drift: fields/010, 022, 050 and 100 are `Entry:` sections for modal classes (the dry-crop classes name 050;
  paddy features name 010), so `_entry_owed.py` will name those pairs for the check sessions.
- The jori-plain knob (A05) and the dry-crop season colors (A15) are GM decisions, not made here.
