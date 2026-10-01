# Handoff - feature 280, group U3 (urban-features: the boom, the charcoal yard, the bales and the huller), session 1

- SECTION=urban-features/040
- SECTION=0197
- SECTION=0199
- SECTION=0208
- SECTION=urban-features/720
- KEY=tsunaba-nikkoku
- KEY=aba-jawiki
- KEY=nippon-fukagawa-kiba
- KEY=shiratori-chobokujo-jawiki
- KEY=guazhi-jianggui
- KEY=jifpro-seitan
- KEY=crd-momigura-tawara
- KEY=nta-nengumai-genmai

Changed write-ups (Used for lines only): mokutan-jawiki, fukagawa-kiba-summary, nta-nengu-nonyu.

## Outcomes

M103 MIXED - the record (new question 720, split from 040 for the size cap; 040's decision points at it) now says premodern East Asia held timber with a rope across a timber river's middle course (the tsunaba, named in a pass of 1422), rafts moored along a bank (Guazhi on the Qingshui, a river rule carved in 1797) and ponds off the river (Shiratori about 1610, 23,900 tsubo by the end of Edo; Kiba lots each a central pond on the 1858 map), while the floating log fence round a pen is known in East Asia only from modern records (ja.wikipedia 網場: modern sources, steel cables, the floating era to the early 1950s) and the boom-and-pen gear only from 19th-century American booms - `s.log_boom` should stop drawing the chain/float fence and pile clusters and draw instead raft-mats moored along a slack bank off the lumber yard (about a third of the river's width, never more than two fifths), or a pond off the river joined by a canal; Minami gets moored rafts - searched 2026-09-28: Japanese 網場, 綱場, 筏溜, 木場, 貯木 with Edo; kotobank 綱場 and 錦織綱場跡, ja.wikipedia 網場, 木材流送, 木場, 白鳥貯木場, the Kiso forestry office's page; Chinese 木排, 木簰, 拦木, 停泊 at Parrot Island (Hanyang) and the Qingshui markets; English log booms in premodern Japan and China. The GM did not rule the pen form in; it came from a research pass answering the GM's question about how booms worked (2026-08-02), not a ruling on its period.

M104 MODERN-ONLY - the record (150) now says the cooling rule is today's handling guidance and that the older record cools charcoal at the kiln (black charcoal in the sealed kiln, late Muromachi into Edo; white charcoal smothered beside the kiln under ash and sand), so charcoal reached a town cooled and baled; and that no premodern figure for a gap round a charcoal store was found (the 30 ft rests on modern wildfire guidance), Edo's rule on a feared fuel stock being to move the trade (timber dealers to Eitaijima after 1641) - CharcoalStore / WeighingFloor / TallyOffice (`compound_kinds/office.py`, `grounds.py`) and `settlement/trades.py` should stop drawing the open cooling apron and stop enforcing the measured 30 ft gap (how far the yard stands from houses is a guess); the tallied depot and weighing floor stand (Ubame, Minami, the magistracy sheets) - searched 2026-09-28: Japanese 炭問屋, 薪炭問屋, 炭置場, 炭蔵, 町触 with fire, charcoal self-ignition in Edo, 消し粉, 窯出し; kotobank 薪炭問屋, ja.wikipedia 木炭, JIFPRO charcoal page, a Tama local-history page on charcoal for Edo; Chinese 天工开物 木炭, 烧炭, 冷却, 贮存. Not ruled in by the GM; the apron and gap were this project's derivation.

M105 MIXED - the record (190) now says the bale and its capacities are premodern (Edo bales of 3 to 3 sho 3 go, 4 to and 5 to by domain, the 4-to/60 kg bale a Meiji rule) but every measured size is modern (a display 4-to bale 75 x 47 cm; a mid-Showa charcoal bale 63 x 39 x 32 cm), and gives the premodern calibration as a labeled guess: scaled by the cube root of capacity, the shogunate's 3 to 5 sho bale about 2.4 x 1.5 ft, a 5-to bale about 2.7 x 1.7 ft, within a tenth of the modern 2.5 x 1.5 ft - TaxBarge (`particulars.py:311`) and CharcoalBales (`particulars.py:414`) need no change to the drawn glyph (the ~4 ft bale is a convention either way); their "real size" notes should say the rice figure is the modern bale's, within a tenth of an Edo bale by the guess, and the charcoal figure a 20th-century bale's with no older one measured (Hayakawa, Ubame) - searched 2026-09-28: Japanese bale dimensions in shaku and cm, Edo bales in museums and excavations, the farm manuals' and Jikata Hanreiroku's bale passages; English Edo rice-bale dimensions; the NDL reference answer on grain-reserve storehouses (read: capacities, no size). Not ruled in by the GM.

M106 PREMODERN-ATTESTED - the record (520) now says Edo tax rice and market rice were threshed and hulled brown rice before leaving the village (National Tax College), the village delivering its baled tax rice to the lord's storehouse (in Dewa via the village storehouse to Sakata), so the rice reaching a town came hulled - no change: nothing is drawn for hulling in town, and the rule stands on a premodern attestation now rather than on the clay-mill page alone. Not a GM ruling; a research outcome of feature 271.

## Open

- 150's heading still names "a cooling ground" (anchor kept stable; the prose says none is drawn). Renaming it owes the inbound links and Entry: tags - left for the orchestrator with the engine change.
- 040 and 720 are both needed until the engine change: 040 still describes the American gear as the analog; once `s.log_boom` is changed, 040's glyph description (the decisions item) should be re-read against the new form.
- test_footnotes fails only on towns.html [^99] (T2's, pre-existing).
- No source for the GM to download.
