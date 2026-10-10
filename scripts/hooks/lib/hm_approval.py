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


def _typed(rec: dict) -> bool:
    if rec.get("isMeta") or rec.get("isSidechain") or rec.get("isCompactSummary"):
        return False
    origin = (rec.get("origin") or {}).get("kind")
    if origin or rec.get("promptSource"):
        return origin == "human" or rec.get("promptSource") == "typed"
    return not str(rec.get("entrypoint") or "").startswith("sdk")


def gm_messages(transcript: str) -> list[str]:
    """Every message the GM wrote in this session: typed prompts, and answers given to AskUserQuestion."""
    out: list[str] = []
    asked: set[str] = set()
    try:
        with open(transcript, encoding="utf-8", errors="replace") as fh:
            lines = fh.read().splitlines()
    except (OSError, TypeError):
        return out
    for line in lines:
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        content = (rec.get("message") or {}).get("content")
        att = rec.get("attachment") or {}
        if rec.get("type") == "attachment" and att.get("type") == "queued_command":
            # a message the GM sent while the session was working (plan review 2026-10-10: 41 of 73 such messages in
            # the last 40 transcripts reached no `user` record); task notifications, peers and auto-continuations
            # carry other origins
            if (att.get("origin") or {}).get("kind") == "human" and not att.get("isMeta") and isinstance(att.get("prompt"), str):
                out.append(att["prompt"])
            continue
        if rec.get("type") == "assistant":
            for c in content if isinstance(content, list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_use" and c.get("name") == "AskUserQuestion":
                    asked.add(c.get("id") or "")
        elif rec.get("type") == "user":
            if isinstance(content, str) and _typed(rec):
                out.append(content)
            for c in content if isinstance(content, list) else []:
                if isinstance(c, dict) and c.get("type") == "tool_result" and c.get("tool_use_id") in asked:
                    body = c.get("content")
                    text = body if isinstance(body, str) else " ".join(str(p.get("text", "")) for p in body or [] if isinstance(p, dict))
                    # an ANSWER, not the harness's note that the GM declined to answer
                    if (rec.get("toolUseResult") or {}).get("answers") if isinstance(rec.get("toolUseResult"), dict) else ANSWERED.match(text):
                        out.append(text)
    return [norm(m) for m in out]


def problem(text: str, messages: list[str]) -> str:
    """"" when the spec's approval stands, else `no-line`, `short` or `not-found`."""
    bad = form_problem(text)
    if bad:
        return bad
    ok = [q for q in quotes(text) if len(norm(q).split()) >= MIN_WORDS]
    return "" if any(norm(q) in m for q in ok for m in messages) else "not-found"


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True, check=False)


def is_new(top: str, rel: str) -> bool:
    """Is this `specs/NNN-slug/spec.md` a new feature, rather than one HEAD already holds (at this path or renumbered)?"""
    if _git(top, "cat-file", "-e", f"HEAD:{rel}").returncode == 0:
        return False
    # GUARD_EDIT_OK: a MERGE brings main's features in - feature 370's sync-in merged 377 itself and the guard refused the
    # merge commit; a spec the merge's other side already holds was filed (and approved) where it was written, not here
    if _git(top, "cat-file", "-e", f"MERGE_HEAD:{rel}").returncode == 0:
        return False
    renamed = _git(top, "diff", "--cached", "-M", "--name-status").stdout.splitlines()
    if any(ln.startswith("R") and ln.split("\t")[-1] == rel for ln in renamed):
        return False
    # a renumber not yet staged as a rename: HEAD's spec of the same slug has LEFT (gone from the working tree, or its
    # deletion staged). A same-slug spec beside one that is still there is a copy, and new (plan review 2026-10-10).
    slug = SPEC.search(rel).group(2)  # type: ignore[union-attr]
    held = _git(top, "ls-tree", "--name-only", "HEAD", "specs/").stdout.split()
    staged_gone = set(_git(top, "diff", "--cached", "--name-only", "--diff-filter=D").stdout.split())
    for d in held:
        old = f"{d}/spec.md"
        if old != rel and re.fullmatch(rf"specs/\d{{3,}}-{re.escape(slug)}", d) and (not os.path.exists(os.path.join(top, old)) or old in staged_gone):
            return False
    return True


def _text(top: str, rel: str, worktree: bool) -> str:
    """The file as the command would commit it: the working tree's for `add` and `commit -a`, else the index's."""
    if worktree:
        try:
            with open(os.path.join(top, rel), encoding="utf-8", errors="replace") as fh:
                return fh.read()
        except OSError:
            pass
    return _git(top, "show", f":{rel}").stdout


def judge(cmd: str, cwd: str, transcript: str) -> list[tuple[str, str]]:
    """(problem, path) for every new feature's spec.md this command would stage without a standing approval."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from hm_conflict import staged_by  # noqa: PLC0415 - the conflict guard's own parser of what a command stages

    out: list[tuple[str, str]] = []
    messages: list[str] | None = None
    # `add` and `commit -a` take the working tree's file; a plain `commit` takes what is staged
    # (the git SUBCOMMAND, not the word: `specs/380-add-thing/` names no add - plan review round 2)
    git_ = r"\bgit(?:\s+-[Cc]\s+\S+)*\s+"
    worktree = bool(re.search(git_ + r"add\b", cmd) or re.search(git_ + r"commit\b[^;&|]*\s(?:-[a-zA-Z]*a[a-zA-Z]*|--all)(?=\s|$)", cmd))
    for path in dict.fromkeys(os.path.normpath(p) for p in staged_by(cmd, cwd)):
        m = SPEC.search(path)
        if not m or int(m.group(1)) < FIRST:
            continue
        top = _git(os.path.dirname(path) if os.path.isdir(os.path.dirname(path)) else cwd, "rev-parse", "--show-toplevel").stdout.strip()
        if not top:
            continue
        rel = os.path.relpath(os.path.abspath(path), top)
        if not is_new(top, rel):
            continue
        if messages is None:
            messages = gm_messages(transcript)
        bad = problem(_text(top, rel, worktree), messages)
        if bad:
            out.append((bad, rel))
    return out


def main(argv: list[str]) -> int:
    if argv[:1] != ["judge"]:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    for bad, rel in judge(cmd, os.environ.get("FA_CWD") or os.getcwd(), payload.get("transcript_path") or ""):
        print(f"{bad}\t{rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
