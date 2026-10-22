"""A claim's label against its own words, flagged at `make claims-owed` (feature 405 T120, plan D91).

WHY. Five claims tasks of 2026-10-22 (T115-T108) spent most of their time in impl-drift rounds returning MISLABELED, not on
code: T115 took four rounds, T116 and T118 a re-decided plan each. Every one was a label its own account contradicted - a
GUESS that said the code departs from a page, a bare GUESS whose account named the page that speaks, a `GUESS <page>` whose
page states no such figure. The words are in the claim at the edit, so they are read there, before any round.

THE VOCABULARY (the claim grammar, `l7r/diagram/tools/claims.py`): a bare `GUESS` - no page speaks; `GUESS <drawing page>` -
the page records it as its own guess; `DEVIATION <page>` - the code departs from what the page says, and the page records the
departure; a page cited - the page states it.

A FLAG, never a refusal: the match is on words, and a refusal on a right label teaches a session to bypass every guard. Only
the owed claims are read - what is about to go to impl-drift - so a checked claim is never flagged again.
Measured 2026-10-22 over every claim of the engine: 31 of 6,178 flagged, so an owed batch rarely carries one.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from pathlib import Path
from typing import Any

#: An account saying the code departs from a page: a DEVIATION, whatever it is labeled.
DEPARTS = re.compile(
    r"\b(?:stricter|looser|wider|narrower|tighter|closer|farther) than (?:the page|its page|0\d{3}\b)"
    r"|\bshort of (?:the page|its page|0\d{3}\b)|\bdepart(?:s|ing|ure)? from\b|\bstricter than\b",
    re.I,
)
#: A question named in an account.
NAMED = re.compile(r"(?<![\d.])0\d{3}\b")
#: An account that says the named page is silent on this, or the figure is ours: a bare GUESS may still name the page.
SILENT = re.compile(r"\bsilent\b|\bno page\b|\bdoes not (?:say|size|give|state|name)\b|\bis ours\b|\bour own\b|\bunsized\b", re.I)
#: A figure in feet, as an account writes it.
FEET = re.compile(r"(?<![\d.])(\d+(?:\.\d+)?)\s*(?:ft|feet|foot)\b")


def _states(text: str, fig: str) -> bool:
    fig = fig[:-2] if fig.endswith(".0") else fig
    return re.search(rf"(?<![\d.]){re.escape(fig)}(?!\d|\.\d)", text) is not None


def flag(key: str, claim: Any, qdir: Path, pages: dict[str, str]) -> list[str]:  # noqa: ANN401 - the engine's Claim
    """The label faults of one claim, each with its fix."""
    if claim.backing != "GUESS":
        return []
    account, out = claim.account, []
    if DEPARTS.search(account):
        out.append(f"claims-label: {key} - its account says the code departs from a page: that is `DEVIATION <page>`, recorded on the page (or say why the page does not speak, and keep GUESS)")
    if not claim.pointers and NAMED.search(account) and not SILENT.search(account):
        out.append(
            f"claims-label: {key} - a bare GUESS says no page speaks, but its account names {', '.join(sorted(set(NAMED.findall(account))))}: "
            "cite the page if it states this, `GUESS <its .drawing.html>` if it records it as a guess, `DEVIATION <page>` if the code departs "
            "(or say the page is silent)"
        )
    if claim.pointers:
        for p in claim.pointers:
            if p not in pages:
                f = qdir / Path(p).name
                pages[p] = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""
        texts = [pages[p] for p in claim.pointers]
        missing = [fig for fig in dict.fromkeys(FEET.findall(account)) if not any(_states(t, fig) for t in texts)]
        if missing:
            out.append(
                f"claims-label: {key} - `GUESS <page>` says the page records this guess, but no page it names states {', '.join(m + ' ft' for m in missing)}: "
                "a bare GUESS if no page speaks, `DEVIATION <page>` if the code departs from the page's figure"
            )
    return out


def flags(rows: Mapping[str, Any], keys: Iterable[str], qdir: Path) -> list[str]:
    """Every label fault among the claims of `keys` (rows of `claims.current`)."""
    pages: dict[str, str] = {}
    return [x for k in dict.fromkeys(keys) if k in rows and rows[k].claim is not None for x in flag(k, rows[k].claim, qdir, pages)]
