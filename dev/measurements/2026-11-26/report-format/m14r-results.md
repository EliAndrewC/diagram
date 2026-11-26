# m14r - a fixed short report format for builders: measured 2026-11-26 (agenda item 14)

Scripts beside this file: `m14r-reports.py` (extract), `m14r-parts.py` (parts, cache shares, use probes), `m14r-windows.py` (what followed each report), `m14r-check.py` (the fourteen re-expressions, both used-item checks, the saving). Data: `m14r-extract.json`, `m14r-reports.txt` and `m14r-windows.txt` (the first 33); the re-expressions `m14r-formatted.md`; the format `m14r-format.txt`.

## Sizes (38 long builder messages from 37 builders named `Build|Finish 451 T...`, 2026-11-25/26 UTC; tokens = chars/4, an estimate not calibrated against the API's count)
- 33 arrived labeled "finished"; 5 more were found late: 4 arrived labeled "is waiting on its own background work" (3 of them that builder's only report) and 1 as an attachment record. The 5 are in the sizes and the saving; the use tally below is hand-read on the first 33 only.
- Median 4,415 chars (about 1,100 tokens); range 1,459-14,469 chars (365-3,620 tokens); total 175,358 chars (about 43,800 tokens). By chars/4 the agenda's "2k-5k tokens" is high: one report passes 2k (R3, whose brief asked for two tables verbatim).
- Share of all report text by part (keyword rules on paragraph and bullet labels; median chars where present; reports carrying it, of 38):
  built / cause / measured 43.5% (1,761; 37) | paths 12.8% (597; 36) | plan review 8.2% (450; 24) | checks 8.0% (440; 30) | candidates 7.1% (616; 21) | caveats and notes 5.5% (320; 25) | status line 4.7% (206; 38) | red-first 4.6% (302; 24) | handoff "next" lists 3.1% (918; 6) | claims 1.9% (146; 21) | verify 0.6% (226; 5).

## What the session used (hand-read on the first 33, from its next turns up to the landing or the successor's dispatch)
| part | used | not used |
|---|---|---|
| status line | 33/33: land, or brief a finisher | - |
| built / cause / measured | 32/32, in the commit message, the NOTE or the GM's summary, at partial depth | by-file breakdowns, internals; R3's second table (4.4k chars, 0 rows relayed; 15 rows of its first were, 5 more summed) |
| red-first | counts quoted in the NOTE 8 times (R19, R20, R21, R22, R24, R28, R29, R32); as the bare word "red-first" about 13 | - |
| checks | green or red as go/no-go 33/33; wall times relayed (R22, R27); a red or a red-apart acted on (R7, R21) | each passing check's own line (`--check-drawn` silent, guard-messages clean, quick re-run, Occasions written): 0 uses in 26 |
| plan review | verdict in the NOTE about 28; every open objection copied into the successor's brief 7/7; round history relayed 3 | - |
| claims | non-empty 2/2 (R18, R21: the claims round dispatched from it); "no claims" as a word | - |
| paths | NEW files named in `git add` 10 (R1-R17); the tree always | the list of modified paths 0/32 (`git add -u`; from R19 on `git add -A <top dirs>`); "leave out" 0/3 |
| candidates | filed as tasks with their paths and figures 16/19 (T253, T260, T262, T264-65, T269-71, T275-77, T286-88, T290, T303-04, T306 ...) | 3 not traced |
| caveats / for the session | acted on 15/24 (R5 sync-in, R6 the deferred command, R9 the commit reason, R18/R30/R33 ids to file, R27 words to confirm, R31 ledger rows ...) | 9 not traced (untracked-file notes, R12's mismatch, the host's disk note x3); kept anyway - a caveat that stops an action leaves no trace |
| handoff "next" lists | 5/5 (the finisher's brief) | - |
| verify / how to test | 0/5 | all |

## The format (final, v2; in place of the builder brief's "Then report: ... the exact paths to commit."; 2428 chars)
```
Then report, in this FIXED FORMAT (451 T<n>, measured 2026-11-26 on 38 reports) - these fields, this order, a field with nothing to say written `none`:
 STATE: one line - the task and what it now does; `STOP POINT met` | `NOT met: <what is open>` | `stopped before building: <why>`; the tree; "nothing staged or committed"; the handoff file's absolute path if you wrote one.
 BUILT: at most 8 bullets of at most 400 characters - the cause as proved, the rule as built, each deviation from the brief with its reason, each defect fixed in passing. A figure the session will repeat to the GM is given; what the plan section says at length is not repeated.
 MEASURED: each figure the brief asked for, one line, with its unit. Of the tables the brief asks for, the first whole (zero rows and repeated columns dropped); every other table, and any output over 40 lines, as its scratch file's path and its five largest rows.
 RED-FIRST: one line a test or suite - `<name>: <n> passed, <m> failed on the old code; <n'> passed after`; then `not run red: <what>`.
 CHECKS: one line - closing-checks GREEN or RED, the final run's wall seconds, the number of runs; then one line for each exception ONLY: a red, a red reported apart, an escape taken (its name), a check not run. A check the STOP POINT lists that simply passed is not listed.
 PLAN REVIEW: `CLEAR | BLOCKED | accept (arbiter)`, the round, the decisions counted; every open objection in full with the fix it asks for; one line for each earlier round (what it blocked on) and for each note left unedited to keep the verdict.
 CLAIMS: `none owed, none touched`, or the keys touched or restated, what `make claims-owed` lists, and the bundle's path.
 COMMIT: the tree; each NEW (untracked) file or directory by path; `modified: <n> tracked files` (not listed: `git add -u` takes them); a file to leave out, with why; words the commit message must carry.
 FOR THE SESSION: one line for each thing the session must do, decide or know that no other field says - a command to run after the landing, ids to file before the tick, a section not to edit again, words to confirm, a friction for the parallel-work notes, a note addressed to it. No cap.
 CANDIDATES: one line each, written as a task title with its paths and figures; `filed: T<n>` for one you filed. No cap.
No other section: no "how to test", no list of modified paths, no passing check, no restatement of the plan section.
```
- v1 failed: its 6-row cap on a table lost 9 rows of R3's category table that the session relayed to the GM and 5 more it summed. v2 keeps the first table whole (zero rows and repeated columns dropped) and sends only further tables to a file.

## The fourteen, re-expressed by hand (chars)
- Eight longest: 56,807 -> 31,341 (55%; without R3 58%). R3 14,469 -> 6,644; R13 6,635 -> 3,873; R4 6,465 -> 3,915; R10 6,368 -> 3,349; R9 6,019 -> 2,797; R12 5,662 -> 2,619; R6 5,630 -> 3,328; R30 5,559 -> 4,812.
- Four typical: 15,948 -> 11,065 (69%). R20 4,410 -> 2,998; R16 4,371 -> 3,071; R22 3,554 -> 2,564; R17 3,613 -> 2,418.
- Two short ones: 4,331 -> 4,265 (98%). R11 1,459 -> 1,482 (longer); R31 2,872 -> 2,783. A short stop-note gains nothing.
- Used items lost: none after correction. Two checks: (a) my own list of 210 used items (written after the re-expressions, by the same hand - not independent): all present; (b) mechanical and independent: every backticked span, path, T-id, hex key and number found in BOTH the original and the session's full following rows must be in the re-expression. (b) caught 3 slips of my first pass - R3's handoff path given relative where the session used the absolute one, R12's "405 T32 D4" (in the commit message), R20's `make claims-checked` (in the NOTE) - each had a field, was restored, and the sizes above are after. What (b) still lists is ruled not a use: stop-point command names the session's brief template repeats (`make claims-triage`, `--check-drawn` ...), a tree path in another spelling, numbers that coincide (14, 17, 19), a modified path the session met through `git diff`.
- BUILT ran 5-7 bullets, longest 351 chars; FOR THE SESSION at most 4 lines; CANDIDATES at most 10.

## The saving (turns = the session's API calls from a report's arrival to the next compaction or the transcript's end)
- Turns a report was re-read over: median 204, range 17-621. Measured cache-read share of input over those turns: 99.6% before the compaction, 99.5% after - so "re-reads are cache reads at about a tenth" holds.
- Today the 38 reports cost 11.4M token-turns, 2.0% of the session's 558M input tokens over those turns.
- Saved: 4.15M token-turns raw (the fourteen measured 2.43M - R3 alone 1.03M; the other 24 estimated 1.71M: no cut under 3,000 chars, else the typical 31%) = 0.74% of the session's input; weighted at 0.1: about 0.41M input-token equivalents for the two days, plus 14.8k tokens once at arrival (18.5k at the 1.25x cache-write rate).
- The format's own cost: pasted into every brief it adds about 570 tokens to each builder's context, re-read over the builder's turns: 3,470 tool uses over these builders, about 1.98M token-turns - 48% of the saving. Kept in its own file that the builder reads at its stop point (one line in the brief), about 0.04M.

## Verdict against "shorter with nothing lost": ADOPT, with format v2, read at the stop point from its own file
Shorter (31% on typical reports, 45% on the eight longest, nothing on reports under 3,000 chars) with no used item lost on the fourteen after the mechanical check. The saving is real but small: under 1% of the coordinating session's input tokens, a quarter of it from one report.

## Caveats
- The re-expressions are mine, written knowing what was used, and still dropped 3 used items on the first pass; a builder will slip the same way. Only BUILT and second tables are capped; objections, FOR THE SESSION, CANDIDATES and NEW files are not - that is what carries the risk, and it is why the cut is 31% and not more.
- Nine caveats and three candidate lists were not traced either way and are kept. A use outside the window (a later turn quoting a report from memory) is not seen.
- R3's brief asked for both tables verbatim; under v2 the format wins and the second table is a path. A brief that needs a second table whole must say so.
- The user-level rule "say how to test" is the session's to the GM; no builder's verify line reached him or was run (0/5), so the field is dropped.
- 16 reports arrived after the last compaction and the session is still running: their turn counts are lower bounds. 16 more builders of the two days ("Parallel: build ...", "Fix ...") fall outside the named pattern and are not counted. Dates are UTC.
- The other 24 reports' cut is an estimate from four; the part shares come from keyword rules, not hand labels; tokens are chars/4.
