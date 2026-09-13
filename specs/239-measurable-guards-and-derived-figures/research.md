# Feature 239 - research

**Every figure below is either produced by a harness committed under `measure/` - named in its section,
with the key it writes into `measurements.json` - or is a JUDGMENT over the review reports, which is
said where it happens.** That distinction is this feature's own subject, so the page keeps it visibly.

## R1 - where 208 minutes went (measured 2026-09-13)

The session that delivered feature 236's second amendment spent **208 minutes**
(`m:amendment-wall-minutes`) between the GM's ruling and their instruction to land it. `measure/time_census.py` reads the session's own transcript,
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

Keys for the four blocks the argument rests on: `m:amendment-replay-minutes`,
`m:amendment-idle-minutes`, `m:amendment-latency-minutes`, `m:amendment-test-minutes`. The census
takes `--record`, so these are re-derived rather than retyped.

The change itself was **309 lines added and 18 removed** in the hook and the module it grew
(`m:amendment-guard-lines-added`; 455 and 43 across all of `scripts/`,
`m:amendment-scripts-lines-added`, from `measure/change_size.py`). **Two of the three largest blocks
are tooling rather than thinking**: the replays cost what they cost because nothing could evaluate a
guard cheaply (R3) and nothing froze the corpus (R4). The third, the review rounds, is half tooling -
R2 classifies what they found.

## R2 - what five review rounds found, classified (a judgment, 2026-09-13)

**This is a classification, not a measurement**: the twenty findings of the five `spec-fidelity`
VERIFY rounds on feature 236's second amendment, read from the round reports in this session's
transcript (`~/.claude/projects/-diagram/de91c2c7-81d4-47af-b7e8-31fb61ee8c11.jsonl`) and sorted by
what a fix required. An independent reviewer re-derived the same assignment from the same reports.

**A FIGURE - stale, unreproducible, or measured one way and stated another (10).** Round 1: the window
measured with a prefilter the hook had corrupted; the dash half never priced; a `2.2 s` that was never
measured; the predicate's class label and its split counts. Round 2: the split stated 9/44/2 against a
measured 9/42/4. Round 3: a residue figure judged by the hook's own output; `201 of 545` left
standing. Round 4: D9's counts superseded; `19/4` not reproducing. Round 5: the same `19` surviving in
a fourth place.

**A DEFECT in the implementation (4).** The exemption judged by every path a command mentions; a
suffix roster that dropped every `Makefile`; write targets read from raw text (11 verdicts wrong in
the record); the import stub whose arity silenced the whole guard.

**The spec and the code saying different things (3).** FR-007c dropping a clause the hook still used;
SC-006 naming a literal path where the record used four shapes; a criterion true only of the cases its
own tests exercised.

**STALE TEXT a change falsified (3).** A docstring describing the deleted rule; two statements the
amendment falsified; `git commit` listed among unresolvable targets.

**Half the findings were arithmetic.** The four defects are what an independent reviewer is for - one
would have shipped a guard that switched itself off silently. What the last two rounds found is worth
stating exactly, because it is the case for section C and it is smaller than "nothing but arithmetic":
**three figures and two stale sentences**, none of which changed the shipped behavior.

## R3 - what a guard decision costs, spawned and called (measured 2026-09-13)

`measure/decision_cost.py` lifts the hook's own Python program out of its shell string, times the
shipped hook over the 60 longest real commands it acts on, and then times the SAME program compiled
once and executed in process with its stdin redirected per command - which is what FR-001 makes
permanent, and which is why the figure can be taken before the extraction exists.

| over all 560 frozen commands | per command | key |
|---|---|---|
| the hook as it runs today | **144 ms** | `m:decision-spawned-ms` |
| the same program, compiled once, called in process | **7.0 ms** | `m:decision-in-process-ms` |
| a bare `python3 -c pass` | 19 ms | `m:bare-python-spawn-ms` |

That is **21x** (`m:decision-spawn-ratio`), and over the whole window **80 s against 3.9 s**
(`m:window-spawned-s`, `m:window-in-process-s`, `m:frozen-window-commands`). The cost is not process
startup - a bare spawn is 19 ms (`m:bare-python-spawn-ms`) - it is the hook rebuilding its whole world per command. Nine passes
were needed while the questions were being settled, which is where the replay time went.

Every timing entry carries the load average at both ends of its run and the sample it measured, and
across three repeats on an unchanged tree the figures spread by 3.4% (`m:timing-run-to-run-drift-pct`) -
inside the 0.10 default band FR-011a sets.

**The ratio depends on the command MIX, and the first measurement of it was taken on a biased
sample.** Over the 60 LONGEST commands in the window the ratio is only 4x: a 79 KB heredoc gives the
decision real work to do while the spawn overhead stays constant. Over a sample of the commands the
guard ACTS on - short ones, mostly - it was 37x. The figure recorded is the one a bench actually
faces, the whole window, and this paragraph is why it is not the largest of the three.

## R4 - the corpus was never frozen, and the program cannot be imported (measured 2026-09-13)

**The frozen corpus, and what it costs to keep.** `measure/freeze_window.py` froze the window into
`scripts/fixtures/command-window-2026-09-13.json`: 560 commands (`m:frozen-window-commands`), 2.7 MB of
command text and 3.0 MB as the JSON on disk. The ten largest commands are 38-79 KB heredocs; capping a
command at 10,000 characters would keep 88% of them for 1.04 MB, which spec D6 prices and rejects.

**Nothing froze the window.** Each of the nine passes re-read the transcripts to rebuild the same
command list, and two of them ran against a prefilter this very hook had corrupted - its literal
dashes were rewritten to hyphens as the file was saved, so it matched any command containing a spaced
hyphen. The scan is only seconds warm, so this is not the expensive half; it is why every new question
meant a fresh full pass rather than a query against a file.

**The decision cannot be imported.** `measure/guard_census.py` counts, for every `scripts/*.sh`, the
lines strictly between the delimiters of each inline Python block (the convention is in its docstring,
because the first hand count of this got two files wrong in both directions):

| guard | program lines | blocks | file lines |
|---|---|---|---|
| `house-style-hooks.sh` | 275 | 1 | 367 |
| `pair-hooks.sh` | 86 | 5 | 454 |
| `repo-safety-hooks.sh` | 67 | 1 | 196 |
| `no-poll-hooks.sh` | 48 | 2 | 218 |
| `_guardlog.sh` | 40 | 1 | 141 |
| `source-block-hooks.sh` | 35 | 1 | 116 |
| `finished-run-hooks.sh` | 34 | 1 | 85 |
| `make-only-hooks.sh` | 33 | 2 | 200 |
| `readme-hooks.sh` | 23 | 1 | 91 |
| `discard-hooks.sh` | 18 | 1 | 146 |
| `gate-hooks.sh` | 13 | 1 | 174 |
| `guard-file-hooks.sh` | 12 | 2 | 172 |
| `agent-stall-hooks.sh` | 7 | 2 | 114 |
| `sync-with-main.sh` | 5 | 1 | 440 |
| `measure-hooks.sh` | 4 | 1 | 187 |

**15** guard scripts carry one (`m:guards-with-inline-python`; **25** counting the test scripts,
`m:guards-with-inline-python-including-tests`), and the house-style hook is by far the largest at
**275** of its **367** lines (`m:house-style-program-lines`, `m:house-style-file-lines`).

**And a quoted program has a failure mode of its own.** One apostrophe in a comment ends the string,
the program then fails to parse, and the wrapper turns that into silence. It happened **twice** in one
evening on this file, each time presenting as every case failing at once, and the file already carried
a warning about it from an earlier incident.

## R5 - what a reviewer has to do to check a figure (a judgment, 2026-09-13)

Read from the same round reports. In **every** round the reviewer measured rather than trusted, which
is why the ten stale figures were caught. In **four of the five** it had to write the harness itself -
its round-3 report names five scripts it wrote under its own scratchpad, and rounds 1, 2 and 5 each
rebuilt a replay of the window. The exception is round 4, whose dispatch named the harness the session
had by then written down: that report says it re-ran that script, and its verdict was that every
figure reproduced "to the command".

So the cost this feature removes is not the reviewer's skepticism - it is the reviewer rebuilding the
same instrument four times because the figures arrived as text with no route back to the run.
