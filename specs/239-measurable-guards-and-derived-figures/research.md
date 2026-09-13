# Feature 239 - research

Everything here was measured on this repository, by a command that is committed beside it. Where a
figure came out of a one-off harness, the harness is named and the run is dated.

## R1 - where 208 minutes went (measured 2026-09-13)

The session that delivered feature 236's second amendment spent **208 minutes** between the GM's
ruling and their instruction to land it. `measure/time_census.py` reads the session's own transcript,
pairs every `tool_use` with its `tool_result`, counts the gap from a result to the next assistant
message as model latency, and reports the remainder as idle:

    python3 specs/239-measurable-guards-and-derived-figures/measure/time_census.py \
        de91c2c7-81d4-47af-b7e8-31fb61ee8c11 --from "exempt that sed shape" --to "go ahead and land it"

| where | min | share | calls |
|---|---|---|---|
| replaying the command window | 78.9 | 37.9% | 40 |
| idle, waiting on the five review rounds | 78.0 | 37.5% | - |
| model turn latency | 29.3 | 14.1% | - |
| tests and checks | 15.0 | 7.2% | 44 |
| a foreground `sleep` on a background run | 6.0 | 2.9% | 1 |
| edits, git, the push, everything else | 0.9 | 0.4% | 129 |

The change itself was about 40 lines of code. **Two of the three largest blocks are tooling, not
thinking**: the replays cost what they cost because nothing could evaluate a guard cheaply (R3), and
because nothing froze the corpus, so each new question re-derived the whole window (R4). The third,
the review rounds, is half tooling: R2 classifies what those rounds actually found.

## R2 - what five review rounds found, classified (2026-09-13)

The twenty findings of the five `spec-fidelity` VERIFY rounds on feature 236's second amendment,
read from the round reports in the session transcript and classified by what a fix required:

| class | findings | what they were |
|---|---|---|
| **a FIGURE that was stale, unreproducible, or measured one way and stated another** | **10** | the window measured with a corrupted prefilter; the dash half never priced; a `2.2 s` that was never measured; the split stated 9/44/2 against a measured 9/42/4; a residue figure judged by the hook's own output; `201 of 545` left standing; D9's counts superseded; `19/4` not reproducing; the same `19` surviving in a fourth place |
| a DEFECT in the implementation | 4 | the exemption judged by every path a command mentions; a suffix roster that dropped every `Makefile`; write targets read from raw text (11 verdicts wrong); the import stub whose arity silenced the whole guard |
| the spec and the code saying different things | 3 | FR-007c dropping a clause the hook still used; SC-006 naming a literal path where the record used four shapes; a criterion true only of the cases its own tests exercised |
| STALE TEXT a change falsified | 3 | a docstring describing the deleted rule; two statements the amendment falsified; `git commit` listed among unresolvable targets |

**Half the review findings were arithmetic.** The four defects are what an independent reviewer is
for - one of them would have shipped a guard that switched itself off silently. The ten figures are
what a script can check, and they are the reason the rounds went to five: rounds 4 and 5 found
nothing else at all.

## R3 - what a guard decision costs, spawned and in process (measured 2026-09-13)

Measured over the 60 longest real commands the house-style hook acts on, and over 20 bare spawns:

| | per command |
|---|---|
| the hook as it runs today (bash wrapper + `python3 -c` + its imports and 44 regex compilations) | **164 ms** |
| a bare `python3 -c pass` | 20 ms |
| a bare `bash -c true` | 2 ms |
| the same decision called IN PROCESS | **3.7 ms** |

Over one 558-command window that is **92 s against 2.1 s**, a factor of 44, and the gap is not process
startup: it is the hook rebuilding its whole world per command. Nine passes were needed while the
questions were being settled, which is where 78.9 minutes went.

## R4 - the corpus was never frozen, and the program cannot be imported (measured 2026-09-13)

**Nothing froze the window.** Each of the nine passes re-read 1,034 transcripts (1,749 MB) to rebuild
the same command list. The scan is only 8 s warm, so this is not the expensive half - but it is why
every new question meant a fresh full pass rather than a query against a file.

**The decision cannot be imported.** `scripts/house-style-hooks.sh` is 366 lines, **273** of them a
Python program inside a single-quoted shell string. Nothing can `import` it, so a measurement must
spawn it (R3) and a test can only drive it as a subprocess. The shape is not unique to this guard: a
census of `scripts/*.sh` finds inline Python in **16** files, the largest being `repo-safety-hooks.sh`
(88 lines) and `pair-hooks.sh` (67).

**And a quoted program has a failure mode of its own.** One apostrophe in a comment ends the string,
and the guard then fails to parse - which the wrapper turns into silence. It happened **twice** in one
evening on this file, each time presenting as every case failing at once, and the file already carried
a note warning about it from a previous incident.

## R5 - what a reviewer has to do to check a figure (2026-09-13)

In **four of the five rounds** the reviewer built its own replay harness to check the numbers it had
been handed - its round-3 report names five scripts it wrote under its own scratchpad, and rounds 2, 4
and 5 each re-derived the window the same way. That is the right instinct and it caught four stale
figures, but it is rebuilt from scratch every round because the figures arrive as text in a document
with no route back to the run that produced them.

The one round where this was cheap is the one where the harness was committed: by round 4 the session
had `final2.py` in the scratchpad and named it in the dispatch, and the reviewer re-ran it rather than
rewriting it. Its verdict that round was that every figure reproduced "to the command".
