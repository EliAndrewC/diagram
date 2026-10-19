"""Institutional and commercial works: what a domain builds because it administers and trades,
as opposed to what its inhabitants build in order to live.

Split from settlement/civic_grounds.py by feature 115 - see settlement/civic_grounds/CLAUDE.md for the index.

Research: plumbing - NONE
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core import Settlement


class CivicWorksMixin:
    def district(self: Settlement, name: str, kind: str, poly: Any, rank_band: str | None = None) -> None:  # type: ignore[misc]
        """A declared fabric DISTRICT (feature 021): a named placement region for the housing
        packs and the ground truth for capital_rank_gradient. A declarative overlay like
        quarter() - draws nothing and reserves nothing; the packs it names do the drawing.
        Records M['districts'] {name, kind, poly, rank_band?}; kinds: yashiki, detached,
        terrace, machi, monzen, entertainment.

        Research: district overlay - NONE: draws and reserves nothing
        """
        rec: dict[str, Any] = {"name": name, "kind": kind, "poly": [list(p) for p in poly]}
        if rank_band is not None:
            rec["rank_band"] = rank_band
        self.M.setdefault("districts", []).append(rec)
