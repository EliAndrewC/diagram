# Feature 292 - how a research section is presented

**Feature**: 292-research-presentation-style | **Created**: 2026-09-29 | **Status**: Draft (pilot phase)
**Input**: the GM's request, verbatim in [`request.md`](request.md).

## Summary

The research record is organized one section per question asked, and many of those questions arose mid-session, so
their headings read as session artifacts and one topic is scattered over several sections. The GM asks for a
STYLE GUIDE and a CHECK that holds it: a section is a TOPIC with a plain-English title; it opens with a short
plain-English account of what the thing was and why it existed; its findings follow as short bullets, most led by a
bold Q&A-style question on its own line; framing, restatement and descriptions of what the map plainly shows are
cut; unfamiliar terms are glossary tooltips; there is no `Sources:` roster and no quotation of the GM's inciting
question. Two mechanical changes come with it: a footnote tooltip's source link goes to the work's entry on the
citations page, not to the source; and a section's sources are read from its footnotes once it has no roster.

The feature runs in two phases. **Pilot**: write the guide and the check, rewrite one topic (the homestead grove),
and iterate topic by topic with the GM until they sign off on the guide and the check. **Sweep**: only after that
sign-off, tasks are added to rewrite every other section of the record in the style. Nothing lands on main during
the pilot; the GM reads the pages in this feature's clone.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A written style guide MUST state the presentation rules generalized from the GM's worked example -
  the topic title, the opening paragraphs, the Q&A bullet form (a bold question on its own line, a lead-in sentence
  where the numbers need context), one finding per bullet, what is cut (framing that the whole record presumes,
  restatements of a number already given, descriptions of what the map plainly shows, parenthetical asides carrying
  real content), when prose is left as prose, and the glossary as the place to explain a term - each rule with the
  GM's words it comes from.
- **FR-002**: Sections that cover one topic MUST be merged into one section under a plain-English title naming the
  topic, organized for a reader who knows nothing of it: the account of what the thing was and why first, then the
  findings in the order a reader needs them - never one section appended after another.
- **FR-003**: A restyled section MUST carry no `Sources:` roster, and removing a roster MUST lose no citation: every
  key the roster named is cited by a footnote of the section, and every passage the roster's own footnote quoted is
  quoted by a footnote in the section.
- **FR-004**: A section's sources, as the map's references read them, MUST be derived from the keys its footnotes
  cite when it has no roster.
- **FR-005**: The source link inside a footnote's hover MUST lead to that work's entry on the page's citations page
  (`citations/<page>.html#work-<key>`), which itself links the source.
- **FR-006**: The rule that the GM's inciting question is quoted verbatim in a section MUST be struck; the guide MUST
  say the inciting question appears nowhere in a section. Removing the existing quotations is the sweep's work.
- **FR-007**: "knob" MUST be a glossary term whose definition says what the GM said a knob is (the settings the
  generator varies to show the ways settlements differ - by chance, by region, by the lie of the land), and "canopy
  tree" MUST be a glossary term.
- **FR-008**: A check agent MUST judge a section against the guide - one verdict per rule, with the passage and the
  fix - pinned to a tier, launched without the repository's CLAUDE.md files, reading a bundle.
- **FR-009**: The pilot's first topic MUST be the homestead grove: the scale section the GM quoted, the section on
  the grove before 1868 that it links to, and the section on which sides of the house the grove took (split from the
  second by feature 291), folded into one section titled for the reader.
- **FR-010**: A merge MUST keep every finding, label (accurate / deviation / convention / GUESS), GM ruling, spec
  rule and footnote of the sections merged, except what the guide cuts by name; every link into a merged section MUST
  be re-aimed at the new anchor.
- **FR-011**: The GM's sign-off on the guide and the check MUST be an open task, and the sweep's tasks MUST NOT be
  written or started before it is ticked.

## Success Criteria *(mandatory)*

- **SC-001** (FR-001, FR-006): the guide exists, each rule carries the GM's words, and the struck inciting-question
  rule is gone from the rules files.
- **SC-002** (FR-002, FR-009, FR-010): the grove topic is one section with a plain-English title; the three old
  anchors resolve to nothing and nothing links to them; a diff of footnote keys and labels before and after shows
  each one kept or cut by a named rule.
- **SC-003** (FR-003): a test fails on a restyled section whose roster key or roster-footnote passage is quoted by
  no footnote of the section - proved by seeding one.
- **SC-004** (FR-004): a unit test derives a roster-less section's sources from its footnotes.
- **SC-005** (FR-005): a unit test shows the hover's key link aimed at the work's entry on the citations page.
- **SC-006** (FR-007): both terms are in the glossary and wrap on the restyled section.
- **SC-007** (FR-008): the check, run on the grove section as it stood before the rewrite, finds the faults the GM
  named in their example; run on the rewrite, it finds none it cannot justify.
- **SC-008** (FR-011, spec-wide): the tasks file ends the pilot in an unticked GM sign-off task.

## Decisions Recorded

- **Two phases in one feature**, as the GM proposed: the pilot's tasks, the sign-off task, and the sweep's tasks
  added only after it. Nothing is pushed to main during the pilot - the GM inspects the pages in
  `.clones/diagram-reorg`.
- **The third grove section is folded in too.** The GM named two sections; feature 291 has since split the second,
  moving its shape half into "Which sides of the house did a homestead grove take?". Folding only two would leave the
  grove on two sections for no reason the GM would accept, so all three are folded.
- **Built on feature 291's text.** Feature 291 is rewriting the same three sections in another clone and has not
  landed; this clone merges its committed work, so the rewrite starts from the corrected record, not from main's.
- **The 20,000-byte question cap** (feature 250 D14) bounds what one check reads. A merged topic may exceed it; the
  pilot measures the merged section and, if it is over, raises the choice with the GM (a topic cap, h3 subsections
  within the topic, or checks run on subsets of its notes) rather than splitting the topic the GM asked to merge.
- **The roster's job moves to the footnotes.** The map's references list read a section's sources from its roster;
  with no roster they are read from the keys its footnotes cite, which is the same set when the roster was honest
  (every roster key already had to be quoted by a footnote).

## Out of scope

- Rewriting any section other than the pilot's topics before the GM's sign-off.
- The map modals' own prose, except where a merge re-aims an `Entry:` tag.

## Review history

(none yet)
