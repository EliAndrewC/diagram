"""STAGE 6c (feature 273, the GM 2026-09-27; feature 280 M68): where a hamlet's dead lie - in the village's ground.

The GM ruled that a village district's main village alone keeps the shrine, the headman's house and the cremation
ground, and asked where a hamlet's dead then lie - its own ground, the village's, or bones brought home - to follow
the history where it agrees and to roll a knob where it does not. Feature 273 rolled `hamlet_burial` between a ground
at the hamlet's edge and none. Feature 280 (research/religion-and-death/155, M68) searched for the hamlet's own ground
before modern times: a settlement's own graveyard is attested at the end of the Edo period as ONE form among an
individual's, a lineage's and a temple's, and the dead went more often to temple graves; that EVERY hamlet kept a
ground of its own rests only on twentieth-century folklore records and surveys - an undated record of custom, which
spec 280 D1 counts as modern (`undated-custom`), and by the GM's ruling of 2026-09-28 a form attested only in modern
times is not drawn. So the knob keeps its one attested value: the hamlet's dead lie in the village's ground (or its
temple's), off the map, and the hamlet draws none. If the GM re-sorts the undated records as premodern, the own ground
returns as the knob's second value - its sizing and seat were the record's band (750-2,450 sq ft) and the shared edge
seat (`settlement/civic_grounds/edge_seat.py`), which the village's cremation ground still uses.
"""

from __future__ import annotations

from l7r.diagram.settlement import Settlement

from .plan import SitePlan

BURIAL_FORMS = ("village_ground",)  # the one attested form (feature 280 M68): the hamlet's dead lie in the village's ground


def stage_burial(s: Settlement, plan: SitePlan) -> None:
    """Where the hamlet's dead lie: in the village's ground, off the map (feature 280 M68).

    Records `meta.hamlet_burial` on a hamlet, so a map says where its dead lie; a pinned value must be an attested one.
    Nothing is drawn - the village's ground lies with the main village, and the hamlet's own ground is attested only in
    twentieth-century records (research/religion-and-death/155).

    Steps:
        l7r.diagram.hamletgen.burial.stage_burial
    """
    if not s.M.get("houses") or s.M["meta"].get("scale") != "hamlet":
        return
    form = s.knob_pins.get("hamlet_burial") or BURIAL_FORMS[0]
    if form not in BURIAL_FORMS:
        raise ValueError(f"hamlet_burial: {form!r} is not one of {BURIAL_FORMS} (feature 280 M68: a hamlet's own ground is attested only in modern records)")
    s.M["meta"]["hamlet_burial"] = form
