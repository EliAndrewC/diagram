"""Items of a modal that depend on the settlement's knobs (feature 319, FR-015, SC-009, plan D14). The GM, 2026-10-05: *"Could
we make that kind of item still automatic but dependent on the "knobs" for a settlement in cases where that is relevant?"*"""

from __future__ import annotations

import pytest

from l7r.diagram.interactive import conditions
from l7r.diagram.interactive.page import explanations

NUCLEATED = {"settlement_form": "nucleated"}
DISPERSED = {"settlement_form": "dispersed"}


def test_a_condition_is_read_off_the_item_and_held_against_the_map() -> None:
    assert conditions.split("[settlement_form=nucleated|linear] A guess.") == (("settlement_form", ("nucleated", "linear")), "A guess.")
    assert conditions.split("A plain guess.") == (None, "A plain guess.")
    assert conditions.shown(["[settlement_form=nucleated] Only here.", "Everywhere."], NUCLEATED) == ["Only here.", "Everywhere."]
    assert conditions.shown(["[settlement_form=nucleated] Only here.", "Everywhere."], DISPERSED) == ["Everywhere."]
    assert conditions.shown(["[settlement_form=nucleated] Only here."], {}) == [], "a map recording no value shows none of the knob's items"
    assert conditions.label(("settlement_form", ("nucleated", "linear"))) == "(only where settlement_form is nucleated or linear)"


def test_a_malformed_condition_is_refused_rather_than_shown() -> None:
    with pytest.raises(ValueError, match=r"written \[knob=value\]"):
        conditions.split("[Settlement Form = nucleated] A guess.")


def test_an_entry_path_with_a_condition_is_dropped_where_it_fails() -> None:
    entry = "research/questions/0072-a.html, research/questions/0031-b.html [settlement_form=nucleated]"
    assert conditions.strip_entry(entry) == "research/questions/0072-a.html, research/questions/0031-b.html"
    assert conditions.shown_entry(entry, NUCLEATED) == "research/questions/0072-a.html, research/questions/0031-b.html"
    assert conditions.shown_entry(entry, DISPERSED) == "research/questions/0072-a.html"


def test_an_unknown_knob_or_value_is_refused_with_the_registry_s_words() -> None:
    assert "nucleated" in conditions.knobs()["settlement_form"], "the populated registry"
    conditions.check("x", [None, ("settlement_form", ("nucleated",))])
    with pytest.raises(ValueError, match="names no registered knob"):
        conditions.check("x", [("settlement_shape", ("nucleated",))])
    with pytest.raises(ValueError, match=r"\['clustered'\] not among settlement_form's forms"):
        conditions.check("x", [("settlement_form", ("clustered",))])


def test_the_windbreak_s_shared_wood_guess_and_its_question_show_only_on_a_clustered_map() -> None:
    """SC-009, the GM's own case: on a nucleated map the guess and the question it alone rests on (0031) are there; on a
    dispersed map neither is, and the rest of the modal is the same."""
    near, apart = explanations({"windbreak"}, meta=NUCLEATED)["windbreak"], explanations({"windbreak"}, meta=DISPERSED)["windbreak"]
    shared = [g for g in near["guesses"] if g.startswith("That a clustered village sheltered")]
    assert shared and not shared[0].startswith("["), "shown, its condition removed"
    assert not any(g.startswith("That a clustered village sheltered") for g in apart["guesses"])
    clustered = [q for q in near["questions"] if "clustered-and-scattered-villages" in q["url"]]
    assert clustered and not any("clustered-and-scattered-villages" in q["url"] for q in apart["questions"])
    assert near["about"] == apart["about"] and near["depiction"] == apart["depiction"], "only the conditioned items differ"
    assert len(apart["questions"]) == len(near["questions"]) - 1
