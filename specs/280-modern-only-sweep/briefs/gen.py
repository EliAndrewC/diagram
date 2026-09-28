#!/usr/bin/env python3
"""Briefs for feature 280's research sessions (the modern-only sweep), on feature 269's pattern (`make page-session`).

    python3 specs/280-modern-only-sweep/briefs/gen.py write F1    -> writes f1-write.md, prints its path
    python3 specs/280-modern-only-sweep/briefs/gen.py checks F1   -> reads f1-handoff.md, writes one check brief per
                                                                     two questions, prints each path
    python3 specs/280-modern-only-sweep/briefs/gen.py all         -> every group's write brief

A write session researches ONE group of `inventory.md` (at most four questions, feature 274's cap) and writes the
outcomes; the check sessions (two questions each, the registry keys in the last) run the record checks on bundles and
apply them. The state between them is the handoff, never a context. The groups, their titles and their prefix ranges
are read from `inventory.md`'s `## <G> - <title>` headings and the `Where:` line under each, so the inventory is the
one place a group is defined.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FEATURE = HERE.parent
CLONE = FEATURE.parents[1]
SLUG = FEATURE.name
SESSION = "diagram-supplemental-2"

HEAD = """# Brief - feature 280 (the modern-only sweep), group {group}: {title}, session {what}

You are a FRESH session for one part of feature 280. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`{clone}`); the project's CLAUDE.md files apply to you, the research record's
`CLAUDE.md` above all (it auto-loads when you read a research file).

**What the feature is for.** The GM, 2026-09-28: *"We should eliminate anything which is only modern"* and *"We should
avoid anything that appears only on modern lists."* Each item below is a form a map draws (or a figure it uses) that an
audit found MAY be attested only in the modern period. Your job is to find out, searching for a PREMODERN attestation
FIRST, and to record what you find. You do not change the engine or the maps: the eliminations are a later phase.

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**A held section is researched, never edited, and never skipped.** A section is HELD when the claims file names it
in progress for another feature (religion-and-death 124-129 are feature 279's while its line is open), or when
feature 269 rewrote it and has not landed - whatever 269's claim line says, "done, committed in clone" included: any
output from `git -C /diagram/.clones/diagram-supplemental log origin/main..HEAD --oneline -- .claude/skills/diagram/research/<page>/<NNN>-*`
means unlanded. For an item on a held section, do the research all the same, but do not edit the section: put the
outcome in the handoff as usual, with `OWED-TO <feature>` and the exact text the section owes (the finding and its
footnotes), so the orchestrator applies it once the hold clears. No item leaves your session without an outcome.
**Coordination files are read by line, never whole** (feature 274): `make lines FILE=<f> KEY=<regex>` and
`make append FILE=<f> LINE="<text>"`. **Claims first:** `make lines FILE=/diagram/.clones/RESEARCH-CLAIMS.md
KEY="<each page your items name>"` (a held section is handled as above, never skipped); then `make append FILE=/diagram/.clones/RESEARCH-CLAIMS.md LINE="Diagram supplemental ({session}) | 280 |
group {group} in progress (<the sections>) | <date>"`. Read only your own lines of a handoff (`make lines
FILE=<handoff> KEY="SECTION=<yours>|KEY=<yours>"`), and add to a checks report with `make append`.
**New registry entries and glossary terms take their prefix from `make reserve KIND=registry|glossary KEY=<k>`** (in
`.claude/skills/diagram`), never "the highest + 10" by eye; a write session's eleventh registry key is refused - then
follow its message (write the unreached items to `$L7R_CONTINUE` as a brief of this same shape, commit, stop).
"""

WRITE = HEAD + """
## Your items (from `specs/{slug}/inventory.md`, group {group})

Each names the section that makes the claim, the drawn form, why the audit thinks it modern-only, and the maps it
touches. The kinds and maps named will be changed from your outcome by the orchestrating session, NOT by you.

{items}

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Search for a PREMODERN attestation first.** For each item, search for the form before modernity: in Japan before
   the Meiji Restoration (1868), in China before the end of the Qing (1912). Look for Edo farm manuals (nosho, e.g.
   農業全書, 百姓伝記), period illustrations (名所図会, 農業図絵, 耕作図), village records (村明細帳), archaeology, a
   museum's or prefecture's page, J-STAGE open papers, kotobank and jawiki for Japan; 天工開物, 農政全書, gazetteers
   (地方志) and the Chinese Text Project for China; and modern historians who DATE the form. Search in Japanese or
   Chinese as well as English. Save every candidate page with `make source-pages OUT=/tmp/l7r-check/280-{low}-pages
   URLS="<u1> <u2> ..."` (one directory for the group; a second call adds to it) and grep them yourself - a page over
   20,000 characters is saved in PARTS. A source already in the registry reaches `source-reader` as
   `make check-bundle KEY=<key> WHOLE=1`. Keep a list of every search you ran (terms, language, where) - a MODERN-ONLY
   outcome must state it.
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read - exactly one of:
   - **PREMODERN-ATTESTED**: a readable source places the form in Japan before 1868 or in China before 1912, whatever
     the source's own date (a modern historian who dates it counts). Cite it.
   - **MODERN-ONLY**: every attestation found is modern practice, or a 20th-century record that gives no date. Record
     the search that found nothing earlier: the terms, languages and places searched, and the date. Where the only
     attestation is an undated modern record of custom ("in the old days", remembered practice), the outcome is
     MODERN-ONLY with the tag `undated-custom` (spec D1: an undated record could mean the Meiji era; the GM may re-sort
     that set).
   - **MIXED**: some forms (or some values of a figure) are attested premodern and some only modern. Name each form,
     cite the attested ones, give the search for the rest. For a degree (a size, density, count), give the premodern
     figure the map should be calibrated to, as the GM ruled for mulberry spacing.
   A search that finds nothing is an outcome, not a failure: record it and move on.
5. **Write** on {pages}. The finding is written in the section that makes the claim: the premodern attestation cited,
   or the modern-only finding with its search and date, and the decision in plain words ("the maps do not draw it").
   Write it as the finding a casual reader needs, never as what the section used to say. A new question, where one is
   needed, is a fragment `research/<page>/NNN-<heading id>.html` at a free prefix in your range, opening with
   `<h2 id="...">` whose text is the question a reader would ask from the map, and a
   `<p><strong>Sources:</strong> ...</p>` roster. Footnotes: `<sup class="fn" data-note="<key>"></sup>` in the prose,
   `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted, translated and
   marked as such, the original after), an ABSENCE note (what was searched, where, when), or a GROUNDS note. A new
   key gets its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is (both write-ups). A
   source only the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format.
   First `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` - never script an edit. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`, and
   `python3 scripts/check-question-size.py` from the clone root (a question and its notes stay under 20,000 bytes -
   split one along its topics).
6. **Hand off.** Write `specs/{slug}/briefs/{low}-handoff.md`: one line per new or changed question as
   `- SECTION=<page>/<NNN>` (e.g. `- SECTION=homesteads/250`), one per new registry key as `- KEY=<key>`, and one line
   per item: `M<nn> <OUTCOME>[ undated-custom] - <one sentence of what the record now says> - <what it means for the
   kinds and maps named: what the generator should stop drawing, or draw instead, if anything> - <searched: terms,
   languages, where, date> (for MODERN-ONLY and MIXED)`. Say also, per item, whether the GM ruled the form in (the
   record or the kind says so) and whether knowingly. Then anything left open and why. Commit (a message beginning
   `280 {group}:`). Do NOT run the record checks, do NOT push - the check sessions do that in fresh contexts. Your
   last message is one paragraph saying what you wrote.
"""

CHECK = """<!-- page-load: kind=check -->
""" + HEAD + """
Session 1 researched this group and committed; its handoff is `specs/{slug}/briefs/{low}-handoff.md`. You check and
apply ONE GROUP of the questions it wrote - read only your own lines of the handoff.

**Your questions:** {sections}
**Your registry keys:** {keys}

## The procedure (check, apply)

1. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE=<page> SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format`, each agent naming its own MANIFEST.md and nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`. An ABSENCE note that says what was searched is checked as
   one: its search is stated, dated and specific.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>` (in
   `.claude/skills/diagram`), `SKIP=<n,n>` for a block you disagree with. Then do BY HAND only what it lists as
   REFUSED, what you skipped, and the `EDIT: none` findings - all in ONE message of parallel `Edit` calls. A source
   `source-applicability` rules NOT-APPLICABLE: the assertions resting on it are relabeled (absence or guess), the key
   is listed in your report, and where that turns a PREMODERN-ATTESTED item into MODERN-ONLY, say so in the report.
   Then `make glossary` if a term was added, `make record && make citations` and the four record tests ONCE.
3. **Re-check ONCE, only what moved** (`make check-bundle ... NOTES=<key,key> FOR=quote-check`, one `quote-check`). A
   PARTIAL left after it is labeled honestly in the note and left.
4. **Commit** with a message beginning `280 {group} check:`; do not push.
5. **Report.** Append to `specs/{slug}/briefs/{low}-checks.md` (with `make append`) one line per question and key: its
   verdicts (quote-check, record-format, source-applicability), any outcome the checks changed, and anything left
   open. Your last message is one paragraph.
"""


def groups() -> dict[str, tuple[str, str, str]]:
    """group -> (title, where its questions go, its item lines), from `inventory.md`'s `## <G> - <title>` blocks."""
    text = (FEATURE / "inventory.md").read_text(encoding="utf-8")
    out = {}
    for m in re.finditer(r"^## ([A-Z]+\d+[A-Z]?) - (.+)$", text, re.M):
        body = text[m.end() :].split("\n## ", 1)[0]
        where = re.search(r"^Where: (.+)$", body, re.M)
        items = "\n".join(line for line in body.splitlines() if line.strip() and not line.startswith(("Where: ", "Holds: ")))
        out[m.group(1)] = (m.group(2).strip(), where.group(1).strip() if where else "the existing sections the items name", items)
    return out


def write(group: str) -> int:
    title, pages, items = groups()[group]
    out = HERE / f"{group.lower()}-write.md"
    out.write_text(WRITE.format(group=group, title=title, what="1: research and write", clone=CLONE, slug=SLUG, low=group.lower(), pages=pages, items=items, session=SESSION), encoding="utf-8")
    print(out)
    return 0


def checks(group: str) -> int:
    title, _pages, _items = groups()[group]
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
        out.write_text(CHECK.format(group=group, title=title, what=f"2{chr(96 + n)}: check and apply", clone=CLONE, slug=SLUG, low=low, sections=shown, keys=(", ".join(f"KEY={k}" for k in keys) or "none") if last else "none - the last group has them", session=SESSION), encoding="utf-8")
        print(out)
    return 0


if __name__ == "__main__":
    verb = sys.argv[1]
    if verb == "all":
        raise SystemExit(max((write(g) for g in groups()), default=0))
    group = sys.argv[2].upper()
    raise SystemExit(write(group) if verb == "write" else checks(group))
