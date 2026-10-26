"""A claims check's REPLY, read and recorded: the verdict lines parsed, a reply's elided page names restored, and the index
rows it writes (`record`). Lifted out of `claims.py` at the 1,000-line bar (feature 426; the GM's rule of 405 T53: split, never
trim to just under); `claims` re-exports every name, so `claims.record` and the rest still resolve.

Research: claims plumbing - NONE
"""

from __future__ import annotations

import re
import sys
from collections.abc import Mapping
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


FINDINGS = ("DRIFTED", "NEEDS-RESEARCH", "MISLABELED", "UNCLAIMED", "CANNOT-TELL")

VERDICTS = ("IN-STEP", *FINDINGS)

# ...the verdict also read where a reply sets it off with a dash or closes it with a colon (`KEY - IN-STEP - note`, `KEY IN-STEP:
# note`): read strictly, the dash went into the key, every line was "not a claim of this bundle" and nothing was recorded (feature
# 417 T50, two impl-drift rounds)
_VERDICT = re.compile(r"^VERDICT\s+(\S.*?)\s+(?:-\s+)?(" + "|".join(VERDICTS) + r")(?:\s+-\s+|:\s+)(.*)$")

_UNCLAIMED = re.compile(r"^UNCLAIMED\s+(\S+?::\S.*?)\s+-\s+(.*)$")

OUTSIDE = "[outside the change]"

def outside_tag(note: str) -> tuple[bool, str]:
    """(did the check tag it outside the change, the note without the tag)."""
    s = note.strip()
    return (True, s[len(OUTSIDE) :].strip()) if s.startswith(OUTSIDE) else (False, note)

def parse_reply(text: str) -> tuple[dict[str, tuple[str, str]], list[tuple[str, str]]]:
    """({key: (verdict, note)}, [(uid, decision)]) from a check's reply."""
    sys.path.insert(0, str(HERE.parent / "hooks" / "lib"))
    from hm_house import americanize  # noqa: PLC0415 - feature 385 T78: a note's words in the house style, its key as written

    verdicts: dict[str, tuple[str, str]] = {}
    unclaimed: list[tuple[str, str]] = []
    for raw in text.split("\n"):
        line = raw.strip().strip("`")
        if m := _VERDICT.match(line):
            verdicts[m.group(1).strip("`")] = (m.group(2), americanize(m.group(3).strip()))
        elif m := _UNCLAIMED.match(line):
            unclaimed.append((m.group(1).strip("`"), americanize(m.group(2).strip())))
    return verdicts, unclaimed

_RESTS = re.compile(r"\[(§[^\]]*)\]\s*$")

_ELIDED = re.compile(r"\b(\d{4})-[\w-]*\.\.\.?[\w-]*?((?:\.drawing)?\.html)")

def unelide(reply: str, stems: list[str]) -> str:
    """The reply with each pointer a check wrote shortened (`0236-...-home-plot.drawing.html`) given its full file name, so a
    verdict note written into the index never fails `check-research-pointers.py` (feature 319: four did, and the index had to
    be hand-repaired). `stems` are the question stems (`0236-shrine-...`); a number with no question, or with more than one
    stem, is left as written for a person to see."""

    def full(m: re.Match[str]) -> str:
        hits = [s for s in stems if s.startswith(m.group(1) + "-")]
        return f"{hits[0]}{m.group(2)}" if len(hits) == 1 else m.group(0)

    return _ELIDED.sub(full, reply)

def rests_of(note: str, numbered: Mapping[str, str]) -> tuple[str, list[str] | None]:
    """A verdict note without its closing `[§3, §12]`, and the `page:digest` of each block it names (feature 318, FR-016): `[§]`
    is an empty list (the questions are silent on the claim), no tag at all None (either way any change on its pages is
    triaged); a number the bundle does not hold is dropped."""
    m = _RESTS.search(note)
    if not m:
        return note, None
    names = [x.strip() for x in m.group(1).split(",")]
    return note[: m.start()].rstrip(), sorted({numbered[n] for n in names if n in numbered})

def record(
    index: dict[str, dict[str, Any]],
    units: dict[str, dict[str, Any]],
    reply: str,
    today: str,
    numbered: Mapping[str, str] | None = None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """The index with a check's reply applied, and the messages for the session (spec FR-009). A key not in the bundle is
    refused; a bundle key the reply gives no verdict stays owed; an UNCLAIMED finding is a row of its own, and a unit's earlier
    UNCLAIMED rows are dropped when this check of its claims does not report them again. Each row keeps the pages it was checked
    at and the blocks its verdict rests on (feature 318, FR-016)."""
    verdicts, unclaimed = parse_reply(reply)
    msgs: list[str] = []
    out = dict(index)
    for key in sorted(set(verdicts) - set(units)):
        msgs.append(f"refused: `{key}` is not a unit of this bundle")
    uids_checked = {u["uid"] for u in units.values()}
    for key in [k for k, v in out.items() if v.get("verdict") == "UNCLAIMED" and k.rsplit("#", 1)[0] in uids_checked]:
        del out[key]
    for key, fp in sorted(units.items()):
        if key not in verdicts:
            msgs.append(f"no verdict for `{key}` - it stays owed")
            continue
        verdict, note = verdicts[key]
        outside, note = outside_tag(note)
        note, rests = rests_of(note, numbered or {})
        # ...ONLY ON ITS OWN PAGES (feature 328 wave 95): an agent re-sent a fresh bundle cited the section numbers of the bundle it
        # first read, and claims came to rest on blocks of pages they do not cite, so an edit to their own pages no longer
        # re-owed them. A foreign rest is dropped and named; with none of its own left the claim triages any change on its pages
        if rests and "pages" in fp:
            foreign = [r for r in rests if r.rsplit(":", 1)[0] not in fp["pages"]]
            if foreign:
                msgs.append(
                    f"`{key}`: rests on {', '.join(sorted({r.rsplit(':', 1)[0] for r in foreign}))}, a page it does not cite - dropped (was the reply judged against another bundle's numbering?)"
                )
                rests = [r for r in rests if r not in foreign] or None
        row: dict[str, Any] = {
            "verdict": verdict,
            "code": fp["code"],
            "core": fp["core"],
            **{f: fp[f] for f in ("body", "claim") if f in fp},
            "research": fp["research"],
            "date": today,
            "note": note,
        }
        if "pages" in fp:
            row["pages"] = fp["pages"]
        if "section" in fp:
            row["section"] = fp["section"]
        if rests is not None:
            row["rests"] = rests
        if outside and verdict in FINDINGS:
            row["outside"] = True
        out[key] = row
    cores = {u["uid"]: u["core"] for u in units.values()}
    for uid, said in unclaimed:
        if uid not in cores:
            msgs.append(f"refused: UNCLAIMED `{uid}` is not a unit of this bundle")
            continue
        outside, decision = outside_tag(said)
        out[f"{uid}#{decision}"] = {
            "verdict": "UNCLAIMED",
            "code": cores[uid],
            "core": cores[uid],
            "research": "",
            "date": today,
            "note": decision,
            **({"outside": True} if outside else {}),
        }
        msgs.append(f"UNCLAIMED {uid} - {decision}: write a claim for it, then check it")
    return out, msgs
