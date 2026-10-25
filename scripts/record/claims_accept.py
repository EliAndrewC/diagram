#!/usr/bin/env python3
"""`claims.py accept --keys <k,...> --trigger <ask:...>` - a round-arbiter accept stands as the named claims' verdict (the GM
2026-10-24). Split from `claims.py`, which stood at 990 lines (the 1,000-line bar); `make arbiter-ruled` runs it when an accept
answers an ask filed with `REVIEW=claims:<keys>`."""

from __future__ import annotations

import argparse
import datetime
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
import claims  # noqa: E402 - the module beside this one


def accept_line(key: str, was: dict[str, Any], trigger: str) -> str:
    """The VERDICT line an accept records for one claim. A KNOWN DRIFT STAYS DRIFTED (feature 417, the round arbiter's ruling on
    ask:417-T29-drifted): an accept that rewrote a DRIFTED claim IN-STEP hid the departure the claim states, and took it out of
    the list a fixing pass reads; every other verdict the accept stands in for is IN-STEP."""
    if was.get("verdict") == "DRIFTED":
        return f"VERDICT {key} DRIFTED - {was.get('note', '')}; a known drift accepted by the round arbiter ({trigger}) to land as filed"
    return f"VERDICT {key} IN-STEP - accepted by the round arbiter ({trigger}), binding; the GM reviews it"


def split_semicolon_keys(text: str, known: Any) -> list[str]:  # noqa: ANN401 - a mapping of claim keys
    """The claim keys a `;`-separated `text` names. A label may hold a `;` of its own (`("the well or basin"; the required item
    is `well`)`, feature 417 T36's accept), so the pieces are joined back into the LONGEST run that is a `known` key, as
    `claims.split_keys` does for commas; a piece no run makes known is returned alone, for the caller to name as unknown."""
    parts = text.split(";")
    keys: list[str] = []
    i = 0
    while i < len(parts):
        j = next((j for j in range(len(parts), i, -1) if ";".join(parts[i:j]).strip() in known), i + 1)
        key = ";".join(parts[i:j]).strip()
        if key:
            keys.append(key)
        i = j
    return keys


def accept(root: Path, cur: dict[str, Any], index: dict[str, dict[str, Any]], args: argparse.Namespace) -> int:
    """`claims.py accept`: a round-arbiter ACCEPT asked with `REVIEW=claims:<keys>` stands as those claims' verdict, recorded
    at the code and research they have now - a later edit owes them again, as any verdict (the GM 2026-10-24: T26's landing
    met the claims gate on a claim the arbiter had accepted with no third round, and needed CLAIMS_OK at the landing and again
    at the stop-work push)."""
    keys = split_semicolon_keys(args.keys, cur)
    missing = [k for k in keys if k not in cur]
    if missing or not keys:
        print(f"claims-accept: no such claim: {', '.join(missing) or '(none named)'}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        claims.bundle(root, cur, keys, Path(tmp))
        units = json.loads((Path(tmp) / "units.json").read_text(encoding="utf-8"))
    reply = "\n".join(accept_line(k, index.get(k) or {}, args.trigger) for k in keys)
    new, msgs = claims.record(index, units, reply, datetime.date.today().isoformat())
    claims.save_index(root / claims.INDEX, claims.live_rows(cur, new))
    for m in msgs:
        print(f"claims-accept: {m}")
    kept = sum(1 for k in keys if (index.get(k) or {}).get("verdict") == "DRIFTED")
    print(f"claims-accept: {len(keys) - kept} claim(s) recorded IN-STEP and {kept} kept DRIFTED (a known drift) on {args.trigger}'s accept")
    return 0
