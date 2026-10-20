# Feature 406 - the request, verbatim

The GM, 2026-10-19 (after the session reported that `make fix-yield` read 22 of 45 tooling fixes as "saves nothing"):

> What do you think about those tooling fixes which apparently read as saving nothing? it sounds like it's a weak assertion at best, though it may well turn out to be accurate in some cases. How much effort would it be to evaluate how much each of those tools are actually doing for us? Because, I mean, I don't think that I can just, like, look at them and figure it out by, like, reading the source code of the tool or whatever. Whether or not it's doing something for us should be a measurable question, right? And in cases where a tool is too new to have gathered measurements, then that's fine, but there should at least be a way that it is notionally possible for us to see how often a tool is used, right? Or how often it makes a difference, etc.

> I mean, you mentioned the fixed-to-signal mapping for these 45, but, like, in general, isn't this something that we want basically for every tool? Not just the ones that we've added recently that we're a little less sure about?

> Yes, go ahead and do this as a process feature. So go ahead and file it and then fully implement it. And let me know when it is landed on main. Thanks.

The session's proposal those last words approve, verbatim (its reply to the second message):

> 1. **One report, `make tool-yield`,** covering every tool by kind. For each: uses per week, interventions, likely misfires, and the date of first use. A tool with too little history says "too new", as you said. Most of this reads logs that exist today.
> 2. **A small usage-log helper** for the automatic steps that leave no trace, wired in wherever such a step lives.
> 3. **A rule enforced by tooling,** like "every guard has a test": a new guard, target or check is refused unless it names its usage signal. Then the answer exists from the day a tool lands, and nobody has to remember to add it.
> 4. **The 22 "saves nothing" fixes judged on the new report,** as its first use. `fix-yield` becomes one view of it.
