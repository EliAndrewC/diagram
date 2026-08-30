# Specification Quality Checklist: Retire the post-placement check battery into the placer

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-08-30
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] No implementation details (languages, frameworks, APIs) - names existing artifacts (`check_village`, `pool/regressions/`) as the SUBJECT of the work, which is unavoidable for a feature whose subject is code that exists
- [x] Focused on user value and business needs - the GM's iteration-loop cost and the architectural argument
- [x] Written for non-technical stakeholders - the GM is the stakeholder and is the source of the argument
- [x] All mandatory sections completed

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous - FR-001 defines "fires"; FR-002 forbids the grep proxy
- [x] Success criteria are measurable - SC-001 zero unclassified, SC-003 byte-identical renders, SC-005 a number
- [x] Success criteria are technology-agnostic - stated as verdicts, coverage and render identity
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified - five, each drawn from a recorded incident in `dev/gate.md`
- [x] Scope is clearly bounded - User Story 3 is explicitly out of scope and FR-010 forbids it
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
- [x] No implementation details leak into specification

## Notes

- The one judgment call worth a reviewer's attention is FR-006 (read the placer before deleting a
  NEVER-FIRES check). It is a safeguard the GM did not name, justified by feature 158's recorded rule that
  the census's verdict is a candidate rather than a ruling. Sent to `spec-fidelity` specifically to be
  challenged as a possible carved-out exception (constitution XVI).
