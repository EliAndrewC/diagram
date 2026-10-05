"""The planted and the wild green - bamboo, the windbreak, copses, the commons, scrub and marsh.

Each class's modal text is its own file, `assets/modals/hamlet/<slug of its key>.md`, in the About form (feature 319),
parsed by `_base.parse_explanation`. Edit the file and the page changes; the gate does not re-open.

Research: modal explanation - NONE: the explanation's research is its Entry:, checked by entry-drift
"""

from __future__ import annotations

from ._base import Kind


class HomesteadBamboo(Kind):
    key = 'homestead bamboo'


class SharedBambooGrove(Kind):
    key = 'shared bamboo grove'


# The GM's rulings: the maps show the regional northwesterly winter wind unless a place declares its own.
class Windbreak(Kind):
    key = 'windbreak'


class HomesteadGrove(Kind):
    key = 'homestead grove'


class Alder(Kind):
    key = 'alder'


# The GM's correction: the copse's fruit trees and bamboo fill the gaps throughout the cluster.
class Copse(Kind):
    key = 'copse'


class WoodlandCommons(Kind):
    key = 'woodland commons'


# The GM's ruling: an irrigation channel's bank keeps scrub off by the same 6 ft as a bund.
class ScrubAndRoughGrazing(Kind):
    key = 'scrub and rough grazing'


class Marsh(Kind):
    key = 'marsh'
