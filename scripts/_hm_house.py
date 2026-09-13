#!/usr/bin/env python3
"""What the house-style hook may CORRECT in a Bash command, and what it must only name.

GUARD_EDIT_OK: feature 236, amendment 2 (the GM 2026-09-12, on spec D2): *"I think that we could exempt
that sed shape and otherwise correct in the hook rather than warning. So, basically, we should warn when
it is the sed shape, and for other shapes just correct it."*

An Edit carries text a session is WRITING. A Bash command also carries text it is only NAMING - the word
it searches for, the old side of the fix it applies, the file it reads - and correcting a named word does
not fix the command, it breaks it: `grep centre` corrected searches for the other word, and
`sed -i s/centre/center/` corrected replaces a word with itself. So the command is read in ranges, and
each range with a British word in it is one of three kinds:

    CORRECTED  prose the command writes - a heredoc body, a commit message, an echo. The default.
    WARNED     the sed shape (the GM's ruling), and a command that carries BOTH spellings of a word,
               which is the same shape written another way: a replacement pair in a Python sweep, an
               `_patch.py` anchor and its replacement. The command is left exactly as typed.
    LEFT ALONE a MENTION: a code span or a quotation (the rules the Edit path already keeps), a search
               - a searcher's segment wherever it stands, a regex alternation `a|b`, a character class -
               and a path token, which names a file that exists under that name.

Every rule was taken from the replay of the real commands this hook would have rewritten
(`specs/236-catch-mistakes-early-and-cheaply/measure_bash_corrections.py`, `research.md` R10). The word
list and the replacement table are the hook's own and are passed in, so this file carries no copy of
either - the hook corrects text as it is written, and a copy here would be corrected on the way in.
"""

from __future__ import annotations

import os
import re
from collections.abc import Callable

_SEARCHERS = ("grep", "egrep", "fgrep", "rg", "ack", "ag", "ripgrep")
_DASHES = "\u2014\u2013"

# What may stand in front of a segment's real command: a negation, a grouping, a substitution opener,
# a shell keyword, an assignment, and the wrappers that run another program.
_LEAD = re.compile(
    r"^(?:\s+|!|\(|\{|\$\(|\x60|(?:then|do|else|elif|if|while|until|time|sudo|command|env|nohup|git)\b"
    r"|[A-Za-z_][A-Za-z0-9_]*=\S*|xargs(?:\s+-\S+)*\b)+"
)
# a run of two or more alternatives joined by `|` or `\|`, as a search pattern writes them
_ALTERNATION = re.compile(r"[\w\\.?*+-]+(?:\\?\|[\w\\.?*+-]+)+")
# a character class, or a `$'...'` string, carrying a dash - a dash being LOOKED FOR
_DASH_CLASS = re.compile(r"\[[^\]\n]*[%s][^\]\n]*\]|\$'[^'\n]*[%s][^'\n]*'" % (_DASHES, _DASHES))
# A QUOTED WORD IS A TOKEN, NOT PROSE. A string whose whole content is one word is the same thing a
# backtick span is in prose - the word NAMED rather than used: the entries of a sweep's word list
# (a set of quoted spellings), a search argument, a dict key. Correcting those rewrote the word list
# of every house-style sweep in the record, which is the tool that finds the violations.
_QUOTED_TOKEN = re.compile(r"""(['"])[\w\\.?*+()\[\]{}|-]{1,40}\1""")
# a one-character string holding a dash: a dash named as a token, as in `.replace("<dash>", " - ")`
_DASH_LITERAL = re.compile(r"(['\"])[%s]\1" % _DASHES)
# a path: something with a slash, or a file name with an extension
_PATH = re.compile(
    r"[\w.~$-]*/[\w./~$-]+|[\w-]+\.(?:md|py|sh|html|json|jsonl|txt|toml|js|css|ya?ml|csv)\b"
)
_SUBSTITUTION_SEARCH = re.compile(r"\$\(\s*(?:git\s+)?(?:%s)\b[^)]*\)" % "|".join(_SEARCHERS))


def _segments(cmd: str) -> list[tuple[int, int]]:
    """(start, end) of each piece of a command between `;`, `&&`, `||`, `|` and newlines."""
    out, start = [], 0
    for m in re.finditer(r"&&|\|\||;|\||\n", cmd):
        out.append((start, m.start()))
        start = m.end()
    out.append((start, len(cmd)))
    return out


def _head(text: str) -> str:
    """The program a segment runs, past whatever stands in front of it."""
    rest = text[_LEAD.match(text).end():] if _LEAD.match(text) else text.lstrip()
    word = rest.split(None, 1)[0] if rest.split() else ""
    return os.path.basename(word)


def held_ranges(cmd: str) -> list[tuple[int, int, str]]:
    """(start, end, kind) for every range that must not be corrected: kind `warn` or `mention`."""
    held = []
    for a, b in _segments(cmd):
        seg = cmd[a:b]
        head = _head(seg)
        if head == "sed" or re.search(r"-exec\s+sed\b", seg):
            held.append((a, b, "warn"))          # the GM's named shape
        elif head in _SEARCHERS:
            held.append((a, b, "mention"))
    for pattern in (_SUBSTITUTION_SEARCH, _ALTERNATION, _DASH_CLASS, _DASH_LITERAL, _PATH, _QUOTED_TOKEN):
        held += [(m.start(), m.end(), "mention") for m in pattern.finditer(cmd)]
    return held


def write_targets(cmd: str, cwd: str | None = None) -> list[str | None]:
    """The paths a command WRITES - a redirect's target or a `tee` argument (GUARD_EDIT_OK).

    The exemption for a path outside the project (`/tmp`, the session state directory) has to be
    decided by where the write LANDS. Reading every path the command mentions gets it wrong in both
    directions: a heredoc writing the auto-memory index mentions relative file names in its own body,
    and a command that reads the memory file and writes a project file in the same breath mentions one
    of each. Both cases are real - the amendment review found the second, its fix produced the first.

    THE WALK IS `_hm_tree`'s, not a second one. The first version here read redirect targets out of the
    raw text, and the amendment review measured what that costs over the real window: 7 writes outside
    the project newly corrected and 4 project writes newly silenced. Every one was a shape `_hm_tree`
    already handles for the main-tree guard - a target behind a variable assigned in the same command
    (`M=<path>; cat >> $M`, this project's own memory-write shape), a `> ` line inside a heredoc BODY
    read as a redirect, and `git commit`, whose write lands in the repository rather than in a file.

    A `None` in the list is a write whose destination cannot be known, and it is never outside: an
    interpreter reading its program from a heredoc can write anywhere, which is how a `write_text` into
    the pool sat beside a `> /tmp/gate.log` redirect and took the exemption.
    """
    try:
        from _hm_tree import walk
    except Exception:                       # a guard never takes the session down with it
        return []
    home = os.path.expanduser("~")
    return [t["path"] for t in walk(cmd, cwd, home, home)["targets"]]


def plan(
    cmd: str,
    pairs: dict[str, str],
    spans: re.Pattern[str],
    correct_plain: Callable[[str], tuple[str, list[str]]],
) -> tuple[str, list[str], list[str]]:
    """(the command to run, the corrections made, the words warned on and left as typed).

    `pairs` is the hook's replacement table, `spans` its code-span-and-quotation pattern, and
    `correct_plain` its correction of plain text - all three passed in so there is one of each.
    """
    words = re.compile(r"\b(%s)\b|[%s]" % ("|".join(map(re.escape, pairs)), _DASHES), re.I)
    if not words.search(cmd):
        return cmd, [], []
    # BOTH SPELLINGS IN ONE COMMAND IS A FIX, however it is written - the sed shape's reason, which is
    # the GM's: a correction would turn the fix into a replacement of a word with itself.
    both = sorted(w for w, a in pairs.items()
                  if re.search(r"\b%s\b" % re.escape(w), cmd, re.I) and re.search(r"\b%s\b" % re.escape(a), cmd, re.I))
    if both:
        return cmd, [], both
    held = _merged([(m.start(), m.end(), "mention") for m in spans.finditer(cmd)] + held_ranges(cmd))
    warned, out, notes, last = [], [], [], 0
    for a, b, kind in held + [(len(cmd), len(cmd), "mention")]:
        piece = cmd[last:a]
        # THE HOOK RUNS ON EVERY BASH COMMAND, so the whole-table correction is only reached for a
        # piece that has a word in it. Without this the walk cost seconds on a heredoc holding a page
        # of prose - 44 word patterns over every gap between two held ranges, and a long command has
        # hundreds of them - which is seconds added to every command a session runs.
        if piece and words.search(piece):
            fixed, got = correct_plain(piece)
            out.append(fixed)
            notes += got
        else:
            out.append(piece)
        if kind == "warn":                       # inside the fix shape a word is named, never corrected
            warned += [m.group(0) for m in words.finditer(cmd[a:b])]
        out.append(cmd[a:b])
        last = b
    return "".join(out), list(dict.fromkeys(notes)), list(dict.fromkeys(w.lower() for w in warned))


def _merged(held: list[tuple[int, int, str]]) -> list[tuple[int, int, str]]:
    """The held ranges as one sorted, non-overlapping list; a range the sed shape covers stays `warn`."""
    out: list[tuple[int, int, str]] = []
    for a, b, kind in sorted(held):
        if out and a <= out[-1][1]:
            pa, pb, pkind = out[-1]
            out[-1] = (pa, max(pb, b), "warn" if "warn" in (pkind, kind) else pkind)
        else:
            out.append((a, b, kind))
    return out


def _selftest() -> None:
    table = {"alpha": "alfa", "grays": "greys"}          # stand-ins: the real table is the hook's

    def plain(t: str) -> tuple[str, list[str]]:
        notes = []
        for w, a in table.items():
            if re.search(r"\b%s\b" % w, t):
                t = re.sub(r"\b%s\b" % w, a, t)
                notes.append(w + " -> " + a)
        if "\u2014" in t:
            t = re.sub("\\s*\u2014\\s*", " - ", t)
            notes.append("em-dash -> hyphen")
        return t, notes

    spans = re.compile(r"\x60[^\x60]*\x60")
    def run(c: str) -> tuple[str, list[str], list[str]]:
        return plan(c, table, spans, plain)

    assert run("cat > a.md <<'EOF'\nthe alpha of it\nEOF")[0] == "cat > a.md <<'EOF'\nthe alfa of it\nEOF"
    assert run("sed -i 's/alpha/beta/' a.md") == ("sed -i 's/alpha/beta/' a.md", [], ["alpha"])
    assert run("git ls-files | xargs sed -i 's/alpha/x/'")[2] == ["alpha"]
    assert run("python3 - <<'PY'\nt = t.replace('alpha', 'alfa')\nPY")[2] == ["alpha"]
    assert run("! grep -qiE 'alpha' a.md")[1] == []
    assert run("echo x && grep -c alpha a.md")[1] == []
    assert run("n=$(grep -c alpha a.md); echo $n")[1] == []
    assert run("python3 -c \"re.compile(r'(alpha|beta)')\"")[1] == []
    assert run("cat docs/alpha-notes.md")[1] == []
    assert run("grep -n $'\u2014' a.md")[1] == []
    assert run("python3 -c \"t.replace('\u2014', ' - ')\"")[1] == []
    assert run("echo 'the token `alpha` is named' >> a.md")[1] == []
    assert run("echo 'an alpha - here' >> a.md")[0] == "echo 'an alfa - here' >> a.md"
    assert run("python3 - <<'PY'\nWORDS = {'alpha', 'beta'}\nPY")[1] == []      # a word list is named
    assert run("python3 - <<'PY'\nt = \"the alpha of it\"\nPY")[1] == ["alpha -> alfa"]
    print("_hm_house selftest ok")


if __name__ == "__main__":
    _selftest()
