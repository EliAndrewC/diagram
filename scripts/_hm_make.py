#!/usr/bin/env python3
"""The MAKE and REWRITE family - which target a command invokes, and the compliant form (feature 172).

Split out of `_hookmatch.py`, and this is the module the split was FOR: only `gate`, `make-only` and
`pair` use it, so a change to `combine`, `as_make_target`, `as_paired` or `targets` now re-runs three
suites instead of twenty-one. Features 162 (combine rather than reject) and 164 (correct rather than
refuse) live here."""

from __future__ import annotations

import json
import re
import sys

from _hm_escape import escape_used
from _hm_shape import _POS, _PY, _strip_heredocs, _strip_quotes

# a guard file, as the TARGET of a write - the filename adjacent to the operator that writes it
_GUARD = r"[\w./-]*(?:Makefile|[\w-]*-hooks\.sh|settings\.json)"

# GUARD_EDIT_OK: feature 169 - TWO FALSE POSITIVES, one of which blocked a command that wrote
# nothing at all. These were matched against the RAW command, so:
#   * `printf '... -> scripts/main-tree-hooks.sh (new) ...'` was refused, because the ARROW in a
#     printf string reads as a redirect. Fixed by `(?<![-\w])`: `->` and `2>` are not `>`.
#   * a guard filename inside a QUOTED STRING is prose, not a target. The shell patterns now match
#     the sanitized command (heredoc bodies and quoted strings blanked), which is what every other
#     decision in this file already does.
# The python-write patterns keep matching RAW on purpose: there the filename IS inside quotes -
# `Path("...settings.json").write_text(...)` - so sanitizing would blank the very thing they detect.
# Fourth and fifth time this repository has made the mention-versus-invocation mistake in this one
# function; proximity is the signal, presence never is.
_GUARD_WRITE_SHELL = (
    rf"(?<![-\w])>>?\s*{_GUARD}(?:\s|$)",         # cat > Makefile ; echo x >> scripts/a-hooks.sh
    rf"sed\s+-i\b[^;|&]*?{_GUARD}(?:\s|$)",        # sed -i 's/a/b/' scripts/a-hooks.sh
    rf"tee\s+(?:-a\s+)?{_GUARD}(?:\s|$)",          # tee Makefile
)

_GUARD_WRITE_PY = (rf"{_GUARD}[\"\']\s*\)?\s*\)?\s*\.write_text",)  # Path("...Makefile").write_text(

# GUARD_EDIT_OK: feature 164 - THE VARIABLE ROUTE, found by walking through it. The patterns above
# need the guard filename ADJACENT to the write, so the ordinary two-line python shape slips past:
#
#     p = pathlib.Path(".claude/settings.json")
#     p.write_text(json.dumps(d))          # <- writes a guard file, matched nothing
#
# This session used exactly that to wire a hook into settings.json while implementing this feature.
# Proximity is still the signal rather than presence (a docstring naming a hook must stay legal), so
# the two halves are tied by the VARIABLE NAME: a name bound to a guard path, and that same name
# writing. `_guard_write_via_name` is separate from the tuple above because it needs two matches.
_GUARD_BIND = re.compile(rf"(\w+)\s*=\s*(?:pathlib\.)?Path\(\s*[\"'][^\"']*{_GUARD}[\"']\s*\)")

def _guard_write_via_name(raw: str) -> bool:
    for m in _GUARD_BIND.finditer(raw):
        if re.search(rf"\b{re.escape(m.group(1))}\.write_text\s*\(", raw):
            return True
    return False

_TARGET = re.compile(_POS + r"(?:\$\(MAKE\)|make)\s+(?:-\S+(?:\s+\S+)?\s+)*(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*([a-z][\w-]*)")

def targets(cmd: str) -> set[str]:
    """Every make TARGET this command actually INVOKES - a mention is not an invocation.

    The same anchoring `classify` uses, for the hooks that care about WHICH target: heredoc bodies and
    quoted strings are blanked first, and a target only counts at a command position (start, or after
    `;`, `|`, `&&`, `||`, a newline), past any flags and `VAR=value` prefixes. `gate-hooks.sh` used a
    bare substring test until 2026-08-29 and blocked six pieces of correct work in one day: a script
    ANALYSING how often its two targets had been run, a plan document quoting them, twice the test file
    that exists to prove guards do not do this, and finally the very command that fixed it. Fourth time
    this repository has made the mention-versus-invocation mistake, which is why the answer lives here
    rather than in another `case`.
    """
    return {m.group(1) for m in _TARGET.finditer(_strip_quotes(_strip_heredocs(cmd)))}

def classify(cmd: str) -> str:
    # The escape is checked FIRST and stays first (CLAUDE.md: a guard that cannot be repaired
    # through the channel it guards is a worse defect) - what changed in feature 169 is the MATCH.
    # `grep -rn GUARD_EDIT_OK scripts/` used to classify the whole command as `ok`, which switched
    # this guard off for the rest of that command.
    if not cmd:
        return "ok"
    # GUARD_EDIT_OK: feature 170 - A DISTINCT VERDICT, so the escape can be RECORDED. It used to
    # return plain `ok` - the same value a command that matched nothing returns - so `make-only`
    # could not tell an escape from an ordinary permitted command and recorded neither. That was
    # feature 169's R13, deferred with a sketch because it changes this function's return contract;
    # the audit that deferral asked for found two consumers, and only `make-only` dispatches on the
    # whole value (`gate-hooks.sh` compares one arm), whose `case` falls through to a permit - so a
    # new value is safe by construction and the arm that records it is explicit.
    if escape_used(cmd, "GUARD_EDIT_OK"):
        return "guard-edit-ok"
    raw = cmd
    c = _strip_quotes(_strip_heredocs(cmd))

    def at(pat: str) -> bool:
        return re.search(_POS + pat, c) is not None

    if at(r"make\s+(?:-\S+\s+)*(?:-f|--file|--makefile)(?:[=\s]|$)"):
        return "foreign-makefile"
    if at(rf"{_PY}\s+(?:-\S+\s+)*-m\s+l7r\.diagram\.") or at(rf"{_PY}\s+\S*l7r/diagram/(?:pipeline/regen|hamletgen/__main__)\.py"):
        return "engine-entry-point"
    if at(rf"(?:{_PY}\s+(?:-\S+\s+)*-m\s+)?pytest\b"):
        return "bare-pytest"
    # AN OVERRIDE COUNTS WHEREVER IT SITS ON THE COMMAND. `REF_WHY=x make done` puts it in front;
    # `make done FULL=1 REF_WHY=x` passes it as a make argument. Both skip the prompt, so both are
    # tier 2 - the first cut only matched the leading form and the suite caught it immediately.
    if re.search(r"\b(?:REF_WHY|REF_OK|GATE_OK)=", c) and (at(r"make\b") or re.search(_POS + r"(?:REF_WHY|REF_OK|GATE_OK)=", c)):
        return "inline-override"
    # GUARD-WRITE READS THE RAW COMMAND, NOT THE STRIPPED ONE, and this is the one place that is
    # right: everywhere else a heredoc body is prose to ignore, but here it is the payload that does
    # the writing - `python3 - <<PY ... write_text("...Makefile") ... PY` is exactly the route that
    # slipped past layer 3 all day.
    #
    # THE GUARD FILE MUST BE THE TARGET OF THE WRITE, not merely present somewhere. The first cut
    # asked "does a guard filename appear AND does a write appear", which blocked a command creating
    # an ordinary test file whose DOCSTRING mentioned a hook by name. Third time this feature has
    # made the mention-versus-invocation mistake - a grep, a commit message, and now a docstring -
    # which is worth stating plainly: proximity is the signal, presence never is.
    if (
        any(re.search(pat, c) for pat in _GUARD_WRITE_SHELL)          # sanitized: see feature 169
        or any(re.search(pat, raw) for pat in _GUARD_WRITE_PY)        # raw: the name lives in quotes
        or _guard_write_via_name(raw)
    ):
        return "guard-write"
    return "ok"

# ---- COMBINE, DO NOT REJECT (feature 162) ---------------------------------------------------
#
# WHY (GM 2026-08-30): *"does that mean our tooling should detect when both are being run and then
# combine them into `make done` automatically instead of rejecting?"* It does. `gate-hooks.sh` used
# to refuse a command naming both targets, and the refusal cost a round trip - measured over this
# project's transcripts, 37 firings of which 23 were escaped with `GATE_OK` in the very next call,
# so 62% of the time the guard spent a turn and prevented nothing. A `PreToolUse` hook may instead
# return the command REWRITTEN (`updatedInput`), which costs nothing at all.
_SEP = re.compile(r"(\s*(?:&&|\|\||;|\n)\s*)")

_MAKE_HEAD = re.compile(r"^(?:[A-Za-z_][A-Za-z0-9_]*=\S*\s+)*(?:\$\(MAKE\)|make)\b")

# EVERY GOAL OF ONE MAKE CALL, not just the first. `targets()` answers "which targets does this
# command invoke" and stops at the first goal of each call, which is enough for a yes/no guard and is
# NOT enough to rewrite `make quick done` - the shape the GM asked to be combined. Kept local so the
# eleven other guards keep the matcher they were tested against.
# The `[./~]\S*` arm exists so a PATH argument does not end the scan: `make -C /x quick` would
# otherwise stop at `/x` and never see the goal behind it, and the rewrite would silently decline a
# command it understands perfectly well. _TAKES_ARG below is what keeps that path from counting as a
# goal itself.
_GOALS = re.compile(
    _POS + r"(?:\$\(MAKE\)|make)((?:\s+(?:-\S+|[A-Za-z_][A-Za-z0-9_]*=\S*|[./~]\S*|[a-z][\w-]*))*)"
)

# `-C dir` and `-f file` take an ARGUMENT, and the argument is not a goal. Without this, `make -C done
# quick` reads as a call carrying both goals and the rewrite would "combine" it into `make -C done`,
# which runs the default target somewhere else entirely. No such command exists in this repository
# today; a rewrite that must never guess does not get to rely on that.
_TAKES_ARG = ("-C", "-f", "--directory", "--file", "--makefile", "-o", "--old-file", "-W")

def _goals(seg: str) -> set[str]:
    out = set()
    for m in _GOALS.finditer(_strip_quotes(_strip_heredocs(seg))):
        skip = False
        for word in m.group(1).split():
            if skip:
                skip = False
                continue
            if word in _TAKES_ARG:
                skip = True
                continue
            if re.fullmatch(r"[a-z][\w-]*", word):
                out.add(word)
    return out

def _balanced(text: str) -> bool:
    return text.count("(") == text.count(")") and text.count('"') % 2 == 0 and text.count("'") % 2 == 0

def combine(cmd: str) -> str | None:
    """`cmd` with the `make quick` work removed, when it invokes BOTH quick and done.

    None means "leave it alone": the shape is not one that can be rebuilt exactly, so the command
    goes through UNCHANGED rather than being guessed at. A guessed rewrite costs a session its
    command; the fallback costs one warm `quick` (4.1 s). `done` is a superset of `quick` - it runs
    the same lint, format and typecheck and a strict superset of the tests - so dropping `quick`
    never drops a question that was asked.
    """
    if not cmd or "GATE_OK" in cmd or "<<" in cmd:
        return None
    if "quick" not in _goals(cmd) or "done" not in _goals(cmd):
        return None
    parts = _SEP.split(cmd)                       # [seg, sep, seg, sep, ...]
    segs, seps = parts[0::2], parts[1::2]
    kept: list[tuple[str, str]] = []
    dropped = False
    for i, seg in enumerate(segs):
        sep = seps[i] if i < len(seps) else ""
        got = _goals(seg)
        makeish = bool(_MAKE_HEAD.match(seg.strip())) and _balanced(seg)
        if makeish and "quick" in got and "done" not in got:
            dropped = True                        # a whole segment whose work `done` supersedes
            continue
        if makeish and got >= {"quick", "done"}:
            rebuilt = re.sub(r"\s+quick\b", "", seg, count=1)
            if _goals(rebuilt) != got - {"quick"}:
                return None
            kept.append((rebuilt, sep))
            dropped = True
            continue
        kept.append((seg, sep))
    if not dropped:
        return None
    out = "".join(s + (p if j < len(kept) - 1 else "") for j, (s, p) in enumerate(kept))
    out = out.strip().rstrip("&|; \n").strip()
    if not out or out == cmd or "done" not in _goals(out) or "quick" in _goals(out):
        return None
    return out

# ---- CORRECT, DO NOT REFUSE (feature 164) ----------------------------------------------------
#
# GUARD_EDIT_OK: new shared decisions for the guards, at the GM's request (2026-08-30): *"are there
# places where a makefile command is refusing to do something but a tool could do a rewrite or return
# additional context or whatever?"* There are. The audit found 280 refusals in six days, each one
# spending a model round trip; where the guard already KNOWS the compliant command - it names it in
# its own refusal - it may as well produce it. These decisions live here rather than in the hooks so
# they can be tested with plain strings instead of through bash quoting.

# What `make test-file` runs: pytest with workers, `-q` and `--no-cov` on the paths in FILE, with
# `-k "$(K)"` when K is set (feature 212). A flag that target already supplies, or one that only
# shapes output, is safe to drop. Anything that changes WHICH tests run or HOW they are measured is
# not, so those keep the refusal - the same never-guess rule feature 162 set for the quick/done
# rewrite - and the refusal names the token that stopped the rewrite (`why_not_make_target`).
#
# GUARD_EDIT_OK: feature 212 - THE TARGETED RUN CONVERTS, NOT ONLY THE BARE FILE (GM 2026-09-07:
# *"if A Claude code session is using Pytest to run a targeted set of tests, such as targeting a
# specific module or even a specific test case, then rather than failing ... we translate it into
# the make target which should have been run"*). Feature 164's rewrite took ONE file and nothing
# else, and the census of every refusal since (specs/212, R2) found it had converted none of the
# eight targeted runs in the record: every one carried `2>&1 | tail -N` after the pytest segment,
# which the old rule read as "a pipeline: not ours to rebuild". The pipeline is not part of the
# pytest invocation - it consumes the output of whatever runs - so the segment is rebuilt and what
# follows it is kept verbatim. `-k` (the GM's "specific test case") becomes `K=`, a directory or a
# node id is a path, several paths are several. Still refused: a marker filter, a deselect, a
# collection, a coverage run, a plugin LOAD, an absolute path - each a change to what runs.
_DROP_FLAG = re.compile(r"^(-q|-qq|--quiet|-x|--exitfirst|--no-cov|--no-header|-v|-vv|-vvv|--tb=\S+|--color=\S+)$")
_DROP_PAIR = {"-n", "--dist", "--tb", "--color"}     # take one argument, then are dropped
_REDIR = re.compile(r"^(?:\d?>>?&?\S+|\d?<\S+)$")      # 2>&1  >log  2>/dev/null  <in
_REDIR_OP = re.compile(r"^\d?>>?$")                    # `> log` written with a space
# a RELATIVE test path: the tests tree, a directory under it, or a test file with an optional node id
_TESTPATH = re.compile(r"^(?:tests(?:/[\w.-]+)*/?|(?:[\w.-]+/)*test_[\w-]+\.py(?:::[\w\[\]:.,-]+)?)$")

_PYTEST_RUN = re.compile(r"(?:\S*/)?python3?\s+(?:-\S+\s+)*-m\s+pytest\b|(?<![\w/.-])pytest\b")

_MASK_HEREDOC = re.compile(r"<<-?\s*['\"]?(\w+)['\"]?\n.*?\n\s*\1\b", re.S)
_MASK_QUOTE = re.compile(r"(?<!-c )(?<!-c\t)([\"'])(?:\\.|(?!\1).)*\1", re.S)

def _masked(cmd: str) -> str:
    """`cmd` with heredoc bodies and quoted strings replaced by spaces OF THE SAME LENGTH, so a match
    found in the masked text sits at the same offset in the raw one. `_strip_*` change the length,
    which is fine for a yes/no verdict and useless for a rewrite that must cut the raw command."""
    def blank(m: re.Match[str]) -> str:
        return " " * len(m.group(0))
    return _MASK_QUOTE.sub(blank, _MASK_HEREDOC.sub(blank, cmd))

def _segment(tail: str) -> tuple[str, str]:
    """Split the text after the invocation at its first unquoted separator: (segment, rest)."""
    i, q = 0, ""
    while i < len(tail):
        ch = tail[i]
        if q:
            if ch == "\\" and q == '"':
                i += 2
                continue
            if ch == q:
                q = ""
        elif ch in "\"'":
            q = ch
        elif ch == "\\":
            i += 2
            continue
        elif ch in ";\n)|":
            return tail[:i], tail[i:]
        elif ch == "&":
            if tail[i : i + 2] == "&&" or i == 0 or tail[i - 1] != ">":
                return tail[:i], tail[i:]       # a chain or a background `&`; `>&` is a redirect
        i += 1
    return tail, ""

def _words(seg: str) -> list[tuple[str, str]]:
    """Shell-ish word split: (raw word, its unquoted value)."""
    out: list[tuple[str, str]] = []
    i, n = 0, len(seg)
    while i < n:
        while i < n and seg[i] in " \t":
            i += 1
        if i >= n:
            break
        j, q, buf = i, "", ""
        while j < n and (q or seg[j] not in " \t"):
            c = seg[j]
            if q:
                if c == q:
                    q = ""
                else:
                    buf += c
            elif c in "\"'":
                q = c
            else:
                buf += c
            j += 1
        out.append((seg[i:j], buf))
        i = j
    return out

def _targeted_pytest(cmd: str) -> tuple[str | None, str]:
    """(the compliant command, "") or (None, why the shape keeps its refusal)."""
    if not cmd:
        return None, "no command"
    m = _PYTEST_RUN.search(_masked(cmd))
    if not m:
        return None, "no pytest invocation"
    head, tail = cmd[: m.start()], cmd[m.end() :]
    seg, rest = _segment(tail)
    body = seg.rstrip()
    trail = seg[len(body) :]
    ws = _words(body)
    paths: list[str] = []
    redirs: list[str] = []
    k: str | None = None
    i = 0
    while i < len(ws):
        raw, w = ws[i]
        nxt = ws[i + 1][1] if i + 1 < len(ws) else None
        if w == "-k" or w.startswith("-k="):
            if k is not None:
                return None, "`-k` given twice"
            if w == "-k":
                if nxt is None:
                    return None, "`-k` with no expression"
                k, i = nxt, i + 2
            else:
                k, i = w[3:], i + 1
            continue
        if _REDIR_OP.match(w):
            if nxt is None:
                return None, "a redirect with no target"
            redirs.append(f"{raw} {ws[i + 1][0]}")
            i += 2
            continue
        if _REDIR.match(w):
            redirs.append(raw)
            i += 1
            continue
        if w == "-p":
            if nxt is None or not nxt.startswith("no:"):
                return None, f"`-p {nxt or ''}` loads a plugin"
            i += 2
            continue
        if w.startswith("-p") and w[2:].startswith("no:"):
            i += 1
            continue
        if w in _DROP_PAIR:
            i += 2
            continue
        if _DROP_FLAG.match(w):
            i += 1
            continue
        if w.startswith("-"):
            return None, f"`{w}`"
        if w.startswith("/"):
            return None, f"the absolute path `{w}`"
        if _TESTPATH.match(w):
            paths.append(w)
            i += 1
            continue
        return None, f"the argument `{w}`"
    if not paths:
        return None, "no test path"
    out = f"{head}make test-file FILE=" + (f'"{" ".join(paths)}"' if len(paths) > 1 else paths[0])
    if k is not None:
        if any(ch in k for ch in "\"$`"):
            return None, "a `-k` expression carrying a quote, a dollar or a backtick"
        out += f' K="{k}"'
    if redirs:
        out += " " + " ".join(redirs)
    return out + trail + rest, ""


def as_make_target(cmd: str) -> str | None:
    """A targeted pytest run as `make test-file FILE=... [K=...]`, or None to keep refusing.

    None means the shape is not one that can be rebuilt exactly - a marker filter, a deselect, a
    collection, a coverage flag, a plugin load - and the guard refuses it as it always has; the
    reason is `why_not_make_target`. What the rewrite preserves is feature 127's invariant, that
    every test invocation goes through a make target; it does NOT preserve coverage floors,
    because neither this command nor the target holds them.
    """
    return _targeted_pytest(cmd)[0]


def why_not_make_target(cmd: str) -> str:
    """Why `as_make_target` declined - the token that stopped it, for the refusal to name."""
    return _targeted_pytest(cmd)[1]


# ---- AN ENGINE ENTRY POINT A MAKE TARGET WRAPS BECOMES THAT TARGET (feature 212) ----------------
#
# GUARD_EDIT_OK: feature 212 - the compliant command is DERIVED from the Makefile at hook time,
# never kept in a table here: a table names targets that get renamed (feature 193 retired nine) and
# misses the ones added after it. A target qualifies when its recipe is ONE line of the form
# `$(RUN).<module> <args>` (or `$(SWITCH) <word>` for the switches module) and the command's
# arguments lay onto that recipe word for word - a literal matches itself, `$(ARGS)` takes the rest,
# `$(or $(VAR),default)` takes one word, `$(if $(VAR),--flag,)` takes an optional flag. A recipe with
# a `$(REF_FIRST)` guard or a second line is not one command, and a module nothing wraps keeps the
# refusal: a derived table cannot name a target that does not exist. Of the 29 entry-point refusals
# in the record, four were modules a target wraps (specs/212 R1); the twelve `tools.scatter_audit`
# runs were not, and the refusal now lists what IS wrapped so the next session can tell.
_ENTRY_RUN = re.compile(r"(?:\S*/)?python3?\s+(?:-\S+\s+)*-m\s+l7r\.diagram\.([\w.]+)")
_RECIPE_ARG = re.compile(r"\$\(ARGS\)|\$\(or \$\((\w+)\),([^)]*)\)|\$\(if \$\((\w+)\),([^,]*),\)|(\S+)")
_TARGET_LINE = re.compile(r"^([a-z][\w-]*):(?!=)")

def _makefile_for(cwd: str) -> str:
    """The skill Makefile of the tree the command runs in - walking up from `cwd` - else this
    repository's own. A clone and main carry the same targets, and a target missing from the tree
    the command runs in fails loudly in make, never silently."""
    from pathlib import Path
    rel = Path(".claude/skills/diagram/Makefile")
    here = Path(cwd).resolve() if cwd else None
    while here is not None:
        if (here / rel).is_file():
            return (here / rel).read_text()
        if here.parent == here:
            break
        here = here.parent
    own = Path(__file__).resolve().parents[1] / rel
    return own.read_text() if own.is_file() else ""

def _recipes(text: str) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    cur: str | None = None
    for line in text.split("\n"):
        if line.startswith("\t"):
            if cur is not None:
                body = line[1:].strip()
                if body and not body.startswith("#") and not body.startswith(': "'):
                    out[cur].append(body)
            continue
        m = _TARGET_LINE.match(line)
        if m and ": export" not in line:
            cur = m.group(1)
            out.setdefault(cur, [])
        elif not line.startswith("#"):
            cur = None
    return out

def wrapped_modules(text: str) -> dict[str, list[tuple[str, list[tuple[str, ...]]]]]:
    """module -> [(target, recipe tokens)] for every one-line `$(RUN).<module>` recipe in `text`."""
    out: dict[str, list[tuple[str, list[tuple[str, ...]]]]] = {}
    for target, lines in _recipes(text).items():
        if len(lines) != 1:
            continue
        line = lines[0].lstrip("@")
        if line.startswith("$(SWITCH)"):
            module, rest = "switches", line[len("$(SWITCH)") :]
        else:
            m = re.match(r"^\$\(RUN\)\.([\w.]+)\s*(.*)$", line)
            if not m:
                continue
            module, rest = m.group(1), m.group(2)
        toks: list[tuple[str, ...]] = []
        for a in _RECIPE_ARG.finditer(rest):
            if a.group(0) == "$(ARGS)":
                toks.append(("ARGS",))
            elif a.group(1):
                toks.append(("OR", a.group(1), a.group(2)))
            elif a.group(3):
                toks.append(("IF", a.group(3), a.group(4)))
            else:
                toks.append(("LIT", a.group(5)))
        out.setdefault(module, []).append((target, toks))
    return out

def _lay(args: list[str], toks: list[tuple[str, ...]]) -> list[str] | None:
    """The `VAR=value` assignments that reproduce `args` through `toks`, or None when they cannot."""
    out: list[str] = []
    i = 0
    for tok in toks:
        if tok[0] == "LIT":
            if i < len(args) and args[i] == tok[1]:
                i += 1
            else:
                return None
        elif tok[0] == "OR":
            if i < len(args) and not args[i].startswith("-"):
                out.append(f"{tok[1]}={args[i]}")
                i += 1
        elif tok[0] == "IF":
            if i < len(args) and args[i] == tok[2]:
                out.append(f"{tok[1]}=1")
                i += 1
        elif tok[0] == "ARGS":
            rest, i = args[i:], len(args)
            if rest:
                if any(ch in r for r in rest for ch in "\"'$`"):
                    return None
                out.append('ARGS="' + " ".join(rest) + '"')
    return out if i == len(args) else None

def _wrapped(cmd: str, cwd: str = "") -> tuple[str | None, str]:
    if not cmd:
        return None, "no command"
    m = _ENTRY_RUN.search(_masked(cmd))
    if not m:
        return None, "no engine entry point"
    module = m.group(1)
    head, tail = cmd[: m.start()], cmd[m.end() :]
    seg, rest = _segment(tail)
    body = seg.rstrip()
    trail = seg[len(body) :]
    args, redirs = [], []
    for raw, w in _words(body):
        if _REDIR.match(w):
            redirs.append(raw)
        elif raw != w:
            return None, f"the quoted argument {raw}"
        else:
            args.append(w)
    table = wrapped_modules(_makefile_for(cwd))
    if module not in table:
        wrapped = ", ".join(f"`{mod}` -> `make {t}`" for mod in sorted(table) for t, _ in table[mod])
        return None, f"no make target wraps `l7r.diagram.{module}` (wrapped: {wrapped})"
    for target, toks in table[module]:
        laid = _lay(args, toks)
        if laid is not None:
            out = f"{head}make {target}" + "".join(" " + v for v in laid)
            if redirs:
                out += " " + " ".join(redirs)
            return out + trail + rest, ""
    return None, f"`make {table[module][0][0]}` cannot carry these arguments"


# ---- A RECIPE COMMENT MUST NOT RUN (feature 212, the GM's request relayed 2026-09-07) ---------------
#
# GUARD_EDIT_OK: feature 212 - THE SAME HAZARD, THREE TIMES. This project comments a recipe with a shell
# no-op, `: "..."`, and inside a double-quoted shell string a backtick or a `$(` is a COMMAND
# SUBSTITUTION. Feature 185 found `test-full`'s phase loop running lint on every gate because its
# comment named `lint` in backticks; feature 207 wrote a comment naming `make test-full` in backticks
# INTO `test-full`, which ran itself, reached the comment again, and recursed 914 levels until the
# container hit its 2,048-process limit and every session's forks failed; feature 188's `make tick`
# ran `_ENGINE_DIRS` as a command out of an interpolated note. Each fix was a reworded line and a note
# saying not to do it again, and the GM ruled that a note is not prevention: *"anytime I see a bad
# problem having occurred, then just commenting, saying not to do it again is not a good way to
# reliably make sure that the problem does not recur."* So the shape is REFUSED at edit time by
# `guard-file-hooks.sh` (the only point that sees every Makefile write before it can execute - a
# gate-phase check runs only inside a target that includes the phase, and the recursion fired from a
# bare `make test-full`) and scanned at the gate by `tests/tooling/test_makefile_recipe_comments.py`
# for the routes an edit can arrive by that the hook does not see (a merge, a scripted sweep).
#
# WHAT COUNTS: a recipe line (a tab, optional `@`, `: "`) whose double-quoted string holds an
# UNESCAPED backtick, or `$$(` / `$${` (make's `$$` is one `$` to the shell, so that IS `$(` when the
# line runs). `\`` and `\$$(` are literal to the shell and pass - the Makefile's own `\$$(MAKE)`
# mention is the worked example. A single-quoted comment (`: '...'`) cannot substitute and passes.
_RECIPE_COMMENT = re.compile(r'^\t\s*@?\s*:\s+"((?:[^"\\]|\\.)*)"')
_UNESCAPED_SUBST = re.compile(r"(?<!\\)`|(?<!\\)\$\$[({]")

def recipe_comment_hazards(text: str) -> list[tuple[int, str]]:
    """(1-based line, the line) for every `: "..."` recipe comment whose string would RUN something."""
    out: list[tuple[int, str]] = []
    for n, line in enumerate(text.split("\n"), 1):
        m = _RECIPE_COMMENT.match(line)
        if m and _UNESCAPED_SUBST.search(m.group(1)):
            out.append((n, line))
    return out


def as_wrapped_target(cmd: str, cwd: str = "") -> str | None:
    """`python3 -m l7r.diagram.<module> <args>` as the make target that wraps it, or None."""
    return _wrapped(cmd, cwd)[0]


def why_not_wrapped_target(cmd: str, cwd: str = "") -> str:
    return _wrapped(cmd, cwd)[1]


def as_paired(cmd: str) -> str | None:
    """`make done` as `make verify` - the paired command - or None to keep refusing.

    `pair-hooks` refuses the gate when no review is beside it, and names `make verify` in the refusal.
    That is a substitution, so it is performed: the gate still runs, and the session is told to
    dispatch the review in the same turn. Only an invocation whose goals are EXACTLY `done` converts;
    `make done FULL=1` and anything carrying another goal keep the refusal, because `verify` is not
    defined to take them and a guard may not guess at what a session meant.
    """
    if not cmd or "FULL" in cmd:
        return None
    # TWO REWRITES MUST NOT RACE FOR ONE COMMAND. `gate-hooks` combines a `quick`+`done` command into
    # `make done`; if this one also fired, the outcome would depend on hook order, and a guard whose
    # result is unpredictable is worse than one that refuses. So a command naming `quick` is left to
    # that conversion, and this one declines it.
    if "quick" in _goals(cmd):
        return None
    segs = _SEP.split(cmd)[0::2]
    hits = [s for s in segs if _MAKE_HEAD.match(s.strip()) and _goals(s) == {"done"}]
    if len(hits) != 1:
        return None
    seg = hits[0]
    rebuilt = re.sub(r"(?<=\s)done(?=\s|$)", "verify", seg, count=1)
    if _goals(rebuilt) != {"verify"}:
        return None
    return cmd.replace(seg, rebuilt, 1)


# ---------------------------------------------------------------------------------------------
# A LEAF CLI, so a guard can depend on the module it uses rather than on all of them (feature 172).
# A split behind an umbrella that imports everything changes no dependency set at all: the closure is
# what matters, not the file count. Guards invoke this file directly.
def _payload() -> tuple[str, str, str]:
    raw = sys.stdin.read()
    try:
        ti = json.loads(raw).get("tool_input", {}) or {}
    except Exception:
        ti = {}
    cmd = ti.get("command", "") or ""
    content = (ti.get("new_string") or "") + (ti.get("content") or "")
    return raw, cmd, content


if __name__ == "__main__":
    RAW, CMD, _CONTENT = _payload()
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    if mode == "targets":
        print("\n".join(sorted(targets(CMD))))
    elif mode == "combine":
        out = combine(CMD)
        if out:
            print(out)
    elif mode == "as-make-target":
        out = as_make_target(CMD)
        if out:
            print(out)
    elif mode == "why-not-make-target":
        print(why_not_make_target(CMD))
    elif mode == "recipe-hazards":
        # the edit's text (new_string + content), one offending line per row: "<n>: <line>"
        for n, line in recipe_comment_hazards(_CONTENT):
            print(f"{n}: {line.strip()}")
    elif mode in ("as-wrapped", "why-not-wrapped"):
        try:
            _cwd = json.loads(RAW).get("cwd", "") or ""
        except Exception:
            _cwd = ""
        if mode == "as-wrapped":
            out = as_wrapped_target(CMD, _cwd)
            if out:
                print(out)
        else:
            print(why_not_wrapped_target(CMD, _cwd))
    elif mode == "as-paired":
        out = as_paired(CMD)
        if out:
            print(out)
    else:
        print(classify(CMD))
