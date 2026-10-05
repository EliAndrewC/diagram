"""The farmstead and what stands on it - the dwelling, its outbuildings, its yards and fixtures.

Each class's modal text is its own file, `assets/modals/hamlet/<slug of its key>.md`, in the About form (feature 319),
parsed by `_base.parse_explanation`. Edit the file and the page changes; the gate does not re-open.

Research: modal explanation - NONE: the explanation's research is its Entry:, checked by entry-drift
"""

from __future__ import annotations

from ._base import Kind


# The GM's ruling: a farmhouse's work yard and garden beds always line up with their house.
class Farmhouse(Kind):
    key = 'farmhouse'


class StorageShed(Kind):
    key = 'storage shed'


class Byre(Kind):
    key = 'byre'


class RetirementHouse(Kind):
    key = 'retirement house'


class ThreshingYard(Kind):
    key = 'threshing yard'


class Garden(Kind):
    key = 'garden'


class Privy(Kind):
    key = 'privy'


class WoodShed(Kind):
    key = 'wood shed'


class ManureHeap(Kind):
    key = 'manure heap'


class BathRoom(Kind):
    key = 'bath room'


class HenCoop(Kind):
    key = 'hen coop'


# The GM's ruling: the old-families pattern for household shrines (rare, notable when it appears; three to
# eight households in a hundred), over the every-house pattern of other regions.
class HouseholdShrine(Kind):
    key = 'household shrine'


class Persimmon(Kind):
    key = 'persimmon'


class BurialGround(Kind):
    key = 'burial ground'
