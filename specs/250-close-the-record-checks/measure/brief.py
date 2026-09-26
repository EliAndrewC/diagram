#!/usr/bin/env python3
"""The brief a fresh page session starts from (feature 250 D7): what ONE page owes, and how to do it.

    brief.py <page> <task>      writes briefs/<page>-1.md (locate, read, write) and briefs/<page>-2.md (check,
                                apply, close) - two FRESH sessions per page (feature 250, recommendation 2: the first
                                page's applying turns ran at the end of a session that had read every source, and were
                                a third of it)

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
4. **Hand off.** Write `{handoff}`: one line per changed question (`SECTION=<NNN>`), one per new or changed
   registry key (`KEY=<key>`), each item's form (citation / absence / grounds), each FR-006 item's verdict, and
   anything left open and why. Commit. Do NOT run the checks, do NOT tick, do NOT push - session 2 does the checks
   in a fresh context. Your last message is one paragraph saying what you wrote.
"""

CHECK = COMMON + """Session 1 has written this page's notes and committed them. Its handoff, `{handoff}`, lists the questions
and registry keys it changed - read it first; it is your work list.

## The procedure (session 2: check, apply, close)

5. **Check, one agent per changed question or key, all in one message, in the background.** For each question:
   `make check-bundle PAGE={page} SECTION=<NNN>`, then `quote-check` and `record-format`, each naming the
   MANIFEST.md it printed and nothing else (the MANIFEST holds every copy inline). For each new or changed key:
   `make check-bundle KEY=<key>` and `source-applicability`. Each replies with its counts first, then only what
   you must act on.
6. **Apply** every finding (a glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then
   `make glossary`), then re-run the record commands and tests.
7. **Re-check only what moved.** If you changed a note on a check's finding, re-check THAT note alone:
   `make check-bundle PAGE={page} SECTION=<NNN> NOTES=<key,key>` and one `quote-check` naming its MANIFEST.
8. **Close.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py {page}.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T={task} BOXES=1 NOTE="<what closed, with the counts>"`. Do NOT run
   `scripts/sync-with-main.sh done`.
9. **Report.** One paragraph: items closed per form, FR-006 items confirmed or worked, the agents run, anything
   left open and why. A finding that needs the GM (the record contradicts itself, a rule would change) is not
   decided: leave the text and say so.
"""


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: brief.py <page> <task>", file=sys.stderr)
        return 2
    page, task = argv
    items2, items6 = fr002(page), fr006(page)
    if not items2 and not items6:
        print(f"brief: {page} owes nothing under FR-002 or FR-006", file=sys.stderr)
        return 2
    slug = page.replace("/", "-")
    briefs = FEATURE / "briefs"
    briefs.mkdir(exist_ok=True)
    marks = HERE / f"marks-{slug}.json"
    fields = dict(page=page, task=task, clone=CLONE, marks=marks.relative_to(CLONE), slug=slug,
                  handoff=(briefs / f"{slug}-handoff.md").relative_to(CLONE),
                  fr002="\n".join(items2) or "- none", fr006="\n".join(items6) or "- none")
    outs = []
    for n, (what, template) in enumerate((("locate, read and write", WRITE), ("check, apply and close", CHECK)), 1):
        out = briefs / f"{slug}-{n}.md"
        out.write_text(template.format(n=n, what=what, **fields), encoding="utf-8")
        outs.append(out)
    print(f"brief: {len(items2)} FR-002 and {len(items6)} FR-006 item(s) -> " + " then ".join(str(o) for o in outs))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
