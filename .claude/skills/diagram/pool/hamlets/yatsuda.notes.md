# Design notes: Yatsuda (谷津田), the RIBBON-VALLEY hamlet

*Reconstructed 2026-08-08 from the generator's docstring and comments.*

**Subject**: a hamlet of 16 households whose paddy is a **ribbon meandering down a narrow valley
floor** - `field_archetype="ribbon_valley"`, `terrain="narrow_valley"`, drawn by `build_ribbon`.

**Why it exists**: it is a field-GEOMETRY archetype for **confined valley ground**, where there is no
room for either an organic fan or a surveyed grid - the cultivable land is the valley floor itself,
so the field takes the valley's shape and the settlement takes what dry flank is left.

## Map notes

<!-- READ BY THE INTERACTIVE MAP (`l7r/diagram/interactive/notes.py`, feature 156): these bullets
     appear on the page's title card and in feature modals. Everything is optional and the reader is
     forgiving by design (GM 2026-08-29: "we should not presume that such sections exist ... should
     default to simply not pulling anything in if the parsing fails") - a missing, misspelled or
     half-written block simply contributes nothing. The key list and the format are documented in
     `l7r/diagram/interactive/CLAUDE.md`. Every other word in this file is prose and is never parsed. -->

### Place

- **district**: Takadani
- **district direction**: south

*Takadani (高谷, "high valley") is INVENTED for this map - drawn from gm-assistant's
`place-names/pool.jsonl`, which carries its kanji and meaning, and not ruled on by the GM. The
DIRECTION is not invented: it is the way this map's land falls (`meta.down_deg`), the wider ground a district's main village sits on.*

## Correction recorded 2026-08-08

The gen's docstring **described a polder** - a rectilinear block inside a perimeter dike, water in at
the high corner, the village on the dike - which is Enokida's map, copy-pasted. The declared
archetype and the actual call (`build_ribbon`, `terrain="narrow_valley"`) were always the ribbon
valley; only the prose was wrong. The docstring has been corrected. Worth knowing because a reviewer
reading the old text would have judged this map against the wrong archetype entirely.

## What makes it a hamlet, not a village

A hamlet is a small outlying community belonging to a village district, and the absences are the
definition: **no headman of its own** (its overseer, the district headman, lives in the main
village), **no shrine** (`religious_matches_scale`), **no tax-free plots**, and **no graveyard** -
its dead go to the village district's burial ground. Drawn at 1 ft/px, twice a village's pixel
scale, which keeps a ~15-household map a sensible size; the to-scale homestead bundle carries its
dimensions in FEET and draws them at `ftpx`, so the same 46x28 ft minka is 46 px here against 23 px
on a village sheet.

## Known open

- **No `notes.md` existed for this map until 2026-08-08**, so anything settled between its authoring
  and that date lives only in gen comments and may not be recorded here. Treat gaps as unrecorded
  rather than as decided.
