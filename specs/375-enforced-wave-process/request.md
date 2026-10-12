# Feature 375 - the GM's request

The GM, 2026-10-10, after the session's look back at feature 372's waves 105-111 (five changes proposed: content-scoped
record-check owing, line-scoped claim re-owing, decide-then-freeze waves, a pre-gate preflight, and the triage parser and
plan-verdict fixes):

> Yes, please reserve a feature to include all five of those. And do you believe that this new feature will address all of the process inefficiencies that you are describing in your analysis here? remember that in order to actually work. Then we need to enforce good procedure at the tooling level, because anything that requires someone to just remember to do the right thing is not tenable and will inevitably slide back into doing the wrong thing.

Earlier the same day:

> In particular, I want to make sure that our tooling is up to snuff. [...] at the rate that we're going, it'll probably take like a week of constant running in order to close out this feature. And if that's what it takes, then that's what it takes. But in the past, it has often turned out to be the case that process improvements will give us order of magnitude speedups in development time.

Then, on detecting loops and limiting rounds (2026-10-10). The session answered the first of the messages below by
proposing event tripwires in place of an hourly timer, FR-006 and FR-007 beyond the five, a held / to-review split for his
review, and the report owed before the last tick; the GM's replies ("Okay, thanks", then the last message below) built on
those proposals (transcript `8d3395e5-fe32-4f85-9c89-80c344d2ac1a`):

> Are there ways to give that advisor specific instructions for things that we want it to look out for? Because I do think it might be good to have something like an hourly check that looks at the session and asks kind of just a general series of questions about, like, are we running lengthier tests than we should? Or are we oscillating back and forth? Or did a round of reviews or changes end up triggering a cascading series of other changes and other reviews, which is disproportionate to the actual tweaks being made? [...] Or heck, Maybe in addition to that, the very last step of implementing any spec kit feature is a post-mortem review of how the implementation went and whether there were any inefficiencies. [...] if at the end of every feature we literally had a table of how was spent running tests and how much time was spent thinking and how much time was spent implementing and how much time was spent waiting for subagent reviews and how much time was spent actually making the spec kit feature [...] maybe the actual solution here is that we have hooks built into our tooling which will save off timestamps that allow us to mechanically and trivially calculate these numbers. Such that the post hoc session review or analysis of how long a feature took is not actually difficult to do and might be able to happen action of a second with a make command.

> Now you mentioned a set threshold within "a wave" But I don't think that these kinds of waves are a normal part of our development. [...] today there is an escalation path which is basically saying that you get a certain number of rounds before you need a waiver from me, the human. But I think that we should probably first escalate that question to a subagent designed to answer that question. And then I, the human, can review those choices either after the feature has closed, or as a prerequisite for the feature closing. Though I do think that I tend to want things to land on main without needing my review. So that probably does suggest either a post-feature thing or we allow things to land on main with that and only that category of box unticked. And then just as we have a make target for our `make speckit-todo` we could have a separate target [...] the idea is that our progress does not stop because we are going through an unexpectedly high number of rounds of reviews, but rather we escalate to a subagent, and that subagent might say to continue, or it might say that it deems that what we have now is actually fine, and we don't need the further review, and maybe it will look at what is happening and say, oh, we're caught in a loop, we're oscillating, we're having reviews that trigger other reviews [...]

> I think I actually like this being all part of one feature because conceptually this is all under the same umbrella of process improvements and making sure that we are implementing things efficiently and not going in circles, et cetera, et cetera. So yes, please go ahead and fold all of this into the same new feature


## Amendment 1 (2026-10-10, a later session)

The hourly check measured feature 343's run: 141 check dispatches, 94 of them pop-up checks, and of the 35 second rounds
18 ran on pop-ups whose checked words had not changed. The cause: a pop-up's checks are still owed by a whole page - the
triage names a pop-up and every check of it is owed, so a findings edit re-owed its depiction and a drawing edit re-owed
its research checks (the kept triage, 14 of 61 units); and any edit to a pop-up re-owes its depiction. The session proposed
owing a pop-up check only where a changed block is one it reads, and, separately, `make speckit-todo` showing a feature's
state in the session clones (the GM had found the research features shown untouched though their specs and plans were
accepted in the research clone). The GM:

> yes to each of those possible changes, though for the in-progress features you can probably limit yourself to clones with active sessions, if it helps performance.

## Amendment 2 (2026-10-11, the same later session)

The hourly check found feature 343's page session asking the round arbiter once per pop-up per check as a batch of pop-ups
reached the round cap together (45 pop-up rulings, 44 of them `accept`), and some bundles reaching the arbiter with no
round history ("no Rounds section"). The session proposed one ruling for a batch reaching the cap together, with per-pop-up
exceptions, and to look at the bundle defect. The GM:

> Yes, it does seem like a whole batch of pop-ups reaching the round cap at once should get a single ruling. because they are likely to be related. And that does sound like it would be more efficient. And then yes, please also do look at that bundle defect.

## Amendment 3 (2026-10-11, the same later session)

The hourly checks were stopped and the GM asked where 374's time went. Measured from its transcript (1,574 tool calls):
model time 6.5 h, tool time 6.25 h, of which timing runs 2.5 h, the record and claims tooling 59 min (`modal-bundle`,
`claims-owed`, `claims-bundle`, `record-owed`, `check-bundle` - each about 6 s on its real delta, run hundreds of times),
`make hooks-test` 39 min (19 runs). Of the pop-up checks, about 20 of 374's units and 21 of 352's reached the round cap and the
round arbiter accepted nearly all; every second and third round was owed because the pop-up changed - the edits the last
round's checks proposed, applied - and `modal-form` proposed edits in nearly every second round. The session said a fuller fix
would order the checks, and asked to look at more data first. The GM:

> Yes please - the round 3 caps indicating "one structural cause" is definitely worth fixing as well; you mentioned that a fuller fix would order the checks, but that you wanted to look at more data before moving forward.  Do we have enough to be able to do that now?  Even if not then perhaps it's worth trying to make the speculative fix and measuring it afterwards.
>
> Either way, yes it sounds like `modal-bundle` and `check-bundle` and `claims-owed` and `record-owed` are all worth improving and it osunds like that could all be sped up enormously.  And I agree we could skip `hooks-test` could be skipped when not touched which it sounds like would help well.  So yes, please do all of that as part of amendments to 375.
>
> As for timings being thbe biggest single cost, I suspect it might make sense to relax some of the timing requirements, but let's talk about that after you make the other changes.

The timing requirements are not part of this amendment: the GM will discuss them after it lands.
