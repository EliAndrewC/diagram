# The GM's request, verbatim

This feature was IDENTIFIED by the `diagram-testing` session (during feature 166's acceptance) and is
being HANDED OFF to the `Diagram tooling` session to implement, at the GM's direction. The two messages
below are the GM's own words, quoted in full and unedited.

## 1. The question that started it (2026-08-30)

A different Claude Code session had reported to the GM:

> ```
>   3. And one I want to put in front of you properly, because it's the biggest number on the page:
>
>   green `make done`, median by day
>     2026-08-26    44s
>     2026-08-27    35s
>     2026-08-28    68s
>     2026-08-29   111s
>     2026-08-30   148s
>
>   The gate has got 4x slower in three days and nobody knows why. Part of 35->68 is the scope unlock on 08-27, which was deliberate. The rest
>   isn't accounted for. I noticed this on the first day of the session, recorded it in 162/research.md R5 as out of scope, and never came back
>   to it.
> ```

The GM's own question:

> This sounds bad. In fact, I could have sworn that we had some code in place that detected when we had
> our unit tests start to take longer relative to some previous baseline so that if we ever had this kind
> of increase, then we would notice it. So how did this happen? Am I just misremembering that? Does that
> apply to some tests, but not the make done tests? like is that just the quick tests only or something?
> Before we look into the length of the make done tests, I would like to separately take a look at how
> this was able to happen. so that we can prevent this from happening in the future without anyone
> noticing.

## 2. The instruction, after that investigation was reported back (2026-08-30)

> Yes. Please open that feature. And it sounds as if we want to adjust our upper limits as well. For
> example, since make quick is currently at eleven seconds, then I think if it takes even as much as
> fifteen seconds than I would like for that to result in a failure, which should require us to stop and
> see what has happened and whether the quick tests need further efficiency improvements, etcetera. And
> then it sounds as if we need something similar for our make done tests where I would argue that if they
> were down to thirty five seconds, then if they take forty five seconds to run, then that should cause a
> failure, and we should stop and see what has happened, which has caused the tests to take longer,
> etcetera. I know that we have longer tests as well where we will eventually want something like this so
> it would be good if we implemented that general pattern there, but I am not interested in running the
> lengthy tests at this time, especially given that they run on AWS, and we are currently trying to limit
> ourselves and not run on AWS at this time until we get our baseline Hamlet generation absolutely rock
> solid, both in terms of correctness and efficiency. So the first thing we should do is create a feature
> for this work. However, I would like for that feature to then be handed off to the "Diagram tooling"
> session, which is the session which is handling this exact kind of tooling. rather than having you
> actually do the work yourself because we are the ones who have identified the problem. I think it makes
> sense for us to document it and capture whatever context is needed in a spec kit feature. But then we
> want the other Claude code session, which is already handling tooling to handle this once we are done.
> That session is already in the middle of a task, so we can send them a message to let them know about
> the feature once that feature has landed in the main checkout so that it will know that it can tackle
> that next. Once it is finished, it's current feature. And then after you have done this, we will talk
> more about what I want you to do with respect to test efficiency and actually getting those run times
> down.

## What the GM did NOT ask for

Recorded because a handoff is where scope grows silently:

- **Not** the investigation of WHY `make done` went from 35 s to 135 s. The GM was explicit that this is
  separate and comes after: *"before we look into the length of the make done tests"* and *"after you
  have done this, we will talk more about ... actually getting those run times down"*.
- **Not** arming anything for the FULL / AWS scope now. The pattern should be general enough to extend
  there later, and that is all: *"I am not interested in running the lengthy tests at this time"*.
- **Not** any change to what the tests DO. This feature is detection only.
