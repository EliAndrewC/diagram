#!/usr/bin/env python3
"""Briefs for feature 267's research sessions, on feature 250's pattern (`make page-session`).

    python3 specs/267-compound-research-owed/briefs/gen.py write G1     -> writes g1-write.md, prints its path
    python3 specs/267-compound-research-owed/briefs/gen.py checks G1    -> reads g1-handoff.md, writes one check
                                                                           brief per two questions, prints each path

A write session researches ONE group of `inventory.md` and writes its questions; the check sessions (two questions
each, the registry keys in the last) run the record checks on bundles and apply them. The state between them is the
handoff, never a context. `then:` in `make page-session BRIEF="... then:<this> checks G1"` queues the checks when the
write session ends.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FEATURE = HERE.parent
CLONE = FEATURE.parents[1]
SLUG = FEATURE.name

#: group -> (the record page(s) its questions go on, the free prefix range each page takes)
GROUPS = {
    "G1": ("the residence's rooms", "buildings 240-290"),
    "G1B": ("the residence's entry and outbuildings", "buildings 300-350"),
    "G2": ("service buildings", "buildings 360-420"),
    "G3": ("the office and the court", "buildings 430-470"),
    "G3B": ("the gate, the walls and two unreadable sources", "buildings 480-520"),
    "G4": ("the grounds", "buildings 530-580, or vegetation 170-200 for a planting question"),
    "G5": ("the shrine", "religion-and-death 220-260"),
    "G6": ("river, trade and roads", "cities/river-cities 050-080, urban-features 190-220, ways 060-090"),
    "G7": ("the map-story kinds", "buildings 590-640"),
    "G8": ("the in-field grave island", "fields 220-240, or the existing fields question 010 on in-field features"),
}

HEAD = """# Brief - feature 267 (the compound research owed), group {group}: {title}, session {what}

You are a FRESH session for one part of feature 267. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`{clone}`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections** - feature 265, in another session, is working them: buildings 010, 070, 150, 170, 210;
cities/river-cities 010, 020, 030, 040; urban-features 010, 020, 030, 050, 060, 070, 080, 160; ways 020; towns 040,
080, 090, 100, 130; cities/capitals 040. Write the finding in a question of your own; where it OWES one of those
sections a correction, say exactly what in the handoff (the orchestrator makes it once 265 is done with the page).
"""

WRITE = HEAD + """
## Your items (from `specs/{slug}/inventory.md`, group {group})

Each is a research QUESTION the record owes. The kinds named are the map features whose write-ups will be rewritten
from what you find (by the orchestrating session, NOT by you); O, H, U are the Ochiba, Hayakawa and Ubame sheets.

{items}

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Find and save the pages.** Search (Japanese sources first for Edo buildings - jawiki, kotobank, a prefecture's
   or city's page on a surviving jin'ya, bukeyashiki or honjin; Chinese for yamen). Save every candidate with
   `make source-pages OUT=/tmp/l7r-check/{low}-pages URLS="<u1> <u2> ..."` (one directory for the group; a second
   call adds to it) and grep them yourself - a page over 20,000 characters is saved in PARTS, so a grep hit leads to
   one bounded read. A source already in the registry reaches `source-reader` as `make check-bundle KEY=<key> WHOLE=1`
   (the whole page, in parts; the plain `KEY=` bundle is an excerpt for `source-applicability` only - 250 D19).
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited), SILENT (nothing readable says it - an ABSENCE note with what was
   searched and when), or CONTRADICTION-RESOLVED (an existing section was wrong). A CONTRADICTION-RESOLVED is not
   done until the wrong section is CORRECTED, cited, in this session - on any page, whatever its prefix - unless it is
   on the do-not-edit list above, in which case the handoff says exactly what the correction is. A search that finds
   nothing is an outcome, not a failure: record it and move on.
5. **Write.** Each item (or a few closely joined ones) is a question on {pages}: a new fragment
   `research/<page>/NNN-<heading id>.html` at a free prefix in your range, opening with `<h2 id="...">` whose text is
   the question a reader would ask from the map; a `<p><strong>Sources:</strong> ...</p>` roster; the finding; and
   where it drives what a plan draws, the decision in plain words. Footnotes: `<sup class="fn" data-note="<key>"></sup>`
   in the prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted,
   translated from Japanese or Chinese and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by
   the record's rules. A new key gets its registry entry in `research/sources/010-works-cited/NNNN-<key>.html`, shaped
   as `9340-bungotakada-tagoshi.html` is (both write-ups). First `Read` every file you will change ALL IN ONE MESSAGE,
   then `Edit`/`Write` - never script an edit. Then in `.claude/skills/diagram`: `make record && make citations &&
   make test-file FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py
   tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and `python3 scripts/check-question-size.py`
   from the clone root (a question and its notes stay under 20,000 bytes - split one along its topics).
6. **Hand off.** Write `specs/{slug}/briefs/{low}-handoff.md`: one line per new or changed question - a corrected
   existing section included, so the checks read it - as `- SECTION=<page>/<NNN>` (e.g. `- SECTION=buildings/240`), one per new registry key as `- KEY=<key>`, and one line
   per item: `R<nn> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and sheets
   named>`. Then anything left open and why. Commit (a message naming the group). Do NOT run the record checks, do NOT
   push - the check sessions do that in fresh contexts. Your last message is one paragraph saying what you wrote.
"""

CHECK = HEAD + """
Session 1 researched this group and committed; its handoff is `specs/{slug}/briefs/{low}-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** {sections}
**Your registry keys:** {keys}

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE=<page> SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format`, each agent naming its own MANIFEST.md and nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source
   `source-applicability` rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess), and the
   key is listed in your report. Then `make glossary` if a term was added, `make record && make citations` and the four
   record tests ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`). A
   PARTIAL left after it is labeled honestly in the note and left.
4. **Commit** naming your questions; do not push.
5. **Report.** Append to `specs/{slug}/briefs/{low}-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
"""


def inventory_items(group: str) -> str:
    text = (FEATURE / "inventory.md").read_text(encoding="utf-8")
    block = text.split(f"## {group} - ", 1)[1].split("\n## ", 1)[0]
    return "\n".join(line for line in block.splitlines()[1:] if line.startswith("- R"))


def write(group: str) -> int:
    title, pages = GROUPS[group]
    out = HERE / f"{group.lower()}-write.md"
    out.write_text(WRITE.format(group=group, title=title, what="1: research and write", clone=CLONE, slug=SLUG, low=group.lower(), pages=pages, items=inventory_items(group)), encoding="utf-8")
    print(out)
    return 0


def checks(group: str) -> int:
    title, _pages = GROUPS[group]
    low = group.lower()
    handoff = HERE / f"{low}-handoff.md"
    if not handoff.is_file():
        print(f"gen: no handoff at {handoff} - the write session did not finish", file=sys.stderr)
        return 2
    text = handoff.read_text(encoding="utf-8")
    sections = list(dict.fromkeys(re.findall(r"^[ \t]*[-*][ \t]+`?SECTION=([a-z/-]+/\d{3})", text, re.M)))
    keys = list(dict.fromkeys(re.findall(r"^[ \t]*[-*][ \t]+`?KEY=([a-z0-9][a-z0-9-]*)", text, re.M)))
    pairs = [sections[i : i + 2] for i in range(0, len(sections), 2)] or [[]]
    for n, pair in enumerate(pairs, 1):
        last = n == len(pairs)
        out = HERE / f"{low}-check-{chr(96 + n)}.md"
        shown = ", ".join(f"PAGE={s.rsplit('/', 1)[0]} SECTION={s.rsplit('/', 1)[1]}" for s in pair) or "none"
        out.write_text(CHECK.format(group=group, title=title, what=f"2{chr(96 + n)}: check and apply", clone=CLONE, slug=SLUG, low=low, sections=shown, keys=(", ".join(f"KEY={k}" for k in keys) or "none") if last else "none - the last group has them"), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    verb, group = sys.argv[1], sys.argv[2].upper()
    raise SystemExit(write(group) if verb == "write" else checks(group))
