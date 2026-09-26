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

**The main session is now where the tokens go.** It was 83% of this page's measured total, and the agents 17%. The
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
