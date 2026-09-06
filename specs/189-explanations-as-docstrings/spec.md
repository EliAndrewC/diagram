# Feature 189 - a feature class's explanation is its docstring

**Status**: FAITHFUL (`spec-fidelity`, round 2 of 5) - cleared for implementation (constitution XVI).
Round 1 returned three items: the byte-hashed stamp area reached six modules that hold no moved prose
(narrowed to the registry files); the package split was projected, not measured (now conditional on the
emitted line count - measured at 1,195 lines for the class bodies alone, about 1,500 for a single module,
so the split is taken); and the place card's deferral rested on a preference (now on its real obstacle -
interpolated, per-map composed text). Round 2 returned none.
**Request**: [`request.md`](request.md) - the GM's words verbatim
**Predecessors**: feature 188 D4 (recorded that a prose edit in `classes.py` still costs the full gate,
"for now"); feature 134 (the class registry); 156 (the presumption of accuracy - `lead`, `caveat`)

## Summary

The GM's observation is correct: the gate's key is the docstring-stripped AST (`gate-stamp.py`
`semantic_bytes`, GM 2026-08-26), so prose held in a DOCSTRING is not part of it, while prose held in a
string constant is. Today every modal's explanation - `what`, `why`, the label note, the caveat - is a
string constant in `interactive/classes.py`, so rewording one costs the nine-minute gate.

So each of the 51 feature classes becomes a small Python class whose docstring IS its explanation, in a tagged form
the registry parses at import. The documentation in the code is literally the text on the page, which is
the property the GM wants. A prose edit then costs the 26-second `make page-check` (the registry's own
tests and the browser test) and nothing more; a code edit to the same files still costs the gate.

**Checked before agreeing.** Both caches still see a docstring edit: the generation cache hashes class
bodies by their source text (`gencache._split_sources` - a class body is "module level"), so `make map`
regenerates a page whose explanation changed; the render fingerprint hashes bytes (feature 187), so the
mirror regenerates on landing. Only the gate key and the route are blind to docstrings, and that is the
point.

## Functional requirements

### The form (FR-001 to FR-004)

- **FR-001** Each feature class is a Python class deriving from a small base, whose DOCSTRING carries the
  prose in tagged sections, each tag at the start of a line and each value running to the next tag,
  wrapped lines joined with a space:
  - `What:` - what the thing is (today's `what`)
  - `Why:` - why it stands where it does (today's `why`)
  - `Note:` - the one line that justifies the label (today's `label_note`; for a `convention` the GM's
    "we have rendered ..." sentence, which the modal opens with after "Note: ")
  - `Caveat:` - optional, the liberty half of the note shown under the why (today's `caveat`), still
    required to be a verbatim substring of `Note:` (the existing test)
  The fields that are DATA, not prose, stay as class attributes: `key`, `name`, `covers`, `label`,
  `sources`, `entry`. A class missing `What:`, `Why:` or `Note:` fails at import with the class named -
  a registry error is loud, never silent.
- **FR-002** `FeatureClass` and every consumer are unchanged: `page.py`, `place.py` and the tests keep
  reading `fc.what`, `fc.why`, `fc.label_note`, `fc.caveat`, `fc.siblings` exactly as today. The registry
  builds each `FeatureClass` from its class at import; `CLASSES` keeps the spec FR-007 insertion order.
- **FR-003** The registry becomes a PACKAGE, `interactive/classes/`, IF AND ONLY IF the converted single
  module MEASURES past the 1,000-line bar (constitution X clause 13, gated since feature 173). `classes.py`
  is 923 lines today with 51 entries at about 11.8 lines each; the class form is about the same length,
  and the parser and helpers can move to a `_base.py` either way - so the outcome is genuinely either side
  of the bar and is decided by the number the conversion script emits, recorded in T02. Below the bar the
  registry stays one `classes.py` (plus `_base.py` if that keeps it under) and nothing else in this
  requirement applies. Past the bar, modules by feature family, each with its own docstring saying what
  it holds: `_base.py` (the dataclass, `Label`,
  `ANNOUNCED`, the lead and phrase functions, the parser), `homestead.py` (farmhouse to persimmon),
  `greenery.py` (the two bamboos, windbreak, copse, woodland commons, scrub, marsh), `fields.py` (paddy to
  fallow), `water_and_ways.py` (stream to notice board), `dikepond.py` (fish pond to perimeter dike),
  `siblings.py` (the pair texts, FR-004), and `__init__.py` re-exporting today's whole public surface -
  `CLASSES`, `FeatureClass`, `Label`, `ANNOUNCED`, `NOT_HIGHLIGHTED`, `PLACE`, `CONVENTION_LEAD`,
  `lead_sentence`, `label_phrase`, `slug`, `NOT_HIGHLIGHTED_RULINGS`, `NOT_HIGHLIGHTED_OVERTURNED` - so
  every `from l7r.diagram.interactive.classes import ...` in the engine and the tests resolves unchanged.
  A `CLAUDE.md` index in the package says which family lives where and how an entry is written.
- **FR-004** The sibling pair texts (`_PAIRS`) stay string constants, in `siblings.py`. They are not
  rendered (since 2026-08-28 the page shows sibling LINKS), so nothing on the page depends on them, and
  editing one is a change to the record, not to the UI. Recorded as D4.

### The conversion (FR-005 to FR-006)

- **FR-005** The conversion is SCRIPTED from the existing source, never retyped: a one-off script parses
  today's `_DEFS` with `ast`, emits the class definitions with their docstrings, and a snapshot of every
  field of every class as it was is written to `tests/fixtures/classes_before_189.json`.
- **FR-006** A test proves the conversion changed no text: for every key, the new registry's `what`, `why`,
  `label_note`, `caveat`, `label`, `name`, `covers`, `sources`, `entry` and `siblings` equal the snapshot.
  The snapshot stays as the frozen proof (a fixture, like the registry-legacy-rows fixture).

### What a prose edit costs afterwards (FR-007 to FR-008)

- **FR-007** `gate-stamp.py`'s `page` area (feature 188) widens from `interactive/assets` to exactly the
  files that carry page prose in docstrings - the registry (`interactive/classes.py`, or the
  `interactive/classes/` package if FR-003 splits it) - beside the two assets, and the REGISTRY files in
  that area are hashed by BYTES (a per-area rule; the `diagram` and `hooks` areas keep the semantic id).
  So a docstring edit in the registry makes the `page` stamp stale and the push owes `make page-check`
  (26 s), while the `diagram` stamp (semantic) is untouched and no full gate is owed. `make done` stamps
  both on its phases-run exit, as 188 made it. The route is semantic too (`ci/delta._semantically_changed`),
  so a prose-only delta is DIRECT: a tweak, no spec-kit feature, no review, no task file. `page.py`,
  `place.py`, `glossary.py`, `notes.py`, `sources.py` and `tags.py` are NOT in the page area: they hold no
  moved prose, and a comment edit in them keeps costing nothing.
- **FR-008** The cost stated and accepted: a COMMENT edit in the registry files now owes the 26-second
  page check where today it owes nothing, because bytes cannot tell a comment from a docstring. Declined:
  an "AST with docstrings kept, comments dropped" hash for those files - a third notion of identity for
  one directory, for a saving of 26 s on comment edits in the one place comments sit beside page prose.
  An earlier draft byte-hashed the whole `interactive/` package; the review narrowed it to the path that
  carries the prose, which costs nothing and keeps the purpose.

### Documentation and tests (FR-009 to FR-010)

- **FR-009** `interactive/CLAUDE.md`'s `classes.py` row becomes the package row and points at the
  package's own index, which carries the tag format with one worked entry; the root `CLAUDE.md`'s tweak
  lane bullet (feature 188) gains "and a modal's explanation - it is a docstring"; feature 188's D4 is
  noted as closed here.
- **FR-010** Tests: the parser (each tag, wrapping, a missing tag refusing with the class named, `Caveat:`
  optional), the snapshot equality (FR-006), the package surface (every name the old module exported is
  importable from the package - the existing importers are the census), `test_page.py`'s stub text
  `(interactive/classes.py)` becomes `(interactive/classes/)`, and `test-gate-stamp.sh` gains: a
  docstring edit under `interactive/` owes `page` and not `diagram`; a code edit there owes both.

### What this feature does not do

- **FR-011** It changes no explanation's TEXT, no glyph, no map. FR-006 is the proof.
- **FR-012** It does not move the place card's prose (`place.py`: `BASIS`, the `KINDS` descriptions,
  `COLLISIONS`) into docstrings, and the reason is an OBSTACLE rather than a preference: that prose is not
  static text. `KINDS` interpolates setting numbers (`f"...{HAMLETS_PER_DOMAIN:,}..."`) and `place_card()`
  COMPOSES its sentences per map from the manifest (the size sentence, the district sentence, the crop
  sentence, the collisions present), so a docstring cannot hold it as it stands - it would need a template
  form and a renderer of its own. The place card IS a modal explanation visible in the UI, so the GM's
  principle reaches it; D5 records it as the next candidate with that obstacle named.

## Decisions Recorded

- **D1 - tagged sections, not positional paragraphs.** `What:` / `Why:` / `Note:` / `Caveat:` at line
  start. Positional paragraphs (first = what, second = why) were declined: a `why` that needs two
  paragraphs would silently become a caveat. Tags are one word each and read as prose headings.
- **D2 - a package split by feature family**, the exemplar being `settlement/`. Declined: one module of
  51 classes (over the bar) and one module per class (51 files for 51 docstrings, and an import list
  nobody wants to maintain).
- **D3 - the `page` area hashes bytes.** The one place a docstring must count as a change is the stamp
  that demands the page check; every other identity in the repository stays semantic. Cost in FR-008.
- **D4 - sibling texts stay constants** (FR-004). Not rendered; a record.
- **D5 - the place card's prose is next, not now, because it is composed, not stored.** `place.py` builds
  its text per map from `KINDS` (interpolated with setting numbers), `COLLISIONS` and `BASIS`, assembled by
  `place_card()` from the manifest; a docstring holds one static string. Moving it means designing a
  template form (a docstring with placeholders the card fills) - a feature of its own. The principle
  reaches it and the same page check would cover it; the GM decides whether the template form is wanted.
- **D6 - the conversion is scripted and its output is proven equal to a snapshot** before the old file
  is deleted; the snapshot is kept as a fixture. Retyping 51 entries by hand is how a word changes
  without anyone deciding it should.
- **D7 - `python -OO` strips docstrings, and nothing here runs it.** The standing caveat on prose in
  docstrings, noted by the review: under `-OO` every `__doc__` is `None`. No make target, buildspec or hook
  in this repository runs optimized Python, and the registry's parser fails at import with the class
  named when a docstring is missing, so the failure would be loud on the first import rather than a
  blank modal. Recorded so the next person who considers `-OO` finds the reason not to.
