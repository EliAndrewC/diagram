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

## R3 - the census AFTER, and what the delta means

`make footnote-census` on the same tree, after every note this feature touched:

| | cited | grounds | ABSENT | settled |
|---|---|---|---|---|
| before | 969 | 0 | 84 | 0 |
| after | 969 | **1** | **83** | 0 |

One note left the backlog, and it left it by being reclassified as owing no source. Nothing else moved:
no note was deleted, no absence became a citation under this feature, and the settled state shipped with
no instance, exactly as the spec said it would.

**The number this feature was written to produce is the ONE.** The GM's complaint was that a category
meant to denote problems was counting things that are not problems, and the honest answer turned out to
be that today's record contains almost none of that: of eighteen notes a triage proposed for
reclassification, one converts, and seventeen are genuine research questions that stay in the backlog.
That is a smaller fix than the triage promised and a truer one, and the mechanism is what matters going
forward - the next session that meets a sentence with nothing to find now has a word for it, a closed
list of six reasons, four checkers that know the form, and a census that counts it separately.

## R4 - the arguments the three arguable notes lost, and why each is written at its own note

FR-006 said three notes are argued at their pages and convert only if the argument holds. All three were
argued and all three REFUSED, each argument left in an HTML comment at the note so the next reader meets
it rather than re-litigating:

- **`fields.html` fn-85** - `follows from the definitions`. Only the second half of the sentence is
  definitional (a bund across a drain dams it). The opening identity - a paddy's lowest bund IS the
  collector's top-of-bank - is contingent: this record's own `berm` entry draws a strip between a canal
  and the nearest plot, so the two need not be the same earth. FR-003's first clause bars it, and a
  land-consolidation standard could settle it, so it belongs in the backlog. An independent
  `record-format` read of the page reached the same verdict and added the berm evidence.
- **`religion-and-death.html` fn-78** - `the record's own silence`. The clause reports a reading, which
  is what an absence note already says, and the sentence around it asserts something about the world.
  Exhausting the search would make it a SETTLED absence under FR-004, not a grounds note.
- **`religion-and-death.html` fn-49** - the section's own `Sources:` line credits the GM's ruling of
  2026-07-21 on the footprint band, so what the band rests on is `this project's decision`, which
  FR-002's barred set forbids here; and the paragraph is the rule the map FOLLOWS, so the figures were
  chosen and then drawn rather than read off a drawing - the distinction that kept fn-57 open. The
  independent read found a third and stronger ground the argument had missed: the band is a size for a
  real building at a tier drawn to true scale, so FR-003's first clause bars it whatever the reason.
