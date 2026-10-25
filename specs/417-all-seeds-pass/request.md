# Feature 417 - the GM's request, verbatim (2026-10-24)

The session had reported feature 405 T106: two hours, a knot fix landed (T138), the seat turn set down because every
change to it broke other cohort seeds.

> So it sounds like it took 2 hours to fix some seeds at the cost of other seeds breaking?
>
> I think what I'm gathering from this is that we might want to put our claims work on hold and then open a new feature whose goal is "all seeds passing".  Because before we start making adjustments to how things work, we need a solid baseline where everything already there functions as expected.
>
> And the fact that making some seeds pass just ends up breaking other seeds leads me to believe our algorithms are brittle.  In general, the thing we're doing has a ton of details, but isn't fundamentally complicated, so we should probably think about how to get things passing consistently.  And then we can make "all seeds pass" a hard requirement for later features, including when we resume feature 405.  What do you think?

The session measured fresh seeds failing at 14% and proposed the feature, the lane web first.

> Okay, and it sounds like we probably also need a general rule that "place then check" is not something we want **anywhere** in the codebase?  What do you think about that?  I thought we had gotten rid of that as an approach for doing things, but it sounds like it's causing brittleness in other places too.  Where else is this part of our algorithm?

The session proposed the rule (a rule asked of a candidate before it is placed; nothing placed and repaired after; a
finished-map check a backstop only; no candidate admitted -> more room) and an inventory as task 1.

> If the check on the finished map never fires, then do we even need the check on the finished map?  That's extra code to maintain, extra tests, and extra tokens, etc.  Should we just get rid of it as part of this new feature we're scoping?

The session answered: keep one finished-map check per rule, in the cohort and the tests only, calling the placer's own
predicate (it is the measurement, and it sees a later stage breaking what an earlier one placed); delete the repair passes,
any rule coded twice, and the checks the generator runs mid-map. "Shall I file the feature with this scope?"

> Yes please

After filing, the session asked whether to fold open feature 394 (seed regressions refuse a landing; its request is
`specs/394-seed-regressions-refuse-a-landing/request.md`) into 417, and whether to start the plan:

> Yes fold 394 into 417 then start on 417, thanks.
