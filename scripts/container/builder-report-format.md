# The builder's report format

Load this file when: you are a builder at your stop point, about to write your report; or you are changing what a builder reports.

Adopted 2026-11-26 on the GM's pre-approval (a fixed short report format, adopted if shorter with nothing lost;
`docs/process-decisions.md`, "The builders' report has a fixed format"). Measured on 38 builder reports of 2026-11-25/26: fourteen
re-expressed in it came out at 55% to 98% of their length with no item the coordinating session went on to use lost
(`dev/measurements/2026-11-26/report-format/m14r-results.md`). It lives in its own file, read once at the stop point: pasted
into every brief it would cost about half of what it saves.

Then report, in this FIXED FORMAT (agenda item 14, measured 2026-11-26 on 38 reports) - these fields, this order, a field with nothing to say written `none`:
 STATE: one line - the task and what it now does; `STOP POINT met` | `NOT met: <what is open>` | `stopped before building: <why>`; the tree; "nothing staged or committed"; the handoff file's absolute path if you wrote one.
 BUILT: at most 8 bullets of at most 400 characters - the cause as proved, the rule as built, each deviation from the brief with its reason, each defect fixed in passing. A figure the session will repeat to the GM is given; what the plan section says at length is not repeated.
 MEASURED: each figure the brief asked for, one line, with its unit. Of the tables the brief asks for, the first whole (zero rows and repeated columns dropped); every other table, and any output over 40 lines, as its scratch file's path and its five largest rows.
 RED-FIRST: one line a test or suite - `<name>: <n> passed, <m> failed on the old code; <n'> passed after`; then `not run red: <what>`.
 CHECKS: one line - `make builder-checks` (the first tier) GREEN or RED, its wall seconds, the number of runs; then one line for each exception ONLY: a red, a red reported apart, an escape taken (its name), a check not run. A check the STOP POINT lists that simply passed is not listed.
 PLAN REVIEW: `CLEAR | BLOCKED | accept (arbiter)`, the round, the decisions counted; every open objection in full with the fix it asks for; one line for each earlier round (what it blocked on) and for each note left unedited to keep the verdict.
 CLAIMS: `none owed, none touched`, or the keys touched or restated, what `make claims-owed` lists, and the bundle's path.
 COMMIT: the tree; each NEW (untracked) file or directory by path; `modified: <n> tracked files` (not listed: `git add -u` takes them); a file to leave out, with why; words the commit message must carry.
 FOR THE SESSION: one line for each thing the session must do, decide or know that no other field says - a command to run after the landing, a section not to edit again, words to confirm, a friction for the parallel-work notes, a note addressed to it. No cap.
 CANDIDATES: one line for each thing you found and left, which YOU FILED from your tree (`make task-add F=<feature> TITLE="..."`, 451 T289: its id is one no other tree of the clone can take) - `filed: T<n>`, then its title with its paths and figures. One the command refused is `NOT filed: <its refusal>`, then the title. No cap.
No other section: no "how to test", no list of modified paths, no passing check, no restatement of the plan section.
