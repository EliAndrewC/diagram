"""A finding a page edit surfaced on code left unchanged is CARRIED, not refused (feature 385 amendment 3, FR-013, plan D26-D29).

    python3 scripts/record/claims.py carry --feature <n> [--task Txx]     (`make claims-carry F=<n> [T=<Txx>]`)

WHY (the GM, 2026-10-17, "Yes, please lock in option three."): at T03's landing a one-paragraph edit to page 0246 re-owed
the claims that cite it, and the three findings that came back - all on code T03 never touched - refused the push as
INTRODUCED. Option 3: such a finding never blocks the landing; it is filed as an open task of the feature being landed, so that
feature cannot close while it stands.

A LANDING WITH NO ENGINE CODE FILES INTO THE CLAIMS FEATURE (the GM, 2026-10-26: "Yes, a finding carried by a landing that
changes no engine code should go to 405 instead. Please make that the standing rule"): a research-record or tooling landing
cannot fix engine code, and option 3 held feature 422 (miso and soy sauce) open on five engine findings while 405, the feature
that fixes claims findings, was on hold. So `target` is `CLAIMS_FEATURE` when the delta changes no engine code, the active
feature otherwise. "Engine code" is the project's one definition (`l7r.diagram.ci.delta`): a path `is_engine` accepts (so not
`l7r/diagram/ci/`), changed in what it executes - a comment-only, docstring-only or formatting edit is no engine change (the GM
2026-08-25, 08-26, 08-28; spec-fidelity on this amendment, 2026-10-26).

`claims.classify` decides what is carried (D26). This module keeps the record: `specs/<feature>/claims-carried.jsonl`, one row
`{"task", "keys", "utc"}` a filing. A key is FILED while a row of the ACTIVE feature's record names it and that row's task is
still an open box in its `tasks.md` (D27): ticking the task un-files it, so a finding still standing refuses again; another
feature's record never files it, so a finding cannot be parked in a long-lived feature while this one closes (spec-fidelity,
T13 round 1) - except the claims feature's, for a landing with no engine code (above). `speckit-todo.py`'s open-task refusal honors a `[lands-open]` box a row names (D28).
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

RECORD = "claims-carried.jsonl"
#: the standing feature that fixes claims findings (the GM, 2026-10-26): a landing with no engine code files its carries here.
#: When 405 closes, the feature that takes over its claims work is named here.
CLAIMS_FEATURE = "405"
_CHECKOUT = Path(__file__).resolve().parents[2]
_BOX = re.compile(r"^- \[( |x)\] (T\d+)\b(.*)$", re.M)
_LANDS_OPEN = " [lands-open]"


def _plan_gate() -> Any:  # noqa: ANN401 - the module
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "gates"))
    import plan_gate  # noqa: PLC0415 - the moved scripts it imports

    return plan_gate


def active_feature(root: Path) -> Path | None:
    """The feature being landed: the active task's (`plan_gate.active_task`), or None."""
    return _plan_gate().active_task(root)[0]


def _git_lines(root: Path, *args: str) -> list[str]:
    out = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    return [ln.strip() for ln in out.stdout.splitlines() if ln.strip()] if out.returncode == 0 else []


def _engine_tools() -> tuple[Any, Any]:
    """(`l7r.diagram.ci.delta.is_engine`, gate-stamp's `content_id`) from THIS checkout, not the root it reads (a fixture tree
    has no engine package)."""
    import importlib.util  # noqa: PLC0415

    if str(_CHECKOUT) not in sys.path:
        sys.path.insert(0, str(_CHECKOUT))
    from l7r.diagram.ci.delta import is_engine  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("gate_stamp", _CHECKOUT / "scripts" / "gates" / "gate-stamp.py")
    assert spec is not None and spec.loader is not None
    gs = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gs)
    return is_engine, gs.content_id


def touches_engine(root: Path) -> bool:
    """Does this tree's delta - its commits since the merge base with origin/main (HEAD with none), its uncommitted and its
    untracked files - change engine code, as `l7r.diagram.ci.delta` decides it (`_semantically_changed`)?"""
    is_engine, content_id = _engine_tools()
    base = (_git_lines(root, "merge-base", "origin/main", "HEAD") or ["HEAD"])[0]
    paths = _git_lines(root, "diff", "--name-only", base) + _git_lines(root, "ls-files", "--others", "--exclude-standard")
    for f in (p for p in paths if is_engine(p)):
        if not f.endswith(".py"):
            return True
        before = subprocess.run(["git", "-C", str(root), "show", f"{base}:{f}"], capture_output=True)
        now = root / f
        if before.returncode != 0 or not now.is_file():  # ...added or deleted
            return True
        if content_id(before.stdout, f) != content_id(now.read_bytes(), f):
            return True
    return False


def target(root: Path) -> Path | None:
    """The feature a carried finding is filed into: the claims feature (`CLAIMS_FEATURE`) for a delta with no engine code, while
    it has an open task; the feature being landed otherwise."""
    if not touches_engine(root):
        claims = _plan_gate().resolve(CLAIMS_FEATURE, root)
        if claims is not None and open_ids(claims):  # ...a closed claims feature takes nothing: the landing's own, as before
            return claims
    return active_feature(root)


def rows(d: Path) -> list[dict[str, Any]]:
    f = d / RECORD
    lines = f.read_text(encoding="utf-8").splitlines() if f.is_file() else []
    return [json.loads(ln) for ln in lines if ln.strip()]


def open_ids(d: Path) -> set[str]:
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8") if tasks.is_file() else ""
    return {m.group(2) for m in _BOX.finditer(text) if m.group(1) == " "}


def carried_ids(d: Path) -> set[str]:
    """The task ids the record names - the boxes the tooling put there, which the open-task refusal honors."""
    return {str(r.get("task")) for r in rows(d)}


def filed(root: Path) -> dict[str, str]:
    """key -> its open task, for every key the record of the feature carries file into (`target`) files (none with none)."""
    d = target(root)
    if d is None:
        return {}
    live = open_ids(d)
    return {k: str(r["task"]) for r in rows(d) if r.get("task") in live for k in r.get("keys") or []}


def _ruled(d: Path, ruling: str) -> bool:
    """Is `ruling` a `trigger` the feature's round-arbiter record holds (`arbiter.jsonl`)?"""
    f = d / "arbiter.jsonl"
    for ln in f.read_text(encoding="utf-8").splitlines() if f.is_file() else []:
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("trigger") == ruling:
            return True
    return False


def _file_into(text: str, task: str, keys: list[str], by: str = "the claims gate (385 FR-013)") -> str:
    """`text` (a tasks.md) with `keys` appended to open box `task`'s line, before its closing `[lands-open]`."""
    for m in _BOX.finditer(text):
        if m.group(2) != task:
            continue
        if m.group(1) != " ":
            raise ValueError(f"{task} is ticked; file into an open task, or leave T= off for a new one")
        line = m.group(0)
        tail = _LANDS_OPEN if line.endswith(_LANDS_OPEN) else ""
        body = line[: len(line) - len(tail)] if tail else line
        return text[: m.start()] + f"{body}; carried by {by}: {', '.join(keys)}{tail}" + text[m.end() :]
    raise ValueError(f"no task {task} in tasks.md")


def _new_box(text: str, keys: list[str], ruling: str = "") -> tuple[str, str]:
    """(`text` with a new open box for `keys`, the box's id): numbered after the highest task, before the GM-review box."""
    task = f"T{max((int(m.group(2)[1:]) for m in _BOX.finditer(text)), default=0) + 1:02d}"
    by = f"the round arbiter's ruling {ruling}: findings it carried" if ruling else "the claims gate (385 FR-013): findings on code the change left unchanged"
    box = f"- [ ] {task} Carried by {by} - fix the code or the claim and re-check each: {', '.join(keys)}{_LANDS_OPEN}\n      research: rendering\n"
    gm = re.search(r"^- \[[ x]\] GM review\b", text, re.M)
    if gm:
        return text[: gm.start()] + box + text[gm.start() :], task
    return text.rstrip("\n") + "\n" + box, task


def carry(root: Path, feature: str, task: str, keys: list[str], now: str | None = None, ruling: str = "") -> str:
    """File `keys` into the feature being landed (D27); returns what was done. Raises ValueError naming what to do instead.

    `ruling` (feature 385 T45, D59): `keys` are findings the gate counts as introduced, which that round-arbiter ruling carried;
    it must be a `trigger` in the feature's `arbiter.jsonl`, and the record's row names it. The box and its row are written
    together, so `holding` honors the box by its id - never a box that merely cites a trigger."""
    d = _plan_gate().resolve(feature, root)
    here, active = target(root), active_feature(root)
    if d is not None and here is not None and active is not None and d.resolve() == active.resolve():
        d = here  # ...the feature being landed names itself (`make land` does); a delta with no engine code files into 405
    if d is None or here is None or d.resolve() != here.resolve():
        where = "the claims feature's - this delta holds no engine code" if here is not None and active is not None and here.resolve() != active.resolve() else "the active task's"
        raise ValueError(f"a carried finding is filed only into {where} ({here.name if here else 'none: `make task-start F=<n> T=<Txx>` first'}), not {feature}")
    if ruling and not _ruled(d, ruling):
        raise ValueError(f"RULING={ruling} is no trigger in {d.name}/arbiter.jsonl - name the round arbiter's recorded ruling that carried these findings")
    if not keys:
        return "claims-carry: no carried finding is unfiled"
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8")
    by = f"the round arbiter's ruling {ruling}" if ruling else "the claims gate (385 FR-013)"
    if task:
        text = _file_into(text, task, keys, by)
    else:
        text, task = _new_box(text, keys, ruling)
    tasks.write_text(text, encoding="utf-8")
    row: dict[str, Any] = {"task": task, "keys": keys, "utc": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    if ruling:
        row["ruling"] = ruling
    with (d / RECORD).open("a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    return f"claims-carry: {len(keys)} finding(s) filed into {d.name} {task}; commit tasks.md and {RECORD} with the landing"


def gate(cx: Any, root: Path) -> tuple[list[str], list[str]]:  # noqa: ANN401 - `cx` is the claims module, passed to avoid a cycle
    """(refusals, warnings) for the push: owed units, introduced findings and carried ones not yet filed (FR-013, D28);
    pre-existing and filed carried findings warn."""
    refuse, intro, pre, carried = classified(cx, root)
    # ...A KNOWN DRIFT IS NO INTRODUCED FINDING (feature 417, the round arbiter's ruling on ask:417-T29-drifted): a DRIFTED claim
    # whose code the landing left as the base had it, and whose own text names an open task row that names it, is drift a
    # relabel revealed, not drift the landing made - it warns, and the fixing task carries it
    known = known_drifts(cx, root)
    intro, revealed = [x for x in intro if _key_of(x) not in known], [x for x in intro if _key_of(x) in known]
    # ...ADMITTED ONCE RECORDED FOR THE GM (feature 430 T06, D6): a known drift on its open task lands as a row of that feature's
    # gm-review.jsonl, which `make gm-review` lists; unrecorded, it refuses with the command that records it (make land runs it)
    done_known = recorded_known(root)
    unrecorded = [x for x in revealed if known[_key_of(x)] != "accepted by the round arbiter" and _key_of(x) not in done_known]
    pre = pre + [f"known drift ({known[_key_of(x)]}): {x}" for x in revealed if x not in unrecorded]
    done = filed(root)
    d = target(root)
    how = f"`make claims-carry F={d.name.split('-', 1)[0]}`" if d is not None else "`make task-start F=<n> T=<Txx>`, then `make claims-carry F=<n>`"
    unfiled = [f"carry: {line} - a finding on code the change left unchanged: file it with {how} (make land files it itself)" for k, line in carried if k not in done]
    warn = [f"carried ({d.name if d else ''} {done[k]}): {line}" for k, line in carried if k in done]
    unknown = [f"known: {x} - a known drift ({known[_key_of(x)]}) to record for the GM: `make claims-known` (make land runs it)" for x in unrecorded]
    return refuse + [f"introduced: {x}" for x in intro] + unfiled + unknown, [f"pre-existing: {x}" for x in pre] + warn


#: the kind of a gm-review.jsonl row that records an admitted known drift (feature 430 D6)
KNOWN_KIND = "known-drift"


def recorded_known(root: Path) -> set[str]:
    """Every claim key a feature's `gm-review.jsonl` records as an admitted known drift."""
    out: set[str] = set()
    for f in sorted((root / "specs").glob("*/gm-review.jsonl")):
        for ln in f.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(ln)
            except ValueError:
                continue
            if r.get("kind") == KNOWN_KIND and r.get("claim"):
                out.add(str(r["claim"]))
    return out


def record_known(cx: Any, root: Path, now: str | None = None) -> list[str]:  # noqa: ANN401 - `cx` is the claims module
    """`make claims-known`: each known drift the gate would refuse unrecorded, written as a row of its own task's feature's
    `gm-review.jsonl` (the GM's review box added with it); returns the lines written."""
    refuse, _warn = gate(cx, root)
    written: list[str] = []
    for line in refuse:
        m = re.match(r"known: (.*) - a known drift \((\d{3}) (T\d+[a-z]?)\) to record", line)
        if not m:
            continue
        key, feat, task = _key_of(m.group(1)), m.group(2), m.group(3)
        specs = sorted((root / "specs").glob(f"{feat}-*"))
        if not specs:
            continue
        row = {"kind": KNOWN_KIND, "claim": key, "task": task, "finding": m.group(1).strip()[:400],
               "utc": now or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with (specs[0] / "gm-review.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        _gm_review().ensure_box(specs[0])
        written.append(f"{specs[0].name} {task}: {key}")
    return written


def _gm_review() -> Any:  # noqa: ANN401 - the module, loaded by path
    import importlib.util  # noqa: PLC0415

    spec = importlib.util.spec_from_file_location("gm_review", Path(__file__).resolve().parents[1] / "gm_review.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


_TASK_NAMED = re.compile(r"feature (\d{3}) (T\d+)")
#: The words `claims_accept.accept_line` records when the round arbiter accepts a known drift.
ACCEPTED = "a known drift accepted by the round arbiter"


def _key_of(line: str) -> str:
    """The claim key a classified line (`f"{verdict:<14} {key} - {note}"`) names."""
    return line[14:].strip().split(" - ", 1)[0].strip()


def known_drifts(cx: Any, root: Path) -> dict[str, str]:  # noqa: ANN401 - `cx` is the claims module
    """key -> `<feature> <task>` for every DRIFTED claim whose own text names an OPEN task row of that feature's tasks.md which
    names the claim's unit - a departure the feature filed for fixing, whether or not the landing changed its code (feature 430
    D6) - and every DRIFTED claim the round arbiter accepted."""
    cur = cx.current(root)
    index = cx.load_index(root / cx.INDEX)
    cand: dict[str, tuple[str, str]] = {}
    for key, v in index.items():
        row = cur.get(key)
        # ...the LAST task the text names: "a departure the code keeps until feature NNN Tnn" closes the claim, and a task named
        # earlier says why the code is so (feature 417 T50: "the track lays no spur (feature 417 T50) ... until feature 417 T32")
        found = _TASK_NAMED.findall(row.claim.account) if row is not None and v.get("verdict") == "DRIFTED" else []
        if found:
            cand[key] = found[-1]
    # ...and a DRIFTED claim the round arbiter ACCEPTED is known on that accept alone, its own text naming no task: the ruling is
    # the binding answer, and a claim reworded to name its task owes another round its ruling closed (feature 417 T38: ask:417-T38-compound-drifts
    # accepted eleven, and two whose text named no task stayed introduced)
    out: dict[str, str] = {
        key: "accepted by the round arbiter"
        for key, v in index.items()
        if key not in cand and cur.get(key) is not None and v.get("verdict") == "DRIFTED" and ACCEPTED in v.get("note", "")
    }
    if not cand:
        return out
    rows: dict[tuple[str, str], str] = {}
    for key, (feat, task) in cand.items():
        if (feat, task) not in rows:
            specs = sorted((root / "specs").glob(f"{feat}-*/tasks.md"))
            box = re.search(rf"^- \[ \] {task} .*$", specs[0].read_text(encoding="utf-8"), re.M) if specs else None
            rows[(feat, task)] = box.group(0) if box else ""
        uid = key.rsplit("#", 1)[0]
        name = uid.split("::", 1)[-1].rsplit(".", 1)[-1]
        # ...THE LANDING'S CHANGE TO ITS CODE OR NOT (feature 430 T06, D6 - proposal 6, approved by the GM 2026-10-26: a "known"
        # departure is one whose claim names the open task carrying the fix): the open row naming the unit is what makes the drift
        # known, and it lands recorded for the GM (`record_known`). Until then only unchanged code counted, and a landing that
        # touched the code asked the round arbiter to accept each one, a round per landing (feature 417 T45, T50)
        if rows[(feat, task)] and re.search(rf"(?<![\w.]){re.escape(name)}(?!\w)", rows[(feat, task)]):
            out[key] = f"{feat} {task}"
        elif ACCEPTED in index[key].get("note", ""):
            # ...and a claim whose named row does not name its unit is still known on the arbiter's accept, as one naming no task
            # is (feature 417 T50: ask:417-T50-claims accepted two, and the one whose text named T50 first stayed introduced)
            out[key] = "accepted by the round arbiter"
    return out


def classified(cx: Any, root: Path) -> tuple[list[str], list[str], list[str], list[tuple[str, str]]]:  # noqa: ANN401
    """(owed refusals, introduced, pre-existing, carried) at `root` against its merge base with origin/main."""
    cur = cx.current(root)
    index = cx.load_index(root / cx.INDEX)
    due = cx.owed(cur, index, root / "research" / "questions", cx.load_store(root / cx.STORE))
    mb = (cx._git(root, "merge-base", "HEAD", "origin/main") or cx._git(root, "rev-parse", "HEAD") or "").strip()
    base_index = json.loads(cx._git(root, "show", f"{mb}:{cx.INDEX}") or "{}") if mb else {}
    with tempfile.TemporaryDirectory() as tmp:
        bskill = cx.base_tree(root, mb, Path(tmp)) if mb else Path(tmp)
        cores = cx.base_cores(bskill, keep=root) if mb else {}
        answered = frozenset(k for k, v in index.items() if k in cur and cx.relabel_answered(v, cur[k], root))
        intro, pre, carried = cx.classify(
            cur, index, base_index, cores, bskill / "research" / "questions", cx.load_deferred(root / cx.DEFERRED), answered
        )
    return [f"owed ({why}): {key}" for key, why in due], intro, pre, carried
