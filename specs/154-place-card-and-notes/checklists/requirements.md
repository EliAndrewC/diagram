# Specification Quality Checklist: The place card, and per-map notes the page can read

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-29
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) - the FRs name files only where the GM
      named them (`<name>.notes.md`) or where the constitution requires a record to land
- [x] Focused on user value and business needs - every story is written from the player at the page
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Success criteria are technology-agnostic
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified - the absent notes file, the malformed block, the non-hamlet scale,
      the empty crop list, markup in an annotation
- [x] Scope is clearly bounded - the HTML target and the notes files; the drawing is untouched
      (SC-007)
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- FR-008's "whether that is the ordinary case" is deliberately conditional on the research pass
  (Assumptions): the page ranks the hamlet type only if the record supports the ranking. Constitution
  XII forbids presenting a guess as a finding, and the GM's own phrasing - "if this is the most
  common type of hamlet that exists or whatever" - is a question, not an assertion.
- The independent spec review required by Principle XVI is `review-spec-fidelity.md` in this
  directory.
