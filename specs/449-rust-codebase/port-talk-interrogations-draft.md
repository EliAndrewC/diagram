<!-- A DRAFT, written 2026-11-27 by one read-only agent for the talk before the port resumes (the GM's third message in port-talk-gm-goal.md asks for it); not reviewed, nothing in it decided. Its quotations of the GM are his words from this session's messages. Load this file when: the process reviewer's feature is being written. -->

# The GM's process interrogations, 2026-11-14 to 2026-11-27: a catalog of kinds of question

Draft reference examples for the process-reviewer feature. Twenty kinds of question, each with the GM's words, what was
found, the signal that could have prompted it unasked, the measurement that answers it, and how it has been answered
wrongly. Two closing sections list what fits no kind and what this catalog cannot support.

## How to read this

- **Sources.** S1 is `gm-messages.md` in the session scratchpad (the GM's typed and dictated messages since 2026-11-14).
  PD is `docs/process-decisions.md`; AUD is `dev/audits/<name>.md`; a `T<n>` is a task of
  `specs/451-time-retro-and-efficiency/` (`tasks.md`, `tasks-done.md`) unless another feature is named; REQ is that
  feature's `request.md`; MEAS is `dev/measurements/<date>/<name>/`; GOAL is
  `specs/449-rust-codebase/port-talk-gm-goal.md`. All paths are under `/diagram/.clones/diagram-backlog/`.
- **Quotes.** Every quoted line of the GM's is a contiguous verbatim excerpt (dictation and typing errors kept) under its
  UTC timestamp. An excerpt is not the whole message.
- **S1 is not complete.** It lacks 38 messages the GM sent while the session was mid-turn (a few are resends of one
  another); they are in the session transcript's queue records
  (`/home/agent/.claude/projects/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51.jsonl`, `queue-operation` / `enqueue`) and
  not in S1. Several of the most useful quotes are among them. A quote marked `[Q]` is taken from those records with the
  record's own timestamp; it is not in S1. S1 also cuts two messages off mid-sentence (2026-11-26T18:23:31Z and
  18:50:02Z); the GM's own completions of them are `[Q]` messages at 18:24:09Z and 18:50:40Z.
- **Dates disagree between sources.** S1 and the transcript stamp in UTC; the repository's records date the GM's words in
  local time. REQ's "2026-11-19, the retrospective" is S1's 2026-11-20T03:43:15Z, and PD's "2026-11-25" pre-approval is
  S1's 2026-11-26T02:44:05Z. This file uses the UTC stamps for quotes and the records' own dates for measurements.
- **What makes two questions one kind.** The same signal and the same measurement steps make one kind; different steps
  make two. A candidate with no verbatim question of the GM's is not a category here (see the closing sections).
- **Report names** are the project's own: `make task-time` (the task time breakdown; its window section "The biggest
  blocking, and whether it could run in parallel", its per-task category table and its "make target or program" table
  with a `runs` column - names read from `dev/measurements/2026-11-25/task-time/tt24-final.log`), `make task-progress`,
  `make sampler-report`, `make where-time`, `make audits`, `make guard-log`, `make review-cost`, `make disk-audit`, the
  event log (`.git/l7r-events/*.jsonl`, its `Phase` lines), `dev/review-ledger.md`.

---

## 1. Is the pace what it should be, and where did the time go?

**The question.** We landed N tasks in H hours. Is that how long this should take, and what ate the time?

**The GM's words.**
- 2026-11-16T13:23:58Z: "And your impression is that the time it's taking is representative of how long these tasks should take?"
- 2026-11-20T03:43:15Z: "How much time are we spending on running our tests? How much time are we spending on recompiling things?"
- 2026-11-26T18:07:54Z: "So do you feel like the progress that we are making is commensurate with the complexity of what we're doing?"

**What was found.**
- 2026-11-20 (the first 14-hour breakdown, assembled by hand from transcripts): six ranked improvements, the largest
  keeping builder contexts small, at 44 to 95 minutes, and not using `make static` as the edit loop, at 26 to 52 (one task
  ran it 24 times). The existing report could not say this: its categorizer put 206 of 208 tooling minutes in "other
  tool". Source: REQ, the section on what the proposed improvements refer to (the session's words). Result: T02-T21.
- 2026-11-21: after the last code edit, 39 builders spent 63 minutes on foreground tests and 101 minutes idle on their own
  background runs, beside 158 minutes of model time that needed no check's result. Result: T55 (closing checks run at
  once, in the background). Source: T55's line.
- 2026-11-25 (the first tooled breakdown, 47 tasks landed in 24 hours): of the working blocking time, builders' own model
  turns 309.8 minutes (34.5%), tests 60.0 (6.7%), compile 54.1 (6.0%); waiting on the GM 435.1 minutes, reported apart.
  Source: `dev/measurements/2026-11-25/task-time/tt24-final.log`.
- A "no": 2026-11-21T14:40:11Z the GM read the overnight breakdown and wrote "Okay, those numbers look pretty good. I
  don't see any obvious bottlenecks" - then asked the session for ideas anyway. What the session answered is not in the
  sources read.

**How to notice it unasked.** `make task-time SINCE=last`: the window's table and its "biggest blocking" list.
Visible before the GM asked: no for the asks up to 2026-11-25T13:20:43Z (the existing report put 206 of 208 tooling
minutes in "other tool", and that ask is the one that produced T243); yes for the asks of 2026-11-26T15:35:32Z and
18:07:54Z, when the report existed and the GM was still the one who called for it.

**How to check it.**
1. Run the breakdown over the window since the last one.
2. List the three largest blocking rows and the three largest make targets by runs times minutes.
3. Compare minutes a landed task and tasks landed a wall hour with the previous window's.
4. For each large row, ask kinds 2, 3, 4 and 12 below. A row is not a finding until one of them is answered.

**The trap.** Acting on one task's minutes instead of the window's throughput. The GM's account (an account, not a
measurement) of the earlier hourly step-back reviewer, GOAL second message: "if it saw that a particular change would
have caused one specific task to save a minute or two, then it would implement that change even if that change on net
was going to reduce the overall throughput of tasks." It is still in the code, switched off (GOAL, "What the session
found").

---

## 2. Is anything actually waiting on this, or is it just running?

**The question.** This took a long time - but was anything held up by it, or did it run beside the real work?

**The GM's words.**
- 2026-11-21T03:49:37Z: "how often do you think we need to be waiting for the tests to run vs running them in the background while we continue our work?"
- 2026-11-25T15:39:56Z: "Actually, for what it's worth, I think that a minute should count as blocking. When something else is waiting on it to be done before it can be started."
- 2026-11-26T17:24:27Z: "it probably will be almost or completely in the category of non-blocking time that is never a bottleneck"

**What was found.**
- Research looked like half the day and blocked nothing: on 2026-11-25 "research and page sessions" were 924.3 of the
  1,037.2 minutes "Waited on, blocking no task" (tt24-final.log). The GM had seen "50%" in an earlier table and asked
  (2026-11-25T15:19:28Z) whether it was misleading; it was. Result: the blocking definition (PD, "What counts as blocking
  time"), the research switch (T244), feature 455.
- The definition itself took three tries: two readings were rejected the same day, one of which booked 949 minutes of a
  headless page session's turns as blocking (PD; AUD `blocking-definition.md`).
- The second tier: its blocking was expected near zero; `make task-time` showed 123.3 minutes over 2026-11-26T17:00Z to
  2026-11-27T01:00Z. Measured: the three warm pool trees stood idle 336 of 1,440 tree-minutes (23%) with the queue never
  short, because the session finished each builder's end (commit, carry, resolve, check, land) before briefing the next.
  Result: T394. Source: MEAS `2026-11-27/tree-idle/results.md`.
- A "no, leave it": coverage stays out of a builder's closing step. A failed batch gate delays the landing on main, and
  no builder waits on it (PD, "REVERSED the same night").

**How to notice it unasked.** Every category row of `make task-time` has a minutes column and a blocking column; the
signal is a row whose blocking is large, or a row expected near zero that is not (the second tier's own line, T298).
Visible before the GM asked: not established for the 123.3 figure - it reached the GM in a breakdown they had requested
(2026-11-27T00:31:43Z [Q]), and whether the session had seen it first is in no record read; no for the 2026-11-21 and
2026-11-25 questions, which came before the report had a blocking column (T243).

**How to check it.**
1. For the step in question, name what waits on its result (a task's next step, a tree's next handout, the landing).
2. Take its minutes and its blocking minutes over the window from the breakdown.
3. If blocking is high, classify each blocked interval by what the waiter was doing (the tree-idle method: each idle 10
   seconds classed as a landing running, the session in its own turn, or the session stopped).
4. If nothing waits, the step is a cost in machine time and tokens only; say so and stop.

**The trap.** Optimizing a count that nothing waits on. The session added coverage to every builder's closing step
because 4 of the first 9 batch gates had failed; that cost each builder 7 to 111 seconds on its own critical path to
save repairs that held no builder. The GM caught it (2026-11-26T23:37:00Z) and it was reversed; T381 withdrawn. Source:
PD, "Two tiers of checking".

---

## 3. Is the same work being done more than once?

**The question.** Are we recompiling, re-running or re-reading something we already did?

**The GM's words.**
- 2026-11-17T14:44:10Z: "recompiling everything when making a change that should only actually need to recompile a small portion of our code base"
- 2026-11-22T19:39:30Z: "are we able to do something like copy the current cache into that builder's working directory so that it doesn't have to do a cold compile the first time"
- 2026-11-26T18:23:31Z: "So are you able to break down for me how many compilations and runs of the tests that represents?"

**What was found.**
- Any edit of the guard crate rebuilt 27 gate crates: 128 guard rebuilds at a median 18 seconds and 18 whole-workspace
  coverage rebuilds of about 15 minutes (measured 2026-11-21 from the event log's Phase lines). Result: T58, the shared
  readers split into their own crate.
- The gate compiled each crate three times and ran its tests twice: test build 73 minutes, coverage build 78, lint 54,
  against about 45 minutes of tests run (2026-11-22, 01:00 to 08:15). Result: trial T154; T57.
- Builders started cold: 21 of 22 code builders at two-at-once ran in a fresh worktree whose first closing checks took
  14 to 30 minutes against about a minute warm (PD, "Two code builders at once"; AUD `builder-pool.md`). Result: the warm
  pool, T285.
- A library compiled again in another configuration: 75 compiler runs for 58 targets; after T325, 58 for 58, and the
  checks' test step 171.1 s before against 51.6 s after (one sample each, under different load). Source: MEAS
  `2026-11-26/feature-unify/results.md`.
- A "no": a shared compiler cache (sccache) gave 0 hits of 18 and a cold build 23% slower; incremental builds off made a
  one-file rebuild 55 s to 363 s. Both declined (PD, "Three build levers"; AUD `declined-build-levers.md`).

**How to notice it unasked.** The `runs` column of `make task-time`'s "make target or program" table (one task shows
`make rust-test` 27 times in tt24-final.log), and the event log's Phase lines by step (`build`, `test`, `cover-build`,
`cover-run`, `lint`). Visible before the GM asked: no on 2026-11-17 (no Phase lines yet; they are T05's, in use by
2026-11-20T12:35Z per T57's line); yes after that - the guard rebuilds (T58) and the triple compile (T154) were read
from those lines without the GM naming them, and the cold trees were the session's own doing (it removed each worktree
and its cache after the landing, REQ "builder worktrees").

**How to check it.**
1. For one landed task, count the runs of each compiling or testing step from its Phase lines.
2. For each step run more than once, say what changed between runs. Nothing changed: it is a duplicate.
3. For a build, count compiler runs against distinct targets after a one-file edit (the T325 method).
4. For a new working copy, time its first run against its second.
5. Price the lever before adopting it: the same measurement, cold and warm, median of three.

**The trap.** A number asserted about where build time goes, then corrected by measuring. The session's reading that
"the tests' own run time dominates a builder's test run" was wrong: alone, a gate crate's tests run in 0.8 to 1.9 s and
its build after a one-line edit in 0.8 to 2.9 s; the seconds were a build waiting up to 57.3 s for a slot (PD, "Five
levers on a builder's test run", which says it corrects the earlier reading).

---

## 4. Could this start earlier, or run beside something else, instead of after it?

**The question.** Why are we waiting for A to finish before starting B?

**The GM's words.**
- 2026-11-25T14:09:12Z: "we could probably just do the first 4 minutes of implementation. While the plan review is running"
- 2026-11-25T14:13:14Z: "I expect that there are places where we currently block on things where we could begin the next round of whatever it is that we're doing in parallel"
- 2026-11-26T18:23:31Z: "it feels like there is room for additional parallelization and less blocking. Does that sound right to you?"

**What was found.**
- Building before the plan review returns: adopted. Of 301 reviewed tasks, 224 (74%) were CLEAR on the first round; of
  69 readable blocked rounds, 5 (about 7%) reversed built work. Source: PD, "Building begins before a new feature's plan
  review returns"; MEAS `2026-11-25/reversals/`.
- Building the fix beside its reproduction: declined. Over 47 defect fixes the reproduction was 2 to 4 minutes of a
  34-minute median; a split would save 4 to 38 of 1,440 builder-minutes for about 480 extra, and the brief's diagnosis
  was wrong in 8 of 42 chains. Source: PD, "Declined so far"; MEAS `2026-11-26/split-reproduction/m16-results.md`.
- Compiling at handout: adopted (T316). A first test build of 7.7 s fell to 0.1 s after a finished pre-warm (AUD
  `builder-prewarm.md`).
- Rolling dispatch: builders ran three at once only part of the night because tasks were dispatched and landed in
  batches (T88; the share is 26% in T88's line and 33% in T98's - see "What the catalog cannot support").

**How to notice it unasked.** `make task-time`'s window section says, for each large blocking row, what share was "a
foreground run its actor waited on, which could run in the background beside other work" (73.7% of tests' blocking and
52.5% of compile's, tt24-final.log). Visible before the GM asked: no for the questions of 2026-11-25T14:09:12Z and
14:13:14Z - that report's window ends 16:20Z the same day, and the reversal rate behind the plan-review answer was
measured only afterward; yes for the 2026-11-26 questions, by which time the line was printed in every breakdown.

**How to check it.**
1. Name A and B and what B needs from A.
2. Measure how often A's result changes what B does (the reversal rate, the wrong-diagnosis rate).
3. Measure A's minutes as a share of the task.
4. Saving = A's minutes times the share of cases where B's early work survives; cost = B's thrown-away minutes in the
   other cases plus the extra agent. Adopt only if the first clearly passes the second; record it either way.

**The trap.** A parallel step that breaks the thing it runs beside. Under its spare-slot rule the pre-warm cut its own build short
when a slot was taken; a test build killed that way left the cache unable to link until its incremental directories were
removed (T336; AUD `builder-prewarm.md`, "THAT CUT WAS REMOVED").

---

## 5. How many can run at once, and what really sets the limit?

**The question.** Why two at a time? Is that memory, processor, disk or a lock - and did we measure it?

**The GM's words.**
- 2026-11-25T19:01:53Z: "is the number 2 here something that was picked deliberately, or is it just what we did by default because 2 is the simplest possible case"
- 2026-11-26T13:38:04Z: "Are you sure you're being careful to distinguish cached RAM which gets automatically freed by the kernel when needed vs RAM actually in use?"
- 2026-11-26T13:39:51Z: "wouldn't it be better to address that with some synchronization rather than pre-emptively limiting builders just in case?"

**What was found.**
- Throughput: 1.71 builder-built tasks landed a wall hour with one builder, 2.02 with two (PD, "Two code builders at
  once"; MEAS `2026-11-26/builder-count/m1-results.md`).
- Memory is not the cap: in-use (anonymous) memory peaked at 6.3 GiB with two code builders and 6.4 GiB with three,
  against a 10 GiB limit. The 9.5 GiB reading that looked like the limit was page cache, which is given back (PD, same
  entry).
- What coincides is the limit: all twelve highest memory samples fell where three trees were in a coverage build at
  once. Result: a machine-wide build slot (T284) in place of a builder cap, and a lane for small builds (T347: a wait of
  60 s became 1 to 2 ms). Source: AUD `build-slot.md`.
- Open: the count at three and four is still owed its re-measurement (PD, same entry, "Decided, and to be re-measured").

**How to notice it unasked.** `make sampler-report` (rows by the count of pool trees held) and `make task-time`'s
`waiting on a build slot` category. Visible before the GM asked: no. Neither existed: the first memory samples were a
hand-started loop, "2" had no measurement behind it, and the GM also had to ask why the measurement had not been run
(2026-11-26T12:38:07Z).

**How to check it.**
1. Run the same kind of work at N and N+1 and compare tasks landed a wall hour and pace a worker.
2. Sample the resource every 10 seconds while they run: in-use memory (not total, not cache) against the container's
   limit (the cgroup's, not the host's), load against cores, memory stall, kills.
3. Join the peaks to what was running (the Phase lines) to learn which step coincides.
4. Prefer a lock on that step to a lower count.

**The trap.** A limit asserted without running it. PD: "The session had first concluded, without running it, that a
third builder would pass the margin; the run says otherwise". And reading the wrong number: `free` shows the host's 15
GB where the container's limit is 10 GiB, and total memory in place of in-use.

---

## 6. Is this number the right number, or just a number someone picked?

**The question.** We have a limit of X. Why X? What would happen at half of it or double?

**The GM's words.**
- 2026-11-25T14:44:06Z: "Does it actually make sense for us to stop at only 300,000 tokens?"
- 2026-11-23T18:48:23Z: "But if those size limitations are causing us to cut details that could cascade, then I think that actually a good rule of thumb is that we should literally never do that."
- 2026-11-27T01:02:01Z: "then I am personally skeptical about something like a target of 10%."

**What was found.**
- The builders' 300k context cap: kept, on measurement. Across 61,271 builder turns, time was a wash from 300k to 800k
  and tokens favored the handoff (33% fewer at 300k). The session had recommended 600k and withdrew it; the GM's own
  suspicion that the cap was too low was also not borne out. The real lever was the size of the brief (kind 17). Source:
  PD, "The builders' context cap stays at 300k"; AUD `declined-context-cap-600k.md`.
- The research pages' 20,000-byte cap: trims made to meet it had dropped content on two pages. Result: a size edit may
  not change a claim, a page splits or gets its own recorded limit after an adversarial check (T184). Still open: HTML
  comments count toward the cap, and four pages sit within 20 bytes of it (T266).
- The second tier's threshold ("about six tasks or ninety minutes", labeled a guess): accepted for now with a trial to
  read it again (PD, "The second tier's threshold"; feature 458).
- The "under 10% idle" target of T394: labeled a guess by the session and questioned by the GM the same hour, who asked
  whether the arrangement, not the number, is what should change (kind 20).

**How to notice it unasked.** `make audits` (each entry's `threshold:` line, many marked GUESS), `make tunables`, and
`make guard-log GUARD=<name>` for how often a cap fires: 107 of 135 handoffs were at the cap (AUD
`builders-context-cap.md`). Visible before the GM asked: yes for the context cap (its firings were in the guard log and
the handoffs in the session's own reports); not established for the page-size cap and the idle target, which the
session itself brought to the GM.

**How to check it.**
1. Find who set the number, when, and on what (a measurement, or a guess).
2. Count how often it binds and what each binding costs (a handoff's re-read, a trimmed page, a refused run).
3. Measure the outcome at the number and at values around it, from data already recorded where possible.
4. Ask whether one number fits all cases or a default with named exceptions does (the GM's own example of a per-test
   time limit, GOAL second message).
5. Keep, move or remove; record the result with what would reopen it.

**The trap.** Defending the threshold by degrading the work. Content was cut from pages to fit the size cap, and the
cuts then set off checks on everything citing those pages (REQ, "the convergence talk": "told the 0009 and 0059 trims
dropped content").

---

## 7. Is the rigor in the right place?

**The question.** This check is thorough - but is this the point where it needs to be, or are we doing it early, late
or twice?

**The GM's words.**
- 2026-11-26T16:45:38Z [Q]: "when in fact the correct place for that level of rigor is checking whether something in the session clone can land back in the main checkout and in the main branch on GitHub"
- 2026-11-26T16:40:55Z: "But are we doing something like waiting to even try compiling things until... we have that lock? Because that doesn't seem necessary to me, unless I'm missing something."
- 2026-11-26T15:56:44Z: "Or did we run through a lot of expensive stuff before finding that at the very end?"

**What was found.**
- The full checks ran twice a task (a builder's closing checks, two to four runs, then the landing's gate), and closing
  checks were 63% of a small task's builder clock. Result: two tiers of checking, adopted as a trial - tests, lint and
  format in the builder's tree; one full gate over the batch where work reaches main. Source: PD, "Two tiers of
  checking"; MEAS `2026-11-26/task-route/m11-results.md`.
- What a landing waits on that it need not: the push's lock covers seconds, but a guard held commits in any tree while
  a gate ran, and one refusal came after the gate had already run. Filed, open: T307.
- A cheap check placed first: the unfinished-carry refusal runs in 0.06 s before anything expensive (AUD
  `unfinished-carry-over.md`), after three landings ran over an unfinished cherry-pick and one pushed its tick without
  its code.
- A "no": the first tier does not take on coverage (kind 2's reversal); the plan review "stays where it is" (PD).

**How to notice it unasked.** In `make task-time`: `make closing-checks` runs a task, the landing rows, and landing
attempts that end red on something other than the task landed (five in round one, PD). Visible before the GM asked:
yes for the duplicated checks (T154 had measured the gate's own repeats from the Phase lines on 2026-11-22); what the
data did not supply was the GM's reframing (where does work become shared?). Not established for the lock and
fail-late questions.

**How to check it.**
1. List each check and each point it runs between a builder's edit and main.
2. For each point, name what a failure there would harm (one builder's tree, the session's staging, everyone's main).
3. A check that runs before the point where its failure would harm anyone else is a candidate to move later; a cheap
   check that runs after an expensive one is a candidate to move earlier.
4. Measure the moved check's failures and their repair minutes against the minutes it used to cost every task.

**The trap.** The same as kind 2's: after rigor was moved later, the session moved part of it back to reduce visible
gate failures, the wrong goal.

---

## 8. What does this safeguard actually catch?

**The question.** This review or rule costs time on every task. How often does it find something really wrong, as
opposed to a difference, a wording point or nothing?

**The GM's words.**
- 2026-11-19T01:53:55Z: "we're not doing something silly like saying "that's 1px off from where we expect but is still in line with our research but we will put in a lot of work to fix it anyway" are we?"
- 2026-11-22T04:21:17Z: "So how many things are in that first category as opposed to things that we know were causing us issues?"
- 2026-11-25T04:29:25Z: "see which of them actually resulted in research findings that changed anything that we were rendering?"

**What was found.**
- Sub-pixel "defects" were being filed and fixed. Result: the rule that a defect is a wrong outcome, not a difference
  (root `CLAUDE.md`, "Research", dated 2026-11-19).
- Research before every guess: of eight hamlet searches, two changed what is drawn (REQ, "a research backlog"). Result:
  UNRESEARCHED and the backlog (T236), then the research switch (T244).
- The plan review on small tasks: first round blocked 2 of 8, and one block changed the code that landed, on a path the
  tests did not reach. Kept. Source: MEAS `2026-11-26/task-route/m11-results.md`.
- The filter on what reaches the GM is unsteady: replayed twelve times it agreed with its own recorded rulings on 53% of
  items and cut something the GM had gone on to answer in 5 of 12 runs (PD, "The escalation check on a narrower
  bundle"). Open. Its trigger fired 12 times on 2026-11-26 and about half were statements, not questions (REQ, T299).
- Task time estimates: the GM learned they existed and judged them not worth their cost (2026-11-25T16:14:46Z). What
  followed is not in the sources read.

**How to notice it unasked.** `dev/review-ledger.md` and `make review-cost` hold every review pass with its verdict and
cost; `make guard-log` holds every refusal and escape. A check whose rows are nearly all CLEAR, or whose findings are
nearly all wording, or a guard escaped nearly every time (158 plan-gate escapes against 354 commits, AUD
`plan-gate-escape.md`), shows there. Visible before the GM asked: yes as raw rows (the reversals measure read ledger
rows going back to 2026-11-19); no as a finding - each classification was done by hand after the question.

**How to check it.**
1. Take the safeguard's last N findings (or refusals).
2. Class each: a wrong outcome that would have reached main or a map; a real gap fixed with a measurement; wording or
   form; nothing.
3. Count its cost over the same N (agent minutes, blocking minutes, tokens, re-rounds).
4. For a filter, replay recorded inputs several times and count how often it agrees with itself.
5. Keep, narrow to the class that pays, or remove; record it.

**The trap.** Treating every finding as a defect because a rule says to fix defects. The session's own report, quoted
by the GM at 2026-11-19T01:53:55Z: "following your rule I filed and fixed each before moving on."

---

## 9. Is the work generating more work than it finishes?

**The question.** We keep being 'nearly done'. Are we closing things, or does every fix open two more - and are the new
ones real?

**The GM's words.**
- 2026-11-23T18:06:15Z: "The problem is when we do a cascading set of reviews that triggers a cascading set of changes that is mostly not finding actual problems"
- 2026-11-24T14:11:34Z: "we will not still be stuck in a loop in which for every task we close, we open 2 new tasks"
- 2026-11-25T04:25:07Z: "Or is it likely that 24 hours from now we will be relatively close, but in kind of a Zeno's paradox kind of way?"

**What was found.**
- Cascades: a page edit re-owed checks on every pop-up citing it. Of 30 pop-up edits the cascade produced, 20 corrected
  something wrong, 6 only completed, 3 were wording and 1 made things worse (REQ, "the convergence talk"). Result: seven
  rules (T184-T190) - only a claim-changing edit re-owes a check, only factual findings cascade, later rounds are scoped
  to the change, settled choices stay settled.
- The fix was itself tested on a real change, as the GM asked (2026-11-23T20:20:07Z), and the test found six defects in
  the new rules, among them 147 claims forced by a regenerated document (T209-T214).
- Bundling: every small defect paid the whole fixed cost of a task. Result: T141, a bundle shares one builder, one
  review and one landing.
- Plan review re-rounds: of 56 later rounds (169 minutes), 26 were a real objection; the rest followed an edit after a
  CLEAR, an unreviewable section or a missing id. Result: the mechanical causes refused before a review is dispatched
  (PD, "A plan review's later rounds").

**How to notice it unasked.** Tasks filed against tasks ticked a day (each filed line names what found it and the date);
a check's round count on one subject (the third-round tripwire); the count of units a single edit re-owes. Visible
before the GM asked: yes - on 2026-11-23T14:10:33Z the GM reacted to "52 follow-ups", a number the session itself had
reported, and on 2026-11-22T04:16:42Z [Q] to the session's own statement that tasks were being filed faster than
closed.

**How to check it.**
1. Count opened and closed over the window, and class the opened ones by what opened them (a real observed failure, a
   notional one, a review's wording point, a cascade).
2. For a cascade, take the edits that set it off and ask of each whether it could have changed what depends on it.
3. For re-rounds, class each later round by its cause from the round before it.
4. Fix the generator (what re-owes, what a round may reopen), not the count.

**The trap.** Reaching for filing less, or for the expensive complete pass. The GM declined a change of the first kind
(2026-11-23T18:06:15Z, "I don't want to make that change just yet"; what the session had proposed is not in the sources
read) and replaced a 6-to-10-hour agent pass with a script (2026-11-24T03:45:45Z to 03:59:30Z; REQ, "On T192's route").

---

## 10. Does the tooling enforce this, or does someone have to remember?

**The question.** You say we do it this way now. What stops the next session, or you in an hour, from not doing it?

**The GM's words.**
- 2026-11-20T04:33:18Z: "And let's make sure all of the enforcement is real enforcement and not just instructions."
- 2026-11-26T14:23:29Z: "we should definitely not rely on you remembering to do the correct thing with worktrees"
- 2026-11-26T20:10:15Z: "is this also part of our checklist-based process for kicking off and managing builders? Or do we not have such a checklist?"

**What was found.**
- Worktrees: the recorded rule was to reuse them; the session made each by hand and deleted it and its cache after the
  landing. Result: the pool and a guard that refuses a hand-made worktree (T285).
- Candidates to file: builders' reports listed them and the session filed them from memory; four went unfiled until the
  GM asked (2026-11-26T14:24:09Z). Result: T289.
- Builder briefs: the sizing rule lived in a file the session was to read; it broke the rule four times in a day with
  nothing refusing. Result: `make builder-brief` and a guard (T334); replayed over the day's 110 dispatches the guard
  refused 56, every one a builder's, none wrongly (AUD `builder-brief-command.md`).
- Keeping the pool full: the session was doing it by hand; the GM asked for it to be enforced (2026-11-26T18:03:28Z).
  Filed, open: T313.
- Recording declined options: three had a saved measurement and no entry until the GM asked. Filed, open: T320.

**How to notice it unasked.** A rule in a doc or a decision entry with no guard, gate or command named beside it; and
any promise to remember, or any statement that a brief or doc now says it, in the session's own messages. `make audits`
lists mechanisms with no entry (254 of 267 on 2026-11-26, AUD `audit-register.md`). Visible before the GM asked: yes
for worktrees and unfiled candidates (the hand steps and the four unfiled items are in the records as the session's
own); not established for the others.

**How to check it.**
1. State the rule in one sentence and find where it is written.
2. Find what refuses or performs it (a guard, a gate step, a make target). None: it is remembered, not enforced.
3. Count violations over the recent window by replaying the recorded commands or dispatches through the rule.
4. If violated, build the command that does it right and the refusal that names that command; prove the refusal on the
   recorded violations and that it does not fire on correct work.

**The trap.** Answering "the brief and the queue now say it plainly" - an instruction offered as a fix (the session's
phrase as the GM quotes it at 2026-11-26T20:10:15Z).

---

## 11. Is the measurement itself right?

**The question.** This figure does not match what I expected. Is the process wrong, or is the report wrong?

**The GM's words.**
- 2026-11-22T13:22:23Z: "we should also make the hook suites measure their time so they won't be missing; we want everything measured so we know where our time goes"
- 2026-11-25T15:19:28Z: "then that number would be misleading because it would essentially imply that we spent half of our wall clock time waiting for research to be done"
- 2026-11-27T00:45:39Z [Q]: "that's a HUGE problem, either with our    measurements or with our process, and we should get to the botom of that ASAP"

**What was found.**
- Whole phases were invisible: only the Rust checks and `make land` wrote Phase lines, so hook suites (about 5 minutes
  a run), map generation and page sessions did not appear. Result: T153.
- Time booked to the wrong task: edits and page-session passes booked to the clone's mark (T161, T167); a pool tree's
  Phase lines booked to a task it had been handed to five handouts earlier (T344, T332).
- Blocking that was not blocking: "wait loops" were 25.6 of a window's 128.7 blocking minutes, 12.1 of them another
  task's leftover background loop (T328); 27.6 of the second tier's 123.3 were booked as waiting on the GM (MEAS
  `2026-11-27/tree-idle/results.md`).
- A report that does not add up: the second tier's batch lines summed to less than its total (T331, open).
- The denominator: time waiting on the GM is reported but left out of the other percentages, at the GM's direction
  (2026-11-25T15:13:58Z).
- Both at once: the 123.3 figure was loosely defined and it pointed at a real fault (kind 2).

**How to notice it unasked.** A category named "not classified", "other" or unassigned (`_unassigned.jsonl`) with real
minutes in it; rows that do not sum to their total; a row the report's own text says to expect near zero; a figure that
exceeds the wall clock. Visible before the GM asked: yes for the blocking minutes (at 2026-11-26T19:40:24Z the GM asked
after a report "of those blocking minutes being off from what we expected", so the session had already raised it) and
for the unclassified minutes (2026-11-25T13:47:27Z, a row of the table the GM was reading); no for the missing phases,
which by their nature no report showed.

**How to check it.**
1. Recompute one task's row by hand from the event log and the transcript and compare (the falsifier of AUD
   `blocking-definition.md`: more than about one in ten disagreeing).
2. Check sums: lines against totals, categories against the window.
3. For each surprising figure, list the intervals inside it with what started each and what waited on it.
4. Fix the booking rule, then re-read the figure before drawing any process conclusion from it.

**The trap.** Two, in opposite directions: drawing a process conclusion from a wrongly booked number, and dismissing a
surprising number as a booking fault. The second-tier figure was partly a booking fault and still pointed at 23% idle
trees.

---

## 12. Why does this one thing take so long?

**The question.** That is a single step. I would have guessed seconds, and it took minutes. What is inside it?

**The GM's words.**
- 2026-11-26T14:17:30Z: "Though out of curiosity, why is this taking so long? How long does it take to do our compiling exactly?"
- 2026-11-26T16:23:26Z: "The numbers that you're citing are larger than what I had thought was the case. saying that our tests take several minutes to run?"
- 2026-11-24T03:45:45Z: "Why is that something that will take 6 to 10 hours?"

**What was found.**
- A builder's test run, taken apart (T315): the tests and the one-file build were each about 1 to 3 s alone; the rest
  was a build waiting up to 57.3 s for a slot, one test that was 8.4 s of a crate's whole run (T339), 3.2 s waiting on
  processes the tests left behind (T340) and 2.0 s of the checks' own tool before the build (T341).
- The guard crate's tests ran three times slower under the default temp directory: every temp-directory creation listed
  all of `/tmp` (5,443 entries), 509 times a run (MEAS `2026-11-26/tmp-clutter/t365-results.md`; T370, T372).
- A hook on every file edit took 333 ms because it re-read and parsed the feature's whole 41.0 MB event log each time;
  another 480 ms in the session's own clone came from reading the whole 274 MB transcript to find the session's name
  (MEAS `2026-11-26/edit-hook/t373-results.md`; T383, T385).
- The "6 to 10 hours" of label tagging assumed an agent writing a sentence for every item; a script did the mechanical
  part (REQ, "On T192's route").
- A "no": five levers on the test run were priced and declined, each worth under a second (AUD
  `declined-test-run-levers.md`).

**How to notice it unasked.** A make target whose minutes a run in `make task-time` are far above its floor when run
alone; a `runs` count that looks ordinary beside minutes that do not; a per-call cost that grows with a file that only
grows (the event log, the transcript). Visible before the GM asked: not established for the test and compile times
(the per-target minutes were in the breakdown, but no record shows a floor to compare them with); no for the edit
hook, which was in no report and was found while measuring something else.

**How to check it.**
1. Run the one step alone, warm, on a quiet machine: that is its floor.
2. Split the real run into parts (waiting for a slot, compile, link, the tests' own run, start-up, clean-up) from its
   Phase lines or by timing each part.
3. The difference between the real run and the floor is waiting or contention; name what it waited on.
4. For a per-call cost, check what it reads and whether that grows.
5. Price a lever for each large part; build only those that pay; record the rest as declined.

**The trap.** Guessing the part instead of splitting the step (kind 3's trap), and estimating a job by its most
expensive method (the 6-to-10-hour figure).

---

## 13. What is this leaving behind, and does cleaning it up cost us time?

**The question.** Why is the disk full - and if we delete things to fix that, are we deleting something that was
saving us time?

**The GM's words.**
- 2026-11-22T19:37:32Z: "I want to make sure that we are deleting old invalid caches, but not caches that we are actually still using."
- 2026-11-25T17:30:11Z: "We shouldn't actually be short of disk for what it's worth.  if we are then it means there are things wer're not cleaning uup."
- 2026-11-26T15:53:36Z: "So we definitely don't want to clean things up if it is going to cost us time later."

**What was found.**
- 2026-11-22: the disk reached 100% (485 MB free) and every coverage run failed; the build caches held over 100 GB and
  thousands of scratch directories 63 GB (T158).
- 2026-11-25: the build cache was 190 GB against its own 100 GB budget, and the existing cleanup's dry run would have
  freed 27 MB. Result: `make disk-audit`, a budget that holds, an automatic trigger below a free-space floor (T245,
  T246; AUD `disk-budget.md`).
- A "no", by the GM's word: dropping a coverage build at each landing would free about 65 GB and cost up to 512 s cold
  against 123 s warm. Declined ("we definitely want those extra 6 minutes more than we want the 65G",
  2026-11-26T12:38:07Z). The principle is recorded: a cache is evicted for being unreusable or under real disk pressure,
  never for being idle (PD, "THE PRINCIPLE, for every disk rule").
- Another "no": shallow clones; the history is 404 MB and the disk was the build caches (AUD
  `declined-shallow-clones.md`).
- Found by looking: 20 of one cache's 21 GB was stale variants no build would read again (PD; T278, open).

**How to notice it unasked.** `make disk-audit` and `df` against the floor; a cache's size against a fresh one's (44 GB
against 2.65 GB, T278). Visible before the GM asked: no on 2026-11-22 - no report watched the disk, and the GM's
message of 19:35:20Z says the notice came to them; which came first, that notice or the builders' failures at "about
17:05" (T158, no time zone given), is not established. On 2026-11-25 the budget constant existed and was exceeded by
90 GB with no report saying so.

**How to check it.**
1. List every place the container writes, with size, owner and age.
2. For each, say whether anything will read it again (a live tree's cache: yes; a removed tree's: no).
3. Before evicting something reusable, measure the cold cost of rebuilding it against the warm cost.
4. Evict the unreusable first; trade time for disk only under real pressure and only on the GM's word.

**The trap.** A cleanup rule that is safe and useless (27 MB of 190 GB), and the opposite: the session deleting each
builder's warm cache after its landing as tidiness (kind 3).

---

## 14. Is this text costing tokens for nothing?

**The question.** That message, file or report is long and gets read on every turn. Could it say the same in less?

**The GM's words.**
- 2026-11-16T04:02:36Z: "One question about this feature though: why is tasks.md so big?"
- 2026-11-23T05:04:24Z: "That amount of output consumes tokens, so could we accomplish the same thing with no loss of fidelity and fewer tokens?"
- 2026-11-26T02:02:23Z: "we should make sure to measure whether the complexity of the handoffs actually saves time and/or tokens relative to either letting the builders grow or not using them in the first place"

**What was found.**
- Hook messages: one Stop message fired about 550 times and another about 150 in a session, mostly unchanged (T171); one
  refusal was 268 firings of 489 characters, 131,150 characters in the session's context (T177). Result: a word budget
  on every guard message, checked mechanically, with a review of each changed message (T170), and an unchanged block
  said once (T171).
- Builder reports: 38 reports, median 4,415 characters; the modified-path list was never used afterward (0 of 32).
  Result: a fixed format. The saving is small and recorded as such: about 0.74% of the session's input tokens (PD, "The
  builders' report has a fixed format").
- Three "no"s: a terse output style (the main session is about 8% of output tokens; AUD
  `declined-terse-output-style.md`); the check on what reaches the GM run on a cheaper model (it read 2.7 times the
  input tokens and cut a question the GM had answered, 3 of 3 runs); the same check on a narrower bundle (input down 42%
  and 69%, three catches lost). Source: PD, "Declined so far".
- Open: whether delegating to builders pays at all is still unmeasured (AUD `delegating-to-builders.md`,
  "last-audited: never").

**How to notice it unasked.** Firing count times message length per guard (`make guard-log`, `dev/guard-messages.tsv`);
the size of any file every session auto-loads or every builder reads; an agent's token count at its stop in the event
log. Visible before the GM asked: yes for the repeated hook messages (each firing was in the guard log and the
transcript; the counts of 550 and 150 were made after the GM pasted one); not established for the rest.

**How to check it.**
1. For the text, count how often it enters a context and how many later turns re-read it.
2. Multiply by its length; state it as a share of the session's input tokens.
3. Rewrite it shorter and check nothing a reader used is lost (which fields were used afterward; a fidelity review).
4. If the share is small, say so and decline; a saving under about a percent is not worth a new mechanism.

**The trap.** Assuming cheaper per token is cheaper overall (the cheaper model used 2.7 times the tokens and the
seconds), and cutting input that carried the catches (the narrower bundle).

---

## 15. Is the coordinating session the bottleneck, and is anything actually happening?

**The question.** Are the workers busy, or are they waiting for the coordinator - and when it says something is
running, is it?

**The GM's words.**
- 2026-11-19T11:24:59Z: "And that's sooooo much idle time!  Is that time where nothing was happening?!"
- 2026-11-23T21:34:55Z: "because you said that something was finishing, but I don't see anything happening, and your last message was 30 minutes ago."
- 2026-11-27T01:02:01Z: "as in the one that I am conversing with right now, be kept as idle as possible all the time so that it is doing basically nothing but coordinating subagents and relaying that to me?"

**What was found.**
- The first retrospective (spec.md dates it 2026-11-19; whether it is what the GM was shown at 2026-11-19T11:24:59Z
  is inferred): the stretches with nothing running were an agent's untracked background run (14.9 minutes) and a long
  poll (2.9); result: guards on untracked runs and slow polls (spec.md of 451, User Story 4; T15, T16).
- 2026-11-23: a builder waited about an hour on a page session that had already ended, and the coordinator reported it
  as finishing without looking. Result: T193, T201.
- 2026-11-25: over 24 hours the coordinating session waited 385 minutes on agents, 251 on background commands and 148 on
  nothing (`specs/449-rust-codebase/port-talk-agenda.md`, "Measured context").
- 2026-11-27: pool trees idle 23% of eight hours with the queue never short: 170 tree-minutes while the session was in
  its own turn, 105 while a landing ran, 46 while it was stopped. Result: T394; the orchestrator question is open (MEAS
  `2026-11-27/tree-idle/results.md`).
- A "no", by the GM: builders are not kept alive for follow-up; a fresh one is briefed instead (PD, "Keeping a builder
  alive for follow-up": two fresh builders closed out others' work in 8 and 22 minutes).

**How to notice it unasked.** `make task-progress` (what is running now, and each builder's step); the pool's log
against the event log (a tree held by nobody while the queue has work); `make task-time`'s "Working at once" line (none
190.3 minutes, one 480.3 on 2026-11-25, tt24-final.log) and its "waiting: nothing in flight" row (72.5 blocking minutes
that day). Visible before the GM asked: yes for idle workers in general (those two lines were printed from
2026-11-25); no for the tree-idle share, which no report computes and which was measured only after the GM's alarm; no
for the stalled builder of 2026-11-23, which the idle check of the time counted as running.

**How to check it.**
1. Over the window, compute each worker slot's busy and idle minutes.
2. Class every idle stretch of 3 minutes or more by what the coordinator was doing.
3. Check the queue: was there work a free worker could have taken?
4. To learn whether something is running, probe the process and the transcript's last movement, never the last message.
5. Convert idle minutes into tasks at the window's median minutes a task (336 idle tree-minutes was about nine tasks).

**The trap.** Enforcing busyness instead of throughput: Stop hooks that blocked the session's stop to keep it busy cost
23 turns spent only answering them while it was correctly waiting (T183). And a guessed target for the idle share in
place of asking whether the coordinator should be doing that work at all.

---

## 16. Is the decision recorded with what would reverse it, and has it been checked since?

**The question.** We changed how we work on the strength of a measurement. Where is that written, what result would
tell us it was wrong, and has anyone looked?

**The GM's words.**
- 2026-11-25T14:55:08Z: "and then also crucially what we would look at that would falsify the notion that this is a good idea"
- 2026-11-26T02:44:05Z: "We should also make sure our processes record decisions about what NOT to implement for future reference in the same way we record decisions about the processes and tooling we DO implement."
- 2026-11-26T19:16:40Z: "that is getting captured somewhere that we are able to look it up later, right?"

**What was found.**
- Nothing held it before 2026-11-25. Result: PD (each decision with its measurement, command and falsifier) and the
  audit register (T259), with a landing refused when it adds a mechanism without an entry.
- The backlog is large: 267 mechanisms in force, 254 with no entry (AUD `audit-register.md`; T260, open).
- Declined options were not being recorded even after the rule: three had a measurement and no entry until the GM asked
  (T320, open). The performance checklist gained its question 7 that day (`docs/performance-checklist.md`).
- Follow-up reads are filed as their own trials: features 456 (feature size), 457 (builder handoff rate), 458 (the
  second tier's threshold).
- Before-and-after measurements that were owed and waited: T22 ("waits: a full day after T02-T21 land", still open) and
  T98.
- A decision reversed within hours by its own stated goal: the coverage amendment (kind 2), kept in PD with its figures.

**How to notice it unasked.** `make audits` (overdue entries first, and the BACKFILL list); a results file under
`dev/measurements/` that no entry names; an entry whose `last-audited:` is "never" or whose `measured:` is "unmeasured"
(`delegating-to-builders.md`, `research-switch.md`); an open task that "waits" on a measured day. Visible before the GM
asked: no on 2026-11-25 (no register existed); yes on 2026-11-26T19:16:40Z, when the three unrecorded measurements
were files on disk that nothing listed as unfinished.

**How to check it.**
1. For a change, find its entry: the question, the measurement with date and command, the alternatives, the falsifier
   and threshold.
2. Missing: write it in the same landing as the change, adopted or declined.
3. On its cadence, re-run the recorded command over the period since and compare with the threshold.
4. Past the threshold: tune the number or back the change out, and record that too.

**The trap.** A change that helps the tasks in front of it and is never looked at again - the GM's stated worry (GOAL,
second message: "overfitted some tuning to a couple of tasks that just happened to be getting worked").

---

## 17. Is the unit of work the right size?

**The question.** Are we giving one worker too much, or paying the whole overhead of a task for a one-line fix?

**The GM's words.**
- 2026-11-22T04:22:49Z: "Like, it sounds like what you're saying is that every individual task goes through the same process, but that feels like it is itself the issue."
- 2026-11-26T15:48:28Z: "I thought that we had already addressed the issue about builders running out of context. Is that still an ongoing concern that we are having to work around?!"
- 2026-11-25T14:19:21Z: "whether to have long-running features like the ones that we have been working for the last few weeks, or whether it is better to have small SpecKit features that get filed and then completely closed out"

**What was found.**
- Too small: each tiny defect paid a builder reading in, a replay, a closing run, a plan section, review rounds and a
  landing. Result: bundles (T141).
- Too large: of 97 builders, 27 (28%) hit the context cap or handed off; a brief of four or more jobs handed off 52% of
  the time against 16% at one or two, and one that began with a measurement 46% against 25%. Result: a brief is one
  task and at most three jobs; a claims round is its own dispatch (T237). The next day about one builder in fifteen
  reached the cap. Source: PD, "The builders' context cap stays at 300k".
- The coordinator's own hands are cheaper only for a one-turn edit: about half a small builder's tokens; past five
  minutes or several files, about 1.5M tokens (PD, same entry).
- Long-running against small features: no data yet; filed as a trial (feature 456).

**How to notice it unasked.** The context-cap guard's firings and handoff files; `make task-progress`'s context size
against the cap for each running builder; minutes a task against lines changed. Visible before the GM asked: yes - the
GM met a builder hitting its context limit in the session's own reports three times (2026-11-25T14:35:58Z,
2026-11-26T02:00:39Z [Q], 2026-11-26T15:48:28Z) before the brief's size was made a command. Not established for the
fixed cost of small tasks before the 2026-11-22 bundling question.

**How to check it.**
1. For recent workers, record jobs in the brief, files edited, whether it opened with a measurement, and whether it
   handed off.
2. Compare handoff rates across those groups (the M1 method, MEAS `2026-11-25/talk-measures/`).
3. For small tasks, split the task's clock into the fixed route and the work itself.
4. Set the size rule from the groups; make the dispatch command refuse an oversized brief (kind 10).

**The trap.** A rule of thumb read as a law: the six one-job briefs handed off half the time (3 of 6), and the groups
are small (PD says so). And a size rule that lives in a file: the session broke it four times in one day (kind 10).

---

## 18. What collides when things run side by side?

**The question.** If two of these run at once - two builders, two sessions, a test beside a build - what do they step
on?

**The GM's words.**
- 2026-11-26T18:42:49Z [Q]: "How do multiple builders filing their own tasks resolve when two builders each file a task and then it lands on the session clone?  Wouldn't that be an automatic merge conflict?"
- 2026-11-26T15:23:52Z [Q]: "do you feel like you have gathered or are currently gathering enough data to be able to know the difference between tasks editing the same files and tasks that are not?"
- 2026-11-26T16:01:53Z: "Doess it also catch unstaged files as well as modified-and-uncommitted ones?"

**What was found.**
- Shared single-valued state: in the first parallel trials one started-task mark was overwritten, two builders filed
  the same task number twice, and every carry conflicted on one review record and was merged by hand. Result: T254,
  T255, T256, T257 (AUD `started-task-mark-per-tree.md`, `task-numbers-one-writer.md`, `plan-review-merge-driver.md`).
- Shared files: 24% of same-day task pairs share a registry file and 37% of those edits meet in one region, because
  unrelated entries share one very long line (T300, open; MEAS `2026-11-26/file-overlap/m15-results.md`).
- Tests that fail only under load: three load-sensitive checks in one day (T104, T304, T314), each red in a gate and
  green alone.
- A "no", by the GM: no merge driver across sessions, since two sessions never work one feature (PD, "A merge driver
  ...", quoting 2026-11-26T18:45:05Z).
- A "no": the session's own edits stay in its clone rather than "worktrees always" (PD, "A session's own edits in a
  pool tree").

**How to notice it unasked.** A hand merge or a hand-moved mark in the transcript; a gate red that turns green on an
unchanged rerun; a landing held by another task's files. Visible before the GM asked: yes - each first appeared as the
session working around it by hand (marks moved for each landing in trials 2 to 5, AUD
`started-task-mark-per-tree.md`), and most were fixed without the GM asking; the GM's questions here probed for
collisions the trials had not yet met.

**How to check it.**
1. List everything two workers can both write: files, state under the shared git directory, temp directories, locks,
   the machine itself.
2. For each, count collisions in the recent parallel runs (conflicts, overwrites, waits).
3. For a test, run it alone and under load and compare.
4. Give each writer its own copy, or one writer and a lock; pin it with a two-writer test.

**The trap.** Reproducing a load failure by loading the shared machine: two builders held the load at 240 to 400 for
over an hour each, which slowed two batch gates and failed a third suite (T321). The GM noted it had skewed the day's
throughput numbers too (2026-11-26T19:50:10Z [Q]).

---

## 19. Is the work in the right order?

**The question.** If this fix makes everything after it faster, or tells us where the time goes, why is it not first?

**The GM's words.**
- 2026-11-20T12:35:26Z: "okay well let's prioritize those remaining improvement fixes, okay?  doing those first makes everything after them faster"
- 2026-11-26T02:03:55Z: "should we move that item up to or near the front, so it can apply to all of the other optimzations we're building at the moment?"
- 2026-11-26T18:57:03Z [Q]: "for putting the ones most likely to give is better measurements at the front of the line, followed by the ones most likely to increase our task throughput?"

**What was found.**
- 2026-11-20: after the first night the measurement half had landed and none of the six improvements (REQ's heading for
  that day). Result: performance work goes first, enforced - `make task-start` refuses other work while a performance
  task is open (T28); measurement tasks count as performance (2026-11-21T02:55:18Z).
- 2026-11-26: the audit register was built before the other optimizations so each arrived with its entry (T259).
- 2026-11-26: the builders' queue was written down in the GM's order, measurements first, then throughput
  (`specs/451-time-retro-and-efficiency/queue.md`).
- 2026-11-26: the parallelization question was settled before the next round of fixes, because the answer speeds the
  fixes (2026-11-26T15:29:06Z).

**How to notice it unasked.** Open tasks tagged `[perf]` while untagged ones land; a measurement task queued behind the
work it would measure; `queue.md`'s order against what is in flight. Visible before the GM asked: yes on 2026-11-20
(REQ's heading for that day records that the overnight report showed none of the six improvements landed); not
established for the later two.

**How to check it.**
1. List open tasks that speed up or measure the work itself.
2. For each, name the later tasks that would benefit and roughly how many.
3. Anything with many dependents and no blocker goes to the front; state the order and why.

**The trap.** A rule the GM believed was already in force and was not: "can we in general priotitize performance
improvements going forward?  I thought that was already a rule." (2026-11-20T12:36:33Z).

---

## 20. Is this arrangement still the right one, now that things around it have changed?

**The question.** We set this up one way for reasons that made sense then. We have changed a lot since. Does it still
make sense, or is there a different way to arrange it?

**The GM's words.**
- 2026-11-25T14:13:14Z: "our separate clone-based approach made sense when we first started, but as we have many different subagents working on different things in parallel, then perhaps work trees make more sense than clones"
- 2026-11-25T14:19:21Z: "And I think on balance, this is probably for the best, but that is an assumption worth questioning."
- 2026-11-26T16:05:50Z: "Should that be a real use case, though, now that we are using work trees for each builder?"

**What was found.**
- Clones against worktrees: a clone 3.0 s and 615 MB, a worktree 2.2 s and 288 MB, a cold build cache 13 to 14 GB either
  way. Decided: clones for sessions, pooled worktrees for builders (PD, "Clones for sessions").
- Must everything go through the task route: its own steps are about 2 of a small task's 43 builder minutes (5%) and
  17% of its tokens, and its review caught one real defect in eight. Kept (MEAS `2026-11-26/task-route/m11-results.md`).
- Stop hooks against a timer: the GM asked (2026-11-23T16:22:04Z [Q]) whether blocking hooks were "even the right
  approach, as opposed to something like a cron that fires every 5 minutes"; result: a periodic idle check, with Stop
  hooks blocking only for what must happen before stopping (T183).
- The dirty-clone landing path: 66 of 128 landings used it while builders shared the clone, and one of eleven since
  builders moved to worktrees, by mistake. Filed to retire it (T302, open).
- Open, unexamined: the session as orchestrator rather than worker, and which work should run as workflows
  (2026-11-27T01:02:01Z).

**How to notice it unasked.** A mechanism whose reason names a condition that no longer holds (a guard for "two writers
in one clone" after every writer has its own tree); a code path whose use has fallen to near zero in the event log; a
recent process decision in PD that touches the same ground as an older mechanism. Visible before the GM asked: not
established - no report lists arrangements against the conditions they were made for; the dirty-clone path's fall from
66 of 128 landings to 1 of 11 was counted only after the question.

**How to check it.**
1. State what the arrangement was for and what has changed since.
2. Count how often its original case still occurs.
3. Cost both arrangements on the same recent work: minutes, tokens, disk, and the tooling that would have to change.
4. Keep, change or retire; record it with what would reopen it.

**The trap.** None recorded as answered wrongly. The risk the GM names is the reverse of the others: changing an
arrangement for a small gain where all the tooling assumes it ("all of our tooling kind of revolves around the fact
that we are using clones", 2026-11-25T14:13:14Z).

---

## Questions the GM asked that fit no category

- 2026-11-20T03:36:03Z - whether the container's temp directory lives in RAM. Nearest is kind 13 (the same resource
  question, asked of memory); one instance.
- 2026-11-22T04:18:09Z - whether the task review ever rejects a task as not worthwhile, and whether it should. Nearest
  are kinds 8 and 9; what was found is not in the sources read (a withdrawal command came later, T359).
- 2026-11-24T13:45:04Z and 13:48:05Z, 2026-11-25T03:57:46Z - whether subagents inherit the session's model. A
  configuration question; result T216, T217.
- 2026-11-25T16:03:16Z - whether GitHub was having an outage. An outside-cause check.
- 2026-11-26T14:55:03Z - whether the session can message a running builder.
- 2026-11-26T14:50:15Z - whether a running task's time can be seen before it lands. Result: `make task-progress`
  (T293). It is a request for a report, used here as a signal source for kinds 15 and 17, not a kind of its own.
- 2026-11-26T17:10:08Z - a backup branch before landing, and how a builder count would be shared across several
  sessions (feature 459). Design input, not interrogation.
- 2026-11-26T03:18:12Z [Q] - whether everything is captured well enough to destroy the container and start fresh. A
  durability question; related results are T258 (the tooling-state repository) and the port-talk handoff file.
- 2026-11-26T17:17:25Z [Q] - whether the existing breakdown will show the two-tier change's before and after without
  being updated. Folded into kind 16; on its own it is a single instance.
- 2026-11-17T05:13:24Z, 2026-11-18T10:16:25Z, 2026-11-18T11:28:07Z, 2026-11-20T03:34:43Z - whether outputs were being
  held to exactness. These produced the rule that no port or change is held to its bytes (root `CLAUDE.md`). They are about the standard of work, not
  the process's speed, though they share kind 8's root (a difference treated as a defect).
- 2026-11-19T04:52:24Z - why the Python code was being read during the port when tooling had once prevented it. A lost
  safeguard; nearest is kind 10 (one instance of an enforcement that had gone missing).
- 2026-11-22T20:41:55Z, 20:43:11Z, 2026-11-24T15:30:52Z [Q] - asking that items which are not open decisions stop being
  listed at every stop. Reporting noise; nearest is kind 14.

## What the catalog cannot support

- **The quotes rest on two sources, not one.** Five of the sixty quoted lines above, and nine further citations (all marked `[Q]`), are not in S1; nor is the GM's second goal message, which this file quotes from GOAL. They come from
  the session transcript's queue records. The repository's own copies of some of them (REQ, PD) are second-hand - copied
  from a task line by a builder "who did not hear them", with that line's ellipses - so this file quotes the transcript
  instead. The transcript does not outlive its container.
- **The session's side of each exchange was not read.** S1 holds only the GM's messages. Where a finding is described
  as "what the session answered", it comes from a record (PD, AUD, REQ, a task line), and where no record holds it this
  file says "not in the sources read" (the answers to the GM's 2026-11-21T14:40:11Z and 2026-11-25T05:18:31Z questions about obvious improvements, the
  fate of task time estimates, the change the GM declined on 2026-11-23T18:06:15Z, the 2026-11-22T04:18:09Z answer).
- **"Was the signal visible before the GM asked" is mostly inferred.** It is established from records for kinds 2
  (the 123.3 figure was in the report), 3 (Phase lines dated from T05), 6 (the guard log's count), 9 (the session
  reported "52 follow-ups" itself) and 15 (the report's own lines). For the others it is this file's reading that the
  data existed, not a recorded finding that someone could have seen it.
- **Kinds that overlap.** 2 and 15 share their newest instance (the tree-idle measurement): 2 asks whether a step holds
  anything up, 15 whether workers stand idle. 1 and 12 are the same question at two scales (the window, one step). 5
  and 6 both ask about a number; 5's is set by a resource and found by sampling, 6's by a choice and found by varying
  it. 8 and 9 share the cascade work: 8 classes one safeguard's findings, 9 counts work opened against work closed. A
  reader who merges each pair gets sixteen kinds; the measurement steps are what keep them apart here.
- **Kinds with thin support.** Kind 19 (order) has clear quotes but its instances are scheduling decisions, not
  measurements; no figure shows what the right order saved. Kind 20's orchestrator and workflow questions are open with
  nothing measured. Kind 7's "is the check failing early or late" rests on one question (2026-11-26T15:56:44Z) whose
  subject this file infers to be the unfinished-carry check. Kind 18's load-sensitive tests have no question of the
  GM's behind them, only agreement (2026-11-26T16:23:26Z, "I agree with prioritizing the test that fails under load
  being fixed").
- **Traps recorded only as the GM's account.** Kind 1's trap (the earlier step-back reviewer optimizing single tasks)
  is the GM's description in GOAL; no measurement of what it did was read. Kind 20 has no recorded trap.
- **Figures the sources state two ways.**
  - Builders three at once on the night of 2026-11-21: 26% (153 of 580 minutes) in T88's line, 33% (191 of 580) in
    T98's.
  - "23%" is two unrelated figures: the GM's "23% of our time waiting on gate runs" (2026-11-22T13:17:13Z, quoting a
    session figure not found in the records read) and the pool trees' 23% idle (2026-11-27).
  - Pop-up edits "really needed": 24 in the GM's question (2026-11-23T19:39:55Z), 20 of 30 "corrected something wrong"
    in REQ's later account.
  - The 45 blocked plan-review rounds of the reversals measure are "code that built on what was there" in PD and "a
    real defect in the approach" in MEAS `2026-11-26/task-route/m11-results.md`.
  - The feature-unify before and after (171.1 s, 51.6 s) are one sample each under different load, by the record's own
    caveat.
- **Not counted.** How many tasks each kind produced was not tallied; the GM's "many dozens of tasks" is consistent
  with the 391 task lines of feature 451 but no task-to-kind mapping was made.
- **The GM's own example is unexamined.** The per-test time threshold named in GOAL's second message has no
  measurement or task in the sources read; it stands as an example of kind 6 with nothing found.
