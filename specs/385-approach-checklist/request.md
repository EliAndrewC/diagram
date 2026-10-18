# Feature 385 - the GM's request

The GM, 2026-10-17, asked to begin feature 384 (`specs/384-match-the-research-remainder/`) and instead proposed carving its first
items into a feature worked slowly, task by task, measuring each and improving the process between them. Verbatim:

> I would like you to begin work on spec kit feature number 384. However, I don't think that I want to just have you churn through that feature. In fact, I think that feature is too big in a way that is going to impair our ability to make good progress on it. So um, I think it might make sense to not start work on it just yet, but maybe to split it out a little into multiple features. Or rather, um, I guess really my goal is to get to a point where I can just turn you loose on that feature, but the thing that is stopping me is that in the past, I think we have found that our development processes need to become more efficient. And some of this is about tooling, which are improvements that we have already made since our last session. Some of it is recorded as I think the very first item in the SpecKit feature, which is like just our general approach to how we try to resolve these things. Because we keep running into situations where like we will try to implement a feature by essentially trying to solve the bin packing problem or to try to rearrange houses instead of rearranging paths, etc.
>
> So I think that what I want to do basically is carve off like I don't know a set of 10 or so items from the feature and move those into their own separate feature. And then the point of doing that feature is that we are going to kind of slowly and deliberately work on them. Where like we do one task and then we measure how long we spent kind of doing each part of the task. And then we see whether there are process improvements that would have made that take less time. And then we go on and do the next task, and then do the same assessment, etc. Uh, and then basically the goal is to see whether we can get things down to kind of taking an amount of time that is reasonable because I think that the combination of the size of this code base and the complexity of what we're doing has made it so that we often kind of get lost and hyper-focus on something without stepping back and taking the 10,000 foot view and saying, oh, hey, what are we actually trying to accomplish here, and is there a better approach? And yes, we do have some tooling changes around this. There is a round arbiter, and, you know, we have the uh, Claude Code advisor functionality enabled, but, you know, I think that there's probably some sets of changes that we can make that make it more likely that we're going to do the correct thing. And I wonder if part of what that is going to involve is something like a checklist-based approach that is above and beyond what we are doing in SpecKit.
>
> So here's kind of my thinking on this. Um, spec kit is something that we are using because it is a good way for us to kind of have a lot of stuff that is part of a feature where we don't forget about any of it. And then we have tooling based around that, and we're kind of using that in what I think is a standard-ish way. I mean, I say standard-ish because I have not actually engaged with the specifics of the SpecKit constitution, and I think our project guidelines do explain that this is what I am using SpecKit for, uh, rather than me having taken the time to write this the way that I would if, you know, this was a different project.
>
> But with that being said, let's take a look at the very first item that is indicated that we should work in this spec kit feature that we will then be taking out into its own spec kit feature. Um, this came about because a previous session was really just kind of thrashing on trying to make the village lanes fit. And then it was having trouble laying them out, and then kind of basically a couple of things happened that lead me to believe that we need some new structure in our project that a checklist-based approach might be a possible solution to. The first thing that happened is that the Claude Code session kept seeing that our lane placement algorithm had a rule that, you know, two lanes shouldn't come together at a 19 degree angle. And then lanes would come together at that angle because of an obstruction. And then instead of saying, oh, well, that rule kind of was meant to denote the fact that under normal circumstances, lanes tend to come together at fairly broad angles, you know, 90 degree angles or 70 degree angles or whatever. But if I'm walking through the forest and there's a rock and then, you know, like a footpath has to go around the rock, then things will come together at different angles than they otherwise would if the rock wasn't there. And so similarly, um, we ran into difficulty with that rule. And at no point did the Claude Code session say, okay, well, should this rule actually apply when there are obstructions? And I mean, I want to be careful about this because I don't want future sessions to just throw away rules when they are inconvenient. But a lot of times there will be kind of rules or guidelines or thresholds or numbers that kind of are just implementation details and didn't actually come from anything in particular. So like a previous example of this is that I found a Claude Code session thrashing on trying to fit every farmhouse in a nucleated settlement within 700 feet of the rice paddies. And then when I asked why that number was picked, then it said that it looked and found that there was literally no reason for it. Just like at a certain point in the past, uh, we had had a distance from the rice paddies and then 700 feet was recorded arbitrarily. And then we spent literal hours of wall clock time trying to conform to that when there was literally no reason to not just increase that size because, you know, like it wasn't based on any research. There was no reason not to have farmhouses be further away from rice paddies than that, etc. And so, you know, if we had some kind of checklist-based approach that asked about the rules that we're trying to conform, and then which parts of them are based on our research and which parts of them are just arbitrary implementation details, then that would, I think, help us to not fall into this trap. Because in some cases, it makes sense to keep a rule but then refine a number, or to keep a rule and add an exception. So for example, uh, in the case of these paths, it would make sense to say that, oh, well, in the absence of an obstruction, then two footpaths will not come together at a 19 degree angle, but they might come together at such an angle if there were obstructions that led to that being the case. However, as I think is indicated in the skill, if there are two different footpaths that are nearly parallel to each other and very close together, then that is the kind of situation in which a single footpath would emerge. And so there are like multiple solutions to the thing that we were thrashing on, one of which was relaxing a restriction by placing a principled exception to it, and then one of which was actually adding a restriction, like adding a new rule, where the new rule did in fact solve the problem. because if the footpaths were collapsed into a single footpath, then they wouldn't come together at all.
>
> And the thing is, this is the kind of thing that uh, isn't going to happen naturally, because this can't be mechanically enforced. This does rely on model judgment, but the way that we can help the model make the judgment in an implementation session is by having some kind of checklist which kind of guides the approach that we are taking. And that could be something that happens at the beginning. There could also be a checklist of that sort, whether it's the same one or a different one, that comes up when a session is taking a while, or when we're having to go through a lot of trouble to make something work on all seeds, or I don't know, just stuff like that.
>
> And this process of making a larger change should also be, you know, taking into account our general practices and guidelines. So as an example, um, something that troubled me was that the recommendation that the previous session made was that the footpaths should Uh, once we run into this kind of situation, uh, allow our algorithm to move homestead features around. Now the reason why this is troubling is, I mean, I guess it's troubling for multiple reasons. First of all, I sincerely doubt that that would be algorithmically better. because trying to shift around things within a very confined set of parameters sounds a lot like oh, if we can just solve the bin packing problem, then we're good here. But let's ignore that for a second. The reason why we place village lanes after homesteads and their features are placed is that in real life, that is how footpaths develop. Footpaths are the routes that humans will naturally take when navigating the environments that they inhabit. Nobody in real life moves their house so that a footpath will join with another footpath at a more intuitive angle. That doesn't happen. And so that suggestion, in addition to being algorithmically questionable, betrays a fundamental misunderstanding of what we are doing and why. Now the thing is, I think it is very understandable that this suggestion was made because when a Claude Code session, or for that matter a human, is really, really in the weeds on trying to get a specific algorithm to work, then that is the kind of thing that just seems reasonable. Like, oh, if we moved this house, then the lane might look better. But that means it is exactly the kind of thing where when considering such a change, then a checklist-based approach where we like literally go through and consider options one by one and kind of take into account and answer questions like, does this conform to how these things actually developed? And you know, are we trying to work around a limitation that is real? And are the numbers that we are using that are leading to this problem based in our actual research, or is there just an arbitrary figure that on inspection we just put there as an implementation detail months ago and then never thought about, and we could just change that, and then the problem becomes easy. or You know, are we trying to do something that is algorithmically very complicated to work within a limited amount of space when we could just expand the amount of space? that kind of thing. Now I framed this as wanting to split out initial things from that spec kit feature, but as I talk this out, I am wondering whether we should be splitting that out and then using that to develop these checklists, or if we have enough information now in order to develop the checklists. I mean, to some extent, you probably could both try to synthesize these sorts of checklists from our project guidelines, and then also maybe even go back and look at transcripts of past Claude Code sessions from, you know, let's say the last two to three weeks. Um, there hasn't been much that has happened since the beginning of this week. Um, I mean, I think I was running stuff on Monday and maybe even Tuesday. I don't remember, but, um, you know. I think if you go back a full week or two, then, you know, there will be tr- session transcripts where we might be able to see the kinds of pitfalls that we are falling into or rakes that we are stepping on. Um, I do want to be careful about doing this kind of audit because, like, I don't want to accidentally blow through our token budget for the rest of the week by having you basically re-consume every token that was, you know, emitted or outputted or whatever. Um, so I'm actually not totally sure how that kind of an audit would look. You know, because if you had to, like, read every message or read everything that was done, then that in and of itself would be comparable to just redoing all of the work. And, you know, it's not like you can re-consume two weeks worth of tokens in, like, you know, a single audit. But, I don't know, I'm just throwing that out as an idea that if there was some way to relatively cheaply perform the kind of audit that I am describing, then that could be a way to help us determine what types of checklist items are needed, what types of actions should force the use of a checklist, etc. Anyway, before we move forward, what do you think about all of this? What do you think a good set of first steps would be? What do you think the new feature that we are proposing should begin with, and how should that new feature be scoped?

The session proposed the shape (spec.md, "Why"); the GM, 2026-10-17, verbatim:

> Yes, please proceed with that. Uh, the shape that you have proposed looks right. So please file it, draft checklist version 1, and start the cheap audit. Thanks.

Carried from 384 (`specs/384-match-the-research-remainder/request.md`): its requests and the usage cap at 90% of the weekly
window, for the tasks moved here.

## The proposal the GM approved (the session's words, 2026-10-17, verbatim)

The GM's "the shape that you have proposed" refers to this reply, quoted whole:

> I agree with the diagnosis. I'd change one part of the plan: you don't need the split to write the first checklist. There's enough evidence to draft one now, and the split feature is where we test it, one task at a time.
>
> ## What I think
>
> **The rule exists, but it's asked too late.** CLAUDE.md already says "a number set only to implement against is a knob to move, never a target to defend." But only the round arbiter asks that, and the arbiter only runs after a cap or tripwire fires, which is after the hours are gone. In both your examples (the 19° meeting and the 700 ft distance), one question asked at the start would have ended the problem: "where does this rule or number come from: research, your ruling, or us?" So the fix isn't a new principle. It's asking the existing questions at two earlier moments:
>
> 1. **Before the first edit of a task.** This hooks into the existing `make task-start` / `make decide` step.
> 2. **When the work starts to resist.** For example, the first seed the change refuses, a second red gate, or the hourly step-back from feature 383.
>
> At either moment, the checklist would be the required content: `make tick` refuses until it's answered, the way the decide-first rule already works. That keeps it in tooling rather than memory.
>
> **The checklist content (v1).** For each rule or number the work is fighting:
> - **Where does it come from?** A `Research:` claim, one of your rulings, or an implementation detail of ours? If it's ours, it's a knob.
> - **Does it describe how the thing actually came about, or is it tidiness of ours?** Footpaths are walked after the houses stand, so houses never move for a path.
> - **Name at least three exits besides "conform", and judge each:**
>   - Refine the number.
>   - Add a principled exception, like "unless an obstruction forces it."
>   - Add a rule that removes the case, like merging two near-parallel paths.
>   - Give it more room.
> - **Is the plan secretly a packing search against an unresearched constraint?**
> - **Guardrail:** dropping or loosening a rule needs its reason recorded where the code changes. This is not permission to throw out inconvenient rules.
>
> **The audit is cheap if it reads the right things.** Two weeks of transcripts come to 2.5 GB, so reading them is out. But I measured the high-signal parts:
> - **Your typed prompts:** 216 messages, about 26,000 words. Your corrections ("why 700 ft?") are the rakes we stepped on, already pointed out.
> - **236 round-arbiter rulings:** 115 accept, 35 continue. Each one is a moment a session got stuck, already labeled.
> - **The `make feature-report` breakdowns.**
> - **The ~10 lesson memories already written:** room before packing, homesteads before lanes, derive don't pin, and others.
>
> One Sonnet reader can turn all of that into a list of pitfalls, each tagged with what it cost and which checklist item would have caught it. That's roughly a few hundred thousand tokens, not two weeks' worth.
>
> **The retros need a measure we don't have yet.** Feature 374's report shows "thinking" was 51% of its time (25.5 h) and Bash another 8 h. It can't say how much of that was churning between approaches and how much was doing the work, and that split is exactly what you want to see per task. So the new feature should also make the report divide each task's time at its decision points, roughly "before the approach settled" and "after."
>
> ## Proposed first steps
>
> 1. **Draft checklist v1 now,** from CLAUDE.md, the lesson memories and the cheap audit above.
> 2. **File the new feature,** once you approve it. Its first task is the lane law (384's FR-000), which is the worked example: the needle angle rule made obstruction-aware, and near-parallel lanes merged. 384's own FR-003 already says no work starts until you decide how to go faster, so this feature is FR-003's answer.
> 3. **Run each task with the checklist,** then do a short retro: where the time went, which checklist item fired or should have, and what to change. Amend the checklist in the same step, then take the next task.
>
> ## Scope
>
> About 10 items, taken in the order 384's "How it starts" already sets:
> - the lane law
> - the four cohort seeds failing at HEAD (17, 21, 40, 45)
> - T48 (the web carries a re-deal of the seats)
> - T47's patch re-landed
> - about five ranking rows of different kinds, so the checklist is tested on more than lanes
>
> The feature succeeds when the time per task falls and the checklist stops changing between tasks. 384 keeps everything else and resumes under the finished process.
>
> ## Answers
>
> - **What do I think?** You're right. The missing piece is timing, not a principle: the "where does this number come from?" question exists but is only asked after the thrashing. A checklist at task start and when the work resists, enforced by the existing decide/tick tooling, fixes that.
> - **Split first or checklists first?** Both, in that order of thinking: draft v1 now from what we already have, and use the split feature to refine it task by task.
> - **Can the audit be cheap?** Yes. Skip the transcripts and read your prompts, the arbiter rulings, the feature reports and the lesson memories.
> - **What does the feature begin with?** Checklist v1 plus the report's per-task time split, then the lane law as task 1.
> - **How is it scoped?** About 10 items from the front of 384, each followed by a retro. 384 is amended to move them out.
>
> Project rules require your explicit approval before I file the new feature or move items out of 384. If this shape looks right, say so in your own words and I'll file it, draft checklist v1 and start the cheap audit.

## Amendment 1 (2026-10-17, after T01)

The GM, after T01 landed, verbatim:

> Yikes, okay, so it does sound like we need some tooling fixes because 3 hours and 22 minutes is exactly the kind of time that we are trying to have not happen here. Um, I guess I do understand that a lot of that was actual, like tooling evaluation and even tooling fixes. Although it sounds like we have even more tooling fixes, which it sounds like is T02. Though, if I understand correctly, you're saying that we still have failures? Like, were, are those failures unrelated to what we're doing here? And that's why you're saying that we're done, even though the same stuff is failing as before? Sorry, I'm just kind of confused about what you mean by saying that we're done and also there are failures, unless those failures are just like totally unrelated to our work, in which case that makes sense.
>
> I'm curious uh, if we made the tooling fixes, do you think that that would have caused us to take a reasonable amount of time in order to implement this, or what? Because, again, nearly three and a half hours to make what is not a fundamentally complicated fix is, like, pretty crazy. But, again, if we made, like, five different tooling fixes and we're trying out this new system for the first time ever, and, you know, we still are just seeing how it works, then that makes sense. And I understand that this is not going to be, like, the representative version, and that we will, you know, kind of make our additional rounds of tooling fixes next, and then we'll do, like, another claim fix off of the backlog, and then see how long that one takes, etc. But I'm just curious whether you think that after we make the T02 tooling fix that we will be well set up to do that test, or if we can kind of already tell that this isn't working. Because I'm just not sure. I could see that being a good next step, or I could see us saying that, oh, actually things are pretty bad and we need to address the badness with more than just T02. So what do you think?

The session proposed widening T02 (its reply, verbatim, the part the GM approved):

> So I'd widen T02 to cover what T01 measured:
>
> 1. **Re-checks against the version last read.** Compare against the version the last check actually read. This alone would have saved most of the 50 minutes.
> 2. **One check where several are now spent.** One quote-check batch should answer a page-wide check, and one agent should judge all the pop-ups that cite a changed page, not one agent per pop-up.
> 3. **Guards instead of reminders.** Refuse writes to the tree while your own gate runs, rather than relying on the checklist's C6.
> 4. **Its own measurement.** T02 records what each check cost per line changed, so T03 shows whether the fixes worked.
>
> Then T03, the four seeds plus the general side-by-side merge, is the real test. If T03 still takes more than about two hours, the problem is bigger than tooling: we'd be paying for verification that's out of proportion to the work, and we should rethink how much checking a change owes.
>
> Changing T02's scope amends the spec, so it needs your approval. Shall I amend T02 to include these four items?
> Noted: memory is near the cap, but none of my jobs are running right now. I'll keep any next work small until usage drops.
>
> I'm still waiting on your answer: shall I amend T02 to include the four check-cost fixes?
> Two things first: amending the spec, and checking the research behind those two rules. Both questions are fair, and as you say, they're exactly what part A of the checklist should catch. Looking up what the record actually says:
> Appending your two messages and my proposal to `request.md` verbatim, then the amendment itself:

The GM, verbatim:

> Yes, please append the spec to include those four items. Thank you.
>
> Also, when it comes to fixing those four seeds, Are we sure that household paths don't cut through neighbors' yards? I thought that our research findings were that they did.
>
> Similarly, I didn't think that there was a rule about village lanes needing to reach the fields. Is that actually based on our research? I mean, like, I'm almost reluctant to ask this question, or ask these questions, because these are exactly the kinds of questions that our checklist-based approach is supposed to uncover. So to some extent, it might be that the thing to do when we reach this spec is to, like, remove that from the spec and then have a, like, new session try to implement that as a test, or, uh, I mean, I don't even mean, like, me starting a new session. I mean, if you're able to create a sub-session that doesn't have access to the fact that we have already evaluated this as, like, not being necessary or something, then we would be able to see whether the actual fix is to say that there isn't a problem, because the thing that we're doing is actually fine, because it's exactly the kind of thing that our checklists Uh, like the new checklists are supposed to help us determine rather than just wasting a lot of time. What do you think about that?

## Amendment 2 (2026-10-17): the blind Approach

The GM, in amendment 1's message (above), on T03's rules: *"if you're able to create a sub-session that doesn't have access to the fact
that we have already evaluated this ... then we would be able to see whether the actual fix is to say that there isn't a problem"*.
The session proposed, verbatim:

> T03 starts with an agent that sees only the task, the checklist, and the code and record, and writes T03's Approach block. My answers are sealed in a scratch file outside the repository, which it can't read. If it questions these two rules on its own, the checklist works without hindsight; if not, we learn which question to sharpen. The cost is one agent and no implementation.
>

The GM, verbatim:

> yes please make the blind approach T03's first step. And no, I don't think I want the two-hour threshold, like, on record. Because, to be honest, I haven't even looked at what we would be doing. So I don't know for sure that a two-hour threshold is bad for it, although my instinct is that for the things that we are doing, it is bad. But I don't think that that's a matter of a specific threshold. I think that's more about just, you know, doing a review after the fact and seeing how it goes, and then, you know, doing measurements until we figure out how long stuff takes in practice when we don't seem to be going in circles.

## Amendment 3 (2026-10-17)

The GM asked: "Please explain the one ruling that you say seems worth my judgment so that I can make a ruling on it now." The
session put the claims-gate question (`ask:t03-claims-at-landing`) as three options, verbatim in part:

> 3. **Never block on unchanged code; the gate files the finding as an open task instead.** The landing goes ahead, and the gate itself writes each finding into the feature's `tasks.md` as an open item. Since a feature can't close with an open task, the finding must still be fixed before the feature closes, just not before this task lands. This automates what the arbiter did by hand for T03.

The GM, verbatim:

> Yes, please lock in option three. Thanks.

## Amendment 4 (2026-10-18)

The GM, verbatim:

> Okay, so whenever you finish locking in that option 3 stuff, let's talk how how we did on task number three  It looks like it took nearly two and a half hours to fix 4 broken seeds.  That still feels not great.  You mentioned it took 2 hours and 25 minutes.  Can you break that down and see whether there are other improvements we need to make, other process improvements, etc?  Go ahead and finish your option 3 implementatilon before working on this, I don't mean to interrupt you, I just want to make sure we do more measurements before we proceed with T04 and see how things are working.

The session proposed, verbatim in part:

> - **Fix the measurement.** Record which subagent made each tool call, if the hook input carries that; otherwise use each agent's start and stop window. `make feature-report` would then split time into the session, the subagents and idle, and print a per-phase table like the one above.
> - **One goal per task.** A checklist item: a task's "done" names one goal, and a second goal becomes its own task.
> - **The decision log comes from the tooling.** `make feature-report` prints the log's skeleton (agent runs, cohorts, part B stamps, ticks), so a retro is filled in rather than reconstructed.

The GM, verbatim:

> Yesa please implement the proposals you made for what to do before task 4, as amendment 4.
