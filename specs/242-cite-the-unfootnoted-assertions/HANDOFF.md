# Handoff - feature 242, cite the unfootnoted assertions

Written 2026-09-14 for the session that picks this feature up. The GM paused the feature because its
checks were consuming the weekly token quota; nothing here is blocked on a decision, and nothing is
half-edited. This file says what is done, what is not, where the evidence sits, and what to run first.

## 1. State in one paragraph

Every research page except `cities/sizing.html` has had its bare assertions footnoted from
source-reader returns (14 page passes, about 1,440 citation notes and 314 absence notes across 19
citations pages, 0 never-searched absence notes left). 117 new registry keys were added since commit
`700933b0` and judged by `source-applicability`; the registry corrections from four of the five
applicability batches are applied. Thirteen check reports (5 applicability, 4 quote-check, 4
record-format) were filed on the whole record and copied verbatim into `handoff/reports/`; the findings
of nine of them are NOT yet applied. The four record tests pass on the committed tree. No task is ticked,
nothing is pushed beyond the number claim.

## 2. Where the work lives

| what | where |
|---|---|
| clone | `/diagram/.clones/diagram-research` (session name `diagram-research`) |
| tip | `720f68f6` "242: registry write-ups corrected from source-applicability batches 2-5" |
| unpushed | 48 commits ahead of `origin/main`, all on `main` in the clone; the first feature commit is `d7ba038e` |
| pushed | only the number claim: `specs/242-cite-the-unfootnoted-assertions/` exists on `origin/main` |
| exports | `export SPECIFY_FEATURE=242-cite-the-unfootnoted-assertions; export SPECIFY_FEATURE_DIRECTORY=specs/242-cite-the-unfootnoted-assertions` |
| spec review | FAITHFUL; `plan-review.json` CLEAR at round 2 (commit `2896f403`) |
| research record | `research.md` R1-R10 (R5-R10 are the per-page passes and what they corrected) |
| download list | `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` entries 93-224 are this feature's, in the GM's format |
| tooling | `measure/worklist.py`, `measure/apply_notes.py`, `measure/note_census.py`, `measure/inventory_census.py`; the session helpers copied to `handoff/_lib.py` and `handoff/batch-templates/` |
| check reports | `handoff/reports/` (17 files: the 13 whole-record checks plus the four earlier homesteads/water and urban-features checks that were already applied) |

Working tree at the tip is clean apart from this `handoff/` directory.

## 3. Task by task

Nothing is ticked because `make tick` was deferred until every page had passed its checks, and the
checks came back after the pause. The verification each task owes is named in the last column.

| task | page | state | what the checks still owe it |
|---|---|---|---|
| T01 | `cities/capitals.html` | footnoted (commits `717e4665`..`1bb38215`), record-format, quote-check and applicability applied | none known; 30 items the work list reads as LOCATED (see section 4) want a hand check |
| T02 | `urban-features.html` | footnoted, checks applied (`e56a61fd`, `764fccc5`, `8144e925`) | none known |
| T03 | `homesteads.html` | footnoted, checks applied (`123aa97a`) | none known; 23 LOCATED items want a hand check |
| T04 | `water.html` | footnoted, checks applied (`123aa97a`) | none known; 14 LOCATED items want a hand check |
| T05 | `fields.html` | footnoted (`e4fdacb6`, `afa08e29`) | `qc-fields-religion-archetypes.md`, `rf-fields-religion-archetypes.md`, `appl-01.md` unapplied |
| T06 | `religion-and-death.html` | footnoted (`25cd7c8e`) | same three reports unapplied |
| T07 | `archetypes.html` | footnoted (`f8a5c305`) | same three reports unapplied |
| T08 | `buildings.html` | footnoted (`706cd990`) | `qc-buildings-vegetation.md`, `rf-buildings-vegetation-river-cities.md` unapplied; `appl-02.md` applied |
| T09 | `vegetation.html` | footnoted (`77d0a837`) | same two reports unapplied; `appl-03.md` applied |
| T10 | `cities/river-cities.html` | footnoted (`09b784b9`) | `qc-river-cities-defenses-towns.md`, `rf-buildings-vegetation-river-cities.md` unapplied; `appl-03/04` applied |
| T11 | `cities/defenses.html` | footnoted (`7a3bb2cb`) | `qc-river-cities-defenses-towns.md`, `rf-defenses-towns-fabric.md` unapplied |
| T12 | `towns.html` | footnoted (`f8896cae`) | same two reports unapplied |
| T13 | `cities/fabric.html` | footnoted (`ccfc1b03`) | `qc-fabric-government-hinterland-ways.md`, `rf-defenses-towns-fabric.md` unapplied |
| T14 | `cities/government.html` | footnoted (`84521b49`) | `qc-fabric-government-hinterland-ways.md`, `rf-government-hinterland-ways.md` unapplied |
| T15 | `cities/hinterland.html` | footnoted (`69e8147a`) | same two reports unapplied |
| T16 | `cities/sizing.html` | **UNTOUCHED** - 5 of its 6 items carry no footnote; no reader batch was dispatched for it | the full pipeline (section 6) |
| T17 | `ways.html` | footnoted (`69e8147a`) | same two reports as T14 unapplied |
| T18 | never-searched absence notes | done - `note_census.py --list --json` returns empty; the 120 notes were rewritten page by page inside T01-T17 | tick with that command's output as the verification |
| T19 | roster disclosures | done (`541e1f57`, `700933b0`, `57d99559`, `4688b32e`) - every roster that said "unsourced" or "a GUESS - no readable page supports it" now names whose reading the figure is, with search history in comments | tick |
| T20 | download list | entries 93-224 appended; **nine more owed** (section 5, item E) | append, then tick |
| T21 | closing report | not written | write after the reports are applied (section 6 gives the counts) |
| T22 | `make page-check`, `make done`, push | not run | last |
| T23 | guidelines paragraph | done (`cc540e8c`) | tick |

The item counts in `tasks.md` are upper bounds from `inventory_census.py`; the per-page reader batches
covered every item.

## 4. How to read the work list now

`python3 measure/worklist.py <page> --json` (run from `.claude/skills/diagram`, page path relative to
`research/`) lists each inventory item with a status. FOOTNOTED means the line the sentence was located
on carries a `<sup class="fn">`; LOCATED means that line carries none. The test is line-level, and many
sentences were rewritten or corrected during the passes, so a LOCATED item is usually one whose mark sits
on a wrapped continuation line or whose wording changed, not a bare assertion. Counts at the tip:

| page | FOOTNOTED | LOCATED | NOT-LOCATED / TOO-SHORT / AMBIGUOUS |
|---|---|---|---|
| capitals | 55 | 30 | 7 |
| urban-features | 79 | 2 | 6 |
| homesteads | 19 | 23 | 3 |
| water | 20 | 14 | 8 |
| fields | 20 | 13 | 4 |
| religion-and-death | 31 | 1 | 1 |
| archetypes | 25 | 0 | 1 |
| vegetation | 6 | 12 | 1 |
| river-cities | 13 | 5 | 0 |
| sizing | 1 | 5 | 0 |
| every other page | all | 0 | 0-1 |

Only `sizing.html`'s five are known to be genuinely bare. For the rest, open the page at the line the
work list names and look for the mark on the adjoining lines before treating an item as open.

## 5. The thirteen reports and what each still owes

All verbatim in `handoff/reports/`. The scratchpad they were written to does not survive the session;
these copies are the record.

**A. Source applicability** (`appl-01..05.md`, 117 keys, none NOT-APPLICABLE as a whole source).

- `appl-02` (buildings, archetypes, religion keys), `appl-03` (vegetation, river-cities keys), `appl-04`
  (defenses, towns, hinterland, ways keys), `appl-05` (government, ways, fabric keys): **applied** in
  commit `720f68f6` - the missing limits added to each entry's "Why it applies, and its limits", the
  overstated clauses removed, `panmen-zhwiki` dated to its Yuan fabric, three kotobank citation lines
  renamed to the works the pages carry.
- `appl-01` (fields, religion keys): **unapplied.** Six "What it is" corrections owed: `cultivator-enwiki`
  describes a modern machine and the page does mention paddy; `hongwu-emperor-enwiki` carries no 1390s
  date; `kotobank-kyodo-bochi` names the wrong works and its passage is from the 墳墓 entry;
  `sanuki-kokubunji-jawiki` and `shimotsuke-kokubunji-jawiki` cite a guidebook and signage, not
  excavation reports; `osaka-nanabaka-jawiki` attributes 2019-20 counts to 2017. Nine missing limits
  (genge undated, mu varied by period, danka Japan-only, fushimi count is today's, kyodo-bochi universal,
  and so on) and two overstated ones (`fushimi-inari-enwiki` does give the rows; `sodo-jawiki` gives one
  tatami per monk).

**B. Quote-check** (four reports, 233 notes checked; no host refused; no NOT-READABLE).

- `qc-fabric-government-hinterland-ways.md`: hinterland fn-18 quote NOT-ON-PAGE (the page's own words are
  "In southern China, clan members could form a village known as an ancestral village"); fabric fn-64 and
  government fn-53 do not support their sentences; government fn-44's quoted year (1669) contradicts the
  body's 1668; government fn-56 renders 人宿 as "ninshuku" against "hitoyado" elsewhere; fabric fn-19's
  prose still says "no source is cited"; fabric fn-71 truncates the source's purpose clause; ways fn-26's
  parenthetical quotes a width not on the page; four notes rest on the Chang PDF, public but image-only.
- `qc-buildings-vegetation.md`: DIFFERS at buildings fn-102 (missing 担当する), fn-110 (貲 for 資),
  vegetation fn-107 (second quote is a paraphrase of the 1972 rule), fn-109 (dropped parenthetical);
  buildings fn-111 cites a sentence the prose calls unsourced; fn-108's English carries a clause outside
  its original; vegetation fn-122 quotes the tsuijimatsu full circuit that fn-89 and the roster declare
  absent; fn-108 (grounds) carries a physical claim; seven truncations without ellipsis; six notes on
  image-only PDFs (`coggins-minor-2018`, `umca-windbreak-manual`).
- `qc-river-cities-defenses-towns.md`: river-cities fn-20 and fn-37 NOT-ON-PAGE (the link is 上海老城厢,
  the registry names 上海县城 - probably a mis-pointed link); fn-27's kotobank 27 m sentence not on the
  page (the page gives the 200-koku Tone boat with no length); fn-31 and fn-39 attached to the wrong
  sentence; fn-32 drops the source's hedge; fn-40's flushing clause uncited; defenses fn-31 traditional
  characters against a simplified page; fn-36/37/38 rest on the `jah-song-military-cities` PDF, public
  but unreadable to the tool; towns fn-29 comma, fn-41 wording, fn-44 wiki brackets, fn-45 階層; towns
  fn-36/37 carry unmarked project English in 「」; fn-38 uses a ward-gate curfew for a city gate.
- `qc-fields-religion-archetypes.md`: religion fn-138 attached one clause late (Sakai and Akita carry no
  mark); archetypes fn-121 and fn-132 misplaced; fields fn-99 (0.164 not 0.1647), fn-115 (條 for 条, and
  misplaced), fn-123 (en dash, "While terrace beds"); archetypes fn-120's 25-30 percent comes from a
  chapter the key does not link and the prose says 15-30; five PDFs unverifiable (`tabayashi-1987`,
  `obata-1977-taue`, `feng-yizhong-jiangnan`, `lin-2001-miaohui`, `chi-2024-dike-pond-commons`).
- Each report ends with the unfootnoted real-world assertions it found per section: roughly 40 across the
  twelve pages, each wanting an absence note or a citation.

**C. Record-format** (four reports).

- `rf-fields-religion-archetypes.md`: nine Japanese quotations in `fields.html` (water-depth and
  shitsuden sections) stand original-first without the translation form, one with no English; five
  `., ` roster artifacts on fields; two footnote marks inside a quotation and an "e.g."; an unmatched
  `</strong>` and a duplicated clause on archetypes; a garbled clause in the pigs-and-ducks item; several
  history passages to move into comments; `L7R` and `ft/px` in religion prose; glossary terms owed
  (lodging, oyaike, yui, tauchiguruma, seed, adlittoral, muen variant); citations-page defects (dangling
  punctuation in seven fields notes, three backticked bare keys on archetypes, OCR garbles unrepaired).
- `rf-buildings-vegetation-river-cities.md`: **a nested HTML comment on `vegetation.html` around line 440
  leaks a fetch list and a literal `-->` into the reader's text** (fix first); a duplicated clause at
  line 394; `ACCURATE` labels in a vegetation heading and body; two untranslated quotations in
  buildings prose; the `ochiba` glossary term fires on the manor named Ochiba; `fire-gap` hyphenated
  form has no tooltip; footnote marks inside `<em>`; five duplicated English renderings and two
  `((English).` on the buildings citations page; the `hu-2011` citation line carries fetch verdicts;
  roughly 70 registry citation lines give titles only in Japanese or Chinese.
- `rf-defenses-towns-fabric.md`: roster carrying footnote marks on defenses; "What the research found"
  field labels in prose; a comment swallowing a sentence opening on defenses line 96; duplicated 18 ft
  disclosure across two fabric entries; history passages on towns (frontage test, shelter-belt metrics);
  duplicated quotations and unmarked 「」 English on the towns and defenses citations pages; glossary
  terms owed (bastion, menbansho, mukaibansho, master laborer, juan, Wubei Zhi, and others) and variants
  (ditai under mamian, uranagaya).
- `rf-government-hinterland-ways.md`: government roster at line 66 broken by prose; a contradicted claim
  at line 88 (Sendai and Hachinohe); untranslated 侍町/町人地/寺町 at line 103; hinterland line 67 has no
  opening `<p>`; ways history passages (the 2026-07-22 plank census, the hand-placed decks); doubled
  quotations on the government citations page (fn-9, fn-13, fn-20) and the trailing-paraphrase pattern
  in ten notes; `SOURCES.html` carries the `attested-instances-anchors-not-works` heading twice (lines
  2185 and 4462) with the same table; garbled `manzello-2019-firebrand` sentence; glossary terms owed
  (girder, footslope, post-horse system, waystation, metrology, stroke, and others).

## 6. What remains, and roughly how much

In the order a fresh session should take it:

1. **Fix the reader-visible defects first** - the vegetation comment leak, the hinterland missing `<p>`,
   the archetypes unmatched `</strong>`, the government roster, the duplicate `SOURCES.html` heading.
   Under an hour of edits; no agents.
2. **Apply the quote-check findings** (section 5B): about 25 note edits, 6 mark relocations, 3 notes
   converted to absence notes, 2 prose corrections. A session's afternoon; no agents, except one
   `source-reader` to check whether zh.wikipedia 上海县城 carries the two Shanghai moat passages.
3. **Apply the record-format findings** (5C) and `appl-01` (5A): about 60 edits across pages, citations
   pages and the registry, then `make glossary` after adding roughly 50 terms and variants to
   `l7r/diagram/interactive/assets/glossary.json` (a term no page uses fails a test).
4. **Footnote `cities/sizing.html`** (T16): one `source-reader` batch over its 6 items (template in
   `handoff/batch-templates/`), then `apply_notes.py`, then one `quote-check` and one `record-format`
   over that page.
5. **Absence notes for the unfootnoted assertions** the quote-checks listed (about 40), through
   `apply_notes.py` with `form: absence` and a `searched` field naming the pages read for that section.
6. **Download list**: append entries 225 onward for the image-only PDFs (Chang morphology,
   `jah-song-military-cities`, `tabayashi-1987`, `obata-1977-taue`, `feng-yizhong-jiangnan`,
   `lin-2001-miaohui`, `chi-2024-dike-pond-commons`, `coggins-minor-2018`, `umca-windbreak-manual`), each
   with a direct link and a Google-search fallback.
7. **Re-run the four record tests** after each page:
   `make citations && make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`
   (257 passed at the tip).
8. **Re-check**: one `quote-check` and one `record-format` over the pages edited in steps 2-5 is the
   honest close; budget them (section 7). A `source-applicability` pass is owed only for keys added in
   step 4. No `settlement-review` is owed (no map changed).
9. **T21**: write the closing report into `research.md` as R11 from the counts in `note_census.py --json`
   and `worklist.py`; note the two items feature 238 left to the GM as settled (the inn's form knob in
   feature 244; the Xuxiebian absence note as the record carries it).
10. **Tick** T01-T23 with `make tick F=242-cite-the-unfootnoted-assertions T=Txx NOTE="..."`, then
    `make page-check`, `make done`, `scripts/sync-with-main.sh done`. The push refuses while any task is
    open, and the delta is research-only, so the route is DIRECT.

Remaining effort, honestly: two to three working sessions, most of it the edits in steps 2, 3 and 5, and
the token cost concentrated in step 8's re-checks.

## 7. What was expensive

The check agents, not the edits. Measured on this feature's last round (Opus, per agent):

| agent | tokens each | duration |
|---|---|---|
| `source-applicability` over 25 keys | 230,000-280,000 | 7-8 min |
| `quote-check` over 2-4 pages | 340,000-440,000 | 12-15 min |
| `record-format` over 3 pages plus their citations pages and the registry band | 430,000-720,000 | 13-19 min |

The thirteen together cost about 5.5 million subagent tokens. `record-format` is the heaviest because it
reads `SOURCES.html` (about 4,500 lines) alongside the pages. Ways to spend less next time: give
`record-format` only the changed sections rather than whole pages; dispatch `quote-check` per page rather
than per three pages so a failed fetch does not cost the batch; skip the registry band once its
citation-line titles are translated in one mechanical sweep. The `source-reader` batches themselves
(about 30 batches of 10 items) were cheaper than the checks. WebSearch was exhausted (200 of 200) early on
2026-09-14, so every reader worked fetch-only by address; the absence notes say so honestly.

## 8. The tooling, and its pitfalls

`measure/apply_notes.py <page> <notes.json> [--dry-run]` places footnotes from a JSON list of notes
(`line`, `sentence` fragment on one raw line, `form` citation|absence|grounds, `key`, `url`, `quote` or
`language`+`translation`+`original`, `gloss`, `extra`, `registry`, `fn` to replace an existing note,
`searched` WITHOUT the "searched YYYY-MM-DD:" prefix, `reasons`). It reports NOT-PLACED, RELOCATED,
NO-ROSTER and NO-SUCH-NOTE; check for those and for a Traceback before applying. Known behaviors:

- A fragment shorter than three words is tried only at the last sizes; Japanese fragments often fail to
  place - use the English clause or hand-place the `<li>` with the next free number.
- NO-ROSTER in a page whose sections are `<h3>`: create a roster before the next heading, or append the
  keys to the parent `<h2>`'s roster.
- The registry entry's link must equal the note's href, and ja/zh Wikipedia keys whose registry gives a
  kanji URL need the unencoded form in the note; a URL with a closing parenthesis (`町屋_(商家)`) must be
  quoted whole.
- A key without the two write-ups cannot be cited (`kuramai` was replaced by `kuramai-jawiki` for that).
- Each 「CJK」 in a gloss needs its own `(translated from the X by this project; original: 「…」)`; write
  `&` as `&amp;`.
- `handoff/_lib.py` carries the session's `Page` helper: `wsub` matches across tags and line wraps and
  keeps any footnote marks inside the span; `.C()`/`.A()` build citation and absence notes; `regurl(key)`
  reads the registry's URL; `key_for_url(url)` finds an existing key.
- The house-style hook rewrites Bash payloads: write dashes as `chr(0x2013)` in Python and commit
  messages through `git commit -F - <<'MSG'`.
