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

## 2026-11-25, a builder's claims round split off

Told that most code builders on 2026-11-24/25 hit the 300k context cap and handed off (449 T420, T423, T427, T429, T430; 451 T218-T222), each handoff costing a fresh builder 10 to 20 minutes of re-reading, and that the cause is one builder doing the fix, the measurement sweep, the plan section, the plan review and the claims round, the session proposed splitting the claims round off by default. The GM:

> sounds good please do that ASAP

## 2026-11-25: the task time breakdown (451 T243)

The GM, 2026-11-25 (verbatim, dictated; voice substitutions none):

> let's take a look at all of the tasks that have landed over the last 24 hours or so, and I would be interested to know how they break down in terms of the time that was spent, you know, like how much time was spent actually writing code and reading code in order to know what to write versus compiling code versus running tests versus generating maps versus landing and such. We should probably have like a name for this kind of breakdown so that I don't have to keep specifying it. Maybe if I just say "task time breakdown" then that can mean this kind of thing, like maybe that could go into our CLAUDE.md or something. And also into, I guess, the makefile comments that describe the timing and such. And yeah, basically just everywhere that we're gathering these timings, then we could refer to this as being in support of "Task Time Breakdown" or something.

> I think that when you give the breakdown we should also make sure to include percentages, just since that is a helpful thing for me. So that I don't have to do the percentage math in my head.

> I believe that it is the case that some of these things end up running in parallel, right? ... So how will that be reflected in the task time breakdown? Like, I guess the two numbers that we would care about for any given thing would be the number of minutes and, of course, its associated percentage that we spend doing that thing, but then also separately the number of minutes that we spend blocking on that thing. So for instance, if we spent 122 minutes running tests, but only 84 minutes blocking on those tests running, then that is significant. So I think that the tooling needs to be able to reflect that

> I think that we do want the spec fidelity agents, reading and judging, to be in a separate category than the reading and writing of code, because that is conceptually different, and the way that we would optimize it is also different.

> it sounds like in addition to each category, then it will be the case that each makefile command that we run will have its own timing breakdown, I guess, because that's something that is fairly easy to track in our tooling?

The session answered that `make task-time` would be built on `make where-time` (a new make target, the GM's "that sounds great. Yes, let me know when that's ready.").

The GM, 2026-11-25, on the breakdown's biggest buckets (verbatim, dictated):

> the things that take a larger percentage of our time seem like they are worth asking whether they can be parallelized

The session's paraphrase, not the GM's words, of two amendments he agreed in the same exchange: every minute named, or the remainder reported with what it is and why it could not be booked, never a silent "other" (amendment (c)); and the review bucket's commands split by kind - plan review, claims round, record and pop-up checks, arbiter - each beside its agents' minutes, after he asked whether "review tooling" includes the plan review before a task begins (amendment (e)).

The GM, 2026-11-25, three later amendments, relayed by the coordinating session; the ellipses are that session's, not the GM's:

> (i) time spent waiting for me should probably not be counted in those percentages, even if it is recorded ... it is useful for you to mention ... that 458 minutes were spent waiting for me, and that this is 20% of the total time, but then when looking at everything else, those minutes should not be part of the denominator when calculating the other percentages ... as a percentage of the time that our Claude Code sessions spent working.

> (j) as long as that automatically gets broken down in the future as we do our task timing breakdown.

(said of the 180 blocking minutes the first run booked "waiting: nothing in flight")

> (k) if they were running in parallel with other things, including running in parallel with other tasks which were not research-based, then that number would be misleading because it would essentially imply that we spent half of our wall clock time waiting for research to be done before we could proceed with implementation, which may or may not actually be true.

(said of the 949 blocking minutes the first run booked "research and page sessions"; the coordinating session's reading, not his words: a session's own working time is minutes, blocking only where a waiter was stalled on it with nothing else in flight, and the window's concurrency is reported)

The GM, 2026-11-25, after round 4 of T243's plan review, defining blocking (relayed by the coordinating session; the ellipses are that session's, not the GM's). It replaces the reading of (k) above and round 4's:

> (l) a minute should count as blocking. When something else is waiting on it to be done before it can be started. because that is a different standard than whether or not a different unrelated piece of work is able to be done at the same time. So for example, if we are doing research in order to clarify the wording of things ... but that is simply done in parallel with other tasking, then that is really not blocking anything. On the other hand, if we need to decide which of two implementations to perform, and ... that research must complete prior to us beginning our implementation work, then that research is blocking. And that research would be blocking even if there was a different unrelated task happening in a different subagent at the same time. ... that is admittedly more difficult for us to measure because that is not something that our tooling can inherently know ... to the extent that we can pass that kind of context clues to our tooling when the data is collected, whether through environment variables or I don't even know what else, then that will make it easier ... it doesn't have to be 100% exact ... only 90% of the time are we correct ... I think that's basically fine, because what we're looking for here is just a broad understanding of where our time goes when we are implementing tasks.

(the coordinating session's build of it, not his words: blocking is per task and by dependency - a stretch of work blocks a task when that task's next step waits on its result, whatever runs elsewhere; a `Blocks:` clue in a dispatch's or page brief's prompt and `L7R_BLOCKS=` on a command, recorded with the data; stated defaults where none is given; the window's blocking the sum over tasks, which may pass the clock where tasks ran side by side)

The GM, 2026-11-25, on the research queued (relayed by the coordinating session in T244's task line; the ellipses are that session's, not the GM's):

> because none of the research that we currently have queued is particularly important, in terms of being blocking, or likely to significantly change our scripted map generation, then I would like to essentially defer all of it until at least tomorrow ... will our current procedures end up inadvertently kicking off a bunch of research tasks ... If so, then what can we do about that?

(the coordinating session's build of it, not his words: a `research` switch, open or deferred, beside claims and port - T244)

## 2026-11-25: the escalation check's cost and the Stop hook's false questions (451 T235)

The GM, 2026-11-25, after pasting a QUESTION UNFILTERED refusal of a message that asked him nothing (verbatim, dictated; voice substitutions none; the cost is his figure as dictated):

> So you have already told me what the cost is roughly for each of these at about $70,000 tokens per run. Though I do have a couple of questions about that. One is that you said 1.85 million tokens in, but I thought that our context window was only 1 million tokens at a maximum. So what does it mean for something to be 1.85 million tokens? Another question is, whether or not there are more efficient ways to do this Or efficiencies that we can add to augment this.

(the session's reply, not his words, listed the levers: stop the false firings, which T235 fixes; a mechanical pre-filter, the hook sending the agent only messages that put something to him - a sentence ending in "?" addressed to him, or an offer - "T235's natural shape"; and a narrower bundle for the check, which is a separate change. The coordinating session's T235 brief relays the pre-filter as asked by him that day.)
## 2026-11-25: what this container leaves on disk (451 T245)

The GM, 2026-11-25, with the disk at 88% (relayed by the coordinating session in T245's task line, three sentences as quoted there):

> my host has a 461G disk drive, so if that is full then it is because this container specifically is leaving artifacts sitting around

> having some kind of audit of disk space and what this container specifically is leaving sitting around is probably something we should add to our performance tuning and checks

> we might even want to trigger something automatically if our disk space ever drops below a certain percentage of free space

(the coordinating session's build of it, not his words: `make disk-audit` - every place the container writes, its size, owner and age, against a budget each; the cache budget made to hold - least-recently-built variants and idle trees' targets evicted past the budget, never under a running build; an automatic eviction below a free-space percentage, a knob, GUESS 20% free, that says what it freed; a removed worktree's build directory removed with it; the audit register's disk entry (449 T437 item 13) noted in the plan and not built in this task, by the builder's brief - T245)

## 2026-11-25: the per-clone leftovers (451 T246)

The GM, 2026-11-25, on the coordinating session's report of what its clone kept (relayed by the coordinating session in T246's task line, as quoted there):

> the old task scratch folder is over 1/3 of a gigabyte? That doesn't seem right to me

(the host session's measurements, passed on at the GM's request - the host session's words as T246's task line relays them, not his: "(1) /tmp/claude-1000 is 17 GB and 14.4 GB of it is files older than 3 days, mostly finished sessions' and tasks' output, never read again - an age sweep (a knob, GUESS 3 days) at session start and at the low-disk trigger, the running session's scratchpad kept; (2) a trial worktree's build cache goes as soon as its worktree is gone (keyed to the tree's existence, not idle time - 451 T245's sweep catches a hand removal at the next sweep: measure that it does), and whether the clones diagram-backlog-review and diagram-backlog-pages are still wanted is checked; (3) the live build caches (diagram-backlog 80 GB, -land 43 GB) measured with debug = line-tables-only (or 0) for the dev and test profiles and CARGO_INCREMENTAL=0 for one-shot gate and landing builds, before and after in size and build time (speed work may change nothing a test pins), and old artifacts inside a live target pruned by age; (4) ~/.claude is shared by every container and the host: make disk-audit counts only this project's transcripts (about 7 GB), never the others; (5) about 13 GB of podman storage on the host is unused image layers, the host's to clean - the audit names it as host-side". The coordinating session's brief to the T246 builder added: change the profile only if build and test times do not get worse beyond noise, else report the numbers and leave it for the GM; first measure whether any review reads a snapshot older than its current unit's, and keep what one does - T246)
## 2026-11-24: a ruling attributed to the GM names his recorded words (451 T233)

The GM, 2026-11-24, told that page 0006's drawing page carried, in a comment, "the GM's ruling, 2026-07: dry plots are rectangles laid out against the canal" (verbatim from `specs/449-rust-codebase/request.md`, "2026-11-24, the GM never ruled that dry plots are rectangles"; also `docs/gm-rulings.md`, "NOT a ruling"):

> I never made a ruling that dry plots are rectangles laid out against the canal. That was never at any point something that I said was true about these maps. That is what a session told me the research showed. But if that is not what the research shows, then we shouldn't do it.

The GM, 2026-10-25, on a choice the research does not settle (verbatim from `specs/417-all-seeds-pass/request.md`, "Later on 2026-10-25"):

> if our research findings do not indicate that things were any particular way, then we can either make it a tunable knob, or we can just do whatever is algorithmically easier.

The research queued is deferred by his words of 2026-11-25 above ("I would like to essentially defer all of it until at least tomorrow"), `dev/switches.json`'s `research` switch.

(the coordinating session's build of it, not his words, from the audit of 2026-11-24 that found 74 of 180 such comments with no recorded words behind them: T233's task line - a check that a research page's comment or a claim's CANON label naming "the GM's ruling|catch|word|decision", "the GM ruled" or "GM <date>" points at a request.md, `docs/gm-rulings.md` or a gm-reviewed row holding his words; the 74 and the about 60 unaudited near-twins its baseline, shrinking as pages are edited; fixing them page work, waiting for the research switch)

## 2026-11-25: before three parallel builders (451 T254-T257) and the tooling-state repository (451 T258)

The GM, 2026-11-25 (verbatim, dictated), on the session's recommendation to start the port's first batch at three builders after four fixes (a started-task mark per task, task numbers from one writer, the plan-review record no longer conflicting, a review recording in its own tree):

> sounds good, please start with that while I make the new repo - what do you think the new repo name should be?

And on the private repository for the record-check answers and event logs:

> I created https://github.com/EliAndrewC/diagram-tooling-state for the tooling state

## 2026-11-25: the audit register (451 T259)

The GM, 2026-11-25 (verbatim, dictated, as `specs/449-rust-codebase/port-talk-agenda.md` item 13 and its "Order" paragraph record
them), on the register:

> when we make this kind of optimization, then we should be documenting the logic behind it, the measurements that we took, and then also crucially what we would look at that would falsify the notion that this is a good idea ... a list of all of the auditable optimizations and processes and procedures, and then each one would know the last time that it was audited ... re-audit to see if they still make sense or if they need to be tweaked or redone or eliminated

On the hidden ones:

> some things are easy to identify as a measurable and auditable part of our tooling ... something like this limit on builder token window context size might not even show up as an optimization ... after the initial backfill, we can backfill as we go, as we find things that we missed

On the decisions not to build something (2026-11-25, which the register's `kind: declined` entries answer):

> We should also make sure our processes record decisions about what NOT to implement for future reference in the same way we record decisions about the processes and tooling we DO implement.

On its order:

> should we move that item up to or near the front, so it can apply to all of the other optimizations we're building at the moment?

On the three-way measurement (agenda item 12):

> we should make sure to measure whether the complexity of the handoffs actually saves time and/or tokens relative to either letting the builders grow or not using them in the first place

## 2026-11-26: builder worktrees (451 T285)

The coordinating session had made each builder a fresh worktree by hand and deleted it and its build cache after the landing, against
the reused-worktrees rule of `docs/process-decisions.md`, "Two code builders at once". The GM, 2026-11-26, as the coordinating session
recorded his words on T285's line in `tasks.md` (commit 26b12e37f1; copied here from that line by T285's builder, who did not hear them):

> Okay, so we should definitely not rely on you remembering to do the correct thing with worktrees, and we should make it so that whatever tooling we use to create worktrees automatically enforces and performs the correct behavior without the opportunity for this kind of mistake in the future.

## 2026-11-26: a build slot instead of a builder cap (451 T284)

The coordinating session had set the builder count at two so that their compiles and a landing's gate would not coincide. The GM,
2026-11-26, as the coordinating session recorded his words on T284's line in `tasks.md` and in `docs/process-decisions.md`, "Two code
builders at once" (copied here from those by T284's builder, who did not hear them; the fragment is all they hold):

> wouldn't it be better to address that with some synchronization rather than pre-emptively limiting builders just in case?

## 2026-11-26: the idle-tests suite's cases that fail under load (451 T104)

The idle-tests guard's suite failed a landing's gate on good work (2026-11-26 16:19Z, green on the rerun unchanged), and T104, filed
on 2026-11-21 for two of its cases, was still open. The GM, 2026-11-26, as the coordinating session gave his words in T104's
builder's brief (copied here from the brief by that builder, who did not hear them; the sentence is all the brief holds):

> I agree with prioritizing the test that fails under load being fixed.

## 2026-11-26: the task time breakdown remembers when he last asked, and the second tier is booked apart (451 T298)

The GM asked for the breakdown "since the last time I asked, whenever that was", then for the second tier of checking to be a category
of its own, then said what he expects of its blocking. His three messages of 2026-11-26, copied whole by T298's closing builder from
the coordinating session's transcript (its queued-message and user records at 15:36:16Z, 17:21:17Z and 17:24:27Z; the builder did not
hear them):

> I suppose this might mean that we might want an additional capability in the time task breakdown to keep track of whenever I last asked, so that I don't have to remember the period of time to ask for when I want the new data.

> Yeah, so for what it's worth, I do think that we should probably move batched landing stuff that happens as the second tier of checks into its own separate category rather than counting it against any individual task.

> Another thing to keep in mind about that is that that separate category in general is rarely going to be blocking anything, right? I mean, one of the things that we're trying to measure with the task time breakdown is where our bottlenecks are. But I would expect that our measurements will consistently show that our second tier of landing checks is pretty much never going to be the bottleneck in terms of running or completing tasks, because it's something that we do after tasks have already landed. And new tasks beginning is not something that blocks on it, so although there is some reason to want to make sure that it is optimized, and isn't eating up too much CPU or disk space or whatever, because that kind of thing can interfere with our tasks, it probably will be almost or completely in the category of non-blocking time that is never a bottleneck, rather than in the category of things that we are waiting to be done before we can proceed with more work. Right?

The rest of T298's line in `tasks.md` is the coordinating session's, not his: the window table and the line a landed task, "a
task's own table ends at its carry into the clone", the one line a batch, the four booking faults it found reading two-tier tasks'
tables, and its relay of the third message as blocking minutes on their own line, "expected near zero since no new task waits on
the gate - a rise is the signal that something has begun to wait on it (a carry behind a running gate, a repair, a build slot)".
## 2026-11-26: a pool tree pre-warmed at its handout (451 T316)

A warm pool tree's first checks run compiled what other builders had landed since the tree last built, in the builder's own time. The
GM, 2026-11-26, as the coordinating session recorded his words on T316's line in `tasks.md` (commit 25787db43f; copied here from that
line by T316's builder, who did not hear them; the question is all the line holds):

> would it make sense to begin compiling immediately within a work tree builder?
## 2026-11-26: two tiers of checking, and the plan review's later rounds (451 T308)

The full checks ran twice a task, once in the builder's worktree and once at the landing's gate in the session clone. The GM,
2026-11-26, as the coordinating session recorded his words on T308's line in `tasks.md` (copied here from that line by the builder
of T308's plan-review part, who did not hear them; each ellipsis is that line's):

> we are undergoing extremely rigorous checks at the point where a builder in a work tree is bending over backwards to make sure that absolutely nothing wrong can land in the session clone, when in fact the correct place for that level of rigor is checking whether something in the session clone can land back in the main checkout and in the main branch on GitHub ... session clones to be a place where already tested things get staged, but where the full level of rigor gets deferred until the session clone itself has gone through that set of gates

On whether a builder is kept after its report:

> being able to close out builders as they complete has some advantages from a simplicity and design perspective. So I want to be wary of needing to keep them around for any reason ... that reason has to outweigh the costs. Not only the costs of tokens or memory or whatever, but the cost of complexity and edge cases and such

> Is that something that the original builder needs all of that context in order to be able to fix?

The rest of T308's line is the coordinating session's build of them, not his words: the trial's shape, what it is measured against,
and its ALSO of 2026-11-26 - that under two tiers nothing runs beside a plan review round, so what each second round was owed for
is measured and the mechanical causes are removed at `make decide` before the review is dispatched.

## 2026-11-26: the Stop hook's false questions are not reported to him (451 T299)

The Stop hook's question and offer detector fired 12 times on 2026-11-26 and about half were statements; the session had been telling
the GM of each false firing. The GM, 2026-11-26, as the coordinating session's brief to T299's builder relays his words (copied here
by that builder, who did not hear them):

> I would prefer not to see these messages about false positives

> I am okay with some number of false positives. I just don't want to see the explanation of the false positives reach me. Though it probably is worth asking whether the number of false positives is within what we should consider an acceptable range.
