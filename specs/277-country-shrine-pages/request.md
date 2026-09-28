# Feature 277 - the GM's request, verbatim (2026-09-28)

> Okay, can you make a scripted process for turning country shrine maps into interactive HTML maps? Basically, this is just what we have already done for magistracy buildings. Like that same process. that we use to avoid repeating ourselves by defining the same thing in multiple places and instead having both the PNG file and the interactive HTML downstream of the same single canonical data source that describes the map features and such.

## Context (measured 2026-09-28 on the one country-shrine sheet, pool/country-shrines/hoshigaoka-shrine/)

- The magistracy process (feature 262): the tracked, hand-authored sheet SVG is the ONE source; each element carries
  `data-kind`; the map's `.gen.py` renders the PNG from it AND writes `<map>.html` with `write_sheet_page(svg,
  COMPOUND_CLASSES)`, failing on untagged ink or an unregistered kind; the kinds' write-ups are docstrings in
  `l7r/diagram/interactive/compound_kinds/`; `tests/interactive/test_compound_kinds.py` holds every sheet complete and
  the registry closed over the maps it serves.
- The shrine sheet already carries `data-kind` on most of its ink (268/270 drew it with tags), and the page writer runs
  on it: 7 kinds are unregistered (approach, basin, hall and dwelling, sacred tree, sanctuary, the monk's rooms, writing
  room) and 5 elements untagged (background, precinct outline, two ground polygons, the well footpath). Its `.gen.py`
  renders only the PNG.
