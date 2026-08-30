# The GM's request, verbatim

Captured BEFORE this feature's `spec.md` is written (constitution XVI). Nothing here is edited.
This feature is the SECOND half of the question feature 141 opened - 141 asked *which* checks still
earn their keep and cut the battery by a third; this one asks whether the post-placement check
battery should exist as an architecture at all.

## 2026-08-30, opening the feature

> I'd like to talk about the "automated checks" which run after our placement algorithm as part of our map generation are actually doing for us.
>
> Specifically, let's talk about what the automated checks are actually doing for us. It sounds like what we are doing is that we have placement algorithms, which in theory should not be buggy, but then the automated checks essentially catch bugs as they slip through and then fix them on the maps. I've been thinking about this, and I think that that's probably just not how we want to do this. Because what that ends up doing is taking code that should be a unit test and then making it happen every time a map is generated instead of having it happen when a thing is placed. Now with that being said, I could imagine a world in which some of what we are doing with our placement algorithm is running checker functions to see where a thing can be placed. and those checker functions might essentially be some form of our automated checks in that they might tell us where something is capable of being placed on the map. That all seems fine. But if we have a placement algorithm, which our automated checks are catching an issue with, then I think that just means that our placement algorithm is bugged. Right? This was not true at an earlier stage of this project when the maps were essentially hand generated and then our automated checks told us whether we had placed things by hand correctly. But now that we are doing things in a scripted way, we basically have a placement algorithm and then automated checks and then also unit tests. And I think that the automated checks just fundamentally from an architectural perspective do not need to exist. Now that is not to say that the correct thing to do right here, right now in this moment is to simply delete all of them. That might be true because if there are no known bugs or if our automated checks are not catching anything in this exact moment, then we can delete any automated check that does not catch anything. However, if there are automated checks which currently serve as a load bearing part of our map generation, then that means we cannot simply delete them. Instead, we need to update our placement algorithm such that those automated checks no longer fire. That could mean integrating something about the automated check into the placement algorithm itself. That could mean fixing whatever bug in our placement algorithm is causing the automated check to sometimes fire. That would probably depend on a case by case basis. What do you think about this rearchitecture that I am proposing? Does this make sense to you conceptually? If so then open a feature for this, the first task of which will be to run through the automated checks to see which ones do not appear to ever actually fire with our current implementation and then delete them and any tests associated with them.  After that we can look at the automated checks which are firing and decide on a case by case basis which of them represent bugs in our placement algorithm and which need to be folded into a trial-and-error version of our placement algorithm, which is a discussion we should stop and have before any changes like that are made.

## 2026-08-30, the GM's ruling after the census (escalation resolved, and the deletion criterion set)

Asked what was waiting on them, the session put two questions: (1) whether the feature proceeds despite
constitution XVI's three-round escalation, and (2) whether `FIRES-HAND-ONLY` - a check proven only by a
hand-typed test manifest, 103 of the 152 - should count as firing "with our current implementation".

The session's recommendation on (2), which the ruling accepts:

> **My recommendation: don't use it as a deletion criterion at all.** Here's why. "Has anything made this
> fail lately" was a good test for finding *dead* code, and it did its job - it found 5 genuinely dead
> things. But for the other 103 it's the wrong question. The right question is the one you already asked in
> feature 141: *can any stage after the placer change what this check reads?* If no, it's re-measuring
> something the placer guaranteed and it should become a unit test of the placer. If yes, it's checking a
> real emergent property and it stays. That's your architecture, and it doesn't care whether a check
> happened to fail recently.
>
> So concretely, what I'd do: delete the 5 dead ones (2 phantom names that can't be emitted at any scale, 3
> that only run on tiers no generator can produce), then go straight into the case-by-case pass over the
> rest - which is the discussion you said you wanted to have anyway.

The GM's answer, verbatim and in full:

> go

Which covers both questions: the feature proceeds, and `FIRES-HAND-ONLY` is NOT a deletion criterion.
