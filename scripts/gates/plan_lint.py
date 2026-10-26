"""What `make decide` refuses before a plan section reaches its review (feature 385 T84 and T86, plans D105 and D107).

WHY. The evening of 2026-10-18 sent 42 plan reviews; four came back unreviewable for what a script can see first - the GM's words
not in `request.md` (T70, T75 twice) and a figure with no date or method (T81) - and T64's first plan misquoted the GM.
"""

from __future__ import annotations

import pathlib
import re

_GM = re.compile(r"\bthe GM(?:'s)?\b", re.I)
_WORD = re.compile(r"[a-z0-9]+")


def _folded(text: str) -> str:
    return " " + " ".join(_WORD.findall(text.lower())) + " "


def gm_quotes(section: str) -> list[str]:
    """Each double-quoted span that follows "the GM" (any case, with or without 's) within the same sentence."""
    out: list[str] = []
    masked = re.sub(r"`[^`\n]*`", lambda c: " " * len(c.group(0)), section)  # a code span names words, it quotes no one
    for m in _GM.finditer(masked):
        if masked[masked.rfind("\n", 0, m.start()) + 1 : m.start()].count('"') % 2:
            continue  # "the GM" inside a quotation is a mention, not an attribution
        i, quoting, start = m.end(), False, 0
        while i < len(masked):
            ch = masked[i]
            if ch == '"':
                if quoting:
                    out.append(section[start:i])  # read from the text as written, code spans and all
                else:
                    start = i + 1
                quoting = not quoting
            elif not quoting and (ch == "\n" and masked[i + 1 : i + 2] in ("\n", "") or ch in ".!?" and masked[i + 1 : i + 2] in (" ", "\n", "")):
                break
            i += 1
    return list(dict.fromkeys(out))


def gm_quotes_missing(section: str, request: str) -> list[str]:
    """The GM quotes whose words, folded, are not a run in the request folded the same way (D105) - every length, no escape."""
    req = _folded(request)

    def found(q: str) -> bool:  # an elided quote is found when each piece between its ellipses is (the plan review's note)
        return all(_folded(p) in req for p in re.split(r"\.\.\.|\u2026", q) if _folded(p).strip())

    return [q for q in gm_quotes(section) if _folded(q).strip() and not found(q)]


_ITEM4 = re.compile(r"^4\. \*\*.*?(?=^\d+\. \*\*|^#|\Z)", re.M | re.S)
_SPAN = re.compile(r"`([^`\n]*)`")
_NOT_A_FIGURE = re.compile(
    r"\b\d{4}-\d\d-\d\d(?:T\d\d:\d\d(?::\d\d)?Z?)?\b|\b\d\d:\d\d(?::\d\d)?Z?\b|\b(?:FR|SC)-\d+[a-z]?\b|\b[TDA]\d+[a-z]?\b|\b0\d{3}\b"
)
#: a number that names a thing rather than measures it: "round 1", "seed 45", "hour 22", "amendment 6", "item 4"
_NAMED = re.compile(r"(?i)\b(?:round|rounds|seed|seeds|hour|amendment|item|items|change|wave|batch|step|task|feature|proposal|part|tier|version|line|group)\s+\d+(?:\s*(?:-|and|to)\s*\d+)?\b")
_LABEL = re.compile(r"(?is)(?=.*\bmeasured\b)(?=.*\b20\d\d-\d\d-\d\d\b)(?=.*\()|\bm:[\w.-]+")


def unlabeled_figure(section: str) -> str:
    """The first figure Approach item 4 states whose own sentence carries no `measured <date> (<method>)` or `m:<key>`, or ''
    (feature 385 T86, plan D107; T81's "4.4 s (measured)" came back unreviewable). A code span holding a path, a key or a command
    is set aside; one holding a value is read as prose; dates, clock times and ids are no figures."""
    m = _ITEM4.search(section)
    if not m:
        return ""
    item = _SPAN.sub(lambda s: " " if re.search(r"/|::|=|\bmake ", s.group(1)) else s.group(1), m.group(0))
    for sentence in re.split(r"(?<=\.)\s+|\n(?=\S)", item):
        bare = _NOT_A_FIGURE.sub(" ", re.sub(r"^\s*4\.", " ", sentence))
        bare = _NAMED.sub(" ", bare)
        if re.search(r"(?<![\w-])\d[\d,.]*(?![\w-])", bare) and not _LABEL.search(sentence):
            return sentence.strip()[:160]
    return ""


def _figures() -> tuple[re.Pattern[str], re.Pattern[str]]:
    """The spec-lint's one definition of a figure with a unit, and of a one-shot label (`spec_figures`)."""
    import sys  # noqa: PLC0415

    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import spec_figures  # noqa: PLC0415 - the module beside this one

    return spec_figures._FIGURE, spec_figures._ONE_SHOT


def unlabeled_unit_figure(section: str) -> str:
    """The first sentence anywhere in the section stating a figure WITH A UNIT and carrying no label - `measured <date>
    (<method>)`, `observed <date>, method: ...` or `m:<key>` for a measurement, a research label, page or knob for a decided
    size (`_DECISION_LABEL`) - or '' (feature 430 T05, D5: item 4 alone was read before, and the
    plan reviews of the day found unlabeled figures in a Constitution Check and a Decision). Code spans and fenced blocks name
    things; they are set aside."""
    figure, one_shot = _figures()
    text = re.sub(r"^```.*?^```", " ", section, flags=re.M | re.S)
    # ...A SENTENCE WRAPPED ACROSS LINES IS ONE SENTENCE (feature 427's plan: a label on one line, its figure on the next): split at
    # a sentence's end, a blank line, or a line that opens a list item, a numbered item, a heading or a table row
    for sentence in re.split(r"(?<=[.;])\s+|\n\s*\n|\n(?=\s*(?:[-*] |\d+\. |#|\|))", text):
        bare = _NOT_A_FIGURE.sub(" ", _SPAN.sub(" ", sentence))  # the figure is read outside code spans, the label anywhere
        bare = _RULE.sub(" ", bare)
        if figure.search(bare) and not (_LABEL.search(sentence) or one_shot.search(sentence) or _DECISION_LABEL.search(sentence)):
            return " ".join(sentence.split())[:160]
    return ""


#: a DECIDED figure's labels (root CLAUDE.md, "every rendering decision is labeled"): a planned size is no measurement, and it
#: carries its research label, its research page, or the knob it is - the test fixture's "the bath 10 x 8 ft" (feature 430 T05).
#: A research-record plan's figure is a SOURCE's, and its label is the verdict it will carry - ATTESTED, ATTESTED ONLY FOR,
#: NOT ATTESTED, SILENT - or "this project's arithmetic" (feature 431: its plan quoted 293 man-days a cho, ATTESTED ONLY FOR one farm book)
_DECISION_LABEL = re.compile(
    r"\b(?:GUESS|CONVENTION|DEVIATION|UNRESEARCHED|ACCURATE|HISTORICALLY ACCURATE|ATTESTED|SILENT)\b|this project's arithmetic"
    r"|research/questions/|\bknob\b|\bR\d+\b"
)


#: a RULE stated as a figure, which measures nothing: the coverage floor ("100% coverage of the new module" - feature 427's plan,
#: the first this lint read, refused on it)
_RULE = re.compile(r"\b100\s*%\s+(?:code\s+|line\s+)?coverage\b", re.I)


_APPROACH_HEAD = re.compile(r"^### (T\d+[a-z]?) Approach\b.*$", re.M)


def missing_red_exit(section: str) -> str:
    """The task whose approach block's item 6 routes no red result through `make arbiter-ask` (D35's wording), or ''."""
    for m in _APPROACH_HEAD.finditer(section):
        rest = section[m.end() :]
        nxt = re.search(r"^#{2,3} ", rest, re.M)
        block = rest[: nxt.start()] if nxt else rest
        item6 = re.search(r"^6\.\s.*?(?=^\d+\.\s|\Z)", block, re.M | re.S)
        if not item6 or "make arbiter-ask" not in item6.group(0):
            return m.group(1)
    return ""


def tasks_without_approach(spec_dir: pathlib.Path, plan_text: str) -> list[str]:
    """In a plan whose tasks owe approach blocks - it opts in (`**Approach checklist**:`) or holds one already - each OPEN task
    of tasks.md with no `### Txx Approach` block in the plan or plan-done.md (feature 430 D5). A plan with neither predates the
    checklist (feature 385, `approach_gate.py` D8) and is not asked."""
    done = (spec_dir / "plan-done.md").read_text(encoding="utf-8") if (spec_dir / "plan-done.md").is_file() else ""
    if "**Approach checklist**:" not in plan_text and not _APPROACH_HEAD.search(plan_text + done):
        return []
    tasks = (spec_dir / "tasks.md").read_text(encoding="utf-8") if (spec_dir / "tasks.md").is_file() else ""
    have = {m.group(1) for m in _APPROACH_HEAD.finditer(plan_text + "\n" + done)}
    return [t for t in re.findall(r"^- \[ \] (T\d+[a-z]?)\b", tasks, re.M) if t not in have]


def plan_refusal(spec_dir: pathlib.Path, plan_text: str, blocks: list[str]) -> str:
    """Why `make plan-delta` writes no bundle: a refusal of any block it would bundle, or a task with no approach block, or ''
    (feature 430 T05, D5: a plan review is never dispatched on what a script can see - no bundle, nothing to dispatch on)."""
    for body in blocks:
        if why := refusal(spec_dir, body):
            return why
    if missing := tasks_without_approach(spec_dir, plan_text):
        return ("open tasks with no `### Txx Approach (checklist part A)` block in the plan - write one for each, `make task-add`'s "
                f"template has the form (feature 430 D5):\n  {', '.join(missing)}")
    return ""


def refusal(spec_dir: pathlib.Path, section: str) -> str:
    """Why `make decide` refuses this section, or ''."""
    req = (spec_dir / "request.md").read_text(encoding="utf-8") if (spec_dir / "request.md").is_file() else ""
    if missing := gm_quotes_missing(section, req):
        return ("the section quotes the GM with words request.md does not hold - add the GM's words to request.md verbatim, or "
                "correct the quote (feature 385 T84):\n  " + "\n  ".join(f'"{q.strip()[:160]}"' for q in missing))
    if fig := unlabeled_figure(section):
        return ("Approach item 4 states a figure whose sentence carries no `measured <YYYY-MM-DD> (<method>)` or `m:<key>` - label "
                f"it where it stands (feature 385 T86):\n  {fig}")
    if fig := unlabeled_unit_figure(section):
        return ("a figure with a unit whose sentence carries no label - a measurement `measured <YYYY-MM-DD> (<method>)`, `observed "
                "<YYYY-MM-DD>, method: ...` or `m:<key>`; a decided size its research label (GUESS, CONVENTION, ...), its page or "
                f"its knob - label it where it stands (feature 430 D5):\n  {fig}")
    if task := missing_red_exit(section):
        return (f"{task}'s approach item 6 routes no red result through `make arbiter-ask` - give it D35's red exit, as `make "
                f"task-add`'s template words it (feature 430 D5):\n  {RED_EXIT_HINT}")
    return ""


RED_EXIT_HINT = "Red: what failed recorded and the task set down, a claim that it cannot be done ruled through `make arbiter-ask`."
