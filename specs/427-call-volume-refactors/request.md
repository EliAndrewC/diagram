# The GM's request, verbatim

Three messages from the session "Diagram performance", 2026-10-26, in order. Dictation: no substitutions apply.

## 1. The exercise (the session ran it; no prototype)

> I've spent a lot of time trying to optimize how long it takes to generate a Hamlet with our scripted process, and it is still pretty slow. I mean, not like unbearably slow, but concerningly slow, and crucially much slower than I would expect it to be. The example I keep coming back to is the number of homesteads that we are placing. It will take us multiple wall clock seconds in order to place a few dozen houses on a map. This fundamentally seems like it should not take that long, given how many billions of computations per second modern microprocessors are able to do. In other words, if we are taking that long to do this, then it really feels like that means that something has gone wrong. Now, there have been a number of sessions in which I have brought this up, and then we've taken a look at the code and been able to make some tweaks and then actually gotten the time down. But these improvements seem incremental and relatively small at this point. Whereas I would expect every single stage of our Hamlet generation to take a fraction of a second. even when we artificially inflate the number of homesteads too far beyond what a regular hamlet has, such as 40.
>
> [...] I just know for a fact that we are capable of doing much, much better, and that we should be able to realize literal order of magnitude improvements without changing our fundamental technology stack away from Python, because I have worked on projects that, for example, do complex geometric calculations using SVG files and lines and checks for things overlapping, etc., etc. And I know that it does not have to take this long to do the general kind of thing that we are doing.

(The elided middle described the subagent exercise itself; the session's record of it is `research/estimate-exercise.md`.)

Follow-up: "Yes, please go ahead, but let's not do the prototype just yet. We'll look at the numbers that we get from this and then decide how to proceed."

## 2. More data first, no changes yet

> Okay, yeah, I don't think we want to make any actual changes just yet, because I do have a different session currently working on some big refactors. That make our tests more efficient and then that is being used to get rid of some of the guess and check that we are doing, which I think will help with this a little bit. But basically, I don't want to be making multiple different fundamental engine refactors at the same time. However, I think that the kind of findings that you are pulling out here are going to be extremely valuable, and I would like to gather even more data about places where we are making millions of calls that we just kind of fundamentally do not need to, you know? [...] what else could we find in our code in terms of hotspots, where the hotspots are not individual functions that take a long time, because as you say, none of them do, but rather places where functions are being called just an absolutely insane number of times, you know, hundreds of thousands or millions of times, even though the maps and things that we're placing are putting down just a relatively small number of items on the map.

## 3. File it, do not work it

> Okay, yeah, I think I would like you to write all of this up as its own feature. I don't want you to actually perform the feature, but I want all of the details that are needed for a future session to work this, like all of your findings, the suggested tooling change for the make target for the performance fanout, and basically everything that we have figured out here to be captured in the feature directory somewhere. You know, there could be multiple different files that talk about the different things. Because I don't just want one super long file that has all of this necessarily, because that's token inefficient, but you know, just as long as everything is captured in that feature directory and then referenced in the specification so that the future session knows where to look to find each piece, then that would be good. And then once I'm in a place to actually work on that, then we can do that.

## 4. Decisions on the session's suggestions (2026-10-26)

> Are those suggestions for me to consider already recorded in the feature itself?
>
> Also, I think that recording call counts alongside the timings might actually be not going far enough, because one of our problems with timings has been that it is difficult to take consistent timings, because which processor we were using and what the current system load is really throws them off. So I think that recording the timings themselves has been tricky and not really done what we needed it to do. So I wonder if the thing that we should actually do is to, I guess, keep recording the timings, but completely stop using timings as a gate on anything. Like, we should no longer have any rules around what kind of timing increase we permit without it flagging something. Instead, we should do as you say and record call counts alongside the timings, but the call counts themselves are the thing that we are gating on, because as you say, that is consistent. And so that flag would replace the timing band Though, as you say, it would not necessarily be a gate, but rather something that would need to be accepted by the arbiter and possibly raised to my attention if it is increasing by too much. But this is the kind of thing that I would expect the arbiter to be able to handle without me.
>
> Since feature 373 overlaps this, then I think we should just fold it into this feature.
>
> This feature should not require all seeds to pass if seeds were previously failing, as we already have a different feature which exists specifically to get all seeds passing.
>
> When I talk about staying in Python, what I am basically expressing is that I do not believe that we need to rewrite everything in Rust. However, if switching away from shapely and numpy is something that we analyze and find would be better, then we can certainly do that. I don't currently see any reason to do that, because as far as I know, these libraries are fairly efficient. And I don't believe that there is like a high performance version of NumPy that is somehow better than NumPy, which already writes all of its critical path code in C, as I understand it. But it is certainly not a hard requirement that we continue using those particular libraries.
>
> please update the new feature 427 to make sure that all of these suggestions are incorporated, both the suggestions that you have made and my refinements of them. Thank you.
