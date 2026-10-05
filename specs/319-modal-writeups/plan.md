# Implementation Plan: Modal write-ups a reader can take in

**Spec**: `specs/319-modal-writeups/spec.md` | **Created**: 2026-10-03

## Summary

Two guideline documents (standardized and particular modals), a new docstring form (`About:` paragraphs and a `Guesses:`
bullet list, no feature-level label), a tabbed modal (About / Guesses / References, the References tab replacing the
references dialog), two defined check agents (`modal-form`, `modal-research`) fed by a bundle and a mechanical prepass and
owed at the push like the record checks, then the pilots one at a time with the GM, then the title card's settlement
choices, then the rollout over the hamlet classes, the choice values and the sheet kinds.

## Technical Context

- Engine (GATED route at landing): `interactive/classes/_base.py` (the parser and `FeatureClass` take the new form beside the
  old until the rollout retires the old), `interactive/page.py` (`explanations()` carries `about`, `guesses`), `assets/page.js`
  and `assets/page.css` (the tabs), `interactive/place.py` (the choices, phase 5). Docstring edits are page content
  (`make page-check`), as since feature 189.
- Scripts: `scripts/_modal_bundle.py` (bundle + prepass), `scripts/_modal_owed.py` (owed units), folded into
  `_record_owed.py` / `entry-gate.sh` so `make record-owed`, `make record-checked` and the push treat the modal checks as they
  treat the record checks. Makefile targets `modal-bundle`, `modal-prepass`.
- Agents: `.claude/agents/modal-form.md`, `.claude/agents/modal-research.md`, `omitClaudeMd: true`, rows in
  `tests/test_agent_models.py`.
- Docs: `.claude/skills/diagram/dev/modals.md` (standardized guidelines) and `dev/modals-particular.md` (particular
  guidelines), indexed from `interactive/classes/CLAUDE.md` and `compound_kinds/__init__.py`; `interactive/CLAUDE.md`'s
  "presumption of accuracy" and "references modal" sections rewritten for the tabs.
- Sizes measured 2026-10-03 (`wc -l`): `page.py` 872, `_base.py` 235, `page.js` 449, `place.py` 408 - all stay under the
  1,000-line bar; `page.py` is the one to watch (D2 adds about 30 lines).

## Decisions

**D1 - The docstring form.** A class in the new form carries `About:` and, when it has any, `Guesses:`, and none of `What:`,
`Why:`, `Note:`, `Caveat:`, `Label:`. `About:` keeps paragraph breaks (a blank line inside the value is a paragraph break; the
parser keeps them for `About:` only). `Guesses:` is a list: each line opening `- ` starts a bullet, wrapped lines join it. The
data tags `Name:`, `Covers:`, `Sources:`, `Entry:` stay required; `Form: particular` is optional (default `standard`) and says
which guidelines and checks hold the modal. `FeatureClass` gains `about: tuple[str, ...]`, `guesses: tuple[str, ...]`, `form`;
`label` becomes `Label | None` (None in the new form - the classification is per statement: a guess is a bullet, a deviation
is said in the About text, a convention on the Depiction tab since D13, the evidence classes stay on the research pages). Both forms parse until the
rollout ends; the last rollout task removes the old form and its tests. (FR-002, FR-005)

**D2 - The tabbed modal.** One dialog; a tab strip `About` / `Guesses` / `Depiction` (D13) / `References` of buttons (`role="tablist"`), a tab with
nothing to show is not drawn, the dialog opens on About every time. About: the new form's paragraphs, then the sibling line;
an old-form class shows its lead, what, why, caveat and on-this-map lines there unchanged, so every modal is tabbed from the
first commit. Guesses: a bulleted list. References: the lead-in line and the question links, as the references dialog has them
today; the separate references dialog, its `behind` class and its "Return to <X> writeup" button go (the tab strip is the way
back). The place card gets the same tabs. Glossary tooltips apply to every tab. The browser test's references-dialog cases
become tab cases. (FR-005, FR-006, FR-007)

**D3 - The guidelines are the checks' contract, by copy.** `dev/modals.md` and `dev/modals-particular.md` are the one source;
the modal bundle copies the relevant one in, so the agents read the current rules without the rules being restated in two
places. Each rule is numbered (`M1`...), and every finding names its rule. The first drafts are written in this phase from
the GM's request; every change the GM asks of a pilot is made there first (FR-010).

**D4 - Two checks, split by what they read.** `modal-form` (Opus, medium) reads only the guidelines and the modal as the
reader sees it (rendered text of each tab, glossary terms marked): does it answer its kind's questions in order, in the voice,
at the length; are guesses on the guesses tab and only guesses; are deviations and conventions where the rules put them. It is
cheap and re-run on every pilot iteration. `modal-research` (Opus, medium) reads the modal, the pages its `Entry:` names and
the prepass's candidate questions: ACCURACY (each statement supported, each guess absent from the record, each hedge matching
the page's evidence class), REFERENCES (each listed question supports a statement, each statement's support is listed), and
GAPS (a candidate question that answers something the modal leaves unanswered or guessed) - reported as THREE verdicts,
one per part, each recorded as its own ledger row and its own answer (`modal-accuracy`, `modal-references`, `modal-gaps` units
answered by the one dispatch), so FR-008's three checks and SC-003 are each measured. For a particular modal the same two
agents apply the particular rules, and `modal-research` reads the `make canon` answer for the kind's terms in place of the
candidates. Both reply counts first, then findings with `EDIT` blocks in the `make apply-edits` shape. One agent each, not
three: references and accuracy read the same pages, and reading them twice was the cost feature 250 measured. (FR-008)

**D5 - The prepass and the bundle.** `make modal-bundle KIND=<Class> FOR=modal-form|modal-research` writes a bundle outside
the repository (the `check-bundle` layout: `MANIFEST.md` with every copy inline, origins named). The prepass, run first and
put in the bundle: word counts per tab against the guideline band; phrases the guidelines bar from the About text (record
talk: "this project", "the record", "page read", "no page", "GUESS", "This is a guess"; the label words); a `Guesses:` bullet
that is not a bullet; an `Entry:` that resolves to nothing; and for `modal-research` the candidates - the UNION of every
question sharing ANY `subject` tag with the pages the kind's `Entry:` names, and every question whose words carry the kind's
name or one of its glossary variants (`research/assets/glossary-variants.txt`), listed with heading, tags and first paragraph
and ranked by how many of the kind's terms and tags they carry; the ranking orders the list, never cuts it, and
`modal-research` may grep the whole record copy in the bundle beyond it. The farmhouse's own case is the test: 0004 carries
`subject=tiers,households`, meeting 0029's `households` tag, and must be a candidate (D7). (FR-008, US3-2)

**D6 - Owed and enforced as the record checks are.** `_modal_owed.py` owes `modal-form:<key>` and the three `modal-research` units (`modal-accuracy:<key>`,
`modal-references:<key>`, `modal-gaps:<key>`) for
each new-form class whose `About:`, `Guesses:` or `Entry:` text changed since the merge base, and `modal-research:<key>` when
a page its `Entry:` names changed (this replaces `entry-drift` for new-form classes; old-form classes keep `entry-drift`).
`_record_owed.py` lists them, `make record-checked CHECK=modal-form BUNDLE=<dir>` answers them by fingerprint, and
`entry-gate.sh` refuses the push while one is unanswered, with the command in its message. (FR-008)

**D7 - The checks are proved on the old text first.** Before any rewrite, both agents run on the CURRENT farmhouse and garden
modals (converted mechanically to the new form so the bundle can read them: `What`+`Why` as About, the `Note` as one guess):
`modal-form` must report the farmhouse's missing materials and occupancy and the garden's guess-led opening;
`modal-research` must report question 0004 as a gap. A check that passes the old text is fixed before the pilot. (constitution:
prove a check fires)

**D8 - The research pass for the pilot.** The farmhouse's standard questions are answered from the record first (0029, 0028,
0004, 0048 for animals under the roof, 0030 for the headman's house); a question the record does not answer (whether doorways
closed, what the walls were) gets the research pass under the doctrine - archive first, then the web, `source-reader`,
`quote-check`, `source-applicability` - and its finding is recorded on the question page it belongs to before the modal states
it. Only what is still unanswered is a guess. Each such task is `research: physical` with the five boxes.

**D9 - The pilot hand-off.** For each pilot: rewrite, both checks green (two rounds at most), regenerate the Inashiro page in
the clone (`make map GEN=pool/hamlets/inashiro/inashiro.gen.py`), and give the GM the page's path and the class to click. The
GM's verdict is recorded in `tasks.md` under the pilot; changes go to the guidelines (and the agents' prepass where they
apply) before the modal. The farmhouse first, the garden second, a further feature only if the garden's first rewrite needs
changes; the rollout waits for the GM's go-ahead. (FR-010, FR-012)

**D10 - The title card's choices (settled 2026-10-05, after the go-ahead).** Measured first: the populated knob registry
holds 22 knobs (`interactive/conditions.knobs()`, which imports every module calling `register_knob(`); the five pool hamlets'
manifests record 14 to 18 of them in `meta`, plus two declared choices that are not knobs - `harvest_weather` (settled |
changeable, `hamletgen/consts.py` `HARVEST_WEATHERS`) and `hamlet_burial` (village_ground, `hamletgen/burial.py` `BURIAL_FORMS`);
`water_source_position` takes hamlet values outside the knob's registry (head_center, head_right, corner_high).
- **The table.** `interactive/assets/choices.json` lists every choice in reading order: its meta key, its reader-facing name,
  and its values, each value's reader-facing label. Every registered knob is in it, both declared choices, and every value the
  registry or a pool manifest gives. A knob that is a DEGREE along a continuum rather than a choice between forms (constitution
  XII's distinction: `grain_drift`, the field's turn in degrees) takes ONE modal for the knob, written once, its value shown
  as the label; every other key takes one modal per value. A test reads the populated registry and the pool manifests and
  fails on a knob, a value or a modal file the table or the modal directory lacks.
- **Every per-settlement roll, not only the knobs** (the plan review of D10, round 1: the table missed rolls no knob
  registers). A hamlet also picks forms from its seed - a row's line, sides and water, a scattered farm's water, the farm
  grove's sides, the copse's siting, the manure's form, the bath's seat, the dike-pond's crop, leftover ground, fry ponds and
  layout, the intake, the drained water's sink, the field grave's form. Each is a choice in the table; one that belongs to one
  settlement form names it in `when` (`[settlement_form=linear]`, the modal conditions' form), and the card lists it only
  where that condition holds, since a map records some of them whatever its form. A roll that is not a choice of form - the
  slope's direction, a share, a count, which flank a grove's open side faces - is named in the table's `not_choices` with why.
  A test scans the hamlet generator's roll sites (`_roll(spec.seed, "<key>")`, `knob_rng(seed, "<key>")`) and fails on a roll
  that is neither. The field grave's form, which the generator rolled but did not record, is now recorded in `meta.grave_form`
  (`settlement/fields/features.py`), so Kashikawa's `### Features` sentence on it is carried by the choice.
- **The modals.** `interactive/assets/modals/choice/<key>--<value>.md` (or `<key>.md` for a degree), in the About form, read by
  the same parser; a registry `interactive/choices.py` keyed `choice:<key>=<value>` (or `choice:<key>`); written to the same
  guidelines and checks as a feature modal (the modal checks discover them by their files, `choice/<slug>`, beside
  `hamlet/` and `sheet/`).
- **The card.** `place_card` gains `choices` - each of the map's recorded choices with its name, its value's label and the key
  of its modal - and `facts`, this settlement's own sentences: the windbreak's side and why (the GM's wording of 2026-10-05,
  moved from the windbreak modal), where the lanes lead (moved from the lane modal), and "10 of its 15 homesteads have a
  retirement house" from `meta.retirement_houses`. Which sides the farm groves take is a CHOICE (`grove_sides`, two, three or
  four sides, rolled per settlement: the plan review's round 1), not a fact, and opens its own modal. The
  page draws the choices as a list on the card's About tab, each value a link opening its modal in the same dialog, the facts
  beneath. The choice modals ride in the page's data like a class's, with no ink to light.
- **The `### Features` facts.** On a hamlet the page reads no `### Features` and writes no `on_this_map`: the five hamlets'
  facts are covered by the choices (harvest weather, where the dead lie, the field grave's form) and the retirement count; the blocks are removed from
  their notes (two of them - Inashiro's and Kashikawa's own burial grounds - were stale: `burial.py` draws no hamlet ground and
  records `village_ground`). Other tiers keep reading theirs until they are standardized. A test holds that the explanations of
  every hamlet class are identical across the five pool maps' `meta` once FR-015's conditioned items are set aside (FR-004,
  FR-009, SC-004).

**D11 - Sheets (phase after the hamlet rollout).** Every compound kind is tagged `Form: particular` or left standard by
`particulars.py` membership and by each kind's content (a kind particular to the setting even if on several sheets is
particular); each sheet's `### Features` entries are reviewed under the particular guidelines; the canon answer goes in the
`modal-research` bundle for particulars. (FR-003, FR-011)

**D12 - One file per modal (amendment, GM 2026-10-03).** Pitched by the session after the farmhouse pilot (editing one modal
read the whole module - `homestead.py` 36 KB for 14 modals, `compound_kinds/household.py` 65 KB for 27 - and two checker rounds
could not quote a docstring's line breaks for their EDIT blocks); the GM: *"Yes, I agree with that. So please go ahead and make
that change now ... I believe that feature 189's reasoning has been superseded by the fact that we now cross-reference our
implementation with our research."* Each modal's text - both forms, the same tags - moves to
`interactive/assets/modals/<hamlet|sheet>/<slug of its key>.md`, moved by script with a test that every registry entry is
field-for-field what it was; the `Kind` class keeps `key` (what the engine stamps) and its `#` comments, and `Kind.feature()`
reads the file. Under `assets/` the files are page content: gate-stamp's `page` area already globs `assets/*` (fnmatch crosses
`/`), the generation cache records the reads of a gen's child process, and the render fingerprint is widened to every file
under `interactive/assets/` (it took only that folder's top level and `.json` elsewhere). Every reader of a modal docstring
follows the text to its file: `_modal_owed`, `_modal_bundle`, `_entry_owed` (the old side of a delta still read from the
docstring where no file existed at the base), `_bundle_owed`, `_check_bundle` (`kind.txt`), `_apply_edits` (the modal folder
an allowed EDIT target).

**D13 - The Depiction tab (amendment, GM 2026-10-04; spec FR-014).** The modal file gains `Depiction:` (paragraphs, as
`About:`) and `Drawing:` (the "how our maps draw it" pages, `research/questions/NNNN-<id>.drawing.html`, comma-separated);
`Entry:` keeps the research questions alone, and a `.drawing.html` listed under `Entry:` is refused at parse with the message
naming `Drawing:`. The page draws a fourth tab, "Depiction", between Guesses and References, holding the `Depiction:`
paragraphs and then the drawing pages as links (the `research_questions` resolver, unchanged); it is absent when both are
empty, and joins the grid cell the other panels share (one size for every tab). The guidelines gain the tab's rules (`dev/modals.md`
section "Depiction", rules D1-D6: what goes there - conventions with the real figure, standardizations with why, the links;
links alone when nothing is notable; absent when neither; a single form is written as deliberate only where a drawing page records
it as a convention, never where the research makes it a knob the code does not roll; and M13 amended - a convention leaves About).
A new defined agent `modal-depiction` (Opus, medium, `omitClaudeMd`) reads a bundle (`make modal-bundle KIND= FOR=modal-depiction`):
the modal's Depiction and About text, the guidelines, the kind's drawing pages whole, the claims-index rows whose cited pages
include any of them (key, verdict, note - so a DRIFTED claim such as the farmhouse's single roof is in front of it), and a crop of
the glyph on a pool page (`interactive/assets` page screenshot at a fixed zoom around the first element of the kind, written by the
bundle script with the browser the page tests already use; a kind on no pool map is bundled without a crop and says so). It reports
COVERAGE (every convention and standardization the glyph shows is told, with the real counterpart), TRUTH (nothing told that the
crop and the pages do not show; nothing presented as deliberate that a claim calls DRIFTED), LINKS (exactly the drawing pages the
modal and its KIND rest on - FR-014's words). So that a conversion leaving `Drawing:` empty is still judged (the plan review,
round 2), the bundle also carries each CANDIDATE drawing page - the one beside each research question under `Entry:` (231 of the
237 drawing pages sit beside a question page, measured 2026-10-04) and any drawing page the modal's file listed at the merge
base - marked apart from the listed ones; a candidate that holds how the map draws the kind and is not linked is a finding. Owed unit `modal-depiction:<uid>`, on ANY change to an About-form modal (new to the form, its About, Guesses, Entry, Depiction
or Drawing) and when a page under `Drawing:` changed - whether or not the modal has the tab, so a conversion that drops its
drawing pages and writes no Depiction is still checked (the plan review, 2026-10-04);
`modal-research` no longer reads the drawing pages (its Entry is research questions only). The farmhouse is rewritten into the
form as the tab's first example and goes back to the GM.

### D14. An item that depends on the settlement's knobs (FR-015, amendment 2026-10-05)

A guess bullet, or a paragraph of About or Depiction, may open with a condition in brackets: `[settlement_form=nucleated]`,
or several values `[settlement_form=nucleated|linear]`. `_base.py` parses it off the item, checks the knob is in the populated
`KNOBS` registry and every value among its forms (else `ValueError` naming the knob's forms - a typo fails at import, as M21's
refusal does), and keeps it on the item. The page writer, which already reads the map's manifest `meta` for the windbreak's
side, keeps a conditional item when `meta[knob]` is among its values and drops it otherwise - a map that records no value for
the knob shows none of that knob's conditional items, since nothing says they hold there. The condition never reaches the
reader. The check bundles render each conditional item with "(only where <knob> is <value>)" so `modal-form`, `modal-research`
and `modal-depiction` judge it with its condition; the guidelines amend M9 and add M22. An `Entry:` path may carry the same
condition, written after it - `research/questions/0031-...html [settlement_form=nucleated]` - and is dropped from References
on a map where it fails, so a question resting only on a hidden item is not linked (FR-006, the spec review of the amendment).
First use: the windbreak's shared-wood guess, under `settlement_form=nucleated`, with 0031 conditioned the same. Row villages
(`linear`) are not in it: 0033 records that "a row farm kept its grove like any other farm".

## Constitution Check

- I, II: N/A - no gm-assistant UI; the map pages are this repository's own artifact under feature 134's rules.
- III, IV, V, VII: N/A - no pool content of a recurring kind, no SOURCE blocks touched.
- VI verify: each engine task runs `make quick`; each docstring or asset task `make page-check`; the landing runs `make done`
  (GATED). The review checks owed by occasion: none (no glyph, map or sheet new to the pool); the modal checks are D6's.
- VIII, IX: the About text is direct voice; particulars are checked against the GM's canon via `make canon` (D4, D11).
- X Python: ruff, pyrefly, red-green tests for the parser, the page data, the owed script and the prepass; 100% coverage;
  no file past 1,000 lines (sizes above).
- XII research: no map drawing changes. What the modals STATE changes: each statement is held to its research page by
  `modal-research`; a standard question the record does not answer gets the research pass (D8) before it may be a guess;
  each guess is a bullet on the Guesses tab saying what was searched. Decisions are in the spec's table.
- XIII regressions: maps and PNGs unchanged (the page is a second serialization, FR-010 of feature 134); the synthetic
  browser test and the interactive tests carry the page behavior. Baseline: `make page-check` green on the merge base before
  the first engine edit (worktree).
- XIV: defects found in the modals, the page or the tooling on the way are fixed in the work.
- XVI literal: every hamlet class, every choice value, every sheet kind and `### Features` entry is rewritten (FR-011); no kind
  exempted.
- Performance bookends: N/A - no generator stage changes; the page's data grows by a few KB of text.

## Risks

- The rollout is 56 hamlet classes, the choice values and 99 sheet kinds (`class ... (Kind)` lines in `compound_kinds/`,
  counted 2026-10-03), each with two checks; run as parallel
  writer agents on disjoint modules after the GM's go-ahead, checks dispatched per class from bundles.
- The research pass may open many questions (doors, walls, stored quantities for every building). Each goes to the page it
  belongs to; a session's page-write limits (feature 274) apply.
- Old and new forms coexist for the length of the feature; the last rollout task deletes the old form so nothing lingers.
