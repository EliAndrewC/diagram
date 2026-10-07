# Request (GM, 2026-10-07, verbatim)

The GM typed this with the `/goal` command; typos are left as written, and the one that changes the reading is corrected in
square brackets ("the go" is then go).

The GM wrote:

`make claims-report` shows all of the places where our implementation doesn't match our research.  I'd like a "fix all of it" feature.  I'm not sure there's any reason for our implementation to not match for anything.  However, some fixes will be harder than oghers, so I'd love to start with the low hanging fruit, i.e. rank all of the findings by how mych implementation work we expect it to be to make the implemnentation match the refenced research, the[n] go from easiest to hardest.  So when you make the feature, the frist step will be doing this audit to rank the claims which don't match the research, then you'll begin moving through the tasks to fix them.  Keep going until you hit 75% of the weekly window, then let whatever subagents are currently running complete then stop working.

Context the GM set in the same session, before the request (summarized, not the GM's words): the session built a per-goal
usage cap (`~/.claude/hooks/usage_cap.py`, armed for this goal at 75%); the GM: *"in this case I want it to be a 75% stop on
a particular goal, but not in general."*
