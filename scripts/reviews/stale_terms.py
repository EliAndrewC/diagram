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

WHERE IT LOOKS: EVERY text file of the feature directory - `spec.md`, `plan.md`, the task lines of `tasks.md`, and
whatever else a feature holds (`data-model.md`, `contracts/`, `quickstart.md`, a ledger) - EXCEPT what is named
here, each of which legitimately keeps an old value: the `Review history` section (it records what used to be); a
task's `verify:` note (a dated record); `request.md` and `gm-request.md` (the GM's words); `research.md` (a results table keeps the
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
#: EVERY text file of the feature directory is searched EXCEPT what is named here, so a file kind nobody anticipated
#: (`data-model.md`, `contracts/`, `quickstart.md`, a ledger) is searched by default rather than skipped in silence.
SKIP_NAMES = ("request.md", "gm-request.md", "research.md", "measurements.json", "plan-review.json")
SKIP_DIRS = ("measure",)
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


def rewritten_from(old: str | None, new: str) -> dict[int, str]:
    """For each line of `new` the change REPLACED (1-based), the old block it replaced. A candidate the same change rewrote FROM a line
    already naming its subject was revisited about that subject on purpose and states the new value (feature 440 T05: feature
    438's and 439's later rounds were refused on the rewritten passages themselves); a line the change rewrote to bring the
    subject in for the first time is still searched."""
    if old is None:
        return {}
    a, b = old.splitlines(), new.splitlines()
    out: dict[int, str] = {}
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "replace":
            # ...THE WHOLE OLD BLOCK, not the line at the same position: a 3-line passage rewritten as 5 paired its second new line
            # with an old line that did not name the subject, and feature 442's round 2 dispatch was refused on its own rewrite
            block = "\n".join(a[i1:i2])
            for k in range(j2 - j1):
                out[j1 + k + 1] = block
    return out


def watched_lines(name: str, text: str) -> list[tuple[int, str]]:
    """(line number, line) of `text` that may be a candidate: none of a skipped file, none of the Review history."""
    path = pathlib.PurePath(name)
    if path.name in SKIP_NAMES or set(path.parts[:-1]) & set(SKIP_DIRS):
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
    wrote = {other: rewritten_from(old_files.get(other), text) for other, text in new_files.items()}
    for name, new_text in sorted(new_files.items()):
        if name not in old_files or not watched_lines(name, "x"):
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
                    if hit_subject and hit_subject in wrote[other].get(n, ""):
                        continue  # rewritten from a line already about this subject: revisited on purpose
                    hit_value = sorted(gone & tokens(line))
                    if hit_subject and hit_value:
                        seen.add((other, n))
                        found.append({"file": other, "line": n, "subject": hit_subject, "old_values": hit_value, "text": line.strip()[:200], "changed_in": name, "changed_to": new_line.strip()[:160]})
    return found


def read_dir(root: pathlib.Path) -> dict[str, str]:
    out = {}
    for p in sorted(root.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts and p.stat().st_size < 1_000_000:
            try:
                out[str(p.relative_to(root))] = p.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue  # not a text file
    return out


def read_ref(clone: pathlib.Path, ref: str, feature: str) -> dict[str, str]:
    """The feature directory's Markdown as it stood at a git ref."""
    base = f"specs/{feature}/"
    names = subprocess.run(["git", "-C", str(clone), "ls-tree", "-r", "--name-only", ref, "--", base], capture_output=True, text=True, check=False).stdout.split()
    out = {}
    for full in names:
        shown = subprocess.run(["git", "-C", str(clone), "show", f"{ref}:{full}"], capture_output=True, check=False).stdout
        try:
            out[full[len(base) :]] = shown.decode("utf-8")
        except UnicodeDecodeError:
            continue  # not a text file
    return out


_REQ = re.compile(r"^- \*\*(FR-\d{3}[a-z]?)\*\*")
_CRIT = re.compile(r"^- \*\*(SC-\d{3}[a-z]?)\*\*\s*\(([^)]*)\)")


def _items(text: str, pattern: re.Pattern[str]) -> dict[str, tuple[int, str, re.Match[str]]]:
    """{id: (line number, the item's whole text - its first line and its indented continuation, the match)} of `text`."""
    out: dict[str, tuple[int, str, re.Match[str]]] = {}
    lines = text.splitlines()
    for n, line in enumerate(lines, 1):
        m = pattern.match(line)
        if m:
            body = [line]
            for more in lines[n:]:
                if not more.startswith("  ") or more.lstrip().startswith("- **"):
                    break
                body.append(more)
            out[m.group(1)] = (n, "\n".join(body), m)
    return out


def criteria_left_behind(old_files: dict[str, str], new_files: dict[str, str]) -> list[dict]:
    """Each success criterion that cites a requirement the change REWROTE and was not itself touched by it (feature 442: three
    of feature 440's ten review findings were a criterion left saying what its rewritten requirement no longer did)."""
    found: list[dict] = []
    for name, new_text in sorted(new_files.items()):
        if pathlib.PurePath(name).name != "spec.md" or name not in old_files:
            continue
        old_req, new_req = _items(old_files[name], _REQ), _items(new_text, _REQ)
        rewritten = {i for i in new_req if i in old_req and new_req[i][1] != old_req[i][1]}
        old_crit = _items(old_files[name], _CRIT)
        for sc, (n, body, m) in _items(new_text, _CRIT).items():
            cited = set(re.findall(r"FR-\d{3}[a-z]?", m.group(2))) & rewritten
            if cited and sc in old_crit and old_crit[sc][1] == body:
                fr = sorted(cited)[0]
                found.append({"file": name, "line": n, "subject": sc, "old_values": sorted(cited), "text": body.splitlines()[0].strip()[:200],
                              "changed_in": name, "changed_to": f"{fr} rewritten; this criterion untouched - does it still measure it?", "kind": "criterion"})
    return found


def render(found: list[dict]) -> str:
    if not found:
        return "stale-terms: no candidate - no line names a changed line's subject and still carries its old value"
    lines = [f"stale-terms: {len(found)} candidate(s) - each names a subject whose value CHANGED and still carries the old value:"]
    for c in found[:25]:
        if c.get("kind") == "criterion":
            lines.append(f"  {c['file']}:{c['line']}  `{c['subject']}` cites {', '.join(c['old_values'][:4])}, which the change rewrote - the criterion was not touched")
            lines.append(f"      {c['text']}")
            continue
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
    new = read_dir(feature_dir)
    found = stale_candidates(old, new) + criteria_left_behind(old, new)
    print(render(found))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
