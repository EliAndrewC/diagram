#!/usr/bin/env python3
"""The attempts log: what each source was tried for, and what came of it (feature 312, FR-015 - FR-018).

WHY (the GM, 2026-10-02): *"it might make sense for efficiency purposes to have a separate file in which we record all of
the things that we have tried to use a source for. and found it wanting ... if we ever do another pass on a research topic,
then we can have a procedure by which we first check to see if we have tried to answer this specific question already using
this source"* - and the same for cited sources, *"because we do often cite the same source multiple times for multiple
different questions"*. The sources-consulted ledger (feature 288) records READS, host-local; this records ATTEMPTS, committed
beside the record: `research/source-attempts.jsonl`, one JSON line per attempt, union-merged (`.gitattributes`) so every
clone appends without a conflict.

A LINE: `{"url": <normalized>, "raw", "key", "question": NNNN | "old:<page>/<NNN>" | "unknown", "sought", "outcome",
"date", "feature", "route"}`. OUTCOMES (spec FR-015): `found`, `partial`, `not-found`, `not-applicable`, `unreadable`,
`unknown` - a read just begun is written `unknown`, and `make source-outcome` appends its outcome as a later line. What a cited source WAS used for is derived from its footnotes and
never copied here.

THE SEED (FR-016): every ledger row becomes a line - its question mapped to the current stem through `moved-303.json`, a
free-text "question" (the seed import of feature 288 kept the reading prompt there) taken as what was sought, an id that
cannot be mapped kept as `old:<id>`, none as `unknown`; what was sought, where nothing says, is
`unknown - recorded before feature 312` (the GM: *"it is of course okay in any case to mark that we don't know why something
was consulted originally"*).

    attempts.py show (--url U | --key K | --q NNNN)     the attempts, and the filter's verdict for a URL
    attempts.py add --url U --q NNNN --sought S [--outcome O] [--route R] [--key K]
    attempts.py seed                                     once: the ledger's rows (refuses a second run)
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import re
import sys

HERE = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import sources as src  # noqa: E402

RESEARCH = pathlib.Path("research")
LOG = RESEARCH / "source-attempts.jsonl"
NOT_KEPT = RESEARCH / "not-kept.jsonl"
UNCITED = RESEARCH / "sources" / "040-uncited-works"
OUTCOMES = ("found", "partial", "not-found", "not-applicable", "unreadable", "unknown")
UNKNOWN_SOUGHT = "unknown - recorded before feature 312"
SEED = "ledger-2026-10-02"
_STEM = re.compile(r"^\d{4}$")
_OLD = re.compile(r"^([a-z0-9-]+(?:/[a-z0-9-]+)*)/(\d{3})$")


def base(root: pathlib.Path) -> pathlib.Path:
    """The tree whose `research/` holds the log: the clone, or `L7R_ATTEMPTS_ROOT` - the tests' seam, as
    `L7R_SOURCES_HOME` moves the ledger (`tests/tooling/conftest.py`); no session sets it."""
    return pathlib.Path(os.environ.get("L7R_ATTEMPTS_ROOT") or root)


def today() -> str:
    return datetime.date.today().isoformat()


def read(root: pathlib.Path, rel: pathlib.Path = LOG) -> list[dict]:
    path = base(root) / rel
    out = []
    for raw in path.read_text(encoding="utf-8").splitlines() if path.is_file() else []:
        try:
            out.append(json.loads(raw))
        except json.JSONDecodeError:
            continue
    return out


def write(root: pathlib.Path, lines: list[dict], rel: pathlib.Path = LOG) -> None:
    """Append under the ledger's kind of lock: two agents of one session never interleave half lines."""
    if not lines:
        return
    for line in lines:
        src._blocked().check(line.get("raw") or line["url"], "the attempts log")
    path = base(root) / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    with src.locked(src.home(root), timeout=30.0), open(path, "a", encoding="utf-8") as fh:
        fh.writelines(json.dumps(x, ensure_ascii=False) + "\n" for x in lines)


def line(url: str, question: str, sought: str, outcome: str = "unknown", *, key: str = "", route: str = "",
         feature: str = "", date: str = "") -> dict:
    if outcome not in OUTCOMES:
        raise ValueError(f"outcome {outcome!r} is not one of {', '.join(OUTCOMES)}")
    return {"url": src.norm(url), "raw": url, "key": key, "question": question or "unknown", "sought": sought,
            "outcome": outcome, "date": date or today(), "feature": feature or os.environ.get("SPECIFY_FEATURE", "")[:3],
            "route": route}


def add(root: pathlib.Path, url: str, question: str, sought: str, outcome: str = "unknown", **more: str) -> dict:
    more.setdefault("feature", src.context(root)["feature"])
    x = line(url, question, sought, outcome, **more)
    write(root, [x])
    return x


# ---- the seed ----


def old_ids(root: pathlib.Path) -> dict[str, str]:
    """`moved-303.json`'s numbers, keyed as the ledger wrote them (`<page>/<NNN>`)."""
    path = root / RESEARCH / "moved-303.json"
    numbers = json.loads(path.read_text(encoding="utf-8")).get("numbers", {}) if path.is_file() else {}
    return {k.replace(" ", "/"): v for k, v in numbers.items()}


def question_of(q: str, mapped: dict[str, str]) -> tuple[str, str]:
    """(the question, what was sought) for one ledger `questions` entry."""
    if _STEM.match(q):
        return q, ""
    if _OLD.match(q):
        return mapped.get(q, f"old:{q}"), ""
    return "unknown", q


_OUTCOME_OF = {"nothing-found": "not-found", "rejected": "not-applicable", "unreadable": "unreadable", "cited": "found"}


def from_ledger(outcome: str) -> tuple[str, str, str]:
    """A ledger outcome as (the attempt's outcome, its key, the rejection's reason)."""
    kind, _, why = outcome.partition(":")
    return _OUTCOME_OF.get(kind.strip(), "unknown"), why.strip() if kind == "cited" else "", why.strip() if kind == "rejected" else ""


def last_sought(root: pathlib.Path, url: str, question: str) -> str:
    """What the latest attempt on this URL for this question sought - so an outcome recorded later carries it."""
    n = src.norm(url)
    hits = [x for x in read(root) if x.get("url") == n and x.get("question") == (question or "unknown")]
    return hits[-1]["sought"] if hits else UNKNOWN_SOUGHT


def outcome(root: pathlib.Path, url: str, question: str, ledger_outcome: str, sought: str = "") -> dict:
    """`make source-outcome`'s attempt line (FR-017): the outcome of the read, with what it sought."""
    result, key, why = from_ledger(ledger_outcome)
    sought = sought or last_sought(root, url, question)
    return add(root, url, question, sought + (f" (rejected: {why})" if why else ""), result, key=key, route="source-outcome")


def seed_lines(rows: list[dict], mapped: dict[str, str]) -> list[dict]:
    out = []
    for r in rows:
        result, key, why = from_ledger(r.get("outcome", ""))
        for q in r.get("questions") or [""]:
            question, sought = question_of(q, mapped) if q else ("unknown", "")
            sought = (sought or UNKNOWN_SOUGHT) + (f" (rejected: {why})" if why else "")
            x = line(r.get("raw") or r["url"], question, sought, result, key=key, route="ledger",
                     feature=r.get("feature", ""), date=r.get("utc", "")[:10])
            x["seed"] = SEED
            out.append(x)
    return out


def seed(root: pathlib.Path, where: pathlib.Path) -> int:
    """Every ledger row with no attempt line yet gets one - so a re-run catches up the rows sessions on code without this
    log wrote meanwhile (three of feature 315's reads, 2026-10-02, before 312 landed). A row is matched to a line by URL,
    day and feature: a second read of one page on one day by one feature already has its line."""
    have = {(x["url"], x.get("date", ""), x.get("feature", "")) for x in read(root)}
    rows = [r for r in src.read(where) if r.get("url") and not src._blocked().blocked(r.get("raw") or r["url"])]
    lines = [x for x in seed_lines(rows, old_ids(root)) if (x["url"], x.get("date", ""), x.get("feature", "")) not in have]
    if not lines:
        print("attempts: every ledger row has an attempt line - nothing written", file=sys.stderr)
        return 0
    new = {x["url"] for x in lines}
    rows = [r for r in rows if src.norm(r["url"]) in new]
    write(root, lines)
    print(f"attempts: {len(lines)} line(s) seeded from {len(rows)} ledger row(s)")
    return len(lines)


# ---- reading ----


def verdict(root: pathlib.Path, url: str) -> str:
    """The filter's word on a URL: not kept (its reasons), kept (its uncited entry), or nothing yet."""
    n = src.norm(url)
    for x in reversed(read(root, NOT_KEPT)):
        if x.get("url") == n:
            note = f" - {x['note']}" if x.get("note") else ""
            return f"NOT KEPT {x.get('date', '')} ({', '.join(x.get('reasons', []))}{note})"
    d = base(root) / UNCITED
    for p in sorted(d.glob("*.html")) if d.is_dir() else []:
        if n in {src.norm(u) for u in src._URL.findall(p.read_text(encoding="utf-8"))}:
            return f"KEPT, uncited: {p.name}"
    return ""


def show(x: dict) -> str:
    return f"  {x.get('date', '')} Q {x.get('question', '')}: {x.get('outcome', '')} - {x.get('sought', '')}"


def report(root: pathlib.Path, *, url: str = "", key: str = "", q: str = "") -> list[str]:
    lines = read(root)
    if url:
        n = src.norm(url)
        hits = [x for x in lines if x.get("url") == n]
        head = [f"attempts: {url} - " + (f"{len(hits)} earlier attempt(s):" if hits else "no earlier attempt")]
        v = verdict(root, url)
        head += [f"  filter verdict: {v}"] if v else []
    elif key:
        hits = [x for x in lines if x.get("key") == key]
        head = [f"attempts: key {key} - {len(hits)} attempt(s)"]
    else:
        hits = [x for x in lines if x.get("question") == q]
        head = [f"attempts: question {q} - {len(hits)} attempt(s)"]
        return head + [f"  {x.get('raw') or x['url']}\n  " + show(x).strip() for x in hits]
    return head + [show(x) for x in hits]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    sh = sub.add_parser("show")
    g = sh.add_mutually_exclusive_group(required=True)
    g.add_argument("--url")
    g.add_argument("--key")
    g.add_argument("--q")
    ad = sub.add_parser("add")
    ad.add_argument("--url", required=True)
    ad.add_argument("--q", default="unknown")
    ad.add_argument("--sought", required=True)
    ad.add_argument("--outcome", default="unknown", choices=OUTCOMES)
    ad.add_argument("--route", default="")
    ad.add_argument("--key", default="")
    sub.add_parser("seed")
    args = ap.parse_args(argv)
    root = src.repo_root()
    if args.cmd == "show":
        print("\n".join(report(root, url=args.url or "", key=args.key or "", q=args.q or "")))
    elif args.cmd == "add":
        add(root, args.url, args.q, args.sought, args.outcome, route=args.route, key=args.key)
    else:
        seed(root, src.home(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
