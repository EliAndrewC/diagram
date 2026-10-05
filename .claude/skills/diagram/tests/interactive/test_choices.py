"""The title card's choices (feature 319, plan D10, FR-004, FR-009, SC-004).

The GM, 2026-10-03, on Inashiro: what was chosen for a settlement belongs on its title card, each value opening its own modal,
so every feature modal can be the same on every map (*"standardized set of modals ... not ... customized modals. For
anything"*)."""

from __future__ import annotations

import glob
import json
import os

from l7r.diagram.interactive import choices, conditions
from l7r.diagram.interactive.classes import PLACE
from l7r.diagram.interactive.notes import MapNotes
from l7r.diagram.interactive.page import render_page

SKILL = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
POOL_HAMLETS = sorted(p for p in glob.glob(os.path.join(SKILL, "pool", "hamlets", "*", "*.json")) if os.path.basename(p)[:-5] == os.path.basename(os.path.dirname(p)))


def _metas() -> list[dict]:
    out = []
    for path in POOL_HAMLETS:
        with open(path, encoding="utf-8") as fh:
            out.append(json.load(fh).get("meta", {}))
    return out


def test_the_table_holds_every_knob_every_value_and_every_value_a_pool_map_records() -> None:
    """Plan D10: no knob left off the card; a value the registry or a manifest gives is in the table with a label."""
    keys = {e["key"]: e for e in choices.table()}
    for knob, values in conditions.knobs().items():
        assert knob in keys, f"knob {knob!r} is not in assets/choices.json - add it with a name and a label per value"
        missing = [v for v in values if v not in keys[knob]["values"]]
        assert not missing, f"{knob}: values {missing} have no label in assets/choices.json"
    assert POOL_HAMLETS, "the pool's hamlets are found"
    for meta in _metas():
        for key, entry in keys.items():
            if key in meta and meta[key] is not None:
                assert str(meta[key]) in entry["values"], f"{meta.get('name')}: {key}={meta[key]!r} has no label in assets/choices.json"


def test_every_value_has_its_modal_in_the_about_form() -> None:
    """FR-009: each value opens a standardized modal; a degree along a continuum opens one modal for the knob."""
    for entry in choices.table():
        for value in entry["values"]:
            path = choices.modal_file(entry, value)
            assert os.path.isfile(path), f"no modal {os.path.relpath(path, SKILL)} - write it in the About form (dev/modals.md)"
            fc = choices.modal(entry, value)
            assert fc is not None and fc.about, f"{os.path.relpath(path, SKILL)} is not in the About form"


def test_the_card_lists_the_map_s_choices_each_opening_its_modal() -> None:
    """US4's independent test: Inashiro's card lists its choices, among them the clustered form, and the value opens its modal."""
    meta = {"scale": "hamlet", "name": "Inashiro", "households": 15, "settlement_form": "nucleated", "byre_form": "detached_commons", "family_form": "retirement_house", "retirement_houses": 10}
    made = choices.made(meta)
    names = [c["name"] for c in made]
    assert names.index("How the houses stand") < names.index("Where the old couple lives"), "in the table's order"
    form = next(c for c in made if c["name"] == "How the houses stand")
    assert form["value"] == "clustered together" and form["k"] == "choice:settlement_form=nucleated"
    page = render_page([], [], "Inashiro", meta)
    blob = json.loads(page.split('<script id="classes" type="application/json">')[1].split("</script>")[0].replace("<\\/", "</"))["classes"]
    card = blob[PLACE]
    assert card["choices"] == made and "choice:settlement_form=nucleated" in blob, "the value's modal rides in the page's data"
    assert "10 of Inashiro's 15 homesteads have a retirement house." in card["facts"]


def test_a_hamlet_page_reads_no_features_block_and_writes_no_per_map_sentence_into_a_feature_modal() -> None:
    """FR-004, SC-004: a hamlet's feature modals are the same on every map; its own facts are the card's."""
    rect = '<rect x="0" y="0" width="10" height="10"/>'
    notes = MapNotes(place={}, features={"farmhouse": "A fact about this map's farmhouses."})
    page = render_page([rect], ["farmhouse"], "T", {"scale": "hamlet", "name": "T"}, notes=notes)
    assert "A fact about this map" not in page
    other = render_page([rect], ["farmhouse"], "T", {"scale": "town", "name": "T"}, notes=notes)
    assert "A fact about this map" in other, "a tier not yet standardized keeps its notes"


def test_every_per_settlement_roll_is_a_choice_or_accounted_for() -> None:
    """The plan review of D10: a hamlet picks forms from its seed that no knob registers (the row's line, a scattered farm's
    water, the manure's form ...); each is on the card or named in `not_choices` with why it is not a choice."""
    import re

    rolled: set[str] = set()
    for tree in ("hamletgen", "settlement"):
        for path in glob.glob(os.path.join(SKILL, "l7r", "diagram", tree, "**", "*.py"), recursive=True):
            with open(path, encoding="utf-8") as fh:
                # every spelling of the seed: `spec.seed`, `plan.spec.seed`, `s.seed`, `self.seed`, a bare `seed` (the plan
                # review of D10, round 2: the narrower pattern missed 17 sites)
                rolled |= set(re.findall(r'(?:_roll|knob_rng)\([\w.]*seed, "([a-z_]+)"', fh.read()))
    assert {"manure_form", "row_line", "grove_sides", "house_bearing", "grove_flank"} <= rolled, "the roll sites are found"
    known = {e["key"] for e in choices.table()} | set(choices.not_choices())
    missing = sorted(rolled - known)
    assert not missing, f"rolled per settlement but neither a choice in assets/choices.json nor in its not_choices: {missing}"


COMB_ONLY = ("grain_drift", "intake", "plot_size")


def test_every_choice_a_hamlet_rolls_reaches_its_map_s_meta() -> None:
    """The plan review of D10, round 2: the card lists only what a map's `meta` records, so a choice the hamlet plan rolls
    and the map never records (`water_sink`, `grain_drift` before this test) is a choice no card could show. Every pool
    hamlet records each rolled choice the table holds, wherever the choice applies to it. The one exception, with why:
    `grain_drift`, `intake` and `plot_size` are read only on a COMB field (`hamletgen/water/comb.py` `stage_field` hands a polder to
    `stage_polder` before any of them), so a polder records none of the three."""
    import re

    with open(os.path.join(SKILL, "l7r", "diagram", "hamletgen", "plan.py"), encoding="utf-8") as fh:
        rolled = set(re.findall(r'_roll\(spec\.seed, "([a-z_]+)"', fh.read()))
    table = {e["key"]: e for e in choices.table()}
    owed = sorted(rolled & set(table))
    assert {"water_sink", "grain_drift", "manure_form"} <= set(owed), "the plan's roll sites are found"
    for meta in _metas():
        polder = meta.get("field_archetype") in ("polder_grid", "mulberry_dike_fishpond")
        missing = [k for k in owed if choices.applies(table[k], meta) and meta.get(k) is None and not (k in COMB_ONLY and polder)]
        assert not missing, f"{meta.get('name')}: rolled but not recorded in meta: {missing} - write `s.M['meta'][<key>]` where the value is settled"


def test_a_choice_of_one_settlement_form_is_not_listed_on_another() -> None:
    """A clustered map records a row village's choices too; its card lists only the choices its settlement made."""
    near = choices.made({"settlement_form": "nucleated", "row_line": "street", "copse_siting": "among_the_houses"})
    row = choices.made({"settlement_form": "linear", "row_line": "street", "copse_siting": "among_the_houses"})
    assert "What the row follows" not in [c["name"] for c in near] and "What the row follows" in [c["name"] for c in row]
    assert "Where the village's trees stand" in [c["name"] for c in near] and "Where the village's trees stand" not in [c["name"] for c in row]


def test_a_value_whose_modal_is_not_written_opens_none() -> None:
    """The card lists a value with no modal file by its label and an empty key (`made`), so a gap shows rather than breaks."""
    entry = {"key": "no_such_choice", "name": "None", "values": {"x": "x"}}
    assert choices.modal(entry, "x") is None
    assert choices.made({"no_such_choice": "x"}) == [] and choices.registry_for({"no_such_choice": "x"}) == {}, "not in the table"
