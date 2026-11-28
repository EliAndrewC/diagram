# Feature 461: the GM's words

<!-- SOURCE: GM NOTES -->

2026-11-27, on the task time breakdown putting the second tier at 84% of blocking:

> Wait. So The entire point of the second tier was to make what happens in the second tier not block anything. Are you telling me that The overwhelming majority of our blocking was the second tier?!

2026-11-27, on the filings that had to wait for a gate:

> And I suppose that once we switch to the main session as an orchestrator, then we won't have to delay writing tasks such as this, because everything will be worktree based, right?

> Okay, to be clear, I don't think that those delays in filing are that big of a deal. I mainly ask because I worry that they are symptomatic of something that is a big deal in other interactions.

2026-11-27, opening the orchestration talk:

> Okay, thanks. And while that is all information that we will want before talking about our process reviewer, it occurs to me that we can probably start talking about the orchestration refactor now. So at a high level, what do the best practices seem to be here? Like, I don't want to completely reinvent the wheel, but I also don't think that we need to overhaul our project to use some other framework, because we have put a lot of work into making things that work for us. So there probably is a kind of best of both worlds thing that we can do, in which we take existing best practices and, heck, I mean, I would even download somebody's skill or whatever if that helped, just in the same way that we have done with SpecKit. But mostly right now I just want to understand the current state of the art, because I think that that will be better than just saying, hey, let's go start using Gastown or one of its competitors, you know?

2026-11-27, after the session's account of current practice and its best-of-both-worlds sketch:

> Okay, yeah, that seems very sensible. It sounds like we have enough to make this its own feature and begin working on it now. Does that sound right? don't actually start it yet. I just want to make sure I understand the state of things.

> Okay, yeah, go ahead and write the spec for the feature now, but don't actually get started on it just yet. I have one or two more questions about our overnight work before we do that.

<!-- END SOURCE -->

The token-cost goal this feature is held to is the GM's fifth process-reviewer message, kept verbatim in
`specs/449-rust-codebase/port-talk-gm-goal.md` ("token cost ... That's just as important as task throughput").

## The sketch the GM called "very sensible" (the session's words, 2026-11-27, not his)

The session's message he answered, its proposal section as sent:

> 1. **A landing lane of its own.** Like the Refinery, it would run as a script in its own worktree rather than in my turns: carry the done commits, run the cheap checks and the gate, and push. On a red result it bisects and ejects the failing change. The rest of the batch lands, and the ejected task returns to the queue as a repair entry.
> 2. **Builders submit only once their change is ready to land.** Before handing in, a builder rebases onto current main and runs the landing's first pass and coverage for its own crates. Conflicts and bookkeeping refusals then get fixed by the builder that has the context, in its own tree.
> 3. **I become the thin coordinator.** I'd dispatch, read short reports and talk with you. The only integration work left to me would be the rare case that needs judgment, and there a fresh agent per batch beats me doing it.

"Coverage for its own crates" in item 2 is struck by the spec (spec-fidelity, 2026-11-27): it reinstates the closing step's coverage
the GM questioned and that was reversed on 2026-11-26 (`docs/process-decisions.md`, around line 191), and the reopening condition
there is not met.

2026-11-27, on comparing measurements (his seventh process-reviewer message, kept whole in
`specs/449-rust-codebase/port-talk-gm-goal.md`; this feature's FR-010):

<!-- SOURCE: GM NOTES -->
> we don't want to do anything silly like capture performance metrics when only one builder is running, and then capture performance metrics when four builders are running, and then compare them without noting how much was happening at the time, because that sort of thing could cause us to think that things are getting better or worse when actually all that's happening is that we are looking at the system when it is implementing different numbers of tasks.
<!-- END SOURCE -->

2026-11-27, starting the feature:

<!-- SOURCE: GM NOTES -->
> Okay, good stuff, thanks. And I think you can go ahead and get started on the orchestrator feature now, because I think that's something that we are going to want to do kind of just regardless, and also orthogonal to the process reviewer, which we can also talk about separately after I look more at these figures. Thank you.
<!-- END SOURCE -->

2026-11-28, scheduler priorities as first-class support (after the session gave 462's disk work builders that 461's phase 3 could have used):

<!-- SOURCE: GM NOTES -->
> This is probably somethigng that needs first class support in the orchestrator.  Like I probably want to be able to indicate priorities like:
> -> "this feature gets all builders it needs, other things get only what is left over"
> -> "this feature always gets 1 builder so that it is able to move forward, but other features get the rest of the builders if they need them, and this feature only fills the available builders if there is no contention"
> -> "performance fixes and process-based bugfixes get priority over everything else regardless of what feature they are attached to"
>
> That kind of thing.  Basically, our scheduler probably needs some tool-based enforcement of these kinds of prioritizations so that you don't need to remember to do the correct thing in the future.
<!-- END SOURCE -->

On where it goes, after the session proposed 461:

<!-- SOURCE: GM NOTES -->
> yeahm, I agree this should be part of the existing orchestration feature.
<!-- END SOURCE -->

2026-11-28, after the lane's gate sat on a hung test for 4 h 51 min (290.5 minutes, measured 2026-11-28, method: batch 461-4's `run` line in `l7r-lane/lane.jsonl`, 06:42:52Z to 11:33:17Z) with nothing woken (batch 461-4):

<!-- SOURCE: GM NOTES -->
> How's it going?  things look like they've been idle since 3am
<!-- END SOURCE -->

On the session's account of the stall and its filing of T107:

<!-- SOURCE: GM NOTES -->
> Okay, sounds like our tooling needs a fix for that!
<!-- END SOURCE -->
