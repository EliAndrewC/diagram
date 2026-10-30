# Trial: does a local semantic index find what the archive's text search misses?

**Form**: trial

**Created**: 2026-10-29

**Status**: Running - amendment 3 (the GM, 2026-10-30): the index KEPT, and a combined search built on it; its end-to-end
validation on the field-size question closes the feature.

**Affects**: tooling

**Approved**: the GM, 2026-10-29, "Either way, go ahead and file the feature"

**Approved**: the GM, 2026-10-30, "Perhaps we could use that as a reference and count time and tokens?  Dispatcvhing to subagents to ensure it's a good and fair comparison?"

**Approved**: the GM, 2026-10-30, "I also agree with keeping the index and building the combined command. And then we can go ahead and run that test as essentially an end-to-end validation of the new combined system. So yes, I approve, and please proceed."

**Input**: `request.md` (the GM's words, verbatim).

## The question

Would a semantic index over the research record (`research/questions/`) and the private source archive's texts find the passages
a research question needs - the same idea in other words, or in another language - that today's text search (`make archive-find`,
every term required) misses, cheaply enough to keep? The model is fixed: the larger multilingual one, BGE-M3, stronger at matching an English question to
a Japanese or Chinese passage (the GM 2026-10-29: "let's just go ahead and lock in the larger one"); no smaller model is
measured. Asked now because the field's size cap (feature 444 FR-018) needs a research pass, and the GM is interested in
the experiment's result for its own sake.

## What is built for it

- The record's pages and the archive's texts cut into passages of a few hundred words, each with its file and place.
- Each passage embedded by BGE-M3, run locally, keyed by a fingerprint of its text: an update embeds only the new or changed
  passages; a change of model rebuilds whole.
- The vectors in a plain file, searched by brute force (the corpus is tens of thousands of passages); a `make` target that takes a
  question and returns the nearest passages with their file and place, beside `make archive-find`, never in its place.
- The index is stored in the private research archive's repository (`EliAndrewC/diagram-research`, checked out at
  `.specify/source-archive/`), beside the texts it indexes, as binary shards: the vectors at reduced precision, each shard holding
  the passages of a group of source files and kept under GitHub's file-size limits, so an update commits only the shards whose
  passages changed; pushed with the archive, so it survives the container, and rebuildable from the texts if ever lost.
- Nothing leaves the machine: the model runs locally, and the archive's text is never sent to a service (the archive is private,
  CLAUDE.md, "Research").
- Its tooling held to the project's rules: 100% coverage, a test companion, a make target, house style.

## Resuming

The build is long (about 120,700 passages; the full build took 8 h 42 min, about 231 passages a minute) and is safe to interrupt:

- Each shard is written to the archive's working copy (`.specify/source-archive/semantic-index/bge-m3-int8/<shard>.npz`, on
  the host's disk) as soon as it is done; a rerun of `make semantic-index` skips every shard whose passages are unchanged, so an
  interruption loses only the shard in progress. The commit and push to the archive's repository come at the end of a build.
- The model is BGE-M3's 8-bit build (`Xenova/bge-m3`, `onnx/model_int8.onnx`), cached in `.specify/model-cache/`; the
  docstring of `scripts/record/semantic_index.py` says why not the full one.
- To resume: `make semantic-index` (it picks up where it stopped). Then run the comparison, `trial.py` beside this spec - its 17
  questions (ten English, seven answered by Japanese sources), each with the archive capture known to answer it - from outside the repository
  (the make-only hook refuses a bare interpreter inside it): `cd /tmp && python3 <clone>/specs/447-semantic-index/trial.py
  <out.json>` (`deep.py` and `warm.py` the same way; each finds the repository from its own place), and record it under "The
  evidence".

## The measurement

1. The cost: the time to build the index over the whole corpus on this machine, its size on disk, and the time an update and a
   search take.
2. The comparison: a handful of past research questions whose answers the record already holds (the passages that answered them
   known), each asked through the index and through today's text search; for each, which of the known passages each finds in its
   first results, and what it finds that the other does not.

## Amendment 1 - a real research question, by tokens and time (the GM, 2026-10-30, `request.md`)

The GM: token use counts above wall-clock time, and a question is asked in every language the corpus holds, whichever search is
used. The corpus (one-shot count 2026-10-30, by script of each archived text's first 20,000 characters): 3,629 texts - 2,346
Japanese, 608 Chinese, 673 English or other Latin-script, 2 Korean.

3. **The research question** of feature 444 FR-018 - how large a single paddy plot was, typically and at its largest, in a
   premodern farming village of China and of Japan - searched by two `research-pass` agents with the same brief, the same
   languages (English, Japanese, Chinese) and the same stopping rule, confined to the record and the archive (no web, so the one
   difference is the search): arm T with today's search (`make archive-find`, Grep, Read), arm S with the same plus
   `make semantic-find`. Measured: each arm's tokens and wall time (the agent's own usage), its searches by kind, and its findings;
   a third agent, blind to which arm is which, judges the two reports' findings against the archive.

**The rule for amendment 1**: none set by the trial - the GM decides, on the measurement: keep the index (the tooling, the index
and a way to ask in every corpus language), or remove it per the first rule.

## Amendment 2 - "have we already answered this?" (the GM, 2026-10-30, `request.md`)

4. Nineteen record pages drawn at random, a question for each in the GM's own words, asked of the index and of a text search of the
   record whose terms were chosen blind to the pages: the index's rank of the page against the text search's try and hit count
   (`research/t03-answered.md`). The GM decides on amendments 1 and 2 together.

## Amendment 3 - the index kept, and one combined search (the GM, 2026-10-30, `request.md`)

The decision amendments 1 and 2 left with the GM: **the index is kept**, and the two searches are combined, because each found
sources the other missed (`research/t02-judge.md`). The goal is to find everything relevant locally before the web - "optimizing
for finding things that are relevant rather than doing something which is cheaper because it misses actual matches"; the web's
cost is not measured ("an unalloyed good for us to find things locally before searching the web").

- **FR-A3-1, one command, both searches.** `make research-search` takes the question in each corpus language the session gives -
  the list is open: English, Japanese, Chinese, Korean (the corpus holds two Korean texts, amendment 1's count) - and term sets (each set every term
  required, as `make archive-find`), runs the meaning search for each question and the text search for each term set over the
  record and the archive, and merges the hits by SOURCE (an archive capture, or a record page): each source printed once, ranked,
  with its best passage and what found it (index, text, or both). This is the GM's "we don't need to reevaluate sources that
  we've already turned up as hits with the first approach".
- **FR-A3-2, paging, never hiding.** One call prints a bounded number of sources (a default and a knob), the record's pages and
  the archive's sources apart; the cap limits what one call PRINTS, never what the search finds: the output counts every source
  found and the ones not printed, and a call under a KEY prints the next batch - the sources already printed for that key are
  held in `<archive home>/search-seen/<key>.json`, kept a day and then forgotten, so a question's later wordings and its next
  pages show only sources not yet read.
- **FR-A3-3, the research pass uses it.** The `research-pass` contract's "archive first" step runs the combined command before
  any web search.
- **SC-A3, the end-to-end validation.** A `research-pass` agent answers feature 444's field-size question with the combined
  command (archive and record only, the same brief as arms S and T). Success is decided on the SOURCES it surfaces: those the
  blind judge rated SOME or HIGH from either arm - Shicang 1898 `83/831d8174fa8b`, the Shizuoka replanning 1872 `e5/e542a5322e62`,
  the Huizhou 1581 parcel `04/04c46c135344`, Shiroyone `f4/f457740405c1` (or its other copy `56/5649138bf1c5`), the Yayoi small plots `d1/d1f4b30193e3` - those both arms
  found - Iwamuro 1602 `75/7588a47ce738`, Kami-Baba 1684 `27/27341e70863d`, King `e8/e81890ad0ea3`, Taipingqiao 1897
  `29/29423acf58a9` - and those the judge found both arms missed that bear on the premodern question - Hattori `97/97f6d769ce72`,
  Ofuro `10/100916836bb9`, Konosu 1902 `c3/c36ae8c62a1c` (the judge's fourth, a modern 3-tan standard `71/71ad2d8933fa`, is left
  out: it is not premodern). Its tokens and wall time are measured and reported beside the arms' (51,261 and 59,011 tokens,
  `research/t02-arm-s.md`, `research/t02-arm-t.md`), not held to them. Its result is reported to the GM.

## The rule

(The first trial's rule; amendment 1 handed the decision to the GM, and amendment 3 records it: the index is kept.)

- The index is kept where it finds passages today's search missed on at least a fair share of the questions, at a cost that keeps
  an update to seconds and a search under a second. Otherwise the trial is set down, its evidence recorded, the tooling not kept.
- Either way the result is reported to the GM, who asked for the experiment's result.

## The evidence

`research/t01-evidence.md`: the build's cost (8 h 42 min, 275 MiB, 120,669 passages), an update's and a search's time, and the 17
questions through both searches - asked in English, deeper (the first 200), and the seven Japanese-answered ones in Japanese, with
today's search in Japanese beside them. The outputs are `research/trial-out.json` and `research/deep-out.json`, from `trial.py`,
`deep.py` and `warm.py` beside this spec.

## The time

As feature 437 reported it: `make feature-report F=447`.

## Review history

- 2026-10-30, round 1 (spec-fidelity, MODE 2, `make trial-review F=447`): CHANGES REQUIRED - the verdict "set down" is the
  branch of the rule the measurement took and keeping the index until the GM chooses is LEGITIMATE; three figures fixed (four,
  not five, ranked first or second; the size in MiB; the build's measured rate in "Resuming") and the one-shot timings labeled, in
  `b8c0be19c`.
- 2026-10-30, round 2 (spec-fidelity, MODE 3 on `b8c0be19c`): FAITHFUL - each fix re-derived from the JSON and the time output.
  Owed: the GM's choice, put as an offer through escalation-check: the tooling and the index removed per the rule (restorable from
  the archive's history, commit `d8881575`), unless he keeps them for their ranking.
- 2026-10-30, the GM, before any removal: "Before we delete the index, there's another thing which we should consider, which is
  token usage ... I want to think more about the ways in which it's better [or] worse before we make a final decision." Removal
  held; the output sizes of both searches recorded (`research/t01-evidence.md`, section 5).
- 2026-10-30, amendment 3 round 1 (spec-fidelity, routed to MODE 3): CHANGES REQUIRED - the cap pages and never hides, the key's
  memory serves paging with its store and a day's life, SC-A3 decided on sources with its files named and tokens reported, not
  held, the language list open; applied in `c73f9840d`.
- 2026-10-30, amendment 3 round 2 (spec-fidelity-verify): FAITHFUL - its four small notes (an FR id in a comment, Q_KO in the
  contract and the usage line, Shiroyone's second copy) applied.
