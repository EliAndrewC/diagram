<!-- page-load: kind=assertions -->
# Brief - feature 292, the closing pass, part {id}: {title}

You are a FRESH session for one part of feature 292. This brief is the whole of what you need; do not read the
feature's spec or plan. Work in this clone (`{clone}`); the research record's `CLAUDE.md` applies to you (it auto-loads
when you read a research file).

**What the feature is for.** The research record has just been reorganized into one section per TOPIC and rewritten
under the style guide `research/STYLE.md` (a plain-English title, a short opening, lead-line bullets, how our maps draw
each thing in a separate RENDERING section under `research/questions/`). The sweep's check sessions left a few items for
a closing pass; an `escalation-check` agent and the GM decided each one (2026-10-01). Your items are below - each says
what to do. They are edits to sections already in the style: keep the style (STYLE.md), never lose a citation or a
finding, keep every GUESS labeled where its claim stands, and say a decision is the project's choice - a ruling of the
GM's goes in an HTML comment beside the sentence, never visible.

## Your items

{items}

## The procedure

1. **Claim:** `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram reorg ({clonename}) | 292 | closing pass {id} in progress | {date}"` (in `.claude/skills/diagram`).
2. **Find and read, in one message,** the sections and modal classes each item names: a section is a fragment under
   `research/<page>/` or `research/questions/<page>/` (find it with a glob or grep on its title or id - never edit an
   assembled page); a modal is a class docstring under `l7r/diagram/interactive/classes/` or `.../compound_kinds/`, and
   its `Entry:` line names the sections it is written from; `tests/fixtures/classes_before_189.json` carries the same
   `entry` string for a class under `classes/`, changed with it.
3. **Do each item.** A research item (marked RESEARCH) is a research question under the record's rules: search
   before deciding, read what you cite (`make source-pages OUT=<dir> URL=<u>` saves a page to grep; a PDF over the
   fetch tool's 10 MB is downloaded with `curl -sL -o <file> <url>` and read with `pdftotext <file> -`), quote what you
   cite with its footnote, record every page read with `make source-outcome`, take a new registry key from
   `make reserve KIND=registry KEY=<k> URL=<u>`, and run `source-applicability` on a new source before its numbers reach
   a rule. A source only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format.
4. **Build and test**, in `.claude/skills/diagram`: `make glossary` if a term changed, `make record && make citations`,
   `make style-prepass PAGE=<page> SECTION=<id>` on every section you changed (its FAIL lists empty),
   `make test-file FILE=tests/interactive`, `python3 scripts/check-question-size.py` from the clone root.
5. **Check what you changed**, dispatching each check in the FOREGROUND, two Agent calls per message, never with
   `run_in_background` (you are a headless session: a background agent's result never reaches you, and ending a turn
   to wait hangs the session for good): `make check-bundle PAGE=<page> SECTION=<id> NOTES=<the keys you added or
   changed> FOR=quote-check` for `quote-check` on notes you added or changed; `... KIND=<class> FOR=entry-drift` for
   `entry-drift` on every modal whose section or docstring you changed. Apply what they find (`make apply-edits
   FROM=<the report saved to a file>` for a quote-check report), rebuild and test once.
6. **Commit** only the files you changed (`git -C {clone}` with paths), message beginning `292 closing {id}:`; do not
   push. Report with `make append FILE={clone}/specs/292-research-presentation-style/sweep/closing-checks.md LINE="- {id} <item>: <what was done; what the checks said; anything left open>"`, one line per item, and close the claim with `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram reorg ({clonename}) | 292 | closing pass {id} committed in clone | {date}"`. Your last message is one paragraph.
