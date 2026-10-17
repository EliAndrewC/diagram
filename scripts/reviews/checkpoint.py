#!/usr/bin/env python3
"""The feature's hourly checkpoint: the step-back and every owed review, together (feature 383, plan D10-D13).

WHY (the GM 2026-10-12: *"for longer running features, we will have a set of checks that we do, which previously was only the
glyph check ... but now will be the glyph check and also this sanity check or stepping back and looking at the problem from
above check"*). The glyph clock (feature 375 amendments 9 and 10, `review_owed.py`) becomes the feature's checkpoint. An hour
after the feature's start in this clone - its first event, or its most recent reopening - or after its last checkpoint,
everything the checkpoint owes comes due at once:

- a STEP-BACK review of the hour: the round arbiter on an `hour:<feature>@<n>` trigger (`make step-back` opens it and builds its
  bundle, `stepback_bundle.py`), asked whether the session is going in circles, packing against an unresearched number, held
  up by a slow step or a misfiring guard, or facing something for the GM;
- and every review unit then owed (`review_owed.all_owed`: the glyph units and, since FR-003, the others).

HELD, NOT OPTIONAL (FR-011): while the checkpoint is due, `make tick` refuses (`hold`) until the hour's ruling is recorded and
every unit it owed has been dispatched since it opened. There is no escape: the session in a loop is the one the step-back is
for, and the 379 tooling-fix hold beside it has none either. A feature under an hour, or with no event log, owes nothing.

The clock is the glyph clock's file (`<git dir>/glyph-clock.json`), under the feature: `checkpoint_at` (when the last
checkpoint's ruling closed it), `checkpoints` (how many), `checkpoint_open_at` and `checkpoint_trigger` (one opened by
`make step-back`, not yet ruled), `checkpoint_units` and `units_since` (what it owed, dispatched since when).

    checkpoint.py open [--root <clone>]       open the hour's checkpoint: print its trigger (make step-back)
    checkpoint.py hold [--root <clone>]       exit 1 printing the refusal while the checkpoint holds `make tick`
    checkpoint.py status [--root <clone>]     where the clock stands
    checkpoint.py due --tool <T> [--agent <A>] [--root <clone>]   exit 1 printing the refusal a make done or a dispatch gets past the hour
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "hooks" / "lib"))
import review_owed as ro  # noqa: E402

#: an hour of the feature's time - the glyph hour (the GM: "every feature which takes longer than 1 hour to implement")
CHECKPOINT_S = ro.GLYPH_HOUR_S


def _clock(root: Path) -> tuple[Path | None, dict]:
    g = ro._gitdir(root)  # noqa: SLF001 - the glyph clock's own reader
    return (g / ro.CLOCK if g is not None else None), (ro._read_json(g / ro.CLOCK) if g is not None else {})  # noqa: SLF001


def _write(path: Path | None, clock: dict) -> None:
    if path is not None:
        path.write_text(json.dumps(clock, indent=1) + "\n", encoding="utf-8")


def gm_waits(root: Path, feature: str, since: float, now: float) -> float:
    """Seconds between `since` and `now` the session spent waiting on the GM: each gap from a Stop to the GM's next prompt (an
    event marked `"gm": true` - a notification is not the GM's), clipped to the window. The round arbiter's tooling fix on
    hour:385-approach-checklist@4 (feature 385): an hour 34 of whose 63 minutes were waits, mostly on the GM, opened a step-back
    of an hour the session had not spent. An event with no `gm` mark (logged before the mark existed) counts as the session's."""
    from datetime import datetime  # noqa: PLC0415

    g = ro._gitdir(root)  # noqa: SLF001 - the glyph clock's own reader
    path = g / "l7r-events" / f"{feature}.jsonl" if g is not None else None
    if path is None or not path.is_file():
        return 0.0
    waited, stop = 0.0, None
    for raw in path.read_text(encoding="utf-8").splitlines():
        try:
            e = json.loads(raw)
            t = datetime.fromisoformat(str(e["t"]).replace("Z", "+00:00")).timestamp()
        except (ValueError, KeyError, TypeError):
            continue
        if e.get("ev") == "Stop":
            stop = t if stop is None else stop
        elif e.get("ev") == "UserPromptSubmit" and stop is not None:
            if e.get("gm") is True:
                waited += max(0.0, min(t, now) - max(stop, since))
            stop = None
        elif e.get("ev") in ("PreToolUse", "SubagentStop"):
            stop = None
    return waited


def state(root: Path, now: float | None = None) -> dict:
    """{feature, due, since, hour, open: trigger or "", units, units_since}; `due` False with no feature or no event log."""
    now = time.time() if now is None else now
    feature = ro.active_feature(root)
    start = ro.feature_start(root, feature) if feature else None
    if start is None:
        return {"feature": feature, "due": False}
    mine = _clock(root)[1].get(feature) or {}
    since = max(start, float(mine.get("checkpoint_at") or 0))
    return {"feature": feature, "due": now - since - gm_waits(root, feature, since, now) >= CHECKPOINT_S, "since": since, "hour": int(mine.get("checkpoints") or 0) + 1,
            "open": str(mine.get("checkpoint_trigger") or ""), "units": list(mine.get("checkpoint_units") or []),
            "units_since": float(mine.get("units_since") or 0)}


def open_checkpoint(root: Path, now: float | None = None) -> str:
    """`make step-back`: the hour's trigger, opened once - its time and the units owed at that moment kept with it. Refused
    (ValueError) before the hour is up."""
    now = time.time() if now is None else now
    st = state(root, now)
    if st.get("open"):
        return st["open"]
    if not st.get("due"):
        # the minutes alone read as "now" for the minute before it: say how long is left too
        when = (time.strftime("%H:%M:%S", time.localtime(st["since"] + CHECKPOINT_S)) + f", in {int(st['since'] + CHECKPOINT_S - now)} s"
                if "since" in st else "never (no feature or event log)")
        raise ValueError(f"the checkpoint is not due - the feature's next hour is up at {when}")
    trigger = f"hour:{st['feature']}@{st['hour']}"
    path, clock = _clock(root)
    units = [u.slug for u in ro.all_owed(root)[1]]
    clock.setdefault(st["feature"], {}).update({"checkpoint_open_at": int(now), "checkpoint_trigger": trigger,
                                                "checkpoint_units": units, "units_since": int(now)})
    _write(path, clock)
    import hm_arbiter  # noqa: PLC0415 - the trigger the round arbiter rules on, recorded as every trigger is

    hm_arbiter.trip(root, trigger, "hour", "", f"the feature's hourly step-back, hour {st['hour']}", now)
    return trigger


def close_checkpoint(root: Path, trigger: str) -> None:
    """The hour's ruling is recorded (`hm_arbiter.record_ruling`): the clock restarts from when the checkpoint opened."""
    path, clock = _clock(root)
    for mine in clock.values():
        if isinstance(mine, dict) and mine.get("checkpoint_trigger") == trigger:
            mine["checkpoint_at"] = mine.pop("checkpoint_open_at", int(time.time()))
            mine["checkpoints"] = int(mine.get("checkpoints") or 0) + 1
            mine.pop("checkpoint_trigger", None)
    _write(path, clock)


def current_key(root: Path) -> str:
    """The engine key of the clone's working tree (`make -s engine-key REF=worktree`), '' where it cannot be had."""
    import subprocess

    out = subprocess.run(["make", "-s", "engine-key", "REF=worktree"], cwd=root, capture_output=True, text=True, check=False)
    return out.stdout.strip() if out.returncode == 0 else ""


def answered(root: Path, slug: str, key: str) -> bool:
    """Does the unit's verdict record answer it at `key` - PASS or NEEDS-WORK recorded at the engine key the tree has now? A
    check answered before the checkpoint opened is owed no dispatch: feature 374 wave 151's two glyph checks passed at the
    current key minutes before the step-back, and the tick was held for them as undispatched."""
    rec = ro._read_json((ro._gitdir(root) or Path("/nonexistent")) / "review-verdicts" / f"{slug}.json")  # noqa: SLF001
    return bool(key) and rec.get("verdict") in ("PASS", "NEEDS-WORK") and str(rec.get("engine_key") or "") == key


def _undispatched(root: Path, units: list[str], since: float) -> list[str]:
    """The checkpoint's units still owed, not dispatched since it opened (the pair guard's `dispatched[<slug>].at`) and not
    answered at the tree's engine key (`answered`)."""
    if not units:
        return []
    owed_now = {u.slug for u in ro.all_owed(root)[1]}
    disp = ro._read_json((ro._gitdir(root) or Path("/nonexistent")) / ro.PAIRING).get("dispatched") or {}  # noqa: SLF001
    at = lambda s: float((disp.get(s) or {}).get("at") or 0) if isinstance(disp.get(s), dict) else 0.0  # noqa: E731
    left = [s for s in units if s in owed_now and at(s) < since]
    if not left:
        return []
    key = current_key(root)
    return [s for s in left if not answered(root, s, key)]


def hold(root: Path, now: float | None = None) -> str:
    """The refusal `make tick` prints while the checkpoint holds it, or ""."""
    st = state(root, now)
    if not st.get("feature") or "since" not in st:
        return ""
    if st["open"]:
        return (f"the feature's hourly checkpoint is open ({st['open']}) and owes the round arbiter's ruling: dispatch "
                f"`round-arbiter` on the bundle `make step-back` built (/tmp/l7r-check/step-back-{st['open'].split(':', 1)[1].replace('@', '-')}/MANIFEST.md); "
                "it records the ruling with make arbiter-ruled (feature 383)")
    if st["due"]:
        return ("the feature has run an hour since its last checkpoint: run `make step-back` (the round arbiter steps back over "
                "the hour) and dispatch the review checks owed now (`make verify` writes one prompt per unit) - feature 383")
    left = _undispatched(root, st["units"], st["units_since"])
    if left:
        return (f"the last checkpoint owed {len(left)} review unit(s) not yet dispatched: {', '.join(left)} - `make verify` writes "
                "one prompt per unit; dispatch each on a green gate (feature 383)")
    return ""


def due(root: Path, tool: str, atype: str = "", now: float | None = None) -> str:
    """The refusal a `make done` or an agent dispatch gets when the feature's hour is up and its step-back is not yet open,
    or "". THE STEP-BACK FIRES ON THE HOUR, NOT ONLY AT THE TICK (the round arbiter's tooling fix on hour:374@2: the hour ran
    216 minutes because batch 17 did not tick until its landing, so the step-back reviewed three hours as one). The round
    arbiter's own dispatch passes - it is the step-back."""
    if tool == "Agent" and atype == "round-arbiter":
        return ""
    st = state(root, now)
    if not st.get("due") or st.get("open"):
        return ""
    return ("the feature's hour is up and its step-back is not open: run `make step-back` and dispatch `round-arbiter` on the "
            "bundle it builds, then carry on (feature 383; the round arbiter's tooling fix on hour:374@2)")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("verb", choices=("open", "hold", "status", "due"))
    ap.add_argument("--root", default=".")
    ap.add_argument("--tool", default="")
    ap.add_argument("--agent", default="")
    args = ap.parse_args(argv)
    root = Path(ro._git(Path(args.root), "rev-parse", "--show-toplevel") or args.root)  # noqa: SLF001
    if args.verb == "open":
        try:
            print(open_checkpoint(root))
        except ValueError as e:
            print(f"step-back: {e}", file=sys.stderr)
            return 1
        return 0
    if args.verb == "due":
        why = due(root, args.tool, args.agent)
        if why:
            print(why)
            return 1
        return 0
    if args.verb == "hold":
        why = hold(root)
        if why:
            print(why)
            return 1
        return 0
    print(json.dumps(state(root), indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
