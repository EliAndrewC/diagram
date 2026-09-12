# The GM's request, verbatim

2026-09-12, session "Diagram (Kuwabata)", after feature 228 landed and the session had broken down its 32 minutes (18.7 of them waiting on a settlement-review of a delta whose manifest was byte-identical; a pair-guard refusal caused by the guard reading the mirror's state; a pool snapshot the session was supposed to take by hand; a pixel-check script written twice):

> Can you explain what recon and clone setup is and why it took one point seven minutes? That seems like a lot of time to set up a clone. Either way, it does look like we have three tooling fixes that we can make. A tooling fix. that makes the first paraguard issue either impossible or be automatically fixed in the way that I think some of our other tools do. Like, I know that if we try to change directory into the main checkout, then I think a tool just kind of automatically diverts us into the correct clone. So we could probably do something like that. And if we are supposed to snapshot the pool before I make verify, then it should not be on you to remember to do that. That should just happen automatically if that is something that is important for the process. And, yeah, it sounds like there's no reason to need to write a scratch script to do pixel checks every single time. like, we should think about what that reviewer pass is actually doing and what tools it needs, and then give it those tools so that the process is more streamlined. I think that doing a reviewer pass is worthwhile, but if it's taking nearly twenty minutes, But that means that something has gone wrong for a feature like this. And, actually, now that I think about it, why did we do a settlement review in the first place? I mean, for this specific feature. we did not actually change anything about the engine or how the settlement is laid out. We purely made a change to the highlighting behavior on one of the maps. That should not trigger a settlement review in the first place. So while it is good for us to fix the tooling and improve the settlement review process for those features where it does matter, it sounds like we also need some better guidelines around when a settlement review should even happen. like, if there are no changes to the actual way that the settlement is laid out, then we should not need to re review the settlement because we're just rereviewing things that have not changed. Right? So I guess that probably means that the first step in the settlement review process or even the thing that determines whether a settlement review is necessary is probably some kind of scripted check, probably part of the make verify or some other command. that tells us whether or not there were any changes that should even trigger a review of the settlement.

---

## The amendment (GM 2026-09-12, after feature 231 landed)

The session reported that the resolver leaves one residual: when this session's clone cannot be resolved
(an unnamed session, or a clone claimed but never created) the guard still falls back to the shell's own
directory, so a session standing in the mirror could get the old misreading again. Offered a fix - the
guard notices it fell back onto main's tree and says so in one line rather than judging silently - the GM:

> Yeah. Go ahead and do that. Thanks.

