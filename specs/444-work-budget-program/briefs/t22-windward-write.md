<!-- page-load: kind=assertions -->
# Brief - feature 444 T22, the windward tie recorded. Session W: write

You are a FRESH session for the record edits of one task of one feature. This brief is the whole of what you need. Work in this
clone (`/diagram/.clones/diagram-backlog`). The project's CLAUDE.md files apply to you, the research record's `CLAUDE.md` above all.

**What is asked.** The round arbiter's ruling on ask:444-T22-windward (`specs/444-work-budget-program/arbiter.jsonl`): the hamlet
roll takes the high windward margin on every hamlet - a rolled fall is drawn only from the falls that leave the windward side high or
level (`rust/phases/src/water_frame.rs::admitted`, `l7r/diagram/hamletgen/plan.py::fall_backs_the_wind`) - while 0031's drawing page
says the high margin on the windward side "is one case among several; how common it was is a GUESS". Record the every-hamlet rule
on the page as a deliberate DEVIATION. One drawing page only - no finding page, no new research; the code stays as it is.

## Your item

1. 0031's drawing page (`research/questions/0031-clustered-and-scattered-villages-shuson-sanson.drawing.html`), the bullet
   "Where does a village's cluster sit?": after "how common it was is a GUESS", add that our hamlets take it on every map, a
   deviation: a hamlet's land is rolled to fall away from the wind or square across it (its high side windward or level), so its
   houses keep their back to the wind; the share the page cannot give is not rolled. Add "the windward high margin on every hamlet"
   to the page's `<!-- Evidence: ... deviation (...) -->` comment's deviation list. Keep the bullet's own wording and its notes.

## The procedure (session W: write)

1. `make research-claim Q="0031" FEATURE=444`.
2. Edit the fragment, then `make record && make citations` and the record tests; `make quick` green but for its known failures
   (the strict-xfail ports in `tests/_waiting_ports.py` pass as xfail). Commit with messages opening `444 T22: `.
3. Append to `specs/444-work-budget-program/briefs/t22-windward-handoff.md` (with `make append`) a `## Session W` section: the
   block changed (`- SECTION=0031/<id>`) and its anchor.
4. Release the claims (`STATUS=done`). Do not push. Your last message is one paragraph.
