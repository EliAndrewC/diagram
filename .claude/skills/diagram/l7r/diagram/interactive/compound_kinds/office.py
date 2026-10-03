"""The office and its works - the hall and the bench, the clerks, the stores, the cell, the watch, the tally.

Each class's DOCSTRING is its explanation - `What:`, `Why:`, `Note:`, optional `Caveat:`, then the data tags -
parsed by `..classes._base.parse_explanation` (feature 189). Every kind is written FROM the existing record
(feature 262, FR-005): the sections its `Entry:` names, and the `buildings/types.json` program item folded into
it where there is one - the item's class and why are carried here, not re-decided: a size band the item calls a
guess is the kind's caveat (office hall, barracks), and a presence-only item's class is the kind's label (clerks'
room, gatehouse). The measurement behind each label is `specs/262-interactive-magistracy-pages/coverage.md`.
"""

from __future__ import annotations

from ..classes import Kind


class OfficeHall(Kind):
    key = "office hall"


class MagistratesDais(Kind):
    key = "magistrate's dais"


class ClerksRoom(Kind):
    key = "clerks' room"


class TaxArchive(Kind):
    key = "tax archive"


class Granary(Kind):
    key = "granary"


class Cell(Kind):
    key = "cell"


class Gatehouse(Kind):
    key = "gatehouse"


class Barracks(Kind):
    key = "barracks"


class BenchNoticeBoard(Kind):
    key = "notice board"


class TallyOffice(Kind):
    key = "tally office"


class WeighingFloor(Kind):
    key = "weighing floor"


# ---- the parts of the office (feature 264: a thing drawn inside a feature is its own kind) ----------------------


class DayOffice(Kind):
    key = "day office"


class OfficialStudy(Kind):
    key = "official study"


class ClerksSeats(Kind):
    key = "clerks' seats"


class KneelingPositions(Kind):
    key = "kneeling positions"


class GranaryStilts(Kind):
    key = "granary stilts"
