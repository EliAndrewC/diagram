"""The field fabric - paddy and its bunds, the dry crops on the hem, and fallow.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:` - parsed by
`_base.parse_explanation` (feature 189). Edit the prose here and the page changes; the gate does not re-open.

Research: modal explanation - NONE: the explanation's research is its Entry:, checked by entry-drift
"""

from __future__ import annotations

from ._base import Kind


class Paddy(Kind):
    key = 'paddy'


class WetPaddy(Kind):
    key = 'wet paddy'


class Bund(Kind):
    key = 'bund'


class BundBeans(Kind):
    key = 'bund beans'


class Millet(Kind):
    key = 'millet'


class Buckwheat(Kind):
    key = 'buckwheat'


class Barley(Kind):
    key = 'barley'


class Soy(Kind):
    key = 'soy'


class Fallow(Kind):
    key = 'fallow'


class Holding(Kind):
    key = 'farm holding'
