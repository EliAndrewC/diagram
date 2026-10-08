#!/usr/bin/env python3
"""The access tag: what can be got of each source, and when that was last known (feature 313, spec FR-011).

WHY (the GM, 2026-10-02, `specs/312-uncited-source-catalog/request.md`): *"it is useful for us to record what things in the
past you were able to get versus things that timed out versus things that I was able to get ... versus things that I was
able to get only a like partial summary of ... versus things that I found require a paid login"*, and (313's request)
*"do include the access tags thing as part of uh, feature 313."*

THE STATES are declared once, in order from the most open, in `research/source-access.json`: open, gm-full, gm-partial,
paywalled, bot-refused, down, gone, never-read.

DERIVED, NOT STORED (spec Decisions): a stored copy would go stale at the next archive capture and conflict across clones,
so the tag is computed each time from what the repository records (plan D9):
  1. a GM mark recorded on a download-list entry naming the key: downloaded -> gm-full whatever else is ticked; partial ->
     gm-partial; paywalled alone -> paywalled; not found alone gives no state. Several entries: the newest mark that gives a
     state, on the same date the most open; a not-found only adds to the basis;
  2. else the most open of the key's archive manifest rows (feature 309), dated by its capture - a row whose page would
     not render whole but whose served text is kept counts as open, since we read it;
  3. else, no row: open with a READ comment, dated by the latest READ; never-read without one;
  4. a state recorded by hand in `source-access.json` (`make access-tags SET=`) wins over 2-3 on the same date or later,
     never over a GM mark that gives a state - the GM's tick is the latest word.
A download-list entry with no registry key is `download:<id>`: rule 1, then a state recorded by hand, else never-read.

    access_tags.py report [--key K | --id ID] [--json]       `make access-tags`
    access_tags.py set <key|download:ID> <state> <date> <reason>   `make access-tags SET=`
"""

from __future__ import annotations

import argparse
import dataclasses
import glob
import json
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import downloads as dl  # noqa: E402

RECORD = "research"
ACCESS = f"{RECORD}/source-access.json"
REGISTRY = f"{RECORD}/sources/010-works-cited"
MANIFEST = f"{RECORD}/archive"
KEY_HEAD = re.compile(r'<h3 id="([^"]+)"')
READ = re.compile(r"READ (\d{4}-\d{2}-\d{2})")
TICKED_KEY = re.compile(r"`([a-z0-9][a-z0-9-]*)`")
KEY_LINE = re.compile(r"^- Key: (.+)$", re.M)
LINK = re.compile(r"\]\((https?://[^)\s]+)\)")
HTTP = re.compile(r"HTTP (\d{3})")


@dataclasses.dataclass(frozen=True)
class Tag:
    state: str
    date: str | None
    basis: str


def load_states(root: pathlib.Path) -> tuple[list[str], dict[str, list[dict]]]:
    doc = json.loads((root / ACCESS).read_text(encoding="utf-8"))
    return [s["id"] for s in doc["states"]], doc.get("recorded", {})


def row_state(row: dict) -> str:
    """One manifest row's state (plan D9 rule 2)."""
    outcome = row.get("outcome", "")
    if outcome in ("archived", "archived-earlier-snapshot"):
        return "open"
    if outcome == "archived-gm-copy":
        return "gm-full"
    reason = row.get("reason", "")
    if reason.startswith("the page would not render whole"):
        # The site served the page and its text is kept (`archive.py`, the REFUSED branch's capture): we read it; only
        # the whole-page snapshot failed. 22 rows on 2026-10-02 (a count of the manifest by reason).
        return "open"
    code = HTTP.search(reason)
    if code and code.group(1) in ("404", "410"):
        return "gone"
    if (code and code.group(1).startswith("5")) or re.search(r"Timeout|network|aborted|ECONN|ENOTFOUND|socket", reason, re.I):
        return "down"
    return "bot-refused"


def mark_state(m: dl.Marks) -> str | None:
    """A recorded mark's state (plan D9 rule 1); None for not found alone, or no mark."""
    if m.downloaded:
        return "gm-full"
    if m.partial:
        return "gm-partial"
    if m.paywalled:
        return "paywalled"
    return None


@dataclasses.dataclass
class World:
    """What the repository records, read once."""

    order: list[str]
    recorded: dict[str, list[dict]]
    keys: dict[str, list[str]]  # key -> READ dates
    rows: dict[str, list[dict]]  # key -> manifest rows
    marks: dict[str, list[tuple[str, dl.Entry]]]  # key or download:<id> -> (date, entry) with recorded marks
    keyless: list[str]  # download:<id> of entries naming no key
    entry_keys: dict[str, set[str]]  # download:<id> -> the registry keys that entry names

    def rank(self, state: str) -> int:
        return self.order.index(state)


def entry_keys(e: dl.Entry, keys: set[str], url_keys: dict[str, set[str]]) -> set[str]:
    """The registry keys an entry names (plan D8): backticked keys, `- Key:` lines, and its links' manifest keys."""
    text = e.heading + "\n" + e.body_text()
    found = {k for k in TICKED_KEY.findall(text) if k in keys}
    for line in KEY_LINE.findall(text):
        found |= {k.strip() for k in line.split(",") if k.strip() in keys}
    for url in LINK.findall(text):
        found |= url_keys.get(url, set())
    return found


def load(root: pathlib.Path) -> World:
    order, recorded = load_states(root)
    keys: dict[str, list[str]] = {}
    for f in sorted(glob.glob(str(root / REGISTRY / "*.html"))):
        text = pathlib.Path(f).read_text(encoding="utf-8")
        m = KEY_HEAD.search(text)
        if m:
            keys[m.group(1)] = READ.findall(text)
    rows: dict[str, list[dict]] = {}
    url_keys: dict[str, set[str]] = {}
    for f in sorted(glob.glob(str(root / MANIFEST / "*" / "*.json"))):
        row = json.loads(pathlib.Path(f).read_text(encoding="utf-8"))
        for k in row.get("keys", []):
            rows.setdefault(k, []).append(row)
            for u in (row.get("url"), row.get("final_url")):
                if u:
                    url_keys.setdefault(u, set()).add(k)
    marks: dict[str, list[tuple[str, dl.Entry]]] = {}
    keyless: list[str] = []
    named_by: dict[str, set[str]] = {}
    canon = root / dl.CANON
    for e in dl.entries(dl.parse(canon.read_text(encoding="utf-8"))) if canon.is_file() else []:
        named_by[f"download:{e.id}"] = entry_keys(e, set(keys), url_keys)
        named = named_by[f"download:{e.id}"] or {f"download:{e.id}"}
        if named == {f"download:{e.id}"}:
            keyless.append(f"download:{e.id}")
        rec = dl.RECORDED.match(e.recorded or "")
        if e.marks is not None and e.marks.any() and rec:
            for k in named:
                marks.setdefault(k, []).append((rec.group(1), e))
    return World(order, recorded, keys, rows, marks, keyless, named_by)


def tag(w: World, key: str) -> Tag:
    """The tag of one registry key or `download:<id>` (plan D9)."""
    gm = _from_marks(w, key)
    if gm is not None and gm.state != "":
        return gm
    derived = _derived(w, key)
    hand = sorted(w.recorded.get(key, []), key=lambda r: r["date"])
    if hand and (derived.date is None or hand[-1]["date"] >= derived.date):
        h = hand[-1]
        return Tag(h["state"], h["date"], f"recorded by hand: {h['reason']}")
    if gm is not None:
        return dataclasses.replace(derived, basis=derived.basis + "; " + gm.basis)
    return derived


def _from_marks(w: World, key: str) -> Tag | None:
    """Rule 1. A Tag with state "" carries only a not-found basis; None where no mark is recorded."""
    marked = w.marks.get(key, [])
    giving = [(d, e, mark_state(e.marks)) for d, e in marked if e.marks is not None and mark_state(e.marks)]
    if giving:
        date, e, state = max(giving, key=lambda t: (t[0], -w.rank(t[2] or "never-read")))
        assert state is not None
        return Tag(state, date, f"the GM's mark on entry {e.id}, recorded {date}")
    if marked:
        ids = ", ".join(e.id for _d, e in marked)
        return Tag("", None, f"the GM did not find it (entry {ids})")
    return None


def _derived(w: World, key: str) -> Tag:
    """Rules 2 to 4."""
    if key.startswith("download:"):
        return Tag("never-read", None, "a download-list entry with no registry key and no mark")
    reads = sorted(w.keys.get(key, []))
    rows = w.rows.get(key, [])
    if rows:
        best = min(rows, key=lambda r: (w.rank(row_state(r)), "~" if not r.get("captured") else "", -int(re.sub(r"\D", "", r.get("captured", "0"))[:14] or 0)))
        state = row_state(best)
        date = (best.get("captured") or "")[:10] or None
        why = best.get("outcome", "") + (f" ({best['reason'][:80]})" if best.get("reason") else "")
        return Tag(state, date, f"the archive manifest: {why}, {best.get('url', '')}")
    if reads:
        return Tag("open", reads[-1], "a READ comment in its registry entry; no archive row")
    return Tag("never-read", None, "no READ in its registry entry and no archive row")


def every(w: World) -> dict[str, Tag]:
    return {k: tag(w, k) for k in [*sorted(w.keys), *w.keyless]}


def set_state(root: pathlib.Path, key: str, state: str, date: str, reason: str) -> None:
    """Record a state by hand (rule 5); refuses an unknown state, a bad date or a reason under two words."""
    path = root / ACCESS
    doc = json.loads(path.read_text(encoding="utf-8"))
    states = [s["id"] for s in doc["states"]]
    if state not in states:
        raise dl.Refusal(f"`{state}` is not a state - the states are {', '.join(states)} ({ACCESS})")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", date):
        raise dl.Refusal(f"DATE={date!r} - give the date the evidence was seen, YYYY-MM-DD")
    if len(reason.split()) < 2:
        raise dl.Refusal("REASON= says what the state rests on, in two words or more - the line or page that shows it")
    doc.setdefault("recorded", {}).setdefault(key, []).append({"state": state, "date": date, "reason": reason})
    doc["recorded"] = {k: doc["recorded"][k] for k in sorted(doc["recorded"])}
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    rp = sub.add_parser("report")
    rp.add_argument("--key")
    rp.add_argument("--json", action="store_true")
    st = sub.add_parser("set")
    for a in ("key", "state", "date", "reason"):
        st.add_argument(a)
    a = ap.parse_args(argv)
    root = pathlib.Path(dl.git(pathlib.Path.cwd(), "rev-parse", "--show-toplevel").stdout.strip() or ".")
    try:
        if a.cmd == "set":
            set_state(root, a.key, a.state, a.date, a.reason)
            print(f"access-tags: {a.key} recorded {a.state} ({a.date}) in {ACCESS} - commit it")
            return 0
        w = load(root)
        if a.key:
            if a.key not in w.keys and a.key not in w.keyless and a.key not in w.marks:
                raise dl.Refusal(f"no registry key or list entry `{a.key}` - an entry is `download:<id>`")
            t = tag(w, a.key)
            print(json.dumps({a.key: dataclasses.asdict(t)}, ensure_ascii=False) if a.json else f"{a.key}: {t.state} ({t.date or 'no date'}) - {t.basis}")
            return 0
        tags = every(w)
        if a.json:
            print(json.dumps({k: dataclasses.asdict(t) for k, t in tags.items()}, ensure_ascii=False, indent=1))
            return 0
        counts = {s: 0 for s in w.order}
        for t in tags.values():
            counts[t.state] += 1
        keyed = sum(1 for k in tags if not k.startswith("download:"))
        print(f"access-tags: {keyed} registry keys and {len(tags) - keyed} keyless list entries")
        for s in w.order:
            print(f"  {s:12} {counts[s]}")
        return 0
    except dl.Refusal as r:
        print(f"access-tags: REFUSED - {r}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
