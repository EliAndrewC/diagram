# The GM's goal for how development runs - his words, 2026-11-26 (the talk before the port resumes)

Load this file when: the talk before the port resumes (449 T437) turns to how decisions about the process get made, or a
session is about to record a process decision on its own reading.

Kept verbatim so that a crashed terminal does not lose it (he had just had one). More is to follow in a later message; it is
appended below as it arrives. Nothing here is decided: it is the statement of the problem.

## What prompted it

The session had recorded, as decided under his standing pre-approval, that a builder's closing step also runs coverage on its
own crates. He asked why; the decision had been made on the count of batch gates that failed, where the goal is task
throughput; it was reversed the same night (`docs/process-decisions.md`, "Two tiers of checking", "REVERSED the same night").

<!-- SOURCE: GM NOTES -->

> Okay, glad that that's already been fixed, but I guess at a high level, my question is how we can stop this general kind of wrong decision from being made in the future. This relates to a overall project goal that I have not quite figured out how to implement but which is something I want to try to achieve, or at least begin putting in place before we resume our port of the scripted map generation.
>
> Basically, a pattern that we have been going through for months is that I will ask for features and then as more features get added, then one of two things will end up happening over time. Or sometimes both. The first thing is that what I asked for gets implemented, but in a way that results in defects or other things breaking or becoming less correct. Now, when I say breaking, I don't necessarily mean like failing tests per se, although that did happen for a while and we just had a bunch of failing seeds for a long time. But I more mean things like our maps drifting out of compliance with our research. In ways that our tests did not explicitly capture, or everything technically working, but then when I as a human looked at the map, then I would see things that were just visually bad, like Village lanes that zigzagged for no reason. Or waterways that nearly connected but did not quite connect, or my request for a feature turned out to be difficult and then was simply abandoned in favor of implementing something that did not meet the specifications that I asked for, etc.
>
> So in order to try to avoid this, then we ended up with a second set of problems, which was that everything would just end up taking much, much longer. I added layers of adversarial subagent checks, I added fidelity map reviews and making sure that things passed on our reference seeds as well as random seeds and making sure generated every as part of our landing, etc., etc., etc. And that all did reduce the number of issues, but it ultimately caused development to slow down. And in many cases, when I went back and checked how often these kinds of safeguards were preventing bugs, then it turned out that some of them were occasionally preventing something from slipping through, but being a large drag on feature throughput, or they were generally not catching anything and were just taking longer than they were worth, or they were catching things that were not strictly speaking bugs, but just like minor wording tweaks that might be a little clearer, which would then cascade and cause us to make dozens or hundreds of other wording tweaks that perhaps made things slightly clearer, but did not ultimately fix anything that was wrong, etc.
>
> So what I have basically been doing for the last several weeks as part of the Rustport activities that we have been engaged with has been to try to make things much faster by moving to Rust and then trying to very slowly and deliberately make sure that I understand every aspect of our development workflow optimized to the point where reasonable, and we are knocking out all of the low-hanging fruit that would otherwise stop us from being able to implement things quickly.
>
> Now, the thing that I'm trying to figure out how to put into place is how to get you to do some of what I am doing. And here's what I mean. The primary way that I am streamlining our efficiencies is by going through the process of closing out tasks and then periodically up to a few times a day or if I am very busy then at least a few times a week asking for a breakdown of how long things are taking looking at what the bottlenecks are and then asking, hey, could this be parallelized or could step that takes a long time be made more efficient, or how would we reduce the amount of time that this takes? And then I basically just ask you those questions, and then you pitch ideas, and then I mostly accept the majority of them, rejecting only the ones that really seem like they would be counterproductive or seem like they would be a bad idea for other reasons. So it must be noted that I do not accept all of your ideas, but for the most part I tend to end up just asking you what might work.
>
> I have more to say but I want to make sure this doesn't get lost since I just had a tmux crash, so I'll share more thoughts in a followup message.

<!-- END SOURCE -->

## His second message, the same evening (2026-11-26, about 01:00 UTC on the 27th)

<!-- SOURCE: GM NOTES -->

> Okay, thanks. I will want some number breakdowns on the 21 tasks that have landed under 2 tiers. Before we move forward, but for now I will finish my thought.
>
> At one point, I tried adding a new type of reviewer or arbiter that for long-running sessions would look at what we had done over the past hour or two every so often and then see whether there were any inefficiencies that we might address. I ended up turning this off and then rolling back most of what it implemented because it was good decisions about what was actually going to make the project better overall. So basically, if it saw that a particular change would have caused one specific task to save a minute or two, then it would implement that change even if that change on net was going to reduce the overall throughput of tasks.
>
> So I turned it off and then decided that I would come back to this idea later, because just asking for this at a high level was clearly not good enough. However, since that happened, we have added quite a lot of tooling around measuring how long things take and measuring where the time goes and having a notion of a checklist-based process for determining what it is that we are supposed to do in various cases, and a lot of other things that I think will not inherently solve this problem, but make it much more achievable for us to have this kind of periodic automated process, which would certainly need to be carefully designed, but which overall might be able to do the kind of thing that I'm describing without needing me to be as actively involved. Because fundamentally, I don't even know Rust, and my involvement has mostly been to look at breakdowns of how much time we are spending on different things, and then ask reasonable questions like "should it be taking so long to compile our Rust code?" or "is there some kind of caching we could be doing?" or "are we recompiling more often than we need to be?"  Basic questions like that, which do not require me to have any actual knowledge of Rust whatsoever.
>
> So I think that if we were able to have not only the guiding principles that we are implementing towards with things like adversarial subagent checks and things of that nature, but also rigorous measurements and throughput calculations and retrospective analysis of how much we would expect something to help, and also these changes how they could be measured at a later date to be shown to have not paid off, such that they would need to be either tweaked in terms of their thresholds and specific numbers, or even maybe backed out entirely, then I think that this kind of automated process that keeps things under control would have the potential to keep our performance in check and maintain and even improve our task throughput rather than resulting in a degradation of our project standards. I would also want to have this process be able to look at things like existing thresholds and conventions that we have set if its analysis points it in that direction. For example, if our unit tests begin taking too long to run, then I think we already have something like a threshold where no unit test can take longer than 1/10 of a second to run, or something like that. But I have no idea if that's a good threshold. Does that actually make sense? Should it perhaps be 100th of a second or even 1,000th of a second? Or maybe something like 1,000th of a second could be the default, but then we might have individual tests that genuinely do take 50 times longer than that for a good reason, which would imply that we should set a much more rigorous threshold but then exempt individual tests. I mean, again, I have not looked at this in depth. And part of the reason is that today, the only mechanism by which this kind of analysis would ever be done is if I personally spent the time, focus, and attention to direct you to look at it. And that's fine for now, but I would love to figure out a generalized periodic automated review process for long-running sessions such as this one, where bottlenecks are identified and remediated in a rigorous and structured way that would have enough guardrails around it to ensure that if I left Claude running for a couple of days, I wouldn't come back to find everything degraded, things taking longer rather than shorter because we overfitted some tuning to a couple of tasks that just happened to be getting worked when this kind of automated review process ran.
>
> So that's the overall goal that I am trying to achieve. And I have some ideas for what that might look like, which are fundamentally not different in concept from the failed version that I tried in the past and then backed out, which I think is probably gone from the code base, though it might actually just still be present and turned off or something. And you should probably look to see if that is there, and then we will want to either just delete it completely if it's still there, or if there is anything worth salvaging, then we can decide whether it gets adapted into this new thing that we are describing. this new thing probably needs its own different type of adversarial subagent reviewers, or maybe it uses the normal ones, but the normal ones need to be updated to have a separate and more rigorous set of questions and checks and analysis which get performed on performance and throughput related tasking. I'm not sure.
>
> I suspect, though, that few things are almost certainly true, one of which is that our initial version of this will not be quite right and will need to be modified over time based on how well it seems to perform. Another thing is that there is a category of what is currently a SpecKit feature and might remain as such, but might also turn into a different type of backlog tasking which is basically that these kinds of performance changes once implemented should probably always come with a reanalysis that happens after some amount of work has been done under the new system. In some cases that might only be a matter of hours if we are doing quite a lot of work and end up landing many dozens of tasks in a relatively short period of time. In some cases it might be days, in others it might be weeks. Or maybe it should just always be all of the above. just on general principle, and that one of the things that we might build into our tooling such that this kind of performance reviewer would periodically invoke some make target in long-running sessions such as this one, which would tell it whether or not we owe a retrospective analysis of some particular tweak or tuning or procedural change or whatever to see how well it is holding up. And that this would include both whatever pre-registered standards were recorded when the feature was implemented in order to possibly falsify its usefulness, as well as any common sense things that the performance reviewer at that time thinks we should look at in addition to that.
>
> How does all of that strike you? I definitely want to begin work on this before we resume our port because this will be absolutely crucial as we proceed with that port. But I don't know whether right this moment is the correct time to actually try to implement this, since we are currently landing other more urgent performance tweaks. And it might make sense for us to capture my previous message and this one in a new SpecKit feature in order to circle back to it when we are ready. I'm not sure. What do you think?

<!-- END SOURCE -->

Reading note (the session's, not his): in the second paragraph "because it was good decisions" reads, from what follows, as
"because it was NOT making good decisions" - dictation.

## What the session found when it looked for the earlier version (2026-11-27)

It is still in the code, switched off: the HOURLY STEP-BACK of feature 383 (`specs/383-tooling-caches-and-hourly-step-back/`),
suspended by his words of 2026-10-21 - "let's suspend but not remove the hourly step-back arbitur for now" (405 amendment 4,
T43). `dev/step-back.json` holds `"state": "off"`; `make step-back`, `make step-back-on` and `make step-back-off` are in the
Makefile; the code is `rust/gate/crates/measure/src/measure/stepback_bundle.rs` (660 lines, builds the hour's bundle for the
round arbiter) and `rust/gate/crates/reviews/src/reviews/checkpoint.rs` (554 lines, the hour coming due and the switch).
Whether any of it is kept or removed is his to decide; nothing was changed.

## His third message (2026-11-27, about 02:00 UTC), after the tree-idle measurement

The session had answered his alarm at the second tier's 123 blocking minutes with a measurement (the pool trees idle 23% of
the window, `dev/measurements/2026-11-27/tree-idle/results.md`), a fix (451 T394) and a re-measurement target of "under 10%
idle, a guess".

<!-- SOURCE: GM NOTES -->

> Yeah, I feel like we can probably capture a lot of the work that we've done over the last few days as examples of things that our goal is that it should be able to know to look for these things and notice these things and suggest these kind of changes. I mean, really, I think at this point we have many dozens of tasks, and broadly speaking, probably at least 10 different, like, categories of interrogating our processes that I have directed over the last few days that might be good reference examples to include when we file the feature, because I think we probably, for each category of thing, want to make sure that it is something that we know to look for and know how to check for, and have a checklist-based procedure for ensuring that we are asking the right questions, and so on and so forth. I don't know if that's something that you can just what, but that probably is something that we will want to do relatively soon.
>
> As an example of the kind of judgment that I am talking about, then I am personally skeptical about something like a target of 10%. In the manner that you described in your recent message. because in fact my mode of thinking is basically that that might be okay, but it also might just be that we actually are strategy for how to do the second tier of checks. Should that simply happen in its own subtree with its own agent? as in the one that I am conversing with right now, be kept as idle as possible all the time so that it is doing basically nothing but coordinating subagents and relaying that to me? This is basically describing the purpose of the primary session as an orchestrator rather than a worker, you know? which is not exactly a distinction that we've had in the past, but which is something that we have been naturally evolving towards, and so it might be that we should be looking at the best practices that others have worked out for orchestration of this type. Relatedly, I know that we are using workflows for some things, I think, but then also not other things. But as we have made more changes, I have no idea whether there are things that we are not currently using workflows for that we should be, or vice versa, based on the many, many process changes that we have made just this week. So that is an example of the kind of thing that I would want this type of performance reviewer, or maybe it's more of a process reviewer, to be able to look at.
>
> I do have a few more high-level thoughts, but this was something that I wanted to make sure was captured. Now, while I work on formulating my additional thoughts on this matter.

<!-- END SOURCE -->

## His fourth message (2026-11-27): THE FUNDAMENTAL FRAMING - no single metric is the target

He says of it: "What I am saying here needs to be the fundamental framing for this feature." It answers the session's proposal,
after his second message, of "one stated number that every proposal is judged against".

<!-- SOURCE: GM NOTES -->

> So you had mentioned that your thinking was that we needed to have a single metric that we were optimizing around. But I think that that is both dangerous and probably likely counterproductive. For example, most of what we have been doing over the last few days has been oriented around optimizing task throughput. And that's great because it is the thing that I have been most interested in for the last few days... and also because I trust myself to ask for and approve changes that I think are actually helping with the underlying productivity that I care about rather than with the metric. But consider that if we were literally focusing everything around optimizing task throughput, then we could literally double our task throughput by cutting the scope of each task in half. And we could do exactly the same amount of work with twice as many tasks. Which would not only fail to accomplish the kinds of real productivity that we actually care about in reality, it would actually decrease our productivity by literally doubling our tasking overhead by having us file and land twice as many tasks.
>
> Similarly, I sometimes have looked at the relationship between the number of lines of code in a task and how long the task took to implement. This is very useful because some tasks are very small and serve as a good baseline for things like a simple hook change or a small documentation tweak or a fix for a failing unit test, etc. And then similarly, when we have larger tasks that are a few hundred lines of code, then we can see what the difference is between something that takes a few dozen lines and a few hundred lines, which serves as a useful basis of comparison. However, the moment that we ever integrated lines of code into the metrics that we were optimizing against in any way whatsoever, then that would create a set of incentives that would be very likely if we were oriented around just one metric (even if that metric itself was a computation that took lines of code into account as one of many numbers being synthesized) to result in a negative or even potentially disastrous direction for our project and its standards.
>
> This is Goodhart's Law. Once a metric becomes a target, it ceases to be a good measurement. Goodhart's Law does not in any way imply that we should not have metrics or that we should not try to improve our metrics, but it argues against exactly the kind of one guiding metric that you had proposed previously, and requires us to take a more holistic approach. So I think that one of the fundamental and foundational questions that we have to ask about our process reviewer is which metrics it should consider, and then how it should synthesize those metrics into judgments about whether our processes are getting better or worse. I have no objection whatsoever to looking at the number of lines of code being implemented, because that's something that I do myself when evaluating these kinds of things, just as I have no objection to looking at overall test throughput, or the amount of time that we spend running unit tests, or our utilization of our builders compared to the amount of time we spend idle, etc. Those all seem like good things to look at, and it probably is useful to use some of that data in order to synthesize some high-level metrics about productivity. But I don't think that it is safe for us to then declare that optimizing those metrics is the goal. This would be true even if there were not non-numeric hard to quantify things involved, like whether the maps looked good, or whether we feel that the amount of time that it takes to make minor wording improvements to edit prose for clarity is worth the cascading time and tokens that are being eaten up, etc.
>
> What I am saying here needs to be the fundamental framing for this feature. And so I think that this message should be captured alongside the others in the feature so that when we proceed with it, we can keep all of this in mind as we figure out how to balance these different needs which exist in tension with one another. because optimizing ruthlessly just for the metrics leads to disasters of the sort that Goodhart's Law calls out, but just going by what feels right at the expense of metrics leads us to absolutely unacceptable places where 5 lines of code take 15 minutes to implement.

<!-- END SOURCE -->

## His fifth message (2026-11-27, the morning after): TOKEN COST is as important as throughput

He asks that it be added to these notes. It extends the fourth message's holistic assessment: token cost is one of the measures
that assessment must weigh, with a breakdown by task, and the tooling it needs belongs to the process reviewer feature.

<!-- SOURCE: GM NOTES -->

> Sure - something I didn't emphasize in my discussion of a process reviewer before but which is crucially important, is token cost.  That's just as important as task throughput, since over the course of a week, the real limit on throughput is often tokens.  So whatever metrics we gather must include token cost, such that our holistic assessment of whether things are getting better or worse includes the token costs of each task, ideally with some kind of breakdown.  that will probably require additional tooling improvements, which we can handle as part of that feature - please update our notes so far to include this message about it

<!-- END SOURCE -->

What the session knows today of where token cost is and is not recorded (2026-11-27; a starting point for the feature, not a
design): `make review-cost` and `dev/review-ledger.md` record each review pass's tokens in and out (cached and not); a builder's
own report carries `subagent_tokens` at its end, but nothing books it to a task; 451's request (item 4) notes an agent's token cost
is "Not logged today"; `make task-time` books minutes by category, never tokens. 451 T499 (in flight) measures one slice: how
many bytes of the plan builders read into context.

## His sixth message (2026-11-27, the afternoon after): the MACHINE's resources as metrics - CPU, memory, disk space, disk writes and the file-system journal

<!-- SOURCE: GM NOTES -->
> Okay, that sounds good. And then I guess we should probably also add on to our process reviewer something about how the metrics that it is monitoring to see how the system is doing should include things like CPU usage, disk space usage, memory usage, and also probably something disk writes, we have had periods of time in which the thing that is the bottleneck that we're in contention for is the file system journal. That's actually not something that I have made any attempt to optimize just yet, but literally might be something that I could imagine speeding things up if we made some tweaks. So it feels like a thing that we want to make sure that we are able to keep an eye on. So please add this message to our running list of my messages about the design of the process reviewer. So that this is something that we will take into account when we design and implement that. Thank you.
<!-- END SOURCE -->

What the session knows today of where these are and are not recorded (2026-11-27; a starting point, not a design): the clone's
memory and load sampler (451 T274, `make sampler-start` / `make sampler-report`) writes a JSON line every `L7R_SAMPLE_S` seconds to
`l7r-events/samples/mem-samples.jsonl` in the git common directory - the cgroup's memory and the load average, nothing per process
and no disk; `make disk-audit` reports disk SPACE by area against its budgets when run, keeping no history (it found the build
cache at 246.8 GB against 100 GB that day, filed as 451 T515); nothing records disk WRITES, I/O wait or the journal's contention
(jbd2), though the journal was the contended resource on earlier days; CPU is seen only as the load average.

## His seventh message (2026-11-27, the afternoon after): every measurement says HOW MUCH WAS GOING ON - compare like with like

<!-- SOURCE: GM NOTES -->
> Okay, that sounds great. And yeah, good catch on the coverage in the builders, because that was not something that I realized had somehow slipped back in. I mean, I am obviously reading what you're sending to me, but there's a lot of stuff, and so I am liable to miss things. So I'm glad that that was caught rather than us redoing a costly mistake. I do look forward to seeing the final numbers after we are done putting everything together and I guess we should make sure when we're measuring performance that we are kind of like generally how much is going on at the time, you know, like we don't want to do anything silly like capture performance metrics when only one builder is running, and then capture performance metrics when four builders are running, and then compare them without noting how much was happening at the time, because that sort of thing could cause us to think that things are getting better or worse when actually all that's happening is that we are looking at the system when it is implementing different numbers of tasks. Of course, this is something that I would hope that a process reviewer would be smart enough to see, and indeed the entire purpose of having an intelligent process reviewer is to not fall into this kind of trap. But we still want to clear away as many pitfalls as we can think of in advance to minimize the chances of having the process reviewer step on those rakes, so to speak.
<!-- END SOURCE -->

What the session knows today of where concurrency is and is not recorded (2026-11-27; a starting point, not a design): the pool's
log (`builder-pool.log` in the git common directory) records every handout and release, so the trees held at any second can be
rebuilt; `make task-time` prints a "Working at once" line (how many actors worked together) for the window, not per task or per
figure; the memory sampler's report (451 T274) has a row for each count of pool trees held; the machine's load average is sampled
but not joined to any task's figures; no figure in `make task-time`, `make review-cost` or `make where-time` carries the
concurrency it was measured under, so two windows can be compared without it.
