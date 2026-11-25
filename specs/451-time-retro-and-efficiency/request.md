# Feature 451 - the GM's request, verbatim

## 2026-11-19, the retrospective

> Okay, so can you do like a retrospective breakdown over the last however many hours it's been, I guess just like the last 14 hours And then for each task that you've done, can you indicate a breakdown of where our time went on that task? And then it would be kind of nice to be able to see overall, like, how much time are we spending on running our tooling? How much time are we spending on running our tests? How much time are we spending on recompiling things? Stuff like that. I suspect that there are efficiency improvements that we could make, or process improvements that would help things along. But obviously I'm just guessing because I haven't actually looked, so I'd like to see some actual numbers. Maybe this is all actually fine. I mean, it does seem like we're making pretty good progress. We've done dozens of tasks today, but let's see what those numbers look like.

## 2026-11-19, the tooling question

> Also, is there some tooling that we could add that would make this kind of information easier to collate in the future? Like, I think this is something that we would like to be able to review historical data on in ideally a relatively cheap way. So are there like hooks or things that we can add to our makefile tooling or other things of that nature that would make it much easier for us to assemble this kind of retrospective analysis going forward?

## 2026-11-19, the approval

> All 6 of your proposed improvements sound good so please do all of that, along with your 4 proposed ideas for filling ion what's missing from gathering this kind of data.  And let's make sure all of the enforcement is real enforcement and not just instructions.

## What "your proposed improvements" and "your 4 proposed ideas" refer to

The session's own words, as put to the GM on 2026-11-19 just before his approval (not the GM's words; quoted so the review reads what
he approved):

> **Improvements, ranked by minutes they'd have saved in this window:**
> 1. **Keep builder contexts small: 44–95 min.** A builder's model calls slow down as its context grows: 10 s per thousand output tokens under 200k, 23 s per thousand over 700k. T152 and T221 each passed 1.3 million tokens. A fresh builder per stage, with a handoff file, would fix it. That figure is a correlation, so the saving is an estimate.
> 2. **Stop using `make static` as the edit loop: 26–52 min.** T152 ran it 24 times; T227 and T229 ran it 13 times between them, rebuilding coverage at 1.5–3 minutes a run. A crate-scoped check while iterating, with `make static` once at the end, would do the same job.
> 3. **Make agents start long runs the way the session can track: 18 min.** T225 started `make static` with a plain `&`, so no completion notice came, and it sat idle for 15 minutes. A guard refusing that pattern, plus a shorter poll loop on my side, would close it.
> 4. **Fewer plan re-rounds: about 10 min.** Briefs that default to fixing in the task, and that ask for full coverage up front, would avoid most of them.
> 5. **Split the three slowest hook suites: about 8 min.** Each takes 30–40 s and sets the floor on every `make hooks-test`.
> 6. **Smaller landing fixes: about 5 min.** Accept commas in `T=`, and run `make quick` after `task-add`.

> **What's missing, and what I'd change:**
> 1. **Categories.** The categorizer maps only `make quick`, `test-file`, `done` and a few spec-kit targets. `make static`, `rust-test` and `hooks-test` all land in "other tool" (206 of 208 minutes). The fix maps make targets to tests, compile, gate, land, review and docs.
> 2. **Which run a wait was waiting on.** `where-time` sees the waits between turns, but can't tell whether a land, a gate or a test run was behind them, because a background run's end is never logged. The fix logs that end from its completion notice.
> 3. **Phases inside one make run.** Compiling, testing and the gate's other phases aren't separated in the log. The fix has the Rust checks and `make land` append their phase seconds as event lines.
> 4. **An agent's token cost.** Not logged today. The fix records it at each agent's stop.
>
> Then `where-time` and `feature-report` read those new lines, and `where-time` gains an `UNTIL=`. A breakdown like today's becomes one command, kept for every feature, with no new tool to learn.

## The GM, 2026-11-20, on the order (after the overnight report: the data half landed, none of the six improvements yet)

"okay well let's prioritize those remaining improvement fixes, okay?  doing those first makes everything after them faster"

## The GM, 2026-11-20, on performance work in general (asked right after the order above)

"can we in general priotitize performance improvements going forward?  I thought that was already a rule."

## The GM, 2026-11-20, on measurement work (after the 14-hour report, with T08 - make where-time's columns - building)

"I would also like for this kind of measurement task to be counted as a performance task for the purpose of scheduling and coming first.  Because it's so closely related to performance that it should be counted as such even if the task itself doesn't improve performance."

## The GM, 2026-11-21, on the closing checks (after the split of test time into iterating and closing checks)

"yes please file that as a performance task, thanks"

## The GM, 2026-11-22, on bundling small tasks (T141)

"I also wonder whether small defects can be bundled together and worked at the same time. Like, it sounds like what you're saying is that every individual task goes through the same process, but that feels like it is itself the issue. Because if we have found lots and lots of very small defects, then surely it makes sense for us to look at the current feature and say, hey, what set of tasks is currently open? All of which are very tiny, such that they could all be worked basically at the same time?"

"Okay sounds good, so let's do that then, and not bother cutting back on new tasks filed.  It sounds like we canfilenew tasksjust as fast as we are now if we bundle them together when fixing them."

## The GM, 2026-11-22, on measuring every phase (T153-T156)

The GM: "okay, we should also make the hook suites measure their time so they won't be missing; we want everything measured so we know where our time goes, especially for compiling, running tests, and generating maps"

## The GM, 2026-11-22, on the disk and build caches (T155, T158)

The GM: "Okay, that sounds good. So I guess proceed with whatever it is that is going to make sure that we clean up after ourselves in terms of the file system to not have 30 gigs of stuff suddenly get eaten without us realizing it. But your points about reusing the same build cache and whatnot are well taken. Like, it does seem like you have correctly understood my intention."

## The GM, 2026-11-23, on hook output length

The GM: "A lot of our hooks have somewhat long output ... That amount of output consumes tokens, so could we accomplish the same thing with no loss of fidelity and fewer tokens?  If so then should that be a general project guideline about hooks?  Maybe even something mechanically enforced, where each hook must contain a comment explaining how many words it uses and mentioning the subagent check that reviewed it for brevity and fidelity?  What do you think?"

## 2026-11-23, Stop hooks that keep the session busy, and a timer in their place

Shown a Stop block that fired while the session correctly waited ("still: BLOCKED: a builder slot is free" under a round-arbiter ruling that held new work, and "FINDINGS UNFILTERED" for a builder's own review), the GM asked:

> Do we think that much text needs to be there? For that matter, do we think that these kinds of hooks are even the right approach, as opposed to something like a cron that fires every 5 minutes and does nothing and adds nothing to the context if we are still active, and only injects data into the session if we are stopped?

Told that 23 of the session's turns since 14:42 were spent only answering such blocks, and offered: Stop hooks block only for what the session must do before stopping; a periodic check, silent while the session is active or waiting on a tracked agent, speaks only when it is idle with actionable work and respects binding rulings and set-downs; the findings guard fires only for reviews the main session dispatched, once - the GM said:

> Yes, please go ahead and implement that. Thank you. That seems worth doing before we do our stop and talking more about things. Thanks.

## 2026-11-23, the convergence talk: cascades that change nothing, size trims, labels, oscillation

On the cascade (told that a page edit re-owes checks on every pop-up citing it):

> The problem is when we do a cascading set of reviews that triggers a cascading set of changes that is mostly not finding actual problems and is just making changes that are very time consuming to make, but are not fixing any real flaws. So let's talk about that before we do literally anything else, because we have to fix that before we move forward.

> I want to figure out what the difference is between the ones that might plausibly have required that and the ones that were just straightforward adjustments that never could have plausibly needed this kind of cascade.

On size trims (told the 0009 and 0059 trims dropped content):

> if those size limitations are causing us to cut details that could cascade, then I think that actually a good rule of thumb is that we should literally never do that. ... One possibility is that we could split something into multiple entries, so that all details and the fidelity of information that we have captured is preserved. Another option is that we could raise the size limit. ... an audit-based process that permits us to go past the size limit when an adversarial subagent check confirms that there don't seem to be a lot of good ways to do edits that would allow us to maintain the current amount of useful information ... so that we record a new limit for this specific entry. ... no edit to maintain entry size should ever be substantive.

On splits:

> as long as the original page being linked to directs a reader to the other page where the full information can be found, then nothing needs to cascade simply because a split occurs.

On labels:

> Shouldn't attested versus guess be something that cascades mechanically rather than requiring a review, though?

On oscillation and review scope:

> it seems possible that we should not run full re-reviews and make only the smallest possible changes perhaps with some kind of adversarial subagent review process. ... style edits are just a different category of thing than factual inaccuracies. And it might be that when we are cascading, we are only interested in factual inaccuracies.

Approving the session's seven rules (a size edit never changes a claim; a split is a move; only a claim-changing edit triggers review; labels are data and propagate by regeneration; only factual findings cascade; re-reviews scoped to the change; settled choices stay settled), the re-classification test and the 0009/0059 repair:

> Sounds good. Please do all of that, and then we will talk more about what other changes might need to be made before moving forward with additional rounds of implementation.

On the narrowest check (told: of 30 pop-up edits, 20 corrected something wrong, 16 of them page-caused, 6 only completed, 3 wording, 1 made worse; the mechanical echo check catches every page-caused correction with no agent and fires on 55 of 119 pairs, the agent triage sent 35 of 121 on; the plan: the echo check as T186's first filter, the agent triage after it, the gap-fill clause dropped, the garden-pond sentence fixed in its three places):

> Okay, that seems reasonable, thanks. Please finish that implementation and let me know when you're done so that we can move forward on figuring out good next steps for resuming our port and making sure that we are capable of resuming that port.

On T192 (told: tagging the rest of the record's labels is 670 GUESS items over 241 drawing pages and 613 Guesses bullets over 284 pop-ups, on the order of 60 or more page sessions, unmeasured; untagged labels keep the old review path):

> Yes please tag the rest of the record before resuming our port, thanks.

On T192's route (told the 6-10 hour projection assumed an agent writing a Guesses sentence for every GUESS block and reading every unworded one; offered: a script tags each block that names its own label, a Guesses sentence is written only when a pop-up first cites the item, attested blocks are skipped if nothing reads their tags, and only truly ambiguous blocks go to a session):

> Thanks. Yes, please proceed with that as the way forward rather than the really expensive one that frankly seems kind of pointless for the purpose of what we are trying to accomplish.

## 2026-11-24, the cascade test's six defects fixed before the port resumes

Told what the cascade test's six defects in the new rules are (451 T209 to T214: T209 a new fact contradicting a pop-up is cleared; T213 a claim marked mislabeled can be rewritten unchecked; T210 147 claims forced after a generated doc regenerated; T211 22 claims forced by the item anchors; T212 8 false sends from three fixed phrases; T214 the change-scoped review refuses a sheet with no earlier verdict), and that the session recommended fixing all six before the port resumes, the GM said:

> Yes let's fix all 6 of those before we resume.

## 2026-11-24, where T210's kept section words live

Told that T210's kept section words live in each clone's `.git`, so another clone forces its sections once, the GM asked:

> should it live in the clone rather than in the repo?

The session's answer: in the repository, beside `dev/claims-index.json` (20 sections, 136 KB), because they can be the only copy of what was judged; page texts (5.6 MB) stay per clone, since git history holds them. Escalation-check (2026-11-24) ruled it the session's to build under "Yes let's fix all 6 of those before we resume.": the per-clone limit is T210's own wrong outcome. Filed as T215.

## 2026-11-24, an ad-hoc agent that judges or builds runs on the session's model

The GM, with the session on Fable 5.2 and its builders dispatched as `general-purpose` with `model: opus` (the agent-model guard refuses an ad-hoc dispatch that names no model; the GM 2026-09-19):

> Thanks, and quick question for you. Do the general purpose subagents that you're firing off share the model of the parent subagent? For example, we are currently using Fable 5.2 and I would like for it to be the case that the general purpose subagents that you are firing off to do stuff use whatever model it is that I have selected. So in this case it would be 5.2 of Fable, but if I switch back to Opus 5.5, then I would want them to use that. Do they inherit in this way? Is that how that works?

The GM, the same day, on the rule T216 builds:

> because that ruling from before is something that I still want with regards to enforcing that Sonnet should be used to read, fetch, translate, or extract. But then instead of Opus for anything that judges, I'd like it to be inheriting the parent session model for anything that judges.

## 2026-11-24, the page edits' cascades are watched

The GM, as the session queued the page sessions that close out 449 T420 and T425 and feature 452's page items:

> That all sounds good, and you should make sure to take a look at what cascades happen as a result of any of our page edits, just to make sure that we are cascading appropriately. and not doing anything silly like making a bunch of unnecessary edits as a result of something trivial changing, etc. But also that we really are cascading in situations that do call for it. Thank you.

## 2026-11-25, a research backlog: UNRESEARCHED, no search before a guess

Told what the last two days' research changed (of eight hamlet searches, two changed what is drawn), the GM proposed:

> Okay, so maybe the procedural change here is to not stop and kick off research. In all of these situations right away, but rather to have some kind of research backlog. Where we make a best guess about what to render, and then note it as being something that is unresearched. Where unresearched is different than unsupported, because I think unsupported means, if I'm not mistaken, that we did research and couldn't find anything, whereas unresearched would mean that we know we have not yet checked. Does that sound right to you? And then that would allow us to move forward more quickly and it sounds like that would not in practice make a big difference at this point. Like it's very unlikely that we will be rendering meaningfully different maps as a result of punting on this kind of research until later, right?

Offered the rule change (UNRESEARCHED a fifth label on the research pages as well as in the claims; a new guess recorded as UNRESEARCHED with no search; the backlog `make claims-report`'s UNRESEARCHED list, searched at each port stage's end for the items that stage touched; a search still first where a decision is foundational or a guess is likely visibly wrong; most of page sessions P13 and P14 dropped from the pre-port list, P12 kept), the GM said:

> yes please
