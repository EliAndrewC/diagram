#!/usr/bin/env python3
"""Briefs for feature 271's research sessions - feature 269's generator (itself 267's and 250's pattern), adapted:
the groups are read from `inventory.md`'s own headings, and prefixes are reserved with `make reserve` (on main).

    python3 specs/271-research-coverage-audit/briefs/gen.py write H1     -> writes h1-write.md, prints its path
    python3 specs/271-research-coverage-audit/briefs/gen.py checks H1    -> reads h1-handoff.md, writes one check brief per
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

def groups() -> dict[str, tuple[str, str]]:
    """group -> (title, where its questions go), from `inventory.md`'s `## <ID> - <page>: <theme> (new: <range>)`."""
    out = {}
    for m in re.finditer(r"^## ([A-Z]\d+) - ([^(\n]+?)\s*\(new: ([^)]*)\)", (FEATURE / "inventory.md").read_text(encoding="utf-8"), re.M):
        out[m.group(1)] = (m.group(2).strip(), f"{m.group(3).strip()}, and the existing sections the items name")
    return out


HEAD = """# Brief - feature 271 (the research coverage backfill), group {group}: {title}, session {what}

You are a FRESH session for one part of feature 271. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`{clone}`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** feature 267: buildings 240-640, vegetation 170-200,
religion-and-death 220-260, fields 220-240 (magistracy and compound buildings); feature 268: religion-and-death 080-126;
feature 270: the country/village shrine hall's size; feature 269: every section its inventory
(`/diagram/.clones/diagram-supplemental/specs/269-research-backfill/inventory.md`) names, and its new ranges (fields
250-360, homesteads 250-360, water 290-360, vegetation 210-290, archetypes 200-270, religion-and-death 270-330,
cities/defenses 100-140, cities/government 100-140, cities/fabric 160-190, cities/hinterland 060-090, cities/sizing
030-050, settlements 030 and 090-110). Where a finding OWES one of those a correction, say exactly what in the handoff;
the orchestrator sends it to the owner.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.
**Claims first (FR-002).** Before any research, read `/diagram/.clones/RESEARCH-CLAIMS.md`. Skip any item of yours
that another session has claimed since, and name it in the handoff. Then set 271's line there to say group {group} is
in progress; edit only that line.
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
   candidate with `make source-pages OUT=/tmp/l7r-check/271-{low}-pages URLS="<u1> <u2> ..."` (one directory for the
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
   per item: `<id> <OUTCOME> - <one sentence of what the record now says> - <what it means for the kinds and maps
   named: what the generator should draw differently, if anything>`. Then anything left open and why. Commit (a
   message beginning `271 {group}:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh
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
4. **Owed modals.** `python3 scripts/_entry_owed.py` (from the clone root) names each map or sheet modal whose `Entry:`
   points at a question you changed. For each pair on YOUR questions: `make check-bundle PAGE=<page> SECTION=<NNN>
   KIND=<Class> FOR=entry-drift` (a class name two modules share is qualified: `household.Well`), one `entry-drift`
   agent per bundle, apply with `make apply-edits`, and append one line per pair to
   `specs/250-close-the-record-checks/owed-verdicts.md`:
   `- <Class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. Then
   `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py
   tests/interactive/test_compound_kinds.py"`.
5. **Commit** with a message beginning `271 {group} check:`; do not push.
6. **Report.** Append to `specs/{slug}/briefs/{low}-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
"""


def inventory_items(group: str) -> str:
    text = (FEATURE / "inventory.md").read_text(encoding="utf-8")
    block = text.split(f"## {group} - ", 1)[1].split("\n## ", 1)[0]
    return "\n".join(line for line in block.splitlines()[1:] if line.strip())


def write(group: str) -> int:
    title, pages = groups()[group]
    out = HERE / f"{group.lower()}-write.md"
    out.write_text(WRITE.format(group=group, title=title, what="1: research and write", clone=CLONE, slug=SLUG, low=group.lower(), pages=pages, items=inventory_items(group)), encoding="utf-8")
    print(out)
    return 0


def checks(group: str) -> int:
    title, _pages = groups()[group]
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
