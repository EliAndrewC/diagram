# Research - feature 235, grounds notes are not absences

## R1 - the census BEFORE any note changes (SC-003, T06)

`make footnote-census`, on this tree, 2026-09-12, before a single note was converted:

| | cited | grounds | ABSENT | settled |
|---|---|---|---|---|
| TOTAL | 969 | 0 | 84 | 0 |

Per page, the pages carrying an absence note: `archetypes` 7, `buildings` 2, `cities/capitals` 1,
`cities/defenses` 3, `cities/fabric` 7, `cities/government` 3, `cities/hinterland` 2,
`cities/river-cities` 3, `cities/sizing` 2, `fields` 4, `homesteads` 8, `religion-and-death` 23,
`towns` 1, `urban-features` 4, `vegetation` 10, `water` 1, `ways` 3.

Two things this number is not. It is not the 162 absence notes feature 232 verdicted - that pass closed
most of them, and 84 is what it left. And it is not a backlog of 84 problems, which is the whole reason
this feature exists: the count mixes notes that owe a search with notes that owe nothing and were
labeled "absent" because the record had only two labels to give.

## R2 - the classifier belongs to the engine, not to the test that first needed it

The census tool was written importing `footnote_form` from `tests/interactive/test_footnotes.py`, which is
the wrong direction: `tests/` is invisible to the generation cache by design (`tests/CLAUDE.md`), and the
project's own rule is that *"if you ever need a module here that a generator imports, it does not belong
here - put it in the engine"*. So the form of a footnote is now decided in one place in the engine and
read by three:

- `l7r/diagram/interactive/citations.py` - `ABSENCE`, `SETTLED`, `GROUNDS`, `GROUNDS_REASONS`,
  `grounds_reasons()`, `is_settled()`, `footnote_form()`. The module already owned the note (`NOTE`,
  `_KEY_LINK`, `_BACK`), so the classifier reuses those patterns instead of restating them, which is
  what the test copy had been doing.
- `l7r/diagram/interactive/sources.py` - `registry_keys()` and `canon_keys()`, which are facts about the
  REGISTRY rather than about a note.
- `tests/interactive/test_footnotes.py` imports all six and keeps what only a test can hold: that a
  citation names a registered key and carries a quotation, and that every note is referenced.

One behavior changed on the way, deliberately: `GROUNDS` captures its reason with `*` rather than `+`, so
a note reading `no source is owed:` with nothing after it is reported as a grounds note missing its
reason instead of falling through to the generic "matches no form". The branch that says so was
unreachable before.
