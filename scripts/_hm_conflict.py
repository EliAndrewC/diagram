#!/usr/bin/env python3
"""Does this text carry an unresolved merge conflict, and what would this command stage? (feature 241)

ONE detector, shared by the guard and its push/gate backstop, the way `_hm_make.recipe_comment_hazards` is
shared with the recipe-comment backstop: two copies drift, and the copy in the backstop is the one nobody
reads until it is wrong.

WHAT COUNTS AS A CONFLICT. The TRIPLE `git merge` leaves, in order, each at COLUMN 0: seven `<`, a line of
exactly seven `=`, then seven `>`. Three properties follow from that and each one is load-bearing:

  * any ONE marker alone is not a conflict - a line of seven `=` is an ordinary Markdown underline, and a
    session writing about merges types the other two;
  * COLUMN 0 is what exempts prose. An indented example, and every inline `<<<<<<<` in a backtick span,
    starts with something else. This feature's own spec, research and suite all carry markers and none of
    them is flagged;
  * and there is NO fenced-block exemption, deliberately. One was written and removed the same day: git
    writes its markers at column 0 wherever the conflict falls, INCLUDING inside a fenced block in a
    Markdown file, and 7 of the 23 files of the 2026-09-13 incident were Markdown or HTML - exactly the
    class a fence exemption would have hidden. A file that must show a triple at column 0 says so with
    `CONFLICT_MARKERS_OK: <reason>` in its first 40 lines, the shape `FILE_SIZE_OK` uses, because a
    whole-file exemption is argued rather than tokenized.

WHAT A COMMAND WOULD STAGE. Asked of GIT, never enumerated: `git add --dry-run` answers it exactly, for
every form at once - `-A`, `.` (which is scoped to the CWD, not the tree), `-u`, a directory, a glob. The
enumeration this replaced was wrong in four ways at once, and one of them would have made the guard fire on
correct work (`git add .` in a clean subdirectory while a marker sat elsewhere), which is the failure the
whole design exists to avoid.
"""

from __future__ import annotations

import os
import pathlib
import re
import shlex
import subprocess
import sys

OPEN, MID, CLOSE = "<" * 7, "=" * 7, ">" * 7
EXEMPT = "CONFLICT_MARKERS_OK:"
HEAD_LINES = 40  # where a file-level exemption must stand, as FILE_SIZE_OK does


def declares_exemption(line: str) -> str:
    """The file-level exemption's stated reason, or "" - A MENTION IS NOT A DECLARATION.

    GUARD_EDIT_OK: feature 241, fixing this guard's own version of the defect it exists to avoid. The
    first rule was `EXEMPT in line`, and the very first run of `--list` reported THIS FILE as exempt:
    the docstring above describes the marker in a backtick span, inside the first 40 lines, with a
    placeholder reason - so the one file whose job is to distinguish a mention from an invocation had
    silently exempted itself, and a real triple in it would have been invisible to the backstop.

    So a declaration stands at the START of its line, modulo indentation and comment punctuation
    (`#`, `*`, `:`, `-`, `//`), the way `FILE_SIZE_OK` is read; a placeholder reason (`<reason>`) is
    documentation, not a declaration; and the reason floor is the project's two words.
    """
    m = re.match(rf"^[\s#*:/;\-]*{re.escape(EXEMPT)}(.*)$", line)
    if not m:
        return ""
    reason = m.group(1).strip()
    if reason.startswith("<") or len(reason.split()) < 2:
        return ""
    return reason


def has_conflict(text: str) -> bool:
    """The triple, in order, at column 0 - unless the file claims its exemption with a reason."""
    lines = text.splitlines()
    for line in lines[:HEAD_LINES]:
        if declares_exemption(line):
            return False
    state = 0
    for line in lines:
        if state == 0 and line.startswith(OPEN):
            state = 1
        elif state == 1 and line.rstrip() == MID:
            state = 2
        elif state == 2 and line.startswith(CLOSE):
            return True
    return False


def conflicted(paths: list[str] | tuple[str, ...]) -> list[str]:
    """Which of these carry a conflict. Unreadable as text - binary, a directory, gone - is SKIPPED."""
    bad = []
    for p in paths:
        f = pathlib.Path(p)
        try:
            if not f.is_file():
                continue
            text = f.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        if has_conflict(text):
            bad.append(str(p))
    return sorted(set(bad))


def _assignments(cmd: str) -> dict[str, str]:
    """Simple `VAR=value` assignments made in the command itself.

    The recorded merge-ending command in this repository's own corpus is
    `CL=/diagram/.clones/<name>; git -C $CL add -A && git -C $CL commit ...`, so a guard that reads `-C`
    without expanding `$CL` resolves a repository that does not exist, finds no paths, and permits - which
    is how the first version of this file missed the very incident it was written for. Feature 204's
    `_hm_tree.py judge` walks the same ground for the same reason.
    """
    out: dict[str, str] = {}
    for m in re.finditer(r"(?:^|[;&|\s])([A-Za-z_][A-Za-z0-9_]*)=([^\s;&|]+)", cmd):
        out[m.group(1)] = m.group(2).strip("\"'")
    return out


def _expand(tok: str, vars_: dict[str, str]) -> str:
    for k, v in vars_.items():
        tok = tok.replace(f"${{{k}}}", v).replace(f"${k}", v)
    return tok


def staged_by(cmd: str, cwd: str) -> list[str]:
    """The files a `git add` / `git commit` in this command would stage, asked of git."""
    vars_ = _assignments(cmd)
    here = cwd
    paths: list[str] = []
    for piece in re.split(r"&&|\|\||;|\|", cmd):
        try:
            toks = [_expand(t, vars_) for t in shlex.split(piece, comments=True)]
        except ValueError:
            toks = [_expand(t, vars_) for t in piece.split()]
        if toks and toks[0] == "cd" and len(toks) > 1:
            here = toks[1] if os.path.isabs(toks[1]) else os.path.join(here, toks[1])
            continue
        if "git" not in toks:
            continue
        rest = toks[toks.index("git") + 1 :]
        repo = here
        while rest and rest[0] in ("-C", "-c") and len(rest) >= 2:
            if rest[0] == "-C":
                repo = rest[1] if os.path.isabs(rest[1]) else os.path.join(here, rest[1])
            rest = rest[2:]
        if not rest or rest[0] not in ("add", "commit"):
            continue
        sub, args = rest[0], [a for a in rest[1:] if a not in ("--dry-run", "-n")]

        def _run(*a: str) -> list[str]:
            r = subprocess.run(["git", "-C", repo, *a], capture_output=True, text=True, check=False, cwd=repo if os.path.isdir(repo) else None)
            return [ln for ln in r.stdout.splitlines() if ln]

        if sub == "add":
            # ASK GIT. `add --dry-run` prints `add '<path>'` for exactly what it would stage, so `.` stays
            # scoped to the cwd, a directory expands, and -A/-u mean what git means by them.
            for ln in _run("add", "--dry-run", "--ignore-missing", *args):
                m = re.match(r"^(?:add|remove) '(.*)'$", ln.strip())
                if m:
                    paths.append(os.path.join(repo, m.group(1)))
        else:
            named = [a for a in args if not a.startswith("-") and a != "--"]
            flags = [a for a in args if a.startswith("-")]
            # a commit carries what is already staged; -a adds tracked changes; named paths add those
            paths += [os.path.join(repo, p) for p in _run("diff", "--cached", "--name-only")]
            if any(f in ("-a", "--all") for f in flags) or any(f.startswith("-") and not f.startswith("--") and "a" in f[1:] for f in flags):
                paths += [os.path.join(repo, p) for p in _run("diff", "--name-only")]
            if named:
                # a message is not a pathspec: drop the argument of -m/--message before asking git
                drop = set()
                for i, a in enumerate(args):
                    if a in ("-m", "--message", "-F", "--file", "--author", "--date") and i + 1 < len(args):
                        drop.add(args[i + 1])
                keep = [p for p in named if p not in drop]
                if keep:
                    paths += [os.path.join(repo, ln[3:]) for ln in _run("status", "--porcelain", "--", *keep)]
    return sorted(set(paths))


def tracked_files(root: str) -> list[str]:
    r = subprocess.run(["git", "-C", root, "ls-files", "-z"], capture_output=True, text=True, check=False)
    return [str(pathlib.Path(root) / n) for n in r.stdout.split("\0") if n]


def _selftest() -> int:
    """Prove the detector FIRES, the way every static check wired into the push proves it (GUARD_EDIT_OK:
    feature 241 - a checker that cannot fail is worth nothing, and this one is called by
    `sync-with-main.sh` and by the gate's static phase before it is trusted).

    The markers are BUILT here rather than typed, so this file carries no triple of its own and needs no
    exemption to pass its own scan.
    """
    import tempfile

    triple = f"{OPEN} HEAD\nmine\n{MID}\ntheirs\n{CLOSE} other\n"
    cases: list[tuple[str, str, bool]] = [
        ("the triple at column 0", triple, True),
        ("a fence does not exempt it", f"doc\n\n```\n{triple}```\n", True),
        ("a lone underline is Markdown", f"A heading\n{MID}\n\ntext\n", False),
        ("a lone open marker is prose", f"{OPEN} is what git writes\n", False),
        ("indented, the way prose shows it", "".join("    " + ln + "\n" for ln in triple.splitlines()), False),
        ("out of order is not a conflict", f"{CLOSE} x\n{MID}\n{OPEN} y\n", False),
        ("the file-level exemption, with a reason", f"{EXEMPT} this doc must show one\n{triple}", False),
        ("...as a comment, the way a script declares it", f"# {EXEMPT} a fixture that must hold one\n{triple}", False),
        ("...but not a one-word reason", f"{EXEMPT} x\n{triple}", True),
        ("...and not a MENTION mid-sentence - the defect --list found in this very file",
         f"a doc saying to put `{EXEMPT} <reason>` in the first 40 lines\n{triple}", True),
        ("...nor a placeholder reason", f"{EXEMPT} <reason>\n{triple}", True),
        ("...and not past the head", "\n" * HEAD_LINES + f"{EXEMPT} too far down to count\n" + triple, True),
    ]
    bad = [name for name, text, want in cases if has_conflict(text) is not want]

    # and the COMMAND half: the recorded incident's own shape, which the first implementation missed.
    with tempfile.TemporaryDirectory() as d:
        subprocess.run(["git", "-C", d, "init", "-q"], check=False)
        (pathlib.Path(d) / "f.md").write_text(triple, encoding="utf-8")
        (pathlib.Path(d) / "sub").mkdir()
        (pathlib.Path(d) / "sub" / "ok.md").write_text("clean\n", encoding="utf-8")
        if not conflicted(staged_by(f"CL={d}; git -C $CL add -A", "/")):
            bad.append("the incident shape `CL=...; git -C $CL add -A`")
        if not conflicted(staged_by("git add -A", d)):
            bad.append("a bare `git add -A` in the tree")
        if conflicted(staged_by("git add .", str(pathlib.Path(d) / "sub"))):
            bad.append("`git add .` in a clean subdirectory must pass")
        if conflicted(staged_by('git commit -m "a message naming f.md is not a pathspec"', d)):
            bad.append("a commit message must not be read as a pathspec")

    if bad:
        print("_hm_conflict selftest FAILED: " + "; ".join(bad), file=sys.stderr)
        return 1
    print(f"_hm_conflict selftest: {len(cases)} content cases + 4 command shapes")
    return 0


def exemptions(root: str) -> list[tuple[str, str]]:
    """Every tracked file declaring the file-level marker, with its stated reason.

    GUARD_EDIT_OK: feature 241 - a whole-file exemption nobody can enumerate is one nobody revisits,
    which is feature 173's argument for `check-file-scale.py --list`, and `make audit` prints both.
    """
    found = []
    for p in tracked_files(root):
        try:
            head = pathlib.Path(p).read_text(encoding="utf-8").splitlines()[:HEAD_LINES]
        except (OSError, UnicodeDecodeError):
            continue
        for line in head:
            reason = declares_exemption(line)
            if reason:
                found.append((os.path.relpath(p, root), reason))
                break
    return sorted(found)


def main(argv: list[str]) -> int:
    if argv and argv[0] == "--selftest":
        return _selftest()
    if argv and argv[0] == "--list":
        taken = exemptions(argv[1] if len(argv) > 1 else ".")
        for path, reason in taken:
            print(f"  {path}: {reason[:96]}")
        print(f"  {len(taken)} file(s) declare {EXEMPT[:-1]}" + (" - none" if not taken else ""))
        return 0
    if not argv or argv[0] != "--tracked":
        print("usage: _hm_conflict.py [--selftest | --tracked <root>]   # --tracked exits 1 naming any tracked file with a conflict", file=sys.stderr)
        return 2
    root = argv[1] if len(argv) > 1 else "."
    files = tracked_files(root)
    bad = conflicted(files)
    if not bad:
        print(f"conflict-markers: none in {len(files)} tracked file(s)")
        return 0
    print("\nCONFLICT MARKERS IN TRACKED FILES - a merge was committed unresolved:", file=sys.stderr)
    for p in bad:
        print(f"  {p}", file=sys.stderr)
    print("\nResolve each and commit the resolution. The history here is never rewritten, so these cannot be", file=sys.stderr)
    print("amended away - the fix is a commit on top. A file that must SHOW a triple says so with", file=sys.stderr)
    print(f"`{EXEMPT} <reason>` in its first {HEAD_LINES} lines (feature 241).\n", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
