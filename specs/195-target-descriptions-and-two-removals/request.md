# The GM's request, verbatim

2026-09-06, reading the generated make-target reference:

> What are these actually used for and should we keep them?
> make cache-audit - does using the generation cache change any map?
> make citybudget ARGS - the city/capital space-budget planner
> make cohort N - roll N seeds and report every failure
>
> also, what does `make compound` actually do?  Compounds like magistracies are hand-drawn, so what
> is the make target actually doing?  It would be helpful if the description clarified that.
>
> Do we need `make hamlet-floor`?  It looks unnecessary at a glance, and I thought we decided to get
> rid of pack-audit but I stil see it at file:///home/eli/l7r/diagram/docs/make-targets.html
>
> Also, when a command has arguments, I want to know what each argument does, whereas this:
> ```
> make durations    FULL MARK    where the suite's time goes - run when a target feels slow
> ```
> does not tell me what the difference is between `make duration` and `make duration FULL=1` and
> `make duration MARK=1` (if that is even what I am meant to pass to `MARK` - I'm not sure).

Then, on the answers:

> Go ahead and delete `make citybudget` since we're not using it and won't for some time and might
> use a different shape of tool by the time we get to that point.
>
> Go ahead and remove `make hamlet-floor` since we already use it on `test-full`.  And yeah, good
> call on `pack-audit` but please update the description to note it is specifically used for
> hand-drawn maps.

## Readings recorded, because two of these are narrower than they look

- **`make citybudget`**: the GM named the TARGET. The MODULE `l7r/diagram/citybudget.py` is imported
  at module level by three frozen city exhibits (`tango`, `minami`, `nagahara`) and by
  `wip/shiro_daika/frame.py` - **1,732 lines of in-progress capital work last touched 2026-08-31**,
  which is exactly the "when we get to that point" the GM names. So the target, its CLI and its
  registry row go; the module stays as a library. The GM was told this and can order the module gone
  as a follow-up; deleting it silently would break the work their own sentence anticipates resuming.
- **`make hamlet-floor`**: the target only. `test-full` invokes `l7r.diagram.tools.hamlet_floor`
  directly as a gate phase (`Makefile`), which is the GM's own reason - *"we already use it on
  `test-full`"*. The module is load-bearing and stays.
- **`pack-audit`** is KEPT (GM 2026-09-06, and their 2026-08-30 ruling); only its DESCRIPTION changes
  to say it is for hand-drawn Mode A maps. The GM's *"I thought we decided to get rid of pack-audit"*
  was answered before this instruction: it was kept on their own earlier words.

## The GM ratifies the narrowing (2026-09-06)

Asked whether the `citybudget` MODULE should go too, given that `wip/shiro_daika/` (1,732 lines of
in-progress capital work) imports it:

> Leaving the module is fine as long as the make target for citybudget is gone, thanks.

So D2 is not a session-chosen narrowing any more - it is the GM's own decision on a stated
consequence. The same shape applies to `hamlet-floor` by their earlier reason (*"we already use it on
`test-full`"*), which is about the module being live rather than about future work.
