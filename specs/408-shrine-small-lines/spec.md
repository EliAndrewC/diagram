# Feature 408: the shrine builder's small lines (diagram#10)

**Feature Branch**: none (main, in a session clone)

**Created**: 2026-10-21

**Status**: Draft

**Affects**: research record

**Approved**: the GM, 2026-10-21, "you should treat features that I have asked to be filed as automatic approval, and therefore you should not ask in the future"

The GM asked for issue #10 to be worked ("The GM assistant repo is currently watching that, so please go ahead and do
it."); a money research request gm-assistant opens for him is approved by his asking (GM 2026-10-18, quoted above).

**Input**: `request.md` (issue #10 verbatim), `passes/` (four search passes, 2026-10-21, one per group of the issue)

## Why

gm-assistant's shrine builder prices about fifty small lines (earthwork and grounds, small carpentry and furnishings,
remains and small rites, two small buildings, carrying stone) by its own estimate. The record answers a few of them
already (0255-0258, 0260, 0268-0271) and is silent on the rest; the issue asks for a verdict on each, the lines marked (S)
first.

## User Scenarios & Testing

### User Story 1 - Every line of #10 has a verdict and a fragment (Priority: P1)

gm-assistant reads, per line of the issue, the fragment file that answers it, the verdict, and what is still open.

**Acceptance Scenarios**:

1. **An item an earlier fragment already answers:** the reply names that file and the estimate it answers, and the record
   is not repeated (gm-assistant, #10: "just name the file and say which estimate it answers").
2. **An item a pass found:** the figure is written into the existing money question it belongs to (grounds and earthwork
   0257/0269, small carpentry and furnishings 0258/0270, remains and small rites 0271, the two halls 0268, carrying stone
   0260), quoted verbatim from a public page, with its verdict (ATTESTED, ATTESTED ONLY FOR <the case>, NOT ATTESTED); a
   new question only where none of those fits.
3. **Several items priced together:** the combined figure is given with the list of what it covers (gm-assistant, #10).
4. **An item no pass found:** SILENT, written into the question's absence note with the search named.
5. **Wages beside each figure:** the craftsman's and the laborer's day wage of the same place and period where a source
   gives them; otherwise SILENT naming the nearest, with its class, place, unit and gap in years.

### User Story 2 - The (S) lines are searched first (Priority: P1)

**Acceptance Scenarios**:

1. Each pass searches its group's (S) lines before the rest, and the reply lists the (S) lines first.

### Edge Cases

- A source only the GM can fetch goes on `research/to-download.md` (`make download-add`), named in the reply as a lead.
- A figure the project computes (a per-tsubo rate, a conversion to days) is labeled as the project's arithmetic.
- No price is converted to koku; that is gm-assistant's step.

## Requirements

- **FR-001**: Every line of the issue's four groups gets a verdict in the reply on #10, with the fragment file.
- **FR-002**: New figures are written into the record under the citation rules (research/CLAUDE.md), checked by the record
  checks `make record-owed` names before landing.
- **FR-003**: The feature closes with `make impl-check F=408` (money questions: no code implements them).
- **FR-004**: The reply is posted on #10; gm-assistant verifies and closes it.

## Success Criteria

- **SC-001**: 100% of the issue's lines carry a verdict and a fragment file in the reply.
- **SC-002**: `make record-owed` shows 0 unanswered for the touched questions at landing.

## Assumptions

- Japan first, China as comparison (the issue); GM canon overrides both.
- The estimates gm-assistant gives in koku are its own; this feature reports sources, not judgments on them.
