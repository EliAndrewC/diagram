# Feature 405 - the request, verbatim

The GM, 2026-10-19, routing 385's open work:

> Let's keep the current round of process tasks such that all open process tasks stay in 385 and everything else moves into a new feature.  Then we can finish and land our process tasks and then start the new feature after that ends up in main.

> But don't you start the new feature, just file it.

The GM, 2026-10-19, on 385, the rule for found work that this feature carries with the tasks it governed:

> Yes we should keep findings on code a task didn't change as new tasks in 385.

The GM, 2026-10-20, starting it:

> Done.  Now I think it would be good to test the current state of things by starting feature 405 and fixing 1 claim.  We'll then see how long that takes, how well it goes, how the time breaks down, etc.  This seems like a good way to evaluate the current state of our proceses and tooling.  When we're done we can look at the numbers and take stock of what to do next.

## Amendment 1 (2026-10-20) - the landing

The GM, after T12's numbers:

> No, I do not want each landing to owe a lands open line at the top of the spec, because that's going to slow things down. As you say, that took 3 minutes. It sounds like the landing being the biggest cost is something that we need to do something about. I'm not especially concerned with the spec review portion, because as you say, that's, you know, something that we do at the beginning of a feature, and that won't be the case for other tasks, but 5 minutes is an acceptable amount of time for actually implementing the task. So that's a really good sign, I think. So it sounds like you already have some idea what to do here, but why don't you do an in-depth analysis of what you think would have been a good process that would have done what we wanted in kind of a reasonable amount of time, and what else is needed to make that happen, then create tasks for those changes that will be the very next tasks that we do here in this feature, and then go ahead and work those tooling and process changes. Let me know when you're done so that we can decide whether or not to repeat this experiment by performing another claims task. Thanks.

## Amendment 2 (2026-10-21) - the second claim's fixes

The GM, after T14's numbers (`landing-analysis-2.md`, proposals A-G):

> Let's implement A, B, C, D, F, and E.  Go ahead and implement all of those.  when you're done we'll decide whether to proceed with impementing 1 more claims task.

## Amendment 3 (2026-10-21) - the third claim

The GM, while T36-T41 were being built:

> When you've landed these performance / process improvements, please work 1 more claims task and then measure the results.  I'm going to bed and will check in when I wake up to see how it went and whether our fixes now take the amount of time they "should" take.

## Amendment 4 (2026-10-21) - the hourly step-back suspended, the red-gate hold fixed, a fourth claim

The GM, after T11's numbers (`landing-analysis-3.md`):

> Sounds good, let's suspend but not remove the hourly step-back arbitur for now.  Then let's fix the "second red gate" tripwire so that it fires properly when it should fire.  Then you can do 1 more claims task and measure how long it takes.

## Amendment 5 (2026-10-21) - the gate and the landing cohort in parallel, a fifth claim

The GM, after T19's numbers (`landing-analysis-4.md`) and what `make done` and the landing cohort each run:

> Add the "worth a look" thing to our task list, but not as a high priority.  Then make the make done and the make landing run in parallel.  Then do 1 more claims task and measure how long it takes.

## Amendment 6 (2026-10-21) - the claims round beside the landing, one push, and T47

The GM, after T13's numbers (`landing-analysis-5.md`: the claims round in series before `make land`, 1.5 min; the landing's two
pushes, ~1 min):

> Yeah, let's do both of those remaining time issues, and then we might as well do T47 while we're at it.

## Amendment 7 (2026-10-21) - split at the file bar; the feature taken to completion

The GM, leaving for the day after T49's numbers (`landing-analysis-6.md`):

> Okay, well, I'm about to leave for work. So I think I would like for you to actually just try to take this feature to completion, or at least as close to completion as it is possible to take it. I hope that you do not need research rulings from me, since I would generally hope that you would be able to figure out the correct thing to do based on our project guidelines. In particular, there have been a bunch of times where the research rulings you have asked for from me in past features have been questions along the lines of whether we should follow the research, when in fact that is generally what we should do. I mean, I understand that there are sometimes difficult questions, so I don't want to tell you to never ask me for guidance, because it is certainly much better to ask than to do like dozens of hours of work on a false trail. But I think that for things like this, like claim feed tasks, then I think that the likelihood is that you will be able to figure this out for yourself. But I don't know. Use your best judgment when the time comes. Anyway, before you do any of that, I want you to file a new task as the very next one you do, which has to do with what happens when we reach 1,000 lines, which is our limit. It sounds like what's happening is that we're spending a considerable amount of effort getting things down to exactly 1,000 lines, and I think that that is going to cause problems in the long run. So I think that what we should do as a general guideline is that anytime we exceed 1,000 lines in a file, because that fails, then we should have the automated check that fails instruct us to split the file into multiple submodules where no submodule should ideally be longer than about 2/3 the size of the limit. So, you know, around 650 lines or so. Now that second thing doesn't need to be a hard limit because it's still well under our 1,000 line limit, but the idea is that if we do a refactor that brings us to just barely under 1,000 lines, then what we're really doing is setting ourselves up for having to constantly go back and do iterative tweaks, which are time consuming and eat tokens and inefficient. So really, even though the limit is 1,000 lines, we should not attempt to bring ourselves to just below that limit. When we hit it, we should take that as a sign that we need to do a refactor by pulling the module out into submodules, which should be a relatively easy thing to do, because anything that is importing from that module should be able to have imports that do not change. You know, like if we have a module called landing.py and we change it into a landing/ module whose __init__.py exposes everything which had previously been imported directly from the single file then nothing which uses that module needs to change, which makes the refactor relatively painless. Sound good? If so, then please proceed with adding that task to the feature, working that task, and then working all of the remaining open tasks in the feature. And then I will check on things when I get home. Thanks.

## Amendment 8 (2026-10-21) - the room route made obvious; T107 by room first, within the research

The GM, after the session set T26 down "for the GM to see T107 first":

> I don't understand why you're saying that I need to see this one before the batch starts when we've repeatedly said that adding more space between farms is fine as long as it's in line with our research, which in this case it is, right?

> Okay, so before we actually do that, I want to figure out how this happened, because we moved to a checklist-based approach for evaluating this kind of thing, and I thought that specifically one or more of those checklist items had to do with this exact thing. Like, basically, don't try to solve the bin packing problem. Don't throw up your hands and say that we have to do something really, really difficult because we couldn't possibly just increase space between the farms. [...] I don't want to just say always increase space between the farmhouses anytime something goes wrong, because then we will end up with farmhouses that are like a mile apart from each other, and that is not realistic. But at the same time, I thought that we were specifically calling this out as a thing that is okay to do, so long as the distances are in line with our historical research. But then it's still not happening, so I'm just trying to reason out what might work here.

After the session's proposal (1: `make set-down` refused while a part B has no arbiter ruling; 2: part B charged to every task in flight; 3: a room table with research ceilings, after a spacing research pass):

> Yes, I agree with that. So please build 1 and 2 as tooling with tests. Now, then run the spacing research pass for 3, then do that task by widening the spacing within that bound as you suggest. Thank you.

## Amendment 9 (2026-10-22) - the claim-label lint; the feature taken to completion again

The GM, after five claims tasks whose time went to label rounds, on the session's proposal ("a lint at `make claims-owed` that flags a GUESS naming a page that doesn't hold the figure, and a GUESS whose text says it is 'stricter than the page'"):

> Yes please file that fix for the lint as the next item in 405.  Then I think we should take another run at closing out this feature.  Im leaving for work soon, and it would be awesome to have the whole thing done when I get home.

> Let's also raise our soft cap to 80%
