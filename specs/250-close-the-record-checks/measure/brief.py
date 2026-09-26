#!/usr/bin/env python3
"""The brief a fresh page session starts from (feature 250 D7): what ONE page owes, and how to do it.

    brief.py <page> <task>      writes specs/250-close-the-record-checks/briefs/<page>.md and prints its path

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


BRIEF = """# Brief - feature 250, page `{page}` ({task})

You are a FRESH session for one page of feature 250 (close the record checks). This brief is the whole of
what you need; do not read the feature's spec, plan or research files to orient - they cost you tokens on
every later turn, and everything they would tell you about this page is here. Work in this clone
(`{clone}`); the project's CLAUDE.md files still apply to you.

## Measure as you go

Before each numbered step below, open a window on the token meter:

    python3 specs/250-close-the-record-checks/measure/tokens.py mark "<page> <step>" --marks {marks}

## What this page owes

**FR-002 - assertions a quote-check found carrying no footnote.** Each ends in exactly one of three forms: a
CITATION (a quotation from a public page that says it), an ABSENCE note (`no publicly readable source
(searched YYYY-MM-DD: what was read, and that it does not say this)`), or a GROUNDS note (`no source is owed:
...`) for a sentence that is not a claim about the real world. A note is never written from memory.

{fr002}

**FR-006 - items 242's work list can no longer find.** Each was rewritten during 242. Find it by grepping its
distinctive words (a figure, a name, a term) over `research/{page}/*.html` - the section label beside it is
the REPORT's heading, not the record's, and is only a hint. Then either confirm the sentence carries its note
(say which note) or work it as an FR-002 item. Never confirm against a fragment the grep did not name.

{fr006}

## The procedure

1. **Locate.** For every item, grep its words over `.claude/skills/diagram/research/{page}/` and note the
   fragment and sentence. Read only the fragments that hold items.
2. **Read the sources.** Save the candidate pages with `make source-pages OUT=<dir> URLS="<u1> <u2>"` (in
   `.claude/skills/diagram`; `<dir>` under `/tmp/l7r-check/`), grep them yourself for the passages, then
   dispatch ONE `source-reader` over every item at once. Hand it the saved-pages directory and each claim's
   text written into the prompt - never a path under `/diagram` (a reader that opens one is handed ~28,000
   tokens of CLAUDE.md files; `check-bundle-hooks.sh` refuses the dispatch). A source already in the
   registry: `make check-bundle KEY=<key>` and name its MANIFEST.md.
3. **Write the notes.** In the fragment, `<sup class="fn" data-note="<key>"></sup>` at the sentence; in its
   `.notes.html`, `<li data-note="<key>">...</li>` (no numbers anywhere). A new registry key needs both
   write-ups in a new `research/sources/010-works-cited/NNNN-<key>.html` (a free prefix; copy a neighbor's
   shape). Use `Edit`, not a script, on a file you have read. Then in `.claude/skills/diagram`:
   `make record && make citations && make test-file FILE="tests/interactive/test_footnotes.py
   tests/interactive/test_citations.py tests/interactive/test_sources.py tests/interactive/test_record_format.py"`.
4. **Check, one agent per changed entry or key, all in one message, in the background.** For each changed
   question: `make check-bundle PAGE={page} SECTION=<NNN>`, then `quote-check` and `record-format`, each
   naming the MANIFEST.md it printed and nothing else. For each new or changed registry key:
   `make check-bundle KEY=<key>` and `source-applicability`. Each replies with ONE line of counts and writes
   its report to `REPORT.md` in its bundle.
5. **Apply.** Open a REPORT.md only when its line reports something to apply; apply every finding (a new
   glossary term is a file in `l7r/diagram/interactive/assets/glossary/`, then `make glossary`); re-run
   step 3's commands.
6. **Close.** `python3 specs/242-cite-the-unfootnoted-assertions/measure/worklist.py {page}.html` (from
   `.claude/skills/diagram`) for the FR-006 figure; commit; tick with
   `make tick F=250-close-the-record-checks T={task} BOXES=1 NOTE="<what closed, with the counts>"`.
   Do NOT run `scripts/sync-with-main.sh done` - the feature has other open tasks.
7. **Report.** Your last message is one paragraph: items closed per form (citation / absence / grounds),
   FR-006 items confirmed or worked, the agents run, and anything left open and why.

If a finding needs the GM (a claim the record contradicts, a rule that would change), do not decide it: write
it into your last paragraph and leave the text as it is.
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
    out = FEATURE / "briefs" / f"{page.replace('/', '-')}.md"
    out.parent.mkdir(exist_ok=True)
    marks = HERE / f"marks-{page.replace('/', '-')}.json"
    out.write_text(BRIEF.format(page=page, task=task, clone=CLONE, marks=marks.relative_to(CLONE),
                                fr002="\n".join(items2) or "- none", fr006="\n".join(items6) or "- none"), encoding="utf-8")
    print(f"brief: {len(items2)} FR-002 and {len(items6)} FR-006 item(s) -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
