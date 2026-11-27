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
