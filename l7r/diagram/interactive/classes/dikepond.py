"""The dike-pond hamlet (feature 150, Kuwabata) - ponds, planted dikes, the polder's sluice gates, the stock and the enclosing dike.

Each class's modal text is its own file, `assets/modals/hamlet/<slug of its key>.md`, in the About form (feature 319),
parsed by `_base.parse_explanation`. Edit the file and the page changes; the gate does not re-open.

Research: modal explanation - NONE: the explanation's research is its Entry:, checked by entry-drift
"""

from __future__ import annotations

from ._base import Kind


# ---- the dike-pond hamlet (feature 150, Kuwabata - the first scripted mulberry_dike_fishpond) ----
class FishPond(Kind):
    key = 'fish pond'


# The GM's ruling: the mulberry crowns keep the premodern (late-Qing) spacing, about one bush per 24 sq ft.
class MulberryDike(Kind):
    key = 'mulberry dike'


class PondCanal(Kind):
    key = 'pond canal'


class FruitDike(Kind):
    key = 'fruit dike'


class TeaDike(Kind):
    key = 'tea dike'


class PigSty(Kind):
    key = 'pig sty'


class FryPond(Kind):
    key = 'fry pond'


class ManurePit(Kind):
    key = 'manure pit'


class SluiceGate(Kind):
    key = 'sluice gate'


class PerimeterDike(Kind):
    key = 'perimeter dike'
