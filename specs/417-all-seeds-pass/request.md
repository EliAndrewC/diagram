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

Mid-feature, 2026-10-25, while T03's inventory was coming in:

> Okay, I'm heading to bed, and I think that rather than having you churn all night on the feature, I want you to do the parts of it up until the point where you, try to actually fix everything. So, definitely finish out doing the tasks that involve, turning off automated checks, and then replacing them with just having the algorithm place correctly in the first place. Etc. Do all of that stuff, and then stop so we can slowly and deliberately go through the actual fixing where we get more seeds to pass, etc.

The next morning, 2026-10-25, answering the session's report (dictated; "prionciple" = principle, "onthe" = on the):

> Changing behavior is fine as long as it is in line with our research, so T19 should be worked now before we start on the seed fixes, in the manner you suggest as the next step.  You can also close T24 if it is moot.  It sounds like T16 could use a research pass; this might not even be a research pass on premodern societies per se (since I doubt we will find sources for this - though it would be great if we could), but rather a general research pass onthe angles at which footpaths and lanes and country roads tend to intersect.  We basically want something that doesn't look wrong, visually, to a person looking at the map.  I also approve the new prionciple for the constitution.

Later on 2026-10-25, answering the session's report (dictated; "20%", "15%" and "25%" are degrees, "Tory arches" = torii, "the current of the research" = drifted from the research, "onthe" = on the):

> I accept your recommendation of 20% as the correct angle for the double-tailed rule, but I think we should be careful to document this as an approximation, because if it turns out that allowing a 15% angle instead of a 20% one made our placements much, much easier or fixed a lot of problems for us, then I want to be able to do that. You know? and then similarly, if we later do a sweep and find that in practice everything works if we make it a 25% minimum angle, then that's fine. Maybe we'll end up raising it because we think that that makes the maps look better. Basically, I feel like we need to avoid falling into the trap where we set a number arbitrarily and then end up going through enormous iterations and difficulty to try to make that number work when the number is arbitrary and not an actual hard requirement. So if we leave a comment kind of explaining or even linking to the research that showed that there were no findings on this and that we kind of just picked this and that it can change if needed, then that's fine. We can document that and then aim for that 20% as a goal and then just proceed on that basis. But it's important that in our checklist-based iteration, as we try to fix things, that we have these kinds of numbers marked.
>
> With this in mind, I actually wonder if this is worth another claims category, where I think right now we have a way to mark when a piece of implementation is based on our research. I believe we also have a way to mark when something is a recorded intentional deviation from the research, such as the number of Tory arches in front of a country shrine. And I believe that we also have a way to mark that we have realized that the current of the research and needs to be fixed at some point. And finally, I believe that we have currently a way to mark when something is unsubstantiated by research. Now that is all good, but that last category feels like it needs to be split in two, because there is a difference between something that we have not done a research pass on versus something that we have done a research pass on and have found no conclusive evidence about, and therefore we picked something arbitrary. Now, it's possible that I've misunderstood the current classification, and that given the amount of research that we have already done, it might be that everything that is currently unsubstantiated just is in that category. In which case, that's fine, and we don't need a split. On the other hand, if there are things that we have realized we have not even attempted to track down, then those should be marked differently from the things that we made a real attempt to find a historical basis for and could not do so. Certainly, this question of lane angles is in the second category.
>
> Building on this, I wonder if, before we try to actually fix all of the failing seeds, it's even worth doing an audit of the code to find all of the places where we have this kind of number. Now, I realize this might end up overlapping a little with our claims work in cases where we have not done the research pass. But that's where I think that previous audit will be helpful.
>
> Now, as for your question about the dispersed Hamlet's track, it sounds like you're asking me to make a judgment call about something that our arbiter and reviewers and such are supposed to decide based on the research. So I think the correct thing for me to do here is to decline to answer, because this is not the sort of question that I am qualified to respond to. This is not a question about my preferences regarding this project. You're basically asking me whether our research findings apply to a certain type of map, and my answer is that that is the kind of question that our processes are supposed to answer.
>
> The same thing applies to your question on T27. Our project guidelines should have everything that you need to adjudicate that question. if our research findings do not indicate that things were any particular way, then we can either make it a tunable knob, or we can just do whatever is algorithmically easier. If this is not covered by our project guidelines, then we should update the project guidelines to direct you in this way. I suspect that this is covered by the guidelines, but the fact that these two questions for me slipped through indicates that perhaps our checklist-based processes discerning what things get raised to my attention for my own personal judgment calls need tweaking. The other two questions that you asked me are good. But these two are exactly the kind of thing that should not come to my attention for an answer in this way.
>
> So I would like for you to do all of that. And then yes, I will want you to switch off the 16 repair steps as you did for the lane web. I don't care whether you do it one at a time or all at once. That is an implementation detail where you can pick whichever one you believe will be the most efficient way forward and allow you to get rid of all of them. As per the requirements of this feature.
>
> So please proceed with all of this that I have outlined. The audit of the code for these constants, the documentation of which constants are arbitrary so that future implementation passes know that they can tweak them, which should become part of our checklist-based approach to implementing these kinds of tasks, Any further research that you need to do in order to clarify any of the specific numbers, so that if we have numbers which are currently marked as being unsubstantiated, then we should first check our downloaded research to see whether that means that they are things that we have looked into but not been able to find, or if they are things that we simply have not looked into one way or the other, then please actually perform research for any of those questions that we don't currently have answers for in order to make sure that anything that is marked in that second category, and then you can attempt to answer those two open questions. About the Hamlet's track and open country as well as the T27 question for yourself, And then after all of that, you should switch off the 16 repair steps in whatever manner you find most efficient.
>
> I am leaving for a meeting for worship and will not be back for about 4-5 hours, So hopefully you are able to either complete all of this work during that time, or at least use all of that time in order to move forward on this tasking.

## Speed first (2026-10-26, after feature 427)

Resumed after feature 427 landed its families outside the lanes (a 40-household roll 62.6M -> about 30M calls). The session
reported that the calls left were of two kinds: placing then repairing, which this feature's open tasks remove, and search by
trial - a candidate laid out in full and then refused - which no task of this feature named (dictated; "layout" = lay out):

> Okay, that makes sense. So basically, some of what we're describing is already in 417, but some of it is not. and in particular rules asked by trial rather than by construction is one of the big things that we need to target from what you're saying, and it sounds like that one should maybe be a priority. and the place then repair is the part that 417 already handles, if I understand you correctly. But the try, layout in full, and then refuse is not really handled by 417.
>
> So yes, how about we add these new things that you have identified as tasks to 417, and then we should explicitly make it one of the goals of 417 to get the kind of order of magnitude decrease that we believe should be possible based on the feature that we just completed, and that should be documented in 417 somewhere. And then I think we should order our remaining tasks in 417 to prioritize the things that will make us go faster before the things that will make us correct. And this is basically for the same reason that we did 427 before fixing 417. Because once we make things faster, then it will be easier to make them correct, because we will be able to iterate much more quickly.
>
> So with this in mind, go ahead and add these new tasks and then put them in whatever order you think will put the speed up tasks first, so that the things that will give us the most performance gains will happen at the very beginning of the 417 work that we are to resume. Then tell me what tasks you think those are and why, and then I will tell you whether to reorder things before we proceed. Thanks.
