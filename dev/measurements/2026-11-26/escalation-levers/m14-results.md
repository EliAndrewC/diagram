# m14 - escalation-check: Sonnet tier (A) and narrower bundle (B), measured 2026-11-26

30 runs: 4 drafts x 3 Sonnet + 4 x 3 Opus control (A), 2 drafts x 3 bundle on Opus (B). All as SUBAGENT runs (model-trial `--as-subagent`,
first-turn context 11.4-12.1k as in production, prompt identical to prompt.txt in all 30, model ids confirmed in each transcript).
Answer key written before any run: known.md. Per-run figures: usage.txt. Replies: <case>/reply-<i>.md; recorded verdict: <case>/recorded-reply.md.

## Drafts
| id | recorded run | kind | items | recorded rulings | tree |
|---|---|---|---|---|---|
| D1 | agent-a4c5480a77aec3eb2 | decisions/status list | 7 | 1K 2R 3K 4K 5K 6R 7C | 248d6f919 |
| D2 | agent-af0ea87d72ae66c20 | status list | 3 | 1M 2R 3K | 6fbaa4b6f |
| D3 | agent-a6ceed9d04b620f01 | two offers + two canon questions | 4 | 1R 2K 3K 4R | c3fd6eedf |
| D4 | agent-a7462b7192ebbaf67 | process: what needs him | 6 | 1K 2K 3M 4R 5K 6R | a2b841355 |
Not replayable, dropped: agent-abb5deac (the 5-item canon draft, 4 CUT): it read the deleted clone diagram-backlog-t250's unlanded pages; every commit on main
already holds the GM's later answer in 0138. agent-ad836bfe (3 CUT) read an uncommitted diff and /tmp/pb-checks. agent-a0542e85 (draft14) ran `make claims-report`.
So only ONE recorded CUT item (D1 item 7) is in the sample.

## Trial A - per draft, per tier (3 runs each; "same" = same KEEP/REWRITE/MERGE/CUT as the recorded verdict; reach->CUT = recorded KEEP/REWRITE/MERGE, run CUT)
| draft | tier | same ruling (per run) | reach->CUT | CUT->KEEP | tokens in (mean, summed over turns) | out | seconds |
|---|---|---|---|---|---|---|---|
| D1 | Opus | 5,5,6 of 7 | 0 | 0 | 227k | 6.5k | 96 |
| D1 | Sonnet | 3,3,5 of 7 | 0 | 0 | 563k | 11.0k | 277 |
| D2 | Opus | 1,1,1 of 3 | 0 | - | 78k | 2.8k | 43 |
| D2 | Sonnet | 1,0,0 of 3 | 0 | - | 201k | 4.3k | 106 |
| D3 | Opus | 0,1,2 of 4 | 2 (run 1: items 3 and 4) | - | 155k | 6.7k | 97 |
| D3 | Sonnet | 1,2,2 of 4 | 3 (item 3, every run) | - | 550k | 10.0k | 326 |
| D4 | Opus | 3,5,2 of 6 | 3 (run 1: item 4; run 3: items 4, 5) | - | 87k | 4.9k | 65 |
| D4 | Sonnet | 4,1,2 of 6 | 0 | - | 178k | 5.2k | 90 |
| all | Opus | 32 of 60 (53%) | 5 | 0 of 3 | 137k | 5.2k | 75 |
| all | Sonnet | 24 of 60 (40%) | 3 | 0 of 3 | 373k | 7.6k | 200 |
Reaches-the-GM / withheld agreement with the recorded verdict: Opus 55 of 60, Sonnet 57 of 60.
Recorded catches reproduced (runs of 3; keyword-checked, then read): 
| catch | Opus | Sonnet |
|---|---|---|
| D1 missing "the porting process itself" | 1 | 3 |
| D1 plan reviews per task | 1 | 2 |
| D2 "Item 14: not measured" contradicts the agenda's Measured paragraph | 1 | 2 |
| D2 SPEC-review decision missing | 2 | 3 |
| D2 item 13 unaccounted | 1 (and run 1 says it is closed) | 2 |
| D3 T274 owed / no OOM kill / entry's gloss / 2 px / three answers | 3 / 2 / 1 / 3 / 2 | 3 / 3 / 3 / 0 / 3 |
| D4 10 and 12 not ready / builder-count clause / T417 fork / levers not item 9's | 3 / 0 / 3 / 3 | 3 / 3 / 3 / 2 |
Novel Sonnet claims sampled and checked against the tree, all TRUE: "0.0 in 25 small features" is false (408-shrine-small-lines 19 escapes / 2 landings,
ALL-TABLES.txt:391); `debug = 0` already set (rust/Cargo.toml:101); land-tooling's allowed paths exclude rust/ (scripts/land-tooling.sh:39). Not every novel claim was checked.

## Trial B - narrower bundle (Opus, pinned tier), against the same drafts' full-repository Opus runs
What the recorded runs opened: D1 10 files (+22k tokens of context, 7 turns, 177k in), D2 4 files (+15k, 5 turns, 97k), D3 9 files incl. git log (+21k, 6 turns, 147k),
D4 7 files (+13k, 4 turns, 80k). All 28 recorded runs since 11-24: base context 10.6-12.7k, reads add a median of about 6k; the cost is turns x context, not the reads themselves.
Bundle: bundle.py <prompt.txt> <tree> <out> - a written rule over what the PROMPT names only (paths, task ids, item numbers, figures, quoted phrases); D2 17 kB, D3 21 kB.
| draft | form | same ruling (per run) | reach->CUT | tokens in | out | seconds | turns |
|---|---|---|---|---|---|---|---|
| D2 | full repo | 1,1,1 of 3 | 0 | 78k | 2.8k | 43 | 4-6 |
| D2 | bundle | 2,2,1 of 3 | 0 | 45k | 2.7k | 35 | 3 |
| D3 | full repo | 0,1,2 of 4 | 2 | 155k | 6.7k | 97 | 5-9 |
| D3 | bundle | 2,2,2 of 4 | 1 (run 2: item 4) | 49k | 3.9k | 49 | 3 |
All six bundle runs stayed inside the bundle (two Bash calls each, both under bundle/).
Catches the full-repository runs made that no bundle run made: D3 "no out-of-memory kill" (full 2 of 3, bundle 0); D3 "raised with the GM is the entry's gloss, not his
words" (full 1 of 3 + the recorded run, bundle 0 - the builder kept the ruling's HEADING without its body; run 2 said so); D2 the Measured-paragraph contradiction (full 1 of 3
+ recorded, bundle 0, though the item 14 block WAS in the bundle). The bundle runs also could not verify the three-or-four rule (its entry is in docs/process-decisions.md,
which D2's prompt never names) or the pre-approval's words.

## Verdicts
SONNET: does not move. (1) Strict rule failed: D3 item 3 (the aqueduct banks, recorded KEEP, and a question the GM did answer on 2026-11-26) was CUT in 3 of 3 Sonnet runs
("It fails tests 1 and 4: no norm is violated, and it asks whether a ruling applies to this case."; "It fails tests 1, 2 and 3."; "It fails test 1 (no norm is violated)."); 
D3's "2 px" size catch 0 of 3. (2) No saving to buy: Sonnet read 2.7x the input tokens, wrote 1.5x the output and took 2.7x the seconds.
Baseline that qualifies this: the pinned Opus tier fails the same strict rule against its own recorded verdicts - 53% same ruling, and 5 reach->CUT in 12 runs.
NARROWER BUNDLE: not shown unchanged - not adopted on this evidence. Item rulings were no further from the recorded verdict than the full-repository control (11 of 21 against 6 of 21),
and input fell 42% (D2) and 69% (D3), seconds 19% and 49%; but three recorded catches were lost in every bundle run, two of them through the builder's own gaps.
Not run: bundles for D1 and D4 (budget, 30 runs); a draft with several recorded CUTs.

## Tool gaps (model-trial)
No bundle or modified-prompt form: prompt.txt of an Opus-prepared case was replaced by hand (B/*/prompt.txt), tree symlinked. `run` starts every run at once: the two pilots
started together raced on ~/.claude.json ("corrupted" warning written into run-1.json; the file was valid afterwards), so the remaining 28 were started by drive.sh with the tool's
own command line 12 s apart, 3 live. `usage` counts the dispatcher; figures here are from the subagent transcripts (sub.py).
Caveats: 3 runs a leg, 20 items, one recorded CUT; the trial's paths ("m14", "trial" in the MANIFEST) and the tree's edited agent file were visible to the runs (Sonnet remarked on the
edited agent file in 3 runs, one bundle run on the trial); catches were keyword-matched then read, rulings read by hand from each reply.

## Paths
A: /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/m14/A/d{1,2,3,4}-{opus,sonnet}/
B: /tmp/claude-1000/-diagram/c6fd72d1-ab6c-4736-b723-0697a1f5ca51/scratchpad/m14/B/d{2,3}-bundle/ (bundle/ holds MANIFEST.md, draft.md, passages/)
Scripts: m14/bundle.py, drive.sh, sub.py, tx.py, digest.py; key: m14/known.md; per-run usage: m14/usage.txt
Tier pin, if a later trial passes: rust/gate/crates/checks/src/checks/documents/agent_models.rs:46; .claude/agents/escalation-check.md line 5 and its Tier paragraph; the row in docs/spec-kit-and-reviews.md "Models tried".
