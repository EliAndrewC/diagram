# Request - 248 reviews one per map

The GM, 2026-09-14, verbatim, in the conversation that followed feature 247's time breakdown (36 minutes,
11 of them one settlement-review agent serialized over four maps).

First, on the breakdown:

> When you say "the push was refused once for untouched notes files, 1.5 min" then is that something that could happen much faster than 1.5 minutes?  I mean, that sounds like a simple check which could gate the lengthier checks, right?
>
> Parallelizing the settlement review does indeed also sound good, though can we talk about what the settlement review is actually checking for?  Because I thought we had some diff tools to look at the before and after, so I wouldn't have expected this to be 11 minutes.  For that matter... do we have an audit trail on what if anything the settlement review has caught in the last week or so?  I want to make sure it's worth the effort in general, and also think about whether we can skip it for features like this one specifically, i.e. changing a glyph rendering convention rather than tweaking actual map features to comport to historical norms, or whatever.

The session answered: the push-time checks all run in under a second and the 1.5 minutes were the session's own turns, so the fix is removing the redundancy (the reviewer's verdict record and a hand-written notes entry record the same pass); the ledger shows the review catching defects on every layout feature of the week and nothing on the map for any rendering or performance feature; a waiver keyed on the task classification already required; and one agent per map in parallel. Then:

> Yes to both, thanks.  And also the parallelization of review agents when we DO run them is good too, so we sho0uld gold that in as well.  Because when you say "That is my mistake, not the tooling's." then that is wrong - the point of the tooling is to make the correct thing happen automatically without you or I needing to remember the precise ways to not get it subtly wrong in a costly way.  So whatever the tooling is currently doing to kick off reviews should be modified to make the correct thing happen automatically... somehow.  Before you start on the new feature, tell me how this might be accomplished or whether subagent checks can even guarantee this kind of property in a mechanical, scripted, manner verified and enforced by hooks or other configuration.

The session described three pieces (one map per dispatch refused at PreToolUse; every owed map dispatched before the turn ends, at Stop; parallelism measured after the fact, not forced) and what a hook can and cannot guarantee. Then:

> But could we refuse a map review before it happens if the review asks for a review of more than 1 map?

The session: yes, that is the PreToolUse piece, with no escape token; and asked whether to claim the feature with all four parts (the multi-map refusal, the every-map-dispatched Stop rule, the rendering-classification waiver, the verdict record replacing the notes-file touch). Then:

> Yes please - if I understand you correctly, that is all of the recommendations you have made, which is indeed what I want.  IF those 4 things left anything out that I've said I want then please include it as well, thanks.
