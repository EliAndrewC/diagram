# Data model - feature 257

- **Tree** (`parse.ParsedPlan.trees`): `Rect` bounding a canopy circle, `fill = TREE_FILL`; the circle's
  center and radius are recoverable from the rect. Classified by the canopy fill (own or the
  enclosing group's) or by a `<g id="trees">`. Not in `glyphs`.
- **Fence segment** (`parse.ParsedPlan.fence_segs`): a thin `Rect` per `<line>` inside `<g id="fence">`,
  as `wall_segs` are for the wall groups.
- **OnMap** (`report.OnMap`): `manifest: str` (path from the skill root), `key: str`, `x: float`,
  `y: float`, `sheet_id: str`. Parsed from the notes' `**On map**:` line; `None` when absent.
- **Context** (`registry.Context`): gains `on_map: OnMap | None`.
- **MapFeature** (`mapmatch`): `cls: str`, `x, y` (center, map px), `w, h` (map px, 0 for a point),
  `r` (map px, 0 for a rect), `pts` (a polyline or polygon, or empty). Built per class from the
  manifest by the `CLASSES` table.
- **MapInventory** (`mapmatch`): the features of every class inside the sheet's frame (map px), with
  `has(cls)` for the site items and the list per class for direction (c).
- **Transform** (`mapmatch`): `ftpx` (the map's), `origin_sheet` (the subject rect's center),
  `origin_map` (`x, y` of the declaration); `to_map(px, py)` and `frame(viewbox)`.
- **RequiredItem** (`buildings.types`): gains `site: str | None` - the correspondence class whose
  presence on the declared map decides whether the item is asked for; `types.schema.json` gains the
  field; `programs.md`'s rendered table gains the column.
