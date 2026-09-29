# Feature 289 - research

Three readers, 2026-09-29 (session transcripts; the sources are public pages, quoted as the readers reported them).

## R1 - what the corner-first order is for

- Christensen, Marks & Shieber, "An Empirical Study of Algorithms for Point-Feature Label Placement" (ACM TOG 1995,
  https://www.eecs.harvard.edu/~shieber/Biblio/Papers/tog-final.pdf): the eight-position ranking is "a typical set of
  eight possible label positions for a point feature"; area features are left to other methods (van Roessel 1989,
  boxes inside the polygon).
- Ordnance Survey, "Text on maps" (https://docs.os.uk/more-than-maps/geographic-data-visualisation/guide-to-cartography/text-on-maps):
  "The text should ideally be positioned just above and to the right of the feature it is representing"; "If the
  feature is large enough, the label should be placed within it".
- QGIS, "Setting a label" (https://docs.qgis.org/3.44/en/docs/user_manual/style_library/label_settings.html): "The
  default order, based on guidelines from Krygier and Wood (2011) and other cartographic textbooks, is as follows: top
  right top left bottom right bottom left middle right middle left top, slightly right bottom, slightly left."
- Penn State GEOG 486 (https://courses.ems.psu.edu/geog486/node/557): "cartographers do not always agree on this
  specific order"; "adding point labels is not like making a bulleted list".
- Wu & Buttenfield 1991 (abstract only): Yoeli's prioritization "is not evident on the maps studied, and ... may be a
  matter of map publisher's preference".

## R2 - architecture

Room names go inside the room; small objects are keyed by a tag and leader to a legend (US National CAD Standard,
UDS Module 7 free sample, https://www.nationalcadstandard.org/ncs5/pdfs/ncs5_uds7.pdf: "a 'keyed' note consisted of an
alphanumeric indicator symbol and leader line with a legend of those symbols and the full text notes located elsewhere
on the drawing sheet"). No architectural source read ranks positions around a small object. The GM declined keynotes.

## R3 - other published orders

- Bobák, Čmolík & Čadík, "From Top-Right to User-Right" (IEEE 2024, https://arxiv.org/abs/2407.11996), Table 1:
  Robinson, Brewer, Dent and Slocum rank corners first; Imhof is reconstructed as TR, R, T, B, L; Zoraster's third
  model (1997) as T, TR, TL, R, L, BR, B, BL.
- Lexikon der Kartographie und Geomatik, "Schriftplatzierung"
  (https://www.spektrum.de/lexikon/kartographie-geomatik/schriftplatzierung/4424), citing Imhof 1962: "Für
  Positionssignaturen gilt die Platzierung der Schrift rechts neben dem Kartenzeichen als ideal." (For point symbols,
  placing the lettering directly to the right, beside the map symbol, is considered ideal - translation.)
- Mapbox GL JS, variable label placement (https://docs.mapbox.com/mapbox-gl-js/example/variable-label-placement/):
  `'text-variable-anchor': ['top', 'bottom', 'left', 'right']`.
- Not read (paywalled or not found): Imhof 1975/1962, Krygier & Wood, Brewer, Field, Dent, Slocum, Robinson, Tyner;
  the NCS note-location rules; ISO 128/4157/7519. No source found treats small drawn objects on large-scale plans as a
  case of their own.
