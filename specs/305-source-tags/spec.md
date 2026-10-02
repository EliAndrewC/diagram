# Feature 305 - source tags

**Feature Branch**: none (main, in the clone `diagram-organization`)
**Created**: 2026-10-02
**Status**: FAITHFUL at round 1 (2026-10-02)
**Request**: [`request.md`](request.md) - the GM's words verbatim. A source's write-up today explains, entry by entry, the
limits that come with its *category*: a tourism page cites no study, a present-day page gives modern counts. The GM asks
for tags on the sources, so that (1) the works cited are *"put into sections based on their tags, like `Present day` or
`Premodern Japan` or `Premodern China` or `Modern preindustrial`"* rather than shown in citation order, and (2) the
assembly *"automatically applies the correct labels with ... tooltips to convey the standardized explanation of the
strengths and limitations inherent to the category of source, in addition to the specific explanation"*, so the
category explanation is no longer *"repeat[ed] ... for every similar source"*. The distinctions the GM names: present day
vs premodern; *"preindustrial communities which nonetheless are still in the modern era"* (around 1900, with cheaper
metal tools); Korea and Europe as *"less applicable"*; Imperial China apart from Imperial Japan. The GM left the ideal
set of tags to the session (*"perhaps you can take a look and think through it"*). Message 2 left the period cut-offs to
the session's judgment *"as long as you explain the logic in the tooltips"*. Message 3 confirmed the third facet,
the kind of publication, and asked for the feature to be implemented start to finish.
**Predecessors**: 211 (each work's write-up is written once, in its registry entry), 280 (the modern-only sweep),
301 (the record built as a site), 303 (the record's questions organized by tags; the rule-file idiom reused here).

## Summary

Every keyed work in the registry (2,126 entries, counted 2026-10-02 by listing the files in `010-works-cited/`) carries tags on three facets:

- **Period**: when the evidence the record takes from the work dates from. This is not when the work was published.
  A 2004 article on Edo-period field registers is premodern evidence.
- **Region**: where that evidence comes from.
- **Kind**: what sort of publication the work is.

Each tag has a short label and a standard explanation of what the category is good for and where it falls short. The
build shows the labels on every work wherever the work is listed, and the explanation appears when the reader hovers a
label. The works are grouped into sections derived from the tags by a rule file, in the order of how much weight the
record gives them. The write-ups keep only what is specific to their source: once the label carries the category's
standard limits, the write-up no longer repeats them.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - A reader sees what kind of source they are checking (Priority: P1)

The GM opens a question page, follows a footnote down to "Works cited here", and reaches `visit-toyama-sankyoson`.
Beside its key are three labels, for example *Present day*, *Japan* and *Popular*. Hovering *Present day* explains what a
present-day source is good for (evidence that a form exists and how it is laid out) and why its numbers are anchors
rather than measurements (mechanization, land consolidation, and a population and economy unlike the setting's). The
write-up beneath says only what is particular to this page.

**Why this priority**: this is the GM's central ask - the category's limits conveyed once, by the build, for every
source of the category.

**Independent Test**: build the record; on any question page every listed work carries one label per facet, and each
label's hover text is its vocabulary entry's explanation.

**Acceptance Scenarios**:

1. **Given** a work tagged present-day, Japan, popular, **When** its entry is shown on a question page, on the
   single page or on its registry page, **Then** it shows those three labels, each with its standard explanation on
   hover. Without scripts, the explanation is the label's native tooltip.
2. **Given** a work with two regions (a comparative study of Japan and China), **When** it is shown, **Then** both
   region labels appear, the primary first.
3. **Given** a work citing the GM's own campaign notes, **When** it is shown, **Then** it carries the *Setting canon*
   label and no period, region or kind.

### User Story 2 - Works are grouped by how much they weigh (Priority: P1)

A question's "Works cited here" is no longer one list in citation order. It is a short run of sections, for example
*Premodern Japan*, then *Premodern China*, then *Present-day East Asia*, each holding the works the question cites that
fall in it. The registry's own index and the single page's Sources part use the same sections.

**Why this priority**: the GM's other explicit ask.

**Independent Test**: build the record; every works list is a sequence of section headings in the rule file's order,
and every work sits under the first section whose rule takes its tags.

**Acceptance Scenarios**:

1. **Given** a question citing premodern Japanese, premodern Chinese and present-day Japanese works, **When** its page
   is built, **Then** its works appear under three headings in the rule file's order. Within a section the works keep
   the order of the page's first citations.
2. **Given** the registry index, **When** it is built, **Then** the works-cited group lists its sections in the rule
   file's order, each with its description, and the works within a section keep the registry's order.
3. **Given** a section that holds none of a page's works, **When** that page is built, **Then** no heading is shown
   for it.
4. **Given** the rule file reordered or a rule changed, **When** the record is rebuilt, **Then** the grouping follows,
   with no entry edited.

### User Story 3 - Tags cannot go missing or drift (Priority: P2)

A session adding a source writes its tags when it creates the entry. A session that forgets, or that types a tag the
vocabulary does not hold, is refused by the record's build check, which names the entry and the facet. The review agent
that already judges a write-up's honesty also judges whether the entry's tags are right.

**Why this priority**: without it the grouping decays as soon as the next research session lands.

**Independent Test**: remove one entry's region tag; the record's build check fails naming that entry and that facet.
Restore it; the check passes.

**Acceptance Scenarios**:

1. **Given** an entry missing a facet, or carrying a value not in the vocabulary, **When** the record is checked,
   **Then** the check fails, naming the entry, the facet and the allowed values.
2. **Given** a tag combination no section's rule takes, **When** the record is checked, **Then** the check fails,
   naming the entry and the combination.
3. **Given** a session reserving a new registry entry, **When** it gives the tags, **Then** the stub carries them.
   **When** it gives none, **Then** the stub carries placeholders the build check refuses until they are filled.
4. **Given** a new or changed write-up, **When** `source-applicability` judges it, **Then** its verdict covers whether
   each tag is right, and whether the write-up repeats a category limit its labels already state.

### User Story 4 - Every existing work is tagged, and the write-ups lose the repetition (Priority: P2)

All 2,126 existing entries are classified. Each "Why it applies, and its limits" paragraph is then trimmed of the
sentences that only restate its labels' standard explanation. It keeps why the source applies and every limit specific
to it.

**Why this priority**: the GM's motivating complaint is the repetition. Without the classification, the gate in Story
3 cannot be switched on.

**Independent Test**: the build check passes with no entry exempt. A seeded sample of entries is judged by
`source-applicability` for tag accuracy and for any category limit still repeated in the write-up.

**Acceptance Scenarios**:

1. **Given** `visit-toyama-sankyoson`, **When** the trim lands, **Then** its limits paragraph no longer says it is a
   promotional page citing no study, or that it gives modern round counts for a living landscape. It still says it is
   one plain in one prefecture, and that the density figure is the record's own division of the page's two round
   figures.
2. **Given** a write-up whose only limits are its category's, **When** the trim lands, **Then** its paragraph still
   says why the source applies, and does not invent new limits to fill the space.

### Edge Cases

- **Evidence spanning periods** (an article tracing terraces from the Edo period to today): the entry carries every
  period it supplies evidence from. The primary period, listed first, is the one the record's citations of it rest on,
  as its "Used for" line shows.
- **A modern work about premodern evidence** (an archaeology report, or a historian reading an 1830s register): period
  follows the evidence, so the work is premodern. Kind (scholarship) carries how far it can be trusted.
- **A present-day site preserving a premodern building or landscape** (a rebuilt barrier, a preserved farmhouse): the
  premodern form is tagged premodern, with the restoration's limits stated in the write-up when they matter. A claim
  about the present working landscape is tagged present-day.
- **Facts not tied to a period or place** (how a tree grows, how a wet moat holds water): period *not period-bound*,
  region *general*.
- **The GM's campaign notes** (16 entries name `l7r.md` or `budgets.md`): these are canon, not evidence. They get no
  period, region or kind, carry one fixed *Setting canon* label, and form their own section, first.
- **Ryukyu, Taiwan, Vietnam**: the *other East Asia* region. South Asia, the Americas and studies that span the world
  are *elsewhere*.
- **An entry with no write-up yet**: it is already refused by the build (feature 211); tagging does not change that.

## Requirements *(mandatory)*

### Functional Requirements

**The vocabulary**

- **FR-001**: One vocabulary file declares the three source facets and their values. Each value has an id, a short
  label, and a standard explanation of the category's strengths and limits written for a casual reader. The file also
  holds the fixed *Setting canon* label and its explanation.
- **FR-002**: The starting values are:
  - **Period**: premodern; modern preindustrial; present day; not period-bound.
  - **Region**: Japan; China; Korea; other East Asia; Europe; elsewhere; general.
  - **Kind**: primary; scholarship; reference; institutional; popular.

  The classification pass may add a value where a real group of entries fits none of these. A value is never removed
  while an entry carries it.
- **FR-003**: Each period explanation states its cut-off and the logic behind it (GM, message 2). Every cut-off is set
  by region, because the regions industrialized at different times. The explanation names the change that ends the
  period and says why that change matters to the evidence: cheap iron and new crops, land reform, railways and
  markets, mechanization and land consolidation.

**Tagging the entries**

- **FR-004**: Every keyed registry entry carries at least one value per facet, with the primary value first. Canon
  entries carry none and are recognized as canon by the rule the registry already uses.
- **FR-005**: The tags are written in the entry, in a form a grep finds and the reader never sees as raw text.

**The build**

- **FR-006**: A section rule file, in the idiom of `research/contents.json`, declares the works sections in order. Each
  section has an id, a title, a one-line description and a rule over the primary tags. A work belongs to the first
  section whose rule takes it, and Setting canon is a section of its own, first. Regrouping is an edit to this file
  alone.
- **FR-007**: The works sections are, in order:
  1. Setting canon
  2. Premodern Japan
  3. Premodern China
  4. Premodern Korea and East Asia
  5. Not period-bound
  6. Modern preindustrial East Asia
  7. Present-day East Asia
  8. Beyond East Asia, and general works

  The last section takes every work whose primary region is Europe, elsewhere or general, whatever its period, so
  every combination of tags has a section.

  The order is the weight the record gives each group. Canon governs. Premodern East Asian evidence is the setting's
  model, Japan and China first since Rokugan draws on both. Physical facts transfer whole. Modern preindustrial
  evidence comes before present-day evidence because it shows hand farming. Korea is East Asian but stands apart from
  the two models; Europe and the rest share least.
- **FR-008**: Every list of works the record shows groups its works under the section headings, with each heading's
  description, and omits a section that holds none. This covers a question page's "Works cited here", the single
  page's Sources part and the registry index. Within a section, a question page keeps first-citation order and the
  registry keeps registry order.
- **FR-009**: Every work, wherever it is shown in full, shows one label per tag it carries. That means a question
  page's works, the single page and its own registry page. A label's hover shows its vocabulary explanation in the
  record's existing tooltip box, and without scripts its native tooltip carries the same text.
- **FR-010**: The record's build check refuses, naming the entry and what is wrong (for a missing or unknown value, the facet and its allowed values; for an untaken combination, the combination), in three cases:
  - an entry missing a facet;
  - an entry carrying a value the vocabulary does not hold;
  - an entry whose primary tags no section takes.

  It runs at `make record CHECK=1`, at the gate and at the push.

**The tools and the checks**

- **FR-011**: `make reserve KIND=registry` takes the tags and writes them into the new entry's stub. Without them it
  writes placeholders that FR-010 refuses.
- **FR-012**: The `source-applicability` contract is amended. It judges each tag's accuracy against the entry and its
  source, and whether the write-up restates a limit its labels already state. The contract carries the vocabulary's
  explanations, since a defined agent launches without the record's `CLAUDE.md` files.
- **FR-013**: The operative docs state the rule where a session writing an entry will read it: the research
  `CLAUDE.md`, the research doctrine and the page-session rules. The rule is to tag every entry, judge period by the
  evidence and not the publication, and keep the write-up's limits to what is specific to the source.

**The migration**

- **FR-014**: All existing keyed entries are classified on all three facets before FR-010 is switched on.
- **FR-015**: Every "Why it applies, and its limits" paragraph is trimmed of what only restates its labels'
  explanations. It keeps why the source applies and every source-specific limit, and gains nothing new. The other
  paragraphs of an entry ("What it is", "Used for", the citation line) are not changed by the trim.

### Key Entities

- **Source facet**: period, region or kind. Each has its values.
- **Tag value**: an id, a label and a standard explanation.
- **Works section**: an id, a title, a description and a rule over primary tags. Its position in the rule file is its
  weight.
- **Registry entry**: a keyed work with its tags, primary first.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** (FR-004, FR-005, FR-014): Every keyed registry entry carries valid tags on all three facets, or is canon. The build check passes
  with no exemption.
- **SC-002** (FR-010): The build check fails on each of three seeded faults: a missing facet, an unknown value, and a combination
  no section takes. Each failure names the entry.
- **SC-003** (FR-006, FR-007, FR-008, FR-009): On every question page, the single page and the registry index, every listed work is under exactly one
  section heading, the headings follow the rule file's order, and every work in full shows a label per tag, each with
  its explanation as hover text.
- **SC-004** (FR-001, FR-002, FR-003, FR-004): An independent `source-applicability` check of a stratified sample of at least 60 entries, covering every
  period and region value, rules at least 19 in 20 of the sampled tags correct. Every wrong tag found is fixed, and the
  sample's error pattern is checked across the rest of the registry.
- **SC-005** (FR-015): After the trim, the same sample shows no write-up restating a category limit its labels state, and no
  write-up lost a source-specific limit or its reason for applying.
- **SC-006** (FR-015): Measured over the whole registry, the total length of the limits paragraphs falls. The figure is
  reported, not targeted.

- **SC-007** (FR-011, FR-012, FR-013): `make reserve KIND=registry ... TAGS=` writes a valid marker and refuses an
  unknown value by name; the `source-applicability` contract's vocabulary block matches the vocabulary, and a test fails
  while it does not; the research `CLAUDE.md`, the research doctrine and the page-session rules state the tagging rule.

## Decisions Recorded

This feature draws nothing on a map and states nothing new about one. It labels and groups the record's sources.

| Decision | Class | Why | Recorded at |
|---|---|---|---|
| Three facets: period of the evidence, region, kind | the GM's examples (period, region) plus the session's third facet, confirmed by the GM (message 3) | period and region set applicability; kind sets reliability (the tourism page's caveat) | the vocabulary file; FR-001 |
| Period follows the evidence, not the publication | session judgment | a modern study of Edo registers is premodern evidence; tagging by publication date would bury the best scholarship among tourism pages | the vocabulary's period explanations; `research/CLAUDE.md` |
| The period cut-offs, by region | session judgment, delegated by the GM (message 2) | each region's own industrial transition; the logic is stated in each tooltip | the vocabulary file (FR-003) |
| The section order (FR-007) | session judgment | the record's weight: canon, then the setting's models, then physical facts, then the modern groups, then the regions furthest from the setting | the section rule file; FR-007 |
| Canon gets one fixed label and the first section | session judgment, from the record's rule that the GM's notes are canon, not evidence | they need no applicability judgment | the vocabulary file; the rule file |
| Within a section, first-citation order on a question page | carried from feature 211 D7 | the reader arrives from a footnote | `citations.py` |

## Assumptions

- The classification reads the existing write-ups (most state their period and place) and fetches nothing. A write-up
  too thin to classify from is classified from its cached page or its source, and its write-up is fixed where it was
  wrong (XIV).
- The map's own pages (the modals) show no source write-ups today, so they gain no labels. If a later feature adds
  works to a modal, it reuses the same labels.
- The 16 canon entries stay where they are in the registry; only their display section changes.
- Attested instances (the anchors table) are not keyed works and are not tagged.

## Review history

- Amendment 1 (2026-10-02, during implementation): traceability only, for spec-lint's check once tasks.md exists -
  SC-001..SC-006 name the FRs they verify, and SC-007 is added for FR-011..FR-013, which no criterion named. No
  requirement changed.

- Round 1 (spec-fidelity, 2026-10-02): FAITHFUL. Two asides, not findings, both taken: the 2,126 count now says how it
  was counted, and FR-010's message names the combination for an untaken combination rather than "the allowed values".
  FR-007's last section now takes general-region works of any period, so a premodern general work has a home.
