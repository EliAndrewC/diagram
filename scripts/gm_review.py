#!/usr/bin/env python3
"""The GM's review after landing - `make gm-review`, `make gm-reviewed`, `make accept` (feature 375, FR-012, plan D12).

WHY (the GM, 2026-10-10): *"I tend to want things to land on main without needing my review. So that probably does suggest
either a post-feature thing or we allow things to land on main with that and only that category of box unticked. And then
just as we have a make target for our `make speckit-todo` we could have a separate target"*. So a feature lands with its
GM's review still open, and this lists, by feature, what waits on him:

- HELD - work on the item cannot go on until the GM decides: the rows 328's ranking flags `Held` (`audit/overrides.json`);
- TO REVIEW - the work went on and landed, and the GM may overturn it: every round-arbiter ruling and every finding accepted
  with a reason (`specs/NNN/gm-review.jsonl`, written by `make arbiter-ruled` and `make accept`).

A feature with a row of either kind carries ONE box, `- [ ] GM review (make gm-reviewed F=NNN) [lands-open]`, which this
adds; `make speckit-todo` reads such a feature `Done - GM review pending`; `make gm-reviewed F=NNN` marks its rows reviewed
and ticks the box, and `OVERTURN=<row> TO=<feature>` turns a ruling the GM overturns into an open row of that feature.

A row the GM DISCUSSED with a session and agreed needs no more action is reviewed: the session runs `make gm-reviewed F=NNN
WORDS="<his words, verbatim>"` in that turn, and the words are kept on each row it marks (the GM, 2026-10-10: *"if we have a
discussion like the one we had and then we agree that it doesn't need any more action, then shouldn't that count as me
reviewing it"* - 370's one row sat pending after exactly that discussion).

    gm_review.py list                                   the held rows, and each feature's to-review rows counted
    gm_review.py list F                                 feature F's to-review rows, one line per reason
    gm_review.py accept F FINDING REASON                a finding accepted with a reason: a to-review row
    gm_review.py reviewed F [ROW G]                     the GM has reviewed F's rows (GM_WORDS= in the environment: his words)
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True
ROWS = "gm-review.jsonl"
HELD = Path("specs/328-match-the-research/audit/overrides.json")


def box(d: Path) -> str:
    """The one GM-review box a feature carries, in the one form `speckit-todo.py --holding` honors."""
    return f"- [ ] GM review (make gm-reviewed F={int(d.name.split('-', 1)[0])}) [lands-open]"


def rows(d: Path) -> list[dict]:
    f = d / ROWS
    out = []
    for line in (f.read_text(encoding="utf-8").splitlines() if f.is_file() else []):
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def ensure_box(d: Path) -> bool:
    """Add the GM-review box to `tasks.md` when the feature has an open row and no box yet; True when added."""
    tasks = d / "tasks.md"
    if not tasks.is_file() or not any("reviewed" not in r for r in rows(d)):
        return False
    text = tasks.read_text(encoding="utf-8")
    if "GM review (make gm-reviewed" in text:
        return False
    tasks.write_text(text.rstrip("\n") + "\n" + box(d) + "\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n",
                     encoding="utf-8")
    return True


def held(root: Path) -> list[str]:
    """The rows held for the GM today: 328's ranking rows flagged `Held`."""
    f = root / HELD
    data = json.loads(f.read_text(encoding="utf-8")) if f.is_file() else {}
    return [f"{k}: {v.get('flag', '')[:160]}" for k, v in sorted(data.items()) if str(v.get("flag", "")).startswith("Held")]


KINDS = {"arbiter": "arbiter rulings", "accepted": "findings accepted with a reason",
         "arbiter-fix-done": "tooling fixes the arbiter asked for, made",
         "arbiter-fix-declined": "tooling fixes the arbiter asked for, declined to the GM"}
SHORT = {"arbiter": "rulings", "accepted": "accepted", "arbiter-fix-done": "fixes made", "arbiter-fix-declined": "fixes DECLINED"}


def _num(d: Path) -> int:
    return int(d.name.split("-", 1)[0])


def _fit(line: str, width: int) -> str:
    return line if len(line) <= width else line[: width - 3].rstrip() + "..."


def _subject(r: dict) -> tuple[str, str]:
    """A row's trigger as (check, subject): `round:modal-form|modal:sheet/kitchen@3` -> (`modal-form`, `sheet/kitchen`),
    `red-gate@<utc>` -> (`red-gate`, `<utc>`), a reversal -> its file's name; an accepted finding is its own subject."""
    t = str(r.get("trigger") or "")
    if not t:
        return "", str(r.get("finding", ""))
    m = re.fullmatch(r"round:([^|]+)\|[a-z]+:(.+?)(?:@\d+)?", t)
    if m:
        return m.group(1), m.group(2)
    m = re.fullmatch(r"([a-z-]+)[:@](.+?)", t)
    if m:
        return m.group(1), m.group(2).rsplit("/", 1)[-1] if m.group(1) == "reversal" else m.group(2)
    return "", t


def _ids(ids: list[int]) -> str:
    """Row numbers as runs: [0, 1, 2, 5] -> `0-2,5`."""
    runs: list[list[int]] = []
    for i in ids:
        if runs and i == runs[-1][1] + 1:
            runs[-1][1] = i
        else:
            runs.append([i, i])
    return ",".join(str(a) if a == b else f"{a}-{b}" for a, b in runs)


def open_rows(root: Path) -> list[tuple[Path, list[tuple[int, dict]]]]:
    """Each feature with rows the GM has not reviewed, and those rows with their numbers (OVERTURN= takes the number)."""
    out = [(d, [(i, r) for i, r in enumerate(rows(d)) if "reviewed" not in r]) for d in sorted((root / "specs").glob("*/"))]
    return [(d, o) for d, o in out if o]


def _counts(o: list[tuple[int, dict]]) -> str:
    """`49 rulings (2 continue), 34 fixes made` - the feature's rows by kind; a ruling other than accept is counted by verdict."""
    parts = []
    for kind in sorted({r.get("kind", "") for _, r in o}, key=lambda k: list(KINDS).index(k) if k in KINDS else 99):
        of = [r for _, r in o if r.get("kind", "") == kind]
        verdicts = {}
        for r in of:
            verdicts[r.get("ruling", "")] = verdicts.get(r.get("ruling", ""), 0) + 1
        by = ", ".join(f"{n} {v}" for v, n in sorted(verdicts.items(), key=lambda x: -x[1]) if v != "accept") if kind == "arbiter" else ""
        parts.append(f"{len(of)} {SHORT.get(kind, kind)}" + (f" ({by})" if by else ""))
    return ", ".join(parts)


def _detail(d: Path, o: list[tuple[int, dict]], width: int) -> list[str]:
    """One feature's rows by kind; rows sharing one reason are one line naming every subject."""
    out = [f"{d.name}: {len(o)} row(s) - {_counts(o)}"]
    for kind in sorted({r.get("kind", "") for _, r in o}, key=lambda k: list(KINDS).index(k) if k in KINDS else 99):
        out += ["", f"  {KINDS.get(kind, kind)}"]
        groups: dict[tuple[str, str], list[tuple[int, dict]]] = {}
        for i, r in o:
            if r.get("kind", "") == kind:
                groups.setdefault((r.get("ruling", ""), r.get("why") or r.get("tooling_fix") or ""), []).append((i, r))
        for (verdict, why), g in groups.items():
            subjects = sorted({" ".join(x for x in _subject(r) if x) for _, r in g})
            head = f"    [{_ids([i for i, _ in g])}] " + (f"{verdict}: " if verdict else "")
            out.append(_fit(head + "; ".join(subjects), width))
            out += [_fit(f"        {why}", width)] if why else []
    return out


def listing(root: Path, feature: str = "", width: int = 0) -> str:
    width = width or max(80, shutil.get_terminal_size((140, 24)).columns)
    features = open_rows(root)
    if feature:
        d = _feature(root, feature)
        o = next((o for f, o in features if f == d), [])
        if not o:
            return f"gm-review: nothing of {d.name} waits on the GM\n"
        return "\n".join(_detail(d, o, width) + ["", f"  reviewed:     make gm-reviewed F={_num(d)}",
                                                 f"  overturn one: make gm-reviewed F={_num(d)} OVERTURN=<row> TO=<feature>"]) + "\n"
    hs = held(root)
    if not hs and not features:
        return "gm-review: nothing waits on the GM\n"
    n = sum(len(o) for _, o in features)
    out = [f"GM REVIEW - {len(hs)} held, {n} landed row(s) to review in {len(features)} feature(s)", ""]
    if hs:
        out.append("HELD - work cannot go on until the GM decides (feature 328's ranking, carried by 374)")
        for h in hs:
            key, _, flag = h.partition(": ")
            out += [_fit(f"  * {key}", width), _fit(f"      {re.sub(r'^Held[:,]?\s*', '', flag)}", width)]
        out.append("")
    if features:
        out.append("TO REVIEW - landed; the GM may overturn any row")
        out += [_fit(f"  {_num(d):>3}  {_fit(d.name.split('-', 1)[1], 40):<40} {len(o):>3}  {_counts(o)}", width) for d, o in features]
        out += ["", "  a feature's rows:  make gm-review F=NNN",
                "  reviewed:          make gm-reviewed F=NNN   (agreed in discussion with the GM: add WORDS=\"<his words>\")"]
    return "\n".join(out) + "\n"


def accept(d: Path, finding: str, reason: str) -> dict:
    """A finding accepted with a reason - the work goes on, and the GM may overturn it after landing (FR-012)."""
    if len(reason.split()) < 2:
        raise ValueError("REASON needs two words or more - the GM reads it")
    row = {"kind": "accepted", "finding": finding, "why": reason, "utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
    with (d / ROWS).open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    ensure_box(d)
    return row


def reviewed(root: Path, d: Path, overturn: int | None = None, to: Path | None = None, words: str = "") -> list[str]:
    """The GM has reviewed `d`'s rows: each marked reviewed; an overturned one becomes an open row of the feature `to`; the
    GM-review box is ticked - through the closing check, since it may close the feature (FR-009). `words`, when a session marks
    the review on the GM's behalf after discussing it with him, are his words, kept on each row it marks."""
    if words and len(words.split()) < 2:
        raise ValueError("WORDS are the GM's own, two words or more")
    rs = rows(d)
    msgs = []
    if overturn is not None:
        if to is None or not (0 <= overturn < len(rs)):
            raise ValueError("OVERTURN=<row number> needs TO=<an open feature>")
        with (to / "found.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({"check": "gm-review", "file": d.name, "block": rs[overturn].get("trigger") or rs[overturn].get("finding"),
                                 "finding": f"overturned by the GM: {rs[overturn].get('why', '')}", "status": "open"}, ensure_ascii=False) + "\n")
        msgs.append(f"row {overturn} overturned - an open row of {to.name}")
    tasks = d / "tasks.md"
    text = tasks.read_text(encoding="utf-8") if tasks.is_file() else ""
    if box(d) in text and text.count("- [ ] ") == 1:
        sys.path.insert(0, str(Path(__file__).resolve().parent / "gates"))
        import close_check  # noqa: PLC0415

        why = close_check.reasons(d, root / "specs")
        if why:
            raise ValueError("the GM's box closes the feature, and: " + "; ".join(why))
    today = time.strftime("%Y-%m-%d", time.gmtime())
    (d / ROWS).write_text("".join(json.dumps({**r, "reviewed": r.get("reviewed", today), **({"gm_words": words} if words and "reviewed" not in r else {})}, ensure_ascii=False) + "\n" for r in rs),
                          encoding="utf-8")
    if box(d) in text:
        tasks.write_text(text.replace(box(d), box(d).replace("- [ ] ", "- [x] ")), encoding="utf-8")
    msgs.append(f"{len(rs)} row(s) of {d.name} reviewed")
    return msgs


def _feature(root: Path, f: str) -> Path:
    hits = sorted((root / "specs").glob(f"{int(f):03d}-*")) if f.isdigit() else [root / "specs" / f]
    if not hits or not hits[0].is_dir():
        raise SystemExit(f"gm-review: no specs/{f}* directory")
    return hits[0]


def main(argv: list[str]) -> int:
    root = Path(".").resolve()
    try:
        if argv[:1] == ["list"] and len(argv) <= 2:
            sys.stdout.write(listing(root, *argv[1:]))
        elif argv[:1] == ["accept"] and len(argv) == 4:
            accept(_feature(root, argv[1]), argv[2], argv[3])
            print("accept: recorded for the GM's review after landing")
        elif argv[:1] == ["reviewed"] and len(argv) in (2, 4):
            ov = int(argv[2]) if len(argv) == 4 else None
            to = _feature(root, argv[3]) if len(argv) == 4 else None
            for m in reviewed(root, _feature(root, argv[1]), ov, to, os.environ.get("GM_WORDS", "").strip()):
                print(f"gm-reviewed: {m}")
        else:
            print(__doc__.split("\n\n")[-1], file=sys.stderr)
            return 2
    except ValueError as e:
        print(f"gm-review: refused - {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
