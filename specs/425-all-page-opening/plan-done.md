# 425-all-page-opening - the plan's finished sections (feature 375 FR-044; no review reads this file)

<!-- plan-archive: archived 2026-10-25 -->
## T01 - all.html's opening (FR-001, FR-002)

### T01 Approach (checklist part A)

1. **The goal, in the world.** A reader of the single-page record is told first what the research is for, as on the home page.
2. **The constraints.** One opening text for both pages (Acceptance 1); the pointer to the contents kept, after it (Acceptance 2).
3. **Where each comes from.** O: `request.md`; the spec's FR-001 and FR-002; feature 424's `load_opening`.
4. **Do they describe the world here?** Yes.
5. **The order.** Code and test, the record build, then the gated landing.
6. **The exits.** None.
7. **The search smell.** None.
8. **The budget.** Minutes of code; one `make done`.
9. **Done, measured.** The record site tests green; `make record CHECK=1` clean; `make done` green at the landing.
10. **Before moving a constant.** n/a.
11. **Before fitting things into room.** n/a.

### T01 Decisions

- **D1** `_single`'s head is the title, then `load_opening`'s text, then "Every question, every note and every source on one page.
  The same record, a page per question: the contents." (italic, as now). Rendering: none.
