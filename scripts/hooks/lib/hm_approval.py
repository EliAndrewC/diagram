#!/usr/bin/env python3
"""The decider for `feature-approval-hooks.sh`, and the ONE definition of a feature's approval line (feature 377).

WHY (the GM, 2026-10-10, specs/377-feature-filing-needs-approval/request.md): *"spec kit features should not be filed
without my explicit approval ... unless it has like the line that quotes my approval to file the feature, which is like
formatted in a specific way ... can't be committed at all, like not even to a branch"*. Sessions had been filing
features on their own judgment and saying so, at most, somewhere in two days of output.

THE LINE, in the `spec.md` of every feature numbered FIRST or above, on a line of its own:

    **Approved**: the GM, YYYY-MM-DD, "<the GM's words, verbatim>"

The quote is at least MIN_WORDS words, so a bare "yes" from anywhere in the session approves nothing.

WHAT IS CHECKED, at a session's `git add` / `git commit` that would stage a NEW such `spec.md`: the line is there, and its
quote appears in a message the GM wrote in the session's own transcript - a typed prompt, or the GM's answer to an
AskUserQuestion (whose result holds `"<question>"="<answer>"`, so a short picked answer is quoted with its question).
A typed prompt is told from everything else that is written as a `user` record by its `origin.kind` (`human`) or
`promptSource` (`typed`): measured on 2026-10-10, a headless page session's prompt is `promptSource: sdk`, and the
harness's own notices are `isMeta`. A record carrying neither field (an older Claude Code) counts unless its
`entrypoint` is an SDK one. Whitespace and curly quotes are normalized, nothing else.

A message the GM sent while the session was working is a `queued_command` attachment with `origin.kind` `human`, and
counts too. An AskUserQuestion result counts only when it is an ANSWER (its `answers`, or the answered preamble).

NEW means: absent from HEAD at that path, not the target of a staged rename, and not a renumber - a `specs/*-<same
slug>/spec.md` in HEAD that has LEFT (gone from the working tree, or its deletion staged). A same-slug spec beside one
still there is a copy, and new. A feature below FIRST is never checked (the GM: "only be
with new features um, going forward"). There is no escape: the GM's approval is the way through.

THE STANDING APPROVAL (GM 2026-10-18: *"you should treat features that I have asked to be filed as automatic approval, and
therefore you should not ask in the future"*): a feature whose `request.md` is an issue gm-assistant filed here for the GM
(`# Request: EliAndrewC/diagram#N` and a `**[gm-assistant]**` body) may quote those words instead. Without it, a session
woken by its inbox had no line both `CLAUDE.md` and this guard would accept (feature 428's spec review, 2026-10-26).

spec-lint's check 6 (the push backstop) imports FIRST, LINE and `form_problem` from here, so the commit and the push
cannot disagree about the form.

    hm_approval.py judge < <hook payload>   -> one `<problem>\t<path>` line per refused spec (nothing = pass)
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys

FIRST = 377
MIN_WORDS = 3
LINE = re.compile(r'^\*\*Approved\*\*: the GM, (\d{4}-\d{2}-\d{2}), "(.+)"[ \t]*$', re.M)
FORM = '**Approved**: the GM, YYYY-MM-DD, "<the GM\'s words, verbatim>"'
SPEC = re.compile(r"(?:^|/)specs/(\d{3,})-([a-z0-9][a-z0-9-]*)/spec\.md$")
ANSWERED = re.compile(r"\s*(?:Your questions have been answered|User has answered your questions)\b")
STANDING = "you should treat features that I have asked to be filed as automatic approval"
FILED_FOR_GM = re.compile(r"^# Request: EliAndrewC/diagram#\d+", re.M)
_CURLY = str.maketrans({"‘": "'", "’": "'", "“": '"', "”": '"'})


def norm(text: str) -> str:
    return " ".join(text.translate(_CURLY).split())


def quotes(text: str) -> list[str]:
    """The quotes of every approval line in a spec's text."""
    return [m.group(2) for m in LINE.finditer(text)]


def form_problem(text: str) -> str:
    """"" when the text holds a well-formed approval line, else `no-line` or `short`."""
    found = quotes(text)
    if not found:
        return "no-line"
    return "" if any(len(norm(q).split()) >= MIN_WORDS for q in found) else "short"


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=False)


#: `make speckit-todo`'s states that hold no unhandled work: closed, or done with only the GM's review left
SETTLED = ("closed", "done - GM review pending")
# an INVOCATION, never a mention (2026-10-10: a command writing JSON that named it was refused): the script at the start of a
# command segment, after any `VAR=value` prefixes, an optional `bash`, and any path
PUSH = re.compile(r"(?:^|[;&|(]\s*)(?:[A-Za-z_]\w*=\S*\s+)*(?:bash\s+)?[\w./$-]*sync-with-main\.sh\s+(?:done|push)\b", re.M)


def _todo():  # noqa: ANN202 - scripts/speckit-todo.py, imported by path (its name has a hyphen)
    import importlib.util  # noqa: PLC0415

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "speckit-todo.py")
    spec = importlib.util.spec_from_file_location("speckit_todo", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    sys.modules["speckit_todo"] = mod
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


_OPEN_BOX = re.compile(r"^\s*- \[ \] (.*)$", re.M)
_TASK_ID = re.compile(r"^(T\d+[a-z]?)\b")


def open_tasks(text: str) -> set[str]:
    """Each unticked task, keyed by its id (`T07`) where it has one, else by its normalized line (plan review of
    amendment 1: a COUNT misses a push that ticks a leftover box and adds a new one - 17 closed features hold open boxes)."""
    out = set()
    for m in _OPEN_BOX.finditer(text):
        line = norm(m.group(1))
        tid = _TASK_ID.match(line)
        out.add(tid.group(1) if tid else line)
    return out


def _state_at(top: str, rev: str, d: str, todo, vocab, tmp: str) -> tuple[str, str, set[str], bool]:  # noqa: ANN001
    """(make speckit-todo's state, spec.md text, its unticked tasks, closed by its status line) of `specs/<d>` at `rev`;
    ("", "", set(), False) where it did not exist."""
    names = _git(top, "ls-tree", "-r", "--name-only", rev, "--", f"specs/{d}").stdout.split()
    if not names:
        return "", "", set(), False
    for name in names:
        dest = os.path.join(tmp, rev, name)
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        with open(dest, "wb") as fh:
            fh.write(subprocess.run(["git", "-C", top, "show", f"{rev}:{name}"], capture_output=True, check=False).stdout)
    here = os.path.join(tmp, rev, "specs", d)
    spec = os.path.join(here, "spec.md")
    text = open(spec, encoding="utf-8", errors="replace").read() if os.path.exists(spec) else ""  # noqa: SIM115
    tasks = os.path.join(here, "tasks.md")
    unticked = open_tasks(open(tasks, encoding="utf-8", errors="replace").read()) if os.path.exists(tasks) else set()  # noqa: SIM115
    import pathlib  # noqa: PLC0415

    return todo.feature(pathlib.Path(here), vocab).state, text, unticked, todo.closed_by_status(pathlib.Path(here))
