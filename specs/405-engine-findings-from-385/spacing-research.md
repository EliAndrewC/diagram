# How much room a clustered hamlet's farms take - the research pass of 2026-10-22 (T107)

Load this file when: moving a homestead size or spacing knob (`HOMESTEAD_GROUND_FT`, `SEATING_GROUND_FT`, `grow_gap`,
`MIN_WEB_GAP`), or writing the room table's ceilings. The pass was run by the `research-pass` agent at the GM's request
(2026-10-21: "run the spacing research pass ... then do that task by widening the spacing within that bound"). Its findings
are not yet on a research page: a page session writes them (the house-lot question, beside 0031).

## Verdict: ATTESTED ONLY FOR the cases below

- **House-lot area, Japan (primary, 1698).** Hyakken-honmura, Musashi: 「元禄十一年 新御水帳書抜百姓壱人別名寄帳」, 34 house-lot
  (屋敷) entries summing exactly to the register's 「屋敷合壱町九反拾壱歩」 (5,711 bu). Per lot, in tsubo (sq m):
  min 42 (139), lower quartile 86 (285), **median 157 (519)**, mean 168 (555), upper quartile 227 (749), max 480 (1,587).
  Sides mostly 8-12 ken (15-22 m) by up to 29 ken (53 m). Upland ground; the source does not say the village was clustered.
  Archived `miyashiro-hyakken-honmura-shiryo`.
- **Farmstead area, China (1922-1925 survey).** Buck, *Chinese Farm Economy* (1930), Table 3, seven localities' average:
  about 0.06 ha (about 600 sq m, about 180 tsubo) of buildings and threshing floor per farm; 「farmsteads which are usually
  located in villages or hamlets of varying size」.
- **House lots, a Manchu village of the late 17th century (modern measurement).** Ushijima et al., *Japan Architectural
  Review* 3:3 (2020): 「Many housing lots have sizes of 300-500 m2 while there are only a few housing lots of more than
  1000 m2」; widths mostly 30 m or less; width to depth near 1:2.
- **Spacing, scattered form only.** Tonami: 「相互に100～200m内外の間隔をおき」 (translation: "standing about 100-200 m apart").
- **Spacing, row form only.** Santome (1694-1696): 「間口40間（72m）×奥行き375間（675m）」 (translation: "frontage 40 ken (72 m) by
  375 ken (675 m) deep").

SILENT: any measured distance between neighboring houses in a clustered village; premodern Chinese lot figures; any imperial
regulation of lot size (not searched). Leads: Huizhou fish-scale registers (屋基 in 步), the South Manchuria Railway's North
China village surveys, the Tonami 小島 sanson PDFs.

## What it means for the generator

- A typical clustered-village lot is about 300-600 sq m (90-180 tsubo); a large one 1,000-1,600 sq m (300-480 tsubo), rare.
- `HOMESTEAD_GROUND_FT` (104 ft square, about 1,000 sq m, about 305 tsubo) sits above the typical range, at the rare band's
  floor: three of the 1698 register's 34 lots exceed it.
- `SEATING_GROUND_FT` (162 ft square, about 735 tsubo) counts the household's wood floor too (6,000 sq ft, `HOMESTEAD_WOOD_FT2`),
  which a 屋敷 lot need not hold, so it does not compare directly - but it is above every lot found.
- So the homesteads already stand **above the typical attested lot and inside the rare band**: some widening stays within the
  research, but it moves the maps further from the typical lot. Whether the homesteads should come down toward the median
  is its own question (T112), not worked inside T107.

## Measured on the cohort (T26's wood-shed change in the tree, seeds 1-48 and the pinned rows)

| `grow_gap` | newly failing | record |
|---|---|---|
| 18 + 2 ft (main's) | 10, 24, 36, 47 | `dev/cohort-log/20261022T034510Z-*` |
| 23 + 2 ft | 8, 18, 20, 36, 41, 47 | `dev/cohort-log/20261022T034941Z-*` |
| 28 + 2 ft | the reference map Inashiro refused (a farmhouse no way came within 80 ft of) | stopped at the reference |

Wider spacing made the cohort worse, not better: the band and canvas the seats are dealt over do not grow with the gap.
