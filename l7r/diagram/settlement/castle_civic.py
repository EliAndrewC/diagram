"""Split from settlement.py by feature 025 - see settlement/CLAUDE.md for the index.

Research: civic drawing plumbing - NONE
"""

from collections.abc import Sequence
from typing import TYPE_CHECKING

from ..labels import Subject
from ..labels.geom import rect

if TYPE_CHECKING:
    from .core import Settlement


"""Research: honmaru size - research/questions/0139-the-castle-in-a-capital-where-it-sits-how-big-it-is-and-its-gates-shiro.drawing.html: about 2 ha (Nijo's honmaru about 150 m on a side, Hiroshima's upper honmaru about 2.2 ha)"""


"""Research: hall size - research/questions/0165-martial-training-grounds-and-dojo.drawing.html: one long building about 124 x 35 ft"""

"""Research: martial hall compound - research/questions/0165-martial-training-grounds-and-dojo.html: a master's practice hall at his own house was the private dojo's form - the master's house is drawn inside the martial hall's compound, a departure the code keeps until feature 417 T35; the size and the hall across the north are ours; 130 x 124 ft, the hall across its north, the master's house and the archery lane south of it"""


class CastleCivicMixin:
    """A hand-placed caption request - what is left of the castle and civic-building mixin after
    feature 392 retired the town and city drawing only the frozen legacy maps called.

    Research: mixin plumbing - NONE: the caption request carries its own claims
    """

    def place_caption(  # type: ignore[misc]
        self: Settlement,
        text: str,
        box: Sequence[float] | None,
        size: float = 9,
        italic: bool = True,
        weight: str = "normal",
        color: str = "#5A4326",
        rot: float = 0.0,
    ) -> None:
        """Caption the feature occupying `box` - seated in the label phase by the ONE placer (feature 266) as a POINT
        subject: the feature's box turned by `rot`, the caption beside it at the standard's first free ranked position.
        Use this instead of a hand-picked `s.label(x, y, ...)` whenever the caption names a specific feature. Records the
        subject box on the label so `label_hugs_its_referent` can measure the finished gap.

        `box` accepts None: a None means the subject placed nothing, and captioning it is a gen-script bug, not something
        to draw.

        DEFERRED to the label phase: seating a caption at call time judges it against half a map (Tango's north gate
        market caption took the flank that later filled with the execution ground).

        Research: caption seat - CONVENTION: the one placer's ranked positions"""
        if box is None:
            raise ValueError(f"place_caption({text!r}) got no subject box - the feature it names placed nothing")
        x0, y0, x1, y1 = (float(v) for v in box)
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        subject = Subject("point", tuple(rect(cx, cy, (x1 - x0) / 2, (y1 - y0) / 2, rot)), angle=rot)
        self._captions.append((text, subject, size, italic, weight, color))
