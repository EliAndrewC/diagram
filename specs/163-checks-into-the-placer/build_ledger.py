#!/usr/bin/env python3
"""T14/T15 - build the measurement ledger the GM's case-by-case discussion runs on.

    python3 specs/163-checks-into-the-placer/build_ledger.py

This JOINS two measurements that already exist rather than taking a third:

  - `make check-census` (feature 141) - per check, the manifest keys it reads, the stage each key is
    PLACED at and the stage its content LAST CHANGES, who besides the gate reads the verdict, and
    which frozen fixtures pin it.
  - `make firing-census` (feature 163) - per check, what class of artifact can still make it FAIL.

FR-009 as the spec review left it: **record the measurement and state the evidence for the GM's own two
readings; assign nothing.** The GM named two outcomes for a check the audit catches - *"which of them
represent bugs in our placement algorithm and which need to be folded into a trial-and-error version of
our placement algorithm"* - and the round-3 review was explicit that sorting the checks into categories
before the discussion IS deciding. So every row here carries facts and a POINTER to which reading the
facts support, and no row carries a verdict.

A one-shot for this feature, in this feature's directory, on the precedent of feature 141's own tooling.
Not under the coverage rule; nothing imports it.
"""

from __future__ import annotations

import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SKILL = os.path.abspath(os.path.join(HERE, "..", "..", ".claude", "skills", "diagram"))

# The GM's two readings, plus the honest third the spec review required us to allow.
BUG = "placer bug"  # the check catches something a correct placer would not have produced
FOLD = "fold into a trial-and-error placer"  # no single placer CAN guarantee it; it is an accept condition
NEITHER = "neither"  # the measurement supports neither reading - recorded as an observation


def load(path: str) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def reading_for(row: dict, fires: dict) -> tuple[str, str]:
    """(which reading the measurement points at, the fact that points there). NOT a verdict.

    The discriminator is the one the GM already established in feature 141 and the one this whole
    re-architecture turns on: **can any stage after the placer change what this check reads?**

      no  -> nothing between the placer and the gate can move it, so a failure means the placer
             produced it wrong: the GM's `placer bug` reading, and the disposition is a unit test
             of the placer rather than a per-map audit.
      yes -> the placer only did its best and a later stage undid it. No unit test of the placer can
             carry that guarantee, so it is an ACCEPT CONDITION: the GM's `fold` reading, with
             `farmhouses_reach_a_way` in hamletgen/driver.py as the worked precedent.
    """
    stages = row.get("stages") or {}
    verdict = row.get("verdict")
    readers = row.get("readers") or []
    fired = fires.get(row.get("check"), {}).get("verdict")

    # THE TWO CENSUSES ARBITRATE EACH OTHER, and neither is sufficient alone.
    # `check-census` reads the MANIFEST, so "every input is absent on both scripted maps" is what a
    # VACUOUS check looks like AND what a PASSING one looks like: `all_ink_is_ruled_on`'s inputs
    # (`unclassed_ink`, `unregistered_classes`) are empty precisely because the map is correct. The
    # firing census settles it - if something can still make the check FAIL, it is not vacuous.
    if verdict == "VACUOUS-ON-SCRIPTED" and fired != "NEVER-FIRES":
        return FOLD, f"check-census reads its inputs as absent on both scripted maps, but the firing census has it FIRING ({fired}) - the inputs are empty because a correct map has nothing to report, which is what PASSING looks like"
    if verdict == "VACUOUS-ON-SCRIPTED":
        return NEITHER, "inputs absent on both scripted maps AND nothing makes it fire - the one row where both censuses agree it does nothing"
    if verdict == "NO-SCRIPTED-EXECUTOR":
        return NEITHER, "no scripted map runs it - a tier this engine cannot yet produce. Not a deletion candidate under the GM's 2026-08-30 ruling; a class for the discussion"
    # A READER IS A CONSUMER WHOSE BEHAVIOR BRANCHES ON THE VERDICT - and `readers` is not that field.
    # It also lists every test that names the check and every waiver that mentions it, tagged "(test)"
    # and "(waiver)"; `check_census`'s own docstring says so. Keying on the field NAME instead of its
    # CONTENTS put all eleven retire-candidates into `fold` and left `placer bug` at zero - the same
    # "two correct things, never compared" shape this feature has now hit four times in the engine.
    gen_readers = [r for r in readers if not r.endswith(("(test)", "(waiver)"))]
    if gen_readers:
        return FOLD, f"a generator ALREADY branches on this verdict: {', '.join(gen_readers)} - it is an accept condition today, not an audit"
    if not row.get("keys"):
        return NEITHER, "reads no manifest key the census can see (derived entirely) - judge by hand"
    if verdict == "RETIRE-CANDIDATE":  # 141's own name for "every input settles at the stage that placed it"
        return BUG, f"every input settles at the stage that placed it ({_stage_text(stages)}) - nothing after the placer can move it"
    return FOLD, f"an input changes after its placer ({_stage_text(stages)}) - the placer cannot guarantee the finished state"


def _stage_text(stages: dict) -> str:
    if not stages:
        return "no stage data"
    bits = []
    for m, v in sorted(stages.items()):
        if isinstance(v, (list, tuple)) and len(v) == 2:
            bits.append(f"{m}: placed {v[0]}, last changed {v[1]}")
        else:
            bits.append(f"{m}: {v}")
    return "; ".join(bits)


def build() -> str:
    census = load(os.path.join(HERE, "ledger.json")) if os.path.exists(os.path.join(HERE, "ledger.json")) else None
    if census is None:
        sys.exit("run `make check-census OUT=specs/163-checks-into-the-placer/ledger` first")
    firing = load(os.path.join(HERE, "firing-census.json"))
    fires = firing["rows"]
    rows = {r["check"]: r for r in census["rows"]}

    live = sorted(fires)
    groups: dict[str, list[tuple[str, str, dict]]] = {BUG: [], FOLD: [], NEITHER: []}
    for name in live:
        row = rows.get(name, {})
        reading, why = reading_for(row, fires)
        groups[reading].append((name, why, row))

    out = [
        "# T14/T15 - the measurement ledger, for the GM's case-by-case discussion",
        "",
        "**This ledger decides nothing.** Every row carries the measurement and the fact that points at one",
        "of the GM's two readings; the ruling is the GM's, check by check. Built by joining",
        "`make check-census` (which stage last changes each input) with `make firing-census` (what can still",
        "make it fail) - see `build_ledger.py`.",
        "",
        f"{len(live)} live checks. The discriminator is the one the GM set in feature 141: **can any stage",
        "after the placer change what this check reads?**",
        "",
        "| reading | n | what it means |",
        "|---|---|---|",
        f"| **{BUG}** | {len(groups[BUG])} | nothing after the placer can move its inputs, so a failure means the placer produced it wrong. Disposition: a unit test of the placer, not a per-map audit. |",
        f"| **{FOLD}** | {len(groups[FOLD])} | a later stage can undo the placer, so no unit test of the placer can carry the guarantee. Disposition: an accept condition inside the loop - `farmhouses_reach_a_way` is the worked precedent. |",
        f"| **{NEITHER}** | {len(groups[NEITHER])} | the measurement supports neither reading; recorded as an observation. |",
        "",
    ]
    for reading in (BUG, FOLD, NEITHER):
        out += [f"## {reading} ({len(groups[reading])})", "", "| check | still made to fail by | the measurement |", "|---|---|---|"]
        for name, why, _row in groups[reading]:
            ev = sorted({k for k, _s in fires[name]["evidence"]}) or ["nothing"]
            out.append(f"| `{name}` | {', '.join(f'`{e}`' for e in ev)} | {why} |")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    text = build()
    with open(os.path.join(HERE, "surviving-checks.md"), "w", encoding="utf-8") as fh:
        fh.write(text)
    print(f"wrote surviving-checks.md ({len(text.splitlines())} lines)")
