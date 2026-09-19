"""The Mode A type declaration (feature 254): its shape, and that nothing else knows a type by name.

The GM, 2026-09-19: "some of those automated checks will likely just be the same for all types of
buildings ... and some of them may be specific to individual building types. So since this is the
first time that we are adding a second type of diagram ... it would be good for us to think about
the implications of how our code will be structured". The structure is ONE declaration; these tests
hold the engine to it - a tier name typed anywhere else is the five-places-by-hand failure the
declaration exists to end (spec 254 SC-001).
"""

from __future__ import annotations

import json
import os
import re
import subprocess

import pytest

from l7r.diagram.buildings import types as bt

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(os.path.dirname(os.path.dirname(SKILL)))
DECLARATION = os.path.join(SKILL, "l7r", "diagram", "buildings", "types.json")


def _raw() -> list[dict]:
    with open(DECLARATION, encoding="utf-8") as fh:
        return json.load(fh)


def test_both_types_are_declared_with_the_pool_tier_as_the_name() -> None:
    assert bt.tiers() == {"magistracies", "country-shrines"}
    magi = bt.by_tier("magistracies")
    assert magi is not None and magi.hand_drawn and set(magi.generated_exceptions) == {"county-magistracy-example", "ochiba-roundtrip-test"}
    shrine = bt.by_tier("country-shrines")
    assert shrine is not None and shrine.hand_drawn and shrine.generated_exceptions == ()
    assert bt.hand_drawn_tiers() == {"magistracies", "country-shrines"}
    assert bt.by_tier("forts") is None


def test_every_declared_tier_is_a_pool_folder_or_about_to_be() -> None:
    """A declared tier names a folder under `pool/` (the country shrine's is created by its exemplar task)."""
    live = os.path.join(SKILL, "pool")
    present = {d for d in os.listdir(live) if os.path.isdir(os.path.join(live, d))}
    assert "magistracies" in present
    for t in bt.load_types():
        for stem in t.generated_exceptions:
            assert os.path.isfile(os.path.join(live, t.tier, stem, stem + ".gen.py")), f"{t.tier}: generated exception {stem} has no gen"


@pytest.mark.parametrize(
    ("mutate", "message"),
    [
        (lambda d: d[0].pop("checks"), "carries"),
        (lambda d: d[0].__setitem__("tier", "Magistracies"), "kebab"),
        (lambda d: d[0]["required"][0].__setitem__("class", "sort of accurate"), "class must be one of"),
        (lambda d: d[0]["required"][0].__setitem__("band_ft", {"w": [30, 10]}), "min <= max"),
        (lambda d: d[0]["required"][0].__setitem__("band_ft", {"depth": [1, 2]}), "only w, h and area"),
        (lambda d: d[0]["required"].append(dict(d[0]["required"][0])), "ids repeat"),
        (lambda d: d.append(dict(d[0])), "declared twice"),
        (lambda d: d[0]["required"][0].pop("why"), "required item carries"),
        (lambda d: d.clear(), "non-empty list"),
    ],
)
def test_a_malformed_declaration_is_refused_by_name(mutate, message: str) -> None:
    data = _raw()
    mutate(data)
    with pytest.raises(ValueError, match=message):
        bt.parse_types(data)


def test_a_band_holds_either_orientation_and_an_area() -> None:
    band = bt.Band(w=(20.0, 40.0), h=(10.0, 20.0))
    assert band.holds(30, 15) and band.holds(15, 30)
    assert not band.holds(50, 15) and not band.holds(30, 25)
    area = bt.Band(area=(100.0, 200.0))
    assert area.holds(10, 15) and not area.holds(20, 20)
    assert bt.Band().presence_only and bt.Band().holds(1, 1)
    assert not bt.Band(w=(1.0, 2.0), area=(1.0, 2.0)).presence_only


def test_a_form_can_change_or_remove_an_item_band() -> None:
    shrine = bt.by_tier("country-shrines")
    assert shrine is not None
    hall = next(i for i in shrine.required if i.id == "hall")
    dwelling = next(i for i in shrine.required if i.id == "dwelling")
    assert hall.band_for(None) is hall.band and hall.band_for("one roof") is not None and hall.band_for("one roof").area == (2100.0, 3600.0)
    assert dwelling.band_for("two buildings") is dwelling.band and dwelling.band_for("one roof") is None
    assert hall.label.search("Hall and dwelling") and not hall.label.search("village hall")


# --- the census: a type name lives in the declaration and nowhere else in the engine (SC-001) ---

_ENGINE_GLOBS = ("l7r", "scripts")  # the skill's engine and the repository's scripts
_ALLOWED = ("l7r/diagram/buildings/types.json",)  # the declaration


def _engine_files() -> list[str]:
    out: list[str] = []
    for root in (os.path.join(SKILL, "l7r"), os.path.join(REPO, "scripts"), os.path.join(SKILL, "Makefile")):
        if os.path.isfile(root):
            out.append(root)
            continue
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames if d not in ("__pycache__", "fixtures")]
            out += [os.path.join(dirpath, f) for f in filenames if f.endswith((".py", ".json", ".sh"))]
    return out


def test_no_type_name_outside_its_declaration() -> None:
    """Zero hits: the classifier, the index, the ignore rule, the size table and the sweep all DERIVE."""
    names = sorted(bt.tiers())
    pattern = re.compile("|".join(re.escape(n) for n in names))
    hits = []
    for path in _engine_files():
        rel = os.path.relpath(path, SKILL)
        if rel in _ALLOWED:
            continue
        with open(path, encoding="utf-8", errors="replace") as fh:
            for n, line in enumerate(fh, 1):
                if pattern.search(line):
                    hits.append(f"{rel}:{n}: {line.strip()[:80]}")
    assert not hits, "a building type is named outside its declaration - derive it from l7r/diagram/buildings/types.json:\n  " + "\n  ".join(hits)


def test_the_census_fires_on_a_planted_literal(tmp_path, monkeypatch) -> None:
    planted = tmp_path / "planted.py"
    planted.write_text("TIER = 'magistracies'\n")
    monkeypatch.setattr("tests.test_building_types._engine_files", lambda: [str(planted)])
    with pytest.raises(AssertionError, match="planted.py:1"):
        test_no_type_name_outside_its_declaration()


# --- the ignore rule per hand-drawn tier (D3) ---


def test_ignore_file_negates_each_hand_drawn_tier_and_reignores_its_generated_exceptions() -> None:
    with open(os.path.join(REPO, ".gitignore"), encoding="utf-8") as fh:
        lines = [ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")]
    prefix = ".claude/skills/diagram/pool/"
    for t in bt.load_types():
        if t.hand_drawn:
            assert f"!{prefix}{t.tier}/*/*.svg" in lines, f"{t.tier}: hand-drawn source is not un-ignored per tier"
            for stem in t.generated_exceptions:
                assert f"{prefix}{t.tier}/{stem}/{stem}.svg" in lines, f"{t.tier}/{stem}: a generated svg in a hand-drawn tier is re-ignored by name"
    stray = [ln for ln in lines if ln.startswith("!" + prefix) and not any(ln == f"!{prefix}{t.tier}/*/*.svg" for t in bt.load_types() if t.hand_drawn)]
    assert not stray, f"per-file un-ignores under pool/ are the shape this feature retired: {stray}"


def test_git_sees_hand_drawn_source_as_tracked_and_generated_as_ignored() -> None:
    pool = os.path.join(SKILL, "pool")
    for t in bt.load_types():
        if not t.hand_drawn or not os.path.isdir(os.path.join(pool, t.tier)):
            continue
        for stem in sorted(os.listdir(os.path.join(pool, t.tier))):
            svg = os.path.join(pool, t.tier, stem, stem + ".svg")
            if not os.path.isfile(os.path.join(pool, t.tier, stem, stem + ".gen.py")):
                continue
            ignored = subprocess.run(["git", "-C", REPO, "check-ignore", "-q", svg], check=False).returncode == 0
            assert ignored == (stem in t.generated_exceptions), f"{t.tier}/{stem}: svg ignored={ignored}, generated exception={stem in t.generated_exceptions}"
