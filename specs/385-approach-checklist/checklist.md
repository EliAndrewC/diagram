# The approach checklist - v1 (draft, 2026-10-17)

Load this file when: starting a task of feature 385 (its plan section's **Approach** block answers part A), or when the work
resists (part B); part C holds the execution habits. v1 is drafted from the project's doctrine and the GM's request; the audit (`audit.md`) and each task's retro
(`retro.md`) amend it. Each item names where it comes from; `audit #n` is pitfall n of `audit.md` (the GM's messages,
the round arbiter's rulings and the feature reports of the two weeks to 2026-10-17).

The checklist is a way to ask the questions in time. It is not a license to drop rules when they are inconvenient: a rule
loosened, excepted or retired carries its reason at the point of change and on the research record's drawing page, and a rule
the research or the GM set is changed only by new research or the GM.

## A. At task start (the Approach block)

Answer each in writing in the task's plan section. One line each is enough where one line is true.

1. **The goal, in the world.** What will the reader of the map or sheet see when this task is done, and what real process
   produces that thing? (*Footpaths are the routes people walk round what already stands; that is why lanes are laid after
   the homesteads* - the GM, 2026-10-17.)
2. **The constraints, listed.** Every rule, threshold, band, cap and seed set the task will be judged against: validators, the
   lane law's rules, size bands, reaches, the cohort.
3. **Where each comes from - checked, not remembered.** For each constraint: **R** (research: name the question file its
   `Research:` claim cites), **G** (a GM ruling: quote and date it), or **O** (ours: an implementation detail or a
   convenience). Find it - grep the claim, `git log -S` the number - before answering. An **O** constraint is a knob to move,
   never a target to defend (CLAUDE.md, "Room before packing"; *the 700 ft reach was O, and hours went into meeting it* -
   audit #1, four cases). For a **G**, quote the words and ask how hard they are: a preference ("all else being equal, try
   this first") is a tie-break, not a limit (audit #10: *"My 'ruling' on preferring to stay close was not a hard
   requirement"*).
4. **What each R or G rule describes, and whether it holds here.** Research usually describes the typical case. Does the
   rule still describe the world in the situation the task meets - an obstruction, a slope, a map edge, a crowded site?
   (*Lanes meet at broad angles where nothing is in the way; a rock in the way makes a sharp meeting natural.*)
   **And is the refusal itself right?** If the map broke this rule here, would a reader of the research call the place wrong?
   If not, the rule is a preference - a tie-break, not a refusal. (T03: seed 21 was refused for a farmer's path 3-6 ft off his
   OWN garden fence; nobody would call that wrong. The blind Approach listed the fallback but never asked this - SC-006.)
5. **The order of operations.** Does the plan respect the order things arose in the world? Nothing placed earlier moves to
   suit something placed later (homesteads before lanes - GM 2026-10-02 and 2026-10-17; paved roads excepted).
6. **The exits, each weighed.** Before choosing to conform, name what each of these would be for this task, and pick with a
   reason:
   - (a) refine an **O** number;
   - (b) a principled exception to the rule (*a sharp meeting an obstruction forces is lawful*);
   - (c) a new rule that dissolves the case (*two lanes side by side become one path, so they never meet*);
   - (d) more room - a bigger homestead, wider spacing, within the research (GM 2026-10-12);
   - (e) conform as the rule stands.
7. **The search smell.** Is the plan a search, packing or repair loop against fixed constraints (re-dealing seats, shifting
   features a little, retrying seeds)? If yes: which constraint, moved within the research, would turn it into a direct
   construction? (Features 297 and 302 each won by construction over carve-and-repair; the GM's gap rule between homesteads
   dropped the lane access search entirely, 2026-10-03 - audit #2, #3 and the approaches kept.) Is anything reserved in
   advance that the space already provides? (The exit strip and field way, dropped 2026-10-04.)
8. **The budget.** About how long should this task take? Twice that is a trigger for part B.
9. **Done, measured.** What shows the task done - the test that is red now, the seeds, the map - and the baseline it is
   compared with (taken at HEAD, CLAUDE.md "No known regressions").

## B. When the work resists

Triggers: a seed or cohort the change refuses; the same validator failing on a second attempt; a second red gate; the hourly
step-back; the task past twice its budget; an approach about to change. Answer before the next attempt, dated, beside the task.

1. **What exactly is refusing?** The rule, the seed, the place on the map. Is it the same rule as last time? **Look at the
   geometry before naming a cause** - dump the lanes and what stands near them, or bisect by commit: a refusal names the TEST,
   not the ground (T01: three causes guessed from refusal text were wrong; each dump or bisection answered in one run).
2. **A3 again, for that rule, freshly checked.** R, G or O? Asked now, not carried over from task start.
3. **A4 again.** Does the rule describe the world at the place it is refusing? Look at the map there.
4. **Is the next fix moving something placed earlier to suit something placed later?** If yes, stop: back to A6.
5. **Tuning or changing?** The third tuning of the same thing (a weight, an order, a retry count) is a step back to A6, not a
   fourth tuning.
6. **The one-sentence test.** Told what is being done in one sentence, would the GM ask "why is that a rule?" or "why not just
   make it bigger?" If so, answer that question first.
7. **The next step is a measurement.** Name what it measures (CLAUDE.md: persistence means progress, not changes).
8. **Before offering routes, or asking the arbiter or the GM to choose:** is every route measured against the pool, the
   cohort and the known refusals already recorded (the found rows)? A ruling made on a partial matrix was superseded 41
   minutes later (audit #7). Can the research decide it? Then it is not a question (audit #12).
9. **After a ruling:** is the next step one the ruling names? If its probe failed, take the step it names next; do not
   switch to a route it did not name, or write prose as if the question were settled (audit #8).

## C. Habits the audit found (execution, not approach)

1. **A checked page is edited once per round.** Gather every suggestion, apply them together, check once (audit #5: the
   privy page took about eight rounds for a few sentences; 374 spent 679 check dispatches). A fix ONE check asks for on a page
   others are keyed on is applied only after every check of that page has returned, so they re-run once together (T01: a
   one-word vocabulary fix re-owed ten pop-ups, two record checks and 229 claims).
2. **The fast test that catches it now.** Run per change the quick tests that would fail at the gate, so a failure surfaces
   in the wave that made it, not at the batch's close (audit #6: one test stale since wave 57) - and `make quick` before every
   `make done` (T01: a lint red gate the quick suite would have caught).
3. **A drawing page, plate or doc draws what the code does,** checked against one real run (audit #11).
4. **New work or a changed reading of the GM's words goes in the turn's final message**, never only mid-stream (audit #9).
6. **Nothing is written to the tree while a gate runs** - not a record, not a ledger row, not a fix to the wait itself; queue it
   and write it after the verdict (T01: two gates voided by a write during the run).
7. **A cohort's count is not its seed set.** Compare failing seeds, rule by rule with their counts, against the same seeds at
   HEAD (`make cohort` prints it since T03); a pass count hid two failing seeds and a changed denominator (T03: "59/60" was
   `N=54`).
8. **Times in a log are read from the event log, never written from memory** (T03: a decision log an hour off, caught by the
   hourly step-back).
5. **A tripwire is read before it is obeyed.** When a round cap fires, check first that the owing diff changed visible words of
   this unit and that the rounds counted are this feature's: of 106 round-cap accepts, 27 were owed only by a later
   edit and 13 by a counting or bundle error (audit #13). A tripwire that fired on tooling error is a tooling fix, made then.
