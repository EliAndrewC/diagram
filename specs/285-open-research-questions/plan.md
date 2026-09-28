# Plan - feature 285, the open research questions, derived from the record

Spec: [`spec.md`](spec.md). Request: [`request.md`](request.md). Measurement: [`research.md`](research.md) R1.

## Decisions

- **D1 - read the fragments, and only the fragments** (FR-001, FR-002). The record is written per entry (feature 258): a
  question is `research/<page>/NNN-<id>.html` (or `research/cities/<page>/...`), its notes the `.notes.html` beside it.
  The assembled pages and the citations pages repeat those fragments, so reading them would count each item twice.
  The page's name is the fragment's directory, the question's heading and anchor are the fragment's `<h2 id="...">`.
- **D2 - what an item is** (FR-002, FR-005). HTML comments are stripped first (a session note is not a claim).
  - *guess*: each occurrence of the capitalized label `GUESS` (or its plural `GUESSES`, research.md R3) in the question's visible text; the item's text is the
    sentence carrying it, tags stripped (a sentence ends at `. `, `? ` or `! ` or the paragraph's end). Two labels in
    one sentence are one item. Lower-case "guess" is not a label (research/README.md's four labels are written in
    capitals).
  - *absence*: each `<li data-note="...">` in the notes file whose visible text contains `no publicly readable
    source`; the item's text is the note (its search record), and, beside it, the sentence in the question that
    carries that note's `<sup data-note="...">` - the claim the search was for, so the reader sees what is unsourced,
    not only where the search went. A note carrying `settled YYYY-MM-DD` is kind *absence-settled*.
  - a GROUNDS note ("no source is owed") and a CONVENTION or DEVIATION label are not items.
- **D3 - the map features a question feeds** (FR-003). Three routes, each read from what the repository records:
  (a) every class in `interactive/classes` `CLASSES`, its `Entry:` resolved with `interactive/sources.py`
  `research_questions` - the one resolver the modal's "See references" and `scripts/check-entry-headings.py` use -
  whose URLs end `<page file>#<anchor>`, inverted to anchor -> class keys; (b) a question a class names that links
  (`href="...#<anchor>"`) to this one gives that class, "through <the linking question>" - one hop only, since a chain
  of links soon reaches everything; (c) a tracked engine `.py` file whose text contains the question's anchor or its
  heading's question (less its dated bookkeeping, `question_text`, and up to its first `?` where it has one - a comment quotes the question, not the answer after it) with no length floor (research.md R5: every short heading's engine matches are real citations) gives that file and line. R2 counted this route by a heading's first `40` characters; the tool's own count is re-measured at the end. A question none reaches says
  "no map feature found depending on it".
- **D4 - the target** (FR-001, FR-004). `make open-questions` in the skill's Makefile, running
  `scripts/_open_questions.py --root <repo>`. It prints the counts first (per page: questions, guesses, absences,
  settled; the outside-the-record lines per area; the totals), then per page, per question in file order: the
  heading, the fragment's path, the map features, and each item; then the outside-the-record guesses by file. Text
  only, to the terminal; nothing is written into the repository. No filters (spec-fidelity round 1: unrequested).
- **D7 - guesses outside the record** (FR-007). `git ls-files` under the skill, less `research/`, `tests/`, the
  tooling's logs (`dev/bypass-log/`, `dev/run-log/`, `dev/perf-log/`) and binary files; every tracked text file is
  read, the hand-drawn `pool/**/*.svg` plans included (spec-fidelity round 2). Each line carrying the whole word
  `GUESS` is an item with file, line number and the stripped line.
- **D5 - tests** (FR-006, SC-001, SC-002). `tests/tooling/test_open_questions.py`, loading the script as
  `test_record_prepass_and_size_table.py` loads its siblings: a fixture record in `tmp_path` (a guess in text, one in a
  comment, a lower-case guess, an absence note with its claim, a settled one, a grounds note, a convention label, two
  labels in one sentence), a class naming a question, a question linked from a class's, an engine file quoting a heading, a tracked file outside the record with a GUESS, the counts; the item gone after the fixture's guess
  is rewritten; and one test on the real record: it finds the homesteads 500 rack-length guess with the `threshing yard` class (through 505) and the `compound.py`
  postern guess, and its guess count equals a plain count of visible `GUESS` sentences. The tooling tree runs at the gate (tests/CLAUDE.md).
- **D6 - speed** (SC-003). One pass over the question fragments and their notes (`573` and `544` files, research.md R1), the tracked text files, and one import of the class registry; a whole-text search before a file's line walk in the code route - `2.0 s`, research.md R4.

## Constitution check

- XII: a tooling feature; it states nothing on a map. It READS the record's labels, so an unlabeled guess stays the one
  failure it cannot see - the labels rule is what makes the list complete.
- XIII: the gate before the push; the tooling tree is new code only.
- XVI: the target lists what the record labels; no item is filtered out beyond what the spec names.
- Indexing: no overlap check.
