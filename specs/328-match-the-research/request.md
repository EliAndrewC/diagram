# Request (GM, 2026-10-07, verbatim)

The GM typed this with the `/goal` command; typos are left as written, and the one that changes the reading is corrected in
square brackets ("the go" is then go).

The GM wrote:

`make claims-report` shows all of the places where our implementation doesn't match our research.  I'd like a "fix all of it" feature.  I'm not sure there's any reason for our implementation to not match for anything.  However, some fixes will be harder than oghers, so I'd love to start with the low hanging fruit, i.e. rank all of the findings by how mych implementation work we expect it to be to make the implemnentation match the refenced research, the[n] go from easiest to hardest.  So when you make the feature, the frist step will be doing this audit to rank the claims which don't match the research, then you'll begin moving through the tasks to fix them.  Keep going until you hit 75% of the weekly window, then let whatever subagents are currently running complete then stop working.

Context the GM set in the same session, before the request (summarized, not the GM's words): the session built a per-goal
usage cap (`~/.claude/hooks/usage_cap.py`, armed for this goal at 75%); the GM: *"in this case I want it to be a 75% stop on
a particular goal, but not in general."*

---

The GM, 2026-10-07 (amendment 8), verbatim:

> Also it occurs to me that we should probably differentiate between our scripted settlements and the manual ones.  Like, maybe this feature should fix 100% of findings in hamlets but punt on villages and towns and cities.  It should also include magistracies and country shrines since those are permanently manual, but the legacy unscripted settlements are probably not worth the effort to edit.or even fix their automated checks at this time, since those automated checks will eventually go away anyway.  IU hadn't thought about that when asking for this feature, but how would that change the feature's scope?

> Your proposal sounds good.  Please also raise the cap from 75% to 85%

> Thanks.  Please go with the order you've described: finish your current round of in-progress stuff, the edit the feature to limit ourselves to code actually executed by magistracies, country shrines, and scripted hamlets; legacy hand-drawn settlements shall have their findings marked as DEFERRED rather than DRIFTED.  I pre-authorize you to exceed the normal limit on rounds of spec reviews if necessary, so you don't need to ask whether to continue past the usual number - you should do so if needed.  Keep going until the feature is complete or until you hit 85% usage (if you hit 85% usage then let whatever is running finish running even if it drives up usage a few more percenage points and then stop - I believe this is how the cap works, which is what we want).

## The GM, 2026-10-07 (amending the goal, verbatim)

I'm amending the goal to note that I'm leaving for work, so please don't stop working until you hit the cap or the feature is done.  If you need to ask me a question then please defer it to the end of the feature so that I don't come back to find you've been blocking on a question not doing any work for the past 7 hours, etc.
