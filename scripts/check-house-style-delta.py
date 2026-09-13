#!/usr/bin/env python3
"""A British spelling in what THIS change wrote - failed at `make quick` (feature 236, item 4).

The hook corrects an Edit, and since the GM's ruling of 2026-09-13 a Bash payload too - warning only
where the command is itself the fix (spec D2, D9). Neither reaches a write that arrives some other
way: a merge, a scripted sweep, a subagent, an editor. So the delta is scanned as a `make quick`
PHASE. Four properties, each of them a measurement or a ruling rather than a preference:

  THE DELTA, NOT THE TREE. 192 pre-existing lines in 83 files carry one of these words
  (`specs/236-catch-mistakes-early-and-cheaply/research.md` R4, counted the way the hook matches).
  Sweeping them is its own work and wants the GM; failing the gate on them would make this check
  impossible to land, which is how a rule ends up unenforced.

  AND EVERY UNTRACKED FILE. The motivating failures were NEW files written through heredocs, and a
  diff against a merge base does not show a file git has never seen.

  THE HOOK'S OWN WORD LIST, READ FROM THE HOOK. `BRIT` in `scripts/house-style-hooks.sh` is the one
  list. A second copy here would drift, and the drift would be silent in the direction that lets a
  word through - the failure mode this repository has already paid for twice (a stale literal agrees
  with itself).

  EXEMPTIONS ARE JUDGED FROM THE WHOLE FILE. A line inside a `<blockquote>`, a 「」 quotation or a
  `SOURCE` block carries no opening marker of its own, so a line-by-line reading would flag the middle
  of a quotation - and the GM's ruling is that a quotation of someone else's text keeps its own
  characters (2026-09-06). A line merely MOVED (its text appears among the delta's removed lines too)
  is not flagged either: a file split forced by the 1,000-line gate moves content without authoring it.

It is a PHASE and not a pytest test on purpose (FR-008c): `make quick` selects tests by changed code
through testmon, and a scan whose own code never changes would sit unexecuted through exactly the
edits it exists to catch.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent

#: files that must QUOTE the forbidden words to state the rule, the GM's own writing, and the files
#: this feature adds that carry the list or its cases - the hook's exemption set, plus these two
_EXEMPT_NAMES = re.compile(
    r"(^|/)(CLAUDE\.md|constitution\.md|l7r-style\.md|house-style-hooks\.sh|test-house-style-hooks\.sh"
    r"|test_hooks_cases\.py|check-house-style-delta\.py|test_house_style_delta\.py"
    r"|test_guard_firing_log\.py|l7r\.md|gm-request\.md)$")
#: `scripts/fixtures/` holds VERBATIM RECORDS - the guard-refusal corpora, and this feature's own
#: replay of 238 real commands. Several of those commands were house-style sweeps, so they carry the
#: forbidden words by necessity; correcting one would falsify the record and break the measurement it
#: reproduces. Same principle as a quotation: it is somebody else's text, even when that somebody is
#: this project's own past (found the first time this check ran over its own delta).
_EXEMPT_DIRS = ("/.clones/", "/host-l7r-repo/", "/scripts/fixtures/")
_GM_VERBATIM = re.compile(r"specs/[^/]+/request\.md$")

_CODE = r"```.*?```|`[^`]*`"
_QUOTE = r"「[^」]*」|『[^』]*』|“[^”]*”|<q\b[^>]*>.*?</q>|<blockquote\b[^>]*>.*?</blockquote>"
_SOURCE = r"<!--\s*SOURCE: GM NOTES.*?<!--\s*END SOURCE\s*-->"
_PROSE_STRAIGHT = r"\"[^\"\n]*\""


def brit_words(hook: pathlib.Path | None = None) -> list[str]:
    """The hook's own `BRIT` table, read from the hook (never copied)."""
    text = (hook or (HERE / "house-style-hooks.sh")).read_text()
    m = re.search(r"BRIT = \((.*?)\)\n", text, re.S)
    if not m:
        raise SystemExit("check-house-style-delta: the BRIT table has moved in house-style-hooks.sh - "
                         "this check reads it from there on purpose, so fix the reader rather than "
                         "copying the list")
    return re.findall(r'"([a-z]+)"', m.group(1))


def exempt_spans(text: str, path: str) -> list[tuple[int, int]]:
    """Character ranges of the whole FILE a house-style rule does not reach."""
    pattern = _CODE + "|" + _QUOTE + "|" + _SOURCE
    if re.search(r"\.(?:md|html|txt)$", path):
        pattern += "|" + _PROSE_STRAIGHT      # in prose a straight quote quotes; in code it is a string
    return [(m.start(), m.end()) for m in re.finditer(pattern, text, re.S | re.I)]


def exempt_path(path: str) -> bool:
    return bool(_EXEMPT_NAMES.search(path) or _GM_VERBATIM.search(path)
                or any(d in "/" + path for d in _EXEMPT_DIRS))


def _git(root: pathlib.Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                          timeout=60).stdout


def delta_lines(root: pathlib.Path) -> tuple[dict[str, list[tuple[int, str]]], set[str]]:
    """({path: [(line number, text)]}, every removed line's text) for the delta and untracked files."""
    base = _git(root, "merge-base", "HEAD", "origin/main").strip() or "HEAD"
    added: dict[str, list[tuple[int, str]]] = {}
    removed: set[str] = set()
    path, line_no = "", 0
    for raw in _git(root, "diff", "-U0", base).split("\n"):
        if raw.startswith("+++ b/"):
            path = raw[6:]
        elif raw.startswith("@@"):
            m = re.search(r"\+(\d+)", raw)
            line_no = int(m.group(1)) if m else 0
        elif raw.startswith("+") and not raw.startswith("+++"):
            added.setdefault(path, []).append((line_no, raw[1:]))
            line_no += 1
        elif raw.startswith("-") and not raw.startswith("---"):
            removed.add(raw[1:].strip())
    for name in _git(root, "ls-files", "--others", "--exclude-standard").split("\n"):
        if not name.strip():
            continue
        p = root / name
        try:
            if p.is_file() and p.stat().st_size < 2_000_000:
                body = p.read_text(errors="replace")
            else:
                continue
        except OSError:
            continue
        added.setdefault(name, []).extend((i, text) for i, text in enumerate(body.split("\n"), 1))
    return added, removed


def findings(root: pathlib.Path) -> list[str]:
    """Every British spelling this change WROTE, as `path:line: word`."""
    words = brit_words()
    pattern = re.compile(r"\b(" + "|".join(words) + r")\b", re.I)
    added, removed = delta_lines(root)
    out = []
    for path, lines in sorted(added.items()):
        if exempt_path(path):
            continue
        p = root / path
        try:
            body = p.read_text(errors="replace")
        except OSError:
            continue
        spans = exempt_spans(body, path)
        offsets = []
        at = 0
        for text in body.split("\n"):
            offsets.append(at)
            at += len(text) + 1
        for n, text in lines:
            if text.strip() in removed:
                continue                      # MOVED, not written (a 1,000-line-gate split)
            for hit in pattern.finditer(text):
                start = (offsets[n - 1] if n - 1 < len(offsets) else 0) + hit.start()
                if any(a <= start < b for a, b in spans):
                    continue                  # a code span names the word; a quotation is someone else's
                out.append(f"{path}:{n}: {hit.group(0)!r} - CLAUDE.md: American spellings, project-wide")
    return out


def selftest() -> None:
    import tempfile

    words = brit_words()
    assert "colour" in words and "centre" in words and len(words) > 40, len(words)
    assert exempt_path("CLAUDE.md") and exempt_path("specs/236-x/request.md")
    assert exempt_path(".claude/skills/diagram/dev/../../../.clones/other/x.md")
    assert not exempt_path("docs/a.md")
    spans = exempt_spans("a `colour` span\n<blockquote>\nthe colour there\n</blockquote>\nplain colour\n", "docs/a.md")
    text = "a `colour` span\n<blockquote>\nthe colour there\n</blockquote>\nplain colour\n"
    inside = [any(a <= text.index(w) < b for a, b in spans) for w in ("`colour`", "<blockquote>")]
    assert all(inside), spans
    assert not any(a <= text.rindex("colour") < b for a, b in spans), "the plain one is not exempt"
    # the whole thing, over a real git tree
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        subprocess.run(["git", "-C", td, "init", "-q", "-b", "main"], check=True)
        subprocess.run(["git", "-C", td, "config", "user.email", "x@y"], check=True)
        subprocess.run(["git", "-C", td, "config", "user.name", "x"], check=True)
        (root / "base.md").write_text("the pre-existing colour stays\n")
        subprocess.run(["git", "-C", td, "add", "-A"], check=True)
        subprocess.run(["git", "-C", td, "commit", "-qm", "base"], check=True)
        subprocess.run(["git", "-C", td, "branch", "-f", "origin/main"], check=True)
        subprocess.run(["git", "-C", td, "update-ref", "refs/remotes/origin/main", "HEAD"], check=True)
        (root / "new.md").write_text("a fresh centre here\n")            # untracked
        (root / "base.md").write_text("the pre-existing colour stays\nan added behaviour line\n")
        got = findings(root)
        assert any("new.md:1" in x for x in got), got
        assert any("base.md:2" in x for x in got), got
        assert not any("base.md:1" in x for x in got), "a pre-existing line is not in the delta"
    print("check-house-style-delta selftest ok")


def main(argv: list[str]) -> int:
    if "--selftest" in argv:
        selftest()
        return 0
    root = pathlib.Path(argv[0] if argv and not argv[0].startswith("--") else ".").resolve()
    bad = findings(root)
    if not bad:
        return 0
    print("\n".join(bad))
    print(f"\nhouse style: {len(bad)} British spelling(s) in what this change wrote. CLAUDE.md is "
          "project-wide - American spellings, hyphens only. A quotation of someone else's text keeps "
          "its own characters (GM 2026-09-06): put it inside 「」, “”, <q> or <blockquote>, or in a "
          "backtick span if the word is being NAMED rather than used.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
