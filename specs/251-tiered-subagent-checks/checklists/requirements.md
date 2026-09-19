# Specification Quality Checklist: subagent checks tiered by model and effort

**Purpose**: Validate specification completeness and quality before proceeding to planning
**Created**: 2026-09-19
**Feature**: [spec.md](../spec.md)

## Content Quality

- [x] Focused on user value and business needs (tokens saved with no loss of quality; judgment stays on Opus)
- [x] All mandatory sections completed
- [ ] No implementation details - NOT MET BY DESIGN: this repository's tooling specs name the files and
  guards they change (see features 249, 250); the reviewer grades against `request.md`, which names them too

## Requirement Completeness

- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] All acceptance scenarios are defined
- [x] Edge cases are identified
- [x] Scope is clearly bounded (FR-009 lists what was declined)
- [x] Dependencies and assumptions identified

## Feature Readiness

- [x] All functional requirements have clear acceptance criteria
- [x] User scenarios cover primary flows
- [x] Feature meets measurable outcomes defined in Success Criteria
