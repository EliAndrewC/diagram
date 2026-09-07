#!/usr/bin/env python3
"""Where does a write LAND? The main-tree guard's verdict (feature 204).
(GUARD_EDIT_OK: a NEW helper - the verdict half of main-tree-hooks.sh, lifted out of bash.)

WHY THIS IS PYTHON (spec D7). `main-tree-hooks.sh` grew four regexes and three feature-numbered
patches on top of them, and judged a command by where the SHELL STOOD: from 2026-08-30 to
2026-09-07 it refused 173 commands, of which two were the shape it was built for (`cd /diagram &&
git commit`) and 146 contained no `cd` at all - a subagent whose shell happened to start in the
mirror, writing to the scratchpad or to a clone by absolute path. Judging where the write LANDS is
a small interpreter (the shell's directory walked through the command's own `cd`s, variables and
subshells), and that is testable as one function rather than as a bash pipeline. The corpus those
173 make is `scripts/fixtures/main-tree-refusals-2026-09.json`, replayed by the suite.

Three verdicts, and the ladder from feature 164 decides between them:
  allow    - no write lands in main. Silent (spec D3: a guard that speaks on correct work trains
             sessions to skip what it says).
  rewrite  - a write lands in main only because of where the shell stands, or where a `cd` in the
             command put it. The command is moved to the session's own clone at the same relative
             position - `cd <main>[/sub]` becomes `cd <clone>[/sub]`; a write from the standing cwd
             gets `cd <clone>[/sub] && ` prepended - and the session is TOLD (spec D4: moving the
             shell cures the leak for the following commands too, not just this one).
  refuse   - the write names a path inside main ABSOLUTELY (`git -C /diagram commit`, `> /diagram/x`):
             the session said what it meant, and a guard never guesses at that (spec FR-003, D2);
             or the clone cannot be resolved / does not exist; or the shape cannot be rebuilt
             (spec FR-005). Every rewrite is RE-JUDGED before it is emitted, so the guard never
             returns a command that it would itself refuse.

UNKNOWN RESOLVES TOWARD MAIN (spec D6): a `cd` whose target cannot be resolved (`cd $(somewhere)`,
an unassigned variable) leaves the directory unknown, and an unknown directory counts as wherever
the shell was last known to be. So the precision fix cannot become a bypass.

`python3 -c` REMAINS A WRITE (spec D5): it was the guard's commonest false positive on read-only
diagnostics, but an interpreter can write anywhere, and its cost is zero now - from a clone it is
allowed, from main it is moved.
"""

from __future__ import annotations

import json
import os
import posixpath
import re
import sys

from _hm_shape import _strip_heredocs

# git subcommands that write (feature 169's list, kept exactly; `branch -<flag>` is handled inline)
_GIT_WRITES = frozenset(
    "commit add merge rebase reset checkout restore rm mv apply am stash cherry-pick push pull clean tag".split()
)
# tools whose PATH ARGUMENTS are what they write; the value says which arguments. `cp`, `ln` and
# `install` write their LAST argument only - copying FROM main is a read, and the first draft of
# this judged `cp /diagram/scripts/x /tmp/` as a write in main.
_FILE_TOOLS = {
    "vim": "all", "vi": "all", "nano": "all", "emacs": "all", "tee": "all", "touch": "all",
    "mkdir": "all", "rmdir": "all", "rm": "all", "mv": "all", "chmod": "all", "chown": "all",
    "truncate": "all", "cp": "last", "ln": "last", "install": "last",
}
_WRAPPERS = frozenset("sudo nohup setsid env command exec time nice builtin".split())
_ASSIGN = re.compile(
    r"""(?:^|[;&|\n(]|&&|\|\|)\s*(?:export\s+)?([A-Za-z_]\w*)=(?:"([^"\n]*)"|'([^'\n]*)'|([^\s;&|)]*))"""
)
_VAR = re.compile(r"\$\{(\w+)\}|\$(\w+)")
_QUOTED = re.compile(r"""(["'])((?:\\.|(?!\1).)*)\1""", re.S)
_PLAIN_QUOTE_BODY = re.compile(r"^[^\s;|&()<>`\n]*$")
_REDIRECT = re.compile(r"(?<![<>])\d?>{1,2}\|?\s*([^\s;&|()<>]+)")
_FUNCTION_DEF = re.compile(r"^\s*[\w-]+\s*\(\s*\)")


def _quotes_to_paths(cmd: str) -> str:
    """A quoted string is an argument, never a command - but it may be the PATH we are judging.

    `_hm_shape._strip_quotes` blanks every quoted string, which is right for a guard asking "is this
    an invocation" and wrong for one asking "where does this land": `cd "$C"` would lose its
    variable and `> "$SP/x"` its target. So a quote whose body is one plain word (no whitespace, no
    separator, no redirect) keeps its body unquoted; anything else - a message, a sed script with
    spaces, a python program - is blanked to an empty pair.
    """

    def keep(m: re.Match[str]) -> str:
        body = m.group(2)
        return body if _PLAIN_QUOTE_BODY.match(body) else m.group(1) * 2

    return _QUOTED.sub(keep, cmd)


def _sanitize(cmd: str) -> str:
    text = _quotes_to_paths(_strip_heredocs(cmd))
    text = re.sub(r"\d*>&[0-9-]", " ", text)  # 2>&1, >&2 - not files (feature 172's false positive)
    return re.sub(r"\d*>\s*/dev/null", " ", text)


def _expand(token: str, env: dict[str, str], home: str) -> str | None:
    """A token with its variables and `~` substituted, or None when something in it cannot be."""
    if token.startswith("~"):
        token = home + token[1:]
    for _ in range(6):
        if "$" not in token:
            break
        token = _VAR.sub(lambda m: env.get(m.group(1) or m.group(2), m.group(0)), token)
    if "$" in token or "`" in token:
        return None
    return token


def _env_from(cmd: str, cwd: str | None, home: str) -> dict[str, str]:
    """`NAME=value` assignments at command positions, resolved through each other, in order.

    The corpus's second-commonest shape is `C=/diagram/.clones/x; git -C $C ...` and
    `S=/tmp/...; ( cd $S && ... )` - twelve of 173 - and a guard that cannot read its own
    command's assignments cannot tell those from a write in main.
    """
    env = {"HOME": home}
    if cwd:
        env["PWD"] = cwd
    for m in _ASSIGN.finditer(_strip_heredocs(cmd)):
        name = m.group(1)
        value = next((g for g in m.groups()[1:] if g is not None), "")
        env[name] = _expand(value, env, home) or value
    return env


def _resolve(token: str, env: dict[str, str], home: str, effective: str | None) -> str | None:
    """A path token as an absolute, normalized path - or None when it cannot be known."""
    expanded = _expand(token.strip("\"'"), env, home)
    if not expanded:
        return None
    if expanded.startswith("/"):
        return posixpath.normpath(expanded)
    if effective is None:
        return None
    return posixpath.normpath(posixpath.join(effective, expanded))


def classify(path: str | None, main: str) -> str:
    """main (the mirror, outside its .clones), clone, elsewhere, or unknown."""
    if path is None:
        return "unknown"
    clones = main + "/.clones"
    if path == clones or path.startswith(clones + "/"):
        return "clone"
    if path == main or path.startswith(main + "/"):
        return "main"
    return "elsewhere"


def _segments(text: str) -> list[tuple[str, str]]:
    """The command split at its separators: ('seg', text), ('push', '') at `(`, ('pop', '') at `)`.

    A subshell's `cd` must not leak past its `)` - `S=/tmp/x; ( cd $S && cat > m.py ); git commit`
    commits where the shell STOOD, not in /tmp/x - so parentheses push and pop the directory.
    """
    out: list[tuple[str, str]] = []
    buf: list[str] = []
    i, n = 0, len(text)

    def flush() -> None:
        seg = "".join(buf).strip()
        buf.clear()
        if seg:
            out.append(("seg", seg))

    while i < n:
        two = text[i : i + 2]
        ch = text[i]
        if two in ("&&", "||"):
            flush()
            i += 2
        elif two == "$(":
            flush()
            out.append(("push", ""))
            i += 2
        elif ch in ";|&\n":
            flush()
            i += 1
        elif ch == "(":
            flush()
            out.append(("push", ""))
            i += 1
        elif ch == ")":
            flush()
            out.append(("pop", ""))
            i += 1
        elif ch in "{}":
            flush()
            i += 1
        else:
            buf.append(ch)
            i += 1
    flush()
    return out


def _words(seg: str) -> list[str]:
    """The segment's words with leading wrappers and `VAR=value` prefixes removed."""
    toks = seg.split()
    while toks:
        t = toks[0]
        if t in _WRAPPERS or re.match(r"^[A-Za-z_]\w*=", t):
            toks.pop(0)
        elif t == "timeout" and len(toks) > 1:
            toks = toks[2:]
        else:
            break
    return toks


def _git_write(toks: list[str], env: dict[str, str], home: str, eff: str | None) -> tuple[str | None, str] | None:
    """(target, 'named'|'shell') when a git invocation writes, else None."""
    i, c_path = 1, None
    while i < len(toks):
        t = toks[i]
        if t == "-C" and i + 1 < len(toks):
            c_path = toks[i + 1]
            i += 2
        elif t == "-c" and i + 1 < len(toks):
            i += 2
        elif t.startswith("-"):
            i += 1
        else:
            break
    if i >= len(toks):
        return None
    sub = toks[i]
    writes = sub in _GIT_WRITES or (sub == "branch" and any(t.startswith("-") for t in toks[i + 1 :]))
    if not writes:
        return None
    if c_path is None:
        return (eff, "shell")
    how = "named" if c_path.strip("\"'").startswith("/") else "shell"
    return (_resolve(c_path, env, home, eff), how)


def _tool_paths(tool: str, toks: list[str]) -> list[str]:
    args = [t for t in toks[1:] if t not in ("''", '""', "--") and "<<" not in t]
    if tool == "sed":
        keep: list[str] = []
        skip_next, script_seen = False, "-e" in args or "--expression" in args
        for t in args:
            if skip_next:
                skip_next = False
                continue
            if t in ("-e", "--expression", "-f", "--file"):
                skip_next = True
                continue
            if t.startswith("-"):
                continue
            if not script_seen:
                script_seen = True  # the first bare argument is the sed script, not a file
                continue
            keep.append(t)
        return keep
    args = [t for t in args if not t.startswith("-")]
    if _FILE_TOOLS.get(tool) == "last":
        return args[-1:]
    return args


def _path_write(p: str, env: dict[str, str], home: str, eff: str | None) -> tuple[str | None, str]:
    bare = p.strip("\"'")
    expanded = _expand(bare, env, home)
    if expanded is not None and expanded.startswith("/"):
        return (posixpath.normpath(expanded), "named")
    if expanded is None:
        return (None, "named" if bare.startswith("/") else "shell")
    return (_resolve(bare, env, home, eff), "shell")


def _writes_in(seg: str, env: dict[str, str], home: str, eff: str | None) -> list[tuple[str | None, str]]:
    """Every write in one segment as (target directory or file path, 'named'|'shell')."""
    found: list[tuple[str | None, str]] = []
    toks = _words(seg)
    if toks:
        head = toks[0]
        base = head.rsplit("/", 1)[-1]
        if head == "git":
            w = _git_write(toks, env, home, eff)
            if w:
                found.append(w)
        elif base == "make":
            found.append((eff, "shell"))
        elif re.match(r"^python3?$", base) and len(toks) > 1 and toks[1] == "-c":
            found.append((eff, "shell"))
        elif base == "sed" and any(t.startswith("-i") or t == "--in-place" for t in toks[1:]):
            found.extend(_path_write(p, env, home, eff) for p in _tool_paths("sed", toks))
        elif base in _FILE_TOOLS:
            found.extend(_path_write(p, env, home, eff) for p in _tool_paths(base, toks))
    for m in _REDIRECT.finditer(seg):
        found.append(_path_write(m.group(1), env, home, eff))
    return found


def walk(cmd: str, cwd: str | None, main: str, home: str) -> dict:
    """The effective directory through the command, and every write with where it lands."""
    env = _env_from(cmd, cwd, home)
    text = _sanitize(cmd)
    eff: str | None = cwd or None
    hint = classify(eff, main)  # where the shell was last KNOWN to be (spec D6)
    stack: list[tuple[str | None, str]] = []
    targets: list[dict] = []
    cd_into_main = False
    for kind, seg in _segments(text):
        if kind == "push":
            stack.append((eff, hint))
            continue
        if kind == "pop":
            if stack:
                eff, hint = stack.pop()
            continue
        toks = _words(seg)
        if toks and toks[0] in ("cd", "pushd"):
            if len(toks) == 1 or toks[1] == "--":
                eff = home
            elif toks[1] == "-":
                eff = None
            else:
                eff = _resolve(toks[1], env, home, eff)
            if eff is not None:
                hint = classify(eff, main)
                if hint == "main":
                    cd_into_main = True
            continue
        if toks and toks[0] == "popd":
            eff = None
            continue
        for path, how in _writes_in(seg, env, home, eff):
            cls = classify(path, main)
            if cls == "unknown":
                cls = hint if hint == "main" else "elsewhere"  # D6: unknown resolves toward main
            targets.append({"path": path, "class": cls, "how": how, "segment": seg[:120]})
    return {"targets": targets, "final_dir": eff, "cd_into_main": cd_into_main, "standing": classify(cwd, main)}


def _rewrite_cds(cmd: str, main: str, clone: str) -> str:
    """Every command-position `cd <main>[/sub]` in the ORIGINAL text becomes `cd <clone>[/sub]`.

    Only a literal absolute path is rewritten - a cd reached through a variable is not located in
    the original text, and the re-judge below turns that into a `shape` refusal (FR-005).
    """
    pat = re.compile(
        r"((?:^|[;&|(\n]|&&|\|\|)\s*(?:\(\s*)?(?:cd|pushd)\s+)([\"']?)"
        + re.escape(main)
        + r"(?=/(?!\.clones(?:/|$))|[\"'\s;&|)]|$)",
        re.M,
    )
    return pat.sub(lambda m: m.group(1) + m.group(2) + clone, cmd)


def _context_line(verdict: dict, main: str) -> str:
    ctx = verdict["context"]
    clone = ctx["clone"]
    if verdict["cause"] == "cd":
        opening = (
            f"This command cd'd into {main} - the MIRROR, main's tree, never a workspace - and then "
            f"wrote there. The cd was rewritten to your clone, {clone}, at the same relative position"
        )
    else:
        opening = (
            f"Your shell was standing in {ctx['cwd']}, inside {main} - the MIRROR, main's tree, never a "
            f"workspace - so this command's write would have landed in main. It was rewritten to run in "
            f"your clone: `cd {clone}` was prepended"
        )
    return (
        f"{opening}, and the shell stays in the clone for later commands. Read main with "
        f"`git -C {main} <read>`; do everything else in the clone (CLAUDE.md, 'Session clones'). "
        "Rewritten rather than refused: a refusal costs a model round trip to say the same thing. "
        "(scripts/main-tree-hooks.sh; feature 204)"
    )


def explain(verdict: dict, main: str) -> str:
    """The refusal text for a `refuse` verdict - naming the ACTUAL cause (FR-007)."""
    ctx = verdict["context"]
    reason = verdict["reason"]
    clone = ctx.get("clone") or "<your clone under .clones/>"
    if verdict["cause"] == "named":
        where = "this command names a path inside the mirror and writes to it"
    elif verdict["cause"] == "cd":
        where = f"this command cds into {main} - the MIRROR - and then writes there"
    else:
        where = f"your shell is standing in {ctx['cwd']}, inside {main} - the MIRROR - and this command writes where it stands"
    lines = [f"BLOCKED: {where}.", ""]
    lines.append("Main is the integration point, never a workspace. The only write a session makes there is")
    lines.append("render-sync, and that names the tree with `git -C` from sync-with-main.sh rather than cd-ing.")
    lines.append("")
    if reason == "named-main":
        named = ", ".join(t["path"] for t in ctx["targets"] if t["class"] == "main" and t["how"] == "named")
        lines.append(f"Named: {named}")
        lines.append("A write that merely LANDS in main because of where the shell stands is moved to your clone")
        lines.append("(feature 204); one that names main by its path says what it means, and a guard never guesses at")
        lines.append(f"that. Do it in your clone instead: {clone}.")
    elif reason == "clone-unresolved":
        lines.append("It would have been moved to your clone, but this session's clone cannot be resolved: no claim")
        lines.append("under .clones/.session-clones, no /rename record in the transcript, no sessions entry. Ask the")
        lines.append("GM to /rename the session, then work in .clones/<kebab-name>.")
    elif reason == "clone-missing":
        lines.append(f"It would have been moved to your clone, {clone}, which does not exist yet. Create it:")
        lines.append(f"  git clone {main} {clone} && ( cd {clone} && scripts/sync-with-main.sh sync-in )")
    else:
        lines.append("It would have been moved to your clone, but the command's shape could not be rewritten safely")
        lines.append("(it opens with a function definition, or the cd into main is reached through a variable and")
        lines.append(f"cannot be located in the original text). Run it as `( cd {clone} && ... )` yourself.")
    lines.append("")
    lines.append(f"Reading main stays fine: `git -C {main} <read>`. If this genuinely needs to write in main, put")
    lines.append("MAIN_TREE_OK in the command with the reason, and the reason ships with it.")
    lines.append("")
    lines.append("(scripts/main-tree-hooks.sh; features 169 and 204)")
    return "\n".join(lines)


def judge(payload: dict, main: str, clone: str | None, home: str, resolved: bool = False) -> dict:
    """The verdict for one hook payload. `resolved` says the caller already tried to find the clone."""
    ti = payload.get("tool_input") or {}
    cmd = ti.get("command") or ""
    cwd = payload.get("cwd") or None
    main = main.rstrip("/")
    w = walk(cmd, cwd, main, home)
    named = [t for t in w["targets"] if t["class"] == "main" and t["how"] == "named"]
    shell = [t for t in w["targets"] if t["class"] == "main" and t["how"] == "shell"]
    context = {
        "cwd": cwd, "standing": w["standing"], "final_dir": w["final_dir"], "cd_into_main": w["cd_into_main"],
        "targets": w["targets"], "clone": clone,
    }

    def out(verdict: str, reason: str, cause: str, **more: object) -> dict:
        return {"verdict": verdict, "reason": reason, "cause": cause, "context": context, **more}

    if named:
        return out("refuse", "named-main", "named")
    if not shell:
        return out("allow", "no-write-in-main", "")
    cause = "cd" if w["cd_into_main"] else "standing"
    if clone is None:
        return out("refuse" if resolved else "needs-clone", "clone-unresolved", cause)
    if not os.path.exists(os.path.join(clone, ".git")):
        return out("refuse", "clone-missing", cause)
    if _FUNCTION_DEF.match(cmd):
        return out("refuse", "shape", cause)
    new = _rewrite_cds(cmd, main, clone)
    prepended = False
    w2 = walk(new, cwd, main, home)
    if any(t["class"] == "main" for t in w2["targets"]) and w["standing"] == "main":
        sub = os.path.relpath(cwd, main) if cwd and cwd != main else ""
        where = clone if sub in ("", ".") else posixpath.join(clone, sub)
        new = f"cd {where} && {new}"
        prepended = True
        w2 = walk(new, cwd, main, home)
    if any(t["class"] == "main" for t in w2["targets"]):
        return out("refuse", "shape", cause)  # re-judged and still lands in main: never emit that
    context["prepended"] = prepended
    verdict = out("rewrite", "moved-to-clone", cause, command=new)
    updated = dict(ti)
    updated["command"] = new
    verdict["hook"] = {"hookSpecificOutput": {
        "hookEventName": "PreToolUse", "updatedInput": updated, "additionalContext": _context_line(verdict, main),
    }}
    return verdict


def main_cli() -> int:
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    home = os.environ.get("HOME", "/home/agent")
    if mode == "judge" and len(sys.argv) > 2:
        # judge <main>            -> allow | needs-clone | refuse(named-main)
        # judge <main> <clone>    -> the clone was looked up ('' = not found): allow | rewrite | refuse
        try:
            payload = json.load(sys.stdin)
        except Exception:
            payload = {}
        clone = sys.argv[3] if len(sys.argv) > 3 and sys.argv[3] else None
        print(json.dumps(judge(payload, sys.argv[2], clone, home, resolved=len(sys.argv) > 3)))
        return 0
    if mode == "explain" and len(sys.argv) > 2:
        # explain <main>  - the refusal text for the verdict JSON on stdin
        print(explain(json.load(sys.stdin), sys.argv[2].rstrip("/")))
        return 0
    if mode == "hook":
        # hook  - the hookSpecificOutput for a rewrite verdict on stdin
        print(json.dumps(json.load(sys.stdin)["hook"]))
        return 0
    if mode == "log-context":
        # log-context  - the verdict without the (duplicated) hook payload, for the firing record
        v = json.load(sys.stdin)
        v.pop("hook", None)
        print(json.dumps(v))
        return 0
    print("usage: _hm_tree.py judge <main> [clone] | explain <main> | hook | log-context", file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main_cli())
