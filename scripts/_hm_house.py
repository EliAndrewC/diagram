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

import json
import os
import re
import sys
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


_HEREDOC_BODY = re.compile(r"<<-?\s*(['\"]?)(\w+)\1[^\n]*\n(.*?)\n[ \t]*\2\b", re.S)
_QUOTED_SPAN = re.compile(r"([\"'])(?:\\.|(?!\1).)*\1", re.S)


def _masked(cmd: str) -> str:
    """`cmd` with heredoc BODIES and the insides of quoted strings blanked, at the same length.

    GUARD_EDIT_OK: feature 239, fixing a guard that altered a SEARCH in another session's command. A
    separator inside quotes is not a separator: `grep -oE '(HIGH|MEDIUM)|— \\*\\*'` split on every `|`
    became fragments that no longer began with `grep`, the em-dash in the pattern was "corrected" to a
    spaced hyphen, and the grep silently searched for the wrong character (guard log, 2026-09-13
    05:11 UTC, a research session's reader-reports sweep). Offsets survive the mask, so a segment's
    range still indexes the ORIGINAL command.
    """
    chars = list(cmd)
    for m in _HEREDOC_BODY.finditer(cmd):
        chars[m.start(3):m.end(3)] = " " * (m.end(3) - m.start(3))
    blanked = "".join(chars)
    for m in _QUOTED_SPAN.finditer(blanked):
        chars[m.start() + 1:m.end() - 1] = " " * (m.end() - m.start() - 2)
    return "".join(chars)


def _segments(cmd: str) -> list[tuple[int, int]]:
    """(start, end) of each piece of a command between `;`, `&&`, `||`, `|` and newlines.

    Separators are found on the MASKED command, so neither a quoted `|` nor a line of a heredoc body
    starts a segment of its own.
    """
    out, start = [], 0
    for m in re.finditer(r"&&|\|\||;|\||\n", _masked(cmd)):
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

    A `None` in the list is a write whose destination cannot be known, and it is NEVER outside: a
    relative path with no cwd to resolve it against, or a target behind a variable assigned in some
    earlier command. (`git commit` is NOT one of these - the walk resolves it to the repository, as
    the paragraph above says.)

    An interpreter reading its program from a heredoc deliberately produces NOTHING here, though it
    could write anywhere. That is spec D11, and it is a ruling rather than an oversight: an earlier
    draft returned an unknowable destination for every such command, which corrected the auto-memory
    index - whose em-dash is its own format - in commands whose every resolvable target was outside
    the project. A correction that should not have happened rewrites someone else's text silently;
    one that did not happen leaves a spelling `make quick` fails on in the delta. D11 carries what
    that costs, measured.
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


# =====================================================================================================
# THE DECISION (feature 239 FR-001). This was a 275-line Python program inside a single-quoted shell
# string in `house-style-hooks.sh`. Nothing could import it, so measuring it spawned bash and python per
# command - 144 ms against 7.0 ms called in process - and one apostrophe in a comment ended the string,
# which broke the guard twice in one evening. It was lifted MECHANICALLY: every string it prints is kept
# byte for byte, early exits return "" where they printed "", and each verdict is returned rather than
# printed. The shell file is now a wrapper that calls `_hm_house.py decide`.
try:
    from _hm_escape import drop_search_segments
except Exception:                      # a guard never takes the session down with it
    def drop_search_segments(s: str) -> str:
        return s

PAIRS = {
    "colour": "color", "colours": "colors", "centre": "center", "centres": "centers",
    "centred": "centered", "behaviour": "behavior", "behaviours": "behaviors",
    "neighbour": "neighbor", "neighbours": "neighbors", "neighbourhood": "neighborhood",
    "analyse": "analyze", "analysed": "analyzed", "organise": "organize", "organised": "organized",
    "recognise": "recognize", "recognised": "recognized", "defence": "defense",
    "licence": "license", "practise": "practice", "sceptic": "skeptic", "storey": "story",
    "whilst": "while", "travelled": "traveled", "modelled": "modeled", "programme": "program",
    "metre": "meter", "litre": "liter", "mould": "mold", "plough": "plow", "kerb": "curb",
    "draught": "draft", "ageing": "aging", "marvellous": "marvelous", "jewellery": "jewelry",
    "skilful": "skillful", "artefact": "artifact", "demesne": "domain", "labelled": "labeled",
    "labelling": "labeling", "judgement": "judgment", "catalogue": "catalog", "honour": "honor",
    "honours": "honors", "grey": "gray",
}


BRIT = ("colour","colours","centre","centres","centred","behaviour","behaviours","neighbour",
        "neighbours","neighbourhood","analyse","analysed","organise","organised","recognise",
        "recognised","defence","licence","practise","sceptic","storey","whilst","travelled",
        "modelled","programme","metre","litre","mould","plough","kerb","draught","ageing",
        "marvellous","jewellery","skilful","artefact","demesne","labelled","labelling","judgement",
        "catalogue","honour","honours","grey")


def report(d: dict) -> str:
    inp = d.get("tool_input", {}) or {}
    path = inp.get("file_path", "") or ""
    body = (inp.get("new_string") or "") + (inp.get("content") or "")
    is_bash = d.get("tool_name") == "Bash"

    # A BASH HEREDOC IS A WRITE TOO. This hook matched only the Edit/Write tools at first, so
    # `python3 - <<PY ... write_text(prose) ... PY` walked straight past it - and the author did exactly
    # that, minutes after shipping the guard, to write a spec. Same hole layer 3 had, same fix: look at
    # what the command actually writes. Only heredoc BODIES are inspected, because that is where prose
    # travels; a redirect of a single echo is not worth the false positives.
    # GUARD_EDIT_OK: feature 236 (the GM item 4) - THE WHOLE BASH PAYLOAD, NOT ONLY ITS HEREDOC BODIES.
    # The heredoc rule above was already the second version of this hole; the third was measured on the
    # session that motivated feature 236, where British spellings reached the tree through Bash payloads
    # this hook never looked at (`research.md` R3). A command WRITES in more ways than a heredoc - an
    # `echo >>`, a `python3 -c` that calls write_text, a `sed -i` replacement - and the cheap, honest rule
    # is to read the payload. What that costs is a WARNING rather than a correction (spec D2): a Bash
    # payload is often itself the spelling fix (`sed -i \x27s/centre/center/g\x27`), and correcting it
    # would turn the fix into a no-op. The `make quick` phase is the half that fails.
    if is_bash:
        cmd = inp.get("command", "") or ""
        # what a command LOOKS FOR is not what it writes: `git grep -n "centre"` is correct work
        body = drop_search_segments(cmd)
        # the target matters as much as the text: a heredoc writing the GM own words is exempt below,
        # so pick up any path the command mentions
        path = path or " ".join(re.findall(r"[\w./-]+\.(?:md|py|sh|toml|json)", cmd))
    if not body:
        return ""
    # the GM own writing, and the files that must quote the rule
    # gm-request.md is a verbatim transcript of the GM speaking - correcting it would defeat its purpose
    if "/host-l7r-repo" in path or path.endswith("l7r.md") or "gm-request.md" in path:
        return ""
    # A FILE OUTSIDE THE PROJECT IS NOT PROJECT CONTENT (2026-09-06): the rule is project-wide, and a session
    # scratchpad under /tmp is not the project. Measured the day the quotation exemption landed: three of five
    # reader agents writing verbatim page text into /tmp/.../result.json each had their dashes and spellings
    # rewritten, each noticed only by diffing, and each worked around the guard with chr() escapes - a guard that
    # fires on correct work is one that gets worked around (CLAUDE.md, "deliberately NOT enforced").
    # GUARD_EDIT_OK: feature 236 amendment 2 - and the SESSION STATE directory is outside the project the
    # same way `/tmp` is. `~/.claude/projects/<proj>/memory/` is the auto-memory, whose index line format
    # is Claude Code own and uses an em-dash; the correction was rewriting that format as the index was
    # written. Measured on the real commands this hook would have rewritten (`research.md` R10).
    # GUARD_EDIT_OK: feature 236 amendment 2, fixing a guard that went SILENT on work it governs - the
    # exemption is decided by where the write LANDS, never by one path the command mentions. A Bash
    # payload names several at once, and testing the joined list silenced the rule on a command that read
    # the memory file and wrote a project file in the same breath (found by the amendment review).
    def _outside(one):
        # GUARD_EDIT_OK: a write whose destination cannot be known is NEVER outside - an unknown target
        # arrives as None and must not exempt anything. It also must not raise: the wrapper turns a crash
        # into silence, so a guard that throws is a guard that is off.
        return bool(one) and (one.startswith("/tmp/") or "/.claude/projects/" in one)
    # GUARD_EDIT_OK: what the command WRITES decides it; the paths it merely MENTIONS are the fallback,
    # for a write that travels by no redirect at all (a `python3 -` heredoc calling write_text).
    # GUARD_EDIT_OK: the cwd of the shell resolves a relative write target, so the exemption is judged on
    # where the write really lands rather than on whether the path happens to be absolute. (No apostrophe
    # in this comment: the scan is a single-quoted program, and one apostrophe ends it - the trap this
    # file already carries a note about, met again.)
    _judged = (write_targets(inp.get("command", "") or "", d.get("cwd") or None) if is_bash
               else []) or [p for p in path.split() if p]
    if _judged and all(_outside(p) for p in _judged):
        return ""
    # GUARD_EDIT_OK: feature 236 - A FIXTURE IS A VERBATIM RECORD. `scripts/fixtures/` holds corpora of
    # commands that really ran (the guard-refusal replays, and 236 own 238-command parse corpus); several
    # of those commands were house-style sweeps and carry the words by necessity. Correcting one would
    # falsify the record and break the measurement it reproduces - the same ground as a quotation.
    if "/scripts/fixtures/" in "/" + path:
        return ""
    # GUARD_EDIT_OK: feature 236 - two more files that must QUOTE the words to state the rule: the delta
    # check that reads the BRIT table out of this hook, and its suite. The hook corrected both as they
    # were typed, which is the same false positive the three names before them were added for. (No
    # apostrophe in this comment: the scan below is a single-quoted program, and one apostrophe ends it -
    # GUARD_EDIT_OK: the same trap feature 217 hit in guard-file-hooks, met again here.)
    if re.search(r"(^|/)(CLAUDE\.md|constitution\.md|l7r-style\.md|house-style-hooks\.sh|test-house-style-hooks\.sh|test_hooks_cases\.py|check-house-style-delta\.py|test_house_style_delta\.py|test_guard_firing_log\.py|_hm_house\.py)$", path):  # GUARD_EDIT_OK: feature 236 - the census drives the guard with a REAL payload, which must carry a real British spelling or it proves nothing
        return ""
    # a SOURCE block inside the added text is the GM speaking; drop it before looking
    body = re.sub(r"<!--\s*SOURCE: GM NOTES.*?<!--\s*END SOURCE\s*-->", " ", body, flags=re.S | re.I)

    # GUARD_EDIT_OK: feature 164 - CORRECT THE TEXT INSTEAD OF REFUSING THE EDIT (GM 2026-08-30: *"a tool
    # could do a rewrite or return additional context or whatever"*). Both of the two rules here are exact
    # substitutions with no judgment in them, and a session refused for one of them just retypes the same
    # edit with the fix - measured: 3 firings, 3 identical re-edits. So the fix is applied and the session
    # is told. Three things the correction must never do, each one load-bearing:
    #
    #   - CORRECT THE GM OWN WORDS. The path exemptions above cover l7r.md and gm-request.md but NOT
    #     `specs/NNN-*/request.md`, which is where this repository records the GM verbatim requests -
    #     the authority for every spec. Silently rewriting those would breach Principle V, so a file
    #     recording the GM speaking stays on the REFUSAL path, where a person decides.
    #   - CORRECT A WORD THAT IS BEING NAMED RATHER THAN USED. A backtick span is how the project own
    #     prose marks a token it is discussing, and this guard refused feature 164 own plan for NAMING
    #     a British spelling in a sentence about how it is handled. Spans are held out of both the
    #     detection and the correction.
    #   - GUESS. Every pair below is CLAUDE.md own, one American form per word.
    CODE = r"\x60{3}.*?\x60{3}|\x60[^\x60]*\x60"  # a code span, written by codepoint: a literal backtick inside $( ) is command substitution
    # A QUOTATION IS SOMEONE ELSE TEXT (GM 2026-09-06, header bullet three): corner brackets, curly quotes and
    # the two HTML quotation elements anywhere; straight double quotes only in a prose file, where they quote -
    # in a .py or .sh they delimit a string, and the rule reaches code. The heredoc path list is joined by spaces.
    QUOTE = r"「[^」]*」|『[^』]*』|“[^”]*”|<q\b[^>]*>.*?</q>|<blockquote\b[^>]*>.*?</blockquote>"
    # GUARD_EDIT_OK: feature 236 FR-007a - "outside a quoted span" is the HOUSE-STYLE sense, never the
    # SHELL one. In a Bash payload a straight double quote is shell quoting, and under a `<<\x27PY\x27`
    # heredoc the whole payload is shell-quoted, so admitting that form here would let the exemption
    # swallow the rule the payload is being read for.
    if not is_bash and re.search(r"\.(?:md|html|txt)(\s|$)", path):
        QUOTE += r"|\x22[^\x22\n]*\x22"
    SPAN = re.compile(CODE + "|" + QUOTE, re.S)

    
    def _match_case(src, dst):
        if src.isupper():
            return dst.upper()
        if src[:1].isupper():
            return dst[:1].upper() + dst[1:]
        return dst

    
    def correct(text):
        """The corrected text and what was corrected, leaving backtick spans exactly as they are."""
        out, notes, last = [], [], 0
        for m in SPAN.finditer(text):
            piece, fixed_notes = _correct_plain(text[last:m.start()])
            out.append(piece); notes += fixed_notes
            out.append(m.group(0))               # a span is a MENTION: never touched
            last = m.end()
        piece, fixed_notes = _correct_plain(text[last:])
        out.append(piece); notes += fixed_notes
        return "".join(out), notes

    
    def _correct_plain(text):
        notes = []
        for dash, name in (("—", "em-dash"), ("–", "en-dash")):
            if dash in text:
                text = re.sub(r"\s*%s\s*" % dash, " - ", text)
                notes.append(name + " -> hyphen")
        for brit, amer in PAIRS.items():
            pat = re.compile(r"\b%s\b" % brit, re.I)
            if pat.search(text):
                text = pat.sub(lambda m: _match_case(m.group(0), amer), text)
                notes.append(brit + " -> " + amer)
        return text, notes

    
    # what a session can actually see, with the spans held out
    visible = SPAN.sub(" ", body)
    hits = []
    if "—" in visible: hits.append("em-dash (U+2014)")
    if "–" in visible: hits.append("en-dash (U+2013)")
    for w in BRIT:
        if re.search(rf"\b{w}\b", visible, re.I):
            hits.append(w)
    if not hits:
        return ""

    # THE GM SPEAKING IS NEVER CORRECTED - only refused, so a person decides (Principle V).
    # GUARD_EDIT_OK: feature 236 amendment 2 - a Bash payload names several paths at once, so the request
    # file is looked for ANYWHERE in the list rather than only at its end, or a command writing the GM own
    # words beside another path would be corrected.
    GM_VERBATIM = re.search(r"specs/[^/\s]+/request\.md", path) or "gm-request.md" in path

    # CAN THE WHOLE EDIT BE FIXED MECHANICALLY? Only then is it corrected; a violation the table cannot
    # reach keeps the refusal, because a partial correction would hide what is left.
    fixed_fields, notes = {}, []
    for field in ("new_string", "content"):
        if field in inp and isinstance(inp[field], str):
            got, got_notes = correct(inp[field])
            fixed_fields[field] = got
            notes += got_notes
    leftover = SPAN.sub(" ", "".join(fixed_fields.values()))
    still_bad = "—" in leftover or "–" in leftover or any(
        re.search(rf"\b{w}\b", leftover, re.I) for w in BRIT
    )

    # GUARD_EDIT_OK: feature 236 amendment 2 - A BASH PAYLOAD IS CORRECTED TOO, EXCEPT THE SED SHAPE (the
    # GM 2026-09-12, ruling on spec D2: *"we should warn when it is the sed shape, and for other shapes
    # just correct it"*). The first version only ever TOLD the session, because a payload is sometimes
    # itself the spelling fix; the GM kept that case and took the rest. What a command only NAMES - the
    # word it searches for, the file it reads, the old side of a replacement - is held out by `_hm_house`,
    # which prices each range against the real commands this hook warned on (`research.md` R10).
    if is_bash:
        house_plan = plan
        new_cmd, notes, warned = (house_plan(inp.get("command", "") or "", PAIRS, SPAN, _correct_plain)
                                  if house_plan and not GM_VERBATIM else (None, [], hits))
        if new_cmd is not None and notes and new_cmd != (inp.get("command", "") or ""):
            payload = dict(inp)
            payload["command"] = new_cmd
            return json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "updatedInput": payload,
                "additionalContext": (
                    "House style was applied to this command for you (" + ", ".join(notes[:6]) + "). "
                    "A write that travels through a Bash payload owes CLAUDE.md exactly as an Edit does. "
                    "What the command only NAMES was left as typed: a search pattern, a path, a code span "
                    "and a quotation of someone elses text."
                    + (" Left as typed and NOT corrected, because this command carries both spellings and "
                       "is therefore a fix: " + ", ".join(warned[:6]) + "." if warned else "")),
            }})
        if warned:
            # GUARD_EDIT_OK: feature 236 amendment 2 - the REASON is the branch that produced the warning,
            # never a guess. A command left as typed because it is the fix and one left as typed because
            # it writes the GM own words are different facts, and a session told the wrong one will look
            # for a sed expression that is not there.
            # GUARD_EDIT_OK: feature 236 amendment 2 - the message says what the RULE saw, not what the
            # command is. "Both spellings in one command" is the shape a replacement pair takes, and it is
            # also what a quotation, a search and a sentence naming both look like; telling a session its
            # command "is a spelling fix" when it is a quotation is the guard asserting what it cannot see.
            why = ("this file records the GM speaking, and their words are reported, never corrected "
                   "(Principle V)" if GM_VERBATIM else
                   "this command carries BOTH spellings of a word (or is the sed shape), which is how a "
                   "replacement pair looks - correcting it could replace a word with itself and make the "
                   "fix silently do nothing. If it is not a fix, the word is yours to correct")
            return json.dumps({"hookSpecificOutput": {
                "hookEventName": "PreToolUse",
                "additionalContext": (
                    "House style, in this command payload: " + ", ".join(warned[:6]) + ". Not corrected "
                    "for you: " + why + ". `make quick` fails on a British spelling in the delta, so it "
                    "is cheaper to fix now than at the gate."),
            }})
        return ""

    if fixed_fields and notes and not still_bad and not GM_VERBATIM:
        payload = dict(inp)
        payload.update(fixed_fields)
        return json.dumps({"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "updatedInput": payload,
            "additionalContext": (
                "House style was applied to this edit for you (" + ", ".join(notes[:6]) + "). "
                "Both rules are exact substitutions from CLAUDE.md, so the correction is made rather "
                "than the edit refused - a refusal costs a model round trip to say the same thing. "
                "Text inside backticks was left alone: a word in a code span is being named, not used. "
                "Text inside quotation marks was left alone too: a quotation is someone else text (GM 2026-09-06)."),
        }})

    return " | ".join(hits[:6]) + (" [the GM own words - not corrected, only reported]" if GM_VERBATIM else "")


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
    if sys.argv[1:2] == ["decide"]:
        # the hook's own entry: the payload on stdin, the report on stdout - "" for silence, a JSON
        # verdict for a correction or a warning, and anything else is the text of a refusal
        try:
            _payload = json.load(sys.stdin)
        except Exception:
            _payload = None
        sys.stdout.write(report(_payload) if isinstance(_payload, dict) else "")
    else:
        _selftest()
