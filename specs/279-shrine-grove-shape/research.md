# Research - feature 279

The research itself is on the record: `research/religion-and-death/129-what-shape-is-a-village-shrines-wood-and-on-which-sides-of-the-hall-does-it-stand.html`
(its sources, checks and reader reports as run 2026-09-28). This file holds only what the spec measures.

## R1 - the grove as drawn before this feature

Observed 2026-09-28; method: the manifest's `village_groves` record of role `shrine` in
`legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json` - w 68.3 by h 107.7 map px, at the map's 2 ft to
the px (`meta.ftpx`) - 136.6 by 215.4 ft, the precinct box of feature 268's layout (sheet px 220-630 by 170-816,
3 px to the ft). The render shows the crowns filling that box to straight sides.

## R2 - the `STRAIGHT_RUN` bar

A chosen bar, not a measurement. The smallest crown the layout throws is `19.5 sheet px` in radius, `6.5 ft` (the layout's own
constant, not a measurement); a run of
four edge crowns whose centers all lie within `2 ft` (a third of that radius) of one line reads as a ruled edge.
Measured by the layout script on the tree list: the edge crowns (centers within a crown's radius plus `6 px` of the
grove region's outline), ordered along the outline; every window of four is tested against the line through its
first and last.

## R3 - every text that placed a feature against the old grove, and what it says now

Found 2026-09-28 by `grep -n -i grove` over every file the sheet renders from - `pool/country-shrines/hoshigaoka-shrine/`
(notes, svg), `l7r/diagram/interactive/compound_kinds/shrine.py` and `grounds.py`, the country-shrine part of
`buildings/programs.md` and `types.json` - and over the owed list; each hit read and ruled on.

| where | said | now |
|---|---|---|
| notes, the precinct bullet | "The precinct is the grove", the wood "several crowns deep behind the hall", `138 canopies over 60%` of the precinct (feature 270's figure) | the precinct holds its wood at its sides; the flanks, 84 canopies (m:grove-trees-hoshigaoka), a canopy share of 0.653 of the flanks' ground (m:grove-canopy-share-hoshigaoka) |
| notes, the clearing bullet | "so is the grove's own edge"; the footpath "through the grove to the well" | "so are the wood's edges"; the path across the open ground behind the hall |
| notes, the arches bullet | the outermost "at the grove's edge"; the approach "from the grove's edge" | at the precinct's edge, in open ground below the flanks |
| notes, the sacred tree bullet | "the grove's biggest"; the arches "from the grove's edge" | the precinct's biggest, alone below the east flank; from the precinct's edge |
| notes, knob list | seven knobs | knob 8, `sides`, with the roll's exact call |
| notes, the trees bullet | "a seeded dart-throw inside the grove" | inside the two flanks' outlines |
| notes, Map notes `torii` | "the outermost at the grove's edge" | at the precinct's edge |
| notes, Map notes `shrine grove` | "the precinct itself ... 137 by 215 ft, from the well at its back edge" | the wood at the precinct's sides, the form and why |
| notes, Map notes `well` | "at the grove's back edge" | in the open ground at the precinct's back edge |
| notes, line 11 (the sheet matches the map), line 27 (knob 4, "the grove the map now draws") | true under sides | unchanged |
| svg, the header comment | "the hall in its grove", "the well at the grove's back" | the hall and its wood at its sides; the well behind the hall |
| svg, the parchment, precinct, floor, footpath, grove, approach, arches and well comments | the precinct is the grove; the grove's edge and back edge | restated to the precinct and its flanks |
| svg, the `grove-floor` pattern and "Add grove to map" (the GM's words) | true under sides | unchanged |
| `shrine.py` `SacredTree` What | "the grove's greatest tree" | the precinct's greatest tree |
| `shrine.py` `SweptClearing` What, Why, Covers | "inside the grove", "the grove left standing round it" | about the building; its wood left standing |
| `shrine.py` `Footpath` What, Why | "through the grove" | from the kitchen side to the well, off the sanctuary's ground |
| `shrine.py` `ShrineApproach` What, Covers | "from the grove's edge" | from where the way enters the precinct |
| `shrine.py` module docstring, line 5 | names the grove among the shared kinds | true, unchanged |
| `grounds.py` `ShrineGrove` Why, Note, Caveat, Entry | "draws a village shrine's precinct as its grove"; the wood fills the unbuilt ground | the forms by the ground; the edge and the roll as guesses; Entry names research 129 |
| `programs.md` composition rule, approach rule, size anchors, knob list; `types.json` notes | "the precinct is the grove"; the outermost arch "at the grove's edge" | the precinct holds its grove (knob 8); the precinct's edge; knob 8 |
| `future-work/farming-communities.md`, the shrine-grove entry | "a village shrine's precinct IS its grove"; fill the precinct | holds its grove in the form its ground gives; the knob, the roll, the edge, the open paddy question |
