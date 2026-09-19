# Research - 255 cheaper checks by tooling

Every seeded run of this feature, one row each (SC-001). Method is feature 251's R5 (`specs/251-tiered-subagent-
checks/measure/seeded.py prepare`, then `run_seeded.sh`: a headless session in a detached worktree at the commit the
recorded run saw, the clone's current agent files copied in, hooks off). "Weight" is 251's R1 scale - fresh input
6.25, cached input 0.5, output 25 per million tokens, a relative weight and not a bill. Every figure below was
observed 2026-09-19; method: each run's own `usage` block in its `run.json`, the recorded figures folded from that
run's transcript by `_agent_census.fold_usage`. The candidates as they were tested are commit `4c0486d5`.

A control, where one was run, is the SAME case in the SAME headless setting with the agent file as it stood before
the candidate: a headless session is a main thread and not a subagent, so its turns and weight are not the recorded
run's (251 R5 said so), and only a same-setting control isolates what the candidate did.

## R1 - `source-applicability` handed its entries (FR-002, T01): NOT ADOPTED

The candidate: `make source-entries KEYS=...` (`scripts/_source_entries.py`: per key the registry entry, and every
footnote citing it with its passages and its assertion) appended to the prompt, and a "step 0" in the contract -
start from the listing, open the registry only for a key it lacks. Cases: the single-key Shanghai county-wall run
(`79288e26/13fe2f10`, recorded findings below) and a CLEAN two-key slice of the dike-pond run (`17e1cafe/e54ec63f`
cut to `fao-ac264e-ch9` and `qimin-yaoshu-yangzhu`, both recorded ACCURATE and HONEST; its recorded weight is the
six-key run's 3.68 pro rata, 1.23).

Recorded findings on the Shanghai case: limits MISSING two - (a) the 1753 dredging is ONE event, so "dredging as
maintenance" rests on a single instance; (b) the article gives TWO moat lengths (1,500 and 1,620 zhang); plus (c)
"after it silted" called the session's inference, and (d) fn-37's anchor not found as quoted. The control and the
first candidate run both found the page DOES carry a silting sentence and both wordings of the dredging, so (c) and
(d) are the recorded run's own errors and are not scored.

| run | contract | result against (a) and (b) | limits verdict | turns | weight |
|---|---|---|---|---|---|
| recorded | as it stood | (a) hit, (b) hit | MISSING | 13 | 2.44 |
| control | as it stood, no listing | (a) hit as "one instance ... dredged this moat once", (b) hit | MISSING | 22 | 2.78 |
| candidate, run 1 | step 0 | (a) MISSED; (b) seen and called "optional rather than owed" | **HONEST** | 5 | 0.73 |
| candidate, run 2 | step 0 | (a) MISSED, (b) MISSED; a different limit raised (the quoted sentences are uncited within the article) | MISSING, not the recorded ones | 3 | 0.70 |
| candidate, revised step 0 ("the listing saves you the registry, never the source") | revised | (a) MISSED; (b) listed as a limit of the source, not as missing from the write-up | **HONEST** | 4 | 0.80 |
| clean slice | step 0 | recorded HONEST for both keys; the run called each MISSING one minor limit | two false alarms | 5 | 0.40 (1.23 pro rata) |

**Verdict: NOT ADOPTED** by FR-001 - the candidate missed a recorded finding on every one of its three runs of the
findings case, and the same-setting control did not. It is the cheapest check this feature measured (about a
quarter of the control) and the saving is real; what it buys it with is the judgment. The runs that were handed
their entries took 3 to 5 turns where the control took 22, and the limits they missed are the ones a reviewer
reaches by going back over the source against each sentence of the write-up - which is what the turns were. On
this agent the turns are not only cost. The contract is as it was; the script, its test and the make target were
removed (they are in `4c0486d5`) so that no later session follows a header that says "run BEFORE
source-applicability". Not to be retried blind: a variant worth its price would have to keep the agent's passes
over the source while cutting only the registry paging, and the revised step 0 above, which said exactly that in
words, did not do it.

## R2 - a scoped `record-format` or `quote-check` handed its text (FR-003, T02): NOT ADOPTED, both agents

The candidate: `make record-prepass ... SECTION=` also printing THE TEXT IN SCOPE (the section's visible text and
its numbered source lines), and a contract step saying that for a scoped check the handed text - or, for
`quote-check`, the `NOTES=`-scoped report - is the reading list and the page is opened only to settle a doubt.
Cases are 251's R5 and R7 cases, re-prepared from the same transcripts. For both agents the same-setting reference
is 251's own run of the same case at the same tier WITHOUT the candidate (R7's opus / medium `record-format` runs;
R5's opus / medium `quote-check` run), which is what a control would have been.

| agent, case | recorded findings (observed 2026-09-19; method: read from the recorded reply and the run's own reply) | the candidate's result | turns: 251's run -> candidate | weight: recorded / 251's run / candidate |
|---|---|---|---|---|
| `record-format`, one homesteads section (`881af52a/abea4bd5` cut to "The garden's sun, and how far the windbreak shades") | 2 stray `</strong>`, a sentence contradicting its clause, a fetch-verdict phrase ("the pages read record"), `the frame`, `clump` | both tags and the contradiction hit; **the fetch-verdict phrase, `the frame` and `clump` MISSED** (it raised `(unsourced)` and `shoulder month` instead) | 11 -> 7 | (7.99, two pages) / 2.05 / 1.29 |
| `record-format`, towns scoped re-check (`79288e26/8861f73e`, all nine sections the diff touches handed over) | a prose session note ("the city-tier research validated"), the one history passage (the 450 ft avenue), `ward` | the session note and the history passage each SEEN and DISMISSED, `ward` not listed: **all three MISSED**. The run says it opened neither page | 8 -> 5 | 3.33 / 2.13 / 1.51 |
| `quote-check`, urban-features fn-90..98, 102..108, 113 (17 notes of `881af52a/a8589cb7`) | undisclosed PARTIAL at fn-94 and fn-95 | fn-94 PARTIAL hit; **fn-95 under-called SUPPORTS** - "Dingbian, named alongside Xingcheng, is not in these passages - presumably its own mark": the run saw the gap and, not having read the page, assumed it away | (26, both slices in one run) -> 10 | (10.47, 102 notes) / 2.98 both slices / 1.69 |
| `quote-check`, capitals fn-235..240 (6 notes, same run) | fn-237 NOT-ON-PAGE at its link, and "23" in no quote | both hit (DOES-NOT-SUPPORT for the clause, the right juan located) | -> 10 | - / (in the 2.98) / 1.61 |

**Verdict: NOT ADOPTED for either agent.** `record-format` missed three of six and three of three; at about two
thirds of the weight of 251's run that is a saving bought with exactly the findings R7 kept the agent on Opus for.
`quote-check` under-called one of its three support findings for the very reason the candidate exists - it did not
read the page - and was not cheaper either: two scoped runs weighed 3.30 together against 2.98 for 251's single run
of both slices, because each run pays its fixed context and its ten turns again. Both contracts, the script, its test
and the make target are as they were before the feature. (The quotation halves matched the script in every run, as
in 251.)

## R3 - independent tool calls go out together (FR-004, T03): ADOPTED, in the seven contracts

The line, under each contract's opening paragraph: "Send the reads, greps and fetches you already know you need in
ONE message, and do not spend a turn on a single lookup whose result does not decide the next one." Tested on the
twin (`spec-fidelity-verify`, opus / high, its pinned tier) on 251's two later rounds, each run twice in the same
headless setting - with the line, and with the contract as it stood.

| case | recorded (`spec-fidelity`, as a subagent) | control: the twin without the line | the twin with the line |
|---|---|---|---|
| feature 250 round 2 (`79288e26/3fc3f084`): CHANGES REQUIRED, two items - FR-004's unrequested scope; its added half has no success criterion | 7 turns, 1.01 | both items, 10 turns, 0.95 | both items, **7 turns, 0.69** |
| feature 250 round 2 after the fix (`79288e26/427f9b4c`): FAITHFUL | 3 turns, 0.54 | FAITHFUL, 9 turns, 0.71 | FAITHFUL, **6 turns, 0.58** |
| total | 10 turns, 1.55 | 19 turns, 1.66 | **13 turns, 1.27** |

**Verdict: ADOPTED.** Nothing missed on either round, no false alarm on the clean one, and about a quarter less
weight than the same agent in the same setting without the line (a third fewer turns). Against the recorded runs the
total is lower too, though the clean round alone is not (0.58 against 0.54 - a headless main thread takes more turns
than a subagent did on a three-turn job, with or without the line). The line is now in `spec-fidelity.md`,
`spec-fidelity-verify.md`, `source-applicability.md`, `record-format.md`, `quote-check.md`, `settlement-review.md`
and `source-reader.md`, in the same words; `perf-audit.md`, `building-review.md` and `size-audit.md` are untouched
(FR-004).

**What R1 to R3 say together.** The two candidates that cut what a check READS both lost findings, and in each the
runs got shorter - 22 turns to 3-5, 11 to 7, 8 to 5 - while the one candidate that cut TURNS WITHOUT cutting what is
read lost nothing. 251's R9 priced a check as turns times context and pointed at both levers; on these agents the
context is not only cost. What a judging agent reads on its way to a finding is part of how it finds it.

## R4 - `source-reader` greps saved pages (FR-006, T04): misses nothing, costs more - the GM's decision

The candidate: `make source-pages OUT=<dir> URL=...` (`scripts/_source_pages.py`: each pointer fetched once by
`_quote_verbatim.Pages`, its full visible text saved one sentence to a line, a manifest `pointer | file | state`),
the manifest appended to the prompt, `Grep` added to the agent's tools, and a step 0 - grep the saved file for the
claim's terms, read only around the hits, fetch only what the script could not reach. The URLs were taken from each
recorded prompt by a regular expression, not by a model. Cases: 251's three (`a238c6db` 08-28, `a800a049` 08-29,
`ada2e102` 09-12). Recorded weights here are folded today from each transcript at R1's rates (0.60, 0.69, 0.92); 251's R5 table
prints 0.24 and 0.28 for the first two and the same 0.92 for the third, and that difference was not traced.

| case | pointers saved | recorded findings (observed 2026-09-19; method: read from the recorded reply and the run's own reply) | the candidate's result | turns rec -> new | weight rec -> new |
|---|---|---|---|---|---|
| 08-28 (25 claims) | 8 of 9 (one TLS timeout) | CONTRADICTED: the clause "except those who are not engaged in agricultural or fishing work" is "not in the text anywhere near it"; "boats determine the village plan" READ | **the recorded CONTRADICTED was wrong, and the candidate corrected it**: the sentence is on the page verbatim, clause and all (the saved archive.org text, line 2381, checked by hand), so READ; "boats determine..." READ verbatim; one NOT-FOUND the recorded run also gave | 4 -> 16 | 0.60 -> 0.69 |
| 08-29 | 0 of 1 (403) | CONTRADICTED (the privy is not sited by wind) | CONTRADICTED, hit - by other sources, the paper unreachable as in every re-run of this case | 15 -> 31 | 0.69 -> 0.92 |
| 09-12 (clean) | 2 of 2 | two partial passages: the pigsty dike's 5-10 m width; pond water on the dike crops | **both found**: "The width of the dikes for pigsties, cow sheds piping, or traffic should range from 5 to 10 m" and the "fertigate" sentence - the width is the passage Sonnet missed three times and Opus at medium once (251 R7) | 7 -> 20 | 0.92 -> 1.20 |
| total | | | nothing missed; one recorded false alarm removed | 26 -> 67 | 2.21 -> 2.81 |

**Verdict under FR-006's two-axis rule: it misses nothing AND costs more (about a quarter more), so the agent is
left as it was and the measurement goes to the GM as a quality-for-cost decision.** What the quarter buys: the
recorded 08-28 finding was a fetch extract's omission reported as the source's - a CONTRADICTED that would have had
a session rewrite a correct sentence - and the width passage is found on the first try. It is also far cheaper than
251 R8's whole-page reading of the same three cases (5.48 in all by R8's table: 3.73 for the reader, 1.75 for the
fetcher). Where the script reached nothing
(08-29) the candidate is simply the old procedure with more turns. `make source-pages`, its script and its test stay
(they are the means of the decision either way, and useful to a session that wants a page rather than an extract);
the contract's step 0 and the `Grep` tool are in commit `4c0486d5` plus the step's text in this feature's history,
ready to restore on a yes. One mechanical note: make keeps only the last of a repeated `URL=`, so several pointers
are passed as `URLS="<u1> <u2>"`.

## R5 - what fills a subagent's fixed context (FR-007, T05)

Probes: `measure/probe.sh` - a headless Haiku session dispatches one trivial inline agent (`--agents`, its prompt
"Reply with the single word OK"), hooks off, and the SUBAGENT's first assistant message is read from its own
transcript for its input (fresh + cache-creation + cache-read). One thing varied per probe. The "repo copy" is a
detached worktree of this clone in the scratchpad: its path is its own project, so no memory index loads there.

| probe | subagent's first-turn input (tokens) | delta |
|---|---|---|
| an empty directory, tools `Read` | 2,009 | the floor: the subagent system prompt, one tool, the prompt |
| repo copy WITHOUT the root `CLAUDE.md`, tools `Read` | 2,447 | +438: the repository itself (git status, environment) |
| repo copy WITH `CLAUDE.md`, tools `Read` | 7,495 | **+5,048: the project `CLAUDE.md`** (17.6 k characters) |
| the same, with `--append-system-prompt` (the standing-authorizations file) | 7,500 | **+5: the appended system prompt does not reach a subagent** (it adds 567 to the MAIN thread's first turn) |
| `/diagram`: `CLAUDE.md` and the session memory index, tools `Read` | 14,146 | **+6,651: the memory index** (21.9 k characters; the subagent's transcript shows one `instructions` attachment of 40 k characters carrying both files, which is the direct evidence that a subagent is handed the index) |
| empty directory, tools `Read, Grep` | 3,066 | +1,057 for `Grep` |
| empty directory, tools `WebFetch, WebSearch, Read` | 3,032 | +1,023 for the two web tools |
| empty directory, tools `Read, Bash, Grep, WebSearch, WebFetch` (`settlement-review`'s line) | 6,203 | +4,194 over `Read` alone |
| empty directory, tools `Read, Bash, WebSearch, WebFetch` (the same without `Grep`) | 6,203 | **0: beside `Bash`, `Grep` costs nothing** - the harness does not send it (and no agent that has `Bash` has ever called it: 0 of 4,798, 3,274, 208 and 105 tool calls) |
| empty directory, ALL tools (no `tools:` line) | 11,163 | +9,154 over `Read` alone: what a tools line saves an agent |

A leg that could not be run as planned: copying the index into the scratch copy's own project memory directory
changed nothing (7,495 both ways) - the harness did not read a memory directory created by hand under that path -
so the index's delta is the `/diagram` leg's, as the plan specified, with the transcript attachment as its check.

**So a real check's 47-67 k first turn (251 R9) is, in order: its own contract (`settlement-review`'s is 48 k
characters, roughly 12 k tokens) and whatever nested `CLAUDE.md` its reading pulls in, then the memory index
(6.7 k), the project `CLAUDE.md` (5.0 k), its tools (1-4 k) and the floor (2 k).**

**The two trims.**
- *The memory index*: every entry kept, each hook cut at a word boundary to at most 120 characters - 18 of 111
  hooks were longer; 754 characters removed. Re-probe from `/diagram`: 14,146 -> 13,937, **209 tokens saved** on
  every subagent's first turn and on every session's. That is all this trim can give: the hooks were already short,
  and 10.1 k of the index's 21.1 k characters are the titles and file links, which the trim may not touch.
- *An agent's tool list*: the census of every recorded run against every `tools:` line found three tools never
  called and not named as a tool in their contract - `Grep` in `settlement-review`, `spec-fidelity` and
  `escalation-check`. The re-probe above says removing it saves **0 tokens**, because all three have `Bash`; and
  `spec-fidelity` and `escalation-check` tell the agent to "grep", which it does through `Bash`. No tool line was
  changed: a trim that saves nothing is only a difference to explain later. Every other listed tool is called.

**Reported to the GM, not cut (FR-007):** the memory index is the largest removable-looking item in a subagent's
fixed context - 6.4 k tokens after the trim, paid on every turn of every check, for an index none of the checks
consults - and the project `CLAUDE.md` is next at 5.0 k. Whether a subagent should receive either is the harness's
behavior and the GM's call; no check's contract refers to the memory index at all.

## R6 - `settlement-review` measures in one call and carries a shorter contract (FR-005, T06): NOT ADOPTED

The candidate: `make review-facts MAP=<pool map>` (`scripts/_review_facts.py`: the artifacts present and their age,
the manifest's `meta` and every key with its count, the per-key DELTA against a git ref, every label with its
count, the notes' headings and the "Settled by the GM" section) appended to the prompt; a Tooling paragraph telling
the agent to start from it; and the `Validated examples` section (7.9 k characters of a 48 k contract) moved
verbatim to `docs/settlement-review-examples.md` behind a pointer. Cases: two recorded reviews whose subject is
reproducible from history - Kuwabata after feature 233 (`17e1cafe/a18e043a`, the tree at `240ad0fe`) and Sawada
with Mizuguchi at feature 230's pass 14 (`012f2cee/5fd7e2f3`, the tree at `17ee271c`). The renders are gitignored,
so each map was regenerated inside its worktree by that commit's own engine (`make map`) before the run.

| case | recorded ERRORS (observed 2026-09-19; method: read from the recorded reply and the run's own reply) | the candidate's result | turns rec -> new | weight rec -> new |
|---|---|---|---|---|
| Kuwabata / 233 | (1) the research entry's 6.5 m "shared bank" is one pond's two collars summed, the real dike being 13.2 m; (2) the notes carry no entry for feature 233 | **both MISSED** - the run's CONFIRMATIONS say the record "was brought into line with the drawing". It raised a different error (three sties seated on a corner chamfer) and three nitpicks | 40 -> 48 | 4.24 -> 5.37 |
| Sawada + Mizuguchi / 230 pass 14 | (1) Mizuguchi's board gave up 3-4 farmhouses of traffic for clearance it did not need; (2) Sawada's notes state a 6.6 ft clearance the drawing contradicts | (1) **MISSED** - the run confirms "Change 2 did not cost either board its traffic seat"; (2) hit, filed as QUESTIONABLE, and sharpened (the plank stood under the crown at that commit). A different error raised (Mizuguchi's caption lies across the connector) | 41 -> 33 | 4.40 -> 3.94 |
| total | four | one of four hit | 81 -> 81 | 8.64 -> 9.31 |

**Verdict: NOT ADOPTED** - three of four recorded errors missed, and no saving: the same 81 turns and more weight.
The listing did not shorten a review; the agent still asked the manifest its own questions, which are about the
delta in hand and not the inventory (251 R9's "39 Bash calls" are judgment-specific measurements, not an opening
ritual a script can pre-answer). Two honest limits on reading the misses as the candidate's doing: no same-setting
control was run (at about 4.5 units a run it was not bought), and a review's findings vary from pass to pass more
than any other check's - both runs found real-looking defects the recorded passes had not. And one confound: the
current contract's FIRST STAGE names make targets that do not exist at those old commits, and both runs spent turns
discovering that. None of it rescues the candidate under FR-001: it missed, and it was not cheaper. The contract
is as it was apart from R3's line; the script, its test, the make target and the `docs/` file are removed (the
script and test are in commit `8d2ebf64`). Moving the examples alone is worth about 2 k tokens of a first turn near
50 k, under one percent of a run, and is not worth a second test at this price.

## What the feature found

| candidate | verdict | what it would have saved (observed 2026-09-19; method: the weights in the tables above) | what it cost |
|---|---|---|---|
| R1 entries handed to `source-applicability` | NOT ADOPTED | about 70% of a run | the recorded limits, on three runs of three |
| R2 scoped text for `record-format` / `quote-check` | NOT ADOPTED | a third of a `record-format` run; nothing for `quote-check` | three of six and three of three findings; one under-called support verdict |
| R3 the batching line | **ADOPTED**, seven contracts | about a quarter of a later review round (a third of its turns) | nothing |
| R4 saved pages for `source-reader` | the GM's decision (FR-006) | nothing - it costs about a quarter MORE | nothing missed; one recorded false CONTRADICTED corrected, one always-missed passage found |
| R5 fixed context | measured; the index trimmed by 209 tokens; no tool trim exists | - | - |
| R6 `review-facts` and the moved examples | NOT ADOPTED | nothing | three of four recorded errors |

Total spent on seeded runs: 26.6 weight units over 18 runs (the sum of the weights in the tables above), and twelve
Haiku probes.
