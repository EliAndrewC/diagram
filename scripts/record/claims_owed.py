"""`scripts/record/claims_owed.py` - which claims a change owes a check, and why (split out of `claims.py` at the 1,000-line bar by
feature 385 T116, plan D134; `claims.py` re-exports every name)."""

from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import TYPE_CHECKING, Any

from claims_triage import page_blocks

if TYPE_CHECKING:
    from claims import Row

SECTION_TRIAGE = "section triage"
CODE_TRIAGE = "code triage"
TRIAGED = ("triage", SECTION_TRIAGE, CODE_TRIAGE)


def standing(pointers: Sequence[str], qdir: Path, memo: dict[str, Any]) -> set[str]:
    """`page:digest` for every block now standing on the questions `pointers` cite."""
    out: set[str] = set()
    for ptr in pointers:
        name = ptr.rsplit("/", 1)[1]
        out.update(f"{name}:{d}" for d, _w in page_blocks(name, qdir, memo)[1])
    return out


def research_why(
    row: Row,
    was: Mapping[str, Any],
    qdir: Path,
    store: Mapping[str, list[str]],
    memo: dict[str, Any],
) -> str:
    """Why a claim whose cited research moved is owed (feature 318, FR-016): a full re-check when a block it rested on is gone
    (`rests changed`), its row predates the snapshots or it cites a page its check never read (T105) (`research changed`); else the TRIAGE."""
    pages = was.get("pages")
    if not isinstance(pages, dict) or any(d not in store for d in pages.values()) or {p.rsplit("/", 1)[1] for p in row.claim.pointers} - set(pages):
        return "research changed"
    rests = was.get("rests")
    if isinstance(rests, list) and not set(rests) <= standing(row.claim.pointers, qdir, memo):
        return "rests changed"
    return "triage"


def owed(
    cur: dict[str, Row],
    index: Mapping[str, Mapping[str, Any]],
    qdir: Path | None = None,
    store: Mapping[str, list[str]] | None = None,
) -> list[tuple[str, str]]:
    """(key, why) for every claim with no row, whose code moved, or whose research moved
    (FR-016: `rests changed` / `research changed` owe `impl-drift`; `triage` owes only the triage of the changed blocks)."""
    out: list[tuple[str, str]] = []
    memo: dict[str, Any] = {}
    moves = moved(cur, index)
    for key, row in sorted(cur.items()):
        was = index.get(key) or index.get(moves.get(key, ""))  # a unit moved to another file with its code intact (405 T58)
        if was is None:
            out.append((key, "new"))
        elif was.get("code") != row.code and not (qdir is not None and relabeled_only(was, row, qdir.parent.parent)):
            # ...TRIAGED FIRST (feature 385 T116, D133): one edit to `stage_web` re-owed its 20 claims, 17 of them unaffected. Owed in
            # full as before: a claim the triage has named (`touched`), a procedure section's own line (a doc, not code), and a
            # claim whose own text was rewritten (the change is the claim itself)
            text = row.claim.normalized() if row.claim is not None else ""
            full = was.get("triage") == "touched" or row.unit.line_keyed or was.get("claim") not in (None, text)
            out.append((key, "code changed" if full else CODE_TRIAGE))
        elif was.get("triage") == "touched":
            out.append((key, "triage touched"))
        elif row.unit.line_keyed and "section" in was and was["section"] != row.unit.core:
            out.append((key, SECTION_TRIAGE))  # feature 375 FR-002: its own line stands; the rest of its section moved
        elif was.get("research") != row.research:
            out.append(
                (
                    key,
                    research_why(row, was, qdir, store or {}, memo) if qdir is not None else "research changed",
                )
            )
    return out


def moved(cur: Mapping[str, Row], index: Mapping[str, Mapping[str, Any]]) -> dict[str, str]:
    """{new key: old key} for every claim of a unit MOVED to another file with its code intact - a file split into a package
    at the 1,000-line bar (405 T53, T58): the same unit and claim name, the old key gone from the tree, the same code
    fingerprint, and one such row only. Keyed by file, the index otherwise owed every moved claim a full check."""
    gone: dict[str, list[str]] = {}
    for k in index:
        if k not in cur and "::" in k:
            gone.setdefault(k.split("::", 1)[1], []).append(k)
    out: dict[str, str] = {}
    for key, row in cur.items():
        if key in index or "::" not in key:
            continue
        olds = [k for k in gone.get(key.split("::", 1)[1], []) if index[k].get("code") == row.code]
        if len(olds) == 1:
            out[key] = olds[0]
    return out


def rekey(cur: Mapping[str, Row], index: dict[str, dict[str, Any]]) -> int:
    """Carry each moved claim's row to its new key and drop the old one (`moved`); returns how many moved."""
    moves = moved(cur, index)
    for new, old in moves.items():  # copied, then the old keys dropped: a module's NONE shared by the package's every submodule
        index[new] = dict(index[old])
    for old in set(moves.values()):
        index.pop(old, None)
    return len(moves)


def judged(due: Sequence[tuple[str, str]]) -> list[str]:
    """The owed keys `impl-drift` must judge: every owed key but those owed only a triage."""
    return [k for k, why in due if why not in TRIAGED]


def live_rows(cur: dict[str, Row], index: dict[str, dict[str, str]]) -> dict[str, dict[str, str]]:
    """The index rows that still speak of something: a claim in scope, or an UNCLAIMED row whose unit still exists."""
    uids = {r.uid for r in cur.values()}
    return {k: v for k, v in index.items() if k in cur or (v.get("verdict") == "UNCLAIMED" and k.rsplit("#", 1)[0] in uids)}


# ---- the bundle --------------------------------------------------------------------------------------------------


_RESEARCH_BLOCK = re.compile(r"(?ms)^[ \t]*(?:\"\"\"|''')?Research:.*?(?=\"\"\"|'''|^[ \t]*$)")
"""A docstring's `Research:` section, from its `Research:` line to the docstring's close or a blank line."""


def body_of(root: Path, unit: Any) -> str:  # noqa: ANN401
    """A unit's source with its `Research:` section taken out, fingerprinted: what stays the same when only a claim's label
    or citation is rewritten (the round arbiter's tooling fix on ask:t01-claim-labels, feature 385 - three impl-drift rounds
    on T01's claims were about labels alone, each relabel re-owing every claim of its unit)."""
    try:
        text = _source(root, unit)
    except OSError:
        return ""
    return hashlib.sha256(_RESEARCH_BLOCK.sub("", text).encode("utf-8")).hexdigest()[:16]


def relabeled_only(was: Mapping[str, Any], row: Row, root: Path) -> bool:
    """Is a claim whose code fingerprint moved changed in its `Research:` lines alone - the unit's body as last judged - and
    either its own claim text unchanged (another claim of the unit was rewritten) or rewritten after a MISLABELED verdict (the
    relabel that verdict prescribed)? Then it owes no new round. A row recorded before bodies were kept owes one, as before."""
    if not was.get("body") or body_of(root, row.unit) != was["body"]:
        return False
    text = row.claim.normalized() if row.claim is not None else ""
    return was.get("claim") == text or was.get("verdict") == "MISLABELED"


def relabel_answered(was: Mapping[str, Any], row: Row, root: Path) -> bool:
    """A MISLABELED verdict answered by the relabel it prescribed - the claim's text rewritten since, the unit's body the one
    judged - so the gate does not refuse what `owed` no longer asks of it (385 T23, plan D45)."""
    text = row.claim.normalized() if row.claim is not None else ""
    return was.get("verdict") == "MISLABELED" and was.get("claim") not in (None, text) and relabeled_only(was, row, root)


def _source(root: Path, unit: Any) -> str:  # noqa: ANN401
    """A unit's lines, with the comment block directly above it (a constant's why lives there)."""
    return source_span(root, unit)[1]


def source_span(root: Path, unit: Any) -> tuple[int, str]:  # noqa: ANN401
    """(the 1-based line `_source`'s text starts at, the text) - so a bundle can mark the lines a delta changed (405 T36)."""
    lines = (root / unit.path).read_text(encoding="utf-8").split("\n")
    start = unit.lineno - 1
    while start > 0 and lines[start - 1].lstrip().startswith(("#", "@")):
        start -= 1
    end = unit.end_lineno
    if unit.kind == "class":  # its own statements only: each method is a unit of its own, shown under its own heading
        indent = len(lines[unit.lineno - 1]) - len(lines[unit.lineno - 1].lstrip())
        for k in range(unit.lineno, unit.end_lineno):
            st = lines[k].lstrip()
            if st.startswith(("def ", "async def ", "class ", "@")) and len(lines[k]) - len(st) > indent:
                end = k
                break
    if unit.kind == "constant" and end < len(lines) and lines[end].lstrip().startswith(('"""', "'''", '"', "'")):
        while end < len(lines) and lines[end].strip():  # the claim literal after it
            end += 1
    return start + 1, "\n".join(lines[start:end])
