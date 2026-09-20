# Contract: the map declaration and the correspondence classes

## The declaration (a sheet's `.notes.md`)

One line, anywhere in the notes:

```text
**On map**: <manifest path from the skill root> - <manifest key> at (<x>, <y>) = <sheet id>
```

- `<manifest path>`: the Mode B map's recorded manifest, e.g.
  `legacy-hand-authored-pool/villages/hoshigaoka/hoshigaoka.json`. Never a generator.
- `<manifest key>`: the top-level list the subject is recorded in (`religious`, `houses`, ...).
- `(<x>, <y>)`: the subject's center in the map's own px; the check requires a feature of the key
  within the grain of it.
- `<sheet id>`: the `id` of the rect on the sheet that IS the subject (the shrine's `hall`); its center
  is the transform's origin.

A sheet with no such line is "on no map": the check reports that and nothing else.

## The transform

sheet px / 3 = ft (the Mode A scale); ft / `meta.ftpx` = map px; origin: the subject's center on
the sheet maps to `(x, y)`; north is up on both.

## The grain

`MAP_GRAIN_PX = 15` map px (`m:map-grain`, research.md R1).

## The classes

| sheet class | the sheet marks it | manifest keys |
|---|---|---|
| tree | a canopy circle (the canopy fill, or a `<g id="trees">`) | `tree_crowns`, `village_groves[*].clumps`, `forest_patches` |
| burial ground | `id="burial_ground"` | `cemeteries` |
| water point | `id="well"` or `id="basin"` | `wells` |
| arch | `id="arch"` | `torii` |
| water | `id="water"` | `streams`, `channels`, `pond`, `crescent_ponds` |
| lane | `id="lane"` | `lanes` |
| building | `id="building"` (any built footprint that is not the subject) | `houses`, `byres`, `farm_sheds`, `storehouses`, `buildings` |

A class the sheet marks that the table lacks is a finding.

## The findings

- (b) `<class> at svg(x,y) has no <class> on the map within <grain> (map (mx,my))`
- (c) `the map's <class> at map (mx,my) = svg(x,y) is inside the frame and not on the sheet`
- (d) `the subject is W x H ft on the sheet; the map draws it W' x H' ft`
- the declaration: `the manifest <path> cannot be read`, `no <key> feature within <grain> of (x, y)`,
  `the sheet marks id="<id>" and the check knows no such class`
- none: `on no map`
