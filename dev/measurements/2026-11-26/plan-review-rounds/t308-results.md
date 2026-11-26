# What each later plan review round was owed for (feature 451 T308, measured 2026-11-26)

Method: every `spec-fidelity` subagent transcript of the coordinating session (`subagents/agent-*.jsonl`, 734 of them) whose prompt
opens `MODE 4: PLAN REVIEW` for feature 451, started from 2026-11-24T00:00Z to 2026-11-26T19:42Z (`t308-index.py`, then
`t308-rounds.py`): its task, its minutes (first to last line of the transcript), the verdict `make plan-verdict` printed or the reply
stated, the section as the bundle held it - cut at the prefix whose SHA-256 is the digest the block's header states, exact for 125 of
the 132 task rounds - and the verdict JSON. A round is "later" when an earlier round of the same task (or the same batch of blocks)
is in the corpus. Each later round was classed by hand from the round before it: its NOT LEGITIMATE rulings or its reply, and the
section's diff between the two rounds (`t308-show2.py` prints both; `t308-class.py` holds each class and prints the tallies).

The corpus: 135 rounds (132 of one task's section, 3 of changed blocks) over 79 units, 373 minutes in all, median 2.73 minutes a
round; 38 units took one round, 32 two, 7 three, 1 five and 1 seven. 56 rounds were later rounds, 169 minutes. Cross-check: the
review ledger holds 121 MODE 4 rows for 451 on those dates; 13 of the 135 rounds recorded no verdict (a NOT-REVIEWABLE return, or a
record refused), which leaves 122, one more than the ledger. Left out: T298's round 2, in flight when the corpus was frozen; an earlier unreviewable return of T246 that its one round here
speaks of; the
449 and 452 reviews of those days; `spec-fidelity-verify` (none was a 451 plan review).

| class | what the round was owed for | rounds | minutes | median | mean |
|---|---|---|---|---|---|
| (a) | a found-and-left item with no filed task id or order | 4 | 11.0 | 2.66 | 2.74 |
| (b) | NOT-REVIEWABLE: an unlabeled figure, or the GM's words missing from request.md | 8 | 40.6 | 4.69 | 5.08 |
| (c) | the section edited after its CLEAR | 16 | 31.5 | 1.15 | 1.97 |
| (d) | a real objection to a decision | 26 | 78.6 | 3.08 | 3.02 |
| (e) | other: the round before could not be recorded, the section edited while it was reviewed | 2 | 7.4 | 3.71 | 3.71 |

Inside the classes:

- (a), every view: 4 rounds blocked on that alone (T250, T305, T309, and T285's round 5 - its round 4 blocked on one item, a
  path-spelled git passing the guard, left with no filed id, and the cure it offered and the builder took was the filing, T295), 2
  more where an unfiled item blocked beside a real objection (T295, T316, counted under (d)), and 2 of (c) where the only edit
  after a CLEAR was the filed ids written in (T251 r3, T265 r3): 8 rounds, 23.0 minutes, whose root cause was an id nobody had
  filed. All but T316 predate 451 T289 (a builder files its own). T285's round 5 was first classed (d), which made this 3 rounds
  alone and 7 in all; re-read 2026-11-26 from round 4's ruling and round 5's reply, and `t308-class.py`'s table moved with it.
- (b): the GM's words missing in 6 (T243, T245, T233, T254 alone; T235 and T285 with a figure too), a figure alone in 2 (T259,
  T284). The 8 NOT-REVIEWABLE rounds themselves took another 20.6 minutes. Three of the six quoted him on the task's own line
  of tasks.md (T243, T245, T285); three cited him by reference (T233 `docs/gm-rulings.md`, T235 "the pre-filter request", T254 an
  approval under another heading). The figures: "about 70k tokens" (T235), "the gate's 20-odd minutes" and "the 634-transcript
  pass" (T259), "21 of 22 code builders", "six more profiles" and "the largest count of builders ever run at once" (T285),
  "589 s" and "load median 42" (T284).
- (c): a real change (a decision gained, scope widened, a mechanism restated) in 9 rounds, 20.6 minutes; the filed ids in 2, 4.2;
  a touch-up that changed no decision (a figure's label added, a restatement, an evidence sentence) in 3, 1.9 (T207, T243 r7,
  T228); a caveat the CLEAR review itself asked for in 1, 3.9 (T284 r3); results restated in 1, 0.9 (T272).
- (e): 8 of the 135 rounds had `make plan-verdict` refuse their record ("it changed while it was being reviewed"); 6 recovered
  inside the round, 2 cost a round each.

## What today's `make decide` already refuses (the replay)

`t308-replay.py` writes each digest-exact section into a scratch tree with today's request.md and tasks.md and runs HEAD's
`l7r-gate plan decide` on it (124 sections; 108 pass, 16 are refused, every one on the deferral form alone - an artifact of the
scratch tree's tasks.md for 12, and T233's and T265's sections, which were dispatched under `DEFER_FORM_OK`). None of the rounds
before the 8 (b) rounds is refused: every figure above passes the lint, and no rule reads the task line. The (a) items of T250,
T305, T309 and T285 stood in a decision's own words ("left"), outside the found-and-left answer the deferral lint reads.

## The candidate rules, replayed for false refusals

- The GM's words quoted on the task's own line, absent from request.md. BUILT, and then replayed AS BUILT (`t308-d1replay.py`:
  `l7r-gate plan decide` over each of the 77 tasks' round-1 sections, the task lines of today's tasks.md and tasks-done.md, and
  request.md twice - as committed before the task's first round, and as the task's surviving review bundle holds it, the last
  round's). Against the committed request.md it fires on 11 tasks; against the bundle's on 2. Read with each round-1 reply:
  - 6 are what the rule is for, the round-1 review itself saying request.md lacked his words: T243, T245 and T285 (the three of
    the six (b) rounds), T298 (its round 1 returned unreviewable on them; its round 2 is outside the corpus), T316 (round 1 said so
    and judged without them) and T246 (its one round in the corpus says "the rebuilt bundle fixed what the first return flagged:
    `request.md` now has the T246 section" - an earlier return this corpus does not hold).
  - 3 are the replay's artifact, not refusals a builder would have met: T244, T259 and T284, whose words stood in the worktree's
    uncommitted request.md. T244's bundle is its round-1 bundle and holds them; T259's and T284's are a later round's, and their
    round-1 replies named no missing words (T284's names "the GM's words in `request.md`").
  - 2 are FALSE REFUSALS, firing against the bundle's request.md too, on a section whose review raised nothing about those
    spans: T241 (the line's 'watch the cascade both ways', which request.md does not hold in those words; CLEAR in one round) and
    T235 (the hook's own lines 'Nothing is waiting on you.', quoted within reach of "the GM" and not his). Each is cured by the
    refusal's own second remedy, correcting the task line. 2 of 77 tasks.
  The first replay (`t308-gmwords.py`, a Python sketch of the rule, committed request.md only) reported T243, T245, T285 and "8
  other tasks, where the words were in the worktree's uncommitted request.md (T244, T246, T259, T284, T298, T316) or the script
  misread" (T233, T265): that reading was checked for none of the six and is wrong for T246, T298 and T316, and the sketch missed
  T241 and T235.
- A count with a `k` or `M` suffix, and "N-odd <unit>" (`t308-figures.py`, the 124 sections): one sentence each, T235's and
  T259's, no other. BUILT. Replayed AS BUILT afterwards, with the threshold's numeral taking the suffix (`t308-replay.py`'s
  `all_first()` on the tree's `l7r-gate plan decide`, compared section by section with the replay before the rules): of the 124
  sections both runs hold, the two rules newly refuse T235's and T259's first-round sections and no other.
- "N of M" as a count: 47 unlabeled sentences in 26 sections, of which the reviews objected to 1 (T285). NOT built: 46 false
  refusals for one round.
- A digest over the decisions rather than the section: none of the 132 sections holds a `**D<n> - ` line or a Decisions block, so
  there is no machine-readable decision to take a digest over, and of the 16 (c) rounds at most 5 (the touch-ups and the filed
  ids, 6.1 minutes) changed no decision. NOT built: an edit kept by rule could carry a decision.
- A placeholder answer refused (item 9 `<after the build>`): one section of 132 (T229). NOT built.

## The verdict across a typo: kept only once the reviewed section is committed

`status::task_current` keeps a CLEAR across a typo-scale edit (`sections::typo_only`) by comparing the section with its reviewed
text, and the only reviewed text it can reach is a committed version of plan.md (`History::section`): `record_task` keeps the
digest and no text. Proved 2026-11-26 by `status::tests::a_task_verdict_survives_a_typo_only_once_its_reviewed_section_is_committed`
(the real `record_task`, then `task_current` on four edits): with the reviewed section uncommitted, one respelled word voids the
verdict as a changed digit does; once it is committed, the respelling keeps it and the digit voids it. A builder's tree never
commits, so there every edit of the section owes a round. `make decide`'s notice says that; the tolerance is filed as 451 T337.

## Each later round

| task | round | start (UTC) | min | prior | class | what it was owed for |
|---|---|---|---|---|---|---|
| T202 | 2 | 11-24T00:19 | 1.47 | BLOCKED | (d) | D8 replace_all left as not a defect |
| T207 | 2 | 11-24T00:35 | 0.69 | CLEAR | (c) touch-up | a figure gained its label (observed, method) |
| T213 | 2 | 11-24T13:18 | 0.59 | CLEAR | (c) real | the Approach line restated the mechanism |
| T215 | 2 | 11-24T13:48 | 2.63 | CLEAR | (c) real | item 9 filled; Performance work yes -> no |
| T217 | 2 | 11-24T14:24 | 0.84 | BLOCKED | (d) | (c) an unprobed route passed |
| T219 | 2 | 11-24T15:56 | 0.87 | BLOCKED | (d) | D3 closed reader set |
| T220 | 2 | 11-24T16:22 | 1.09 | BLOCKED | (d) | no backfill of one row |
| blocks:T173-T178 | 2 | 11-24T18:06 | 1.56 | BLOCKED | (d) | blocks review: T223 deferral to T224 judged not legitimate (it had a filed id) |
| T236 | 2 | 11-25T06:50 | 2.42 | BLOCKED | (d) | D11 what STAGE= covers |
| T230 | 2 | 11-25T12:19 | 0.64 | CLEAR | (c) real | two decisions gained |
| T240 | 2 | 11-25T12:47 | 2.5 | BLOCKED | (d) |  |
| T237 | 2 | 11-25T13:11 | 4.19 | BLOCKED | (d) |  |
| T243 | 2 | 11-25T14:41 | 7.48 | None | (b) GM words | request.md held none of the GM's words for the task (they were on the task line) |
| T243 | 3 | 11-25T15:00 | 3.43 | BLOCKED | (d) |  |
| T243 | 4 | 11-25T15:26 | 6.88 | BLOCKED | (d) |  |
| T243 | 5 | 11-25T16:00 | 4.57 | BLOCKED | (d) |  |
| T243 | 6 | 11-25T16:14 | 0.7 | BLOCKED | (d) |  |
| T243 | 7 | 11-25T16:19 | 0.68 | CLEAR | (c) touch-up | restatement after CLEAR, no new decision |
| T228 | 2 | 11-25T17:35 | 0.58 | CLEAR | (c) touch-up | an evidence sentence added |
| T235 | 2 | 11-25T18:04 | 3.93 | NOT-REVIEWABLE? | (b) figure + GM words | "about 70k tokens" unlabeled; the GM's pre-filter request not in request.md |
| T235 | 3 | 11-25T18:25 | 4.18 | CLEAR? | (e) edited during review | round 2's record refused: the section changed while it was being reviewed |
| T245 | 2 | 11-25T18:58 | 6.69 | None | (b) GM words | "the GM's three sentences in tasks.md T245" not in request.md |
| T229 | 2 | 11-25T20:00 | 1.03 | CLEAR | (c) real | item 9 filled from its placeholder; one decision added |
| T232 | 2 | 11-25T21:26 | 1.45 | BLOCKED | (d) |  |
| T233 | 2 | 11-25T22:13 | 4.06 | NOT-REVIEWABLE? | (b) GM words | cited docs/gm-rulings.md and 449's request.md; not in this request.md |
| T248 | 2 | 11-25T23:11 | 4.55 | CLEAR | (c) real | a file split recorded as a new bullet |
| T253 | 2 | 11-26T00:05 | 3.82 | BLOCKED | (d) | a class fix's census unmeasured (FR-009) |
| T253 | 3 | 11-26T00:10 | 4.03 | CLEAR | (c) real | D3 gained a consequence; a garbled figure corrected |
| T257 | 2 | 11-26T01:07 | 1.13 | CLEAR | (c) real | found-and-left gained an item fixed here |
| T254 | 2 | 11-26T01:28 | 3.4 | CLEAR? | (b) GM words | "quoted in T254's line of tasks.md" not in request.md; the wrong D4 cited |
| T259 | 2 | 11-26T02:36 | 5.95 | NOT-REVIEWABLE? | (b) figure | "the gate's 20-odd minutes", "the 634-transcript pass" |
| T259 | 3 | 11-26T02:56 | 9.74 | BLOCKED | (d) |  |
| T251 | 2 | 11-26T04:43 | 4.57 | BLOCKED | (d) | fringe: a DEVIATION left (the remedy offered a deferral line) |
| T251 | 3 | 11-26T05:06 | 3.05 | CLEAR | (c) filed id | "Filed as T<n> by the coordinating session" became the ids |
| T263 | 2 | 11-26T04:46 | 4.33 | BLOCKED | (d) | a class fix's census method (FR-009) |
| T250 | 2 | 11-26T06:10 | 3.79 | BLOCKED | (a) | visible-text defects left with no filed id or order |
| T265 | 2 | 11-26T07:28 | 3.24 | CLEAR? | (e) edited during review | round 1's record refused: plan.md edited 3 minutes after the bundle |
| T265 | 3 | 11-26T07:54 | 1.16 | CLEAR | (c) filed id | "Not filed by this builder" became "Filed as T277/T276" |
| T268 | 2 | 11-26T12:55 | 0.94 | BLOCKED | (d) |  |
| T272 | 2 | 11-26T13:12 | 0.89 | CLEAR | (c) results | item 9's counts and a table row restated after a test moved |
| T292 | 2 | 11-26T15:00 | 3.55 | BLOCKED | (d) |  |
| T292 | 3 | 11-26T15:06 | 3.05 | BLOCKED | (d) |  |
| T285 | 2 | 11-26T15:05 | 3.12 | BLOCKED | (d) | D4b land-batch releases nothing; D9c the cache budget may empty pool trees |
| T285 | 3 | 11-26T15:09 | 3.82 | NOT-REVIEWABLE? | (b) figure + GM words | "21 of 22 code builders ran cold", "six more profiles"; the 2026-11-26 words in no request.md |
| T285 | 4 | 11-26T15:15 | 3.41 | BLOCKED | (d) | D6a a hold that names no feature |
| T285 | 5 | 11-26T15:19 | 4.77 | BLOCKED | (a) | D9a a path-spelled git passes the guard, left with no filed id (the cure offered and taken: filed as T295) |
| T284 | 2 | 11-26T16:02 | 5.32 | NOT-REVIEWABLE? | (b) figure | "589 s", "load median 42" |
| T284 | 3 | 11-26T16:13 | 3.87 | CLEAR | (c) review-asked | a caveat the CLEAR review raised, written in; tests' description |
| T295 | 2 | 11-26T16:38 | 4.54 | BLOCKED | (d) also (a) | census bypasses left unfiled AND make -C unread |
| T281 | 2 | 11-26T16:10 | 1.07 | BLOCKED | (d) |  |
| T305 | 2 | 11-26T17:32 | 0.89 | BLOCKED | (a) | D10 event-log booking left, no filed task |
| T309 | 2 | 11-26T17:58 | 1.52 | BLOCKED | (a) | D7 test-written log entries left, no deferral |
| T289 | 2 | 11-26T18:16 | 1.26 | BLOCKED | (d) | Performance work? no |
| T104 | 2 | 11-26T18:47 | 2.8 | CLEAR | (c) real | two more cases found and fixed |
| T159 | 2 | 11-26T18:50 | 3.15 | CLEAR | (c) real | scope widened to three crates |
| T316 | 2 | 11-26T19:41 | 3.25 | BLOCKED | (d) also (a) | D7 pre-warm during rollout AND D11 a failure left unfiled |

The scripts beside this file read `t308-rounds.json`, the rounds as pulled from the session's transcripts. That file is not kept in
the repository (it is raw transcript text, and the repository is public); it was built by `t308-rounds.py` from the
coordinating session's transcript and stands only in that session's scratchpad, so the tables above are the kept result.
