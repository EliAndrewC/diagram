# Research - feature 279

The research itself is on the record: `research/religion-and-death/`
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

`LONG_RUN` (added after the settlement-review of 2026-09-28, which found a `114 ft` east edge within `8 ft` of a plumb
line that `STRAIGHT_RUN`'s four-crown window could not see): any stretch of consecutive edge crowns whose chord is
`150 sheet px` (`50 ft`) or more and whose crowns all lie within the smallest crown radius of that chord.

The outer sides (added after the settlement-review's second round, which found the wood's two outer edges still a
near-plumb parallel pair where the old box's sides were): the drawn silhouette - the union of the crowns - sampled
every `1 px` down each side, a best-fit line through each; a side that stays within a crown radius of its line reads
as ruled. (A first version took the outermost crown centered in each band, which let an interior crown stand for the
edge; the building-review's fourth round measured the silhouette instead.)

## R3 - every text that placed a feature against the old grove, and what it says now

Found 2026-09-28 by `grep -n -i grove` over every file the sheet renders from - `pool/country-shrines/hoshigaoka-shrine/`
(notes, svg), `l7r/diagram/interactive/compound_kinds/shrine.py` and `grounds.py`, the country-shrine part of
`buildings/programs.md` and `types.json` - and over the owed list; each hit read and ruled on.

| where | said | now |
|---|---|---|
| notes, the precinct bullet | "The precinct is the grove", the wood "several crowns deep behind the hall", `138 canopies over 60%` of the precinct (feature 270's figure) | the precinct holds its wood behind the hall and at its sides; 134 canopies (m:grove-trees-hoshigaoka), covering 0.896 of the ground they may cover (m:grove-canopy-share-hoshigaoka) |
| notes, the clearing bullet | "so is the grove's own edge"; the footpath "through the grove to the well" | "so are the wood's edges"; the path through the wood behind the hall |
| notes, the arches bullet | the outermost "at the grove's edge"; the approach "from the grove's edge" | at the precinct's edge, in open ground below the wood's tips |
| notes, the sacred tree bullet | "the grove's biggest"; the arches "from the grove's edge" | the precinct's biggest, alone below the wood's east tip; from the precinct's edge |
| notes, knob list and header | seven knobs | knob 8, `behind and sides`, with the mid-slope candidates and the roll's exact call; the `**Grove form**:` line |
| notes, the trees bullet | "a seeded dart-throw inside the grove" | inside the wood's outline |
| notes, Map notes `torii` | "the outermost at the grove's edge" | at the precinct's edge |
| notes, Map notes `shrine grove` | "the precinct itself ... 137 by 215 ft, from the well at its back edge" | the wood behind the hall and at its sides, the form and why |
| notes, Map notes `well` | "at the grove's back edge" | at the wood's back edge |
| notes, line 11 (the sheet matches the map), line 27 (knob 4, "the grove the map now draws") | true under sides | unchanged |
| svg, the header comment and the subtitle | "the hall in its grove", "the well at the grove's back"; the subtitle "in its wood" | the hall in its wood, behind and at its sides; the well at the wood's back edge; the subtitle without "in its wood" |
| svg, the parchment, precinct, floor, footpath, grove, approach, arches and well comments | the precinct is the grove; the grove's edge and back edge | restated to the precinct and its flanks |
| svg, the `grove-floor` pattern and "Add grove to map" (the GM's words) | true under sides | unchanged |
| `shrine.py` `SacredTree` What | "the grove's greatest tree" | the precinct's greatest tree |
| `shrine.py` `SweptClearing` What, Why, Covers | "inside the grove", "the grove left standing round it" | about the building; its wood left standing |
| `shrine.py` `Footpath` What, Why | "through the grove" | from the kitchen side to the well, off the sanctuary's ground |
| `shrine.py` `ShrineApproach` What, Covers | "from the grove's edge" | from where the way enters the precinct |
| `shrine.py` module docstring, line 5 | names the grove among the shared kinds | true, unchanged |
| `grounds.py` `ShrineGrove` What, Why, Note, Caveat, Entry | "around the compound's shrine, its hall and arch set in a cleared opening"; "rather than in cleared ground"; "draws a village shrine's precinct as its grove" | kept trees on the sides of the hall its ground gives them; the forms by the ground; the edge and the roll as guesses; Entry names research 129 |
| `programs.md` composition rule, approach rule, size anchors, knob list; `types.json` notes | "the precinct is the grove"; the outermost arch "at the grove's edge" | the precinct holds its grove (knob 8); the precinct's edge; knob 8 |
| `future-work/farming-communities.md`, the shrine-grove entry | "a village shrine's precinct IS its grove"; fill the precinct | holds its grove in the form its ground gives; the knob, the roll, the edge, the open paddy question |
