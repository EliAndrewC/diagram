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
and a convention are said in the About text, the evidence classes stay on the research pages). Both forms parse until the
rollout ends; the last rollout task removes the old form and its tests. (FR-002, FR-005)

**D2 - The tabbed modal.** One dialog; a tab strip `About` / `Guesses` / `References` of buttons (`role="tablist"`), a tab with
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

**D10 - The title card's choices (phase after the pilots; sketch, settled then).** The manifest's `meta` already holds every
rolled or declared knob value (`settlement_form`, `lane_web`, `bamboo`, `harvest_weather`, `byre_form`, `hamlet_burial`,
`family_form` ...). A declared table (`interactive/assets/choices.json`) names which meta keys are choices - EVERY per-settlement choice,
rolled, declared or pinned (FR-009's "every"); it separates choices from the meta's other keys (measurements, counts) and
leaves no knob off - a test holds every knob `settlement/_knobs.py` declares and every meta key a `### Features` fact came from
in the table -
their reader-facing name, and for each value the key of its modal; each value's modal is a class in a new registry
(`interactive/choices/`) in the new form, standardized across maps. The per-map `### Features` facts of the five hamlets
become choices (burial ground form, harvest weather, the retirement-house custom) or a title-card count ("10 of its 15
homesteads have a retirement house"); the page stops reading `### Features` for a hamlet, and a test holds that no hamlet
feature modal differs between two pool maps. (FR-004, FR-009)

**D11 - Sheets (phase after the hamlet rollout).** Every compound kind is tagged `Form: particular` or left standard by
`particulars.py` membership and by each kind's content (a kind particular to the setting even if on several sheets is
particular); each sheet's `### Features` entries are reviewed under the particular guidelines; the canon answer goes in the
`modal-research` bundle for particulars. (FR-003, FR-011)

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
