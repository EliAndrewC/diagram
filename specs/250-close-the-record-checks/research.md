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
| the main session (92 turns) | 18.6 million | 91,000 | 87% |
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
peak context, and five to twelve times what it read of the record.

**The experiment (X1).** `record-format` over `ways` 010 twice, same fragment, same prepass, same tier:

| where the agent read the entry | nested files | peak | input | candidates ruled on |
|---|---|---|---|---|
| in the tree (`research/ways/...`) | 3 | 47,700 | 102,300 | 33 of 33 |
| copies in the scratchpad | 0 | 14,500 | 62,600 | 25 of 25 |

Peak context fell 70%; billed input 39% (the second run took five turns where the first took three). One
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
