# Plan - 251 subagent checks tiered by model and effort, the mechanical parts in scripts

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Research: [`research.md`](research.md).

## Constitution Check

- **I / VI**: the checks stay independent of the author; this feature changes which model runs them and
  proves each downgrade on known findings (FR-011) before it stands.
- **XVI**: spec FAITHFUL at round 2 before any code; this plan reviewed (MODE 4) before any tick.
- **XVIII**: `_hm_review_round.py` is a guard's decision module; its change ships with new cases in
  `test-review-round-hooks.sh`, and every edit to a guard file carries `GUARD_EDIT_OK` with a reason.
- **X**: no engine code; four new scripts, each well under the 1,000-line bar, each with a test module
  under `tests/tooling/`.
- **XII**: nothing physical is decided; every task is `research: rendering`.
- **Route**: `scripts/`, `.claude/agents/`, `tests/`, the skill Makefile, docs -> DIRECT.

## Design

- **P1 the census (`scripts/_agent_census.py`, FR-001).** Stdlib only. Walks
  `~/.claude/projects/<project>/<session>/subagents/agent-*.meta.json` for every `<project>` whose name
  is `-diagram` or begins `-diagram-` (the mirror and its clones; `ROOT=` overrides for the test). Agent
  type from the meta's `agentType`. Per transcript: assistant records grouped by `message.id`, usage
  taken as the per-field maximum over the group (R2); the model from `message.model`. Row = agent type;
  columns = runs, turns, fresh input, cached input, output, thinking, per-run means, and a `models`
  tally. An ad-hoc block under the table: for the types with no file under `.claude/agents/`, how many
  runs carried no dispatch `model` and the models they actually ran on (the round-2 aside: Fable named
  specifically). `SINCE=` filters on the transcript's first timestamp. `--json` writes the same rows;
  the first run lands in `measurements.json` under `census-2026-09-19` and as the table in R1.
  `decide()`-style pure functions (`fold_usage`, `rows`, `render`) take plain dicts so the test needs no
  transcripts on disk beyond one small fixture tree.
- **P2 the verbatim script (`scripts/_quote_verbatim.py`, FR-003).** Stdlib only (`html.parser`,
  `urllib.request`). Three separable stages, each a pure function over text so each is tested with
  plain inputs: `footnotes(research_html, citations_html)` -> the entries (id, key, link, passage,
  original, translated flag, class, assertion); `visible_text(html_bytes, declared_charset)` -> text,
  decoding by the HTTP header, then the `<meta charset>`, then `utf-8`, then `shift_jis`, and reporting
  NOT-CHECKED when none decodes cleanly; `verdict(passage, page_text)` -> VERBATIM / DIFFERS /
  NOT-ON-PAGE. The match: both sides have runs of whitespace collapsed to one space; the passage loses
  only its DELIMITING quotation marks (the outer 「」 or curly or straight pair the footnote wraps it
  in); then `passage in page`. On a miss, DIFFERS is decided by `difflib.SequenceMatcher` over a sliding
  window of the page at the passage's length: a best ratio of 0.85 or more is DIFFERS with the window
  and the differing spans shown, under it NOT-ON-PAGE (0.85 is a reporting threshold, not a verdict of
  support: it only chooses which of two non-passing words is printed, and both go to the session). The
  fetch: one `urlopen` per distinct URL, 20 s timeout, a browser user agent, one attempt per HOST per
  run (a second URL on a host that refused is UNFETCHABLE without a request); `Content-Type` of
  `application/pdf` or a `.pdf` path is NOT-CHECKED (pdf). A passage with an elision (`...` or `[...]`)
  is matched piece by piece in order. A note that carries more than one link (the key's page and an
  "(on <page>)" alternative) is VERBATIM when the passage is on ANY of them. A page's own reference
  markers (`[3]`) inside a quoted sentence are NOT forgiven - the verdict stays DIFFERS, literal - but
  the entry carries `only_reference_markers: true` when removing them is all it takes, so the reader of
  the report dismisses it at a glance. The translated form: the ORIGINAL (after `original:`) is what is
  matched; the entry carries both so the agent can judge the translation. `make quote-verbatim
  PAGE=<name> [OUT=<json>]`; `--offline DIR` reads pages from files named by URL hash, which is how the
  test runs with no network.
- **P3 `quote-check` rewritten around the report (FR-004).** The Input section names the report as the
  first thing read; Procedure step 2 becomes "take the script's Readability and Quotation verdicts as
  given; fetch ONLY footnotes it marked UNFETCHABLE or NOT-CHECKED"; the verdict vocabulary and the
  Output section are untouched. The dispatching rule ("run `make quote-verbatim` first, name its report
  in the prompt") goes in `research/CLAUDE.md`, root `CLAUDE.md` and `docs/research-doctrine.md`.
- **P4 the record pre-pass (`scripts/_record_prepass.py`, FR-005).** Shares `visible_text` with P2 by
  import (`scripts/` is on the path for both via the same `_load` idiom the tests use; the module-level
  import is `from _quote_verbatim import visible_text` guarded by `sys.path.insert` of the script's own
  directory). Sections split on `<h2>`/`<h3>`. SESSION-NOTE patterns as a table of `(label, regex)`:
  `Grounds:`/`Evidence:` fields, `feature \d+`/`F\d{3}`, `T\d{2,3}`, `specs/\d{3}-`, `make [a-z-]+`,
  `[\w/]+\.(py|sh|json|md)`, a `<code>` span holding an identifier with an underscore or a dot, the
  fetch-verdict words in capitals. VOCABULARY candidates: CJK runs, `<i>`/`<em>` spans, a capitalized
  Latin binomial; each dropped when `glossary.json` has it as a term or a variant (case-folded). Output:
  per section, the label, the match and its sentence. The agent's Procedure gains a step 0 ("you are
  handed the pre-pass; confirm or dismiss each line") and keeps steps 1-3.
- **P5 the feet table (`scripts/_size_table.py`, FR-006).** `xml.etree` over the plan SVG: every
  `<rect>` (x, y, w, h -> ft at 3 px = 1 ft, honoring a parent `transform="translate(..)"`, other
  transforms reported as `transform not applied`), every `<line>`/`<path>` stroke width, and wall gaps -
  for collinear wall rects or lines sharing an axis within 1 px, the gaps between consecutive segments.
  Label = the nearest `<text>` by center distance, with the distance printed so a far label reads as
  doubtful. The agent's Method step 1 starts from the table and says to check it against the sheet and
  add what it missed.
- **P6 the tier table and the files (FR-002, FR-007).** `tests/test_agent_models.py`: `TIERS: dict[str,
  tuple[str, str]]`, the five assertions of FR-002 as separate tests so a failure names its rule, plus a
  non-vacuity count. Each agent file gains `effort:` under `model:`; `record-format` and `source-reader`
  move to `sonnet`. Descriptions and "Model" paragraphs restated to the present ruling (GM 2026-09-19),
  one line each; `test_entry_owed.py:134`'s `model: opus` assertion for `entry-drift` stays true and is
  left, with its message pointed at the tier table.
- **P7 the twin and the routing (FR-008).** `.claude/agents/spec-fidelity-verify.md`: frontmatter
  (opus, medium, `Read, Grep, Bash`), then MODE 3, FIGURES, the round-limit note and "What you do NOT
  do" copied from `spec-fidelity.md`; `spec-fidelity.md`'s MODE 3 shrinks to a pointer plus the
  hand-dispatch case. `_hm_review_round.py`: `AGENTS = ("spec-fidelity", "spec-fidelity-verify")`,
  `TWIN = "spec-fidelity-verify"`; `judge` admits either; on the rewrite branch `updated["subagent_type"]
  = TWIN`; the `history-without-snapshot` context names the twin; `previous_verdict` already finds a
  verdict by the feature directory named in the transcript, not by agent type (verified in the file), so
  it needs no change. The waist, enumerated by `grep -rn spec-fidelity scripts Makefile
  .claude/skills/diagram/Makefile .claude/settings.json container-scripts` (R3): CHANGED -
  `_hm_review_round.py`, `review-round-hooks.sh` (header text), `test-review-round-hooks.sh` (new cases:
  a rewritten dispatch carries the twin's type; a hand dispatch of the twin is rewritten, snapshotted
  and keeps its type), `container-scripts/append-system-prompt.md` (the authorized list), the settings
  matcher if it names the type; NOT KEYED on the type, recorded and left - `review-gate.sh` (greps the
  spec's text for FAITHFUL), `_plan_gate.py`/`plan-gate.sh`/`plan-verdict` (`AS=spec-fidelity` is the
  plan reviewer, MODE 4, which stays on `spec-fidelity`), `escalation-hooks.sh` (its roster is the three
  map reviewers), `pair-hooks.sh`, `_review_prereq.py`, `discard-hooks.sh`, `spec-lint.py` (mentions in
  comments). That the harness honors a changed `subagent_type` in `updatedInput` was PROVEN before this
  design relied on it (R4, 2026-09-19): a probe hook rewrote a dispatch of `probe-a` into `probe-b`, the
  reply was `probe-b`'s and the transcript meta names `probe-b`. The spec's fallback is not needed.
- **P8 the seeded-fault runs (FR-011).** Artifacts are picked by R5 from the record, each materialized
  under the scratchpad from `git show <commit-before-fix>:<path>` so nothing in the tree changes; one
  artifact per run, in the background. THE RUNS ARE HEADLESS SESSIONS STARTED IN THE CLONE (`claude -p
  --agent <name>`, working directory the clone), not Agent-tool dispatches: this session's agent types
  are the mirror's (R4), so an Agent dispatch would test the tier being replaced, and the Agent tool has
  no effort parameter. A headless session in the clone loads the clone's agent file with its pinned
  model and effort, which is the thing under test. Each run's reply is saved beside the artifact and its
  tokens are read from its own transcript by the census's `fold_usage`. R5's table is filled from the
  replies. Budget: six agents x three artifacts = eighteen runs.
- **P9 the record (FR-010, FR-012).** Root `CLAUDE.md`: the review-subagents bullet restated (tiers
  pinned per file, ad-hoc agents carry an explicit model - sonnet to read, opus to judge - never none),
  the research bullet gains "the verbatim check is a script, run first", the guard table's
  `review-round-hooks.sh` row says it routes. `docs/spec-kit-and-reviews.md`, `docs/research-doctrine.md`,
  `docs/guards.md`, `docs/efficiency-tooling.md`, `research/CLAUDE.md`, the memory file. The make targets
  carry `## [project]` help lines like their neighbors so `test_make_docs.py` sees them.

## Order

T01 census (task zero) -> T02 tier table + files -> T03 verbatim script -> T04 quote-check contract ->
T05 pre-pass + record-format -> T06 feet table + size-audit -> T07 twin + routing -> T08 seeded runs ->
T09 the record -> T10 `make hooks-test`, `make quick`, land, and THEN the question FR-010 owes the GM -
whether a hook should fill a missing model on an ad-hoc dispatch - put to them with R1's count (72
no-model runs, 62 of them on Fable), through `escalation-check` like any question for the GM. R1 may
reorder T03-T07; it cannot remove one, because each is a thing the GM approved.
