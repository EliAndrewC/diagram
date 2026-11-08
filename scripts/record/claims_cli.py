"""`make claims-*`'s command handlers, split from `scripts/record/claims.py` at the 1,000-line bar (feature 444 T16, the rule of
constitution Principle X clause 13): the argument parser and each command's body; `claims.main` dispatches to them.

Research: the claims commands - NONE: tooling
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from pathlib import Path
from typing import Any

import claims as cx  # noqa: E402 - the reader they drive, each name reached through it as the handler runs (so a test's patch of `claims` reaches it); `claims.main` imports this module lazily


def _parser() -> argparse.ArgumentParser:
    """The command line (lifted out of `claims.main` by feature 370, the 100-statement cap)."""
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("owed")
    b = sub.add_parser("bundle")
    b.add_argument("--owed", action="store_true")
    b.add_argument("--module", default="")
    b.add_argument("--units", default="")
    b.add_argument("--out", default="")
    b.add_argument("--reason", default="")
    b.add_argument("--with", dest="context", default="", help="path::qualname,... shown as context, not judged")
    b.add_argument("--pages", default="", help="question files (NNNN-<id>[.drawing].html,...) added to the bundle")
    r = sub.add_parser("record")
    r.add_argument("--bundle", required=True)
    r.add_argument("--reply", required=True)
    sub.add_parser("triage-owed")
    tr = sub.add_parser("triage")
    tr.add_argument("--out", default="")
    td = sub.add_parser("triaged")
    td.add_argument("--bundle", required=True)
    td.add_argument("--reply", required=True)
    sub.add_parser("backfill")
    sub.add_parser("backfill-sections")
    sub.add_parser("rekey")
    sub.add_parser("refingerprint")
    rp = sub.add_parser("report")
    rp.add_argument("--all", action="store_true", help="list the DEFERRED findings too")
    sub.add_parser("gate")
    sub.add_parser("known")
    cc = sub.add_parser("carry")
    cc.add_argument("--feature", required=True)
    cc.add_argument("--task", default="")
    cc.add_argument("--keys", default="", help="findings a round-arbiter ruling carried, ';'-separated (with --ruling)")
    cc.add_argument("--ruling", default="", help="the arbiter.jsonl trigger that carried --keys")
    ac = sub.add_parser("accept")
    ac.add_argument("--keys", required=True, help="the claims a round-arbiter accept stands for, ';'-separated (a claim's label may hold a comma)")
    ac.add_argument("--trigger", required=True, help="the arbiter.jsonl trigger whose accept this records")
    cv = sub.add_parser("coverage")
    cv.add_argument("--path", default="", help="only units whose file path contains this")
    ap.add_argument("--root", default=".")
    return ap


def _carry_cmd(root: Path, args: argparse.Namespace) -> int:
    """`make claims-carry`: file the carried findings as an open task of the feature (folded out of `claims.main` at the cap, 405 T58)."""
    try:
        if bool(args.keys) != bool(args.ruling):
            raise ValueError("KEYS= and RULING= go together: the findings a round-arbiter ruling carried, and that ruling's trigger")
        keys = [k.strip() for k in args.keys.split(";") if k.strip()] if args.keys else [k for k, _ln in cx.claims_carry.classified(cx, root)[3] if k not in cx.claims_carry.filed(root)]
        print(cx.claims_carry.carry(root, args.feature, args.task, keys, ruling=args.ruling))
    except ValueError as e:
        print(f"claims-carry: {e}", file=sys.stderr)
        return 2
    return 0


#: a triage bundle of this many claims or fewer is not triaged: impl-drift reads them directly (feature 430 T06, D6; proposal 6,
#: approved by the GM 2026-10-26: "skip claims-triage for bundles of a few claims"). CONVENTION - "a few" is the spec's knob,
#: set at 3: a triage round and an impl-drift round cost about the same on so few, and the triage would only route them on

#: where each skipped triage is recorded (feature 430 D6)


def _small_triage(root: Path, keys: list[str], out: str) -> int:
    """A triage too small to be worth one (`claims.TRIAGE_SKIP_MAX`): the impl-drift bundle of the same claims, and the skip on the ledger."""
    why = f"a claims triage of {len(keys)} claim(s), at most {cx.TRIAGE_SKIP_MAX}, goes straight to impl-drift (feature 430 D6)"
    rc = cx.main(["--root", str(root), "bundle", "--units", ",".join(keys), "--reason", why, *(["--out", out] if out else [])])
    if rc == 0:
        # ...RECORDED IN ITS OWN FILE, not as a row of the review ledger's measured table: a skip has no check, class or cost of
        # its own, and the ledger's guard (`ledger_hooks.rs`) refused the first form's row at the next commit (2026-10-26)
        row = {"date": datetime.date.today().isoformat(), "claims": len(keys), "keys": keys, "why": why}
        with (root / cx.SKIPS).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
        print(f"claims-triage: {why} - dispatch `impl-drift` on the MANIFEST above, then `make claims-checked BUNDLE=<dir> REPLY=<file>`; the skip is in {cx.SKIPS}")
    return rc


def _refingerprint_cmd(root: Path, index: dict[str, dict[str, Any]]) -> int:
    """`make claims-refingerprint`: every claim's fingerprint read with and without the star re-exports, its row carried."""
    cl = cx.engine(Path(__file__).resolve().parents[2])

    def codes(stars: bool) -> dict[str, tuple[str, str]]:
        cl.STAR_REEXPORTS = stars
        try:
            return {u.key(c): (u.code(c), u.core) for u, _e in cl.all_units(root) for c in u.claims}
        finally:
            cl.STAR_REEXPORTS = True

    n = cx.refingerprint(index, codes(False), codes(True))
    if n:
        cx.save_index(root / cx.INDEX, index)
    print(f"claims-refingerprint: {n} claim row(s) carried to the fingerprint the star re-exports give, their code otherwise unchanged")
    return 0


def _rekey_cmd(root: Path, cur: dict[str, cx.Row], index: dict[str, dict[str, Any]]) -> int:
    """`make claims-rekey` (405 T58): each moved claim's row carried to its new key."""
    n = cx.rekey(cur, index)
    if n:
        cx.save_index(root / cx.INDEX, index)
    print(f"claims-rekey: {n} claim row(s) carried to the file their unit moved to")
    return 0


def _triage_cmd(args: argparse.Namespace, root: Path, cur: dict[str, cx.Row], index: dict[str, dict[str, Any]], qdir: Path, store: dict[str, Any]) -> int:
    """`claims-triage`: clear the claims a page move alone owes (feature 432), then triage the rest of what a triage owes."""
    due = cx.owed(cur, index, qdir, store)
    # ...a page moved and no block the claim rests on did: cleared, not triaged (feature 432, FR-005 a). A row with no `rests`
    # may rest on any block of the page, so it keeps the triage (the plan review's note on D7)
    pages = [k for k, why in due if why == "triage" and (index.get(k) or {}).get("rests")]
    if pages:
        index, snaps = cx.claims_triage.clear_page_moves(cur, index, pages, qdir, datetime.date.today().isoformat())
        cx.save_index(root / cx.INDEX, cx.live_rows(cur, index))
        cx.save_store(root / cx.STORE, {**store, **snaps})
        print(f"claims-triage: {len(pages)} claim(s) cleared without a triage - a page each cites moved and no block it rests on did (feature 432, FR-005 a)")
    keys = [k for k, why in due if why in cx.TRIAGED and k not in pages]
    if not keys:
        print("claims-triage: no claim is owed a triage")
        return 0
    if len(keys) <= cx.TRIAGE_SKIP_MAX:
        return _small_triage(root, keys, args.out)
    tout = Path(args.out) if args.out else cx.DEFAULT_OUT / "claims-triage"
    manifest = cx.triage_bundle(cur, index, store, keys, qdir, tout)
    data = json.loads((tout / "triage.json").read_text(encoding="utf-8"))
    if set(data["forced"]) >= set(keys):
        # ...EVERY CLAIM OWED IN FULL, NOTHING TO TRIAGE (feature 417 T54, 2026-10-27): a code move left no diff to show, and the
        # triage agent dispatched on the empty bundle could only say so, its reply then refused as empty - recorded here instead
        new, msgs = cx.record_triage(index, data["units"], "", datetime.date.today().isoformat(), data["forced"])
        cx.save_index(root / cx.INDEX, cx.live_rows(cur, new))
        cx.save_store(root / cx.STORE, {**store, **data["snapshots"]})
        cx.keep_texts(qdir, data["units"])
        print(
            f"claims-triage: all {len(keys)} claim(s) are cx.owed in full (no diff or removed block to show) - no triage to dispatch; "
            "they go straight to impl-drift: `make claims-bundle OWED=1`, then `make claims-checked BUNDLE=<dir> REPLY=<file>`"
        )
        return 0
    print(manifest)
    cx.claims_flight.mark(root, tout)  # in flight until `claims-triaged` records its reply (feature 426 D1)
    print(
        f"claims-triage: {len(keys)} claim(s); dispatch the `claims-triage` agent on the MANIFEST (a session started before 2026-10-17's amendment 6 landed: restart to load it), save its reply, then `make claims-triaged BUNDLE=<dir> REPLY=<file>`"
    )
    return 0


def _triaged_cmd(args: argparse.Namespace, root: Path, cur: dict[str, cx.Row], index: dict[str, dict[str, Any]], qdir: Path, store: dict[str, Any]) -> int:
    """`claims-triaged`: record a triage reply - the claims it names go on to impl-drift, the rest are cleared."""
    data = json.loads((Path(args.bundle) / "triage.json").read_text(encoding="utf-8"))
    if not (reply := cx.claims_triage.read_reply(args.reply, "claims-triaged", "nothing cleared")).strip():  # feature 385 T92
        return 2
    new, msgs = cx.record_triage(
        index,
        data["units"],
        reply,
        datetime.date.today().isoformat(),
        data.get("forced", []),
    )
    cx.save_index(root / cx.INDEX, cx.live_rows(cur, new))
    cx.save_store(root / cx.STORE, {**store, **data["snapshots"]})
    cx.keep_texts(qdir, data["units"])
    for m in msgs:
        print(f"claims-triaged: {m}")
    named = sum(1 for m in msgs if m.startswith("touched") and " - a removed block the history no longer shows" not in m)
    forced = sum(1 for m in msgs if m.startswith("touched")) - named
    print(
        f"claims-triaged: {named + forced} of {len(data['units'])} sent on to impl-drift ({named} named by the reply"
        + (f", {forced} cx.owed in full: a removed block's words could not be shown" if forced else "")
        + "); the rest cleared"
    )
    cx.claims_flight.clear(root, Path(args.bundle))  # its reply is recorded (feature 426 D1)
    return 0
