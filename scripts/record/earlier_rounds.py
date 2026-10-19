#!/usr/bin/env python3
"""The EARLIER ROUNDS of a record or pop-up check, handed to its next round in the bundle (feature 393, the GM 2026-10-18).

WHY. The GM's note: *"give each reviewer the earlier rounds' verdicts and reasons to prevent reviewer loops"*. `spec-fidelity`
gets the previous verdict and the diff (feature 249), the map reviewers their previous verdict file and the notes' settled
items (240, 294), and the round arbiter every round marked NEW / REPEATED / REVERSING (375). The record and pop-up checks got
none of it: a later round judged the page or pop-up afresh, and of the 106 arbiter rulings feature 385's audit counted, 104
were on these checks, about 100 of them ruling that the next round would re-read text already passed. Only the arbiter, after
the cap, saw the rounds; the round that re-raised never did.

WHAT IT DOES. `section(root, out, manifest)` reads the MANIFEST a bundler is about to write - its `owed-checks:` line and its
`unit:` lines - and, for each check and subject with an earlier round in the active feature, writes each round's whole reply
beside the MANIFEST (`earlier/`) and returns a section listing the round's verdict, its findings marked as the arbiter's bundle
marks them, its EDIT blocks marked APPLIED or NOT APPLIED against the files as they stand, and the round arbiter's rulings on
the unit with their reasons. With no earlier round it returns '' and the bundle is unchanged (spec SC-002).

It reads the check state (`hm_checks`) and the rulings (`hm_arbiter`) and never writes them: how a round is keyed, counted and
capped is `hm_checks.py`'s (feature 393's out of scope; the Money session's round-key fix).
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path[1:1] = [str((HERE / _d).resolve()) for _d in ("../reviews", "../hooks/lib", "../measure")]  # the moved scripts it imports
import arbiter_bundle as ab  # noqa: E402

HEAD = "## Earlier rounds (feature 393)"
DIR = "earlier"
#: the contract paragraph's rule, said once more where the agent meets the rounds (the paragraph itself is in each agent file)
INTRO = (
    "Earlier rounds of this check on this subject in this feature, oldest first, and the round arbiter's rulings on them. Read "
    "them before the artifact: an APPLIED finding is settled (confirm it holds, do not re-raise it); what an earlier round "
    "passed stays passed while its text stands (THE CHANGE, where listed, says which text moved); a NOT APPLIED finding is "
    "judged against the text as it stands - settled if the defect is gone, else reported again as `REPEATS round <n>:`; a "
    "`continue` ruling's `what` bounds this round; to reverse an earlier verdict, say `REVERSES round <n>` and why. Each "
    "round's whole reply is the file named under it."
)
_OWED = re.compile(r"^owed-checks: (.+)$", re.M)


def feature_start(root: pathlib.Path) -> float:
    """When the active feature began (its `spec.md`'s first commit), or 0.0 - every round kept - when that is not known. The
    check state keeps dispatches across features (`hm_checks`: a new feature resets only the counts), and an earlier feature's
    round on the same page answered another change."""
    d = ab.ha.feature_dir(root)
    if d is None:
        return 0.0
    r = subprocess.run(["git", "-C", str(root), "log", "--diff-filter=A", "--format=%ct", "--", str(d / "spec.md")],
                       capture_output=True, text=True, check=False)
    stamps = [int(x) for x in r.stdout.split() if x.isdigit()]
    return float(min(stamps)) if stamps else 0.0


def rounds(state: dict, check: str, subject: str, since: float, notes: set[str]) -> list[dict]:
    """The returned dispatches of `check` on `subject` since `since`, oldest first. Where a dispatch records the notes its bundle
    read (`notes`, [] for the whole page), a note-scoped bundle gets only the rounds that read one of its notes or the whole page."""
    out = []
    for v in sorted(state.get("dispatches", {}).values(), key=lambda v: v.get("t", 0)):
        if v.get("check") != check or subject not in v.get("subjects", []) or v.get("t", 0) < since:
            continue
        if v.get("state") in ("pending", "running"):
            continue
        read = v.get("notes")
        if notes and isinstance(read, list) and read and not notes & set(read):
            continue
        out.append(v)
    return out


def _name(check: str, subject: str, i: int) -> str:
    return f"{DIR}/{check}-{re.sub(r'[^A-Za-z0-9]+', '-', subject).strip('-')}-round-{i}.md"


def _ruling_lines(rulings: dict, check: str, subject: str) -> list[str]:
    prefix = f"round:{check}|{subject}@"
    out = []
    for t, r in sorted(rulings.items(), key=lambda kv: ab.ha._round_no(kv[0])):
        if t.startswith(prefix):
            line = f"- the round arbiter on `{t}`: **{r.get('ruling', '?')}** - {r.get('why', '(no reason recorded)')}"
            if r.get("what"):
                line += f" | what the next round looks at: {r['what']}"
            out.append(line)
    return out


def unit_section(root: pathlib.Path, out: pathlib.Path, state: dict, rulings: dict, check: str, subject: str, since: float,
                 notes: set[str]) -> list[str]:
    """The lines for one check on one subject, its replies written beside the MANIFEST; [] with no earlier round or ruling."""
    mine = rounds(state, check, subject, since, notes)
    ruled = _ruling_lines(rulings, check, subject)
    if not mine and not ruled:
        return []
    replies = [ab.reply_of(v) for v in mine]
    others = [(o, n) for v in state.get("dispatches", {}).values()
              if subject in v.get("subjects", []) and v.get("check") != check and v.get("t", 0) >= since
              for _p, o, n in ab.hc._blocks(ab.reply_of(v))]
    files = ab.subject_files(root, subject)
    lines = [f"### {check} on {subject}", ""]
    for i, (reply, marked) in enumerate(zip(replies, ab.mark_rounds(replies, others), strict=True), 1):
        lines.append(f"**Round {i}** - verdict: {ab.el.verdict_of(reply) or 'none read'}" if reply else f"**Round {i}** - no reply kept")
        if reply:
            (out / _name(check, subject, i)).parent.mkdir(parents=True, exist_ok=True)
            (out / _name(check, subject, i)).write_text(reply, encoding="utf-8")
            lines.append(f"The whole reply: `{_name(check, subject, i)}`.")
        lines += [f"- {m}: {f}" for m, f in marked]
        lines += ab.last_edits(root, reply, files) if reply else []
        lines.append("")
    if ruled:
        lines += ["Rulings:", *ruled, ""]
    return lines


def section(root: pathlib.Path, out: pathlib.Path, manifest: str) -> str:
    """The MANIFEST's Earlier rounds section for the checks and subjects `manifest` owes, or '' when none has an earlier round."""
    m = _OWED.search(manifest)
    checks = [c for c in (m.group(1).replace(",", " ").split() if m else []) if c in ab.hc.PAGE_CHECKS]
    subjects = ab.hc.subjects_of_manifest(manifest)
    path = ab.hc.state_path(str(root))
    if not checks or not subjects or path is None or not path.is_file():
        return ""
    state, rulings, since = ab.hc.load(path), ab.ha.rulings(root), feature_start(root)
    notes = ab.hc.notes_of_manifest(manifest)
    body = [ln for c in checks for s in subjects for ln in unit_section(root, out, state, rulings, c, s, since, notes)]
    return f"\n{HEAD}\n\n{INTRO}\n\n" + "\n".join(body) if body else ""
