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
_FINDING = re.compile(r"^\s*(?:\d+[.)]|[-*])\s+(.{12,})$", re.M)
#: a NUMBERED item - a check's finding. A reply that numbers its findings also bullets what it confirmed ("the rest of the tab
#: matches the pages"), and reading those bullets as findings listed confirmations as NEW (feature 374, the arbiter's fix)
_NUMBERED = re.compile(r"^\s*(?:\*\*)?\d+[.)]\s+(.{12,})$", re.M)  # "1. x" and the bold heading "**1. x**" (374)
#: where a background agent's transcript lives, by its id - the reply when the hook kept none
TRANSCRIPTS = Path.home() / ".claude" / "projects"


def _words(text: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9 ]", " ", text.lower()).split())


def mark_rounds(replies: list[str]) -> list[list[tuple[str, str]]]:
    """Each round's findings, `(mark, finding)`: NEW, REPEATED (its words were an earlier round's finding) or REVERSING (an EDIT
    whose old and new text are an earlier round's new and old)."""
    seen: set[str] = set()
    edits: set[tuple[str, str]] = set()
    out = []
    for reply in replies:
        blocks = [(o, n) for _p, o, n in hc._blocks(reply)]
        marked = []
        for f in _NUMBERED.findall(reply) or _FINDING.findall(reply):
            w = _words(f)
            marked.append(("REPEATED" if w in seen else "NEW", f.strip()))
            seen.add(w)
        marked += [("REVERSING", f"EDIT {o!r} -> {n!r} undoes an earlier round's fix") for o, n in blocks if (n, o) in edits]
        edits |= set(blocks)
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
    if subject.startswith("q:"):
        return sorted(str(p.relative_to(root)) for p in (root / "research" / "questions").glob(f"{subject[2:]}-*"))
    if subject.startswith("modal:"):
        return [f"l7r/diagram/interactive/assets/modals/{subject[6:]}.md"]
    return []


class MissingRecord(Exception):
    """What the loop's own record lacks for a ruling (each a line the refusal prints)."""


def bundle(root: Path, trigger: str, out: Path, allow_missing: str = "") -> Path:
    """The MANIFEST for `trigger`; raises `MissingRecord` where a round kept no reply or a reversal has no record, unless
    `allow_missing` gives the reason to bundle anyway (it is printed in the MANIFEST for the arbiter to weigh)."""
    owed = ha.owed(root).get(trigger, {})
    d = ha.feature_dir(root)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)
    parts = [f"# Round arbiter bundle (feature 375, FR-011)\n\ntrigger: {trigger}\n",
             f"Kind: {owed.get('kind', trigger.split(':', 1)[0])}. Fired: {owed.get('detail', '(not in arbiter-owed.json)')}.\n",
             f"Clone root (for `make arbiter-ruled`): {root}\n"]
    unit = str(owed.get("unit") or "")
    check, _, subject = unit.partition("|")
    files: list[str] = []
    if trigger.startswith("reversal:") and "|" not in unit:
        # a reversal the EDIT wire caught names a FILE, not a check|subject: its rounds are every check's on that file's
        # subject, its A -> B -> A the file's own history (368's ruling on 0047, 2026-10-11: the bundle had neither)
        path = Path(unit or trigger.split(":", 1)[1].split("@", 1)[0])
        check, subject = "", hc.subject_of_path(str(path))  # no "|": partition put the whole path in `check`
        files = [str(path.resolve().relative_to(root)) if path.is_absolute() and path.resolve().is_relative_to(root) else str(path)]
    state = hc.load(hc.state_path(str(root)) or Path("/nonexistent"))
    missing: list[str] = []
    rounds: list[dict] = []
    if subject:
        rounds = sorted((v for v in state.get("dispatches", {}).values() if (not check or v.get("check") == check) and subject in v.get("subjects", [])),
                        key=lambda v: v.get("t", 0))
        replies = [reply_of(v) for v in rounds]
        parts.append(f"## Rounds - {check or 'every check'} on {subject}\n")
        for i, (v, marked) in enumerate(zip(rounds, mark_rounds(replies), strict=True), 1):
            c = str(v.get("check"))
            parts.append(f"### Round {i}: {c} ({v.get('state')}; verdict: {el.verdict_of(replies[i - 1]) or 'no reply kept'})\n")
            parts += [f"Owed by: {o}" for o in v.get("owed", [])] or ["Owed by: (not recorded - a dispatch before feature 374 kept no occasion)"]
            if replies[i - 1]:
                # THE REPLY ITSELF, beside the MANIFEST: the marks read numbered and bulleted lines only, and a check that words its
                # findings otherwise (modal-form's sections) left the arbiter with "no findings" on 374's first day (2026-10-10)
                (out / f"round-{i}-{c}.md").write_text(replies[i - 1], encoding="utf-8")
                parts.append(f"The whole reply: `round-{i}-{c}.md` beside this file.")
            else:
                missing.append(f"round {i} ({c}, bundle {v.get('manifest') or '?'})")
            parts += [f"- {m}: {f}" for m, f in marked] or ["- (no numbered or bulleted findings - read the whole reply)" if replies[i - 1]
                                                             else "- (no reply kept for this round)"]
            parts.append("")
        files = files or subject_files(root, subject)
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
    if gaps and not allow_missing:
        shutil.rmtree(out)
        raise MissingRecord(gaps)
    if gaps:
        parts.append("## Missing from the record (bundled anyway: " + allow_missing + ")\n\n" + "\n".join(f"- {g}" for g in gaps) + "\n")
    # a feature whose sessions logged nothing yet has no log file: no events, not a crash (368's check session, 2026-10-10)
    log = el.log_path(root, d.name) if d else None
    events = list(el.read_jsonl(log)) if log and log.is_file() else []
    flow = [f"{e['t'][11:19]} {e.get('tool')} {e.get('path') or e.get('agent') or e.get('make') or ''}"
            for e in events if e.get("ev") == "PreToolUse" and (e.get("cat") == "edit" or e.get("tool") == "Agent")]
    (out / "cascade.txt").write_text("\n".join(flow[-200:]) + "\n", encoding="utf-8")
    parts.append(f"## The cascade\n\n`cascade.txt`: the feature's last {min(len(flow), 200)} edits and dispatches, in order.\n")
    sys.path.insert(0, str((HERE / "../measure").resolve()))
    import feature_report as fr  # noqa: PLC0415

    rev = fr.reversals(events)
    parts.append("## Oscillation\n\n" + ("\n".join(f"- {p} at {t[11:19]}: an edit put back text an earlier edit replaced" for p, t in rev)
                                        or "- none in the event log") + "\n")
    for name in ("request.md", "spec.md"):
        if d and (d / name).is_file():
            shutil.copyfile(d / name, out / name)
    parts.append("## The feature\n\n`request.md` (the GM's words) and `spec.md` beside this file.\n")
    (out / "MANIFEST.md").write_text("\n".join(parts) + "\n", encoding="utf-8")
    return out / "MANIFEST.md"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("trigger")
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default="")
    ap.add_argument("--missing-ok", default="", help="the reason to bundle with a reply or a reversal's record missing")
    a = ap.parse_args(argv)
    root = Path(a.root).resolve()
    slug = re.sub(r"[^a-z0-9]+", "-", a.trigger.lower()).strip("-")[-60:]
    try:
        print(bundle(root, a.trigger, Path(a.out) if a.out else DEFAULT_OUT / f"arbiter-{slug}", a.missing_ok.strip()))
    except MissingRecord as e:
        print("arbiter-bundle: the record lacks what the arbiter rules on - " + "; ".join(e.args[0]) + " (neither the hook's kept "
              "reply nor the agent's transcript has it). Bundle anyway, so the arbiter weighs the gap: "
              '`make arbiter-bundle TRIGGER=... MISSING_OK="<why it is gone>"`', file=sys.stderr)
        return 2
    print("arbiter-bundle: dispatch `round-arbiter` on that MANIFEST; it records its own ruling (make arbiter-ruled)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
