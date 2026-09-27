# 271 V5 handoff - archetypes: terraces, overlays and polders (session 1: research and write)

Written 2026-09-27 in clone diagram-research-2. One source-reader pass over 28 claims (27 READ, 1 NOT-FOUND,
none contradicted); everything written rests on a READ quote. The record checks are NOT run - they are the
check sessions' work.

## Sections

- SECTION=archetypes/300
- SECTION=archetypes/310
- SECTION=archetypes/320
- SECTION=archetypes/330
- SECTION=archetypes/340
- SECTION=archetypes/020
- SECTION=archetypes/080
- SECTION=archetypes/150
- SECTION=archetypes/160

## Registry keys

- KEY=wuhurec-wanchun
- KEY=fukui-kuzuryu-edo-dikes
- KEY=wajyu-nogyo
- KEY=ishizue-ariake
- KEY=people-longgu-shuiche
- KEY=njg-horita
- KEY=kotobank-tanada
- KEY=chikuma-obasute
- KEY=bunka-shiroyone
- KEY=sakaori-ishizumi
- KEY=kotobank-warichi-seido
- KEY=kotobank-bunsan-sakuho
- KEY=tokyo-ja-kasai-renkon
- KEY=katsushika-renkon
- KEY=pwsannong-zhuwei

Shared, not new here: `chaen-jawiki` (11600) is held by 271 V6 in diagram-research-3 and
`l7r-merchant-families` (13810) by 271 V7 in diagram-research-1, both unpushed; `make reserve` refused them, so
this clone carries BYTE-IDENTICAL copies (a merge sees the same add twice). Their `Used for:` lines should gain
"(archetypes)" once, in the owner's copy. Likewise the glossary term `keihan-cha` (10900) is V6's, copied
verbatim. New glossary terms here: `horita` (12990), `hakehi` (13000), `warichi` (13010).

## Items

- A12 KNOB - a terrace paddy runs from about 20 m2 on the steepest ground (Shiroyone) through about a quarter of a tan (the old register notation) to about 270-420 m2 (Obasute, a 1-in-7 slope); walls are higher and paddies smaller the steeper the ground (Sakaori), and the wall's FORM is attested two ways - a near-vertical stone face (western Japan) or a sloping earth bank (eastern Japan; Shiroyone) - while no Japanese page gives a wall height in meters (absence; the record's 0.8-1.5 m stays the FAO figure on fields/024) - for the generator: paddy size tied to slope as a calibrated liberty (bench depth = wall height x run per rise), and the wall form a knob rolled per settlement; no scripted generator draws terraces yet, so nothing re-draws until one does.
- A21 KNOB - tea had two forms, the hillside garden and Japan's bund tea (one row of bushes along field banks, taking no plot); mulberry on a polder stood in rows along the dike crest (Wanchun, 1061); lotus was grown only a little before the Meiji market and whole-district lotus is a late crop near a great city; the lotus share of a village's paddy stays unsourced (absence) - for the generator: tea rolls between the hill fringe and a bund-row form; on a non-dike-pond polder mulberry belongs on the dike crest (the perimeter dike already draws an inner mulberry row, consistent); lotus belongs at the low end, which puts the GM's 2026-07-19 liberty (upper part of the band) further from what was read - raised for the GM, NOT changed.
- A24 ACCURATE - a household's land was small parcels scattered among its neighbors' (the pre-reform pattern), warichi re-divided fields by lot in unstable lowland and landslide villages with one part of every quality group to each lot, and in the setting most farmers are tenants; nothing read says tenure or tenancy left any mark on the ground (absence) - for the generator: nothing to change; the maps are right to draw no holdings, no household blocks and no tenant marking.
- A62 ACCURATE (bounds; a village polder's own dike SILENT) - the Wanchun polder's dike was six zhang broad and one zhang two chi high (foot five times the height), crown only a few chi, planted with mulberry and willow with reeds at its foot; an early Edo river dike was about 5.45 m base, 1.82 m crown, 3.64 m high; a Mino waju dike was fixed 1 m lower than Owari's great dike by agreement; a Fukutsuka drain culvert through the ring was 41.1 m long - for the generator: a dike's size is a calibrated liberty scaled by the polder; a village polder's dike belongs under about 3.6 m high on about 5.5 m of foot. MEASURE the perimeter dike band (drawn 14-40 px across, `settlement/land/dikes.py`) in feet on the Kuwabata manifest and say whether it sits inside those bounds; I did not convert px to feet.
- A66 KNOB + CONTRADICTION-RESOLVED - a polder drained by gravity through gated culverts (hakehi) opened when the water outside fell, intake at the high end and outlet at the low, as many as its size needed (Fukutsuka 1789-1872: 34 drains, 1 gate, 4 intakes); by the chain pump lifting water out in flood; or, where it stayed waterlogged, by raising the rice on horita strips with boat channels between (Japan, about 1753 to 1975); a sea polder's outlet worked the same way against the tide (the tide operation itself is absence-noted) - for the generator: two sluices are fine for a village polder, drains should sit at the low end and intakes at the high (the pool polders already do); horita is a knob a Japanese polder may roll in place of ordinary paddy. CONTRADICTION-RESOLVED: archetypes/160 said water crossed "only at the two gated sluices" as if a property of polders; it now says the pool maps draw two and a larger polder had as many as it needed.

## Owed to other owners

- 269 B35 (archetypes/040): its sentence "the leveled cell stays the size it is everywhere else" is contradicted by archetypes/300 - terrace paddies scale with slope, from about 20 m2 (Shiroyone) to a few hundred (Obasute). Its two absence notes can cite `kotobank-tanada` ("on steep mountain ground the paddies become narrow strips with fairly high vertical walls between tiers, kept with stone") and `tanada-jawiki`; and it should point to 300 for wall and paddy size.
- 269 B35 (archetypes/050): may point to 320 for whether tenure shows in the plot pattern.
- archetypes/030 (no owner named in either inventory): its note "bund-margin tea (keihan-cha) is a Japanese practice with no Chinese equivalent" is labeled absent, but `chaen-jawiki` now attests bund tea in Japan (310); the Chinese half stays unsourced.

## Left open

- The lotus liberty (020) is the GM's; the evidence read now points at the low end of its band. For the GM, via escalation-check.
- The ~1.5 m small-polder dike (160) stays unsourced; the Ming polder-building manuals (陈瑚《筑圩说》, 孙峻《筑圩图说》) named by `pwsannong-zhuwei` would likely give it, but no readable text was found.
- Unreadable here and worth a GM download if the figures matter: J-STAGE `suirikagaku/61/5/61_41` (Suetsugi, Edo water-management techniques, PDF) and `journalhs1981/9/0/9_0_123` (Chino, river dikes in early modern documents, PDF). Not added to TO-DOWNLOAD.md: both are public PDFs the container could not text-extract, not GM-only fetches.
- Entry drift: bodies of 020, 080, 150 and 160 changed (pointers and one citation; 160's sluice sentence reworded) - `_entry_owed.py` will name their classes at push.
