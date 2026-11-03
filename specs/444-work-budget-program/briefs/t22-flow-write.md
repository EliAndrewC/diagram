<!-- page-load: kind=assertions -->
# Brief - feature 444 T22, a hamlet's flow recorded. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** T22's claims round (feature 444, FR-021; the round arbiter's ruling ask:444-T22-windward, which settles
`plan_site`'s flow in the same pass): a hamlet's drainage bearing is taken as its land's fall unless its spec declares one
(`l7r/diagram/hamletgen/plan.py::plan_site`, `water_flow = spec.water_flow if spec.water_flow is not None else down_deg`), while
0054's drawing page says every map declares the two "separately" and that they "differ by design". Record the hamlet's case on the
page as a deliberate DEVIATION. One drawing page only - no finding page, no new research; the code stays as it is.

## Your item

1. 0054's drawing page (`research/questions/0054-which-way-water-flows-and-how-channels-bend-and-join.drawing.html`), the bullet
   "Every map declares its land's fall and its water's bearing, separately.": add that a hamlet takes its water's bearing from its
   land's fall unless its spec declares one, a deviation - a hamlet's sheet draws one field on one slope, not a valley floor
   between two sides, and rolls no bearing of its own. Add "a hamlet's bearing taken from its fall" to the page's
   `<!-- Evidence: ... deviation (...) -->` comment's deviation list (if the page has one). Keep the bullet's own wording and notes.

## The procedure (session W: write)

1. `make research-claim Q="0054" FEATURE=444`.
2. Edit the fragment, then `make record && make citations` and the record tests; `make quick` green but for its known failures.
   Commit with messages opening `444 T22: `.
3. Append to `specs/444-work-budget-program/briefs/t22-flow-handoff.md` (with `make append`) a `## Session W` section: the block
   changed (`- SECTION=0054/<id>`) and its anchor.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
