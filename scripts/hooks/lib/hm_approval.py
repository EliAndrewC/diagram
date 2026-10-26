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


def standing(spec_text: str, request_text: str) -> bool:
    """Does a spec of an issue gm-assistant filed for the GM quote his standing approval (2026-10-18)?"""
    filed = bool(FILED_FOR_GM.search(request_text)) and "**[gm-assistant]**" in request_text
    return filed and any(STANDING in norm(q) for q in quotes(spec_text))


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
        text = _text(top, rel, worktree)
        bad = problem(text, messages)
        if bad == "not-found" and standing(text, _text(top, os.path.join(os.path.dirname(rel), "request.md"), worktree)):
            bad = ""
        if bad:
            out.append((bad, rel))
    return out


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


def reopened(top: str, transcript: str) -> list[tuple[str, str]]:
    """Amendment 1 (the GM, 2026-10-10: "the number of features with open work that is not handled [must not] increase
    without my knowledge"): every feature CLOSED at the push's base and OPEN at HEAD, unless HEAD's spec.md adds an
    approval line whose quote the GM wrote in this session. Reopened, worked and closed again within the delta passes."""
    import pathlib  # noqa: PLC0415
    import tempfile  # noqa: PLC0415

    base = _git(top, "merge-base", "HEAD", "origin/main").stdout.strip()
    if not base:
        return []
    dirs = sorted({n.split("/")[1] for n in _git(top, "diff", "--name-only", base, "HEAD", "--", "specs/").stdout.split() if n.count("/") >= 2})
    if not dirs:
        return []
    todo = _todo()
    vocab = todo.vocabulary(pathlib.Path(top))
    out: list[tuple[str, str]] = []
    messages: list[str] | None = None
    with tempfile.TemporaryDirectory() as tmp:
        for d in dirs:
            was, before, open_before, _ = _state_at(top, base, d, todo, vocab, tmp)
            now, after, open_after, status_closed = _state_at(top, "HEAD", d, todo, vocab, tmp)
            reopen = was in SETTLED and bool(now) and now not in SETTLED
            # FR-012: an unticked task added under a status line that still says Done (speckit-todo reads it closed)
            # GUARD_EDIT_OK: feature 375 amendment 8 - the box `make accept` writes for the GM (`GM review (make gm-reviewed
            # F=NNN) [lands-open]`) is no hidden work: `make gm-review` holds it, and every feature with a row for the GM
            # lands with it open (343, 352, 374, 378) - it refused 375's landing after its own accept row (2026-10-12)
            added_open = {t for t in open_after - open_before if not t.startswith("GM review (make gm-reviewed F=")}
            hidden = bool(now) and status_closed and bool(added_open)  # a task open now that was not
            if not (reopen or hidden):
                continue
            added = [q for q in quotes(after) if q not in quotes(before) and len(norm(q).split()) >= MIN_WORDS]
            if messages is None:
                messages = gm_messages(transcript)
            if not any(norm(q) in m for q in added for m in messages):
                kind = "reopened" if reopen else "hidden-open"
                out.append((kind if not added else kind + "-not-found", f"specs/{d}/spec.md"))
    return out


def push_repo(cmd: str, cwd: str) -> str:
    """The repository a `sync-with-main.sh done|push` command runs in: the last `cd` before it, else the cwd."""
    before = cmd[: PUSH.search(cmd).start()]  # type: ignore[union-attr]
    cds = re.findall(r"(?:^|[;&|]\s*|\s)cd\s+(['\"]?)([^\s;&|'\"]+)\1", before)
    where = cds[-1][1] if cds else cwd
    where = where if os.path.isabs(where) else os.path.join(cwd, where)
    return _git(where, "rev-parse", "--show-toplevel").stdout.strip()


def main(argv: list[str]) -> int:
    if argv[:1] != ["judge"]:
        print(__doc__.strip().splitlines()[-1].strip(), file=sys.stderr)
        return 2
    try:
        payload = json.loads(sys.stdin.read() or "{}")
    except json.JSONDecodeError:
        return 0
    cmd = str((payload.get("tool_input") or {}).get("command") or "")
    cwd, transcript = os.environ.get("FA_CWD") or os.getcwd(), payload.get("transcript_path") or ""
    found = judge(cmd, cwd, transcript)
    if PUSH.search(cmd):
        top = push_repo(cmd, cwd)
        found += reopened(top, transcript) if top else []
    for bad, rel in found:
        print(f"{bad}\t{rel}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
