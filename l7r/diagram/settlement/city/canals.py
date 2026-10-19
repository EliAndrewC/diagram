"""Water carried for transport and irrigation rather than defense, and the farmland ring it feeds.

Split from settlement/city.py by feature 113 - see settlement/city/CLAUDE.md for the index.

Research: plumbing - NONE
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..core import Settlement


"""Research: sluice standoff - research/questions/0146-moats-where-their-water-comes-from-and-where-it-goes-hori.drawing.html: each tap stands about 90 ft outside the moat's rim"""


class CanalsMixin:
    def canal(self: Settlement, pts: Any, width: float | None = None, flow: str = "level") -> float:  # type: ignore[misc]
        """A navigable CARGO CANAL - the one way water legitimately enters a walled city (through
        a water gate; the trunk river never does - the Kaifeng lesson). A middle tier on the
        water-width ladder: clearly heavier than an irrigation hairline, clearly lighter than the
        moat/river. Drawn through the shared water block (it merges with the moat/river/dock and
        passes UNDER the rampart at the gate); records M['canals'] + a no-build corridor.

        Research:
            canal width - research/questions/0178-city-canals-horikawa.drawing.html: a 36 ft poling barge canal
            place on the width ladder - research/questions/0068-how-wide-canals-and-ditches-are-the-ladder-of-channel-widths.drawing.html: heavier than a ditch, lighter than the moat
            canal stroke and sheen - CONVENTION
            no-build corridor - research/questions/0058-ground-too-wet-to-build-on.drawing.html: about 33 ft of a centerline; half the width plus 16 px kept clear of buildings
        """
        if width is None:
            width = self.px(36)  # a poling barge canal ~36 ft
        dd = 'M' + ' L'.join(f'{x:.1f},{y:.1f}' for x, y in pts)
        rec = {"poly": [[round(x, 1), round(y, 1)] for x, y in pts], "w": width}
        self._flow_record(rec, pts, flow)
        self.M.setdefault("canals", []).append(rec)
        self._water(
            f'<path d="{dd}" fill="none" stroke="#9CB4C8" stroke-width="{width}" stroke-linejoin="round" stroke-linecap="round"/>',
            rec,
            sheen=f'<path d="{dd}" fill="none" stroke="#B6CAD8" stroke-width="{max(2, width * 0.35):.0f}" stroke-linejoin="round" stroke-linecap="round"/>',
        )
        self.corridors.append(([(x, y) for x, y in pts], width / 2 + 16))
        return width
