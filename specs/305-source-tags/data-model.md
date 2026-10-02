# Feature 305 - data model

- **SourceVocabulary** (`research/source-tags.json`): `period`, `region`, `kind` - each an ordered list of
  `{id, name, description}`; `canon` - one `{id, name, description}`. Ids are lower-case kebab. Order is display order.
- **SourceTags** (an entry's marker): `period: tuple[str, ...]`, `region: tuple[str, ...]`, `kind: tuple[str, ...]`,
  each non-empty, no repeats, every value in the vocabulary; `primary(facet)` is the first.
- **WorksSection** (`research/source-sections.json`): `id` (prefix `works-`), `title`, `description`, `canon: bool`,
  `takes: list[clause]`; a clause maps any of `period`/`region`/`kind` to a value or list, tested against PRIMARY values.
  A canon section takes no clauses; every other section takes at least one.
- **Catalog** (built per build): key -> (section, labels html) for every registry entry; the errors list.

Validation (FR-010), each naming the entry file: no marker on a non-canon entry; a marker on a canon entry; a facet
missing or repeated; an unknown value (with the facet's allowed ids); primary tags no section takes (with the
combination); and, for the files: a section id twice, a clause naming an unknown facet or value, no canon section, a
non-canon section with no clause.
