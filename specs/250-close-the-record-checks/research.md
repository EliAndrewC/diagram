# Research - feature 250

## R1 - where the tokens went on the measured slice (2026-09-21, T10, plan D3)

The GM asked, before this feature's pipeline runs at scale, whether splitting the record into per-entry
files made the research checks cheap enough: *"how many tokens are eaten up by the main session, how many
by each named subagent, how many by the ad hoc subagents"*. The slice was T01 to T09: `cities/sizing`
footnoted end to end (FR-001) and one entry's vocabulary (FR-003). Every figure below is from
`python3 specs/250-close-the-record-checks/measure/tokens.py report`; the rows are kept in
`measure/tokens-slice.json`. "Input" is fresh plus cached input summed over an agent's turns, which is
what is billed; "peak" is the largest context any one turn held.

### The three totals

| who | input | output | share of input |
|---|---|---|---|
| the main session (92 turns) | 18.6 million | 91,000 | 87% (observed 2026-09-21; method: `measure/tokens.py report`, the last table, main over main plus named) |
| named agents (13 runs, all Opus) | 2.8 million | 118,000 | 13% |
| ad-hoc agents | 0 | 0 | none was dispatched |

### Finding 1 - the split works: a check reads 2,000 to 11,000 tokens of the record

No check opened an assembled page or `SOURCES.html`. Per run, everything a check read:

| agent | runs | input per run | peak | what it read, in tokens |
|---|---|---|---|---|
| `source-reader` (5 items) | 1 | 154,000 | 52,000 | 5,400 |
| `quote-check` (one entry) | 2 | 102,000 - 107,000 | 49,000 - 51,000 | 4,600 - 4,900 |
| `record-format` (one entry) | 3 | 102,000 - 187,000 | 48,000 - 67,000 | 2,400 - 10,600 |
| `source-applicability` (one key) | 2 | 50,000 - 98,000 | 44,000 - 51,000 | 2,300 - 6,200 |
| `spec-fidelity` (plan review, 4 rounds) | 4 | 213,000 - 1,073,000 | 36,000 - 84,000 | 2,500 - 11,700 |

Feature 242 measured the same three checks at 230,000 to 720,000 tokens each, reading two to four whole
pages and the registry (its HANDOFF section 7). Per run that is a cut of roughly two thirds to four
fifths. It is NOT a like-for-like saving on the feature, because a run now covers one entry where it
covered several pages: nine check runs covered two entries and two keys here.

### Finding 2 - a check's cost is no longer the record; it is three CLAUDE.md files

Every check agent's first turn held 6,000 to 8,500 tokens (the harness, its contract, the dispatch). Its
second held about 45,000. The difference is not the record: the moment an agent READS a file under
`research/`, the harness attaches the three `CLAUDE.md` files above that file - the clone's root one,
`.claude/skills/diagram/CLAUDE.md` and `research/CLAUDE.md` - 113,700 characters, about 28,400 tokens,
as `nested_memory`. `omitClaudeMd: true` (feature 256) drops the copy given at LAUNCH and does not touch
these. Measured on all nine check runs: three files attached, every time. That is 55% to 65% of a check's
peak context (observed 2026-09-21; method: 28,400 over each run's `peak_context` in
`measure/tokens-slice.json`), and five to twelve times what it read of the record.

**The experiment (X1).** `record-format` over `ways` 010 twice, same fragment, same prepass, same tier:

| where the agent read the entry | nested files | peak | input | candidates ruled on |
|---|---|---|---|---|
| in the tree (`research/ways/...`) | 3 | 47,700 | 102,300 | 33 of 33 |
| copies in the scratchpad | 0 | 14,500 | 62,600 | 25 of 25 |

Peak context fell 70% and billed input 39% (both observed 2026-09-21; method: the two rows above, one
run each) (the second run took five turns where the first took three). One
run a leg, so the size of the saving is an estimate and its direction is not: the attachment count went
from three to none. The two lists differ because eight terms were defined between the runs. Whether the
check's FINDINGS hold without those files is not shown by one run and is owed three a leg before it is
adopted (the tier rule); the contract is meant to carry what the check needs (feature 256).

### Finding 3 - the main session is 87% of the input, and it is turns times context

92 turns at a mean context of 202,000 tokens. The context was 98,000 before any work began (the system
prompt, the root `CLAUDE.md`, the memory index at 5,700 tokens, tool schemas, and orientation reads) and
324,000 at the end. What grew it, largest first:

- the same nested `CLAUDE.md` attachment, in the main session: opening one file under `research/` brought
  in the engine dev-loop file (7,500 tokens, nothing in it bears on research work), and opening a test
  brought in `tests/CLAUDE.md` (5,000 tokens);
- **a file the session had Read, then changed with a script, is echoed back whole** by the harness on the
  next turn ("changed on disk"): four times here, 4,000 to 10,000 tokens each. `Edit` does not do this;
- thirteen agent reports returned into the context, 2,000 to 5,000 tokens each, every one re-read on
  every later turn;
- four plan-review rounds. Each was a real finding, and each added main-session turns at 200,000 to
  300,000 tokens a turn - the rounds cost more in the main session than in the reviewer.

All 228,000 characters of tool results in the whole session are about 57,000 tokens - under a fifth of
the final context. The cost is not any one large read; it is that every token, once in, is paid for on
every later turn, and a research feature takes many turns.

### What the slice did NOT measure

- `entry-drift`: owed only at the close (FR-007); not run.
- any ad-hoc agent: none was needed; the saved pages and one grep did what an ad-hoc reader would have.
- `source-applicability` on a NEW key with a page to fetch: both runs were changed write-ups with the
  page already saved.
- `source-reader` with fetching: its pages were saved by `make source-pages` first, so it fetched nothing
  and searched once.
- `escalation-check`, `settlement-review`: not owed by this feature.

### What it implies for phases 2 to 4 - for the GM to rule on before they start

FR-002 is 72 items over 15 pages (`measure/assertions.py`), against the five items of this slice. At this
slice's rates that is on the order of 15 reader passes and 60 to 90 check runs: about 8 to 12 million
agent tokens as things stand, and several times that in the main session if it is one long session.

1. **Stop the nested attachment for check agents** (finding 2): hand a check copies outside the tree -
   the prepass scripts already name the fragments and could write the copies - or move what
   `research/CLAUDE.md` says out of a file the harness auto-attaches. Worth about 28,000 tokens a turn on
   every check run. Needs three seeded runs a leg first.
2. **One session per page, not one for the feature** (finding 3): a session that starts at 98,000 and
   does one page ends near 150,000; this one ended at 324,000. The work list, not the context, carries
   the state between them.
3. **Agent reports to a file, a verdict line to the session**: a report is applied once and then re-read
   for the rest of the session.
4. **Never script-edit a file the session has Read** - `Edit` it, or patch it before reading it.
5. **Batch the plan review's evidence**: three of the four rounds were one decision (D4) whose claim had
   not been run. A plan that specifies a script is cheaper reviewed after the script exists.

### Defects found and fixed in the slice (constitution XIV)

- `make record` wrote the research page and not its citations page, so its own `CHECK=1` named a STALE
  file the command could not clear. `tools/record_asset.py` now calls `store.write_pages`; regression
  test added. This is engine Python, so the feature's route is GATED, not DIRECT as spec D2 expected.
- `make record-prepass SECTION=010` on `cities/sizing` matched no section and said nothing (a slug
  re-derived from "city's" is `city-s`; the record's id is `citys`), so `record-format` was handed an
  empty list. The same slug kept that question's notes out of the candidate scan. The wanted headings
  are now read from the fragment, and an unmatched `SECTION` exits 2. Test added.
- `test_the_candidate_list_over_the_real_entry` asserted that `girder` is RAISED on the live record, so
  it failed the day the glossary defined it. It asserts the raising against an empty glossary now.
- NOT fixed, reported: `make quote-verbatim ... SECTION=` checks the whole page whatever `SECTION` says
  (both sizing runs printed all 11 footnotes), though `research/CLAUDE.md` documents the option.

### One thing in the record the GM should look at

`cities/sizing` said an oversized wall ring "would not have been built". The Chang passages the fabric
entry already quotes say the opposite: a seat's ring was sized by its RANK in expectation of growth, and
one that did not grow was "inevitably left with large tracts of intramural land". The entry now says
that. The map's rule survives on the same source - the spare ground was farmed or under water, so every
open was claimed by something - and no rule or number moved. The budget's tight ring was already labeled
a deliberate departure in the same entry.

## R2 - did the token work pay? The next page against the slice (2026-09-26, T15, T16, plan D6 to D9)

The GM adopted R1's three recommendations on 2026-09-26 and asked for the next subset of the research to be
measured against the slice. What was built: record checks read a BUNDLE copied out of the repository
(`make check-bundle`, refused otherwise by `check-bundle-hooks.sh`); a check's report was to go to a file with
a one-line reply; and a page is worked in a FRESH headless session started from a brief (`make page-session`).
The next subset was `homesteads`: five FR-002 items (the slice had five) and three FR-006 items. Every figure is
from `measure/tokens.py` over the transcripts, kept in `measure/tokens-homesteads.json`,
`measure/tokens-slice.json` and `measure/seeded-results.json`; "input" is fresh plus cached input summed over
turns.

### The comparison

| | the slice (R1), its research windows T03-T07 | `homesteads`, one page session |
|---|---|---|
| items | 5 | 8 (5 FR-002, 3 FR-006) |
| main session | 7.13 million over 35 turns, mean 204,000 a turn | 11.28 million over 70 turns, mean 161,000 a turn |
| agents | 7 runs, 0.86 million | 10 runs, 1.22 million |
| total | 7.98 million, **1.60 million an item** | 12.51 million, **1.56 million an item** |
| a check's mean input / peak / turns | 117,000 / 52,000 / 3.2 | 126,000 / 34,000 / 5.9 |
| what a check read of the record | 5,400 tokens | 9,100 tokens |
| nested CLAUDE.md attached to a check | 18 over 6 runs | **0 over 10 runs** |

The slice's whole session was 21.4 million; 13.4 million of it was orientation, four plan-review rounds, a
tooling defect and the vocabulary entry, none of which a page session repeats. The page session cost $10.21
(the harness's own figure) and ran 48.5 minutes (observed 2026-09-26; method: `total_cost_usd` and `duration_ms` in the session's `result.json`).

**Read honestly: per item the page cost the same.** The session started at 40,000 tokens where the slice's
research began at 138,000, and its mean turn was a fifth smaller - but it took twice the turns, and its main
session was still 90% of its tokens (observed 2026-09-26; method: main over total in the table). The work was
bigger than the slice's: three new registry keys where the slice had none, two check rounds where the slice
had one (the first found older defects in two large entries), and entries whose checks read 70% more.

### The bundle, measured on the same bytes (T15)

Five agents, three runs a leg, each case read in the tree and from its bundle:

| agent | tree: input / peak | bundle: input / peak | planted findings named |
|---|---|---|---|
| `record-format` | 196,000 / 77,000 | 166,000 / 33,000 | 3 of 3 runs, both legs |
| `quote-check` | 254,000 / 82,000 | 110,000 / 34,000 | 3 of 3, both legs |
| `source-applicability` | 162,000 / 71,000 | 152,000 / 45,000 | 3 of 3, both legs |
| `entry-drift` | 227,000 / 79,000 | 104,000 / 31,000 | 3 of 3, both legs |
| `source-reader` | 132,000 / 55,000 | 102,000 / 28,000 | 3 of 3, both legs |

No finding was lost; peak context fell 37% to 62%, billed input 6% to 57% (observed 2026-09-26; method: the two columns above, per agent). The input fell least where the
bundle leg took MORE turns (`record-format` six against three): an agent reads the MANIFEST, then each file in
a turn of its own. These runs were headless sessions, where two CLAUDE.md files attach rather than a
subagent's three, so the tree legs understate what a subagent in the tree pays.

### What failed, and was replaced (D8)

As subagents, every check in the page session tried to write its `REPORT.md` and the harness refused it:
*"Subagents should return findings as text, not write report files."* That is a deliberate harness rule and is
not worked around. Each attempt cost the agent a turn. The contracts now reply with the report itself - counts
on the first line, then only what the session must act on, a pass in one line - and `Write` is off their tool
lists. Running each check as a headless process whose output a launcher files was priced and not taken (observed 2026-09-26; method: `measure/d8-pricing.txt` - the first turn of the 15 seeded bundle runs against the 10 subagent checks of the page session, and each report's length times the main-session turns after it): a
headless check's first turn holds 22,300 tokens against a subagent's 7,200, about 87,000 more over a check's
5.8 turns, while an inline report averaged 1,600 tokens re-read on 30 later turns - about 51,000.

### Where the page session's tokens went

Its context grew from 40,000 to 264,000 over 70 turns. The largest parts, measured on the transcript:

- its own edits and reasoning, 72,000 output tokens, which stay in the context like everything else;
- 106 tool results, 174,000 characters (about 43,000 tokens), the largest a 20,000-character grep of notes;
- the nested CLAUDE.md files in its OWN main session - the engine dev loop (about 7,500 tokens, nothing in it
  bears on research) and `research/CLAUDE.md` (about 10,900) - attached on its first read under `research/`;
- ten agent reports inline, 16,300 tokens (the lengths in `measure/d8-pricing.txt`).

The 17 turns of applying findings, at 190,000 to 247,000 a turn, cost 3.8 million by themselves - a third of
the main session.

### Recommendations for the next round

1. **One file per bundle.** Write the bundle as a single `BUNDLE.md` holding every copy inline under its origin
   heading, so a check reads it in one turn. The bundle legs took up to twice the turns of the tree legs for
   this reason alone, and every turn re-reads the whole context. Cheap; worth a seeded re-run of three a leg.
2. **Split a page into two sessions: write, then check-and-apply.** The applying turns were a third of the main
   session because they ran at the END of a session that had already read every source. A second fresh
   session that starts from the committed fragments and the checks' replies would run those turns at about
   60,000 rather than 220,000.
3. **Move the engine's dev-loop CLAUDE.md where research never reaches it.** `.claude/skills/diagram/CLAUDE.md`
   attaches to every session that reads a research file, because `research/` sits under it. Its content
   belongs to `l7r/diagram/` (the engine) and `pool/`; a short skill-level index would stay. About 7,500 tokens on
   every turn of every research session, roughly 5% of this page's main session (observed 2026-09-26; method:
   7,500 over the mean turn of 161,000).
4. **Grep, do not dump.** The session's largest reads were whole notes files and multi-line `sed` ranges of
   large fragments (17,000 to 20,000 characters each) where it needed a few notes by key. A `make notes
   PAGE= SECTION= KEYS=` that prints the named notes alone would cut those.
5. **Re-check only what moved.** The second quote-check round re-read two whole entries to confirm a handful of
   corrected notes; `quote-verbatim NOTES=` and a note-scoped bundle would check the corrected notes alone.

What the remaining work costs at this rate: FR-002 has 64 items left over 14 pages. At 1.56 million tokens and
about $1.30 an item, that is on the order of 100 million tokens and $80 to $90 before recommendations 1 to 5,
and before the cosmetic sweeps (FR-003 to FR-005) and the close.

## R3 - the second round against the first two (2026-09-26, T31 to T33, plan D11)

The GM adopted R2's five recommendations the same day: one-file bundles, two sessions per page, the engine's dev
loop moved out from over the record, `make notes`, and note-scoped re-checks. The next page was `vegetation` -
five FR-002 items and one FR-006 - in two fresh sessions. Figures from `measure/tokens.py`
(`measure/tokens-vegetation-*.json`, `measure/seeded-results.json`); "input" is fresh plus cached input summed
over turns.

### The one-file bundle, on the same planted inputs (T31)

| agent | tree | multi-file bundle | one-file bundle | planted findings named |
|---|---|---|---|---|
| `record-format` | 196,000 in 3.3 turns | 166,000 in 6.0 | 112,000 in 4.0 | 3 of 3 in every leg |
| `quote-check` | 254,000 in 4.0 | 110,000 in 4.0 | 53,000 in 2.0 | 3 of 3 |
| `source-applicability` | 162,000 in 3.0 | 152,000 in 5.0 | 107,000 in 4.0 | 3 of 3 |
| `entry-drift` | 227,000 in 3.7 | 104,000 in 4.0 | 57,000 in 2.0 | 3 of 3 |
| `source-reader` | 132,000 in 3.0 | 102,000 in 4.0 | 74,000 in 3.0 | 3 of 3 |

No finding lost in 45 runs; the one-file bundle halved the input of the checks that read most.

### The three measured rounds

| | the slice (R1) | `homesteads` (R2) | `vegetation` (R3) |
|---|---|---|---|
| items | 5 | 8 | 6 |
| sessions | the long one | one fresh | two fresh |
| main session | 7.13 million, 35 turns | 11.28 million, 70 turns | 14.04 million, 110 turns (40 + 70) |
| mean main turn | 204,000 | 161,000 | **128,000** |
| agents | 7 runs, 0.86 million | 10 runs, 1.22 million | 23 runs, 1.45 million |
| mean input per agent run | 122,000 | 122,000 | **63,000** |
| total | 7.98 million | 12.51 million | 15.48 million |
| per item | 1.60 million | 1.56 million | **2.58 million** |
| harness cost | - | $10.21 | $11.77 ($2.82 + $8.95) |

(Observed 2026-09-26; method: the rows of `measure/tokens-*.json`, main and agents summed per page; the mean turn
is the main session's input over its turns.)

**Read honestly: every unit got cheaper and the page got dearer.** A main-session turn cost 37% less than in
the slice and an agent run 48% less (observed 2026-09-26; method: the mean-turn and per-run rows of the table above) - the two things the changes aimed at. But the page took 18 main turns an
item where homesteads took 9 and the slice 7, and turns times context is the whole bill. Three reasons, each
measured on the transcripts:

- **More work.** The check session ran 23 agents, not 10: eleven first-round checks, five note-scoped
  re-checks, and five `entry-drift` checks with five modal rewrites in `greenery.py`. The last is FR-007 work
  owed at the push, which homesteads left to T23 and this session did early. It applied about 35 findings and
  wrote 14 glossary terms.
- **One step a turn.** Of the check session's 67 tool turns, 63 carried a single call: 20 reads, 12 patches, 11
  record-and-test runs, one at a time, each re-reading a context that averaged 150,000.
- **A fixed floor.** Every turn of every session began from about 40,000 tokens of harness, tool schemas, MCP
  instructions, skill listing and CLAUDE.md before any work - 110 turns at 40,000 is 4.4 million, 28% of the
  page's main session (observed 2026-09-26; method: each session's first-turn context times its turns, over its main input).

The write session is the change's clearest result: locating, reading and writing six items took 40 turns at a
mean of 89,000, where homesteads' same steps ran at 64,000 to 145,000 a turn in the middle of one long session.

### Recommendations for the next round

1. **Lower the session floor.** Start a page session with only the tools a research page uses (Bash, Read,
   Edit, Write, Grep, Agent, WebFetch, WebSearch) and no MCP servers or skill listing; a headless check whose tool
   list is pinned starts at 22,000 where a page session starts at 40,000. At 110 turns that is about 2 million a
   page. A one-line change to the launcher, measured on its first page.
2. **Check and apply one question per session.** The check session's context grew to 218,000 as 23 reports
   arrived. Two or three questions a session - bundles, checks, apply, re-check, entry-drift for that question -
   would each start at the floor and end near 100,000.
3. **A report's findings in one turn.** Apply every finding of one report as one patch or one message of parallel
   `Edit` calls, then run the record commands and tests once. The brief says so, and the step reads so.
4. **Trim `research/CLAUDE.md`** to its operative rules. It attaches to every research session at about 10,900
   tokens, 8% of this page's mean turn (observed 2026-09-26; method: 10,900 over the check session's mean turn of 150,000); its rationale and history belong in `docs/research-doctrine.md`.
5. **Hold the pages to the brief's scope.** Either `entry-drift` belongs in the per-page check session (it is owed
   at the push, so this page did the honest thing) and the brief should say so and budget it, or it waits for
   T23; the comparison between pages needs one or the other.

What the rest costs at this round's rate: 62 FR-002 items remain over 13 pages - on the order of 160 million
tokens and $120 at vegetation's 2.58 million an item, or 97 million at homesteads' 1.56 million.

## R4 - the third round against the first three (2026-09-26, T34 to T41, plan D12)

The GM adopted R3's five recommendations the same day: a lower session floor, check sessions of two questions
each, a report's findings applied in one turn, `research/CLAUDE.md` cut to its rules, and `entry-drift` in the
check sessions. The next page was `cities/defenses` - five FR-002 items and one FR-006, the size of the last -
in three fresh sessions: one to write, then two check groups (questions 010 and 020; 040 and 060). Figures from
`measure/tokens.py` (`measure/tokens-defenses-*.json`); "input" is fresh plus cached input summed over turns.

| | the slice (R1) | `homesteads` (R2) | `vegetation` (R3) | `cities/defenses` (R4) |
|---|---|---|---|---|
| items | 5 | 8 | 6 | 6 |
| sessions | the long one | one | two | three (write, two check groups) |
| first turn of a session | 138,000 | 40,000 | 40,000 | **21,400** |
| main session | 7.13 million, 35 turns | 11.28 million, 70 turns | 14.04 million, 110 turns | **5.74 million, 95 turns** |
| mean main turn | 204,000 | 161,000 | 128,000 | **60,000** |
| agents | 7 runs, 0.86 million | 10 runs, 1.22 million | 23 runs, 1.45 million | 16 runs, 0.81 million |
| total | 7.98 million | 12.51 million | 15.48 million | **6.56 million** |
| per item | 1.60 million | 1.56 million | 2.58 million | **1.09 million** |
| harness cost | - | $10.21 | $11.77 | **$7.39** ($1.75 + $2.27 + $3.37) |

(Observed 2026-09-26; method: the rows of `measure/tokens-*.json`, main and agents summed per page; the mean turn
is the main session's input over its turns; the cost is each session's `total_cost_usd`.)

**This round worked.** Per item the page cost 58% less than vegetation and 30% less than homesteads or the slice
(observed 2026-09-26; method: the per-item row). The mean turn fell by more than half against vegetation: every
session started at 21,400 rather than 40,000, and no session grew past 104,000, where vegetation's check session
reached 218,000. The turns per item were 16, between homesteads' 9 and vegetation's 18 - so the saving is the size
of each turn, which is what the floor and the groups were for.

Two things the comparison has to carry. `cities/defenses` owed no modal check - `_entry_owed.py` named no class
for its questions - where vegetation ran five and rewrote five modals; and the second check group re-checked one
question twice more (`quote-check` three times on 060), a loop the brief does not bound.

### Recommendations for the next round

1. **Go.** At 1.09 million tokens and about $1.25 an item, the 57 FR-002 items left over 12 pages come to on the
   order of 62 million tokens and $70, worked a page at a time as this one was.
2. **Bound the re-check.** One note-scoped re-check per question; a PARTIAL left after it is labeled honestly in
   the note rather than re-checked again. The second group's 060 loop was a third of its session.
3. **Shorten the agent descriptions.** Every session's first turn carries the agent listing - about 22,000
   characters, most of it the long `description` fields of the defined agents. One sentence each, with the detail
   left in the contract body the agent itself reads, lowers the floor of every session in the project, not only
   the research ones.
4. **Give every clone session the floor fix.** The duplicated root `CLAUDE.md` loads in every session that works
   in a clone, the GM's own included - about 5,000 tokens a turn. A `claudeMdExcludes` for the mirror's copy in each
   clone's untracked `.claude/settings.local.json`, written when the clone is made or synced, removes it everywhere.

### Two tooling defects this round found, fixed where found

- **A wait whose producer died printed a success.** The no-poll guard adds a liveness check to a backgrounded
  file-watching loop (feature 227); when the check found no writer it ended the LOOP, and the command after it ran
  as though the wait had succeeded. On this page a wait on `tasks.md` - edited now and then, never held open - was
  declared dead after two minutes and printed `ticked` while the write session was still reading sources. The
  clause now ends the whole command with status 3 (`scripts/_hm_shape.py`), and `test-no-poll-hooks.sh` proves both
  loop forms stop there, nothing after them running.
- **A page's sessions left nothing to wait on.** The runner now keeps one run log open for its whole queue - a line
  as each session starts and ends, then `ALL DONE` - and the launcher prints the backgrounded wait to use, so the
  wait ends when the runner does, finished or killed, and the guard's liveness check finds the runner holding the
  file. The last session of this page ended at 18:14; the hand-built wait that replaced the dead one reported at
  18:15:43, after its own 90-second check that no further session was starting.

## R5 - the fourth round, and the five rounds side by side (2026-09-26, T42 to T46, plan D13)

The GM asked for R4's recommendations 2 to 4 - one re-check round, one-sentence agent descriptions, every clone
without the mirror's CLAUDE.md - and one more equivalent page before the rest. The page was `religion-and-death`,
four FR-002 items and one FR-006, worked exactly as `cities/defenses` was: a write session, then two check sessions
of two questions (010 and 020; 190 and 200). Figures from `measure/tokens.py` (`measure/tokens-religion-*.json`).

| | slice (R1) | `homesteads` (R2) | `vegetation` (R3) | `cities/defenses` (R4) | `religion-and-death` (R5) |
|---|---|---|---|---|---|
| items | 5 | 8 | 6 | 6 | 5 |
| sessions | one long | one | two | three | three |
| first turn of a session | 138,000 | 40,000 | 40,000 | 21,400 | **19,300** |
| largest context any turn | 324,000 | 264,000 | 218,000 | 104,000 | **92,000** |
| main session | 7.13 M, 35 turns | 11.28 M, 70 turns | 14.04 M, 110 turns | 5.74 M, 95 turns | 6.00 M, 104 turns |
| mean main turn | 204,000 | 161,000 | 128,000 | 60,000 | **58,000** |
| agent runs | 7 (0.86 M) | 10 (1.22 M) | 23 (1.45 M) | 16 (0.81 M) | 17 (1.42 M) |
| mean agent run | 122,000 | 122,000 | 63,000 | 51,000 | 84,000 |
| total | 7.98 M | 12.51 M | 15.48 M | 6.56 M | 7.42 M |
| **per item** | 1.60 M | 1.56 M | 2.58 M | **1.09 M** | **1.48 M** |
| harness cost | - | $10.21 | $11.77 | $7.39 | $9.33 |

(Observed 2026-09-26; method: the rows of `measure/tokens-*.json`, main and agents summed per page; the first turn
and largest context are the main sessions' own; the cost is each session's `total_cost_usd`, summed.)

**What the three changes did, measured where they act.** Every session started at 19,300 rather than 21,400 (the
shorter descriptions; the clone's own settings now drop the duplicate CLAUDE.md for every session, not only page
sessions). No session grew past 92,000. The mean main turn fell again, to 58,000. The re-check stayed at one round
per group, where the last page ran one question's three times.

**Why this page still cost more per item than `cities/defenses`: its content, not the tooling.** Its questions carry
more and longer notes, and the checks read them: a `quote-check` read 8,700 tokens of this page against 5,500 of the
last, and its mean input doubled to 93,000 (observed 2026-09-26; method: the agents' `read_chars` and input in the
two pages' records, by kind). The main session was within 5% of the last page's (6.00 against 5.74 million). So the
spread between 1.09 and 1.48 million an item is what two pages of the record differ by; with the tooling as it now
stands, a page's cost follows the size of what it has to read and check.

**For the remaining pages.** 53 FR-002 items remain over 11 pages. At the two structured pages' range, 1.09 to 1.48
million an item, that is on the order of 58 to 78 million tokens and $65 to $100 - against 83 to 137 million at the
first two rounds' rates for the same work.

## R6 - the fifth round: per-check bundles and a size for a question (2026-09-26, T47 to T51, plan D14)

The GM asked for both changes - a bundle per check and a cap on a question's size - and one more measured page. The
page was `cities/government`, three FR-002 items, worked as the last two: a write session, then two check sessions
of two questions (020 and 070; 080 and 081). Figures from `measure/tokens.py` (`measure/tokens-government-*.json`,
`measure/tokens-split-*.json`).

**Two things disturb the comparison, and both are stated rather than smoothed.** The page has only three items, so
a per-item figure is the noisiest yet - and the check work scales with the QUESTIONS checked, which was four on each
of the last three pages. And the last check session died with the GM's terminal after applying its first-round
reports; its re-check and close (steps 7 and 8) were run by the recovery session, whose two re-check agents are
counted below and whose own main turns are not (they were spent mostly reading the dead session's transcript). The
dead session's missing main turns are estimated at about 0.6 million - ten more turns near its own peak of 69,000 - and the estimate
is labeled wherever it is used.

| | `cities/defenses` (R4) | `religion-and-death` (R5) | `cities/government` (R6) |
|---|---|---|---|
| items / questions checked | 6 / 4 | 5 / 4 | 3 / 4 |
| first turn of a session | 21,400 | 19,300 | **19,300** |
| largest context any turn | 104,000 | 92,000 | 95,000 |
| main session | 5.81 M, 95 turns | 6.07 M, 104 turns | 5.30 M, 94 turns (+ about 0.6 M estimated) |
| mean main turn | 61,000 | 58,000 | **56,000** |
| agent runs | 16 (0.88 M) | 17 (1.51 M) | 18 (1.08 M) |
| mean agent run | 55,000 | 89,000 | **60,000** |
| what a `quote-check` read | 22,000 chars | 34,800 chars | **19,400 chars** |
| what a `record-format` read | 19,200 chars | 31,300 chars | **15,000 chars** |
| total | 6.69 M | 7.59 M | 6.38 M measured, about 7.0 M with the estimate |
| **per question checked** | 1.67 M | 1.90 M | **1.59 M** measured, about 1.74 M with the estimate |
| per item | 1.12 M | 1.52 M | 2.13 M measured |

(Observed 2026-09-26; method: every column recomputed the same way from the stored `measure/tokens-*.json` - main
and agents, fresh + cached + output, summed per page - which runs about 2% above R5's table on the same files; the
first turn is each main session's first assistant turn; a check's read is the mean of its agents' `read_chars`. The
harness cost is not given: the dead session wrote no `total_cost_usd`.)

**The two changes did what they were for, where they act.** A check reads its own bundle and the question is capped,
so what a `quote-check` read fell to 19,400 characters from 34,800 on the last page, and a `record-format` to 15,000
from 31,300 - about half, and below `cities/defenses` too. The mean agent run fell to 60,000 from 89,000. Every
session started at 19,300 and none passed 95,000.

**The main session is now where the tokens go.** It was 83% of this page's measured total, and the agents 17% (observed 2026-09-26; method: the table's main
and agent rows, 5.30 of 6.38 million). The
largest single cost on each of the three pages is the APPLY step of a check session - 1.41 million over 27 turns in
this page's first group, against 1.92 and 1.66 million on the last two - each turn re-reading a context of 60,000 to
90,000. Next is the write session's reading: 19 turns and 0.97 million here for three items, where `cities/defenses`
read six in 0.26 million.

**The splits, a one-time cost.** Four questions over the cap were split by fresh sessions for 3.20 million tokens
and $3.70 in all, about 0.8 million a split (observed 2026-09-26; method: the four `tokens-split-*.json` and their
`result.json` costs). Each kept its heading and id, moved every note unchanged to exactly one part, and reported what
each part relies on from the others; no part lost a finding its decision needs. One loose end came with them: the
map modals written from homesteads 210 and 040 still named the unsplit question, and are re-pointed to the parts
that now hold their text (the `entry-drift` answers stay with T23). 18 untouched questions remain over the cap.

### Recommendations for the next round

1. **Hand the apply step ready-made edits.** Have `quote-check` and `record-format` end each finding with the exact
   old and new text (or "no edit - label it" with the label's wording), so a report is applied in one patch and one
   turn; the step now takes 12 to 27 turns a group, each at 60,000 to 90,000 of context.
2. **Split a question over the cap inside its page's write session**, not in a session of its own: a standalone
   split cost about 0.8 million, most of it reading the question the write session has already read.
3. **Look at the write session's read step before the next page**: 19 turns for three items here, against 5 for six
   on `cities/defenses`. Its transcript has not been read for why; that is the measurement to take first.
4. **Report per question checked**, keeping per item for continuity: it is the unit the check work scales with.

## R7 - the sixth round: a report applied by one command, the split in the write session (2026-09-26, T52 to T56, plan D15)

The GM asked for all four of R6's recommendations and one more measured page. The page was `cities/fabric`: three
FR-002 items, as `cities/government` had. The write session split question 140 (36,858 bytes) into 140, 143 and
146 as D15.2 intended, so the check sessions took FIVE questions in three groups (040 and 050; 140 and 143; 146).
Figures from `measure/tokens.py summary` over `measure/tokens-fabric-*.json`.

| | `cities/defenses` (R4) | `religion-and-death` (R5) | `cities/government` (R6) | `cities/fabric` (R7) |
|---|---|---|---|---|
| items / questions checked / sessions | 6 / 4 / 3 | 5 / 4 / 3 | 3 / 4 / 3 | 3 / 5 / 4 |
| largest context any turn | 104,000 | 92,000 | 95,000 | **137,000** |
| main session | 5.81 M, 95 turns | 6.07 M, 104 turns | 5.30 M, 94 turns | **9.84 M, 153 turns** |
| mean main turn | 61,000 | 58,000 | 56,000 | 64,000 |
| agent runs | 16 (0.88 M) | 17 (1.51 M) | 16 (0.94 M) | 18 (0.97 M) |
| mean agent run | 55,000 | 89,000 | 59,000 | **54,000** |
| what a `quote-check` read | 22,000 chars | 34,800 | 19,400 | **14,300** |
| what a `record-format` read | 19,200 chars | 31,300 | 15,000 | **12,900** |
| total | 6.69 M | 7.59 M | 6.24 M | **10.81 M** |
| **per question checked** | 1.67 M | 1.90 M | 1.56 M | **2.16 M** |

(Observed 2026-09-26; method: `tokens.py summary --files <the page's records> --questions N --items N`, which sums
fresh + cached + output over every window of every session; R6's government row is recomputed by the same command
without its estimated tail, so it reads 1.56 M, not R6's 1.59.)

**The agents kept getting cheaper; the main sessions did not.** What a check reads fell again (a `quote-check` to
14,300 characters) and the mean agent run to 54,000. `make apply-edits` did its job where it ran: every report came
back as blocks, and the sessions applied 21 blocks in 2b and all of 2c's with none refused. But the page cost 10.8
million, the most of the structured rounds, and all of the growth is main-session turns.

**Where it went** (observed 2026-09-26; method: each session's windows in `measure/tokens-fabric-*.json`, and the
tool calls of its transcript, in order):

1. **The write session: 3.62 million, against 2.20 on `cities/government`.** Its locate step alone was 22 turns and
   1.50 million: two of the three items were claims about the GM's canon ("an Imperial road is Imperial property",
   "the highest merchant share of any tier"), and the session ran about fifteen greps through `budgets.md` and
   `l7r.md` one a turn, plus git archaeology on where a sentence came from. It also read question 140 whole (32,500
   characters with its notes) to split it, and carried it: its context peaked at 137,000.
2. **The split added a question and a session.** Five questions checked, not four, and a third check session with
   its own start-up and close.
3. **First use of the new tooling found three of my defects**, each fixed by the session that met it, with a test:
   `apply-edits` named glossary files by a rule the loader rejects (2a), missed blocks an agent indented under a
   numbered list (2b), and wrote a term's variants without the term itself, which failed a record test (2b's
   `kidoban`, found by 2c). 2b also fixed a `quote-verbatim` defect (two passages sharing one translation note were
   matched to the wrong original). The turns that touched these directly cost 0.54 million, 6% of the main total
   (observed 2026-09-26; method: the main-session turns whose tool calls name `_apply_edits`, `_quote_verbatim`, their tests or
   `kidoban`); the turns around them are not counted, so the true figure is higher. All four are fixed now.
4. **The apply and re-check steps stayed long**: steps 6 and 7 were 11 to 21 and 6 to 15 turns a group. Part is
   point 3; the rest is verification between commands (tests run one file a turn, a grep to confirm each hand edit)
   and turns spent waiting on agents (`echo waiting`).

### Recommendations for the next round

1. **Give the write brief the canon's own index.** When an item is a claim about the setting, name `budgets.md` and
   `l7r.md` and have the session grep them for all its terms in ONE command - it made about fifteen sequential
   greps here.
2. **Split before the write, as its own step, and drop the split question from the write session's context.** The
   split was right to be in-session (it saved re-reading), but carrying 32,500 characters for the rest of the
   session cost more than the read it saved; a split step that commits and ends, with the write session then reading
   only the part its item falls in, keeps both savings.
3. **Size the check groups by bytes, not by count**, so a split's small parts share a session (146 alone was a
   whole session at 7,200 bytes).
4. **One more page before the rest, with the tool defects fixed**, since part of this round's growth was the first
   use of the new tooling (0.54 million measured directly, more around it) and part was two canon-heavy items; one
   page is not yet a trend.

## R8 - the seventh round: the canon by guard, the split first, groups by bytes (2026-09-27, T57 to T62, plan D16)

The GM asked for all four of R7's recommendations, mechanically enforced, and one more measured page. The page was
`fields`: three FR-002 items and four FR-006 items. A split session divided its question 020 (56,248 bytes) into
seven parts first; then one write session, and - because the check groups are now packed by bytes and its three
questions came to 28,419 - ONE check session. Figures from `tokens.py summary` over `measure/tokens-fields-*.json`;
the split session is `measure/tokens-split-df423d15.json`.

| | `cities/defenses` (R4) | `religion-and-death` (R5) | `cities/government` (R6) | `cities/fabric` (R7) | `fields` (R8) |
|---|---|---|---|---|---|
| questions checked / sessions | 4 / 3 | 4 / 3 | 4 / 3 | 5 / 4 | 3 / 2 (+1 split) |
| modals owed an `entry-drift` | 0 | 0 | 0 | 0 | **7** |
| largest context any turn | 104,000 | 92,000 | 95,000 | 137,000 | **171,000** |
| main session | 5.81 M | 6.07 M | 5.30 M | 9.84 M | 9.08 M, 101 turns |
| mean main turn | 61,000 | 58,000 | 56,000 | 64,000 | **90,000** |
| agent runs | 16 (0.88 M) | 17 (1.51 M) | 16 (0.94 M) | 18 (0.97 M) | 28 (1.18 M) |
| mean agent run | 55,000 | 89,000 | 59,000 | 54,000 | **42,000** |
| total | 6.69 M | 7.59 M | 6.24 M | 10.81 M | 10.26 M |
| per question checked | 1.67 M | 1.90 M | 1.56 M | 2.16 M | 3.42 M |

(Observed 2026-09-27; method: `tokens.py summary --files <the page's records> --questions N --items N`. Not in the
fields row: the split session, 1.35 million over 24 turns; and a first write session stopped after nine turns when
the plan review found the canon guard was not live, 0.28 million.)

**What each recommendation did** (the plan review's item 4):

1. **The canon, by guard - used, never refused.** The write session named the canon and ran `make canon` as its
   brief says; `canon-read-hooks.sh` fired zero times in the round (method: the guard log, `canon-read` entries after
   the restart, and the refusals in both transcripts - none). None of the three FR-002 items was a canon claim, so
   this page is no test of the saving; the guard is proved live (a headless session in the clone, 00:13:14Z).
2. **The split first - worked as built.** The write session never loaded question 020: its peak, 116,000, came from
   its own sourcing, not from carrying a split question (fabric's write session carried 32,500 characters of 140 to
   a peak of 137,000). The split itself cost 1.35 million in its own session, about what a split cost in R6.
3. **Groups by bytes - a regression, and the main cause of this round's cost.** Counting only question bytes, the
   packer put all three questions in one session - and with them seven map modals owed an `entry-drift` check and
   four source write-ups owed `source-applicability`, which the byte count does not see. That one session ran 17
   first-round agents and 10 re-checks, rewrote all seven modals, and grew to 171,000; its apply step alone was 24
   turns and 2.70 million, its re-check 1.41 million.
4. **The modal rewrites were by hand.** `entry-drift` ends with no EDIT blocks, and `apply-edits` writes only under
   `research/`, so the thirteen edits to the modal class files (`interactive/classes/fields.py`, `water_and_ways.py`)
   were thirteen hand edits - the step R6 measured as the largest cost, back again for a kind of finding the D15
   tooling did not cover.

**Per question checked no longer measures the work.** This page checked three questions but also seven modals and
four sources; per THING checked (question, modal or source) it is 0.73 million, against 0.78 million on
`cities/government` (four questions, four sources) and 1.54 million on `cities/fabric` (five questions, two
sources) (observed 2026-09-27; method: the total over the count of questions, owed modals and registry keys each
page's check sessions took).

### Recommendations for the next round

1. **`entry-drift` ends with EDIT blocks, and `apply-edits` writes a modal's docstring** in
   `l7r/diagram/interactive/classes/`, under the same exactly-once rule, so a drifted modal is applied like any
   other finding.
2. **Size a check group by everything it checks**: question and notes bytes, each owed modal's prose, each registry
   entry - and cap it where the measured sessions stayed under about 100,000 of context. Owed modals and sources count.
3. **Report per thing checked** (questions + modals + sources), with per question beside it for continuity.

## R9 - the eighth round: modals applied by command, groups by load (2026-09-27, T63 to T67, plan D17)

The GM asked for R8's three recommendations and another page of similar size. The page was `archetypes`: two FR-002
items (questions 100 and 140) and one FR-006 item. One write session, then check groups packed by load. Figures from
`tokens.py summary` over `measure/tokens-archetypes-*.json`.

**A defect of mine put a third question into the round.** The check step read the handoff's `SECTION=` entries
wherever they appeared, and the handoff's closing note - "- SECTION=170 is over the size cap, but none of this page's
items falls in it, so it was not split here" - was read as a changed question. So a third check group ran on question
170 (32,800 bytes, over the cap, untouched by this page) with the eight dike-pond modals owed from it. That work was
owed at the push anyway (T23: every `_entry_owed.py` pair answered), so it is not wasted, but it is not this page's
work, and it is reported apart. Fixed: the check step now DERIVES the questions and keys from what the write
session's commits changed (`brief.py changed_since`, against a base the write brief records), not from the handoff's
prose; replayed on both handoffs it names 100, 140 and the two keys for `archetypes`, and exactly `fields`' own list.

| | `cities/government` (R6) | `cities/fabric` (R7) | `fields` (R8) | **`archetypes` (R9)** | the 170 group (R9, not the page's) |
|---|---|---|---|---|---|
| questions / modals / keys checked | 4 / 0 / 4 | 5 / 0 / 2 | 3 / 7 / 4 | 2 / 2 / 2 | 1 / 8 / 0 |
| sessions | 3 | 4 | 2 (+1 split) | 3 | 1 |
| largest context any turn | 95,000 | 137,000 | 171,000 | **102,000** | 124,000 |
| main session | 5.30 M | 9.84 M | 9.08 M | 5.46 M, 98 turns | 6.08 M, 77 turns |
| mean main turn | 56,000 | 64,000 | 90,000 | **56,000** | 79,000 |
| agent runs | 16 (0.94 M) | 18 (0.97 M) | 28 (1.18 M) | 12 (0.93 M) | 19 (0.97 M) |
| total | 6.24 M | 10.81 M | 10.26 M | **6.39 M** | 7.04 M |
| per thing checked | 0.78 M | 1.54 M | 0.73 M | 1.07 M | 0.78 M |
| per question checked | 1.56 M | 2.16 M | 3.42 M | 3.20 M | - |

(Observed 2026-09-27; method: `tokens.py summary --files <records> --questions N --items N --modals N --keys N`; the
page's column is its write session and check groups 2a and 2b, the 170 group is 2c. All four sessions together:
13.43 M over 15 things, 0.90 M each.)

**What each change did:**

1. **Modals applied by command - worked.** The 170 group rewrote eight drifted modals and applied two more fixes after
   its re-check with twelve `make apply-edits` runs and NO hand edit; on `fields` the same kind of work was thirteen
   hand edits. On the page itself, group 2b's twelve hand edits were findings the agents marked `EDIT: none` (a new
   source to add, a registry key to link) and four edits to source write-ups, whose check (`source-applicability`)
   writes no EDIT blocks yet.
2. **Groups by load - worked.** No session passed 124,000 (fields: 171,000), and the page's sessions peaked at 102,000
   with a mean turn of 56,000, back to the best rounds. The 170 group was one question whose load (32,800 plus eight
   modals) was over the budget on its own; a single question cannot be split further by packing, and it peaked at
   124,000 - under the fit's prediction, so the fit is if anything cautious.
3. **Per thing checked** - reported above. The page's 1.07 M a thing sits between government's 0.78 and fabric's 1.54;
   its per-question figure is high because two questions carried three sessions, each re-paying its brief and
   start-up (not separately measured here).

**The write session was the cheapest yet**: 1.68 million over 30 turns, peaking at 82,000 (government 2.20, fabric
3.62, fields 3.39 million).

**Two findings the sessions left for the GM** (recorded in the record, not decided): the map's mulberry density (one
bush per 10 to 20 square feet, a guess) is 10 to 20 times sparser than the one figure found (8,000 to 10,000 bushes
a mu, modern); and the county gazetteer dates the fruit, cane and vegetable dikes to the delta's industrialization,
while the map draws them as options labeled accurate.

### Recommendations for the next round

1. **`source-applicability` ends with EDIT blocks** for the write-up fixes it asks for, as the other three checks do.
2. **Measure a session's start-up, then decide the budget**: group 2a checked one small question alone (1.37 million)
   because 140's group was near the budget. Measure what a session costs before its first check, and whether a
   looser budget is safe (the 170 group stayed at 124,000 over a load of about 58,000), before moving it.
3. **Decide where owed modals from earlier work get checked** - the 170 group showed that a page's owed modals from
   OTHER questions are real work T23 will need; checking them per page, packed by load, cost 0.78 million a thing,
   the cheapest rate measured. Folding them into each page's round on purpose (rather than by the defect that found
   them) would clear T23 as the pages go.

## R10 - the ninth round: source write-ups by command, the budget measured, owed modals folded in (2026-09-27, T68 to T72, plan D18)

The GM asked for R9's three recommendations and another page. The page was `cities/hinterland`: two FR-002 items
(questions 010 and 050), four new or changed registry keys, no modal owed. One write session, then two check groups:
050 alone, and 010 with the four keys. Figures from `tokens.py summary` over `measure/tokens-hinterland-*.json`.
Before it, a split session divided `archetypes` 170 (touched by R9's accidental group, and over the cap) into four
questions: 0.93 million, reported apart.

| | `cities/government` (R6) | `cities/fabric` (R7) | `fields` (R8) | `archetypes` (R9) | **`cities/hinterland` (R10)** |
|---|---|---|---|---|---|
| questions / modals / keys checked | 4 / 0 / 4 | 5 / 0 / 2 | 3 / 7 / 4 | 2 / 2 / 2 | 2 / 0 / 4 |
| largest context any turn | 95,000 | 137,000 | 171,000 | 102,000 | **115,000** |
| main session | 5.30 M | 9.84 M | 9.08 M | 5.46 M | 6.91 M, 116 turns |
| mean main turn | 56,000 | 64,000 | 90,000 | 56,000 | **60,000** |
| agent runs | 16 (0.94 M) | 18 (0.97 M) | 28 (1.18 M) | 12 (0.93 M) | 11 (**1.90 M**) |
| total | 6.24 M | 10.81 M | 10.26 M | 6.39 M | 8.80 M |
| per thing checked | 0.78 M | 1.54 M | 0.73 M | 1.07 M | 1.47 M |

(Observed 2026-09-27; method: `tokens.py summary --files <records> --questions N --items N --modals N --keys N`.)

**Where this page's cost went: one source that is a book.** `cdlib-local-elites` is *Chinese Local Elites and
Patterns of Dominance*, whose saved page is the whole book, 1.38 MB. The `source-applicability` check of it read
200,026 characters over 16 turns and cost 0.73 million - against 35,000 to 105,000 for each of the page's other three
sources, and 36,000 to 60,000 a source on the last two pages; the `source-reader` that read it and two other pages
cost 0.55 million over 83,621 characters (observed 2026-09-27; method: the agents' rows in the page's records, and
the size of `/tmp/l7r-check/key-cdlib-local-elites`). Without that one check the page is 8.07 million, 1.35 million
a thing. The write session was 2.43 million (its sourcing - the book among it - peaked at 115,000); group 2a, with
the four keys, was 3.08 million, and split its own question 010 when the check's fixes pushed it over the cap.

**What each change did:**

1. **Source write-ups by command - worked, partly.** Three of the page's source write-up fixes were applied by
   `make apply-edits`; three more were done by hand, among them a fix to an entry (`siheyuan-zhwiki`) that was not one
   of the four checked keys.
2. **The budget, measured and kept** - no session passed 115,000, and the check sessions peaked at 100,000 and 62,000.
3. **Owed modals folded in** - built and replayed (D18.3), not exercised: this page owed no modal.

**What the rounds now say.** Over R6 to R10 the tooling's own costs have come down - agents read their bundles, a
report is applied by command, no session grows past about 115,000, a session's start-up is about 118,000 - and the
figure per thing now moves mostly with the page's CONTENT: how hard its claims are to source, and how large its
sources are (0.73 to 1.54 million a thing, the highest two on the pages whose sessions met first-use defects or a
book-length source).

### Recommendations for the next round

1. **A check reads the part of a long source it needs, not the whole of it.** A key bundle carries the source's
   front matter (title, author, date - what `source-applicability` judges) and a window around each passage the
   record quotes from it, not the whole saved page; the same cap for `source-reader`'s saved pages. One book-length
   source cost 0.73 million in one check on this page.
2. **Then proceed with the remaining pages** rather than another tooling round: what remains between pages is mostly
   the pages themselves.

## R11 - the tenth round: a long source read in part (2026-09-27, T73 to T76, plan D19)

The GM asked for R10's one fix and one more round, to see whether anything else would turn up. The page was `water`:
two FR-002 items and eight FR-006 items. One write session, then three check groups by load: 010 and 170 with
`suzhou-enwiki` and the Stream modal; 120, 130 and 220 with the Marsh modal; and a modal-only group for DrainageDitch
and Weir - modals owed from `water` questions this round did not otherwise change, the first round to exercise D18's
folding. Figures from `tokens.py summary` over `measure/tokens-water-*.json`.

| | `cities/government` (R6) | `fields` (R8) | `archetypes` (R9) | `cities/hinterland` (R10) | **`water` (R11)** |
|---|---|---|---|---|---|
| questions / modals / keys checked | 4 / 0 / 4 | 3 / 7 / 4 | 2 / 2 / 2 | 2 / 0 / 4 | 5 / 4 / 1 |
| largest context any turn | 95,000 | 171,000 | 102,000 | 115,000 | **111,000** |
| mean main turn | 56,000 | 90,000 | 56,000 | 60,000 | **57,000** |
| agent runs | 16 (0.94 M) | 28 (1.18 M) | 12 (0.93 M) | 11 (1.90 M) | 25 (1.27 M) |
| mean agent run | 59,000 | 42,000 | 78,000 | 172,000 | **51,000** |
| total | 6.24 M | 10.26 M | 6.39 M | 8.80 M | 10.55 M |
| per thing checked | 0.78 M | 0.73 M | 1.07 M | 1.47 M | **1.06 M** |

(Observed 2026-09-27; method: `tokens.py summary --files <records> --questions N --items N --modals N --keys N`.)

**What the fix did.** Four of the page's sources were long Wikipedia articles; each was saved in parts (Suzhou's
84,489 characters in five), and the `source-reader` that read them all read 17,780 characters, against 83,621 on the
last page; the one `source-applicability` run read 16,238 and cost 55,141 tokens, in line with the ordinary rounds.
The folded owed modals were checked in a group of their own and their five fixes applied by command, none refused.

**What else the round turned up** - two defects, both fixed where found, neither a change to the process:
`check-bundle`'s excerpt emptied a re-check bundle silently when a question's last paragraph was never closed in its
HTML (the session fixed the excerpt to keep such a block, and closed the paragraph); and one session reported `make
page-check` failing two or three browser tests - owed an answer before the push (T25), whatever its cause.

**The verdict the GM asked for.** No change to the research process is recommended. Across R6 to R11 every tooling
cost the rounds measured has been brought down and has stayed down on the next page - what a check reads, how a
report is applied, how large a session grows, what a long source costs - and the figure per thing checked now sits
at 0.7 to 1.1 million on ordinary pages, moving with the page's own work (how hard its claims are to source), not
with the tooling. So, per the GM's instruction of 2026-09-27, the remaining research tasks move to a new feature and
this one closes, so the process lands on main and other sessions can research other things with it.

## R12 - the closing report (FR-009, T25; plan D20)

**What closed here.**

- **FR-001** - `cities/sizing` footnoted (T03 to T07).
- **FR-002 and FR-006** - ten pages worked to the standard, each by a write session and check sessions:
  `homesteads`, `vegetation`, `cities/defenses`, `religion-and-death`, `cities/government`, `cities/fabric`,
  `fields`, `archetypes`, `cities/hinterland`, `water` - every listed assertion on them in one of the three forms,
  every FR-006 item on them confirmed or worked (the per-page counts are in each task's verify line).
- **FR-007** - every page's changed questions quote-checked and record-formatted with one re-check round, every new
  registry key through `source-applicability`, and every `entry-drift` pair `_entry_owed.py` named answered: the
  owed pairs rewritten or labeled where they had drifted, and the 12 left named at the close each recorded IN-STEP
  in `owed-verdicts.md` (`brief.py owed-check`: 12 pairs, 12 IN-STEP, 0 open, 2026-09-27).

**What moved to feature 265** (the GM, 2026-09-27; plan D20): FR-002 and FR-006 for `towns`, `cities/river-cities`,
`buildings`, `urban-features` and `ways`, and FR-006 for `cities/capitals` - NEVER SEARCHED here, not searched and
failed; FR-003 to FR-005 (the sweeps) and FR-008 (the download list) - not begun here.

**What did not close, searched and failed** - each labeled in its note, and owed to the download list under 265's
FR-008: the Tabayashi 1987 paper (`water`, main canals narrowing) and Chang's model plans (`cities/fabric` 040,
`cities/fabric` 030 citing the same), both scanned PDFs no tool in the container can read; and the four
`religion-and-death` PDF notes T45's verify line records as unfetchable in the container.

**Two decisions for the GM**, recorded as future work at their request (D19.2): the dike-pond mulberry density and
the modern dike forms (`future-work/farming-communities.md`).

**What lands with this feature - the research process** (research R1 to R11, plans D1 to D20): a page worked from
briefs (`measure/brief.py`: split sessions first for any over-cap item question, a write session, check groups
packed by load, owed modals folded in) run headless by `make page-session`; checks that read bundles outside the
repository (`make check-bundle`, per check, a long source as an excerpt for `source-applicability` and in parts for
`source-reader`), reports applied by command (`make apply-edits` - `quote-check`, `record-format`, `entry-drift`,
`source-applicability`); `make canon` and `canon-read-hooks.sh`; the question size cap; `tokens.py` to measure it.
Across the rounds a page's cost came to 0.7 to 1.1 million tokens per thing checked on ordinary pages (R8 to R11);
the first three rounds, measured per item rather than per thing, ran 1.56 to 2.58 million an item (R3). Found and fixed in the closing work: the glossary tooltip showed every
term in a paragraph the paragraph's last definition (`page.js`), and the review-round hook read a report's later
mention of FAITHFUL as its verdict.
