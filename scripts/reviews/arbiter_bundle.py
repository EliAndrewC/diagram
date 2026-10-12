#!/usr/bin/env python3
"""The round arbiter's bundle - what `round-arbiter` reads to rule on a trigger (feature 375, FR-011, plan D11).

The arbiter judges the PROCESS: whether another round is worth its cost, whether what stands can close, or whether the loop is
the fault. So the bundle is the loop's own record, built mechanically, copied OUT of the repository (an agent reading a file
here is handed every CLAUDE.md above it - feature 250):

- the trigger and what fired it (`<git dir>/arbiter-owed.json`);
- for a round trigger, each round of that check on that subject (`checks-open.json` and the replies `check-replies/` kept),
  its findings marked NEW, REPEATED (an earlier round found it) or REVERSING (its EDIT undoes an earlier round's);
- the unit's edits between rounds (`git log -p` over the feature's commits, then the working tree);
- the cascade - the feature's event log, edits and dispatches in order;
- the oscillation - every reversal in the event log;
- the feature's `request.md` and `spec.md`.

    arbiter_bundle.py <trigger> [--root DIR] [--out DIR] [--missing-ok REASON]
"""

from __future__ import annotations

import argparse
import difflib
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for _d in ("../hooks/lib", "../measure"):
    sys.path.insert(0, str((HERE / _d).resolve()))
import event_log as el  # noqa: E402
import hm_arbiter as ha  # noqa: E402
import hm_checks as hc  # noqa: E402

DEFAULT_OUT = Path("/tmp/l7r-check")
#: where a background agent's transcript lives, by its id - the reply when the hook kept none
TRANSCRIPTS = Path.home() / ".claude" / "projects"


#: a reply's top-level item: numbered ("1. x", "**1. x**"), else a bullet or a bold-headed entry ("**VOCABULARY** - ...")
_NUMBERED_START = re.compile(r"^\s{0,3}(?:\*\*)?\d+[.)]\s+\S")
_TOP_START = re.compile(r"^(?:[-*]\s+\S|\*\*[A-Z][^*]{2,}\*\*)")
#: lines that are never a finding: a bundle path, a manifest name, a pass or a confirmation (368's record-format ruling: five
#: rounds of "Ordinary English, dismissed" lists and bundle paths were all marked NEW)
_NOT_FINDING = re.compile(r"^(?:`?/tmp/l7r-check\S*`?\s*$|`?\S*MANIFEST\.md`?\s*$|(?:\*\*)?(?:ok|pass|passes|clean|confirmed|dismissed|ordinary english)\b)", re.I)
_QUOTED = re.compile(r"[\"“'‘「]([^\"”'’」\n]{12,})[\"”'’」]")
_PAGE_REF = re.compile(r"\b(\d{4})(?=[-.\s,;:)]|$)")
_CODE = re.compile(r"\b(?:D\d+|FR-\d+|SC-\d+|ACCURACY|REFERENCES|GAPS|COVERAGE|TRUTH|LINKS|VOCABULARY|SESSION NOTE|HISTORY)\b")
_UNRECORDED = re.compile(r"no page (?:holds|gives|says|records)|needs new research|not recorded|unrecorded|no source gives", re.I)
_STOP = frozenset({"the", "a", "an", "of", "to", "in", "on", "and", "or", "is", "are", "was", "were", "it", "its", "this", "that", "with", "as", "by", "for", "from", "be", "at", "not", "no"})


def _words(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def findings_of(reply: str) -> list[str]:
    """A reply's findings, each WHOLE - its first line with its continuation lines and sub-bullets. Reading one line per finding
    cut a summary at the colon that led into its bullets ("no tract is turned apart from the next:"), so the arbiter got the
    claim without its evidence (368's buckwheat ruling, 343's residence and main-gate rulings, 2026-10-11). Numbered items are
    the findings where the reply numbers them (its bullets then are what it confirmed - feature 374); else top-level bullets and
    bold-headed entries. A bundle path or a confirmation is never one."""
    lines = reply.splitlines()
    numbered = any(_NUMBERED_START.match(ln) for ln in lines)
    out: list[list[str]] = []
    cur: list[str] | None = None
    for ln in lines:
        s = ln.strip()
        if _NUMBERED_START.match(ln) if numbered else _TOP_START.match(ln):
            cur = [s]
            out.append(cur)
        elif not s or s.startswith("#"):  # a blank line or a heading ends the finding
            cur = None
        elif cur is not None and (ln[:1].isspace() or s.startswith(("-", "*", ">"))):  # its continuation and sub-bullets
            cur.append(s)
        else:
            cur = None
    found = [re.sub(r"^(?:(?:\*\*)?\d+[.)]\s+|[-*]\s+)", "", " ".join(item)) for item in out]  # the item's marker off
    return [f for f in found if len(f) >= 12 and not _NOT_FINDING.search(f)]


def _content(text: str) -> set[str]:
    return {w for w in _words(text).split() if len(w) > 3 and w not in _STOP}


def _repeats(f: str, earlier: list[str]) -> bool:
    """Whether finding `f` re-raises an earlier one: the same words, a quoted passage they share, or the same record page with
    the same rule code or most of the same content words. Matching words alone marked every re-raised gap NEW when its
    heading was reworded (343's door, garden, side-gate and genkan rulings, 2026-10-11)."""
    w, quotes, pages, codes, words = _words(f), {_words(q) for q in _QUOTED.findall(f)}, set(_PAGE_REF.findall(f)), set(_CODE.findall(f)), _content(f)
    for e in earlier:
        if w == _words(e) or quotes & {_words(q) for q in _QUOTED.findall(e)}:
            return True
        ew = _content(e)
        overlap = len(words & ew) / max(1, len(words | ew))
        if pages & set(_PAGE_REF.findall(e)) and (codes & set(_CODE.findall(e)) or overlap >= 0.35):
            return True
    return False


def _near_reversal(o: str, n: str, earlier: list[tuple[str, str]]) -> bool:
    """An EDIT that adds back two or more content words an earlier EDIT deleted - the same paragraph moved back toward wording
    a fix replaced, though not word for word (343's garden-pond and border-court rulings: 'stones' and 'gravel' came back)."""
    inserted = _insertion(o, n)
    if inserted is not None:
        # a PURE ADDITION: every word of the old text kept, in order, words added. Two loose content words shared with any
        # earlier deletion flagged all three of copse_siting's depiction additions (352, 2026-10-11, the arbiter's tooling
        # fix: "a prefix of its replacement, not reversals"), so an addition reverses only where a run of its added words is
        # a run an earlier EDIT took out
        tail = _trigrams(inserted)
        return any(tail & (_trigrams(eo) - _trigrams(en)) for eo, en in earlier)
    added = _content(n) - _content(o)
    return any(len(added & (_content(eo) - _content(en))) >= 2 for eo, en in earlier)


def _insertion(o: str, n: str) -> str | None:
    """The words `n` adds to `o` when it keeps every word of `o` in order (an append or an insertion), else None."""
    a, b = _words(o).split(), _words(n).split()
    ops = difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes()
    if not a or any(tag in ("delete", "replace") for tag, *_ in ops):
        return None
    return " ".join(w for tag, _i1, _i2, j1, j2 in ops if tag == "insert" for w in b[j1:j2])


def _trigrams(text: str) -> set[tuple[str, ...]]:
    """Every run of three content words in `text`, in order - a phrase, where `_content` is a bag."""
    w = [x for x in _words(text).split() if len(x) > 3 and x not in _STOP]
    return {tuple(w[i:i + 3]) for i in range(len(w) - 2)}


def mark_rounds(replies: list[str], others: list[tuple[str, str]] | None = None) -> list[list[tuple[str, str]]]:
    """Each round's findings, `(mark, finding)`: NEW, REPEATED (an earlier round raised it - `_repeats`) or REVERSING (an EDIT
    whose old and new text are an earlier round's new and old, or one that adds back words an earlier EDIT deleted, from this
    check or another check on the same subject - `others`)."""
    seen: list[str] = []
    edits: list[tuple[str, str]] = list(others or [])
    out = []
    for reply in replies:
        blocks = [(o, n) for _p, o, n in hc._blocks(reply)]
        marked = []
        for f in findings_of(reply):
            marked.append(("REPEATED" if _repeats(f, seen) else "NEW", f))
            seen.append(f)
        # what this round said no page holds: a later round asking for it again re-raises it (343's main-gate ruling: round 1's
        # "supplying it needs new research" came back as round 2's D2 finding)
        seen += [s for s in re.split(r"(?<=[.;])\s+|\n", reply) if _UNRECORDED.search(s)]
        for o, n in blocks:
            if (n, o) in edits:
                marked.append(("REVERSING", f"EDIT {o!r} -> {n!r} undoes an earlier round's fix"))
            elif _near_reversal(o, n, edits):
                marked.append(("REVERSING", f"EDIT {o!r} -> {n!r} adds back words an earlier fix took out"))
        edits += blocks
        out.append(marked)
    return out


def reply_of(v: dict) -> str:
    """A round's reply: the one the hook kept, else the last text of the agent's own transcript (by its id)."""
    if v.get("reply") and Path(v["reply"]).is_file():
        return Path(v["reply"]).read_text(encoding="utf-8")
    aid = str(v.get("aid") or "")
    found = sorted(TRANSCRIPTS.glob(f"*/*/subagents/agent-{aid}.jsonl")) if aid else []
    return hc._reply_of(str(found[0]), "") if found else ""


def _git(root: Path, *args: str) -> str:
    r = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=False)
    return r.stdout if r.returncode == 0 else ""


def subject_files(root: Path, subject: str) -> list[str]:
    """The files a subject's checks read: a question's pages, or a pop-up's file with the pages its Entry: and Drawing: name -
    an edit to a linked page re-owes a pop-up's check, and a bundle without those diffs left the arbiter unable to see what
    re-owed the round (368's privy ruling, 2026-10-11)."""
    if subject.startswith("q:"):
        return sorted(str(p.relative_to(root)) for p in (root / "research" / "questions").glob(f"{subject[2:]}-*"))
    if subject.startswith("modal:"):
        own = f"l7r/diagram/interactive/assets/modals/{subject[6:]}.md"
        text = (root / own).read_text(encoding="utf-8") if (root / own).is_file() else ""
        linked = re.findall(r"research/questions/[^\s,;]+?\.html", "\n".join(re.findall(r"^(?:Entry|Drawing):(.*)$", text, re.M)))
        return [own, *(f for f in dict.fromkeys(linked) if (root / f).is_file())]
    return []


class MissingRecord(Exception):
    """What the loop's own record lacks for a ruling (each a line the refusal prints)."""


def target(root: Path, trigger: str, owed: dict) -> tuple[str, str, list[str], str]:
    """(check, subject, files, unit) of a trigger. A round trigger missing from the owed record is read from its own name
    (`hm_arbiter.unit_of`): unrecorded, its bundle had no Rounds and no edits (343's M1c, 2026-10-11 - a wave of refusals
    lost their triggers to an unlocked write). A reversal the EDIT wire caught names a FILE, not a check|subject: its rounds
    are every check's on that file's subject, its A -> B -> A the file's own history (368's ruling on 0047); the block wire in
    hm_checks trips `reversal:<subject>@<n>` with the SUBJECT as its unit."""
    unit = str(owed.get("unit") or ha.unit_of(trigger))
    check, _, subject = unit.partition("|")
    files: list[str] = []
    if trigger.startswith("reversal:") and "|" not in unit:
        tgt = unit or trigger.split(":", 1)[1].rsplit("@", 1)[0]
        if tgt.startswith(("q:", "modal:")):
            check, subject = "", tgt
        else:
            path = Path(tgt)
            check, subject = "", hc.subject_of_path(str(path))  # no "|": partition put the whole path in `check`
            files = [str(path.resolve().relative_to(root)) if path.is_absolute() and path.resolve().is_relative_to(root) else str(path)]
    return check, subject, files, unit


def last_edits(root: Path, reply: str, files: list[str]) -> list[str]:
    """The last answered round's EDIT blocks, each marked applied or not against the file as it stands - an unapplied fix was
    inferred from a hunk header (343's side-gate ruling, 2026-10-11)."""
    text = "\n".join((root / f).read_text(encoding="utf-8") for f in files if (root / f).is_file())
    out = []
    for p, o, n in hc._blocks(reply):
        done = n in text and (o not in text or o in n)
        out.append(f"- {'APPLIED' if done else 'NOT APPLIED'}: {p or '(its file)'}: {o[:120]!r} -> {n[:120]!r}")
    return out


def rounds_section(root: Path, out: Path, check: str, subject: str, trigger: str) -> tuple[list[str], list[dict], list[str], str]:
    """The Rounds section: each dispatch of the check (or of every check, for a reversal) on the subject, its verdict, what
    owed it, its whole reply beside the MANIFEST and its findings marked (`mark_rounds`, with every OTHER check's EDITs on the
    subject as earlier fixes a round may undo). Returns (lines, rounds, rounds with no reply, the last reply)."""
    state = hc.load(hc.state_path(str(root)) or Path("/nonexistent"))
    every = sorted((v for v in state.get("dispatches", {}).values() if subject in v.get("subjects", [])), key=lambda v: v.get("t", 0))
    rounds = [v for v in every if not check or v.get("check") == check]
    others = [(o, n) for v in every if check and v.get("check") != check for _p, o, n in hc._blocks(reply_of(v))]
    replies = [reply_of(v) for v in rounds]
    n = trigger.rsplit("@", 1)[1] if trigger.startswith("round:") and "@" in trigger else ""
    parts = [f"## Rounds - {check or 'every check'} on {subject}\n"]
    if n:  # 343's 0104 quote-check ruling: the trigger read @3 and the bundle listed four rounds
        parts.append(
            f"The owed round is the counter's round {n}: it counts the dispatches let through on this unit in this feature, a "
            "first reading of new notes not counted, so the list below - every dispatch kept - may run longer.\n"
        )
    missing: list[str] = []
    for i, (v, marked) in enumerate(zip(rounds, mark_rounds(replies, others), strict=True), 1):
        c = str(v.get("check"))
        parts.append(f"### Round {i}: {c} ({v.get('state')}; verdict: {el.verdict_of(replies[i - 1]) or 'no reply kept'})\n")
        parts += [f"Owed by: {o}" for o in v.get("owed", [])] or ["Owed by: (not recorded - a dispatch before feature 374 kept no occasion)"]
        if replies[i - 1]:
            # THE REPLY ITSELF, beside the MANIFEST: a check that words its findings otherwise (modal-form's sections) left the
            # arbiter with "no findings" on 374's first day (2026-10-10)
            (out / f"round-{i}-{c}.md").write_text(replies[i - 1], encoding="utf-8")
            parts.append(f"The whole reply: `round-{i}-{c}.md` beside this file.")
        else:
            missing.append(f"round {i} ({c}, bundle {v.get('manifest') or '?'})")
        parts += [f"- {m}: {f}" for m, f in marked] or ["- (no findings it numbers or bullets - read the whole reply)" if replies[i - 1] else "- (no reply kept for this round)"]
        parts.append("")
    last = next((r for r in reversed(replies) if r), "")
    return parts, rounds, missing, last


def git_flow(root: Path, files: list[str]) -> list[str]:
    """The commits touching `files`, oldest first, as cascade lines (`HH:MM:SS commit <hash> <subject>`) - the fallback where
    the event log holds no edit on a unit's files (feature 374's bridgehead ruling: cascade.txt read 0 edits beside three
    commits on the pop-up); none outside a git repository."""
    r = subprocess.run(["git", "-C", str(root), "log", "--reverse", "--format=%cI %h %s", "--", *files], capture_output=True, text=True, check=False)
    return [f"{ln[11:19]} commit {ln.split(' ', 1)[1]}" for ln in r.stdout.splitlines() if " " in ln] if r.returncode == 0 else []


def owe_evidence(slug: str, diff: str) -> str:
    """Whether the round's diff shows what owes a unit (feature 374 wave 122, the round arbiter's tooling fix on 0219: the
    bundle owed translation-check on `kameyama-yashikigami` while `owes-round.diff` held that note only as context, and the
    arbiter had to find that by hand). A unit names its note after `#`, else its subject; a changed line (`+`/`-`, not the
    file headers) carrying that name is the cause shown, and none is said plainly."""
    name = slug.split("#", 1)[1] if "#" in slug else slug.split(":", 1)[-1]
    lines = diff.splitlines()
    changed = (ln for ln in lines if ln[:1] in "+-" and not ln.startswith(("+++", "---")))
    if name in ("unfootnoted", "gloss") or any(name in ln for ln in changed):
        return "a changed line in `owes-round.diff` names it"
    # a page-scoped unit (`record-format:0091`) is named by its question's file in a file header (the round arbiter on
    # 0091's third round: the bundle said no changed line named 0091 while the hunks were 0091's own drawing page)
    if "#" not in slug and any(ln.startswith(("diff --git", "+++ ", "--- ")) and f"/{name}-" in ln for ln in lines):
        return f"`owes-round.diff` changes a file of {name}"
    return f"NO changed line in `owes-round.diff` names `{name}` - its cause is not in this round's change; say so in the ruling"


def capped_round_cause(root: Path, out: Path, check: str, subject: str, files: list[str], since: float) -> list[str]:
    """What owes the CAPPED round itself (feature 374 wave 120, the arbiter on the seat pop-ups: the round-3 cause - one word
    on 0190's drawing page, and for one unit its round 2's own fix - was named nowhere in the MANIFEST and had to be dug out
    of edits.diff): the record's owed reason for the unit now, and the commits on the unit's files since the last round's
    dispatch, their hunks in `owes-round.diff`."""
    sys.path.insert(0, str((HERE / "../record").resolve()))
    import record_owed  # noqa: PLC0415

    name = subject.split(":", 1)[1] if ":" in subject else subject
    checks = {"modal-research": ("modal-accuracy", "modal-references", "modal-gaps")}.get(check, (check,))
    owed: list[str] = []
    try:
        owing = [u for u in record_owed.unanswered(root) if u.check in checks and u.subject.split("#")[0] in (name, f"{name}.drawing")]
    except Exception as e:  # noqa: BLE001 - a record that cannot be read leaves the cause to the diff, said so
        owing, owed = [], [f"- (the record's owed list could not be read: {e})"]
    log = _git(root, "log", f"--since=@{int(since)}", "--format=%h %ad %s", "--date=iso", "--", *files) if since and files else ""
    hunks = _git(root, "log", f"--since=@{int(since)}", "-p", "--format=--- %h %ad %s", "--date=iso", "--", *files) if log.strip() else ""
    diff = hunks + _git(root, "diff", "--", *files)
    (out / "owes-round.diff").write_text(diff or "(no change since the last round)\n", encoding="utf-8")
    if owing:
        owed = [f"- `{u.slug}`: {u.occasion} - {owe_evidence(u.slug, diff)}" for u in owing]
    return [
        "## What owes the capped round\n",
        "The record owes it now:\n" + ("\n".join(owed) or "- (nothing listed as owed)") + "\n",
        "Commits on the unit's files since the last round's dispatch (`owes-round.diff` beside this file holds their hunks and the"
        " working tree):\n" + ("\n".join(f"- {ln}" for ln in log.splitlines()) or "- none; the working tree only") + "\n",
    ]


def flow_sections(root: Path, out: Path, d: Path | None, files: list[str]) -> list[str]:
    """The cascade and the oscillation - for a unit, only the edits and reversals on its own files: a pop-up's bundle listed
    feature 368's 0047 reversal as its own loop (343's clerks--seats, office-hall, door and magistrate-s-dais rulings)."""
    # a feature whose sessions logged nothing yet has no log file: no events, not a crash (368's check session, 2026-10-10)
    log = el.log_path(root, d.name) if d else None
    events = list(el.read_jsonl(log)) if log and log.is_file() else []
    mine = (lambda p: any(str(p or "").endswith(f) for f in files)) if files else (lambda _p: True)
    flow = [
        f"{e['t'][11:19]} {e.get('tool')} {e.get('path') or e.get('agent') or e.get('make') or ''}"
        for e in events
        if e.get("ev") == "PreToolUse" and ((e.get("cat") == "edit" and mine(e.get("path"))) or (e.get("tool") == "Agent" and not files))
    ]
    source = ""
    if files and not flow:  # 374's bridgehead ruling: apply-edits and scripted edits never pass the Edit tool, so the log held none
        flow, source = git_flow(root, files), " (from the git log - the event log held no edit on them)"
    (out / "cascade.txt").write_text("\n".join(flow[-200:]) + "\n", encoding="utf-8")
    scope = ("the unit's files" if files else "the feature") + source
    sys.path.insert(0, str((HERE / "../measure").resolve()))
    import feature_report as fr  # noqa: PLC0415

    rev = [(p, t) for p, t in fr.reversals(events) if mine(p)]
    return [
        f"## The cascade\n\n`cascade.txt`: the last {min(len(flow), 200)} edits{'' if files else ' and dispatches'} on {scope}, in order.\n",
        "## Oscillation\n\n" + ("\n".join(f"- {p} at {t[11:19]}: an edit put back text an earlier edit replaced" for p, t in rev) or f"- none on {scope} in the event log") + "\n",
    ]


unit_of = ha.unit_of  # the one parser (feature 375 amendment 2): the bundle and the ruling row read a unit alike


def bundle(root: Path, trigger: str, out: Path, allow_missing: str = "") -> Path:
    """The MANIFEST for `trigger`; raises `MissingRecord` where a round kept no reply or a reversal has no record, unless
    `allow_missing` gives the reason to bundle anyway (it is printed in the MANIFEST for the arbiter to weigh)."""
    owed = ha.owed(root).get(trigger, {})
    d = ha.feature_dir(root)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    parts = [
        f"# Round arbiter bundle (feature 375, FR-011)\n\ntrigger: {trigger}\n",
        f"Kind: {owed.get('kind', trigger.split(':', 1)[0])}. Fired: {owed.get('detail', '(not in arbiter-owed.json) - the unit read from the trigger')}.\n",
        f"Clone root (for `make arbiter-ruled`): {root}\n",
    ]
    check, subject, files, unit = target(root, trigger, owed)
    # feature 379 amendment 2: the two kinds that used to go to the GM say where their record is
    if check == "spec-fidelity":
        parts.append(
            f"## Rounds - the spec review of {subject}\n\nIts rounds are `spec.md`'s Review history (beside this file): each "
            "round's verdict and what was applied. Rule as for any round cap: `accept` lets the spec stand as the last round "
            "left it (the review gate takes the ruling as its verdict).\n"
        )
    if trigger.startswith("ask:"):
        parts.append(
            f"## The question\n\n{owed.get('detail', '')}\n\nA process question the session would have put to the GM. "
            "`continue`: go on as the question proposes; `accept`: it stands as it is (a waiver); `process-fault`: the "
            "process is wrong - name the fix as `tooling_fix`. Say in `what` exactly what the session does next.\n"
        )
    rounds: list[dict] = []
    missing: list[str] = []
    if subject and check != "spec-fidelity":
        lines, rounds, missing, last = rounds_section(root, out, check, subject, trigger)
        parts += lines
        files = files or subject_files(root, subject)
        if last:
            parts.append("## The last answered round's EDITs, against the files now\n\n" + ("\n".join(last_edits(root, last, files)) or "- (it proposed none)") + "\n")
        if trigger.startswith("round:") and rounds:
            parts += capped_round_cause(root, out, check, subject, files, float(rounds[-1].get("t") or 0.0))
    diff = ""
    if files:
        diff = _git(root, "log", "-p", "--format=--- %h %ad %s", "--date=iso", "-20", "--", *files) + _git(root, "diff", "--", *files)
        (out / "edits.diff").write_text(diff or "(no edits)\n", encoding="utf-8")
        parts.append(f"## Edits between rounds\n\n`edits.diff` beside this file: the last 20 commits touching {', '.join(files)}, then the working tree.\n")
    # the arbiter cannot rule on a loop it cannot see: a round with no reply kept, or a reversal with neither rounds nor history,
    # is refused with what is missing (368's three rulings, 2026-10-11, each found "no reply kept" and ruled on an account)
    gaps = [f"no reply kept for {m}" for m in missing]
    if trigger.startswith("reversal:") and not rounds and not diff.strip():
        gaps.append(f"a reversal with no check rounds on {subject or unit or '?'} and no history of {', '.join(files) or '?'}")
    if trigger.startswith("round:") and check != "spec-fidelity" and not rounds:
        gaps.append(f"no dispatch of {check or '?'} on {subject or '?'} in the check state - a round trigger with no rounds to rule on")
    if gaps and not allow_missing:
        shutil.rmtree(out)
        raise MissingRecord(gaps)
    if gaps:
        parts.append("## Missing from the record (bundled anyway: " + allow_missing + ")\n\n" + "\n".join(f"- {g}" for g in gaps) + "\n")
    parts += flow_sections(root, out, d, files if subject else [])
    parts.append(feature_section(root, out, d, trigger))
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out / "MANIFEST.md"


def feature_dirs(root: Path, d: Path | None, trigger: str) -> list[Path]:
    """Where the feature's `request.md` and `spec.md` may be: the active feature, then the feature a trigger names by number
    (`ask:f335-...`) - a page session's ask was bundled where the active feature resolved to none."""
    out = [d] if d else []
    m = re.search(r"(?:^|[^a-z0-9])f(\d{3})(?:[^0-9]|$)", trigger)
    if m:
        out += sorted((root / "specs").glob(f"{m.group(1)}-*/"))
    return [p for p in dict.fromkeys(out) if p.is_dir()]


def feature_section(root: Path, out: Path, d: Path | None, trigger: str) -> str:
    """Copy the feature's `request.md` and `spec.md` beside the MANIFEST and name ONLY the ones copied (feature 335's round
    arbiter, 2026-10-11, `ask:f335-garden-modal-depiction`: the MANIFEST said both were beside it, and that bundle had
    neither). A file found nowhere is named as missing, with where it was looked for."""
    dirs = feature_dirs(root, d, trigger)
    copied, missing = [], []
    for name, what in (("request.md", "the GM's words"), ("spec.md", "the spec")):
        src = next((p / name for p in dirs if (p / name).is_file()), None)
        if src is None:
            missing.append(name)
            continue
        shutil.copyfile(src, out / name)
        copied.append(f"`{name}` ({what}, from {src.parent.relative_to(root) if src.is_relative_to(root) else src.parent})")
    text = "## The feature\n\n"
    if copied:
        text += "Beside this file: " + "; ".join(copied) + ".\n"
    if missing:
        looked = ", ".join(str(p.relative_to(root) if p.is_relative_to(root) else p) for p in dirs) or "no feature directory resolved"
        text += f"NOT in this bundle: {', '.join(missing)} - found in none of: {looked}. Rule from the sections above.\n"
    return text


batch_triggers = ha.batch_triggers  # THE BATCH, defined once (feature 375 amendment 2, FR-017)


def counted(root: Path, unit: str) -> int:
    """The rounds the dispatch counter holds for `unit` in the active feature (`checks-open.json`); 0 where it holds none."""
    state = hc.load(hc.state_path(str(root)) or Path("/nonexistent"))
    d = ha.feature_dir(root)
    if d is None or state.get("feature") != d.name:
        return 0
    return int(state.get("rounds", {}).get(unit, 0))


def misnumbered(root: Path, triggers: tuple[str, ...] | list[str]) -> list[str]:
    """Each round trigger the session NAMED (not one the counter fired) whose `@N` is not the unit's next round - with the one
    to ask about. 352's check session named all 21 pop-up units `@3` in one loop; seven modal-form units and windbreak's
    depiction had run once, and the bundle told the arbiter "the counter's round 3" (2026-10-11, the arbiter's tooling fix)."""
    fired = ha.owed(root)
    out = []
    for t in triggers:
        unit = ha.unit_of(t)
        if not unit or t in fired or t.startswith("round:spec-fidelity|"):
            continue
        want = f"round:{unit}@{counted(root, unit) + 1}"
        if t != want:
            out.append(f"{t} - the counter holds {counted(root, unit)} round(s) of {unit}: ask about `{want}`")
    return out


def batch(root: Path, out: Path, allow_missing: str = "", extra: tuple[str, ...] = ()) -> Path:
    """ONE bundle for every owed round trigger (FR-017; the GM 2026-10-11: "a whole batch of pop-ups reaching the round cap at
    once should get a single ruling. because they are likely to be related"): each trigger's own bundle in a subdirectory, and
    a MANIFEST asking for ONE ruling with an exception per unit ruled differently. Raises MissingRecord with every gap at once."""
    wrong = misnumbered(root, extra)
    if wrong:
        raise ValueError("a named round is not its unit's next: " + "; ".join(wrong))
    triggers = batch_triggers(root, extra)
    if not triggers:
        raise ValueError("no round trigger is owed a ruling - nothing to batch")
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    gaps: list[str] = []
    rows: list[str] = []
    for t in triggers:
        sub = re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-")[-60:]
        try:
            bundle(root, t, out / sub, allow_missing)
        except MissingRecord as e:
            gaps += [f"{t}: {g}" for g in e.args[0]]
            continue
        rows.append(f"- `{t}` - its bundle: `{sub}/MANIFEST.md`")
    if gaps:
        raise MissingRecord(gaps)
    parts = [
        f"# Round arbiter BATCH bundle (feature 375, FR-017)\n\n{len(triggers)} round triggers reached the cap together. Read each "
        "unit's own bundle below; they are likely related (one round of the same checks on related pop-ups or pages).\n",
        f"Clone root (for `make arbiter-ruled`): {root}\n",
        "## The triggers\n",
        *rows,
        *(["\nLeft out - owed in another feature, ruled or rulable there, not in this batch:\n", *(f"- {a}" for a in ha.aside(root))] if ha.aside(root) else []),
        "\n## Reply\n\nONE JSON object: the batch's ruling, and an exception for each unit you rule differently:\n\n"
        '    {"ruling": "continue|accept|process-fault", "why": "...", "what": "...", "tooling_fix": "<or omit>",\n'
        '     "triggers": [<every trigger above>], "exceptions": {"<trigger>": {"ruling": "...", "why": "...", "what": "..."}}}\n\n'
        "Record it with `make arbiter-ruled BATCH=1 FILE=<that file> AS=round-arbiter`: each trigger is recorded under the "
        "batch's ruling or its exception, so each unit's hold, closure and GM-review row work as they do alone.\n",
    ]
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out / "MANIFEST.md"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trigger", nargs="?", default="")
    ap.add_argument("--batch", action="store_true", help="one bundle for every owed round trigger (FR-017)")
    ap.add_argument("--triggers", default="", help="--batch: rounds asked about ahead of their cap, joined to the batch")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="")
    ap.add_argument("--missing-ok", default="", help="the reason to bundle with a reply or a reversal's record missing")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    slug = re.sub(r"[^a-z0-9]+", "-", a.trigger.lower()).strip("-")[-60:]
    if a.missing_ok.strip() and len(a.missing_ok.split()) < 2:  # every escape states a reason of two words or more
        print('arbiter-bundle: MISSING_OK needs a reason of two words or more - MISSING_OK="<why the reply is gone>"', file=sys.stderr)
        return 2
    if not a.batch and not a.trigger:
        print("arbiter-bundle: name the TRIGGER the refusal named, or BATCH=1 for every owed round trigger at once", file=sys.stderr)
        return 2
    try:
        if a.batch:
            print(batch(root, Path(a.out) if a.out else DEFAULT_OUT / "arbiter-batch", a.missing_ok.strip(), tuple(a.triggers.split())))
        else:
            wrong = misnumbered(root, [a.trigger])
            if wrong:
                raise ValueError("a named round is not its unit's next: " + "; ".join(wrong))
            print(bundle(root, a.trigger, Path(a.out) if a.out else DEFAULT_OUT / f"arbiter-{slug}", a.missing_ok.strip()))
    except ValueError as e:
        print(f"arbiter-bundle: {e}", file=sys.stderr)
        return 2
    except MissingRecord as e:
        print(
            "arbiter-bundle: the record lacks what the arbiter rules on - " + "; ".join(e.args[0]) + " (neither the hook's kept "
            "reply nor the agent's transcript has it). Bundle anyway, so the arbiter weighs the gap: "
            '`make arbiter-bundle TRIGGER=... MISSING_OK="<why it is gone>"`',
            file=sys.stderr,
        )
        return 2
    print("arbiter-bundle: dispatch `round-arbiter` on that MANIFEST; it records its own ruling (make arbiter-ruled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
