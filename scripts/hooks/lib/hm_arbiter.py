#!/usr/bin/env python3
"""Tripwires and the round arbiter's rulings - escalation without stopping (feature 375, FR-010, FR-011; plan D10, D11).

WHY (the GM, 2026-10-10): *"our progress does not stop because we are going through an unexpectedly high number of rounds of
reviews, but rather we escalate to a subagent, and that subagent might say to continue, or it might say that it deems that
what we have now is actually fine ... or it will look at what is happening and say, oh, we're caught in a loop, we're
oscillating, we're having reviews that trigger other reviews"*. A pattern is caught the moment it happens, by the hook that
sees it - not by an hourly timer, and not by the looping session judging itself.

THE TRIGGERS (`<git common dir>/arbiter-owed.json`, `{id: {kind, unit, detail, t}}`):

- `round:<check>|<subject>` - a check's third round on one subject in one feature (record checks: `hm_checks.py`; review
  checks: `pair-hooks.sh`), refused at dispatch until ruled;
- `reversal:<path>` - an Edit putting back text an earlier Edit of the same file in the feature replaced (A -> B -> A, from
  the event log's digests);
- `red-gate` - a second red `make done` in a row (`l7r/diagram/ci/state.py` writes it);
- `cascade` - check dispatches per hand-written changed line past the measured threshold.

A trigger owes a RULING before the next check dispatch on its unit (a reversal or a cascade: any check; a red gate: the next
gate). Nothing else stops. `make arbiter-bundle TRIGGER=` builds what `round-arbiter` reads; `make arbiter-ruled` records its
ruling - one per trigger, binding - in `specs/<feature>/arbiter.jsonl` and as a row of the GM's review (`gm-review.jsonl`,
FR-012). `continue` lifts a round cap by one round; `accept` and `process-fault` close the unit (its further dispatches are
refused). A ruling's `tooling_fix` - a `process-fault` always has one - is an OPEN item of the feature until
`make arbiter-fix-done` or `arbiter-fix-declined` settles it, and `make tick` and the closing check refuse while it is open
(feature 379: the first such fix lived only in a ruling's prose and was lost).
"""

from __future__ import annotations

import json
import os
import re
import sys
import time
from collections.abc import Mapping
from pathlib import Path
from typing import Any

OWED = "arbiter-owed.json"
RULINGS = ("continue", "accept", "process-fault")
#: check dispatches per hand-written changed line past which a feature's checks are cascading (FR-010), and the fewest
#: dispatches before the ratio means anything. Set from the SC-006 replay (specs/375-enforced-wave-process/measurements.json
#: `cascade-threshold`): 372's wave 106 ran 0.13 and its looping wave 108 1.35.
CASCADE_RATIO = 1.0
CASCADE_MIN = 10


def common_dir(root: Path) -> Path:
    g = root / ".git"
    if g.is_file():
        m = re.match(r"gitdir:\s*(.+)", g.read_text(encoding="utf-8").strip())
        gd = (root / m.group(1)).resolve() if m else g
        c = gd / "commondir"
        return (gd / c.read_text(encoding="utf-8").strip()).resolve() if c.is_file() else gd
    return g


def feature_dir(root: Path) -> Path | None:
    try:
        fd = json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", "")
    except (OSError, ValueError):
        return None
    return (root / str(fd).rstrip("/")) if fd else None


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}


def owed(root: Path) -> dict[str, dict[str, Any]]:
    return _load(common_dir(root) / OWED)


def trip(root: Path, trigger: str, kind: str, unit: str, detail: str, now: float | None = None) -> bool:
    """Record a trigger once (a second firing of a trigger already owed or ruled changes nothing); True when it is new."""
    if trigger in rulings(root):
        return False
    path = common_dir(root) / OWED
    state = _load(path)
    if trigger in state:
        return False
    state[trigger] = {"kind": kind, "unit": unit, "detail": detail, "t": time.time() if now is None else now}
    m = re.match(r"(\d+) check dispatches", detail)
    if m:
        state[trigger]["dispatches"] = int(m.group(1))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    return True


def rulings(root: Path) -> dict[str, dict[str, Any]]:
    """`{trigger: its ruling}` of the active feature (`specs/<feature>/arbiter.jsonl`)."""
    d = feature_dir(root)
    out: dict[str, dict[str, Any]] = {}
    f = d / "arbiter.jsonl" if d else None
    for line in (f.read_text(encoding="utf-8").splitlines() if f and f.is_file() else []):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if "trigger" in r:  # a `fix_of` row settles a ruling's tooling fix (feature 379); it is no ruling
            out[str(r["trigger"])] = r
    return out


def continues(root: Path, prefix: str) -> int:
    """How many `continue` rulings the round triggers of one unit carry - each lifts its cap by one round."""
    return sum(1 for t, r in rulings(root).items() if t.startswith(prefix) and r.get("ruling") == "continue")


def closed(root: Path, prefix: str) -> str:
    """The ruling that closed the unit (`accept` / `process-fault`), or ''."""
    return next((str(r["ruling"]) for t, r in rulings(root).items() if t.startswith(prefix) and r.get("ruling") in RULINGS[1:]), "")


def blocking(root: Path, unit: str = "", gate: bool = False) -> list[str]:
    """The unruled triggers that hold the next dispatch on `unit` (its own round triggers, and every reversal or cascade), or,
    with `gate`, the next `make done` (a red-gate trigger)."""
    out = []
    for t, v in owed(root).items():
        kind = v.get("kind")
        if gate and kind == "red-gate":
            out.append(t)
        elif not gate and (kind in ("reversal", "cascade") or (kind == "round" and v.get("unit") == unit)):
            out.append(t)
    return sorted(out)


def refusal(triggers: list[str]) -> str:
    if not triggers:
        return ""
    t = triggers[0]
    return (f"a tripwire is owed its ruling first ({', '.join(triggers)}; feature 375 FR-010/FR-011): make arbiter-bundle "
            f"TRIGGER=\"{t}\", dispatch `round-arbiter` on the MANIFEST it prints, then make arbiter-ruled TRIGGER=\"{t}\" "
            "FILE=<its JSON> AS=round-arbiter. The feature goes on elsewhere meanwhile. (Claude Code picks up a new agent file "
            "mid-session - this one did on 2026-10-10 - so only if `round-arbiter` is missing from the session's agent list: "
            "restart it, or carry ARBITER_OK=\"<reason>\" on the gate or in the check's prompt - logged.)")


def reversal(events: list[Mapping[str, Any]], path: str, old: str, new: str) -> bool:
    """Whether an Edit of `path` (digests `old` -> `new`) puts back text an earlier Edit of that file replaced (A -> B -> A)."""
    replaced = {str(e.get("old")) for e in events if e.get("ev") == "PreToolUse" and e.get("tool") == "Edit" and e.get("path") == path}
    return bool(new) and new in replaced and new != old


def cascade(dispatches: int, lines: int, last: int = 0) -> bool:
    """Past the ratio with at least CASCADE_MIN dispatches - counted since the last cascade ruling, whatever it ruled (`last`:
    the dispatches the feature had then). So the wire stays live after a ruling, and fires again only when a round's worth of
    further checks are out of proportion too (the plan review of amendment 1: a raise per `continue` both under- and
    over-shot, and an `accept` switched it off)."""
    return dispatches - last >= CASCADE_MIN and dispatches > CASCADE_RATIO * max(lines, 1)


def cascade_state(root: Path) -> tuple[str, int]:
    """(the next cascade trigger id, the dispatches at the last cascade ruling): the id advances after ANY ruling."""
    ruled = [r for t, r in rulings(root).items() if t.startswith("cascade@")]
    last = max((int(r.get("dispatches") or 0) for r in ruled), default=0)
    return f"cascade@{len(ruled) + 1}", last


#: the units one `modal-research` dispatch is answered as
RESEARCH_UNITS: tuple[str, ...] = ("modal-accuracy", "modal-references", "modal-gaps")


def accept_answers(root: Path, unit: str, result: str) -> list[str]:
    """An `accept` on a round cap answers that check's units on its subject at today's words (feature 374 FR-005): the
    arbiter closed the unit to further dispatches, and the record gate went on owing it, so the push refused what the
    arbiter had accepted. `unit` is `<check>|<subject>` - a pop-up `modal:<uid>` or a question `q:<NNNN>`."""
    check, _, subject = unit.partition("|")
    kind, _, name = subject.partition(":")
    if kind not in ("modal", "q") or not check or not name:
        return []
    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "record"))
    import record_owed  # noqa: PLC0415

    done: list[str] = []
    for c in RESEARCH_UNITS if check == "modal-research" else (check,):
        done += record_owed.answer(root, c, result, kind=name) if kind == "modal" else record_owed.answer(root, c, result, q=name)
    return done


def record_ruling(root: Path, trigger: str, ruling: Mapping[str, Any], declared: str, now: str | None = None) -> dict[str, Any]:
    """Record the round arbiter's ruling: binding, one per trigger (FR-011)."""
    if declared != "round-arbiter":
        raise PermissionError("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, "
                              "recorded, not a proof")
    if trigger in rulings(root):
        raise ValueError(f"{trigger} is already ruled - one ruling per trigger, binding; the session neither re-asks nor overrules")
    if ruling.get("ruling") not in RULINGS or not str(ruling.get("why") or "").strip():
        raise ValueError(f"a ruling is one of {RULINGS} with a `why`")
    fix = str(ruling.get("tooling_fix") or "").strip()
    if ruling["ruling"] == "process-fault" and not fix:  # feature 379 FR-001: the fault IS the fix, made and held, never filed
        raise ValueError("a `process-fault` ruling names its fault as `tooling_fix` - one sentence: the tool and the change")
    d = feature_dir(root)
    if d is None:
        raise ValueError("no active feature (.specify/feature.json) to record the ruling in")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    trig = owed(root).get(trigger, {})
    row = {"trigger": trigger, "kind": trig.get("kind", trigger.split(":", 1)[0]), "unit": trig.get("unit", ""),
           **({"dispatches": trig["dispatches"]} if "dispatches" in trig else {}),
           "ruling": ruling["ruling"], "why": ruling["why"], "what": ruling.get("what", ""), "utc": when,
           **({"tooling_fix": fix, "fix": "open"} if fix else {})}
    d.mkdir(parents=True, exist_ok=True)
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    _gm_row(d, {"kind": "arbiter", "trigger": trigger, "ruling": row["ruling"], "why": row["why"],
                **({"tooling_fix": fix} if fix else {}), "utc": when})
    if row["ruling"] == "accept" and row["kind"] == "round":
        accept_answers(root, row["unit"], f"accepted by the round arbiter ({trigger})")
    path = common_dir(root) / OWED
    state = _load(path)
    if state.pop(trigger, None) is not None:
        path.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    return row


def _gm_row(d: Path, row: Mapping[str, Any]) -> None:
    """A row of the GM's review after landing, and the feature's GM-review box with it (feature 375 FR-012)."""
    with (d / "gm-review.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        import importlib.util  # noqa: PLC0415

        spec = importlib.util.spec_from_file_location("gm_review", Path(__file__).resolve().parents[2] / "gm_review.py")
        if spec and spec.loader:
            gm = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(gm)
            gm.ensure_box(d)
    except (OSError, ImportError):  # pragma: no cover - a tree without the script records the row all the same
        pass


def open_fixes(d: Path) -> list[tuple[str, str]]:
    """(trigger, tooling_fix) of every arbiter tooling fix in feature `d` neither made nor declined (feature 379): the one
    rule `make tick` and the closing check both read. A later `fix_of` row settles one; the latest wins."""
    f = d / "arbiter.jsonl"
    fixes: dict[str, str] = {}
    for line in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("fix") == "open" and r.get("tooling_fix"):
            fixes[str(r.get("trigger"))] = str(r["tooling_fix"])
        elif r.get("fix_of") in fixes and r.get("status") in ("done", "declined"):
            fixes.pop(str(r["fix_of"]))
    return list(fixes.items())


def fix_hold(d: Path) -> str:
    """Why feature `d` may not move on while an arbiter tooling fix is open, naming each and both ways to settle it."""
    fixes = open_fixes(d)
    if not fixes:
        return ""
    return ("the round arbiter's tooling fix is open - make it, with its test, in this feature before going on (feature 379):\n"
            + "\n".join(f"    {t}: {fix}" for t, fix in fixes)
            + '\n  made:     make arbiter-fix-done ID="<trigger>" NOTE="<what was built>" TEST=<its test under tests/>'
            + '\n  overhaul: make arbiter-fix-declined ID="<trigger>" REASON="<why it overhauls a process>" (the GM reviews it after landing)')


def settle_fix(root: Path, trigger: str, status: str, note: str, test: str = "", now: str | None = None) -> dict[str, Any]:
    """`make arbiter-fix-done` / `arbiter-fix-declined`: close an open tooling fix of the active feature, on the GM's review."""
    d = feature_dir(root)
    if d is None:
        raise ValueError("no active feature (.specify/feature.json)")
    fix = dict(open_fixes(d)).get(trigger)
    if fix is None:
        raise ValueError(f"{trigger} has no open tooling fix in {d.name} - `make tick` names the open ones")
    if len(note.split()) < 2 or len(note) < 8:
        raise ValueError("the NOTE (or REASON) needs two words and eight characters - it is what the GM reads")
    if status == "done":
        t = (root / test).resolve() if test else None
        if t is None or not t.is_file() or (root / "tests").resolve() not in t.parents:
            raise ValueError(f"TEST={test or '<none>'} is not a file under tests/ - a fix is done with the test that proves it")
    elif status != "declined":
        raise ValueError("status is done or declined")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    row = {"fix_of": trigger, "status": status, "note": note, **({"test": test} if status == "done" else {}), "utc": when}
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    _gm_row(d, {"kind": f"arbiter-fix-{status}", "trigger": trigger, "tooling_fix": fix, "note": note,
                **({"test": test} if status == "done" else {}), "utc": when})
    return row


def env_ok(name: str, text: str) -> bool:
    return bool(re.search(rf'{name}="[^"]{{8,}}"', text)) or len(os.environ.get(name, "").split()) >= 2


def main(argv: list[str]) -> int:
    """`hm_arbiter.py ruled <trigger> <json file> --as <who>` - what `make arbiter-ruled` runs."""
    import sys  # noqa: PLC0415

    if argv[:1] == ["ruled"] and len(argv) == 5 and argv[3] == "--as":
        root = Path(".").resolve()
        try:
            row = record_ruling(root, argv[1], json.loads(Path(argv[2]).read_text(encoding="utf-8")), argv[4])
        except PermissionError as e:
            print(f"arbiter-ruled: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"arbiter-ruled: refused - {e}", file=sys.stderr)
            return 1
        print(f"arbiter-ruled: {row['trigger']} - {row['ruling']} (binding; recorded in arbiter.jsonl and for the GM's review)")
        return 0
    if argv[:1] == ["fix"] and len(argv) in (4, 5) and argv[1] in ("done", "declined"):
        try:
            settle_fix(Path(".").resolve(), argv[2], argv[1], argv[3], argv[4] if len(argv) == 5 else "")
        except ValueError as e:
            print(f"arbiter-fix-{argv[1]}: refused - {e}", file=sys.stderr)
            return 1
        print(f"arbiter-fix-{argv[1]}: {argv[2]} settled - on the GM's review (make gm-review)")
        return 0
    print("usage: hm_arbiter.py ruled <trigger> <json> --as round-arbiter | fix done|declined <trigger> <note> [<test>]", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
