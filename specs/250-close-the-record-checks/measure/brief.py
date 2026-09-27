#!/usr/bin/env python3
"""The brief a fresh page session starts from (feature 250 D7): what ONE page owes, and how to do it.

    brief.py <page> <task>          writes briefs/<page>-1.md (locate, read, write) and briefs/<page>-checks.sh
    brief.py checks <page> <task>   run by the runner when session 1 ends: one check brief per group of two of the
                                    questions its handoff names, printed a path a line - each a FRESH session
                                    (feature 250: R2's recommendation 2 split write from check; R3's split the
                                    checks, after one check session grew to 218,000 over five questions)

The items are DERIVED - FR-002's from `assertions.py`, FR-006's from 242's `worklist.py` - never typed.
The procedure is the plan's (D2, D5, D6, D8) written out so the session does not have to read the spec,
the plan and three CLAUDE.md sections to learn it: every page a session reads to orient is a page it
carries for the rest of its turns.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
FEATURE = HERE.parent
CLONE = FEATURE.parents[1]
SKILL = CLONE / ".claude/skills/diagram"
WORKLIST = CLONE / "specs/242-cite-the-unfootnoted-assertions/measure/worklist.py"


def fr002_items(page: str) -> list[tuple[str, str, str]]:
    """(the question the report names, the item's text, the report) for each FR-002 item on the page."""
    sys.path.insert(0, str(HERE))
    import assertions  # noqa: PLC0415

    out = []
    for name in assertions.NAMES:
        lines = (assertions.REPORTS / name).read_text(encoding="utf-8").splitlines()
        for item in assertions.items_of(lines):
            if (item["page"] or assertions._ONE_PAGE.get(name, "")) == page.split("/")[-1]:
                out.append((section_of(item["section"]), item["text"], name))
    return out


def fr002(page: str) -> list[str]:
    return [f"- **{sec}** - {text}  _(from `{name}`)_" for sec, text, name in fr002_items(page)]


def _norm(text: str) -> str:
    return re.sub(r"[^a-z0-9 ]+", "", re.sub(r"<[^>]+>|&[a-z]+;", " ", text.lower())).split("  ")[0].strip()


def questions(page: str) -> dict[str, tuple[str, int]]:
    """section number -> (its heading's words, its size in bytes with its notes)."""
    out = {}
    for q in sorted((SKILL / "research" / page).glob("[0-9][0-9][0-9]-*.html")):
        if q.name.endswith(".notes.html"):
            continue
        n = q.with_name(q.name[:-5] + ".notes.html")
        title = re.search(r"<h2[^>]*>(.*?)</h2>", q.read_text(encoding="utf-8"), re.S)
        out[q.name[:3]] = (" ".join(_norm(title.group(1) if title else "").split()), q.stat().st_size + (n.stat().st_size if n.exists() else 0))
    return out


def _text_of(page: str, section: str) -> str:
    """A question's whole text, tags out, lower-cased, one space between words - what an item's words are searched in."""
    q = next(p for p in (SKILL / "research" / page).glob(f"{section}-*.html") if not p.name.endswith(".notes.html"))
    return _words(q.read_text(encoding="utf-8"))


def _words(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]+", " ", re.sub(r"<[^>]+>|&[a-z]+;", " ", text.lower())).split())


def item_questions(page: str) -> list[str]:
    """The sections the page's FR-002 items fall in, read off the heading each report names."""
    qs = questions(page)
    found = []
    for sec, _text, _name in fr002_items(page):
        want = " ".join(_norm(sec).split())[:40]
        hit = next((n for n, (title, _size) in qs.items() if want and (title.startswith(want) or want.startswith(title[:40]))), None)
        if hit is None and want:  # some reports label an item by its quoted text, not its question's heading
            hit = next((n for n in qs if _words(sec)[:30] in _text_of(page, n)), None)
        if hit is None:
            # loud, never silent: an item the mapping cannot place is one the split-first rule cannot see
            print(f"brief: no question on {page} is headed '{sec}' - check its size by hand", file=sys.stderr)
        elif hit not in found:
            found.append(hit)
    return found


def section_of(label: str) -> str:
    """The question a report's label names: `homesteads.html` — "May a byre..." -> May a byre..."""
    quoted = re.search(r'"([^"]+)"', label)
    return quoted.group(1) if quoted else label.strip("`* ")


def fr006(page: str) -> list[str]:
    got = subprocess.run([sys.executable, str(WORKLIST), f"{page}.html"], cwd=SKILL, capture_output=True, text=True, check=False)
    keep = [ln.strip() for ln in got.stdout.splitlines() if re.match(r"\s*\d+\.", ln) and re.search(r"\b(NOT-LOCATED|TOO-SHORT|AMBIGUOUS)\b", ln)]
    return [f"- {ln}" for ln in keep]


COMMON = """# Brief - feature 250, page `{page}` ({task}), session {n} of 2: {what}

You are a FRESH session for one half of one page of feature 250 (close the record checks). This brief is the
whole of what you need; do not read the feature's spec, plan or research files to orient - everything you read
stays in your context and is paid for again on every later turn. Work in this clone (`{clone}`); the project's
CLAUDE.md files still apply to you.

**Read narrowly.** For a few notes of a question use `make notes PAGE={page} SECTION=<NNN> KEYS=<key,key>` (in
`.claude/skills/diagram`), which prints those notes and only the paragraphs carrying them - never `cat` a notes
file or `sed` a wide range of a fragment. Grep with `-o` and a short context. Send the lookups you know you need
in one message.

**Measure.** Before each numbered step, open a window:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "{page} <step>" --marks {marks}

"""

WRITE = COMMON + """## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

{fr002}

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words over `research/{page}/*.html` - the label beside it is the REPORT's heading, only a hint.
Then confirm the sentence carries its note (say which) or work it as an FR-002 item. Never confirm against a
fragment the grep did not name.

{fr006}

**Over the size cap on this page:** {over}

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/{page}/`; note the fragment and
   sentence. An item that is a claim about the SETTING is checked against the GM's canon - `budgets.md` and `l7r.md`
   in `/host-l7r-repo/setting/`, and `/host-l7r-repo/gm-assistant/setting/*.md` - with ONE call naming every term of
   every such item: `make canon TERMS="<term>|<term>|<term>"` (in `.claude/skills/diagram`). A direct read of a canon
   file is refused, and so is a second call that does not fold the first's terms (`canon-read-hooks.sh`; R7: fifteen
   sequential greps on the last page).
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/{slug}-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). Keep ONE directory for the page: a second `make source-pages` into it ADDS pages, it never
   overwrites the first batch. A source already in the registry: `make check-bundle KEY=<key> WHOLE=1` (the whole page, in parts) and name its MANIFEST.md.
3. **Write the notes.** First `Read` every fragment and notes file you will change, ALL IN ONE MESSAGE (parallel
   `Read` calls): `Edit` needs the read, and a file a turn re-reads your whole context each time (feature 250 R6:
   the write step took 19 turns for three items). In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its
   `.notes.html` `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`, shaped as `{example}` is - copy its shape rather than
   studying others. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
3b. **Keep every question you touched under the size cap** - 20,000 bytes, question plus notes
   (`python3 scripts/check-question-size.py` from the clone root names any over it; `make quick` fails on one). A
   question over it is SPLIT along its topics: a finding stays with the decision it drove; each part becomes its own
   question - a free prefix, an `<h2 id>` that is the question a reader would ask, its own `Sources:` line naming the
   keys its notes quote, and the notes that its sentences cite moved into its own `.notes.html`; and the sentences that
   join the parts POINT at each other (a link and what the other question is about) rather than restating its
   evidence, so a check reading one part alone meets no claim without its footnote. If a split would separate a
   finding from what it needs to be understood, say so in the handoff instead of splitting. A question named
   above as over the cap that one of your items falls in is split HERE, in this session, while you have it read
   (feature 250 R6: a split in a session of its own cost about 0.8 million, most of it re-reading the question);
   every part goes in the handoff as its own `SECTION=` line, and in one line say what each part relies on from
   the others.
4. **Hand off.** Write `{handoff}`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.
"""

CHECK = COMMON + """Session 1 wrote this page's notes and committed them; its handoff is `{handoff}`. You check and apply
ONE GROUP of the questions it changed - a fresh session per group keeps every context small (feature 250 R3,
recommendation 2). Read only your own lines of the handoff.

**Your questions:** {sections}
**Your registry keys:** {keys}
**Your modals** (each owed an `entry-drift`, each checked by this group and no other): {modals}

## The procedure (check, apply{closing})

5. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE={page} SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format` - each bundle holds only what that check reads - each agent naming its own MANIFEST.md and
   nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`. And the map's modals - EXACTLY those named under Your
   modals, no others (each is checked once, by the group whose load counts it): for each,
   `make check-bundle PAGE={page} SECTION=<its NNN> NO_QUOTES=1 FOR=entry-drift KIND=<its class>` and `entry-drift` naming its
   MANIFEST (a drifted modal is owed at the push, so it is checked here, with the question it was written from).
6. **Apply each report with ONE command.** `quote-check`, `record-format`, `entry-drift` and `source-applicability` end every finding with an
   `EDIT` block (or `EDIT: none - <why>`) - a drifted modal's block edits its class file and every glossary term with a `GLOSSARY` line. When a report arrives, read its
   findings, and run `make apply-edits FROM=<the output_file its dispatch printed>` (in `.claude/skills/diagram`),
   with `SKIP=<n,n>` for any block you disagree with. Then do BY HAND only what it lists as REFUSED, what you
   skipped, and the `EDIT: none` findings - all of them in ONE message of parallel `Edit` calls, never one a turn
   (feature 250 R6: applying by hand took 12 to 27 turns a group, each re-reading 60,000 to 90,000 of context).
   When every report is applied: `make glossary` if a term was added, then `make record && make citations` and
   the four record tests ONCE.
7. **Re-check ONCE, only what moved.** A note changed on a check's finding: `make check-bundle PAGE={page}
   SECTION=<NNN> NOTES=<key,key> FOR=quote-check` and one `quote-check` naming its MANIFEST. A modal rewritten: one `entry-drift`
   on its bundle again. That is the only re-check round: a PARTIAL left after it is not re-checked again - label it
   honestly in the note (what the quote carries and what it does not, or the assertion narrowed to the quote) and
   move on (feature 250 R4: one group re-checked a question three times, a third of its session).
{close}"""

CLOSE_LAST = """8. **Close the page.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py {page}.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T={task} BOXES=1 NOTE="<what closed on the page, with the counts>"`.
   Do NOT run `scripts/sync-with-main.sh done`.
9. **Report.** One paragraph: what your group closed, the agents run, anything left open and why. A finding that
   needs the GM (the record contradicts itself, a rule would change) is not decided: leave the text and say so.
"""

CLOSE_GROUP = """8. **Commit** with a message naming your questions; do NOT tick - a later group closes the page.
9. **Report.** One paragraph: what your group closed, the agents run, anything left open and why.
"""

GROUP_BYTES = 28_000   # the LOAD one check session takes (D17, R8 recommendation 2). Fitted over the six measured check
#                        sessions of R6 to R8: peak context = 40,881 + 2.08 x load, so a session stays near the
#                        ~100,000 the earlier two-question groups peaked at when its load is ~28,000 bytes (observed
#                        2026-09-27; method: each session's questions + owed modals + registry entries against its
#                        recorded peak_context, least squares). The fit is loose - fabric's 2a peaked at 7.5x its
#                        load while fixing tool defects - and R9 measures it again.
#                        R9 did (D18.2): refitted over nine sessions, peak = 52,184 + 1.41 x load; a session's start-up
#                        is a median 117,693 tokens, about 5% of a session, so the budget stays - merging saves little.
MODAL_WORK = 2_000     # a GUESS, R9 to measure: an owed modal costs its report and its rewrite on top of its prose
#                        (a median 1,225 bytes), and counting the prose alone is how `fields` put seven in one session.


def changed_since(base: str, page: str) -> tuple[list[str], list[str]]:
    """(the page's questions, the registry keys) whose files changed between `base` and HEAD - what the write session
    actually touched, DERIVED from its commits rather than read off its handoff's prose (R9)."""
    got = subprocess.run(["git", "-C", str(CLONE), "diff", "--name-only", f"{base}..HEAD"], capture_output=True, text=True, check=False).stdout
    rel = f".claude/skills/diagram/research/{page}/"
    secs = sorted({pathlib.PurePosixPath(f).name[:3] for f in got.splitlines() if f.startswith(rel) and re.match(r"\d{3}-", pathlib.PurePosixPath(f).name)})
    works = ".claude/skills/diagram/research/sources/010-works-cited/"
    keys = sorted({m.group(1) for f in got.splitlines() if f.startswith(works) and (m := re.match(r"\d+-(.+)\.html$", pathlib.PurePosixPath(f).name))})
    return secs, keys


def handoff_list(field: str, handoff: str) -> list[str]:
    """The handoff's `SECTION=` or `KEY=` LIST entries - a line that begins with one (after a list marker), never a
    mention in a sentence. WHY (R9): the archetypes handoff said "SECTION=170 is over the size cap ... so it was not
    split here", the old pattern matched it anywhere, and a whole check group ran on a question the page never touched."""
    value = r"\d{3}" if field == "SECTION" else r"[a-z0-9][a-z0-9-]*"
    return re.findall(rf"^[ \t]*(?:[-*][ \t]+)?`?{field}=({value})", handoff, re.M)


KEYS = "KEYS"   # the registry keys, packed as one load of their own: one session checks them all


def check_groups(handoff: str, sizes: dict[str, int] | None = None, keys_load: int = 0) -> tuple[list[list[str]], list[str]]:
    """(the handoff's questions - and, as the item KEYS, its registry keys - packed into sessions of at most
    GROUP_BYTES of LOAD, first fit, largest first; its keys).

    A question's load is its bytes with its notes AND the prose of every modal owed an `entry-drift` from it (D17:
    counting question bytes alone put three questions, seven owed modals and four sources into one session on
    `fields`, which grew to 171,000). A question with no size known counts as one at the cap. Each group lists its
    sections in number order, KEYS last."""
    sections = list(dict.fromkeys(handoff_list("SECTION", handoff)))
    keys = list(dict.fromkeys(handoff_list("KEY", handoff)))
    size = {s: (sizes or {}).get(s, CAP) for s in sections}
    # a question in the round only for its owed modals (D18) is an item too, sized by those modals alone
    size.update({s: b for s, b in (sizes or {}).items() if s not in size and b > 0})
    if keys:
        size[KEYS] = keys_load
    bins: list[list[str]] = []
    for s in sorted(size, key=lambda x: (-size[x], x)):
        home = next((b for b in bins if sum(size[x] for x in b) + size[s] <= GROUP_BYTES), None)
        (home.append(s) if home is not None else bins.append([s]))
    return sorted((sorted(b) for b in bins), key=lambda b: b[0]), keys


def owed_modals(page: str) -> list[tuple[str, int, list[str]]]:
    """[(modal class name, its docstring's bytes, EVERY section of this page it is owed from)] for each modal
    `_entry_owed.py` names. A modal can be owed from several questions; `homes` credits it to ONE a check group takes."""
    import ast  # noqa: PLC0415
    got = subprocess.run([sys.executable, str(CLONE / "scripts/_entry_owed.py")], cwd=CLONE, capture_output=True, text=True, check=False).stdout
    out: list[tuple[str, int, list[str]]] = []
    lines = got.splitlines()
    for i, line in enumerate(lines):
        m = re.match(r"(.+?) - .* - prose at (\S+):(\d+)$", line)
        reads = lines[i + 1] if i + 1 < len(lines) else ""
        secs = list(dict.fromkeys(re.findall(rf"research/{re.escape(page)}/(\d{{3}})-", reads)))
        if not (m and secs):
            continue
        src = (CLONE / m.group(2)).read_text(encoding="utf-8")
        node = next((n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.ClassDef) and n.lineno == int(m.group(3))), None)
        out.append((node.name if node else m.group(1), len(ast.get_docstring(node) or "") if node else 0, secs))
    return out


def homes(page: str, handoff: str) -> dict[str, tuple[str, int]]:
    """modal class -> (the ONE checked section it is credited to, its prose bytes): the first of the questions it is
    owed from that the handoff checks. That group's load counts it and that group alone checks it (plan review, D17:
    a modal owed from two checked questions in different groups was checked twice and counted once)."""
    checked = list(dict.fromkeys(handoff_list("SECTION", handoff)))
    out = {}
    for cls, prose, secs in owed_modals(page):
        # a modal owed from a question this round did not change is taken too (D18, R9 rec. 3): it is owed at the push
        # anyway (T23), and a page's round packed by load checked such modals at the cheapest rate measured
        out[cls] = (next((s for s in checked if s in secs), secs[0]), prose)
    return out


def loads(page: str, handoff: str) -> tuple[dict[str, int], int]:
    """(section -> its load: question and notes bytes + its owed modals' prose; the registry keys' load: their entries'
    bytes) - what `check_groups` packs."""
    checked = set(handoff_list("SECTION", handoff))
    qs = questions(page)
    # a checked question's load is its bytes; a question in the round ONLY for its owed modals carries none of its own
    # (the session applies no finding to it - its entry-drift bundles are read by the agents, outside the session)
    size = {n: (b if n in checked else 0) for n, (_t, b) in qs.items()}
    # credited to the FIRST of its sections that a check group takes - the group that runs its entry-drift (plan
    # review, D17: crediting the first on the PAGE lost `paddy`, owed from 110 but listed under 020)
    for home, prose in homes(page, handoff).values():
        size[home] += prose + MODAL_WORK
    works = SKILL / "research/sources/010-works-cited"
    keys = handoff_list("KEY", handoff)
    keys_load = sum(f.stat().st_size for k in dict.fromkeys(keys) for f in works.glob(f"*-{k}.html"))
    return size, keys_load


def checks(page: str, task: str) -> int:
    """After session 1: one check brief per group of questions, printed one path a line for the runner."""
    slug = page.replace("/", "-")
    briefs = FEATURE / "briefs"
    handoff = briefs / f"{slug}-handoff.md"
    if not handoff.is_file():
        print(f"brief: no handoff at {handoff} - session 1 did not finish", file=sys.stderr)
        return 2
    text = handoff.read_text(encoding="utf-8")
    base = briefs / f"{slug}-base.txt"
    if base.is_file():  # the questions and keys the write session's COMMITS touched, as the list the packer reads
        secs, ks = changed_since(base.read_text(encoding="utf-8").strip(), page)
        text = "".join(f"- SECTION={s}\n" for s in secs) + "".join(f"- KEY={k}\n" for k in ks)
    groups, keys = check_groups(text, *loads(page, text))
    owed = homes(page, text)
    changed = set(handoff_list("SECTION", text))
    fields = _fields(page, task)
    for n, group in enumerate(groups, 1):
        last = n == len(groups)
        out = briefs / f"{slug}-2{chr(96 + n)}.md"
        mine = KEYS in group
        out.write_text(CHECK.format(n=f"2{chr(96 + n)}", what=f"check and apply, group {n} of {len(groups)}", sections=", ".join(f"SECTION={s}" for s in group if s != KEYS and s in changed) or "none - this group checks only the modals and keys named below",
                                    keys=", ".join(f"KEY={k}" for k in keys) if mine else "none - another group has them" if keys else "none",
                                    modals=", ".join(f"KIND={c} (SECTION={h})" for c, (h, _b) in sorted(owed.items()) if h in group) or "none",
                                    closing=" and close the page" if last else "", close=(CLOSE_LAST if last else CLOSE_GROUP).format(**fields), **fields), encoding="utf-8")
        print(out)
    return 0


CAP = 20_000   # scripts/check-question-size.py's cap, bytes of a question and its notes (feature 250 D14)


def over_cap(page: str) -> str:
    """The page's questions over the size cap, largest first - the write session splits one an item falls in (D15)."""
    d = SKILL / "research" / page
    sizes = []
    for q in sorted(d.glob("[0-9][0-9][0-9]-*.html")):
        if q.name.endswith(".notes.html"):
            continue
        n = q.with_name(q.name[:-5] + ".notes.html")
        size = q.stat().st_size + (n.stat().st_size if n.exists() else 0)
        if size > CAP:
            sizes.append((size, q.name[:3]))
    return ", ".join(f"SECTION={s} ({b:,} bytes)" for b, s in sorted(sizes, reverse=True)) or "none"


def newest_entry() -> str:
    """The registry entry a new one copies its shape from: the highest-numbered, so the newest form."""
    entries = sorted((SKILL / "research/sources/010-works-cited").glob("[0-9]*.html"))
    return str(entries[-1].relative_to(CLONE)) if entries else "-"


def _fields(page: str, task: str) -> dict:
    slug = page.replace("/", "-")
    briefs = FEATURE / "briefs"
    return dict(page=page, task=task, clone=CLONE, marks=(HERE / f"marks-{slug}.json").relative_to(CLONE), slug=slug,
                handoff=(briefs / f"{slug}-handoff.md").relative_to(CLONE))


SPLIT = """# Brief - feature 250: split ONE research question under the size cap

You are a FRESH session with one job: the question `{path}` is {size:,} bytes with its notes, over the 20,000-byte cap
(`scripts/check-question-size.py`, feature 250 D14). Split it. Work in this clone (`{clone}`); its CLAUDE.md files
apply; read the rule as written in `.claude/skills/diagram/research/CLAUDE.md`, "A question has a size", and nothing
else to orient.

1. Read the question and its notes (`{notes}`). Find its TOPICS - the separate things a map reader might ask about -
   not its entry parts: a finding stays with the decision it drove and with the departures that qualify it.
2. Split it: each topic its own question, a free prefix after `{prefix}` (they count by ten), an `<h2 id>` that is the
   question a reader would ask, the Grounds/Evidence comments that apply, its own `Sources:` line naming exactly the
   keys its notes quote, and the notes its sentences cite moved into its own `.notes.html` - every note in exactly one
   place, none rewritten. Keep the ORIGINAL question's heading and id on the part that carries its main finding (map
   modals and links point at it). The sentences that join the parts POINT - a link and what the other question is
   about - and never restate the other part's evidence.
3. Every part under 20,000 bytes with its notes. If a part cannot get there without stripping a finding of what it
   needs, stop and say so rather than splitting it further.
4. In `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py
   tests/interactive/test_record.py"`, and `python3 ../../../scripts/check-entry-headings.py`. Commit. Do not push.
5. Report in one paragraph, which the session that dispatched you will use to judge the split: the questions you
   made, each one's size, and for each part WHAT IT RELIES ON FROM THE OTHERS - and whether a reader, or a check that
   reads that part alone, has what it needs.
"""


def split_brief(page: str, section: str) -> int:
    sys.path.insert(0, str(HERE.parents[2] / "scripts"))
    d = CLONE / ".claude/skills/diagram/research" / page
    q = next((p for p in sorted(d.glob(f"{section}-*.html")) if not p.name.endswith(".notes.html")), None)
    if q is None:
        print(f"brief: no question {section} on {page}", file=sys.stderr)
        return 2
    n = q.with_name(q.name[:-5] + ".notes.html")
    size = q.stat().st_size + (n.stat().st_size if n.exists() else 0)
    out = FEATURE / "briefs" / f"split-{page.replace('/', '-')}-{section}.md"
    out.write_text(SPLIT.format(path=q.relative_to(CLONE), notes=n.relative_to(CLONE), size=size, clone=CLONE, prefix=section), encoding="utf-8")
    print(out)
    return 0


def fr006_questions(page: str) -> list[str]:
    """The sections the page's FR-006 items fall in: each item's quoted text searched in every question (D16 - the
    fields page's FR-006 items sit in its 56,248-byte question 020, which an FR-002-only mapping never saw)."""
    qs = questions(page)
    found = []
    for line in fr006(page):
        probe = _words(line.rsplit("|", 1)[-1])[:30]
        hit = next((n for n in qs if probe and probe in _text_of(page, n)), None)
        label = re.search(r'h3 "([^"]+)"', line)
        if hit is None and label:  # the item was rewritten (NOT-LOCATED); the report's sub-heading still places it
            hit = next((n for n in qs if _words(label.group(1)) in _text_of(page, n)), None)
        if hit and hit not in found:
            found.append(hit)
    return found


def over_cap_items(page: str) -> list[str]:
    """The sections an FR-002 or FR-006 item falls in that are over the cap - each is split, in a session of its own,
    before the write."""
    qs = questions(page)
    return [s for s in dict.fromkeys(item_questions(page) + fr006_questions(page)) if qs[s][1] > CAP]


def write_brief(page: str, task: str) -> int:
    """The write session's brief - REFUSED while a question one of its items falls in is over the cap (D16).

    WHY (R7, recommendation 2): the fabric write session split question 140 itself and then carried its 32,500
    characters to the end, peaking at 137,000 tokens. The split now runs first, as its own session, and this is what
    makes that order the only one: there is no write brief to start from until every such question is split."""
    owed = over_cap_items(page)
    if owed:
        print(f"brief: {page} still has item questions over the cap ({', '.join(owed)}) - the split sessions run first", file=sys.stderr)
        return 2
    items2, items6 = fr002(page), fr006(page)
    fields = _fields(page, task)
    head = subprocess.run(["git", "-C", str(CLONE), "rev-parse", "HEAD"], capture_output=True, text=True, check=False).stdout.strip()
    (FEATURE / "briefs" / f"{fields['slug']}-base.txt").write_text(head + "\n", encoding="utf-8")  # what the checks diff against
    write = FEATURE / "briefs" / f"{fields['slug']}-1.md"
    write.write_text(WRITE.format(n=1, what="locate, read and write", fr002="\n".join(items2) or "- none",
                                  fr006="\n".join(items6) or "- none", over=over_cap(page), example=newest_entry(), **fields), encoding="utf-8")
    print(write)
    return 0


def _then(briefs: pathlib.Path, name: str, verb: str, page: str, task: str, why: str) -> pathlib.Path:
    step = briefs / name
    step.write_text(f"#!/bin/sh\n# {why}\nexec python3 {HERE / 'brief.py'} {verb} {page} {task}\n", encoding="utf-8")
    step.chmod(0o755)
    return step


OWED = """# Brief - feature 250, T23: the map modals still owed an `entry-drift` on `{page}`, group {n} of {of}

You are a FRESH session with one job: check the map modals below against the research questions they were written
from, and bring each back in step. Work in this clone (`{clone}`); the project's CLAUDE.md files still apply to you.
Read narrowly - you need no question's whole text; the agents read the bundles.

**Measure.** Before each numbered step: `python3 specs/250-close-the-record-checks/measure/tokens.py mark "owed {page} {n} <step>" --marks {marks}`

**Your modals:** {modals}

1. **Check, all in one message, in the background.** For each modal:
   `make check-bundle PAGE={page} SECTION=<its NNN> NO_QUOTES=1 FOR=entry-drift KIND=<its class>` (in
   `.claude/skills/diagram`) and one `entry-drift` naming its MANIFEST.
2. **Apply each report with ONE command**: `make apply-edits FROM=<the output_file its dispatch printed>`; the refused
   blocks and any `EDIT: none` finding by hand, all in ONE message of parallel `Edit` calls.
3. **Re-check ONCE, only what moved**: one `entry-drift` on each rewritten modal's bundle again; a drift left after it
   is labeled honestly in the modal's `Note:`, not checked a third time.
4. **Record the verdicts.** Append one line per modal to `specs/250-close-the-record-checks/owed-verdicts.md`:
   `- <class> (<page> SECTION=<NNN>): IN-STEP | REWRITTEN | LABELED | CANNOT-TELL - <one clause>`. A modal found
   IN-STEP stays on `_entry_owed.py`'s list (only a rewrite clears it), and the push discharges exactly those lines;
   a CANNOT-TELL is NOT discharged - say what the agent needed, and the closing session answers it before the push.
5. In `.claude/skills/diagram`: `make test-file FILE="tests/interactive/test_classes.py tests/interactive/test_classes_docstrings.py"`;
   commit naming your modals. Do NOT tick, do NOT push. Report in one paragraph: each modal's verdict.
"""


def owed_briefs(page: str, task: str) -> int:
    """T23 (D20): the page's owed modals, packed by load into groups, each a brief; printed one path a line."""
    slug = page.replace("/", "-")
    load = {cls: prose + MODAL_WORK for cls, prose, _secs in owed_modals(page)}
    home = {cls: secs[0] for cls, _p, secs in owed_modals(page)}
    if not load:
        print(f"brief: nothing is owed on {page}", file=sys.stderr)
        return 2
    bins: list[list[str]] = []
    for cls in sorted(load, key=lambda c: (-load[c], c)):
        b = next((b for b in bins if sum(load[x] for x in b) + load[cls] <= GROUP_BYTES), None)
        (b.append(cls) if b is not None else bins.append([cls]))
    for n, group in enumerate(bins, 1):
        out = FEATURE / "briefs" / f"owed-{slug}-{n}.md"
        out.write_text(OWED.format(page=page, n=n, of=len(bins), clone=CLONE, marks=(HERE / f"marks-owed-{slug}.json").relative_to(CLONE),
                                   modals=", ".join(f"KIND={c} (SECTION={home[c]})" for c in sorted(group))), encoding="utf-8")
        print(out)
    return 0


def owed_check() -> int:
    """Before the push (D20.2, plan review): every pair `_entry_owed.py` names must have an IN-STEP line in
    `owed-verdicts.md`; a pair without one - CANNOT-TELL, never dispatched, or newly created - is printed and fails,
    because `ENTRY_DRIFT_OK` clears the whole gate and must only ever clear pairs a check found in step."""
    got = subprocess.run([sys.executable, str(CLONE / "scripts/_entry_owed.py")], cwd=CLONE, capture_output=True, text=True, check=False).stdout
    named = sorted({m.group(1) for line in got.splitlines() if (m := re.match(r"(.+?) - .* - prose at \S+:\d+$", line))})
    ledger = FEATURE / "owed-verdicts.md"
    text = ledger.read_text(encoding="utf-8") if ledger.is_file() else ""
    in_step = set()
    for page in ("homesteads", "archetypes", "fields", "water", "vegetation"):
        for cls, _p, _s in owed_modals(page):
            if re.search(rf"^- {re.escape(cls)} \(.*\): IN-STEP\b", text, re.M):
                in_step.add(cls)
    keys = {}
    for f in (SKILL / "l7r/diagram/interactive/classes").glob("*.py"):
        for m in re.finditer(r"^class (\w+)\(Kind\):.*?^    key = \"([^\"]+)\"", f.read_text(encoding="utf-8"), re.M | re.S):
            keys[m.group(2)] = m.group(1)
    open_ = [k for k in named if keys.get(k) not in in_step]
    for k in open_:
        print(f"owed-check: {k} ({keys.get(k, '?')}) has no IN-STEP verdict in {ledger.name} - answer it before the push")
    print(f"owed-check: {len(named)} pair(s) named, {len(named) - len(open_)} with an IN-STEP verdict, {len(open_)} open")
    return 1 if open_ else 0


def main(argv: list[str]) -> int:
    if argv == ["owed-check"]:
        return owed_check()
    if len(argv) == 3 and argv[0] == "split":
        return split_brief(argv[1], argv[2])
    if len(argv) == 3 and argv[0] == "checks":
        return checks(argv[1], argv[2])
    if len(argv) == 3 and argv[0] == "write":
        return write_brief(argv[1], argv[2])
    if len(argv) == 3 and argv[0] == "owed":
        return owed_briefs(argv[1], argv[2])
    if len(argv) != 2:
        print("usage: brief.py <page> <task>  |  brief.py write|checks <page> <task>  |  brief.py split <page> <NNN>", file=sys.stderr)
        return 2
    page, task = argv
    if not (SKILL / "research" / page).is_dir():
        print(f"brief: no research page {page} (a page under cities/ is named cities/<page>)", file=sys.stderr)
        return 2
    if not fr002(page) and not fr006(page):
        print(f"brief: {page} owes nothing under FR-002 or FR-006", file=sys.stderr)
        return 2
    slug = page.replace("/", "-")
    briefs = FEATURE / "briefs"
    briefs.mkdir(exist_ok=True)
    checks_step = _then(briefs, f"{slug}-checks.sh", "checks", page, task, "the check briefs, made from session 1's handoff when it ends (feature 250 R3, recommendation 2)")
    owed = over_cap_items(page)
    queue: list[str] = []
    for section in owed:
        split_brief(page, section)
        queue.append(str(briefs / f"split-{slug}-{section}.md"))
    if owed:
        queue.append("then:" + str(_then(briefs, f"{slug}-write.sh", "write", page, task, "the write brief, made once the splits have run (feature 250 D16)")))
    else:
        if write_brief(page, task):
            return 2
        queue.append(str(briefs / f"{slug}-1.md"))
    queue.append(f"then:{checks_step}")
    print(f'brief: {len(fr002(page))} FR-002 and {len(fr006(page))} FR-006 item(s); {len(owed)} split(s) first. Run:\n    make page-session BRIEF="{" ".join(queue)}"')
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
