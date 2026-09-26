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


def fr002(page: str) -> list[str]:
    sys.path.insert(0, str(HERE))
    import assertions  # noqa: PLC0415

    out = []
    for name in assertions.NAMES:
        lines = (assertions.REPORTS / name).read_text(encoding="utf-8").splitlines()
        for item in assertions.items_of(lines):
            if (item["page"] or assertions._ONE_PAGE.get(name, "")) == page.split("/")[-1]:
                out.append(f"- **{section_of(item['section'])}** - {item['text']}  _(from `{name}`)_")
    return out


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

## The procedure (session 1: locate, read, write)

1. **Locate.** Grep each item's words over `.claude/skills/diagram/research/{page}/`; note the fragment and
   sentence.
2. **Read the sources.** Save candidate pages with `make source-pages OUT=/tmp/l7r-check/{slug}-pages URLS="<u1>
   <u2>"`, grep them yourself, then dispatch ONE `source-reader` over every item at once, handing it the saved
   directory and each claim's text in the prompt - never a path under `/diagram` (`check-bundle-hooks.sh`
   refuses that). A source already in the registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment `<sup class="fn" data-note="<key>"></sup>`; in its `.notes.html`
   `<li data-note="<key>">...</li>` (no numbers). A new key needs both write-ups in a new
   `research/sources/010-works-cited/NNNN-<key>.html`. `Edit` a file you have read; never script it. Then in
   `.claude/skills/diagram`: `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
3b. **Keep every question you touched under the size cap** - 20,000 bytes, question plus notes
   (`python3 scripts/check-question-size.py` from the clone root names any over it; `make quick` fails on one). A
   question over it is SPLIT along its topics: a finding stays with the decision it drove; each part becomes its own
   question - a free prefix, an `<h2 id>` that is the question a reader would ask, its own `Sources:` line naming the
   keys its notes quote, and the notes that its sentences cite moved into its own `.notes.html`; and the sentences that
   join the parts POINT at each other (a link and what the other question is about) rather than restating its
   evidence, so a check reading one part alone meets no claim without its footnote. If a split would separate a
   finding from what it needs to be understood, say so in the handoff instead of splitting.
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

## The procedure (check, apply{closing})

5. **Check, all in one message, in the background.** For each of your questions:
   `make check-bundle PAGE={page} SECTION=<NNN> FOR=quote-check` for `quote-check`, and `... FOR=record-format`
   for `record-format` - each bundle holds only what that check reads - each agent naming its own MANIFEST.md and
   nothing else. For each of your keys:
   `make check-bundle KEY=<key>` and `source-applicability`. And the map's modals: run
   `python3 scripts/_entry_owed.py` from the clone root; for each class it names whose entry is one of YOUR
   questions, `make check-bundle PAGE={page} SECTION=<NNN> NO_QUOTES=1 FOR=entry-drift KIND=<class>` and `entry-drift` naming its
   MANIFEST (a drifted modal is owed at the push, so it is checked here, with the question it was written from).
6. **Apply ONE REPORT PER TURN.** Every finding of one report goes in ONE message: all its edits as parallel
   `Edit` calls (or one patch), never one finding a turn - every turn re-reads your whole context. Then run
   `make record && make citations` and the four record tests ONCE for everything applied, not once per report.
   A glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then `make glossary`.
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

GROUP = 2   # questions a check session takes: R3 measured one session growing to 218,000 over five


def check_groups(handoff: str) -> tuple[list[list[str]], list[str]]:
    """(the handoff's questions in groups of GROUP, its keys) - read off its `SECTION=NNN` and `KEY=k` lines."""
    sections = list(dict.fromkeys(re.findall(r"SECTION=(\d{3})", handoff)))
    keys = list(dict.fromkeys(re.findall(r"KEY=([a-z0-9][a-z0-9-]*)", handoff)))
    return [sections[i:i + GROUP] for i in range(0, len(sections), GROUP)], keys


def checks(page: str, task: str) -> int:
    """After session 1: one check brief per group of questions, printed one path a line for the runner."""
    slug = page.replace("/", "-")
    briefs = FEATURE / "briefs"
    handoff = briefs / f"{slug}-handoff.md"
    if not handoff.is_file():
        print(f"brief: no handoff at {handoff} - session 1 did not finish", file=sys.stderr)
        return 2
    groups, keys = check_groups(handoff.read_text(encoding="utf-8"))
    fields = _fields(page, task)
    for n, group in enumerate(groups, 1):
        last = n == len(groups)
        out = briefs / f"{slug}-2{chr(96 + n)}.md"
        out.write_text(CHECK.format(n=f"2{chr(96 + n)}", what=f"check and apply, group {n} of {len(groups)}", sections=", ".join(f"SECTION={s}" for s in group),
                                    keys=", ".join(f"KEY={k}" for k in keys) if n == 1 and keys else "none - another group has them" if keys else "none",
                                    closing=" and close the page" if last else "", close=(CLOSE_LAST if last else CLOSE_GROUP).format(**fields), **fields), encoding="utf-8")
        print(out)
    return 0


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


def main(argv: list[str]) -> int:
    if len(argv) == 3 and argv[0] == "split":
        return split_brief(argv[1], argv[2])
    if len(argv) == 3 and argv[0] == "checks":
        return checks(argv[1], argv[2])
    if len(argv) != 2:
        print("usage: brief.py <page> <task>  |  brief.py checks <page> <task>", file=sys.stderr)
        return 2
    page, task = argv
    items2, items6 = fr002(page), fr006(page)
    if not items2 and not items6:
        print(f"brief: {page} owes nothing under FR-002 or FR-006", file=sys.stderr)
        return 2
    fields = _fields(page, task)
    briefs = FEATURE / "briefs"
    briefs.mkdir(exist_ok=True)
    write = briefs / f"{fields['slug']}-1.md"
    write.write_text(WRITE.format(n=1, what="locate, read and write", fr002="\n".join(items2) or "- none",
                                  fr006="\n".join(items6) or "- none", **fields), encoding="utf-8")
    then = briefs / f"{fields['slug']}-checks.sh"
    then.write_text(f"#!/bin/sh\n# the check briefs, made from session 1's handoff when it ends (feature 250 R3, recommendation 2)\n"
                    f"exec python3 {HERE / 'brief.py'} checks {page} {task}\n", encoding="utf-8")
    then.chmod(0o755)
    print(f"brief: {len(items2)} FR-002 and {len(items6)} FR-006 item(s) -> {write}, then the check groups: then:{then}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
