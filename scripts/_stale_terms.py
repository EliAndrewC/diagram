#!/usr/bin/env python3
"""After a value changed in a feature directory, where does the OLD value still stand? (feature 253)

WHY. Later `spec-fidelity` rounds are about 61% of what the spec review process costs (274 of 425 recorded
runs, 2026-09-19), and a later round costs nearly what a first reading does. In features 251 and 252 most of
what those rounds found was text the session had left STALE: a tier moved in one table, and another
requirement, a results table and a success criterion went on saying the old thing. Each was a real finding,
and each cost a subagent run to be told something a search finds for nothing. The GM, 2026-09-19: *"That
does seem like a good idea so please implement that suggestion."*

THE RULE. Compare the state the previous review round saw with the present one. For every line the change
REPLACED, the SUBJECTS are the backticked terms the old and the new line share (what the line is ABOUT), and
the OLD VALUES are the words and numbers the old line carried and the new one does not (what CHANGED). A
CANDIDATE is any other line of the present directory that names a subject and still carries an old value.

WHAT IT DOES NOT CLAIM. A changed line with no backticked subject yields nothing - without an anchor a stale
passage cannot be told from an innocent use of a common word. And it finds a VALUE left behind, not a
sentence made false in other words ("stepped back up and re-run" after the re-run was dropped). A candidate
is a line to look at, never a verdict; the caller decides.

WHERE IT LOOKS: `spec.md`, `plan.md` and the task lines of `tasks.md` - the live, operative text. Each thing it
does NOT search legitimately keeps an old value: the `Review history` section (it records what used to be); a
task's `verify:` note (a dated record); `request.md` (the GM's words); `research.md` (a results table keeps the
value that was TESTED - including it made 16 of 18 candidates false on the real case this was proven on);
`measurements.json` and `plan-review.json` (recorded figures and a recorded verdict, re-derived or re-issued,
never edited by hand); `measure/` (a harness's code, not a statement about the feature).
"""

from __future__ import annotations

import argparse
import difflib
import pathlib
import re
import subprocess
import sys

#: only the OPERATIVE documents are searched. Measured on feature 251 (specs/253 research R1): with `research.md`
#: included, 16 of 18 candidates were false - a results table legitimately records the tier that was TESTED.
WATCHED_FILES = ("spec.md", "plan.md", "tasks.md")
#: words that change in any rewording and point at nothing
COMMON = frozenset(
    "the and for that this with from are was were has have had not but its their they them then than into onto over each "
    "when where which while will would should could may must can one two all any more most some such only also both "
    "here there what how why who does did done being been same other after before under between against about".split()
)
TOKEN = re.compile(r"[A-Za-z][A-Za-z-]{2,}|\d+(?:[.,]\d+)*%?")
TICKED = re.compile(r"`([^`\n]{2,60})`")


def tokens(line: str) -> set[str]:
    return {t.casefold() for t in TOKEN.findall(line)} - COMMON


def subjects(line: str) -> set[str]:
    return {s.strip() for s in TICKED.findall(line)}


def changed_pairs(old: str, new: str) -> list[tuple[str, str]]:
    """(old line, new line) for each line the change REPLACED; pure insertions and deletions pair with nothing."""
    a, b = old.splitlines(), new.splitlines()
    pairs: list[tuple[str, str]] = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "replace":
            pairs.extend(zip(a[i1:i2], b[j1:j2]))
    return pairs


def watched_lines(name: str, text: str) -> list[tuple[int, str]]:
    """(line number, line) of `text` that may be a candidate: none of a skipped file, none of the Review history."""
    if pathlib.PurePath(name).name not in WATCHED_FILES:
        return []
    out, in_history = [], False
    for n, line in enumerate(text.splitlines(), 1):
        if line.startswith("## "):
            in_history = line.strip().casefold().startswith("## review history")
        # a task's `verify:` note is a DATED record of what was verified then; the task line above it is live text
        if not in_history and not line.lstrip().startswith("verify:"):
            out.append((n, line))
    return out


def stale_candidates(old_files: dict[str, str], new_files: dict[str, str]) -> list[dict]:
    """Every line of `new_files` that names a changed line's subject and still carries its old value."""
    found: list[dict] = []
    seen: set[tuple[str, int]] = set()
    for name, new_text in sorted(new_files.items()):
        if name not in old_files or not name.endswith(".md"):
            continue
        for old_line, new_line in changed_pairs(old_files[name], new_text):
            subj = subjects(old_line) & subjects(new_line)
            gone = tokens(old_line) - tokens(new_line) - {t.casefold() for s in subj for t in TOKEN.findall(s)}
            if not subj or not gone:
                continue
            for other, text in sorted(new_files.items()):
                for n, line in watched_lines(other, text):
                    if line == new_line or (other, n) in seen:
                        continue
                    hit_subject = next((s for s in sorted(subj) if s in line), None)
                    hit_value = sorted(gone & tokens(line))
                    if hit_subject and hit_value:
                        seen.add((other, n))
                        found.append({"file": other, "line": n, "subject": hit_subject, "old_values": hit_value, "text": line.strip()[:200], "changed_in": name, "changed_to": new_line.strip()[:160]})
    return found


def read_dir(root: pathlib.Path) -> dict[str, str]:
    return {str(p.relative_to(root)): p.read_text(encoding="utf-8", errors="replace") for p in sorted(root.rglob("*.md")) if p.is_file()}


def read_ref(clone: pathlib.Path, ref: str, feature: str) -> dict[str, str]:
    """The feature directory's Markdown as it stood at a git ref."""
    base = f"specs/{feature}/"
    names = subprocess.run(["git", "-C", str(clone), "ls-tree", "-r", "--name-only", ref, "--", base], capture_output=True, text=True, check=False).stdout.split()
    out = {}
    for full in names:
        if full.endswith(".md"):
            out[full[len(base) :]] = subprocess.run(["git", "-C", str(clone), "show", f"{ref}:{full}"], capture_output=True, text=True, check=False).stdout
    return out


def render(found: list[dict]) -> str:
    if not found:
        return "stale-terms: no candidate - no line names a changed line's subject and still carries its old value"
    lines = [f"stale-terms: {len(found)} candidate(s) - each names a subject whose value CHANGED and still carries the old value:"]
    for c in found[:25]:
        lines.append(f"  {c['file']}:{c['line']}  `{c['subject']}` still with {', '.join(c['old_values'][:4])}")
        lines.append(f"      {c['text']}")
        lines.append(f"      (changed in {c['changed_in']} to: {c['changed_to']})")
    if len(found) > 25:
        lines.append(f"  ... and {len(found) - 25} more")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("feature", help="the feature directory's name under specs/")
    ap.add_argument("--clone", default=".")
    ap.add_argument("--against", default="", help="a git ref to compare with; default is the review-round guard's snapshot")
    args = ap.parse_args(argv)
    clone = pathlib.Path(args.clone).resolve()
    matches = sorted((clone / "specs").glob(f"{args.feature}*")) if not (clone / "specs" / args.feature).is_dir() else [clone / "specs" / args.feature]
    if not matches:
        print(f"stale-terms: no feature directory matches specs/{args.feature}*", file=sys.stderr)
        return 2
    feature_dir = matches[0]
    snap = clone / ".git" / "review-round" / feature_dir.name / "snapshot"
    if args.against:
        old = read_ref(clone, args.against, feature_dir.name)
    elif snap.is_dir():
        old = read_dir(snap)
    else:
        print(f"stale-terms: no snapshot of {feature_dir.name} (no review round was dispatched yet) - name a ref with --against", file=sys.stderr)
        return 2
    found = stale_candidates(old, read_dir(feature_dir))
    print(render(found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
