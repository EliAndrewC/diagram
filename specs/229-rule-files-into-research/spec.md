# Feature 229 - the rule files retire into the research pages

**Status**: DRAFT - spec-fidelity round 1 returned six changes (FR-004 bounded by the GM's clause; FR-009's
page additions cut; the README not edited; the frozen exhibits' prose re-pointed; FR-007 a derived surface;
the deletion order stated); round 2 pending
**Request**: [`request.md`](request.md) (the GM's words, verbatim). **Audit**: [`audit/`](audit/) (the seven
file-by-file reports the request was answered from).
**Scope**: documentation and the record - `research/**`, the `settlements/` rule files and `settlements.md`,
every file that points at them, the record's tests, and comment-only edits to engine files. No map changes.

## Summary

The `settlements/*.md` rule files were written to tell a Claude session how to hand-place features. The hamlet
tier is scripted now; the other tiers will be. The audit found that each rule file is, by bytes, mostly text that
is either restated on its research page, encoded in the engine with its reasoning, or describing the validator
that feature 166 deleted - and a small layer of decision record and specification that exists nowhere else. The
GM ruled: one feature, one sweep; fix the contradictions first; migrate the decision records; then retire every
rule file for every settlement type, moving any content that needs preserving - including the specifications for
tiers nothing scripts yet - onto the research pages, where those specifications wait until a generator exists.

After this feature the record has ONE home per topic. A research page holds, per question: the finding, the
decision it drove with the GM's ruling and the alternatives declined, and - for a rule no generator yet encodes -
the specification the future generator must satisfy. The engine holds each scripted number at its point of change
with its comment, as it already does. `settlements.md`, `settlements/*.md` and `settlements/cities/*.md` are gone.

## Functional requirements

**FR-001 - The contradictions are fixed before anything moves.** Every number, label and claim the audit found
disagreeing between a rule file, its research page and the engine is resolved in favor of the measured or ruled
truth, and the research page carries that truth, before any migration lands on it. The audit's list, each an
explicit task: the head-race width (`research/water.html` says 5.0 ft; the engine has 6.0 with the reason);
the bell-and-drum tower (`research/urban-features.html` states the retired 70 ft / 60 ft decision beside the
corrected 36 ft / 30 ft finding); the mulberry bush density (labeled attested in `archetypes.md`, a GUESS on the
page - the page's label is the one that moves); the Shunde township figure (struck on the page, still cited in
`archetypes.md` as evidence for a live design decision - the argument is re-based on what the page supports);
the three defenses claims the page marks unsourced or GUESS that `defenses.md` states as fact (moved with the
page's label); the frontage-tax rationale for row packing (disputed on `fabric.html` - the specification moves
without it); the houses-per-household ratio (`settlements.md` says ~0.7; the engine and 16 of 17 maps say
0.85-1.05 - the page states the engine's rule); the capital's extramural share (`capitals.md` says all 12,360
inside; the 2026-08-10 ruling and the engine say ~3% outside - nothing of the wrong statement moves); the bamboo
legibility floor (20 ft in both documents, 14 ft in the engine - the page states 14); the marsh-wedge sentence
superseded on `water.html` (the superseded reasoning does not move); the river-cities page advertising
junction-angle research it does not contain (the junction hydrology moves there, closing the gap). A
disagreement found during the sweep that this list does not name is fixed the same way and added to the
feature's `research.md`.

**FR-002 - Every decision record moves to its research page.** Every unit the audit classed DECISION-RECORD
(a GM ruling with its date and words; an accepted limitation with its cost and the alternatives declined; a fix
that was tried, measured and reverted; a project-goal rationale) that its research page does not already carry
is written onto that page, under the section it belongs to or under a new question-shaped section, in the
record's form (`research/CLAUDE.md`: a heading the map's reader would ask, the bookkeeping in HTML comments,
nothing about what the record used to say, every term a reader would not know in the glossary, each decision
carrying one of the four labels - accurate, deviation, convention, guess). The GM's words stay quoted; the
declined alternatives stay named; a measurement that decided something stays with its numbers. The audit's
per-file "D items" lists are the inventory; `research.md` carries the map from each item to the anchor that now
holds it, and an item is not ticked until that anchor exists.

**FR-003 - Every specification a generator does not yet encode moves to its research page.** Every operative
rule, threshold, count band, placement order or knob definition in a rule file that the audit found NOT encoded
in `l7r/` - for the hamlet tier the handful of prose-only rules; for the village, town, provincial-city and
capital tiers essentially all of them - is written onto the research page of its topic as a **specification
paragraph**, beside the question whose finding grounds it, or under a new question when none does. A
specification paragraph is marked so a future generator feature can find every one of them and nothing else:
`<p class="spec">` opening `<strong>The rule the map follows:</strong>`. It states the rule in the reader's
terms - real feet where the tier's scale is known, the pixel figure and the scale in an HTML comment beside it -
and names no engine identifier, check name or validator in its visible text. Where the rule had no "why" at
all (the audit names them: the town's caste census and housing banding, the inn and theater adjacencies, the
city well density, the burakumin seam, the charcoal ladder, the sizing model's density constants, the
lane-geometry tolerances), the paragraph says so in the record's honest form - a convention chosen for
legibility, a calibration against the drawn exhibits, or a guess - so the reader is never told a calibration is
a finding.

**FR-004 - What the engine already encodes, with its why, is not written a second time.** The GM's clause is
*"retiring all of the rule files with any content that needs to be preserved, such as specifications for things
that you have scripted moved into the research files"*. FR-003 is what discharges it: every specification a
generator does not encode moves, the scripted hamlet tier's prose-only rules included. This requirement bounds
the one thing that does NOT move: a hamlet-tier rule whose number already sits in `l7r/` at its point of change
WITH the reasoning the rule file gave for it. That rule is preserved by the engine, so it gets no specification
paragraph; the research page keeps the finding and the decision, and the engine keeps the number. The bound is
narrow and checked rule by rule: where the rule file carried a "why" that the engine's comment lacks, that "why"
is content that needs preserving and moves onto the research page as the decision's grounds, with the engine
comment gaining a one-line pointer to the page's anchor. The inventory of those is every such item the audit
reports name (the homesteads report alone has six: the farmhouse aspect bar, the dispersed sizing caveat, the
byre footprint band, the garden area band, the settlement-form research, and the geomantic and field-system
grounding behind the village-form knobs), collected in `research.md`, and an item is ticked only when its
"why" is on the page.

**FR-005 - A physical claim that moves is cited or labeled, never carried bare.** Content that states how a
place was built, farmed or lived in and carries no footnote in its rule file (the audit names them: the
settlement-form research on nucleated and dispersed villages; the degraded south-China commons; the swept-bend
channel radius; the bridge landing's scour and bearing length; the lane-vehicle finding; the plank bridge's
name; the district-catchment burial finding; the swept-ground practice; the funerary size memo; the temple
neighborhood's economy; the village shrine at the water-mouth; the fire-watch narrative; the junction
hydrology; the gate-market suburb's size; the city sizing model's density and share figures) is a `research:
physical` task: the `source-reader` reads each named source in the background, a READ passage becomes a footnote
on the citations page under feature 194's form, a source that cannot be read becomes an ABSENCE note dated to
this sweep, and the claim's label follows what was found. A new registry key carries its two write-ups and a
`source-applicability` verdict before its numbers stand on the page (constitution XII; feature 211). No claim is
cited from memory and nothing is quoted that was not fetched.

**FR-006 - Pages that have no research counterpart get one.** `ways.md`, `presentation.md`, `cities/sizing.md`
and the tier-level content of `settlements.md` and `cities.md` have no page today. This feature adds
`research/ways.html` (roads, lanes, bridges and planks), `research/presentation.html` (the map's drawing
conventions - labels, captions, framing and cropping; conventions are a first-class label under constitution
XII, and the page says plainly that most of what it holds is convention with no historical finding behind it),
`research/cities/sizing.html` (the space budget and the population rule) and `research/settlements.html` (the
tiers: what a hamlet, village, town, provincial city and capital are, the population canon, what a settlement's
page states, the waiver doctrine and the "lock the rules in against ordinary settlements" lesson). Each new page
has its citations page and its derived script, and is listed wherever the record's pages are enumerated.

**FR-007 - The rule files are deleted, in the GM's order, and nothing points at them.** `settlements.md`,
every `settlements/*.md` and every `settlements/cities/*.md` are removed from the tree - each one only after
FR-001, FR-002 and FR-003 have landed for it and every anchor that replaces its content resolves (the GM's
order: fix the contradictions, migrate the decision records, then retire). The surface of references is a
RULE, not a hand list: every tracked file that names a retired rule file - found by the SC-001 grep over the
whole tree - is re-pointed at the research anchor that now holds the content, or its sentence repaired to read
whole without the pointer. The kinds of file that grep finds today, as examples and not as the boundary:
`SKILL.md`, the root `CLAUDE.md`, the skill `CLAUDE.md`, `migration-plan.md`, `dev/*.md`, `future-work/*.md`,
`pending-enclosed-fan-floor.md`, `hamletgen.md`, `buildings.md` and `buildings/programs.md` (which stay
operative and today cite retired files), `flophouse-research.md`, `town-checks-audit.md`, `town-deep-audit.md`,
the pool's `*.notes.md`, the frozen exhibits' `.gen.py` and `.notes.md` under `legacy-hand-authored-pool/`
(the write-once rule covers their RENDERS, `dev/pool.md`; a comment edit re-runs nothing), `wip/`, the research
pages' own introductions and comments, `research/CLAUDE.md`, the `settlement-review` agent's reading list, the
engine's comments and docstrings (about thirty files - comment-only edits, which do not re-key the gate), the
`Entry:` tag in `interactive/classes/greenery.py` (re-pointed to the vegetation page's heading for the belt's
three roles, which FR-002 creates), and the tests that quote a rule file as their authority. Two kinds of file
keep their pointers as recorded history (D5): the guard replay corpus in `scripts/fixtures/` (a census of
commands sessions actually ran, which `tests/interactive/test_record.py` already exempts for the same reason)
and the frozen fixture `tests/fixtures/classes_before_189.json` (a snapshot of a pre-189 state by definition).
`research/README.md` is NOT edited: constitution XVII reserves that exception to the GM, and the GM's words
did not name the README. Its pairing table and its opening sentence are reported to the GM in the feature's
closing report with the exact replacement text offered (D9), and until the GM applies it the README is a third,
named and temporary exemption from the FR-008 rule.

**FR-008 - The record's tests hold the new state.** `tests/interactive/test_record.py`'s "no token anywhere
resolves to a converted record file" rule is extended to the retired rule files: a tracked file outside the
exemptions FR-007 names (the replay corpus, the pre-189 fixture, and `research/README.md` until the GM applies
the offered correction) that names `settlements.md`, `settlements/<name>.md` or `settlements/cities/<name>.md`
fails the gate. The new pages are covered by every existing record test (they
glob `research/*.html` and `research/cities/*.html`). `tests/interactive/test_docs_match_the_mechanism.py`'s
operative list drops `settlements/fields.md` and `settlements.md`.

**FR-009 - `buildings.md` stays operative and out of the retirement.** Mode A plans are hand-authored by
design, so `buildings.md` and `buildings/programs.md` remain the documents a session draws from; this feature
does not retire them and does not add to `research/buildings.html` (the four GM rulings the audit found only in
`buildings.md` are at no risk while the file stays, and whether they belong on the record as well is a separate
question for the GM, listed in the closing report). What this feature does to the Mode A pair is FR-007's
re-pointing of their references to retired rule files, and - under constitution XIV, defects found while doing
that work - the three stale pointers the audit found: the `pack_audit.py` path, now a package, in eight places;
the pointer to the deleted validator at `buildings.md` line 134; `programs.md`'s pointer to a grounding
section that is not there.

**FR-010 - Verification.** Every new or changed research entry is checked by `quote-check` and `record-format`,
dispatched together in the background, and their findings resolved before the feature lands; every new registry
key by `source-applicability`. `make citations` and `make glossary` are run and their assets committed;
`make page-check` is green; `make done` is green (the engine edits are comments and one docstring tag, so the
gate's engine key does not move and the page key does). The landing route is whatever `sync-with-main.sh`
derives from the delta.

## Success criteria

- **SC-001** `ls .claude/skills/diagram/settlements* ` finds nothing; `git grep -l 'settlements/[a-z-]*\.md\|settlements\.md\|settlements/cities/'`
  over the tree returns only files under `specs/`, `scripts/fixtures/`, the one frozen test fixture, and
  `research/README.md` until the GM applies the offered correction.
- **SC-002** Every DECISION-RECORD item in the seven audit reports appears in `research.md`'s map with the anchor
  that holds it, and every anchor resolves (`test_every_link_in_a_record_page_resolves` is the mechanical check;
  the map is the human one).
- **SC-003** Every rule the audit lists under "B items the engine does NOT encode" appears on a research page
  inside a `<p class="spec">`, or in `research.md` with the reason it was dropped (a rule about a deleted
  mechanism with no map behavior behind it - the audit names some, such as the twin-detector's axes).
- **SC-004** No research page states a number the engine contradicts for a scripted feature: the FR-001 list is
  closed, and a spot check of every constant a specification paragraph names against `l7r/` finds no
  disagreement.
- **SC-005** `make page-check` green; `make done` green; `quote-check`, `record-format` and (for new keys)
  `source-applicability` verdicts recorded per changed page in `tasks.md`.
- **SC-006** The four new pages open from disk with their glossary and citations hover working, checked in a
  browser once.

## Decisions Recorded

| Decision | Class | Why | Where recorded |
|---|---|---|---|
| D1 The rule files retire; the research page is the one home per topic | GM ruling 2026-09-12 | the rule files were for hand placement; the scripted tier reads code, the reader reads the record; two copies drift (the audit found eleven disagreements) | `request.md`; `research/CLAUDE.md` |
| D2 Unscripted-tier specifications live on the research pages until a generator exists, marked `class="spec"` | GM ruling 2026-09-12 | *"those specifications will move into the scripted generators once those exist"*; the marker is what lets that later feature find them | this spec FR-003; `research/CLAUDE.md` |
| D3 A hamlet rule already in the engine with its comment is not duplicated onto the page | session, under D1 | the engine is the operative document for a scripted tier; a second copy is what this feature exists to remove | FR-004 |
| D4 Four new pages: `settlements`, `ways`, `presentation`, `cities/sizing` | session | the content has no page to land on; `presentation` is a page of conventions and says so | FR-006 |
| D5 The guard replay corpus and the frozen class fixture keep their stale pointers; the frozen exhibits' prose is re-pointed | session | the corpus is a census of commands actually run (`test_record.py` exempts it on that ground); the fixture is a pre-189 snapshot by definition; the exhibits' write-once rule covers their renders, not a comment | FR-007, FR-008 |
| D6 `buildings.md` stays operative; nothing is added to `research/buildings.html` | session (D6 reviewed FAITHFUL to the GM's "settlement types") | Mode A is hand-authored by design; a copy of an operative document's rulings on the page is the duplication this feature removes | FR-009 |
| D7 Numbers on the page are in real feet with the pixel figure in a comment | session, from the record's reader rule | the reader meets feet on the map's scale bar; the pixel figure is a session's | FR-003 |
| D8 A physical claim that moves without a footnote goes through the research pass, and its label follows what was found | constitution XII | nothing is asserted as a finding that the record cannot support | FR-005 |
| D9 `research/README.md` is not edited; the correction is offered to the GM with the replacement text | constitution XVII | a README is the GM's to write and the exception is theirs to make; the GM's words did not name it | FR-007, the closing report |
| D10 The engine's pointers to a rule file become pointers to a research anchor, not deletions | session | the point-of-change pointer is constitution XII's third leg | FR-007 |

## Assumptions

- "All of the settlement types" means every Mode B tier - hamlet, village, town, provincial city, capital - and
  not Mode A; `buildings.md` is therefore outside the retirement (D6). If the GM meant Mode A too, FR-009 is the
  part to revisit.
- "Content that needs to be preserved" means content that exists in no other place: a decision record the page
  lacks, a specification the engine lacks, a "why" the engine's comment lacks. Content the page or the engine
  already carries is preserved by them.
- A stale specification - one describing a deleted check with no behavior behind it, or a knob no map and no
  code reads - is not preserved; it is listed in `research.md` with the reason, so the drop is deliberate and
  auditable (SC-003).
