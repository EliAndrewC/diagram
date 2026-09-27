# Feature 266 - research

## R1. What the cartographic standard says, and where it can be read (2026-09-27)

A reader agent (Sonnet, background) searched for the standard and saved every page it quotes with
`make source-pages`. The saved text is under the job scratch directory `labels/`. The passages below were
re-checked against those saved files by the session with grep. They are VERBATIM.

**Point labels have two primary factors.** Penn State GEOG 486, "Point labels"
(https://courses.ems.psu.edu/geog486/node/557, public, CC BY-NC-SA): "When placing point labels, two factors are
of primary importance: (1) legibility, and (2) association." And: "your labels should be shifted up or down from
their associated point feature." On the gap: "how closely your labels and points are placed will depend on the
size, shape, and density of your labels, points, and map. Most important is maintaining consistency throughout
your map design." The same paragraph: "map elements that appear too tightly packed are generally undesirable". On
leaders: "Leader lines can be used to connect features with labels that do not fit on or directly adjacent to their
respective feature on the map." and "use leader lines sparingly." On lines: "(1) follow the feature, but not at the expense of legibility, (2) place labels above
lines rather than below, (3) don't write upside down." It lists Imhof 1975 as reading and notes that authorities
differ slightly on the exact ranking ("cartographers do not always agree on this specific order").

**The ranked positions around a point.** QGIS 3.44 user manual, "Label settings"
(https://docs.qgis.org/3.44/en/docs/user_manual/style_library/label_settings.html, public): "following a Position
priority which dictates placement candidates for anchoring labels around and (centered) over the point feature,
and the order in which the positions are tested. The default order, based on guidelines from Krygier and Wood
(2011) and other cartographic textbooks, is as follows: top right top left bottom right bottom left middle right
middle left top, slightly right bottom, slightly left." And, for its Cartographic mode: "The placement priority is
clockwise from the "top right"." The distance: "Labels can be placed: at a set Distance in supported units, either
from the point feature itself or from the bounds of the symbol used to represent the feature". Two options decide
between nearness and position, and the DEFAULT is nearness: "There are two options: Prefer closer labels: By
default, labels are kept close to the feature." The other is the non-default "Prefer position ordering: The label
will try to stay in a specific position (like top left or top right), even if it's a bit farther away from the
feature. The label only moves to other positions if there's no room within the maximum distance at your preferred
position." For an area, its Around Centroid mode: "Around Centroid: places the label within a preset distance around
the centroid, with a preference for the placement directly over the centroid"; and, of its Horizontal and Free
polygon modes (not Around Centroid): "The preferred placement is further from the edges of the polygon."

**The cost formulation.** Christensen, Marks & Shieber, "An Empirical Study of Algorithms for Point-Feature Label
Placement", ACM Transactions on Graphics 14(3), 1995 (public PDF on the author's site,
https://www.eecs.harvard.edu/~shieber/Biblio/Papers/tog-final.pdf): "In Yoeli's scheme, the quality of a labeling
depends on the following factors: • The amount of overlap between text labels and graphical features (including
other text labels); • A priori preferences among a canonical set of potential label positions (a standard ranking
is shown in Figure 1); and • The number of point features left unlabeled." And: "Figure 1 shows a typical set of
eight possible label positions for a point feature." They also cite Imhof (1962; 1975) as the cartographers' study
of labeling quality.

**The offset and its maximum.** Esri ArcGIS Pro, "Offset point labels"
(https://pro.arcgis.com/en/pro-app/latest/help/mapping/text/offset-point-labels.htm, public): "The label offset
controls the distance a label is placed from its feature. The offset is measured from the boundary of the feature
symbol to the outer edge of the label"; "A value of 0 will cause the label to touch the symbol boundary."; "The
default value for the maximum offset is 100 percent of, or equal to, the preferred offset. A maximum offset value
of 200 percent would allow the label to be placed up to twice the preferred offset from the feature."; "Add a
callout with a leader line to the label symbol to remove ambiguity and place the labels up to the maximum offset."

**Overlap versus moving away.** Esri ArcGIS Pro, "Weight labels and features"
(https://pro.arcgis.com/en/pro-app/latest/help/mapping/text/weight-labels-and-features.htm): "A feature weight of
0 indicates that the feature should be treated as available space, while a weight of 1,000 indicates that the
feature is considered an obstacle and should not be overlapped by labels. The Maplex Label Engine first attempts to
place labels in an area of free space. If there is no free space available and a feature must be overlapped, a
location with the lowest total feature weight is chosen." Esri, "Prevent labels from overlapping certain features"
(https://pro.arcgis.com/en/pro-app/latest/help/mapping/text/prevent-labels-from-overlapping-certain-features.htm):
"If it is not possible to place labels where they do not cross a road feature, they are moved to a position where
they only cross one road instead of several."

**Leader lines.** QGIS, same manual, Callouts: "A common practice when placing labels on a crowded map is to use
callouts - labels which are placed outside (or displaced from) their associated feature are identified with a
dynamic line connecting the label and the feature." Esri adds the leader "to remove ambiguity and place the labels up
to the maximum offset" - that is, in the band beyond the preferred offset - and PSU (above) connects "labels that do
not fit on or directly adjacent to their respective feature" and says to use them "sparingly". All three tie the
leader to a label no longer directly adjacent at its preferred offset. Esri's default maximum offset is 100 percent
of the preferred (a label does not leave its preferred offset at all); 200 percent is its worked example.

**A rotated feature's label.** Esri ArcGIS Pro, "Set point label rotation"
(https://pro.arcgis.com/en/pro-app/latest/help/mapping/text/set-label-rotation-using-a-numeric-field.htm): "The
selected placement position is overridden, and the placement is determined by the angle when you choose to rotate
labels by an attribute value." Krygier, GEOG 353 lecture notes
(https://krygier.owu.edu/krygier_html/geog_353/geog_353_lo/geog_353_lo10.html): "Horizontal type is easiest to
locate and read."

**What no readable source settles.**
- Imhof's own text (The American Cartographer 2(2), 1975; the 1962 German original) - paywalled at Taylor &
  Francis (403); Semantic Scholar and SciSpace render nothing. Yoeli 1972 (The Cartographic Journal 9(2)) -
  bibliographic record only. Both go on the GM's download list.
- A NUMERIC gap. No source gives one: Esri and QGIS leave the preferred offset to the map's author (0 allowed),
  Mapbox's `text-radial-offset` defaults to 0 ems, and PSU names consistency as what matters most.
- A numeric leader trigger. Both tools tie the leader to going beyond the normal (preferred) offset, never to a
  stated distance.
- "Cross a line at a right angle" - not found in any of these; the readable rule is Esri's count rule (cross one
  way instead of several).

## R2. The shipped notice-board captions, measured (2026-09-27)

Observed 2026-09-27; method: from each pool hamlet's manifest (`kosatsuba[0]` and its `labels` record), the gap between the caption's drawn,
rotated block and the board's rotated footprint, and the caption's center in the board's own frame:

| hamlet (observed 2026-09-27, method: manifest geometry) | board rot | gap | text block height | center along the board | center across |
|---|---|---|---|---|---|
| Inashiro | 47.3 | 12.3 ft | 8.4 ft | -16.6 ft | 19.0 ft |
| Kashikawa | 126.3 | 14.0 ft | 8.4 ft | 28.2 ft | 20.7 ft |
| Kuwabata | 95.1 | 17.0 ft | 8.4 ft | -2.1 ft | 23.7 ft |
| Mizuguchi | 80.4 | 17.5 ft | 8.4 ft | -2.3 ft | 24.2 ft |
| Sawada | 99.2 | 20.1 ft | 8.4 ft | -2.1 ft | 26.8 ft |

So the gap runs 1.5x to 2.4x the text's own height, and two captions are also slid well along the board (observed
2026-09-27, method: the table above).
The cause, read from `structures/fixtures/boards.py`: the candidate seats are laid out on the PAGE's axes from
hand-chosen gaps (`+11`, `+8`, then `+12` steps to `60 px`, and a twelve-bearing annulus), while the caption is drawn
at the board's angle; the search takes the nearest seat that clears lanes and wells by `3 ft`.

## R3. Every label on every live map, by how its seat is chosen (observed 2026-09-27; method: grep over `l7r/` and `pool/`, `<text` counts with `grep -c`)

The live maps are the five scripted hamlets, the two magistracy sheets `compound.py` draws
(`county-magistracy-example`, `ochiba-roundtrip-test`), the three hand-authored magistracy sheets (`hayakawa`,
`ochiba`, `ubame`) and the hand-authored country shrine (`hoshigaoka-shrine`). The first census counted the
settlement engine only and missed every Mode A sheet; `spec-fidelity` found it (review history, round 0).

**Mode B, the settlement engine (`settlement/`).**
- Searched in the label phase: the notice board (`_draw_board_caption`, its own annulus search), the deferred
  building captions (`place_caption` -> `_best_label_spot`, called in the town tier), the Imperial road's caption
  (`_finish_road_label` -> `_best_label_spot`, town and city) and the field names (`field_name_label`, fixed at the
  field's center). Of these only the notice board is on a live map: every pool hamlet's `labels` holds exactly one
  record, "notice board".
- Hand-seated by their callers: 51 `self.label(x, y, ...)` calls, a few of them inside the label machinery itself,
  the rest in the town, city and capital tiers, whose coordinates the calling code computes. By function (an AST walk over
  `settlement/`): four are the label machinery itself or captions this feature converts (`captions.py` `place_labels` and
  `_draw_queued_label`, `boards.py` `_draw_board_caption`, `ground.py` `_finish_road_label`); the other 47, in 33
  functions, belong to the town, city and capital tiers (a ministry's name
  written across its own roof, a hall caption a fixed drop below it). No live generator runs any of those 47; the maps
  that used them are frozen exhibits.

**Mode A, the compound composer (`compound.py`), live.** Every caption is hand-seated at a fixed offset: the zone
names and building names at the center of their own rectangle, "striking posts", "bath", "well", "latrine",
"fire-water tubs", and the notice board's caption at `(gl - 11.0, env.h_ft + 9.0)` beside the board outside the
gate. Two pool sheets are drawn by it.

**Mode A, hand-authored sheets, live.** The SVG is the source and a session writes it; every caption is placed by
hand. `<text` elements (titles and scale bars included): hayakawa 83, ochiba 65, ubame 85, hoshigaoka-shrine 16;
the compound-drawn sheets 33 and 35. Each magistracy sheet carries a notice board and its caption; the shrine has
none. Every drawn element carries a `data-kind` tag (feature 262), so a tool can read which shapes are which.
The three hand-authored magistracy sheets are the active work of another feature (264) at the time of writing.

## R4. Two figures the spec uses (observed 2026-09-27; method: read from the code)

- The "notice board" caption is 53 ft long on a hamlet (observed 2026-09-27, method: the arithmetic below): `label()` sizes a line as characters x size x 0.55, so
  12 characters at 8 pt is 52.8 px, 1 ft per px at hamlet scale. The board itself is 12 by 5 ft
  (`kosatsuba`, `vw`/`vh` in every pool manifest).
- The engine's house standoff (observed 2026-09-27, method: read from the code) `LABEL_MIN_AIR = 5.0` px (`settlement/_geom/labels.py`) is 0.56 em on a 9 pt
  caption: 5 / 9.

## R5. The board captions after the placer (observed 2026-09-27; method: as R2 - the caption block against the board footprint in each regenerated manifest, and on the two composed sheets read with the seat-label reader)

| map (observed 2026-09-27, method: manifest and sheet geometry) | gap before | gap after | leader |
|---|---|---|---|
| Inashiro | 12.3 ft | 3.9 ft | none |
| Kashikawa | 14.0 ft | 4.0 ft | none |
| Kuwabata | 17.0 ft | 4.0 ft | none |
| Mizuguchi | 17.5 ft | 4.1 ft | none |
| Sawada | 20.1 ft | 4.0 ft | none |
| county-magistracy-example (7 pt, 3 px/ft) | - | 4.2 px | none |
| ochiba-roundtrip-test (7 pt, 3 px/ft) | - | 3.6 px | none |

Every board caption now stands at the preferred offset (0.5 em: 4 ft on an 8 pt hamlet caption, 3.5 px on a 7 pt
draft caption, the draft's rects rounded to whole pixels), at the board's own angle, with no leader - a free ranked seat
existed beside every board. The three hand-drawn magistracy sheets' board captions were re-seated with
`make seat-label WRITE=1` and check clean.
