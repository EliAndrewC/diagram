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
ruling - one per trigger, binding - in `specs/<feature>/arbiter.jsonl`. Only a QUESTION reaches the GM (feature 432, the GM
2026-10-26: "anything that ends up in GM review I actually know is important"): a ruling's `for_gm`, on any trigger, and a
declined fix are written to `gm-review.jsonl` as questions OWED escalation-check (`make gm-escalated`); every other ruling and
every fix made stays in `arbiter.jsonl`, and a ruling whose `why` or `what` hands the GM a decision without `for_gm` is refused. `continue` lifts a round cap by one round; `accept` and `process-fault` close the unit (its further dispatches are
refused). A ruling's `tooling_fix` - a `process-fault` always has one - is an OPEN item of the feature until
`make arbiter-fix-done` or `arbiter-fix-declined` settles it, and `make tick` and the closing check refuse while it is open
(feature 379: the first such fix lived only in a ruling's prose and was lost).
"""

from __future__ import annotations

import fcntl
import json
import os
import re
import subprocess
import sys
import time
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

OWED = "arbiter-owed.json"
#: the reviews an ask may be about, its ruling then standing as that review's verdict (feature 409)
REVIEWS = ("spec", "plan")
RULINGS = ("continue", "accept", "process-fault")
#: the hourly step-back's rulings (feature 383 FR-010): nothing to change, or a binding change of route (`what`)
HOUR_RULINGS = ("continue", "change-route")


def _checkpoint():  # noqa: ANN202 - scripts/reviews/checkpoint.py, imported by path (a hook's helper has no package)
    import sys  # noqa: PLC0415

    sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "reviews"))
    import checkpoint  # noqa: PLC0415

    return checkpoint


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


def asked_feature(root: Path, trigger: str) -> Path | None:
    """The feature an ask names by its SUBJECT's leading number (`ask:414-round3` -> `specs/414-*`), when exactly one directory
    has that number: `ask:414-round3` was filed under 416, the clone's active feature, so 414's ruling sat in 416's
    arbiter.jsonl and GM review (2026-10-24)."""
    # ...AND A ROUND TRIGGER BY THE PLAN OR SPEC IT NAMES (`round:spec-fidelity|plan:427-call-volume-refactors#T01@3`): 427's plan
    # round 3 was ruled while the session's `SPECIFY_FEATURE` still named 430, and its accept was filed in 430's arbiter.jsonl and
    # gm-review, and rewrote 430's plan-review.json, leaving 427's plan with no CLEAR verdict (2026-10-26)
    m = re.match(r"ask:(\d{3})-", trigger) or re.search(r"\|(?:plan|spec):(\d{3})-", trigger)
    dirs = sorted((root / "specs").glob(f"{m.group(1)}-*/")) if m else []
    return dirs[0] if len(dirs) == 1 else None


def feature_dir(root: Path, trigger: str = "") -> Path | None:
    """The active feature: the feature an ask names (`asked_feature`), else a page session's own (`L7R_FEATURE_DIRECTORY`, set
    by the page-session runner from its brief's directory), else the session's exported `SPECIFY_FEATURE` when its directory
    exists, else `.specify/feature.json`. Without the page session's own, feature 343's page session filed its round ruling
    under 378, the feature the clone's main session had last worked (2026-10-10)."""
    asked = asked_feature(root, trigger) if trigger else None
    if asked is not None:
        return asked
    own = os.environ.get("L7R_FEATURE_DIRECTORY", "").strip().rstrip("/")
    if own:
        return root / own
    named = os.environ.get("SPECIFY_FEATURE", "").strip().strip("/")
    if named and (root / "specs" / named).is_dir():  # the feature the session exported (the round arbiter on hour:391@2: a
        return root / "specs" / named  # session working 390 while feature.json named 391 had its hours charged to 391)
    try:
        fd = json.loads((root / ".specify" / "feature.json").read_text(encoding="utf-8")).get("feature_directory", "")
    except OSError, ValueError:
        return None
    return (root / str(fd).rstrip("/")) if fd else None


def _load(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError, ValueError:
        return {}


def owed(root: Path) -> dict[str, dict[str, Any]]:
    return _load(common_dir(root) / OWED)


def mine(root: Path, v: Mapping[str, Any]) -> bool:
    """Whether an owed trigger is the active feature's: fired in it, or recorded before triggers named their feature."""
    d = feature_dir(root)
    return not v.get("feature") or d is None or v.get("feature") == d.name


def aside(root: Path) -> list[str]:
    """The owed triggers another feature fired - left out of this feature's holds and batch, and named so none vanishes."""
    return sorted(f"{t} (feature {v.get('feature')})" for t, v in owed(root).items() if not mine(root, v))


def trip(root: Path, trigger: str, kind: str, unit: str, detail: str, now: float | None = None, review: str = "") -> bool:
    """Record a trigger once (a second firing of a trigger already owed or ruled changes nothing); True when it is new. `review`
    names the spec or plan review an ask is about (feature 409), so its ruling stands as that review's verdict."""
    if trigger in rulings(root, trigger):
        return False
    path = common_dir(root) / OWED
    path.parent.mkdir(parents=True, exist_ok=True)
    # UNDER A LOCK: a wave of checks refused at once runs one hook process each, and an unlocked read-modify-write kept only
    # the last writer's trigger - 343's M1c dispatched 13 modal-form round 3s in one message, and most of their triggers
    # never reached this file, so their bundles were built with no unit (2026-10-11, the arbiter's tooling fix)
    with (path.parent / (OWED + ".lock")).open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = _load(path)
        if trigger in state:
            return False
        d = feature_dir(root, trigger)
        # the feature it fired in: the owed file is the clone's, one for every feature, and a trigger ruled in its own feature
        # was swept into the next feature's batch (352's 0036 batch carried feature 368's three q:0047 triggers, 2026-10-11,
        # the arbiter's tooling fix) - `mine` keeps each feature to its own. GUARD_EDIT_OK: feature 352, the round arbiter's
        # tooling fix on round:quote-check|q:0036@3
        state[trigger] = {"kind": kind, "unit": unit, "detail": detail, "t": time.time() if now is None else now, "feature": d.name if d else ""}
        if review:
            state[trigger]["review"] = review
        m = re.match(r"(\d+) check dispatches", detail)
        if m:
            state[trigger]["dispatches"] = int(m.group(1))
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
        tmp.replace(path)
    return True


def rulings(root: Path, trigger: str = "") -> dict[str, dict[str, Any]]:
    """`{trigger: its ruling}` of the active feature (`specs/<feature>/arbiter.jsonl`), or of the feature `trigger` names."""
    d = feature_dir(root, trigger)
    out: dict[str, dict[str, Any]] = {}
    f = d / "arbiter.jsonl" if d else None
    for line in f.read_text(encoding="utf-8").splitlines() if f and f.is_file() else []:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if "trigger" in r:  # a `fix_of` row settles a ruling's tooling fix (feature 379); it is no ruling
            out[str(r["trigger"])] = r
    return out


def continues(root: Path, prefix: str, after: int = 0) -> int:
    """How many `continue` rulings the round triggers of one unit carry - each lifts its cap by one round; with `after`, only
    those past round `after` (a run counted afresh after a later change, feature 374 FR-005)."""
    return sum(1 for t, r in rulings(root).items() if t.startswith(prefix) and r.get("ruling") == "continue" and _round_no(t) > after)


def _round_no(trigger: str) -> int:
    """`round:<unit>@7` -> 7; 0 where the trigger names no round."""
    tail = trigger.rpartition("@")[2]
    return int(tail) if tail.isdigit() else 0


def closed(root: Path, prefix: str) -> str:
    """The ruling that closed the unit (`accept` / `process-fault`), or ''."""
    return next((str(r["ruling"]) for t, r in rulings(root).items() if t.startswith(prefix) and r.get("ruling") in RULINGS[1:]), "")


def blocking(root: Path, unit: str = "", gate: bool = False) -> list[str]:
    """The unruled triggers that hold the next dispatch on `unit` (its own round triggers, and every reversal or cascade), or,
    with `gate`, the next `make done` (a red-gate trigger)."""
    out = []
    for t, v in owed(root).items():
        if not mine(root, v):
            continue
        kind = v.get("kind")
        if gate and kind == "red-gate" or not gate and (kind in ("reversal", "cascade") or (kind == "round" and v.get("unit") == unit)):
            out.append(t)
    return sorted(out)


def refusal(triggers: list[str], root: Path | None = None) -> str:
    if not triggers:
        return ""
    t = triggers[0]
    batched = batch_triggers(root, triggers) if root is not None else []
    if len(batched) > 1 and t in batched:  # FR-017: a batch at the cap is ruled ONCE - the refusal names the batch, not the unit
        return (
            f"{len(batched)} round triggers are owed together ({', '.join(batched)}; feature 375 FR-017): ONE ruling for the "
            "batch - make arbiter-bundle BATCH=1, dispatch `round-arbiter` on the MANIFEST it prints, then make arbiter-ruled "
            "BATCH=1 FILE=<its JSON> AS=round-arbiter. A round you mean to ask about ahead of its cap joins it with "
            "TRIGGERS=\"<trigger> ...\". The feature goes on elsewhere meanwhile."
        )
    return (
        f"a tripwire is owed its ruling first ({', '.join(triggers)}; feature 375 FR-010/FR-011): make arbiter-bundle "
        f"TRIGGER=\"{t}\", dispatch `round-arbiter` on the MANIFEST it prints, then make arbiter-ruled TRIGGER=\"{t}\" "
        "FILE=<its JSON> AS=round-arbiter. Several units at their cap together (a batch of pop-ups or pages)? `make "
        "arbiter-bundle BATCH=1` puts every owed round trigger to ONE ruling (feature 375 amendment 2). "
        "The feature goes on elsewhere meanwhile. (Claude Code picks up a new agent file "
        "mid-session - this one did on 2026-10-10 - so only if `round-arbiter` is missing from the session's agent list: "
        "restart it, or carry ARBITER_OK=\"<reason>\" on the gate or in the check's prompt - logged.)"
    )


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


def cascade_state(root: Path, since: float = 0.0) -> tuple[str, int]:
    """(the next cascade trigger id, the dispatches at the last cascade ruling INSIDE the window opened at `since`): the id
    advances after ANY ruling; a ruling made before the window opened (a landed batch's) sets no floor, its count being of
    dispatches the window no longer counts (feature 374, cascade@1's tooling fix)."""
    ruled = [r for t, r in rulings(root).items() if t.startswith("cascade@")]
    inside = [r for r in ruled if _epoch(str(r.get("utc") or "")) >= since]
    last = max((int(r.get("dispatches") or 0) for r in inside), default=0)
    return f"cascade@{len(ruled) + 1}", last


def _epoch(utc: str) -> float:
    """A ruling's `utc` (`%Y-%m-%dT%H:%M:%SZ`) as epoch seconds; 0 where it reads as none."""
    import calendar  # noqa: PLC0415

    try:
        return float(calendar.timegm(time.strptime(utc, "%Y-%m-%dT%H:%M:%SZ")))
    except ValueError:
        return 0.0


def nit_answers(root: Path, trigger: str, old: str, new: str) -> list[str]:
    """`make arbiter-nit`: the wording an `accept` ruling asked to fix in passing, made, answers the accepted unit again at
    today's words (feature 374 wave 120: the bridgehead pop-up's nit, made as asked, re-owed the check the ruling had closed,
    and a second ruling was spent on it). Only that wording: the ruling's `what` quotes both the old words and the new, the
    unit's file holds the new and no longer the old - any other edit is a new round's business."""
    r = rulings(root).get(trigger)
    if not r or r.get("ruling") != "accept" or r.get("kind") != "round":
        raise ValueError(f"{trigger} has no `accept` ruling on a round - a nit is made only under one")
    what = str(r.get("what") or "")
    if not old.strip() or not new.strip() or old not in what or new not in what:
        raise ValueError(f"the ruling's `what` must quote both OLD and NEW - it reads: {what[:300]}")
    check, _, subject = str(r.get("unit") or "").partition("|")
    own = root / f"l7r/diagram/interactive/assets/modals/{subject[6:]}.md" if subject.startswith("modal:") else None
    text = own.read_text(encoding="utf-8") if own and own.is_file() else ""
    if new not in text or old in text:
        raise ValueError(f"{own or subject} must hold NEW and no longer OLD - make the edit first (a page's nit is not this target's)")
    return accept_answers(root, f"{check}|{subject}", f"the wording the round arbiter's accept asked for ({trigger}): {old!r} -> {new!r}")


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


def unit_of(trigger: str) -> str:
    """`round:<check>|<subject>@N` -> `<check>|<subject>`; '' for any other trigger (feature 375 amendment 2, FR-018: a round
    asked about ahead of the cap was never recorded as owed, and its bundle and its ruling row lost the unit)."""
    if not trigger.startswith("round:") or "|" not in trigger:
        return ""
    body = trigger[len("round:") :]
    return body.rpartition("@")[0] if "@" in body else body


def batch_triggers(root: Path, extra: Iterable[str] = ()) -> list[str]:
    """THE BATCH (feature 375 amendment 2, FR-017): every round trigger owed now - the units whose checks reached the cap
    together - but a spec review's own rounds (one spec, ruled alone), plus any round the session names (`TRIGGERS=`), asked
    about ahead of the cap. Unrelated units in it are the arbiter's exceptions."""
    own = [t for t, v in owed(root).items() if v.get("kind") == "round" and not t.startswith("round:spec-fidelity|") and mine(root, v)]
    return sorted(set(own) | {t for t in extra if t.startswith("round:") and not t.startswith("round:spec-fidelity|")})


def rekeys(prior: Mapping[str, Any], trigger: str, ruling: Mapping[str, Any]) -> bool:
    """May the arbiter record its SAME ruling on a trigger again? Only to carry the sheet's content key a review unit's round
    row was written without (feature 433: a recorder bug - the owed entry's `<check>|` prefix - left the accept on
    building-review--hayakawa-magistracy keyless, so the review gate could not honor it); the ruling itself may not change,
    so the one-ruling rule stands, and `record_ruling` asks too that the unit HAS a sheet to key (a record check's round has
    none, and stays ruled once)."""
    return (
        trigger.startswith("round:")
        and not trigger.startswith("round:spec-fidelity|")
        and not prior.get("content_key")
        and prior.get("ruling") == ruling.get("ruling")
    )


def record_ruling(root: Path, trigger: str, ruling: Mapping[str, Any], declared: str, now: str | None = None, batch: bool = False) -> dict[str, Any]:
    """Record the round arbiter's ruling: binding, one per trigger (FR-011). A round trigger owed together with others is
    ruled with them, as a batch (FR-017) - not alone."""
    if declared != "round-arbiter":
        raise PermissionError("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, recorded, not a proof")
    if (prior := rulings(root, trigger).get(trigger)) is not None and not (rekeys(prior, trigger, ruling) and unit_content_key(root, unit_of(trigger))):
        raise ValueError(f"{trigger} is already ruled - one ruling per trigger, binding; the session neither re-asks nor overrules")
    others = [t for t in batch_triggers(root) if t != trigger]
    if not batch and trigger in batch_triggers(root, [trigger]) and others:
        raise ValueError(
            f"{len(others)} other round trigger(s) are owed with it - rule them together, ONE ruling: make "
            "arbiter-bundle BATCH=1, then make arbiter-ruled BATCH=1 FILE=<its JSON> AS=round-arbiter (FR-017)"
        )
    hour = trigger.startswith("hour:")  # GUARD_EDIT_OK: feature 383 FR-009/FR-010 - the hourly step-back's own two rulings
    if ruling.get("ruling") not in (HOUR_RULINGS if hour else RULINGS) or not str(ruling.get("why") or "").strip():
        raise ValueError(f"a ruling is one of {HOUR_RULINGS if hour else RULINGS} with a `why`")
    if hour and ruling["ruling"] == "change-route" and not str(ruling.get("what") or "").strip():
        raise ValueError("a `change-route` ruling names in `what` the loop or the unresearched number and the route to take")
    fix = str(ruling.get("tooling_fix") or "").strip()
    fix_on = str(ruling.get("tooling_fix_on") or "") if batch else ""  # a batch's one fix, held by another of its rows (375 a2)
    if ruling["ruling"] == "process-fault" and not fix and not fix_on:  # feature 379 FR-001: the fault IS the fix, made and held
        raise ValueError("a `process-fault` ruling names its fault as `tooling_fix` - one sentence: the tool and the change")
    measure = fix_measure_of(ruling) if fix else {}
    d = feature_dir(root, trigger)
    if d is None:
        raise ValueError("no active feature (.specify/feature.json) to record the ruling in")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    trig = owed(root).get(trigger, {})
    row = {
        "trigger": trigger,
        "kind": trig.get("kind", trigger.split(":", 1)[0]),
        "unit": trig.get("unit") or unit_of(trigger),
        **({"dispatches": trig["dispatches"]} if "dispatches" in trig else {}),
        # the question as it fired (a round's count, a reversal's text, an ask's WHY=), kept with its ruling: `make gm-review
        # EXPLAIN=1` shows the GM what was asked, and the owed entry that held it is dropped below (GUARD_EDIT_OK: the GM
        # 2026-10-12 could not tell what a row asked him to rule on; nothing loosened)
        **({"asked": trig["detail"]} if trig.get("detail") else {}),
        "ruling": ruling["ruling"],
        "why": ruling["why"],
        "what": ruling.get("what", ""),
        "utc": when,
        **({"tooling_fix": fix, "fix": "open", **measure} if fix else {}),
        **({"tooling_fix_on": fix_on} if fix_on and not fix else {}),
        # a spec review's ruling names the spec it ruled on: the review gate honors it only while the spec still reads so
        # an ask about a review (feature 409) names it, and a spec review's its digest, as a spec round's ruling does
        # ...a claims ask's review too (feature 417 T05, 2026-10-25): `REVIEW=claims:<keys>` was dropped here, so the accept the
        # GM's 2026-10-24 ruling makes the claims' verdict never reached the index and the claims gate went on refusing them
        **({"review": trig["review"]} if trig.get("review") in REVIEWS or str(trig.get("review") or "").startswith("claims:") else {}),
        **({"spec_sha": spec_body_sha(d)} if trigger.startswith("round:spec-fidelity|") or trig.get("review") == "spec" else {}),
        # a review unit's ruling names the sheet it ruled on, so the review gate honors an accept while the sheet still
        # reads so (feature 374 batch 5: an accepted unit's last verdict was NEEDS-WORK at an older key, and the gate refused)
        **({"content_key": ck} if trigger.startswith("round:") and not trigger.startswith("round:spec-fidelity|") and (ck := unit_content_key(root, row_unit(trig, trigger))) else {}),
    }
    for_gm = str(ruling.get("for_gm") or "").strip()
    if for_gm:
        row["for_gm"] = for_gm
    elif hands_the_gm(f"{row['why']} {row['what']}"):
        raise ValueError(
            "this ruling hands the GM a decision in its `why` or `what` - put the question in `for_gm` instead, the one door to "
            "him: it is written owed escalation-check and reaches him only if kept (feature 432, FR-003)"
        )
    d.mkdir(parents=True, exist_ok=True)
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    # GUARD_EDIT_OK: feature 432 FR-001 - a ruling reaches the GM only as a question (`for_gm`), owed escalation-check; the
    # rest stays in arbiter.jsonl (feature 375 queued every ruling: 465 open rows, 443 of them not his - 432's audit)
    if for_gm:
        _gm_question(d, for_gm, trigger, when)
    if hour:  # the hour is answered: the checkpoint's clock restarts from when it opened (scripts/reviews/checkpoint.py)
        _checkpoint().close_checkpoint(root, trigger)
    if row["ruling"] == "accept" and row["kind"] == "round":
        accept_answers(root, row["unit"], f"accepted by the round arbiter ({trigger})")
    path = common_dir(root) / OWED
    with (path.parent / (OWED + ".lock")).open("w") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        state = _load(path)
        if state.pop(trigger, None) is not None:
            path.write_text(json.dumps(state, indent=1, sort_keys=True), encoding="utf-8")
    return row


def record_batch(root: Path, ruling: Mapping[str, Any], declared: str, now: str | None = None) -> list[dict[str, Any]]:
    """Record ONE ruling for a batch of round triggers (feature 375 amendment 2, FR-017; the GM 2026-10-11: "a whole batch of
    pop-ups reaching the round cap at once should get a single ruling"): each trigger under the batch's ruling or its own
    exception, so each unit's hold, closure and GM-review row work as they do alone. A batch `tooling_fix` is ONE fix: recorded
    on the first trigger under the batch's ruling (else the first trigger), every other row under the batch naming the trigger
    that holds it (`tooling_fix_on`) - so a batch `process-fault` records whole and opens its fix once (the plan review of
    amendment 2 found the second trigger refused and an exception on the first dropping the fix). Every row is checked before
    any is written."""
    triggers = [str(t) for t in ruling.get("triggers") or []]
    exceptions = ruling.get("exceptions") or {}
    if not triggers:
        raise ValueError("a batch ruling names its `triggers` - every trigger its bundle carried")
    twice = sorted({t for t in triggers if triggers.count(t) > 1})
    if twice:  # a repeat would write its first row and then refuse - checked before anything is written (plan review round 2)
        raise ValueError(f"a trigger is named twice: {', '.join(twice)}")
    stray = sorted(set(exceptions) - set(triggers))
    if stray:
        raise ValueError(f"an exception names a trigger the batch does not carry: {', '.join(stray)}")
    if declared != "round-arbiter":
        raise PermissionError("declined: only the `round-arbiter` subagent records a ruling (AS=round-arbiter) - a declaration, recorded, not a proof")
    done = sorted(set(triggers) & set(rulings(root)))
    if done:
        raise ValueError(f"already ruled: {', '.join(done)} - one ruling per trigger, binding")
    base = {k: v for k, v in ruling.items() if k not in ("triggers", "exceptions", "tooling_fix")}
    fix = str(ruling.get("tooling_fix") or "").strip()
    under = [t for t in triggers if t not in exceptions]
    # the batch's fix never overwrites an exception's own: with no trigger under the batch's ruling it goes on the first
    # exception carrying no fix of its own (plan review round 2); every exception with its own fix - the reply is ambiguous
    free = [t for t in triggers if t in exceptions and not str(exceptions[t].get("tooling_fix") or "").strip()]
    if fix and not under and not free:
        raise ValueError("every trigger is an exception with its own `tooling_fix` - where does the batch's fix go? Fold it into one of them, or leave the batch's out")
    holder = (under or free)[0] if fix else ""
    plan: list[tuple[str, dict[str, Any]]] = []
    for t in triggers:
        one = dict(exceptions[t]) if t in exceptions else dict(base)
        if t == holder:  # the batch's fix with its own measure (feature 385 T119, D139), on an exception's row too
            one.update({"tooling_fix": fix, **{k: ruling[k] for k in ("fix_minutes",) if k in ruling}})
        elif fix and t in under:
            one["tooling_fix_on"] = holder
        plan.append((t, one))
    for t, one in plan:  # all checked first: a bad row writes nothing
        if one.get("ruling") not in RULINGS or not str(one.get("why") or "").strip():
            raise ValueError(f"{t}: a ruling is one of {RULINGS} with a `why`")
        if one["ruling"] == "process-fault" and not (str(one.get("tooling_fix") or "").strip() or one.get("tooling_fix_on")):
            raise ValueError(f"{t}: a `process-fault` ruling names its fault as `tooling_fix` (the batch's, or its own)")
    return [record_ruling(root, t, one, declared, now, batch=True) for t, one in plan]


def fix_measure_of(ruling: Mapping[str, Any]) -> dict[str, Any]:
    """A tooling fix's `fix_minutes`, checked: the cost it measured, which `make fix-yield` shows beside the fix's tools' numbers
    (feature 385 T119, D139). Its `fix_measure` - a regex over the session's commands - was retired with the command-rate
    reading by feature 406 (D165): a fix is now read by what its tools did since it was made, found from its settling commit."""
    how = "a `tooling_fix` names `fix_minutes`, the cost it measured this hour (feature 385 T119)"
    try:
        minutes = float(ruling.get("fix_minutes"))  # type: ignore[arg-type]
    except TypeError, ValueError:
        raise ValueError(how) from None
    if minutes < 0:
        raise ValueError(how)
    return {"fix_minutes": minutes}


def spec_body_sha(d: Path) -> str:
    """sha256 of what a review of feature `d`'s spec judged: spec.md above its Review history (the record of rounds and rulings
    grows): its title and everything from the first `## ` heading, the header block between them dropped WHOLE - a Status line
    rewritten at landing is no amendment, wrapped onto a second line or not (plan review rounds 3 and 4 found an accepted
    feature refused at its own landing push, the second time by a two-line Status)."""
    import hashlib  # noqa: PLC0415

    text = (d / "spec.md").read_text(encoding="utf-8") if (d / "spec.md").is_file() else ""
    body = text.split("\n## Review history", 1)[0]
    head, sep, rest = body.partition("\n## ")
    return hashlib.sha256((head.split("\n", 1)[0] + sep + rest).encode()).hexdigest()


def house_styled(obj: Any) -> Any:  # noqa: ANN401 - a ruling's JSON, any shape
    """A ruling with its text in the house style (American spellings) before it is recorded - the GM 2026-10-24: T26's ruling
    wrote a British spelling into arbiter.jsonl and gm-review.jsonl, and the gate's preflight refused the landing on it. The edit hooks
    correct what a session writes; a record a make target writes passes none of them."""
    import hm_house  # noqa: PLC0415 - the module beside this one

    if isinstance(obj, str):
        return hm_house.americanize(obj)
    if isinstance(obj, list):
        return [house_styled(x) for x in obj]
    if isinstance(obj, dict):
        return {k: house_styled(v) for k, v in obj.items()}
    return obj


def spec_ruled(d: Path) -> str:
    """The arbiter's `accept` or `process-fault` on feature `d`'s spec review that stands for its verdict - one ruled on the
    spec as it reads now - or '' (feature 379 amendment 2; `review-gate.sh` asks this)."""
    f, sha = d / "arbiter.jsonl", spec_body_sha(d)
    for line in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        spec_review = str(r.get("trigger", "")).startswith(f"round:spec-fidelity|{d.name}#") or r.get("review") == "spec"  # an asked one too (409)
        if spec_review and r.get("ruling") in ("accept", "process-fault") and r.get("spec_sha") == sha:
            return str(r["trigger"])
    return ""


def row_unit(trig: Mapping[str, Any], trigger: str) -> str:
    """The unit a trigger is about: its owed entry's, else read from the trigger itself."""
    return str(trig.get("unit") or unit_of(trigger))


def review_unit(unit: str) -> str:
    """The review unit a round row is about, without the check's `<check>|` prefix its owed entry carries: the review gate
    asks by the bare unit (`building-review--hayakawa-magistracy`), the round's entry names `building-review|building-review--
    hayakawa-magistracy` (feature 433: the arbiter's accept on that unit carried no content key and matched no unit, so the gate
    went on refusing a sheet it had accepted)."""
    return unit.split("|", 1)[1] if "|" in unit else unit


def unit_content_key(root: Path, unit: str) -> str:
    """A review unit's sheet as it reads now (`review_prereq.py content-key`), or '' where it has none."""
    import subprocess  # noqa: PLC0415

    script = Path(__file__).resolve().parents[2] / "reviews" / "review_prereq.py"
    r = subprocess.run([sys.executable, str(script), "content-key", "--clone", str(root), "--map", review_unit(unit)], capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 else ""


def unit_ruled(d: Path, unit: str, content: str) -> str:
    """The arbiter's `accept` or `process-fault` on a round of review unit `unit` that stands for its verdict - one ruled on
    the sheet as it reads now (`content`) - or '' (feature 374 batch 5; `review-gate.sh` asks this)."""
    f = d / "arbiter.jsonl"
    for line in f.read_text(encoding="utf-8").splitlines() if f.is_file() and content else []:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if review_unit(str(r.get("unit", ""))) == review_unit(unit) and str(r.get("trigger", "")).startswith("round:") and r.get("ruling") in ("accept", "process-fault") and r.get("content_key") == content:
            return str(r["trigger"])
    return ""


#: words that hand the GM a decision in a ruling's `why` or `what` (feature 432, FR-003, plan D4): 335#2 and 374#60 said so in
#: their prose, and 374#60 never reached him
_HANDS_THE_GM = re.compile(r"the GM'?s (to decide|call|question|decision)|for the GM to|held for the GM|the GM (must|should) decide|GM'?s choice", re.I)


def hands_the_gm(text: str) -> bool:
    """Does a ruling's prose hand the GM a decision (feature 432, FR-003)?"""
    return bool(_HANDS_THE_GM.search(text))


def _gm_question(d: Path, question: str, source: str, when: str) -> None:
    """A question for the GM, OWED escalation-check (`scripts/gm_review.py question`; feature 432, FR-001/FR-002)."""
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("gm_review", Path(__file__).resolve().parents[2] / "gm_review.py")
    assert spec is not None and spec.loader is not None
    gm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gm)
    gm.question(d, question, source, when)


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
    return (
        "the round arbiter's tooling fix is open - make it, with its test, in this feature before going on (feature 379):\n"
        + "\n".join(f"    {t}: {fix}" for t, fix in fixes)
        + '\n  made:     make arbiter-fix-done ID="<trigger>" NOTE="<what was built>" TEST=<its test under tests/> LAND="<the fix\'s files>" F=<feature> TICK=<the task> (lands them, settles the fix, ticks the task)'
        + '\n  overhaul: make arbiter-fix-declined ID="<trigger>" REASON="<why it overhauls a process>" (a question for the GM, owed escalation-check)'
    )


def fix_home(root: Path, trigger: str) -> Path | None:
    """The feature directory holding `trigger`'s open tooling fix: the active feature, else the feature the trigger names
    (`hour:<feature>@n`), else any feature that holds it open (the round arbiter on hour:391@3, 2026-10-18: a ruling filed
    under the feature the pointer named was refused when the session settled it from the feature it was about)."""
    active = feature_dir(root)
    named = re.match(r"^hour:([^@]+)@", trigger)
    for d in [active, root / "specs" / named.group(1) if named else None, *sorted((root / "specs").glob("*/"))]:
        if d is not None and d.is_dir() and trigger in dict(open_fixes(d)):
            return d
    return None


def settle_fix(root: Path, trigger: str, status: str, note: str, test: str = "", now: str | None = None) -> dict[str, Any]:
    """`make arbiter-fix-done` / `arbiter-fix-declined`: close an open tooling fix in the feature that holds it (`fix_home`); a
    declined one becomes a question for the GM, owed escalation-check (feature 432, FR-001)."""
    d = fix_home(root, trigger) or feature_dir(root)
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
        # GUARD_EDIT_OK: feature 385 - an ENGINE fix lands with its feature: `land-tooling` refuses engine files, and the tick this
        # fix holds is the one that lets the feature land, so "on main first" could never be met (T01: a crashed roll's traceback
        # kept, in l7r/diagram/pipeline/rollcache.py). With ENGINE=1 the fix is done once its test is committed in the clone, and
        # the row says it lands with the feature; a tooling fix still lands first.
        if not on_main(root, test):  # amendment 1, FR-006: made in one clone is not done for the sessions on the mirror's hooks
            if not (os.environ.get("ARBITER_FIX_ENGINE") and committed_here(root, test)):
                raise ValueError(
                    f"{test} is not on main as it is here - land and settle it in one command: the same make arbiter-fix-done with LAND=\"<the fix's files>\" (it runs make land-tooling on them first)"
                    " (an ENGINE fix, which land-tooling refuses, lands with its feature: commit it and its test, then the same command with ENGINE=1)"
                )
            note += " (an engine fix: it lands with the feature)"
    elif status != "declined":
        raise ValueError("status is done or declined")
    when = now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    row = {"fix_of": trigger, "status": status, "note": note, **({"test": test} if status == "done" else {}), "utc": when}
    with (d / "arbiter.jsonl").open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    if status == "declined":
        _gm_question(d, f"Build this tooling fix the round arbiter asked for, which the session declined? The fix: {fix} Declined because: {note}", trigger, when)
    return row


def committed_here(root: Path, path: str) -> bool:
    """Is `path` committed at the clone's HEAD exactly as it stands in the tree (no uncommitted change to it)?"""
    import subprocess  # noqa: PLC0415

    head = subprocess.run(["git", "-C", str(root), "rev-parse", "-q", "--verify", f"HEAD:{path}"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(root), "status", "--porcelain", "--", path], capture_output=True, text=True)
    return head.returncode == 0 and not dirty.stdout.strip()


def on_main(root: Path, path: str) -> bool:
    """Is `path` on main (after a fetch) with the same content as at the clone's HEAD (feature 379 amendment 1, FR-006)?"""
    import subprocess  # noqa: PLC0415

    def blob(ref: str) -> str:
        r = subprocess.run(["git", "-C", str(root), "rev-parse", "-q", "--verify", f"{ref}:{path}"], capture_output=True, text=True)
        return r.stdout.strip() if r.returncode == 0 else ""

    subprocess.run(["git", "-C", str(root), "fetch", "-q", "origin"], capture_output=True)
    here = blob("HEAD")
    return bool(here) and here == blob("origin/main")


def env_ok(name: str, text: str) -> bool:
    return bool(re.search(rf'{name}="[^"]{{8,}}"', text)) or len(os.environ.get(name, "").split()) >= 2


def _approach():  # noqa: ANN202 - the module, loaded by path (feature 385 D9)
    import importlib.util  # noqa: PLC0415

    path = Path(__file__).resolve().parents[2] / "gates" / "approach_gate.py"
    spec = importlib.util.spec_from_file_location("approach_gate", path)
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def main(argv: list[str]) -> int:
    """`hm_arbiter.py ruled <trigger> <json file> --as <who>` - what `make arbiter-ruled` runs."""

    import sys  # noqa: PLC0415

    if argv[:1] == ["ruled"] and len(argv) == 5 and argv[3] == "--as":
        root = Path(".").resolve()
        try:
            row = record_ruling(root, argv[1], house_styled(json.loads(Path(argv[2]).read_text(encoding="utf-8"))), argv[4])
        except PermissionError as e:
            print(f"arbiter-ruled: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"arbiter-ruled: refused - {e}", file=sys.stderr)
            return 1
        print(f"arbiter-ruled: {row['trigger']} - {row['ruling']} (binding; recorded in arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)")
        # GUARD_EDIT_OK: feature 385 T02, plan D9 - an hour or red-gate ruling owes the task's part B answered (nothing loosened)
        owed = _approach().ruled(root, row["trigger"])
        plan_review = row["trigger"].startswith("round:spec-fidelity|plan:") or row.get("review") == "plan"  # an asked one too (409)
        if plan_review and row["ruling"] in ("accept", "process-fault"):  # feature 385 T16
            d = feature_dir(root)
            if d is not None:
                sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "gates"))
                import plan_gate  # noqa: PLC0415

                print(f"arbiter-ruled: {len(plan_gate.arbiter_accept(d, row['trigger']))} plan block(s) recorded CLEAR - the accept is the plan's verdict")
        claims_review = str(row.get("review") or "")
        if claims_review.startswith("claims:") and row["ruling"] == "accept":  # the GM 2026-10-24: the accept is the claims' verdict
            keys = claims_review[len("claims:") :]
            done = subprocess.run(
                [sys.executable, str(Path(__file__).resolve().parents[2] / "record" / "claims.py"), "--root", str(root), "accept", "--keys", keys, "--trigger", row["trigger"]],
                capture_output=True,
                text=True,
            )
            print((done.stdout + done.stderr).strip())
        if owed:
            print(owed)
        return 0

    if argv[:1] == ["ruled-batch"] and len(argv) == 4 and argv[2] == "--as":  # `make arbiter-ruled BATCH=1` (375 FR-017)
        root = Path(".").resolve()
        try:
            rows = record_batch(root, house_styled(json.loads(Path(argv[1]).read_text(encoding="utf-8"))), argv[3])
        except PermissionError as e:
            print(f"arbiter-ruled: {e}", file=sys.stderr)
            return 2
        except (OSError, ValueError) as e:
            print(f"arbiter-ruled: refused - {e}", file=sys.stderr)
            return 1
        for row in rows:
            print(f"arbiter-ruled: {row['trigger']} - {row['ruling']}")
            owed = _approach().ruled(root, row["trigger"])  # GUARD_EDIT_OK: feature 385 D9, as for a single ruling
            if owed:
                print(owed)
        print(f"arbiter-ruled: the batch's {len(rows)} triggers recorded (binding; each in arbiter.jsonl; a for_gm question goes to escalation-check: make gm-review)")
        return 0
    if argv[:1] == ["gate-held"] and len(argv) == 1:  # the `done` recipe's first step and `make land` (feature 405 T44, D18)
        # THE GATE ASKS, NOT ONLY THE HOOK: the hook sees a typed `make done`, but T11's 05:09 `make land` ran its gate as a
        # subprocess past `red-gate@2026-10-21T05:02:38Z`, owed and never ruled. GUARD_EDIT_OK: feature 405 T44 - nothing loosened
        why = refusal(blocking(Path(".").resolve(), gate=True))
        if why:
            print(f"make done: refused - {why}", file=sys.stderr)
            return 1
        return 0
    if argv[:1] == ["spec-ruled"] and len(argv) == 2:  # review-gate.sh: does a ruling stand for this spec's verdict?
        return 0 if spec_ruled(Path(argv[1])) else 1
    if argv[:1] == ["unit-ruled"] and len(argv) == 3:  # review-gate.sh: does a ruling stand for this review unit's verdict?
        d = feature_dir(Path(".").resolve())
        return 0 if d is not None and unit_ruled(d, argv[1], argv[2]) else 1
    if argv[:1] == ["ask"] and len(argv) in (3, 4):  # `make arbiter-ask` (feature 379 amendment 2, FR-008/FR-009)
        subject, why = argv[1].strip(), argv[2].strip()
        review = argv[3].strip() if len(argv) == 4 else ""  # REVIEW= (feature 409): the spec or plan review the ask is about
        if not re.fullmatch(r"[\w.-]+", subject) or len(why.split()) < 2 or len(why) < 8:
            print("arbiter-ask: SUBJECT is one short id (letters, digits, . _ -) and WHY the question, two words or more", file=sys.stderr)
            return 2
        if review and review not in REVIEWS and not (review.startswith("claims:") and len(review) > len("claims:")):
            print(f"arbiter-ask: REVIEW= is spec, plan or claims:<key>;<key> (the review whose verdict the ruling stands as), or left out - not {review!r}", file=sys.stderr)
            return 2
        trigger = f"ask:{subject}"
        if trigger in rulings(Path(".").resolve(), trigger):
            print(f"arbiter-ask: {trigger} is already ruled - one ruling per trigger, binding; ask a new SUBJECT for a new question", file=sys.stderr)
            return 1
        stands = f"(REVIEW={review}: an accept stands as the {review} review's verdict)" if review else ""
        trip(Path(".").resolve(), trigger, "ask", "", f"{why} {stands}".strip(), review=review)
        print(f"arbiter-ask: {trigger} recorded - the round arbiter rules on it, not the GM (its ruling reaches him only as a kept for_gm question, feature 432); dispatch `round-arbiter` with the MANIFEST below")
        if stands:
            print(f"arbiter-ask: {stands}")
        elif re.match(r"\d+-(spec|plan)-", subject) or re.search(r"spec-fidelity|plan review|spec review", why, re.I):
            # the question's words count too (2026-10-25: ask:420-round3 asked about spec-fidelity's round 3 under a
            # subject without "spec", got no hint, and its accept could not stand as the verdict - the push refused)
            print("arbiter-ask: hint - if this asks about a spec or plan review, ask it with REVIEW=spec or REVIEW=plan, so an accept stands as its verdict (feature 409)")
        return 0
    if argv[:1] == ["fix"] and len(argv) in (4, 5) and argv[1] in ("done", "declined"):
        # several fixes one change made settle together: ID="<trigger> <trigger> ..." (2026-10-11: 343 carried 36 open fixes,
        # many naming the same few bundle defects, one ruling each before the batch ruling existed)
        root, ids = Path(".").resolve(), argv[2].split()
        d = feature_dir(root)
        unknown = [i for i in ids if fix_home(root, i) is None]
        if unknown or not ids:
            found = [t for f in sorted((root / "specs").glob("*/")) for t, _ in open_fixes(f)]
            print(
                f"arbiter-fix-{argv[1]}: refused - no open tooling fix: {', '.join(unknown) or '(no ID)'}; searched the active "
                f"feature ({d.name if d else 'none'}), the feature an hour trigger names, and every feature; open now: "
                f"{', '.join(found) or 'none'}",
                file=sys.stderr,
            )
            return 1
        try:
            for i in ids:
                settle_fix(root, i, argv[1], argv[3], argv[4] if len(argv) == 5 else "")
        except ValueError as e:
            print(f"arbiter-fix-{argv[1]}: refused - {e}", file=sys.stderr)
            return 1
        print(f"arbiter-fix-{argv[1]}: {len(ids)} fix(es) settled - {', '.join(ids)}" + (" - each a question owed escalation-check (make gm-review)" if argv[1] == "declined" else ""))
        return 0
    if argv[:1] == ["nit"] and len(argv) == 4:  # `make arbiter-nit` (feature 374 wave 120, the arbiter's tooling fix)
        try:
            done = nit_answers(Path(".").resolve(), argv[1], argv[2], argv[3])
        except ValueError as e:
            print(f"arbiter-nit: refused - {e}", file=sys.stderr)
            return 1
        print(f"arbiter-nit: {len(done)} unit(s) answered at today's words - {', '.join(done) or 'none owed'}")
        return 0
    print("usage: hm_arbiter.py ruled <trigger> <json> --as round-arbiter | fix done|declined <trigger> <note> [<test>] | nit <trigger> <old> <new>", file=sys.stderr)
    return 2


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv[1:]))
