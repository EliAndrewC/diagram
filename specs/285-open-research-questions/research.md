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
