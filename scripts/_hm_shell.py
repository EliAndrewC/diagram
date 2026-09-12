#!/usr/bin/env python3
"""What a Bash command would do WRONG, decided before it runs (feature 236, the GM's items 2 and 3).

A leaf beside `_hm_shape`, `_hm_escape` and `_hm_make` (feature 172's shape): a guard depends on the
module it uses, so a change here re-runs one suite rather than twenty-one. Everything in it is pure
apart from one `bash -n` parse and one optional read of a `-F <file>` message.

FOUR RULES, each measured before it was written (`specs/236-catch-mistakes-early-and-cheaply/`):

  1. IT DOES NOT PARSE (FR-004). The tool runs a command through `eval`, one line at a time, so the
     parse must use the options the tool's shell can have enabled - `bash -O extglob -n`. Plain
     `bash -n` refuses `shopt -s extglob` on one line and `!(x)` on the next, which the tool RUNS:
     a guard that fires on correct work is one that gets routed around. Replayed over the 238 real
     commands of `research.md` R6: 2 refused, both of which had also failed at run time, 0 false
     positives.

  2. A BACKTICK THAT WOULD RUN (FR-004a). Valid syntax, so the parse cannot see it; the walk lives in
     `_hm_shape.executing_backticks` and is shared with the Makefile recipe-comment guard. Measured
     over the 60 most recent transcripts: not one executing span in the record was a deliberate
     substitution - every one was a markdown code span written into prose, and several would have
     done real damage (`cd /diagram`, `git init --bare`). This project writes substitution as
     `$(...)`, so the refusal costs nothing and names that form.

  3. `-m` FOR A MESSAGE THAT NEEDS A HEREDOC (FR-005). A refusal rather than a rewrite: the failing
     class parses CLEANLY into the WRONG message - an inner quote closes the string early - so any
     rewrite would faithfully preserve the wrong message.

  4. A CO-AUTHOR ADDRESS THAT IS NOT OURS (FR-006). The instance on record put a placeholder address
     into a trailer through an `||` fallback and it went to main. The KEY is matched
     case-insensitively (git trailer keys are), the ADDRESS is what is checked rather than the
     display name (which carries the model and changes), and every route a trailer can arrive by is
     read: `-m`, `-F -`, `-F <file>` and `--trailer`.
"""

from __future__ import annotations

import json
import pathlib
import re
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from _hm_shape import _strip_heredocs, executing_backticks  # noqa: E402

CO_AUTHOR_ADDRESS = "noreply@anthropic.com"
_SEPARATORS = (";", "&", "|", "\n")


class Word:
    """One shell word, kept with the raw text it was written as.

    The RAW form is what the `-m` rule needs: `-m "a "b" c"` parses into a perfectly good single
    word, which is precisely the failure - the message the session meant is not the message git
    receives. Only the raw text shows the two quoted chunks it was assembled from.
    """

    def __init__(self, value: str, raw: str, chunks: int, quoted: bool) -> None:
        self.value, self.raw, self.chunks, self.quoted = value, raw, chunks, quoted

    def __repr__(self) -> str:  # pragma: no cover - debugging aid
        return f"Word({self.value!r})"


def segments(cmd: str) -> list[list[Word]]:
    """`cmd` split at unquoted separators into segments of words, heredoc bodies left in place."""
    out: list[list[Word]] = [[]]
    value, raw, chunks, quoted, started = "", "", 0, False, False
    i, n = 0, len(cmd)

    def flush() -> None:
        nonlocal value, raw, chunks, quoted, started
        if started:
            out[-1].append(Word(value, raw, chunks, quoted))
        value, raw, chunks, quoted, started = "", "", 0, False, False

    while i < n:
        ch = cmd[i]
        if ch in " \t":
            flush()
            i += 1
            continue
        if ch in _SEPARATORS:
            flush()
            if out[-1]:
                out.append([])
            i += 1
            continue
        started = True
        if ch == "\\" and i + 1 < n:
            value += cmd[i + 1]
            raw += cmd[i:i + 2]
            i += 2
            continue
        if ch == "'":
            j = cmd.find("'", i + 1)
            j = n if j < 0 else j
            value += cmd[i + 1:j]
            raw += cmd[i:j + 1]
            chunks += 1
            quoted = True
            i = j + 1
            continue
        if ch == '"':
            j, buf = i + 1, ""
            while j < n and cmd[j] != '"':
                if cmd[j] == "\\" and j + 1 < n:
                    buf += cmd[j + 1]        # `\"` inside a double-quoted string IS a quote character
                    j += 2
                    continue
                buf += cmd[j]
                j += 1
            value += buf
            raw += cmd[i:min(j + 1, n)]
            chunks += 1
            quoted = True
            i = j + 1
            continue
        value += ch
        raw += ch
        i += 1
    flush()
    return [s for s in out if s]


def parse_error(cmd: str) -> str | None:
    """The parser's own message when bash cannot parse `cmd`, or None.

    `-O extglob` is not decoration: it is the difference between the parse the tool performs and a
    parse that refuses correct work (`research.md` R6).
    """
    try:
        proc = subprocess.run(["bash", "-O", "extglob", "-n", "-c", cmd],
                              capture_output=True, text=True, timeout=10)
    except Exception:                        # a guard never takes the session down with it
        return None
    if proc.returncode == 0:
        return None
    return (proc.stderr or "").strip() or f"bash refused to parse the command (exit {proc.returncode})"


def backtick_problem(cmd: str) -> str | None:
    """The refusal for a backtick span bash would execute, or None."""
    spans = executing_backticks(cmd)
    if not spans:
        return None
    return ("a backtick span that bash will EXECUTE: " + ", ".join(spans[:3])
            + ("" if len(spans) <= 3 else f" (and {len(spans) - 3} more)"))


def _is_git_commit(seg: list[Word]) -> bool:
    words = [w.value for w in seg if "=" not in w.value.split(" ")[0] or not re.match(r"^\w+=", w.value)]
    if not words:
        return False
    head = [w for w in words if w not in ("sudo", "time", "env")]
    if not head or pathlib.Path(head[0]).name != "git":
        return False
    for w in head[1:]:
        if w.startswith("-"):
            continue
        return w == "commit"
    return False


def _dash_m_words(seg: list[Word]) -> list[Word]:
    out, take_next = [], False
    for w in seg:
        if take_next:
            out.append(w)
            take_next = False
            continue
        if w.value in ("-m", "--message"):
            take_next = True
        elif w.value.startswith("--message="):
            out.append(Word(w.value.split("=", 1)[1], w.raw.split("=", 1)[-1], w.chunks, w.quoted))
        elif re.match(r"^-[a-zA-Z]*m.", w.value) and not w.value.startswith("--"):
            out.append(Word(w.value.split("m", 1)[1], w.raw, w.chunks, w.quoted))
    return out


def commit_dash_m_problem(cmd: str) -> str | None:
    """The refusal for a `git commit -m` that should be a heredoc, or None.

    HEREDOC BODIES ARE PAYLOAD, never commands - the mention-versus-invocation rule this repository
    has learned seven times. Without stripping them first, a `python3 - <<'PY'` whose Python happens
    to contain quotes tokenizes as shell text and fifteen of the corpus's 238 commands were refused
    for a `-m` nobody wrote (measured on the replay the moment it first ran).
    """
    for seg in segments(_strip_heredocs(cmd)):
        if not _is_git_commit(seg):
            continue
        ms = _dash_m_words(seg)
        if len(ms) > 1:
            return f"{len(ms)} separate -m messages"
        for w in ms:
            if "\n" in w.value:
                return "a newline inside a -m message"
            if '"' in w.value:
                return "a double quote inside a -m message"
            if w.chunks > 1:
                return ("a -m message assembled from several quoted pieces (" + w.raw[:60]
                        + ") - the shell closes the first quote early, so git receives a message "
                          "nobody wrote")
    return None


def _messages(cmd: str, cwd: str = "") -> list[str]:
    """Every text that could carry a trailer: `-m`, `--trailer`, `-F -` (the heredoc) and `-F <file>`."""
    texts: list[str] = []
    for seg in segments(_strip_heredocs(cmd)):   # bodies are read below, from the raw command
        if not _is_git_commit(seg):
            continue
        texts += [w.value for w in _dash_m_words(seg)]
        take = ""
        for w in seg:
            if take == "trailer":
                texts.append(w.value)
                take = ""
                continue
            if take == "file":
                take = ""
                if w.value == "-":
                    texts += re.findall(r"<<-?\s*['\"]?\w+['\"]?\n(.*?)\n\s*\w+\s*$", cmd, re.S | re.M)
                    continue
                p = pathlib.Path(cwd or ".") / w.value if not w.value.startswith("/") else pathlib.Path(w.value)
                try:
                    if p.is_file() and p.stat().st_size < 200_000:
                        texts.append(p.read_text(errors="replace"))
                except OSError:
                    pass
                continue
            if w.value == "--trailer":
                take = "trailer"
            elif w.value.startswith("--trailer="):
                texts.append(w.value.split("=", 1)[1])
            elif w.value in ("-F", "--file"):
                take = "file"
            elif w.value.startswith("--file="):
                take = "file"
                texts.append("")
                seg = seg  # noqa: PLW0127 - keep the loop simple; --file=<path> is read below
                p = pathlib.Path(w.value.split("=", 1)[1])
                try:
                    if p.is_file() and p.stat().st_size < 200_000:
                        texts.append(p.read_text(errors="replace"))
                except OSError:
                    pass
                take = ""
    return texts


_CO_AUTHOR = re.compile(r"^\s*co-authored-by\s*:\s*(.+?)\s*$", re.I | re.M)
_ADDRESS = re.compile(r"<([^>]+)>")


def coauthor_problem(cmd: str, cwd: str = "") -> str | None:
    """The refusal for a co-author trailer carrying somebody else's address, or None."""
    for text in _messages(cmd, cwd):
        for line in _CO_AUTHOR.findall(text):
            m = _ADDRESS.search(line)
            address = (m.group(1) if m else line).strip().lower()
            if address != CO_AUTHOR_ADDRESS:
                return f"a co-author trailer addressed to {address!r}"
    return None


# (rule slug, refusal headline, the compliant form) - the order the guard applies them in
def verdict(cmd: str, cwd: str = "") -> tuple[str, str] | None:
    """(rule, message) for the first rule `cmd` breaks, or None."""
    err = parse_error(cmd)
    if err:
        return ("parse", "the command does not parse:\n\n" + err + "\n\nBash refuses it before it "
                "runs, so this round trip buys nothing. Fix the quoting - a message or a document "
                "goes in a quoted heredoc (`<<'EOF'`), where nothing in it is shell grammar.")
    bad = backtick_problem(cmd)
    if bad:
        return ("executing-backtick", bad + ".\n\nInside double quotes, and in an unquoted `<<EOF` "
                "body, backticks are COMMAND SUBSTITUTION: bash runs what is between them and puts "
                "the output in their place, so the text you meant to write is corrupted and "
                "something runs that you did not ask for. Write a code span in single quotes or in "
                "a quoted heredoc (`<<'EOF'`); write a deliberate substitution as `$(...)`, which "
                "is what this project uses everywhere.")
    bad = commit_dash_m_problem(cmd)
    if bad:
        return ("commit-dash-m", bad + ".\n\nUse the heredoc form, whose body is literal:\n\n"
                "    git commit -F - <<'EOF'\n    <your message, quotes and newlines and all>\n"
                "    EOF\n\nThe delimiter is QUOTED (`<<'EOF'`, not `<<EOF`) so nothing in the "
                "message is expanded or executed. This is a refusal rather than a rewrite because "
                "the broken form parses cleanly into the WRONG message.")
    bad = coauthor_problem(cmd, cwd)
    if bad:
        return ("coauthor-address", bad + f".\n\nThe co-author address is <{CO_AUTHOR_ADDRESS}>. "
                "A placeholder address reached main once through an `||` fallback and the history "
                "cannot be rewritten to take it out. Other trailers (`Claude-Session:`) are fine.")
    return None


def selftest() -> None:
    assert parse_error("echo hi") is None
    assert parse_error("if true; then") is not None, "an unfinished construct must be refused"
    assert parse_error("shopt -s extglob\nls !(x)") is None, "the tool's own options, not bash's defaults"
    assert backtick_problem('echo "use `make quick` first"')
    assert backtick_problem("cat <<EOF\nsee `make done`\nEOF")
    assert backtick_problem("echo 'use `make quick`'") is None
    assert backtick_problem("cat <<'EOF'\nsee `make done`\nEOF") is None
    assert backtick_problem("x=$(date)") is None
    assert commit_dash_m_problem('git commit -m "a plain message"') is None
    assert commit_dash_m_problem("git commit -am 'a plain message'") is None
    assert commit_dash_m_problem('git commit -m "the pond\'s own "center" thing"')
    assert commit_dash_m_problem('git commit -m "one" -m "two"')
    assert commit_dash_m_problem('git commit -m "line one\nline two"')
    assert commit_dash_m_problem('echo "one" "two"') is None, "only git commit is judged"
    assert commit_dash_m_problem('git log --grep "a "b" c"') is None, "only commit, not every git verb"
    ok = "git commit -F - <<'EOF'\n236: x\n\nCo-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\nEOF"
    assert coauthor_problem(ok) is None
    assert coauthor_problem(ok.replace("noreply@", "duplicate@"))
    assert coauthor_problem("git commit -m 'x' --trailer 'Co-authored-by: Someone <other@example.com>'")
    assert coauthor_problem("git commit -F - <<'EOF'\nx\n\nClaude-Session: https://example\nEOF") is None
    assert verdict("echo ok") is None
    print("_hm_shell selftest ok")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
        raise SystemExit(0)
    RAW = sys.stdin.read()
    try:
        PAYLOAD = json.loads(RAW)
    except Exception:
        PAYLOAD = {}
    TI = PAYLOAD.get("tool_input", {}) or {}
    OUT = verdict(TI.get("command", "") or "", PAYLOAD.get("cwd", "") or "")
    if OUT:
        print(OUT[0])
        print(OUT[1])
