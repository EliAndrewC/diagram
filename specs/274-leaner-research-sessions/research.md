# Research - feature 274: where the research sessions' tokens went, after feature 250 landed

## R1 - the measurement (2026-09-27, the GM's question in request.md)

**Method.** Every page session since feature 250 landed (2026-09-27 ~05:00 UTC) was aggregated from its transcript's
`usage` fields, folded per message id as `specs/250-close-the-record-checks/measure/tokens.py` folds them: 282
sessions in 65 groups, from 250's tail and features 267, 269, 271 and 272, 1.17 B tokens. A group is a write session and
its check sessions; a thing checked is a question, an `entry-drift` modal or a registry key, as in 250's R10/R11. The
per-group table is `measure/groups-table.txt` (and `groups.json`); the scripts that made it are in `measure/`.
Prices are Opus rates relative to uncached input: cache read 0.1x, 1-hour cache write 2x, 5-minute write 1.25x,
output 5x.

**Against 250's band (49 complete groups).**

| | 250 R8-R11 | now: median (IQR) |
|---|---|---|
| per thing checked | 0.7-1.1 M | 1.02 M (0.86-1.20) |
| largest context any turn | 102-171 K | 246 K |
| mean main turn | 56-90 K | 85 K |
| group total | 6-10 M | 22 M, for 21 things |

The cost per thing held. The largest context doubled, and that is the write sessions: median 74 turns, peak 237 K,
mean turn 147 K. A write session's cost correlates 0.92 with its turn count and 0.54 with its key count. Groups are
about twice R11's size, and because every turn re-reads the context so far, a session's cost grows roughly with the
square of its length. The outliers were all long write sessions: one 272 write session cost 24.5 M over 109 turns,
peaking at 385 K. Two 271 write sessions cost 20.0 M and 13.2 M.

**Where the tokens go** (observed 2026-09-27; method: `measure/decomp.py` over R1's sessions). Write sessions' main context is 48.5% of raw tokens (36.6% by price); check sessions' main
context is 37.8% (31.5% by price); agents are 11.7% raw but about 30% by price. In a check session's main input the
fixed floor is the largest part at 34%: about 20 K a turn, of which the clone's root CLAUDE.md is about 5.2 K and the
research CLAUDE.md about 3.5 K.

**What the per-page rounds could not see.**

- **Coordination files are re-read whole** (observed 2026-09-27; method: the transcripts' Read calls, `measure/collect.py`). 619 reads of the cross-session claims file across 172 sessions (~30 M
  carried), 418 reads of a group's handoff across 254 sessions (~20 M, though the briefs say "read only your own
  lines"), and 388 reads of a checks report across 183 sessions (~12 M), mostly to append a line. Together that is
  about 60 M, or 5%.
- **Not worth changing:**
  - Resumes after a usage limit cost under 0.5%.
  - Merging check sessions would cost more: the floor is paid every turn, and a merged session carries the first
    half's context. Two questions a session measured 1.01 M a question.
  - Sources are almost never read twice by different groups.
  - The quote-check re-checks find a real problem 13% of the time after fixes, so they stay.

**The candidates** (observed 2026-09-27; method: estimates from the figures above).
1. Cap a write session at about 4 questions or 10 keys: est. 188-231 M saved (16-20% raw, about 10% by price).
2. Own lines only for coordination files: est. 40-50 M (about 4% raw).
3. A slim instructions file for headless sessions: about 5 K a turn over about 12,500 turns, 60 M raw, about 2% by price.
4. Batch source-applicability keys: about 3% by price, but a "fewer, bigger checks" change that would need seeded-fault
   runs. Not requested.

## R2 - the probe: a page session's first turn under the old and the new flags (FR-004, SC-003)

<!-- The probe's size, stated before launch (plan D9): two headless sessions of one turn each, each answering one
line, about 50 K tokens in all. Run by `measure/probe.sh`. -->

**Method.** `measure/probe.sh`, 2026-09-27, from this clone: two headless sessions launched as the runner launches a
page session, each asked for the single word OK (one turn, no tool). OLD is the launch before this feature (the
standing authorization appended; only the mirror's root CLAUDE.md excluded). NEW is `floor_flags` now (the clone's own
root CLAUDE.md excluded too; the slim rules file appended after the authorization). The first turn's input is its
uncached tokens plus the cache write plus the cache read, from each session's JSON `usage`.

| launch | session | first-turn input | uncached | cache write | cache read |
|---|---|---|---|---|---|
| old | `ec30b943` | 19,642 | 2 | 13,376 | 6,264 |
| new | `909b7b3f` | 13,050 | 2 | 6,784 | 6,264 |

**Result** (observed 2026-09-27; method: the two probe sessions above). The floor fell by 6,592 tokens a turn (34%). That is more than R1's estimate of about 5.2 K for the root
CLAUDE.md, because the file has grown since, and it is net of the slim file (about 1.5 K) added in its place. At
R1's rate of about 12,500 page-session turns, it is about 82 M raw tokens, most of them cache reads.
The research record's CLAUDE.md is not in either figure because the probe reads no research file. It still loads
under both launches.

## R3 - the groups that ran after the landing (feature 347, owed by FR-004)

**Method** (observed 2026-10-10; method: `specs/347-measure-feature274-write-cap-line-reads/measure/run_all.sh`, its
output `results.txt`). Every page session in every clone that started after the landing (2026-09-28T03:43:49Z,
6555db77b): 662 sessions in 299 groups. 274's `collect.py` could not be reused as it stood, because a check brief
written after the landing no longer lists its questions ("the ones the handoff names"). 347's collector counts a
group's things from its handoff instead (distinct questions and registry keys, plus `entry-drift` runs) and folds
each transcript with 274's own helpers. **It reproduces R1 on R1's window** (sessions after 250 landed and before
22:30 on 2026-09-27): 1.04 M per thing (IQR 0.88-1.20) against R1's 1.02 M (0.86-1.20), and a complete-group peak
median of 246 K, as R1 found. Sessions between 22:30 and the landing are in neither set. R1's "about 60 M" of
coordination reads counts every call that names a claims file, a handoff or a checks report, Bash `cat` the bulk of
it; 347's `coord.py` counts the same way and finds 58.4 M on R1's window.

**Which groups compare with R1.** The groups after the landing are of three kinds:
- Research groups like R1's: 269's second half, 280, 291 and 317.
- The 292 restyle sweep: 400 sessions, most groups 1-4 questions.
- The 319 modal write-ups.

The last two are not the same work as R1's, and a group of them checks 2-4 things. So the table gives the
like-for-like rows first and every group last. Feature 269 ran on both sides of the landing, which makes its two
rows the closest comparison.

| (observed 2026-10-10; method: `analyze.py`, `coord.py`) | R1 | 269 before | 269 after | research groups after | every group after |
|---|---|---|---|---|---|
| complete groups | 48 | 12 | 11 | 66 | 175 |
| things checked a group (median) | 21 | 15.5 | 7 | 8 | 4 |
| **per thing checked**, median (IQR) | 1.04 M (0.88-1.20) | 1.18 M | 1.36 M (1.04-1.54) | **1.36 M (1.08-1.87)** | 2.63 M (1.36-5.16) |
| peak context, complete-group median | 246 K | 216 K | 130 K | 169 K | 174 K |
| largest context of any turn | 385 K | 274 K | 202 K | 332 K | 601 K |
| write session turns (median) | 76 | 65 | 46 | 54 | 40 |
| write session mean turn | 152 K | 128 K | 85 K | 105 K | 107 K |
| write session peak (median) | 246 K | 220 K | 130 K | 165 K | 149 K |
| coordination: whole reads (`cat`, Read) | 693 calls, 50.8 M | | | 18 calls, 0.5 M | 92 calls, 5.8 M |
| coordination: every call naming the files | 1,265 calls, 58.4 M | | | 1,232 calls, 30.5 M | 3,267 calls, 86.6 M |

The last column covers 662 sessions against R1's 261, so its coordination total is not per-session comparable. Per
session it is 0.13 M against R1's 0.22 M.

**Where the cost per thing went** (observed 2026-10-10; method: `split.py`, medians over complete groups).

| | things a group | write M/thing | check M/thing | agents M/thing | total M/thing | check sessions a group | write turns a thing |
|---|---|---|---|---|---|---|---|
| R1 window | 21 | 0.56 | 0.37 | 0.11 | 1.04 | 3 | 3.5 |
| 269 before | 16 | 0.56 | 0.47 | 0.15 | 1.18 | 3 | 4.3 |
| 269 after | 7 | 0.59 | 0.59 | 0.15 | 1.36 | 2 | 6.2 |
| research groups after | 8 | 0.63 | 0.53 | 0.18 | 1.36 | 2 | 6.8 |

The cap did what it was built to do to a write session. It is shorter (54 turns against 76), each turn is lighter
(105 K against 152 K), and the peak is back inside 250's band. But a group now carries about 8 things where it
carried 21. Both a write session and a check session have a fixed part that does not shrink with the work: the
check sessions run about 37 turns each, two a group, whatever they check. That fixed part is now spread over fewer
things. A write session takes 6.8 turns a thing against 3.5, and a check costs 0.53 M a thing against 0.37 M. R1's
estimate modeled the quadratic term and not this fixed part. The saving it predicted on the write side is real per
turn, and it is spent on the extra turns per thing.

**Did the cap hold?** (observed 2026-10-10; method: `cap.py`, which counts each write brief with the runner's own
counter as it stood at the landing and as it stands now, counts `make reserve KIND=registry` in each write session's
transcript, and reads the guard log.)
- **Continuations.** Zero `continued` lines in any clone's run logs, and no `continue.md`.
- **Keys.** No write session reserved more than 10 registry keys, so the key cap was never reached. That, not a
  broken hook, is why nothing was ever split.
- **Questions.** 11 write sessions counted over 4 questions without an exempt `page-load`. All of them were 319's
  modal briefs, and every one ran under a logged `WRITE_CAP_OK`: 16 escapes, reason "each brief edits at most four
  questions; the counter reads modal names in quoted conflict lines as questions".
  - Those briefs named their questions on a plain "Questions to edit:" line, which the counter does not read, and
    used `- ` lines for conflicts, which it does read as items. Their handoffs show 4, 4, 4 and 5 distinct questions
    for h1, h5, h8 and h12. h12 edited one of its "read also" questions, which made five.
- **The 292 sweep.** It ran under 127 logged escapes (its plan D7: "a merge cannot be split across sessions"). Its
  briefs sat in a scratchpad that no longer exists, so they could not be counted.
- **A counter defect.** One count was a defect in the counter itself, fixed with this measurement. 269's FX1 assigns
  four items but counted six, because two of its lines cite another item's finding ("B16's finding") and the counter
  took every item id on a line. It now takes only the ids that lead a line: `scripts/pages/brief_load.py`, test
  `test_an_item_that_cites_another_items_finding_is_still_one_question`.

**The coordination reads.** Whole reads are gone: 18 calls carrying 0.5 M in the research groups, against 693
carrying 50.8 M (observed 2026-10-10; method: `coord.py`). The line reads that replaced them still carry 30.5 M:
- `make lines` on the claims file carries 16.0 M over 266 calls. Its median result is 4,147 characters (p90 12,212,
  largest 20,553). The file is 170 KB, and a session greps it by a page name that matches many lines.
- The handoff line reads carry 8.3 M over 206 calls.

So coordination costs about half what it did, not near zero.

**`decomp.py`** was not re-run: none of the figures to beat rests on it. The floor it measured is R2's probe, a
measurement of the launch flags that does not change with the groups that ran.

**Verdict** (observed 2026-10-10; method: the tables above), against the figures to beat. Each is judged on the
research groups, with every group's row in brackets.

| expected (observed 2026-10-10; method: the tables above) | measured | verdict |
|---|---|---|
| write sessions under ~40 turns | median 54 (every group: 40) | not met. Down 29% from 76, but not under 40 |
| the peak back inside 102-171 K | complete-group median 169 K (174 K); write sessions 165 K (149 K) | met for the research groups, at the band's top |
| per-thing cost 10-20% lower | 1.36 M against 1.04 M, up 31% (2.63 M, not comparable) | **not met: it rose**. 269 before and after, the same feature, rose 15% (1.18 -> 1.36 M) |
| coordination reads near zero | whole reads 0.5 M against 50.8 M; all calls 30.5 M against 58.4 M | whole reads met; all calls halved |
| how often the key cap split a session | never | the key cap was never reached; the question cap was respected or escaped with a stated reason |

The caps shortened the sessions and lowered the peak, and the line reads ended the whole reads. But the cost per
thing checked rose, because groups got smaller while each session's fixed cost did not. The next lever is the fixed
part of a group, not the length of a session: one check pass over several write sessions' output, and a `make lines`
that answers the claim a session needs rather than every line naming its page. Both are filed as feature 376.
