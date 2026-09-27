#!/usr/bin/env python3
"""Briefs for feature 272's research sessions - feature 271's generator (itself 269's, 267's and 250's pattern),
adapted: the groups are this feature's (plan D2), each with the reader reports gathered before it (plan D3).

    python3 specs/272-temples-and-shrines-researched/briefs/gen.py write S     -> writes s-write.md, prints its path
    python3 specs/272-temples-and-shrines-researched/briefs/gen.py checks S    -> reads s-handoff.md, writes one check
                                                                                  brief per two questions, prints each

A write session researches ONE group and writes its questions; the check sessions (two questions each, the registry
keys in the last) run the record checks on bundles and apply them. The state between them is the handoff.
"""

from __future__ import annotations

import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
FEATURE = HERE.parent
CLONE = FEATURE.parents[1]
SLUG = FEATURE.name
READERS = FEATURE / "readers"

# group -> (title, where its questions go, reader reports, items)
GROUPS: dict[str, tuple[str, str, list[str], str]] = {
    "S": (
        "the country shrine's open questions (second search)",
        "the existing sections religion-and-death 090, 100, 110, 120, 122, 124, 126, 128 (edits only; no new question)",
        ["272-reader-S.md", "272-shrine-absences.md"],
        """- FR-001 **Every absence note and labeled guess in 090-128** (listed in `readers/272-shrine-absences.md`): a
  second search has run (`readers/272-reader-S.md`, by item label - GREP it by label, it is 100 KB; never read it
  whole). For each: ANSWERED -> cite it (through source-reader); HUMAN-FETCHABLE -> a TO-DOWNLOAD entry; STILL
  SILENT -> the absence note gains the second search (what, where, 2026-09-27) beside the first.
- D50 **A small kuri's size** (120): STILL SILENT after the second search - the note says so.
- D51 **A village shrine-temple's bell tower** (120): STILL SILENT after the second search - the note says so.
- A133 A135 D49 D52-D56 (100-128, COVERED by 268): confirm only; change nothing that the second search leaves as it is.
- FR-007: for EVERY finding, say in the handoff whether it contradicts the Hoshigaoka country-shrine sheet or its
  village map (the sheet: `pool/country-shrines/hoshigaoka-shrine/`; the precinct is an open grove, torii 12 ft apart,
  a 66 by 32 ft one-roof hall-and-dwelling, a basin and a sacred tree by the approach). Do NOT edit the sheet or the
  map; the orchestrating session applies what contradicts them.""",
    ),
    "R2": (
        "town monasteries and town and city shrines",
        "religion-and-death 450-490 (new), and edits to 040 and 210",
        ["272-reader-R2a.md", "272-reader-R2b.md"],
        """- B96 D66 **Town monastery count**: how many monasteries does a county seat keep (canon: one per patron Fortune -
  `make canon`), against real county towns, and who lives in one? (religion-and-death/210, 020). M. P1.
- B97 B98 D65 **Town monastery size and layout**: how big is a town monastery's precinct and hall, walled or fenced,
  what stands in it (gate, main hall, bell, priests' quarters, graveyard), and where it stands in the town (the temple
  quarter at the edge)? (religion-and-death/010, 040, 170 - 170 is 269's: cite it, do not edit). M. P1.
- B101 C152 **Town and city shrine**: how big is a county seat's own shrine (its chinju) and precinct against a
  village's (the 1897 rank floors: 300/500/600 tsubo), and does a city keep a principal shrine (the castle town's
  sōchinju; the Chinese city-god temple, chenghuang miao), how big and where? (100-126 are the village's - cite
  them). M. P1.
- C147 D70 **Clergy housing**: who lives inside a city temple's walls and who outside? (religion-and-death/040, 1
  note). S. P1.""",
    ),
    "R4": (
        "the state cult and temple plans",
        "religion-and-death 550-570 (new) - NOT 580-590, which are group T's",
        ["272-reader-R4.md"],
        """- B91 D78 **State cult buildings**: does a county seat or a city carry the Chinese state cult's buildings (the
  Confucian temple, wen miao; the City God temple; the altars of soil and grain), their setting analogue, where and
  how big? (urban-features/070 is not ours: say in the handoff what it owes; religion-and-death/020). M. P3.
- C144 **Provincial academies**: did a provincial city keep a Confucian academy or school-temple (shuyuan, wenmiao,
  a domain school), and how big? M. P4.
- D75 **Temple as a building plan**: what does a temple precinct hold - main hall, gate (sanmon), bell tower,
  lecture hall, kuri, cloister, cemetery - at what sizes, Japan against China? L. P4.
- D76 D77 **Temple bell tower and pagoda**: does a city temple keep a bell tower (apart from the civic bell-and-drum
  tower) and a pagoda, and how tall and wide? M. P4.""",
    ),
    "B37": (
        "city temples (269's B37, handed over)",
        "religion-and-death 310-330 (new), and edits to 010, 050 and 070",
        ["272-reader-B37.md"],
        """- B37 **City temples**: monk counts "on no page read" (010); the temple-gate shop ratio and meibutsu (050);
  graveyard sharing (070 - the graveyard itself is 269's burial group R1: cite it, never write it). The bone-mound
  size (204) WAITS for 269's R1 and is not yours.""",
    ),
    "R3": (
        "the village temple and wayside shrines",
        "religion-and-death 500-540 (new), and edits to 210",
        ["272-reader-R3.md"],
        """- A138 D64 **Village temple**: did a village of 40-100 households keep a parish temple (danna-dera) of its own,
  beside or instead of its shrine, and how many villages shared one? Research FOR the GM's ruling - the canon gives a
  village a country monk (`make canon`). (religion-and-death/210). M. P2.
- A139 **Village temple precinct**: how big, what stands in it (hall, priest's quarters, bell), and where it sits
  against the houses and the graves. M. P2.
- A140 D61 B103 **Wayside shrines**: jizō, dōsojin, a stone kami, a street-side Inari - how many does a village or a
  town's streets carry, how big, at which thresholds (entrance, crossroads, bridge foot)? (religion-and-death/210, 1
  note). M. P2.
- A144 **Village cremation and ossuary**: ONLY what 269's burial group R1 (religion-and-death 160-206, new 270-300,
  in `/diagram/.clones/diagram-supplemental`) leaves open - read R1's sections first and cite them. M. P2.""",
    ),
    "T": (
        "the city temple complex, the temple neighborhood, and the temple sections' open notes",
        "religion-and-death 580-590 (new), and edits to 010, 020, 030, 040, 050, 060, 070, 210",
        ["272-reader-T.md", "272-temple-absences.md"],
        """- FR-006 **The city temple complex**: how big is a major city temple's precinct and main hall, and how is it
  laid out building by building (gate, main hall, lecture hall, bell tower, pagoda, abbot's quarters, sub-temples,
  cemetery)? Japan and China. (new, 580).
- FR-006 **The temple neighborhood**: the SMALL temple and the SMALL shrine of a temple quarter (teramachi) - the
  plot's frontage and depth, what stands on it, how many to a block, how they pack along the street. (new, 590).
- FR-001 **Every absence note and labeled guess in 010-070 and 210** (listed in `readers/272-temple-absences.md`;
  their second search is part C of `readers/272-reader-T.md`): cite what was found, a TO-DOWNLOAD entry for what a
  human can fetch, the second search added to what stays silent. 130-206 are 269's - never edit them.""",
    ),
}

HEAD = """# Brief - feature 272 (temples and shrines researched), group {group}: {title}, session {what}

You are a FRESH session for one part of feature 272. This brief is the whole of what you need; do not read the
feature's spec or plan to orient - everything you read stays in your context and is paid for again on every later
turn. Work in this clone (`{clone}`); the project's CLAUDE.md files apply to you, the research record's `CLAUDE.md`
above all (it auto-loads when you read a research file).

**Read narrowly.** For a few notes of a question use `make notes PAGE=<page> SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`). Grep with `-o` and a short context. Send the lookups you know you need in one message.
**Do not edit these sections - other sessions own them:** religion-and-death 130-206 and new 270-300 (feature 269's
burial group R1, in `/diagram/.clones/diagram-supplemental`); religion-and-death 220-260 (feature 267); every page
other than religion-and-death. Where a finding OWES one of those a correction, say exactly what in the handoff; the
orchestrator sends it to the owner. Other groups of THIS feature run beside you in sibling clones: stay inside your
own sections and range.
**New registry entries and glossary terms take their prefix under the host-wide lock**, never "the highest + 10" by
eye: `make reserve KIND=registry KEY=<key>` (or `KIND=glossary KEY="<term>"`, in `.claude/skills/diagram`) prints the
stub's path; fill it in. It refuses a key another clone already holds - then use or cite that one.
"""

WRITE = HEAD + """
## Your items (group {group})

{items}

## What was already read

A reader searched for these items on 2026-09-27; its report is {readers} in `specs/{slug}/readers/`. Its quotes are
leads, NOT citations: nothing is written from them until `source-reader` returns it READ (step 3). Its list of
blocked sources is where your TO-DOWNLOAD entries start - first try each once more with `curl` (a PDF through
`pdftotext`; a Shift_JIS page decoded as such), because the reader's fetch tool could not open a PDF.

## The procedure (session 1: research and write)

1. **Canon first, once.** An item that is a question of the SETTING is answered from the GM's canon with ONE call
   naming every term: `make canon TERMS="<a>|<b>|<c>"` (in `.claude/skills/diagram`). Most items here are history.
2. **Save the pages.** Save every source you will cite with `make source-pages OUT=/tmp/l7r-check/272-{low}-pages
   URLS="<u1> <u2> ..."` (one directory for the group; a second call adds to it) and grep them yourself - a page over
   20,000 characters is saved in PARTS. Search further where the reader left an item thin. A source already in the
   registry reaches `source-reader` as `make check-bundle KEY=<key> WHOLE=1`.
3. **Read through `source-reader`.** Dispatch ONE `source-reader` over every claim at once, handing it the saved
   directory and each claim verbatim in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh` refuses
   that). Write only from what it returns READ with a quote.
4. **Decide each item's outcome** from what was read: ACCURATE (the record now says it, cited), KNOB (two or more
   forms attested - name each, each cited), SILENT (nothing readable says it - an ABSENCE note with what was searched
   and when, both searches where there were two; the claim stays a labeled guess), or CONTRADICTION-RESOLVED (an
   existing section was wrong - say which and what corrects it). The GM's canon governs the setting: report the
   history against it, never override it.
5. **Write** on {pages}. A new question is a fragment `research/religion-and-death/NNN-<heading id>.html` at a free
   prefix in your range, opening with `<h2 id="...">` whose text is the question a reader would ask from the map; a
   `<p><strong>Sources:</strong> ...</p>` roster; the finding; and where it drives what a map draws, the decision in
   plain words, labeled (accurate, deviation, convention, guess). Footnotes: `<sup class="fn" data-note="<key>"></sup>`
   in the prose, `<li data-note="<key>">...</li>` in the `.notes.html` beside it - every note a CITATION (quoted,
   translated and marked as such, the original after), an ABSENCE note, or a GROUNDS note, by the record's rules. A
   new key gets its registry entry (reserved as above), shaped as `9340-bungotakada-tagoshi.html` is. A source only
   the GM can fetch goes at the END of `/host-l7r-repo/academic-sources/TO-DOWNLOAD.md` in its format (a heading, the
   believed link, a Google-search link, what rests on it, what blocked the fetch) - read its last entry first for the
   shape; never run git there. First `Read` every file you will change ALL IN ONE MESSAGE, then `Edit`/`Write` -
   never script an edit. Then in `.claude/skills/diagram`: `make record && make citations && make test-file
   FILE="tests/interactive/test_footnotes.py tests/interactive/test_citations.py tests/interactive/test_sources.py
   tests/interactive/test_record_format.py"`, and `python3 scripts/check-question-size.py` from the clone root (a
   question and its notes stay under 20,000 bytes - split one along its topics).
6. **Hand off.** Write `specs/{slug}/briefs/{low}-handoff.md`: one line per new or changed question as
   `- SECTION=religion-and-death/<NNN>`, one per new registry key as `- KEY=<key>`, and one line per item:
   `<id> <OUTCOME> - <one sentence of what the record now says> - <what it means for the maps: what a generator or a
   sheet should draw differently, if anything>`. Then one line per TO-DOWNLOAD entry you appended, and anything left
   open and why. Commit (a message beginning `272 {group}:`). Do NOT run the record checks, do NOT push - the check
   sessions do that in fresh contexts. Your last message is one paragraph saying what you wrote.
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
   `specs/{slug}/briefs/owed-verdicts.md`:
   `- <Class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. Then
   `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py
   tests/interactive/test_compound_kinds.py"`.
5. **Commit** with a message beginning `272 {group} check:`; do not push.
6. **Report.** Append to `specs/{slug}/briefs/{low}-checks.md` one line per question and key: its verdicts (quote-check,
   record-format, source-applicability) and anything left open. Your last message is one paragraph.
"""


def write(group: str) -> int:
    title, pages, readers, items = GROUPS[group]
    missing = [r for r in readers if not (READERS / r).is_file()]
    if missing:
        print(f"gen: reader reports not yet in readers/: {', '.join(missing)}", file=sys.stderr)
        return 2
    out = HERE / f"{group.lower()}-write.md"
    shown = " and ".join(f"`{r}`" for r in readers)
    out.write_text(WRITE.format(group=group, title=title, what="1: research and write", clone=CLONE, slug=SLUG, low=group.lower(), pages=pages, readers=shown, items=items), encoding="utf-8")
    print(out)
    return 0


def checks(group: str) -> int:
    title = GROUPS[group][0]
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
