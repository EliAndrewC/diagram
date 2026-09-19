# Where this feature comes from

A conversation on 2026-09-19 in the session "Diagram research". The GM asked a question, the session
answered with a proposal, the GM asked a second question, the session extended the proposal, and the GM
approved the whole. The GM's three messages are below verbatim; the session's two proposals are
summarized between them, because the GM's "this" in the third message refers to them.

## The GM's first message

> Much of our work involves subagent checks. I have specified that all of our subagent checks should use the Opus model. However, a friend of mine recently told me that he believes that adversarial subagent checks, which are intended to find issues with something that the main model has done, are actually okay to be done with Sonnet rather than with a more powerful model such as Opus. What is the best practice on this? I guess all of this is rapidly changing, so the best practices are a little bit tricky to distill. But I wonder whether the research that we are doing could be done much more efficiently and with less token usage without a loss of quality with different levels of models involved. I'm a little reluctant to use a less powerful model like Sonnet for things like distilling research down to its conclusions, but it occurs to me that it probably is a perfectly fine model to use to do what are functionally mechanical checks, such as making sure that a quotation excerpt does accurately quote the text in question. Things like that. This could also apply to some of the subagent checks that we do on our maps themselves. Though I think that things involving judgment calls should always be done with a more powerful model such as Opus even if we do not use the most powerful model such as Fable. Because our usage of Fable is simply not sufficiently available which is to say I don't have enough of it to spare to do on every possible thing. Please take a look at all of the subagent checks that we have in this repo and then make some recommendations about which models should be used for each of them. Based on your understanding of best practices and what those models are capable of and which checks require more powerful models with better judgment and which checks are closer to being mechanical such that we could rely on a less powerful model. Thanks.

## The session's first proposal (summarized)

Tier each agent by what a silent false PASS costs and by whether its verdict can be checked against
something concrete. Per agent:

| agent | model | why |
|---|---|---|
| `record-format` | Sonnet | pattern spotting on visible text; a miss is cosmetic; the session applies every proposal anyway |
| `source-reader` | Sonnet | the biggest reader of web pages, so the biggest saving; fetch, quote, compare; `quote-check` runs behind it; test it before committing |
| `quote-check` | split | the VERBATIM and READABLE checks belong in a script, not in any model (a model is unreliable at character-for-character comparison - a hyphen against an em-dash, "colour" against "color"); Support, translation faithfulness and grounds-note misuse are judgment and stay on Opus |
| `entry-drift` | Opus | telling maintenance from a moved finding is judgment; a false IN-STEP leaves a wrong modal in front of the reader; tiny inputs |
| `source-applicability` | Opus | pure judgment; gates numbers before they reach a map |
| `size-audit` | Opus | converting pixels to feet is arithmetic; researching real-world sizes independently is not |
| `settlement-review`, `building-review` | Opus | visual and form judgment |
| `spec-fidelity` | Opus | weighs intent against the GM's own words; gates a push |
| `escalation-check` | Opus | pure judgment, small inputs |
| `perf-audit` | Opus | runs counterfactuals and writes a committed audit record; rare |

Two other levers: reasoning effort set in the agent file; and "test before trusting" - run the Sonnet
version against entries with known findings (the 12 drifted modals of feature 232, past CONTRADICTED
verdicts) and count hits and false alarms. What the change would touch: `tests/test_agent_models.py`
becomes a per-agent map; the "on Opus like every subagent check" line in several agent descriptions, in
`CLAUDE.md` and in the 2026-09-07 memory; ad-hoc readers such as the feature 202 translators could
default to Sonnet.

## The GM's second message

> Oh yeah, good point on the effort level. I hadn't thought about tuning that as well. I do indeed want the split for the quote check, and indeed to split out anything that can be split out into a smaller model, but before we do any of that work, can you please also weigh in on what effort level you think each of these tasks and agents should have? And even whether it would make sense in some cases to split a subagent check into multiple checks where one of them is a higher effort level than the other, even if they are using the same model. Again, I am not sure what the best practices are here, but this seems worth evaluating in order to conserve tokens. Thanks.

## The session's second proposal (summarized)

Effort changes thoroughness as well as thinking depth, so the lowest setting is only safe when a script
does the listing and the model judges the items handed to it. Per agent:

| agent | model | effort | notes |
|---|---|---|---|
| verbatim and readable check | script | none | the mechanical part split out of `quote-check` |
| `quote-check` remainder (support, translation, grounds-note misuse) | Opus | medium | a script hands it footnote-and-assertion pairs |
| `record-format` | Sonnet | medium | a script pre-flags the obvious session-note patterns (`Grounds:`, task ids, fetch verdicts, module paths); the model confirms those and handles vocabulary and history |
| `source-reader` | Sonnet | high | its thinking is small next to its page input |
| `entry-drift` | Opus | medium | two short texts, one verdict |
| `escalation-check` | Opus | medium | small input, a rubric of three tests |
| `source-applicability` | Opus | high | |
| `size-audit` | Opus | high | move the pixels-to-feet table into a script and hand it in |
| `building-review` | Opus | high | |
| `settlement-review` | Opus | high | a medium setting for narrow re-checks could come later, only after measuring |
| `perf-audit` | Opus | high | fires too rarely to split |
| `spec-fidelity` first round, exception check, plan review | Opus | high | |
| `spec-fidelity` later rounds | Opus | medium | a second agent file; `review-round-hooks.sh` already rewrites later rounds and could route them to it; the later-round instructions stay strictly about the fixes and the diff |

Splits that do NOT pay and were declined: a translation-only checker, a lighter `perf-audit` for small
increases, an `entry-drift` split. "Measure first": task zero is a per-agent token census from the
session transcripts (input, output, run count), which could reorder the plan; the seeded-fault test then
checks that each downgraded agent still catches known findings.

## The GM's third message

> That sounds great. Please claim a feature number and write the spec and then implement this from start to finish. Thanks.

## The GM's fourth message (mid-implementation, on the seeded runs)

> How much research are you rechecking here exactly? I mean, I understand that in order to test out these agents, you do need to run them on some amount of actual research. But you're not doing a pass over everything that we've ever done or anything silly like that, are you?

The session answered with the run list and proposed cutting the three large cases to slices. The GM:

> Yes, that seems fine. Definitely do a trimmed batch. And since batch one is already small, then you can let it finish. But yes, in general, please be mindful that we are trying to conserve tokens here. So redoing old work is only useful insofar as it does give us sensible measurements about whether the defaults that we are choosing for tuning these different checks are actually what we want. So again, I'm not objecting to you doing this. I just want to make sure that we're careful about it. Thanks.

## The GM's fifth message (after the first misses were reported)

> Thanks, please keep going with the checks and then eventually with the scoring and updating the docs to the tiers that pass. then we can look at what other experiments we need to run on the specific checks that failed or otherwise scored poorly to see what other different models and effort levels. Will actually be suitable to our needs.

## The GM's sixth message (after the close of 251 was reported, with R5's candidate experiments listed)

> I agree that each of the follow-up experiments is worth running, so go ahead and run all of them. Thanks.

(The same message chose the refusing hook, which became feature 252; its words are in that feature's `request.md`.)
