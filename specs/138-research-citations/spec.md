# Feature Specification: Every Research Finding in the Diagram Skill Cites Its Sources

**Feature Branch**: none - this project does not use feature branches (`SPECIFY_FEATURE=138-research-citations`)

**Created**: 2026-08-28

**Status**: ESCALATED to the GM after round 3 (constitution XVI). `spec-fidelity` rounds: 1 = five changes (inventory under-inclusive; the gate check was unasked scope; FR-004 over-tightened; FR-006/FR-008 conflict; the count); 2 = four residues (US1 wording; the check surviving as SC-006; FR-008 mandating migration; the count's arithmetic); 3 = one residue (US1 Acceptance Scenario 2 still mandated migration, contradicting FR-008) - applied, and the reviewer's own note: "a mechanical miss rather than a persistent misunderstanding ... the rest of the spec is faithful". Implementation waits for the GM's word.

**Input**: [`gm-request.md`](gm-request.md), verbatim and unedited. That file is the authority for
this specification.

## The feature, in one sentence

Every historical research finding recorded in the diagram skill that was written down without
citing its sources is found, its research pass is redone under the project's current citation
rules (sources named, registered, read - or labeled SUMMARY-ONLY), the finding is left as it stands
when the re-research agrees with it (supplemented where the new reading usefully adds), and any
finding the new reading CONTRADICTS is corrected in the research record only - the maps and the
map generation are not touched, and each such case is brought to the GM to decide between fixing
now and documenting as future work.

## Why this exists (the GM's words)

- *"a rule which was added to our speckit constitution and our project guidelines after we had
  already done a lot of research was that all research should have citations. And I think that a
  lot of our past research does not."*
- *"find all of the research that we have done in the diagram skill, which does not cite
  sources. and then redo those research passes."*
- *"You don't need to rewrite those findings if they are the same, though if your research adds
  to them or finds things which do usefully supplement them, then that is fine."*
- *"The main thing that we want is to make sure that there are citations for all of the things
  that we have found."*
- *"if you find new sources that contradict what was there or if the previous summaries that we
  had found did not accurately summarize what was true ... you should update the research
  findings with the new citations, but do not make any actual changes to the maps or the map
  generation. if you find anything like this, then we should talk about what to do next"*

## What "research in the diagram skill" is (the inventory's scope)

The inventory covers **every place in the skill where a historical finding is written down** -
the constitution's own words are "in `research/`, a feature's `research.md`, or wherever a
finding is first written down" - because the GM asked for *all* of the research, not for one
file. The homes known at the start:

1. **The research tree** (`.claude/skills/diagram/research/`) - the canonical home. Counting
   rule: an entry is a `## ` heading in any file there other than `README.md` and `SOURCES.md`.
   At the start of this feature **73** entries carry a `**Sources:**` line saying `not recorded`
   and about **44** more carry no `**Sources:**` line at all (most are recent entries that name
   their sources in the prose; the pass normalizes each to a sources line or finds its sources)
   - roughly 117 candidate rows out of ~156-167 headings depending on how a heading that only
   contains a section title is counted; the ledger is the authoritative row list, and a row that
   proves to be a section header rather than a finding is struck with that note. The 73 is the
   firm number; the rest is resolved row by row.
2. **Standalone research documents** under the skill root - `flophouse-research.md`,
   `town-deep-audit.md`, `town-checks-audit.md`, `pending-enclosed-fan-floor.md` and any other
   file there that states a historical finding.
3. **Inline "Historical grounding" prose in any operative or pool document** - the top-level
   `settlements.md` (its "Historical grounding" section), `settlements/*.md`,
   `settlements/cities/*.md`, `buildings.md`, `buildings/programs.md`, `SKILL.md`, and the pool
   notes files (`pool/**/*.notes.md`) - findings written next to their rule or their map before
   the research tree existed, some migrated to (1) with a pointer, some not.
4. **Historical research in spec-kit feature directories** (`specs/NNN-*/research.md`) - the
   research a feature did at plan time. Only the HISTORICAL findings are in scope (how a place
   was built, farmed, planted, lived in, governed, defended); technical research (package
   layout, caching, CI, test tooling) has no sources to cite and is out of scope.
5. **Grounding stated in engine comments** (`l7r/**/*.py` - e.g. a comment giving a Chinese
   county seat's street share, or an Edo zoning law) - a finding is a finding wherever it sits.

A finding that lives in engine code or a pool artifact is **recorded and cited in the research
tree, with the code and the pool text left untouched** - that is how the inventory stays complete
without breaking the GM's prohibition below.

A finding is "uncited" when it names no source a reader can check: a `**Sources:**` line saying
`not recorded`, a grounding paragraph with no sources line at all, or a citation the current rule
excludes (an AI-generated encyclopedia; a search summary cited as if read). The re-sourcing queue
already kept in `research/SOURCES.md` is part of the inventory, not a separate list.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - The uncited research is found and counted (Priority: P1)

A session produces the complete inventory of uncited findings across every home above - the research tree, the standalone research documents, the inline grounding in operative and pool documents, the historical spec research and the engine comments - as a
ledger the feature's later tasks work through and tick off - so "are we done" is a count, not an
impression.

**Why this priority**: the GM's first verb is "find all of"; without the inventory nothing else
can be shown complete.

**Independent Test**: the ledger exists; a fresh scan of all five homes for uncited findings
returns exactly the ledger's open rows.

**Acceptance Scenarios**:

1. **Given** the research tree, the standalone research documents, the inline grounding in
   operative and pool documents, the historical spec research and the engine comments, **When**
   the inventory is taken, **Then** every uncited finding appears in the ledger once, with where it
   lives, the rule it grounds, and its status (open / re-sourced / contradicted).
2. **Given** a finding that lives inline in an operative doc with no entry in the research tree,
   **When** it is inventoried, **Then** it is listed as needing citations by either route of
   FR-008 - a `**Sources:**` line in place, or a cited research-tree entry with a pointer from
   the rule.

---

### User Story 2 - Each uncited finding gets a real research pass and real citations (Priority: P1)

For each ledger row a research pass is redone under the current rules: sources searched, the ones
that support (or contradict) the finding READ - by the `source-reader` agent, which returns a
quote - registered by key in `research/SOURCES.md` with what each was used for, and the finding's
`**Sources:**` line filled in. A source that could not be fetched may be cited as SUMMARY-ONLY,
labeled as such. When the reading agrees with the finding, the finding's text is left as it is;
when it usefully adds (a figure, a named instance, a statute), the addition is made.

**Why this priority**: *"The main thing that we want is to make sure that there are citations for
all of the things that we have found."*

**Independent Test**: pick any ledger row marked re-sourced; its entry cites at least one key;
that key is in `SOURCES.md`; the `source-reader` report for that key says READ (with a quote) or
the entry says SUMMARY-ONLY.

**Acceptance Scenarios**:

1. **Given** an entry whose sources line says `not recorded`, **When** its pass is done and the
   reading agrees, **Then** the entry's prose is unchanged (or supplemented), its sources line
   names keys, and every key is registered with a use.
2. **Given** a source that cannot be fetched (paywall, blocked host), **When** it is the best
   source found, **Then** it is cited with the SUMMARY-ONLY label and what was seen, never as
   read.
3. **Given** a claim for which the pass finds NO checkable source, **When** the pass ends,
   **Then** the entry's sources line says so explicitly (what was searched and not found), its
   evidence class is corrected to `reconstruction` or the entry is labeled a guess - it is never
   given a plausible-looking citation after the fact.
4. **Given** a finding whose only citation is a source the rule excludes (the re-sourcing queue),
   **When** its pass is done, **Then** the excluded source is replaced by a checkable one or the
   finding is handled as in scenario 3, and the queue row is struck.

---

### User Story 3 - A contradicted finding is corrected in the record, and ONLY the record (Priority: P1)

When the re-research finds that a recorded finding is wrong - a new source contradicts it, or the
earlier summary misrepresented what its source actually says - the research entry is updated with
the corrected finding and its citations, the rule it grounds is left exactly as it is, and NO map,
generator, check, constant or pool artifact changes. Each such case is written up for the GM: what
the record said, what the sources say, which rule and which maps it would affect, and the two
options the GM named - fix now, or document as future work.

**Why this priority**: the GM gave an explicit prohibition (*"do not make any actual changes to
the maps or the map generation"*) and an explicit next step (*"we should talk about what to do
next"*); getting this wrong undoes the feature's trust.

**Independent Test**: the diff of the feature touches no engine code, no pool artifact and no
operative rule text; every contradiction is listed in one place for the GM with both options.

**Acceptance Scenarios**:

1. **Given** a finding the sources contradict, **When** its pass is done, **Then** the research
   entry states the corrected finding with citations, keeps the old finding visible as what the
   rule currently implements, and marks the entry `contradicted - rule unchanged, awaiting GM`.
2. **Given** one or more contradicted findings at the end of the feature, **When** the feature
   is reported to the GM, **Then** the report lists each with its affected rule and maps and asks
   fix-now versus future-work; nothing has been changed on the map side in the meantime.
3. **Given** zero contradicted findings, **When** the feature is reported, **Then** the report
   says so explicitly.

---

### Edge Cases

- A finding rests on the GM's own setting notes (`setting-canon`): its source is `l7r.md` /
  `budgets.md` - cited by pointer, not researched historically.
- A finding is a disclosed `liberty`: what is re-sourced is the historical answer it departs from,
  not the departure.
- A finding that was RIGHT but whose earlier text over-generalized (one region's figure stated as
  universal): that is a supplement (scope stated), not a contradiction, unless the rule depends
  on the generalization - then it is reported to the GM as a contradiction.
- Two findings in different files rest on the same source: one key, cited twice.
- A source read once for one entry supports another entry's claim only partly: the second entry
  cites it for exactly the part it supports (`SOURCES.md` "used for" records both uses).
- The pass finds the earlier finding was drawn from a source the current rule excludes
  (Grokipedia): re-source from what that article itself cited, or a better source; never keep it.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The feature MUST produce a ledger of every uncited historical finding across every
  home listed above (research tree, standalone research documents, inline grounding in operative
  and pool documents, historical spec research, engine comments), one row per finding, with
  location, grounded rule and status.
- **FR-002**: For every ledger row the feature MUST redo the research pass under the constitution's
  current rules: sources searched; those cited READ via the `source-reader` agent (a quote on
  record) or labeled SUMMARY-ONLY; never an AI-generated encyclopedia; never a search summary as a
  source.
- **FR-003**: Every source cited MUST be registered by key in `research/SOURCES.md` with what it
  was used for; every re-sourced entry's `**Sources:**` line MUST name its keys.
- **FR-004**: A finding the re-research AGREES with need not be rewritten - the requirement is
  the citation. Its prose MAY be supplemented or corrected for scope and accuracy where the
  reading supports it (a figure, an instance, a statute, a scope); the real prohibition is FR-006.
- **FR-005**: A claim for which no checkable source is found MUST say so on its sources line
  (what was searched) and have its evidence class corrected; it MUST NOT receive a citation that
  was not consulted.
- **FR-006**: A finding the re-research CONTRADICTS MUST have its research entry corrected with
  citations and marked contradicted. Nothing a generator, check or constant reads changes, no
  pool artifact changes and no map is re-rendered by this feature; the operative rule text is
  unchanged except for a pointer to its research entry (FR-008).
- **FR-007**: The feature's report to the GM MUST list every contradicted finding with the rule
  and maps it affects and the two options (fix now / document as future work), or state that
  there were none.
- **FR-008**: An inline grounding finding that cites no source MUST gain citations - either a
  `**Sources:**` line in place, or a research-tree entry (four fields, sources) with a pointer
  from the rule. The rule text itself stays. A finding that lives in engine code or a pool
  artifact MUST take the research-tree route, since the code and the pool text are not touched.
- **FR-009**: The existing re-sourcing queue in `SOURCES.md` MUST be worked as part of the
  inventory and each row struck when re-sourced.
- **FR-010**: The feature MUST NOT add a guard or gate check; the GM did not ask for one, and
  the project's standing decision is that Principle XII is not enforced by a guard.
- **FR-011**: Every task of the feature is classified `research: physical` and carries the three
  research boxes (constitution v2.12.0); the gate's task-research test applies.
- **FR-012**: The feature MUST run its review subagents where the project requires them:
  `spec-fidelity` on this spec against `gm-request.md` before implementation; `source-reader` on
  every pass. No map is rolled, so no `settlement-review` is owed.

### Key Entities

- **Finding**: one recorded research result - anchor, grounded rule, evidence class, sources,
  prose. Lives in the research tree.
- **Source**: a work a reader can check, registered by key with what it was used for; status READ
  or SUMMARY-ONLY per entry.
- **Ledger row**: one uncited finding and its status - open, re-sourced (agrees / supplemented),
  no-source-found, contradicted (awaiting GM).
- **Contradiction report**: the list for the GM - finding, what the sources say, rule and maps
  affected, fix-now / future-work.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Zero research-tree entries say `not recorded` or lack a sources line; zero findings
  in the other homes (standalone research documents, inline grounding in operative and pool
  documents, historical spec research, engine comments) lack either sources of their own or a
  pointer to a cited research-tree entry - the ledger's open-row count is zero.
- **SC-002**: 100% of cited keys are registered in `SOURCES.md` with a use; 100% of READ keys have
  a `source-reader` quote on record; every SUMMARY-ONLY key says what was seen.
- **SC-003**: The feature's diff contains no change under the engine paths or the pool, and no
  change to the operative rule text of any settlement/building document other than a pointer to
  a research entry.
- **SC-004**: Every contradicted finding appears in the GM report with both options; the GM can
  decide each without reopening the research.
- **SC-005**: The re-sourcing queue in `SOURCES.md` is empty (or lists only items the pass
  documented as unresolvable, each with what was searched).

## Decisions Recorded

This feature changes what NO map draws or states; it changes what the RECORD says about why. Each
re-sourced entry keeps or corrects its own accurate / deviation / guess class in place, and every
contradiction is a row in the GM report rather than a rendering decision - the rendering decision
is the GM's to make afterwards. The interactive map (feature 134) reads the same entries, so a
corrected class reaches its reader automatically once the GM has ruled.

## Assumptions

- "The diagram skill" means the tree under `.claude/skills/diagram/` plus the historical
  `research.md` files of this repository's spec-kit features (whose findings the research tree
  cites); gm-assistant's own research is not in scope.
- Technical research in spec directories (package layout, CI, tooling, test audits) is not
  "research" in the GM's sense and needs no citation.
- The feature will be long and is worked in batches by research file; each batch is a task, and
  a batch's pushes are DIRECT (docs only) - engine paths are never touched, so no
  CodeBuild run is owed. The `specs/` claim is pushed first, as the project requires.
- "Redo the research pass" means a genuine search and read, not attributing a source from
  memory; where a finding cites an anchor (Takayama Jin'ya, Pingyao) the anchor's own
  documentation is the source to read.
- Where a session's own doubt or a reviewer's comment surfaces a NEW question during a pass, it
  is researched under the same rules (constitution XII) and recorded; it does not change a rule.
