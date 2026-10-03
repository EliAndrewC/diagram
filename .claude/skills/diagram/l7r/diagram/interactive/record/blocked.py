"""Blocked domains and banned citations: the one decision every fetch route, every store and the build ask (feature 312).

The GM, 2026-10-02, on Grokipedia: *"it should be tool enforced"*, and *"I accept your recommendation about blocking
Grokopedia entirely. And that may end up applying to other domains as well if we, for example, determine that another
domain is similarly AI generated. Then we would treat it the same as Grokopedia."* So a BLOCKED DOMAIN (an AI-generated
site) is refused at every fetch route as well as at citation, write-up, ledger and archive, and the list is a category any
domain can join. A source forbidden for any other reason is BANNED AT THE CITATION by URL pattern, never by domain: the
GM, *"things that we forbid might be hosted on the same domains or whatever as things that we do not forbid"*.

Both lists sit beside the record (`research/blocked-domains.json`, `research/banned-citations.json`) and every entry
carries the GM's approval (a date and the words): the loader refuses an entry without one, so a list cannot grow by a
session's say-so (`specs/312-uncited-source-catalog/plan.md` D1). `scripts/` imports this module, so a fetch route and
the build cannot disagree on what is blocked.
"""

from __future__ import annotations

import json
import os
import re
import urllib.parse
from dataclasses import dataclass
from functools import cache

from l7r.diagram.interactive.sources import RESEARCH_DIR

DOMAINS = "blocked-domains.json"
CITATIONS = "banned-citations.json"


class BlockedListError(Exception):
    """A list file that cannot be trusted - an entry with no approval, or a malformed one. Names the file."""


class Blocked(Exception):
    """A URL on the blocked-domain list, refused where it was about to be read or stored."""


@dataclass(frozen=True)
class Rule:
    """One entry of either list: what it matches, why, and the GM's approval."""

    match: str
    reason: str
    approved: str


def _approval(where: str, raw: dict) -> str:
    approved = raw.get("approved")
    if not isinstance(approved, dict) or not approved.get("date") or not approved.get("words"):
        raise BlockedListError(f"{where}: {raw!r} carries no approval - every entry names the GM's approval as \"approved\": {{\"date\": \"YYYY-MM-DD\", \"words\": \"<the GM's words>\"}}")
    return f'{approved["date"]}: {approved["words"]}'


def _load(record_dir: str, name: str, field: str) -> list[tuple[str, dict, str]]:
    """Each entry of a list file as (what it matches, the entry, the file); a missing file is an empty list."""
    where = os.path.join(record_dir, name)
    try:
        with open(where, encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        return []
    out = []
    for raw in data.get(field + "s", []):
        if not isinstance(raw, dict) or not raw.get(field) or not raw.get("reason"):
            raise BlockedListError(f"{where}: {raw!r} needs its {field} and its reason")
        out.append((raw[field], raw, where))
    return out


@cache
def domains(record_dir: str = RESEARCH_DIR) -> tuple[Rule, ...]:
    return tuple(Rule(m.lower().strip("."), raw["reason"], _approval(where, raw)) for m, raw, where in _load(record_dir, DOMAINS, "domain"))


@cache
def patterns(record_dir: str = RESEARCH_DIR) -> tuple[Rule, ...]:
    rules = []
    for m, raw, where in _load(record_dir, CITATIONS, "pattern"):
        try:
            re.compile(m)
        except re.error as err:
            raise BlockedListError(f"{where}: pattern {m!r} does not compile ({err})") from err
        rules.append(Rule(m, raw["reason"], _approval(where, raw)))
    return tuple(rules)


def host(url: str) -> str:
    """The URL's host, lower-cased; a URL written without its scheme is read as https."""
    u = url.strip()
    if not re.match(r"^[a-z][a-z0-9+.-]*://", u, re.I):
        u = "https://" + u
    try:
        return (urllib.parse.urlsplit(u).hostname or "").lower().strip(".")
    except ValueError:  # a malformed URL on the ledger (`[` in its host, measured 2026-10-02) - its host by pattern
        m = re.match(r"^[a-z][a-z0-9+.-]*://([^/?#:]+)", u, re.I)
        return (m.group(1) if m else "").lower().strip(".[]")


def blocked(url: str, record_dir: str = RESEARCH_DIR) -> Rule | None:
    """The blocked-domain rule a URL falls under: its host is the domain or a subdomain of it, never a name that merely
    ends with the same letters (`notgrokipedia.com` is not `grokipedia.com`)."""
    h = host(url)
    return next((r for r in domains(record_dir) if h == r.match or h.endswith("." + r.match)), None)


def banned(url: str, record_dir: str = RESEARCH_DIR) -> Rule | None:
    """The banned-citation rule a URL matches (a blocked domain is banned too)."""
    return blocked(url, record_dir) or next((r for r in patterns(record_dir) if re.search(r.match, url)), None)


def refusal(url: str, rule: Rule, what: str) -> str:
    """The one message every refusal prints: what was refused, the list, and why the entry is on it."""
    return (
        f"{what} refused: {url} is on the blocked list ({DOMAINS}: {rule.match} - {rule.reason}; approved "
        f"{rule.approved}). Find the same fact on another page; a blocked site is never read, cited or recorded."
    )


def check(url: str, what: str, record_dir: str = RESEARCH_DIR) -> None:
    """Raise `Blocked` for a URL on a blocked domain - the call every fetch route and store makes first."""
    rule = blocked(url, record_dir)
    if rule:
        raise Blocked(refusal(url, rule, what))


def refusals(record_dir: str = RESEARCH_DIR) -> list[str]:
    """One build refusal per cited URL - a registry entry's (its comments' too) or a footnote's link - on a blocked
    domain or matching a banned pattern (FR-003, FR-004). The census is the archive's, so what the build calls cited is
    one thing everywhere."""
    from l7r.diagram.interactive.record import archive  # noqa: PLC0415 - archive reads the store, which reads the record

    out = []
    for url, who in archive.cited(record_dir).items():
        rule = banned(url, record_dir)
        if rule:
            where = ", ".join(who.keys + who.notes)
            listed = DOMAINS if blocked(url, record_dir) else CITATIONS
            out.append(f"banned citation: {url} ({where}) is on {listed} ({rule.match} - {rule.reason}) - cite the fact from another source, or state its absence (feature 312)")
    return out
