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


def accept(root: Path, cur: dict[str, Any], index: dict[str, dict[str, Any]], args: argparse.Namespace) -> int:
    """`claims.py accept`: a round-arbiter ACCEPT asked with `REVIEW=claims:<keys>` stands as those claims' verdict, recorded
    at the code and research they have now - a later edit owes them again, as any verdict (the GM 2026-10-24: T26's landing
    met the claims gate on a claim the arbiter had accepted with no third round, and needed CLAIMS_OK at the landing and again
    at the stop-work push)."""
    keys = [k.strip() for k in args.keys.split(";") if k.strip()]
    missing = [k for k in keys if k not in cur]
    if missing or not keys:
        print(f"claims-accept: no such claim: {', '.join(missing) or '(none named)'}", file=sys.stderr)
        return 2
    with tempfile.TemporaryDirectory() as tmp:
        claims.bundle(root, cur, keys, Path(tmp))
        units = json.loads((Path(tmp) / "units.json").read_text(encoding="utf-8"))
    reply = "\n".join(f"VERDICT {k} IN-STEP - accepted by the round arbiter ({args.trigger}), binding; the GM reviews it" for k in keys)
    new, msgs = claims.record(index, units, reply, datetime.date.today().isoformat())
    claims.save_index(root / claims.INDEX, claims.live_rows(cur, new))
    for m in msgs:
        print(f"claims-accept: {m}")
    print(f"claims-accept: {len(keys)} claim(s) recorded IN-STEP on {args.trigger}'s accept")
    return 0
