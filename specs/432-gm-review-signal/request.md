# Request: the GM, 2026-10-26, the GM-review queue (verbatim, dictated)

## The request for the audit

```text
Okay, so the idea behind the GM review was basically that I felt like a lot of features were hanging open for way too long because there were way too many questions getting escalated to me. So I wanted things to be able to close so that we could move forward, and then I could look at them later. The problem is, I think that most of what's ending up in GM review is just stuff that I shouldn't have to answer. Now, admittedly, I have not done a thorough review, but lots and lots of stuff is ending up in GM review. Like, way more than should for the kinds of work that we are doing. So I think that this is yet another case of stuff being raised to my attention that should just be handled by the arbiter and the implementation generally.

With that being said, before I change the rules, I would like to do an audit of all of the OpenJam review items. And then I think if we take a look, maybe even dispatching a subagent for each or something, though of course we should be efficient about dispatching the subagent because there are lots of OpenJam (OpenJam -> open GM) review things, and so we should make sure to either do this as a workflow or to otherwise use system prompt caching in order to ensure that all of these many different subagents are well-defined and are making use of subagent caching as per our project guidelines.

But I would be really curious to know what the categories of things that exist in GM review are, and which of those things just should not end up there in the first place, and what process improvements we can make to reduce this down so that anything that ends up in GM review I actually know is important and that I should look at it. Because right now I've basically concluded that I should just ignore it because it is almost purely a distraction, which is bad, because that probably means that there are a few important things buried in there that I really should look at, but our system is kind of training me to not even bother, you know? So I think the first thing we should do before we file a new feature or anything like that is just do a review of what is there so that we can see what a good way forward is. Do you feel like you know enough to be able to do this in a token efficient way? Or should we talk more?
```

("OpenJam" is the dictation of "open GM", the GM's own correction inline.)

## The audit's result, as reported to the GM (summary)

465 open rows in 36 features, judged by nine agents on one rubric: 443 not his, 11 YES, 11 MAYBE; after checking each for
staleness, three genuinely his (374#60 the magistracy residence size, 385#40 the dispersed-hamlet feature never filed,
397#10 translation-check as a wave job). The categories: 159 process tooling fixes the arbiter ordered, 156 round-cap
accepts, 37 round-cap continues, 37 routine step-backs, 23 red-gate fixes, 15 route changes, 11 accepted limitations, 10
touching his words or a ruling, 9 process faults, 8 other. The cause: feature 375 queues every round-arbiter ruling and
every fix it orders. The proposal, as put to him:

- A. Stop queuing what isn't his: round-cap rulings, process-only fixes landed with a test, routine step-backs and red-gate
  fixes stay in the arbiter's own log.
- B. One door to the GM: anything that wants his decision passes escalation-check first, then is listed as held and named in
  that turn's final message.
- C. The arbiter can't write "the GM's to decide" without that door.
- D. Fix the held-list bug that dropped the residence item.
- E. Stop check work multiplying from small edits: claims invalidated per cited passage, not per page; pop-ups sharing a
  paragraph checked once.
- F. Clear the backlog: mark the 443 not-his rows reviewed with his words, so the features held only by that box can close.

The audit's files: the rubric and the per-row verdicts are in `audit/` here.

## The GM's answer

```text
Please file A through F as one feature. after we have cleared the backlog, then there will still be the three GM review items that are genuinely mine open, which is exactly what we want. And then I will handle them on my own time as appropriate. Thank you.
```
