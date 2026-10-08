#!/usr/bin/env python3
"""A research question's PROSE stays under a size cap - checked on the questions a change touches (feature 250 D14; prose only
since feature 292).

WHY. Feature 258 split the record into one file per question, but nothing bounded how large one question could grow,
and a check reads a whole question: on feature 250's fourth measured page one question of 23,000 bytes (its prose and
its notes) doubled what the `quote-check` on it read against the page before (research R5). The GM, 2026-09-26: do it,
and pick the size from the measurements.

THE CAP: 20,000 bytes of the question file - set as the record's 90th percentile of question plus notes (288 questions,
median 6,750), about 5,000 tokens, which a check reads in one turn with room to spare. SINCE FEATURE 292 THE NOTES DO NOT
COUNT (GM 2026-09-29, approving the session's proposal): every check and every editing session reads a question's prose
whole, but only the quote-check reads its notes whole, and it is handed them in batches (`_check_bundle.py`,
`NOTES_BUDGET`) - so the notes are bounded where they are read, and a merged topic (feature 292's reorganization) may
carry as many notes as its findings need. The originals of translated quotations (`.originals.html`) are not counted
either: only the translation check reads them. It is applied to what a change
TOUCHES, not to the whole record: 23 questions were over it when it landed, and each is split when its page is next
worked, by the session that knows it. A question over it is split along its topics - a finding stays with the decision
it drove - into questions of their own, each with its heading and `Sources:` line, and the sentences that join them
POINT at each other rather than restating each other's evidence, so a check reading one question alone meets no
unfootnoted claim.

    check-question-size.py              the questions changed since the merge base with origin/main; exit 1 on one over
    check-question-size.py --report     every question over the cap, largest first
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

CAP = 20_000
RECORD = pathlib.Path("research")
#: A question's page (feature 303: `NNNN-<slug>.html`, or how our maps draw it, `NNNN-<slug>.drawing.html`).
_QUESTION = re.compile(r"^[0-9]{4}-[^.]+(?:\.drawing)?\.html$")
#: A question's companion files, beside it: its notes and the originals of its translated quotations.
COMPANIONS = (".notes.html", ".originals.html")


def is_question(path: pathlib.Path) -> bool:
    parts = path.parts
    return _QUESTION.match(path.name) is not None and "questions" in parts


def question_of(path: pathlib.Path) -> pathlib.Path:
    """A question's notes or originals file -> the question it belongs to; a question is itself."""
    for suffix in COMPANIONS:
        if path.name.endswith(suffix):
            return path.with_name(path.name[: -len(suffix)] + ".html")
    return path


def size(question: pathlib.Path) -> int:
    """The question's prose, in bytes - its notes and originals are not counted (feature 292)."""
    return question.stat().st_size


def changed(root: pathlib.Path) -> list[pathlib.Path]:
    base = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=root, capture_output=True, text=True, check=False).stdout.strip()
    names = subprocess.run(["git", "diff", "--name-only", base or "HEAD", "--", str(RECORD)], cwd=root, capture_output=True, text=True, check=False).stdout
    names += subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", str(RECORD)], cwd=root, capture_output=True, text=True, check=False).stdout
    out = {question_of(pathlib.Path(n)) for n in names.split() if n}
    return sorted(q for q in out if is_question(q) and (root / q).is_file())


def every(root: pathlib.Path) -> list[pathlib.Path]:
    return sorted(q.relative_to(root) for q in (root / RECORD / "questions").glob("[0-9][0-9][0-9][0-9]-*.html")
                  if is_question(q.relative_to(root)))


def main(argv: list[str]) -> int:
    root = pathlib.Path(subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True, check=True).stdout.strip())
    if "--report" in argv:
        over = sorted(((size(root / q), q) for q in every(root) if size(root / q) > CAP), reverse=True)
        for n, q in over:
            print(f"{n:>7,}  {q}")
        print(f"{len(over)} question(s) over {CAP:,} bytes of prose")
        return 0
    over = [(size(root / q), q) for q in changed(root) if size(root / q) > CAP]
    for n, q in over:
        print(f"question-size: {q} is {n:,} bytes of prose, over the {CAP:,} cap - split it along its topics (a finding stays "
              "with its decision; each part its own question and heading; the joins point, they do not restate). "
              "Why and how: docs/research-record-rules.md, 'A question has a size'.", file=sys.stderr)
    return 1 if over else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
