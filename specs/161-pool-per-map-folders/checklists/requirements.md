# Specification Quality Checklist: One folder per map, and the frozen hand-authored pool moved out of `pool/`

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

**Note on the first item.** This spec names existing repository artifacts - `poolmaps.classify()`,
`pool/regressions/`, `regen.py`'s scope lock - and that is deliberate, not a leak. The feature's
subject IS the repository's own directory layout, so those names are the domain vocabulary rather
than an implementation choice: FR-011 says the classification must keep answering the same, not how
it should be written. No requirement here dictates a data structure, an algorithm or a call.

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain

  The two questions that genuinely had no reasonable default - filenames inside a map's folder, and
  whether one index or two - were put to the GM before the spec was written and are recorded as
  answered decisions in FR-002 and FR-016.

- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic (no implementation details)
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified

  Six, each drawn from a real property of the current tree rather than invented: an unrendered map,
  a tier that empties, a tier present in both trees, the scope-lock glob, the regression corpus,
  and the `ubame` name collision across trees.

- [x] Scope is clearly bounded

  In: `pool/` and its consumers. Out: `wip/`, the classification itself, any change to what a map
  draws.

- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- The three user stories map one-to-one onto the request's three paragraphs, which is the shape the
  spec review (Principle XVI) will grade against.
- SC-004 and SC-007 exist because the failure mode of a large mechanical move is a file quietly
  altered or a reference quietly missed; both are stated as things to VERIFY by measurement rather
  than by reading.
- The "Decisions Recorded" section is kept and explicitly empty. This feature changes nothing a
  reader of a map could click on, and saying so is more useful than deleting the heading.
