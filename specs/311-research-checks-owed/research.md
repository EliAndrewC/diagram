# Research - feature 311

Measurements behind the plan's decisions and the spec's success criteria, each with how it was taken.

## R1 - SC-005: the seeded runs (2026-10-02)

One batch bundle of 24 questions, the backfill's size (plan D4: the seeds tested in the form the backfill uses), built three
times with `make check-bundle FOR=intro-check QS="0001 0003 0005 0006 0008 0014 0016 0028 0029 0031 0036 0083 0094 0110 0120 0140 0150 0160 0170 0180 0191 0200 0210 0220"`,
and in each copy of 0083 a planted intro (`_check_bundle.refresh` rewrote the MANIFEST around it): *"In Rokugan, the border
between two clans is marked by a carved stone post every hundred paces ... Every domain border in Edo Japan carried such
posts at that spacing ..."* - a setting detail no page carries and a historical claim the findings (earth mounds, no fixed
spacing) contradict.

| seed | known ruling | run 1 | run 2 | run 3 |
|---|---|---|---|---|
| 0094 parley room, no intro | NEEDS-INTRO | NEEDS-INTRO | NEEDS-INTRO | NEEDS-INTRO |
| 0036 farmhouse groves (a plain farm subject) | NO-INTRO-NEEDED | NO-INTRO-NEEDED | NO-INTRO-NEEDED | NO-INTRO-NEEDED |
| 0083 planted intro with an unsupported claim | INTRO-FIX | INTRO-FIX (both faults named) | INTRO-FIX (both) | INTRO-FIX (both) |

9 of 9. The borderline questions moved between runs: 0003 (place names) was flagged in runs 2 and 3, 0110 (border court) in
run 3 - which is why a backfill ruling on a borderline question is read for its REASON, and why the gate's own rounds are on
the written intro rather than on a re-run of the backfill. All three on Opus through an ad-hoc agent handed the contract (R3).

## R2 - SC-002: the owed command replayed over main's record-only commits

`_record_owed.py --between <c>^ <c>` over every non-merge commit on main since the record took its present layout (feature
303's `058ecd101`; before it the question pages lived under per-subject directories the command does not read), touching
`research/questions/` or the registry and no engine file. There are FIVE such commits, not thirty: since 303 the record has
mostly changed beside engine work. "Doctrine owed" counts what "every new or changed entry" reads as - `quote-check` and
`record-format` on each question touched, `source-applicability` on each write-up touched.

| commit | what it did | questions touched | write-ups touched | doctrine owed | owed units |
|---|---|---|---|---|---|
| `404f57474` | Feature 308: Inashiro notes; the bamboo drawing page | 1 | 0 | 2 | 2: quote-check 1, record-format 1 |
| `5efc03d00` | footnote the persimmon drawing rules | 2 | 0 | 4 | 9: quote-check 7 (one per note), record-format 2 |
| `b689e29db` | Feature 305: six tag corrections | 0 | 6 | 6 | 0 (tags are comments) |
| `8ea159a69` | Feature 305: registry sweeps (163 re-trimmed) | 0 | 171 | 171 | 163: source-applicability 163 |
| `6067a07ac` | Feature 305: every entry tagged, 910 limits paragraphs rewritten | 0 | 2,110 | 2,110 | 911: source-applicability 911 |

No commit that changed no note, no noted block and no write-up's words owed a source-reading check: the tag corrections owed
nothing, and the two registry sweeps owed exactly the entries whose visible words moved - 163 against the commit's own "163
re-trimmed", 911 against its "910 limits paragraphs". The replay also found a defect: the registry is numbered past four
digits (1,028 of its 2,126 files are `1xxxx-`/`2xxxx-`), and a four-digit filename pattern had read none of them, so a new
write-up there would have owed nothing (fixed; `test_a_write_up_numbered_past_four_digits_owes_its_check`).

## R3 - A defined agent added mid-session is not dispatchable until the session restarts

`Agent(subagent_type="intro-check")` returned *"Agent type 'intro-check' not found"* in the session that wrote the file. The
seeded runs, the backfill and the written intros' first round therefore ran as an ad-hoc agent on Opus (`model: opus`, the
project's rule for an ad-hoc judge) told to read `.claude/agents/intro-check.md`'s body verbatim - the same contract, without
the pinned effort or `omitClaudeMd` (its prompt read only bundles outside the repository, so no nested `CLAUDE.md` attached).
The next session dispatches the defined agent by name.

## R4 - What the owed command costs at the push

`make record-owed` on this clone, 2026-10-02: 10.5 s as first written, of which 6.2 s was `_translation_owed.py` reading each
notes file with its own `git show` and 2.4 s the registry read whole at the base. One `git cat-file --batch` per revision, a
content-keyed cache of the parsed pairs (`<git dir>/record-checks/translation-pairs.json`) and reading only the write-ups the
delta touched took it to 2.5 s (translation half 0.6 s warm). The `intro-check` batch bundle, first 2+ minutes for 24
questions (the owed units and the modal classes recomputed per question), is about 7 s for four once both are computed once.

## R5 - The parley-room intro and the drawing page

Both `intro-check` (INTRO-OK) and `record-format` (0/0/0) noted that the GM's draft has the two sides "at a table placed
precisely on the border ... sipping tea", each entering "through a door in its own lands", where the drawing page draws
kneeling mats two a side and makes the door that receives the delegation the border itself. The intro keeps the GM's own
words; which picture stands is the GM's call, raised in the closing report.
