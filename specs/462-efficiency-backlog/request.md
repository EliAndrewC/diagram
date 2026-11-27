# Feature 462: the GM's words

<!-- SOURCE: GM NOTES -->
2026-11-27, asking:

> Speaking of our long-running feature that we've been working, which is now at more than 500 tasks, making it by far our largest ever, then I wonder whether, in light of our new orchestration feature and then the process reviewer feature that we will eventually start, whether it makes sense to continue with the tasks which we are currently working, which we have identified as being things we want to do immediately because they are high impact bugs that like affect things in the short run, and then whether it makes sense to move the rest into a new feature and then actually close out this feature, because I don't think that keeping it open for hundreds of additional tasks or whatever is going to be the right thing after we add those other things.

2026-11-27, the go:

> In the meantime, it seems like you have a good amount of work to do with both the tasks that you are closing out and moving everything new feature, afterwards, and then doing the split that we discussed which is all on top of the orchestrator feature that you are working in parallel to that, so I'm going to try to keep an eye on what you're doing for the next few hours, but I will probably be preparing for a dinner and then doing work in the kitchen and such, so let me know if you need anything. But I will probably leave you to it for a while, if you agree that this is a good time to do that. And that you don't need anything else from me beforehand.
<!-- END SOURCE -->

2026-11-27, on the split (the message "the split that we discussed" refers to):

<!-- SOURCE: GM NOTES -->
> So I wonder if we should preemptively do some things like mechanically split up the large files into smaller files that exist in notes explaining what we did and why, and cautioning future sessions that look here to be careful to avoid like wrecking their context usage, because even doing something like grepping for what you need could turn up just so much context that I actually wonder if this might be a key part of why so many of our builders were hitting their 300 K token context window size, you know?
<!-- END SOURCE -->

## The session's proposal he answered with his go (the session's words, 2026-11-27, not his)

> Finish the "now" set in 451. I'm counting as "now": T526, which is in flight; 461's own tasks; the ready short-run fixes T513, T514, T517, T519, T523, T527 to T529, T531 and T532. T308 is listed in the queue as in flight, but 461 has taken it over (T16 closes it), so it isn't 451's now. Everything else in 451's queue, including T321, T307, T300 and T302's remaining parts, goes to the new feature. ... Move the rest. Tasks that belong to 461 go there, and the remaining deferred work goes into a new placeholder feature. The process-reviewer feature doesn't exist yet, so nothing moves to it now. ... Close 451 with its feature report, once the "now" set lands. Measure the large-file readers, before and after.

(T526 and T517 of that list have landed. The spec sends T307 to 461, not here: 461's accepted spec takes it over.)
