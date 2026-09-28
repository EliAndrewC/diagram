# Research - feature 285

## R1 - how many open items the record holds (measured 2026-09-28, main at 0d72276ea)

Method: every question fragment `research/**/NNN-*.html` (573) and its `.notes.html` (544 files); HTML comments
stripped before counting; a note is an `<li>` in the notes file.

| what | count |
|---|---|
| visible GUESS labels in the question fragments | `149`, in `98` questions |
| GUESS inside HTML comments (session notes, not listed) | `12` |
| absence notes ("no publicly readable source") | `580` |
| of them marked `settled DATE` | `0` |

## R3 - the labels the collector finds (observed 2026-09-28, method: the built collector's `guess_sentences` on every question fragment against a whole-word count over the same visible text)

The label is written `GUESS` and, `12` times in the record, `GUESSES` ("the shares are GUESSES"); both are labels. The
collector's `149` labels fall in `139` listed sentences - ten sentences carry two - and none is outside a listed
sentence. R1's `149` counted the substring, which includes the plural; the two methods agree.

## R2 - guesses outside the record, and how a question reaches a map feature (measured 2026-09-28)

`git grep -c -w GUESS` over the skill's tracked files outside `research/` and `tests/`:

| where | lines | files |
|---|---|---|
| engine Python (code, comments, class docstrings) `l7r/**/*.py` | `85` | `25` |
| pool notes `pool/**/*.notes.md` | `20` | `5` |
| skill docs (`l7r/**/CLAUDE.md`, `future-work/`, `buildings.md`, `dev/*.md`) | `8` | `5` |
| hand-drawn Mode A plans `pool/**/*.svg` (tracked sources; `hayakawa-magistracy.svg:860` and `ubame-magistracy.svg:354` mark guesses found nowhere else) | `4` | `2` |
| bypass logs `dev/bypass-log/*.json` (escape reasons the tooling records; all four repeat record items) | `4` | `4` |

At least one is marked only in code: `compound.py`'s kitchen postern, a `6 ft` passage labeled GUESS, whose only
record fragment (`buildings/120`) does not label its width (spec-fidelity round 1's sample).

How the 98 questions with a visible GUESS reach a map feature: a class's `Entry:` names `16`; a question a class
names links to `4` more; engine source quotes the heading's first 40 characters or the anchor for `47` (overlapping
the others); `45` are reached by none of the three. The rack length (homesteads 500) is reached through 505, which
the threshing yard class names and which links to 500 twice.

The motivating item, the rack length per household, is in `research/homesteads/500-...html` ("The length of rack
per household is a GUESS until the record finds a figure").

## R4 - the built target on the whole tree (observed 2026-09-28, method: `make open-questions` from the skill, timed with `date`, its report parsed)

| what | count |
|---|---|
| questions with an open item | `403` of `573` |
| guess items (sentences) / absence items / settled | `139` / `580` / `0` |
| GUESS lines outside the record | `123` (engine `92`, pool `25`, docs `6`) |
| open questions whose map features come through a class's `Entry:` | `52` |
| through a link from a question a class names, only | `19` |
| cited in engine code (the question up to its `?`, or its anchor) | `134` |
| reached by none of the three | `237` |
| wall time | `2.0 s` (`8.5 s` before the whole-text pre-check in `code_citations`) |

## R5 - do short headings match stray text in the engine? (observed 2026-09-28, method: every question heading under `25` characters, up to its `?`, searched in every tracked `l7r/**/*.py` and each hit read)

Five headings are under `25` characters. Two ("Setting canon", "Works cited") and "How a josui actually ran" appear in no engine file. "A castle has TWO gates" appears once (`settlement/castle_civic.py:186`, a comment citing capitals 240 by its heading, whose anchor the engine never names); "Drawing a clan border" four times and "No interrogation room" three, all in `Entry:` lines of the Mode A compound kinds. All eight hits are citations; none is stray text. So the code route takes a heading of any length, and on the current tree that reaches one more open question ("Drawing a clan border", through the compound kinds) than a `25`-character floor did.
