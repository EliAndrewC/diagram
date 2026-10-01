#!/usr/bin/env python3
"""Briefs for feature 269's research sessions, on feature 267's pattern (itself 250's; `make page-session`).

    python3 specs/269-research-backfill/briefs/gen.py write H1     -> writes h1-write.md, prints its path
    python3 specs/269-research-backfill/briefs/gen.py checks H1    -> reads h1-handoff.md, writes one check brief per
                                                                      two questions, prints each path

A write session researches ONE group of `inventory.md` and writes its questions; the check sessions (two questions
each, the registry keys in the last) run the record checks on bundles and apply them. The state between them is the
handoff, never a context.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FEATURE = HERE.parent
CLONE = FEATURE.parents[1]
SLUG = FEATURE.name
RESERVE = "/diagram/.clones/.tools/reserve-prefix.py"

#: group -> (title, where its questions go). The ranges avoid 267's (0091, 0093, 0094, 0102, 0103, 0104, 0105, 0106, 0107, 0108, 0109, 0110, 0111, 0112, 0117, 0239, 0076,
#: 0240, fields 220-240) and 268's (0215, 0220, 0221, 0222, 0223).
GROUPS = {
    "F1": ("fields: paddy kinds", "0013, 0014, and the existing sections the items name"),
    "F2": ("fields: ways and seasons", "fields 290-330, and the existing sections the items name"),
    "F3": ("fields: thin sections", "the existing sections the items name; a new question only if one outgrows the cap, at fields 340-360"),
    "H1": ("homesteads: farmstead fixtures", "the existing 0042, 0043, 0044, 0045, 0046, 0219, and 0047 for a new question"),
    "H2": ("homesteads: siting", "homesteads 300-330, and the existing sections the items name"),
    "H3": ("homesteads: thin sections", "the existing sections the items name; homesteads 340-360 for a split"),
    "W1": ("water: kinds", "water 290-330, and the existing sections the items name"),
    "W2": ("water: thin sections", "the existing sections the items name; water 340-360 for a split"),
    "V1": ("vegetation: woods", "0077, and the existing sections the items name"),
    "V2": ("vegetation: groves and margins", "vegetation 260-290, and the existing sections the items name"),
    "A1": ("archetypes: dike-pond", "0025, 0026, and the existing sections the items name"),
    "A2": ("archetypes: thin sections", "the existing sections the items name; archetypes 250-270 for a split"),
    "R1": ("religion-and-death: burial", "0236, and the existing sections the items name"),
    "R2": ("religion-and-death: city temples", "religion-and-death 310-330, and the existing sections the items name"),
    "C1": ("cities/defenses", "0151, and the existing sections the items name"),
    "C2": ("cities/government", "cities/government 100-140, and the existing sections the items name"),
    "C3": ("cities/fabric", "cities/fabric 160-190, and the existing sections the items name"),
    "C4": ("cities/hinterland and sizing", "0172, cities/sizing 030-050, and the existing sections the items name"),
    "C4A": ("cities/hinterland", "0172, and the existing sections the items name"),
    "C4B": ("cities/sizing", "cities/sizing 030-050, and the existing sections the items name"),
    "X1A": ("towns (265's pages, part a)", "the existing sections the items name (265 has landed; they are free)"),
    "X1B": ("towns, buildings and capitals (part b)", "the existing sections the items name"),
    "X1C": ("river cities and ways (part c)", "the existing sections the items name"),
    "FX1": ("homesteads fixes", "the existing sections the items name"),
    "FX2": ("vegetation, fields and government fixes", "the existing sections the items name"),
    "FX3": ("corrections owed to other sections", "the existing sections the items name"),
    "FX4": ("registry and government pointers", "the existing sections and registry entries the items name"),
    "SP1": ("splits over the size cap, part 1", "the questions it split"),
    "SP2": ("splits over the size cap, part 2", "the questions it split"),
    "FIN": ("the re-checks owed after the last fixes", "none - checks only"),
    "S1": ("settlements: is every household drawn", "the existing settlements 030; settlements 090-110 for a split"),
    "X1": ("the thin sections on 265's pages", "the existing sections the items name (265 has landed; they are free)"),
}

HEAD = """# Brief - feature 269 (the research backfill), group {group}: {title}, session {what}

You are a FRESH session for one part of feature 269. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`{clone}`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 265: 0090, 070, 150, 170, 210;
0175, 0176; 0190, 012, 020, 030, 050, 060, 070, 080, 160; 0081; towns 040, 080,
090, 100, 130; cities/capitals 040, 150, 155, 330-336. Feature 267: 0091, 0093, 0094, 0102, 0103, 0104, 0105, 0106, 0107, 0108, 0109, 0110, 0111, 0112, 0117, 0239, 0076,
0240, fields 220-240. Feature 268: 0215, 0220, 0221, 0222, 0223. Where a finding OWES one of those
a correction, say exactly what in the handoff; the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`); a write session's eleventh registry key is refused - then follow its message (write the
unreached items to `$L7R_CONTINUE` as a brief of this same shape, commit, stop).
**Coordination files are read by line, never whole** (feature 274): `make lines FILE=<f> KEY=<regex>` and
`make append FILE=<f> LINE="<text>"`. **Claims first (FR-011):** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md
KEY="<each page your items name>"`; skip any item another session has claimed since, naming it in the handoff; then
`make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram supplemental | 269 | group {group} in progress | <date>"`.
Read only your own lines of a handoff (`make lines FILE=<handoff> KEY="SECTION=<yours>|KEY=<yours>"`), and add to a
checks report with `make append`.
"""

WRITE = HEAD + """
## Your items (from `specs/{slug}/inventory.md`, group {group})

Each is a research QUESTION the record owes: never researched, labeled a guess, or thinly sourced. The kinds named are
the map features whose write-ups will be rewritten from what you find (by the orchestrating session, NOT by you).

{items}

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Find and save the pages.** Search (Japanese sources first for Edo villages and castle towns - jawiki, kotobank,
   a prefecture's or city's page, J-STAGE open papers, a museum's page; Chinese for Chinese practice). Save every
   candidate with `make source-pages OUT=/tmp/l7r-check/269-{low}-pages URLS="<u1> <u2> ..."` (one directory for the
   group; a second call adds to it) and grep them yourself - a page over 20,000 characters is saved in PARTS, so a
   grep hit leads to one bounded read. A source already in the registry reaches `source-reader` as
   `make check-bundle KEY=<key> WHOLE=1` (the plain `KEY=` bundle is an excerpt for `source-applicability` only).
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited; the map rolls among them per settlement), SILENT (nothing readable says it -
   an ABSENCE note with what was searched and when; the claim stays a labeled guess), or CONTRADICTION-RESOLVED (an
   existing section was wrong - say which and what corrects it). A search that finds nothing is an outcome, not a
   failure: record it and move on. A degree along a continuum is calibrated liberty; distinct forms are a knob.
5. **Write** on {pages}. A new question is a fragment `research/<page>/NNN-<heading id>.html` at a free prefix in
   your range, opening with `<h2 id="...">` whose text is the question a reader would ask from the map; a
   `<p><strong>Sources:</strong> ...</p>` roster; the finding; and where it drives what a map draws, the decision in
   plain words. A THIN-SECTION item is answered in the section that makes the claim: every real-world assertion there
   ends cited, with an absence note, or labeled a guess. Footnotes: `<sup class="fn" data-note="<key>"></sup>` in the
   prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted, translated
   and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by the record's rules. A new key gets
   its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is (both write-ups). A source
   only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format. First
   `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` - never script an edit. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and
   `python3 scripts/check-question-size.py` from the clone root (a question and its notes stay under 20,000 bytes -
   split one along its topics).
6. **Hand off.** Write `specs/{slug}/briefs/{low}-handoff.md`: one line per new or changed question as
   `- SECTION=<page>/<NNN>` (e.g. `- SECTION=homesteads/250`), one per new registry key as `- KEY=<key>`, and one line
   per item: `B<nn> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and maps
   named: what the generator should draw differently, if anything>`. Then anything left open and why. Commit (a
   message beginning `269 {group}:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh
   contexts. Your last message is one paragraph saying what you wrote.
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
4. **Commit** with a message beginning `269 {group} check:`; do not push.
5. **Report.** Append to `specs/{slug}/briefs/{low}-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
"""


def inventory_items(group: str) -> str:
    text = (FEATURE / "inventory.md").read_text(encoding="utf-8")
    block = text.split(f"## {group} - ", 1)[1].split("\n## ", 1)[0]
    return "\n".join(line for line in block.splitlines()[1:] if line.strip())


def write(group: str) -> int:
    title, pages = GROUPS[group]
    out = HERE / f"{group.lower()}-write.md"
    out.write_text(WRITE.format(group=group, title=title, what="1: research and write", clone=CLONE, slug=SLUG, low=group.lower(), pages=pages, items=inventory_items(group), reserve=RESERVE), encoding="utf-8")
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
        out.write_text(CHECK.format(group=group, title=title, what=f"2{chr(96 + n)}: check and apply", clone=CLONE, slug=SLUG, low=low, sections=shown, keys=(", ".join(f"KEY={k}" for k in keys) or "none") if last else "none - the last group has them", reserve=RESERVE), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    verb, group = sys.argv[1], sys.argv[2].upper()
    raise SystemExit(write(group) if verb == "write" else checks(group))
