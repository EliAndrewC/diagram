"""`scripts/reviews/review_owed.py` and `scripts/reviews/review_snapshot.py` - the scripted answer to "which review checks are owed",
keyed on OCCASIONS (feature 294), and the reviewer's per-unit snapshot (features 231, 248).

Every case runs on a real git fixture in `tmp_path`: a repository with both pool trees, an `origin/main` ref, Mode B maps
carrying an `ink_classes` census and a Mode A sheet carrying `data-kind`s, changed in the ways a session changes them. The
cases include the spec's replays: an engine change moving every manifest owes nothing (SC-001); one element new to a map, a
declared redraw, a declared re-placement (the GM's tannery) and a new element drawn with an existing mark each owe exactly
one glyph check (SC-002).
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import pytest

from tests._scripts import script

REPO = Path(__file__).resolve().parents[2]


def _mod(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script(name))
    assert spec and spec.loader
    m = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = m
    spec.loader.exec_module(m)
    return m


owed = _mod("_review_owed")
snap = _mod("_review_snapshot")


def git(root: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=True).stdout.strip()


def _map(root: Path, tree: str, name: str, classes: dict[str, int], *, poly: int = 1, renders: bool = False) -> Path:
    d = root / tree / "hamlets" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.json").write_text(json.dumps({"meta": {"name": name}, "houses": [[poly, poly]], "ink_classes": classes}))
    (d / f"{name}.notes.md").write_text(f"# {name}\n")
    if renders:
        (d / f"{name}.svg").write_text("<svg/>")
        (d / f"{name}.png").write_bytes(b"\x89PNG")
        (d / f"{name}.html").write_text("<html></html>")
    return d


def _sheet(root: Path, name: str, kinds: list[str]) -> Path:
    d = root / "pool" / "magistracies" / name
    d.mkdir(parents=True, exist_ok=True)
    (d / f"{name}.gen.py").write_text("# sheet\n")
    (d / f"{name}.svg").write_text("<svg>" + "".join(f'<rect data-kind="{k}"/>' for k in kinds) + "</svg>")
    (d / f"{name}.notes.md").write_text(f"# {name}\n")
    return d


def _tasks(root: Path, occasions: list[str] | None) -> None:
    d = root / "specs" / "999-test"
    d.mkdir(parents=True, exist_ok=True)
    body = "# Tasks\n\n" + ("## Occasions\n\n" + "".join(f"- {o}\n" for o in occasions) + "\n" if occasions is not None else "")
    (d / "tasks.md").write_text(body + "## Setup\n\n- [ ] T01 a task\n      research: rendering\n")
    (root / ".specify").mkdir(exist_ok=True)
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/999-test"}))


@pytest.fixture
def clone(tmp_path: Path) -> Path:
    """Two shipped hamlets and a legacy map, one Mode A sheet, and an `origin/main` at that commit."""
    root = tmp_path / "clone"
    root.mkdir()
    git(root.parent, "init", "-q", str(root))
    git(root, "config", "user.email", "t@t")
    git(root, "config", "user.name", "t")
    _map(root, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "-": 2}, renders=True)
    _map(root, "pool", "sawada", {"farmhouse": 7, "wood shed": 3})
    _map(root, "legacy-hand-authored-pool", "furu", {})
    _sheet(root, "hayakawa", ["residence", "kitchen"])
    (root / "l7r").mkdir(parents=True)
    (root / "l7r" / "engine.py").write_text("X = 1\n")
    git(root, "add", "-A")
    git(root, "commit", "-qm", "the pool")
    git(root, "update-ref", "refs/remotes/origin/main", git(root, "rev-parse", "HEAD"))
    return root


def units(root: Path) -> list[tuple[str, str, str]]:
    _, got, problems = owed.owed(root, landing=True)  # what is OWED; when a glyph unit is DUE is amendment 9's, below
    assert not problems, problems
    return [(u.check, u.subject, u.on) for u in got]


def test_nothing_changed_owes_nothing(clone: Path) -> None:
    desc, got, _ = owed.owed(clone, landing=True)
    assert got == []
    assert "no review owed" in owed.ruling(desc, got)


def test_an_engine_change_moving_every_manifest_owes_nothing(clone: Path) -> None:
    """SC-001: the shared engine change - every manifest moved, nothing new drawn - owes zero review runs."""
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4}, poly=2, renders=True)
    _map(clone, "pool", "sawada", {"farmhouse": 7, "wood shed": 3}, poly=2)
    (clone / "l7r" / "engine.py").write_text("X = 2\n")
    _tasks(clone, ["none: a speed lever, every element placed under rules already judged"])
    assert units(clone) == []
    assert owed.check_declared(clone) is None


def test_an_element_new_to_a_map_owes_one_glyph_check_on_that_map(clone: Path) -> None:
    """SC-002: the occasion is an element new to the MAP - here the wood shed, which Sawada already draws."""
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "wood shed": 2}, renders=True)
    assert units(clone) == [("glyph-check", "wood shed", "inashiro")]


def test_a_new_element_with_an_existing_mark_still_owes_the_glyph_check(clone: Path) -> None:
    """A new class key drawn with an existing glyph is an element new to the map whatever its mark (round 1's ruling)."""
    _map(clone, "pool", "sawada", {"farmhouse": 7, "wood shed": 3, "storage shed": 1})
    assert units(clone) == [("glyph-check", "storage shed", "sawada")]


def test_one_element_new_to_two_maps_is_one_unit(clone: Path) -> None:
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "byre": 1}, renders=True)
    _map(clone, "pool", "sawada", {"farmhouse": 7, "wood shed": 3, "byre": 2})
    assert units(clone) == [("glyph-check", "byre", "inashiro")]


def test_a_declared_redraw_owes_the_glyph_check_where_the_element_is_drawn(clone: Path) -> None:
    _tasks(clone, ["glyph-redrawn: privy"])
    assert units(clone) == [("glyph-check", "privy", "inashiro")]


def test_a_declared_re_placement_owes_the_glyph_check(clone: Path) -> None:
    """The GM's tannery: the same mark, placed by substantially different rules."""
    _tasks(clone, ["placement-changed: wood shed - now seated off the gable"])
    assert units(clone) == [("glyph-check", "wood shed", "sawada")]


def test_a_declared_re_placement_on_a_named_map_owes_the_glyph_check_there(clone: Path) -> None:
    """`<class> on <map>`: the map the change moved, not the first that draws the class (feature 328 wave 5: every way is
    inked `village lane`, and a row street re-placed on Kashikawa was owed a review of Inashiro's)."""
    _tasks(clone, ["placement-changed: wood shed on sawada - now seated off the gable"])
    assert units(clone) == [("glyph-check", "wood shed", "sawada")]


def test_a_declared_element_not_on_the_named_map_is_a_problem(clone: Path) -> None:
    _tasks(clone, ["placement-changed: wood shed on inashiro"])
    _, _, problems = owed.owed(clone)
    assert problems == ["specs/999-test: placement-changed: 'wood shed' is not drawn on 'inashiro'"]


def test_a_declared_element_no_map_draws_is_a_problem(clone: Path) -> None:
    _tasks(clone, ["glyph-redrawn: tannery"])
    _, got, problems = owed.owed(clone, landing=True)
    assert [u.subject for u in got] == ["tannery"]
    assert "drawn on no pool map" in problems[0]
    assert "PROBLEMS" in owed.ruling("x", got, problems)


def test_an_unknown_occasion_is_a_problem(clone: Path) -> None:
    _tasks(clone, ["repainted: privy"])
    _, got, problems = owed.owed(clone, landing=True)
    assert got == [] and "unknown occasion" in problems[0]


@pytest.mark.parametrize(
    ("line", "expected"),
    [
        ("new-form: sawada", [("settlement-review", "sawada", "sawada")]),
        ("new-tier: sawada", [("settlement-review", "sawada", "sawada")]),
        ("layout-revised: hayakawa", [("building-review", "hayakawa", "hayakawa")]),
        ("new-program: ochaya hayakawa", [("building-review", "hayakawa", "hayakawa"), ("size-audit", "ochaya", "hayakawa")]),
        ("gm-fix: inashiro - the board under the canopy", [("fix-check", "inashiro", "inashiro")]),
    ],
)
def test_each_declared_occasion_owes_its_check(clone: Path, line: str, expected: list[tuple[str, str, str]]) -> None:
    _tasks(clone, [line])
    assert units(clone) == expected


def test_a_review_is_told_what_each_declared_wave_changed_and_files_the_rest(clone: Path) -> None:
    """Feature 374 batch 6, the round arbiter's tooling fix (ask:b6-ochiba-r3): a third building-review round judged a
    garden no wave had moved. The occasion carries every declared wave's text, merged into the one unit the lines
    collapse into, and the building-review prompt files a finding outside it as a row, never as the unit's verdict."""
    _tasks(clone, ["layout-revised: hayakawa - wave 1: the gate posts 2 ft", "layout-revised: hayakawa - wave 2: the wells' gear"])
    _, got, _ = owed.owed(clone, landing=True)
    (unit,) = [u for u in got if u.check == "building-review"]
    assert unit.occasion.endswith(": wave 1: the gate posts 2 ft; wave 2: the wells' gear"), unit.occasion
    text = snap.dispatch_text({"unit": unit.slug, "check": unit.check, "subject": unit.subject, "on": unit.on, "occasion": unit.occasion, "clone": None, "main": None, "missing": []}, clone, "k")
    assert "wave 2: the wells' gear" in text and "severity `outside`" in text and "judge the verdict on the change alone" in text


def test_a_map_new_to_the_pool_owes_the_whole_map_review_and_only_elements_new_to_the_legend(clone: Path) -> None:
    _map(clone, "pool", "kuwabata", {"farmhouse": 5, "privy": 2, "fish pond": 3})
    assert units(clone) == [("settlement-review", "kuwabata", "kuwabata"), ("glyph-check", "fish pond", "kuwabata")]


def test_a_pool_folder_the_delta_only_moved_owes_no_review(clone: Path) -> None:
    """Feature 329: a map or sheet folder renamed by the delta - its tracked files' bytes stood at the base - is not new to
    the pool, though its path did not exist there. The whole project's move read every map and sheet as new."""
    git(clone, "mv", "pool/hamlets", "pool/villages")  # every map folder at a path the base never had, its files unchanged
    assert {d.name for d in owed._folders(clone)} >= {"inashiro", "sawada"}, "the moved folders are still scanned"
    assert units(clone) == []


def test_a_sheet_new_to_the_pool_owes_the_building_review(clone: Path) -> None:
    _sheet(clone, "ochiba", ["residence", "stable"])
    assert units(clone) == [("building-review", "ochiba", "ochiba"), ("glyph-check", "stable", "ochiba"), ("size-audit", "stable", "ochiba")]


def test_a_kind_new_to_a_sheet_owes_the_glyph_check_and_the_size_audit(clone: Path) -> None:
    _sheet(clone, "hayakawa", ["residence", "kitchen", "kura"])
    assert units(clone) == [("glyph-check", "kura", "hayakawa"), ("size-audit", "kura", "hayakawa")]


def test_the_legacy_tree_and_unclassed_ink_owe_nothing(clone: Path) -> None:
    _map(clone, "legacy-hand-authored-pool", "furu", {}, poly=3)
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "-": 5, "place": 1}, renders=True)
    assert units(clone) == []


def test_a_hand_drawn_map_awaiting_conversion_owes_nothing(clone: Path) -> None:
    """GM 2026-10-01: a hand-drawn Mode B map is exempt - new to the pool, a new element on it, or one it alone draws."""
    _map(clone, "legacy-hand-authored-pool", "furu", {"tannery": 2})
    _map(clone, "legacy-hand-authored-pool", "kaze", {"farmhouse": 3})
    assert units(clone) == []
    _tasks(clone, ["placement-changed: tannery"])
    _, _, problems = owed.owed(clone)
    assert problems == ["specs/999-test: placement-changed: 'tannery' is drawn on no pool map or sheet"]


def test_a_mode_a_sheet_in_the_legacy_tree_still_owes_its_review(clone: Path) -> None:
    """GM 2026-10-01: a hand-drawn magistracy or shrine is never scripted, so it keeps its review wherever it lives."""
    d = clone / "legacy-hand-authored-pool" / "shrines" / "kaminari"
    d.mkdir(parents=True)
    (d / "kaminari.svg").write_text('<svg><rect data-kind="hall"/></svg>')
    assert ("building-review", "kaminari", "kaminari") in units(clone)


def test_a_tweak_declares_in_its_commit_message(clone: Path) -> None:
    """GM 2026-10-01 (the household shrine's torii): a change done directly has no tasks.md, so its commit carries the line."""
    (clone / "l7r" / "engine.py").write_text("X = 2\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "the torii's second crossbar\n\nOccasion: glyph-redrawn: privy - the second crossbar")
    assert units(clone) == [("glyph-check", "privy", "inashiro")]
    assert owed.check_declared(clone) is None


def test_a_landed_feature_s_pointer_declares_nothing(clone: Path) -> None:
    """`.specify/feature.json` outlives its feature: once every task is ticked, its occasions are not owed again."""
    _tasks(clone, ["glyph-redrawn: privy"])
    tasks = clone / "specs" / "999-test" / "tasks.md"
    tasks.write_text(tasks.read_text().replace("- [ ] T01", "- [x] T01"))
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "the feature")
    git(clone, "update-ref", "refs/remotes/origin/main", git(clone, "rev-parse", "HEAD"))
    assert units(clone) == []
    (clone / "specs" / "999-test" / "measurements.json").write_text("{}\n")  # a later record in the landed feature's folder
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "a record")
    assert units(clone) == []


def test_a_feature_landed_part_way_declares_again_when_its_tasks_grow(clone: Path) -> None:
    """Feature 328 (2026-10-10): its first waves landed with every box ticked, then it went on - the later waves' tasks and
    occasions are this delta's work, so its `## Occasions` declares again (it was read as landed and the push refused)."""
    _tasks(clone, ["glyph-redrawn: privy"])
    tasks = clone / "specs" / "999-test" / "tasks.md"
    tasks.write_text(tasks.read_text().replace("- [ ] T01", "- [x] T01"))
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "the first waves")
    git(clone, "update-ref", "refs/remotes/origin/main", git(clone, "rev-parse", "HEAD"))
    (clone / "l7r" / "engine.py").write_text("X = 3\n")
    tasks.write_text(tasks.read_text() + "\n- [x] T02 a later wave\n      research: rendering\n")
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "a later wave")
    assert owed.check_declared(clone) is None
    # feature 374 batch 4: the line that landed with the first waves was judged at that push and is not owed again...
    assert units(clone) == []
    # ...and a later wave that changes an element declares a line of its own, which is owed
    tasks.write_text(tasks.read_text().replace("- glyph-redrawn: privy\n", "- glyph-redrawn: privy\n- glyph-redrawn: farmhouse\n"))
    git(clone, "commit", "-qam", "a later wave's occasion")
    assert units(clone) == [("glyph-check", "farmhouse", "inashiro")]


def test_a_committed_change_beyond_the_merge_base_counts(clone: Path) -> None:
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "well": 1}, renders=True)
    git(clone, "commit", "-qam", "a well")
    (clone / "a.txt").write_text("later")
    git(clone, "add", "-A")
    git(clone, "commit", "-qm", "later")
    assert units(clone) == [("glyph-check", "well", "inashiro")]


def test_detected_and_declared_units_are_one_unit(clone: Path) -> None:
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "well": 1}, renders=True)
    _tasks(clone, ["glyph-redrawn: well"])
    assert units(clone) == [("glyph-check", "well", "inashiro")]


def test_code_moved_with_no_occasions_section_is_refused(clone: Path) -> None:
    (clone / "l7r" / "engine.py").write_text("X = 3\n")
    refusal = owed.check_declared(clone)
    assert refusal and "l7r/engine.py" in refusal and "## Occasions" in refusal
    _tasks(clone, None)  # a tasks.md with no section still refuses
    assert owed.check_declared(clone)
    _tasks(clone, ["none: a refactor"])
    assert owed.check_declared(clone) is None


def test_a_tracked_sheet_svg_is_code_and_a_test_or_a_note_is_not(clone: Path) -> None:
    (clone / "tests").mkdir()
    (clone / "tests" / "test_x.py").write_text("")
    (clone / "pool" / "hamlets" / "inashiro" / "inashiro.notes.md").write_text("# more\n")
    assert owed.check_declared(clone) is None
    _sheet(clone, "hayakawa", ["residence", "kitchen"]).joinpath("hayakawa.svg").write_text("<svg><rect/></svg>")
    assert owed.check_declared(clone)


def test_many_touched_files_are_summarized(clone: Path) -> None:
    for i in range(7):
        (clone / "l7r" / f"m{i}.py").write_text("")
    assert "and 2 more" in (owed.check_declared(clone) or "")


def test_without_origin_main_the_base_is_head(clone: Path) -> None:
    git(clone, "update-ref", "-d", "refs/remotes/origin/main")
    assert owed.base_of(clone)[1].startswith("HEAD")


def test_a_repository_with_no_commits_reports_everything_new(tmp_path: Path) -> None:
    root = tmp_path / "fresh"
    root.mkdir()
    git(root.parent, "init", "-q", str(root))
    _map(root, "pool", "inashiro", {"farmhouse": 1})
    assert owed.base_of(root) == ("", "no commits yet")
    _, got, _ = owed.owed(root, landing=True)
    assert [(u.check, u.subject) for u in got] == [("settlement-review", "inashiro"), ("glyph-check", "farmhouse")]


def test_a_mirror_supplies_a_generated_sheets_base(clone: Path, tmp_path: Path) -> None:
    """A generated sheet's SVG is gitignored: its base is main's mirror copy beside `.clones/`."""
    mirror = tmp_path / "mirror"
    inner = mirror / ".clones" / "s"
    subprocess.run(["git", "clone", "-q", str(clone), str(inner)], check=True)
    git(inner, "update-ref", "refs/remotes/origin/main", git(inner, "rev-parse", "HEAD"))
    gen = inner / "pool" / "magistracies" / "example"
    gen.mkdir(parents=True)
    (gen / "example.gen.py").write_text("")
    git(inner, "add", "-A")
    git(inner, "commit", "-qm", "a generated sheet")
    git(inner, "update-ref", "refs/remotes/origin/main", git(inner, "rev-parse", "HEAD"))
    (gen / "example.svg").write_text('<svg><g data-kind="residence"/><g data-kind="well"/></svg>')
    (mirror / "pool" / "magistracies" / "example").mkdir(parents=True)
    (mirror / "pool" / "magistracies" / "example" / "example.svg").write_text('<svg><g data-kind="residence"/></svg>')
    _, got, _ = owed.owed(inner, landing=True)
    assert [(u.check, u.subject, u.on) for u in got] == [("glyph-check", "well", "example"), ("size-audit", "well", "example")]


def test_a_malformed_census_is_no_elements() -> None:
    assert owed.ink_classes("not json") == set()
    assert owed.ink_classes(json.dumps({"ink_classes": [1, 2]})) == set()


def test_the_slug_is_file_safe() -> None:
    assert owed.Unit("size-audit", "manure heap", "inashiro", "x").slug == "size-audit--manure-heap"


def test_a_glyph_check_is_keyed_by_its_element_and_its_map() -> None:
    """Feature 374 FR-007: keyed by the element alone, a second sheet's check overwrote the first's verdict."""
    assert owed.Unit("glyph-check", "manure heap", "inashiro", "x").slug == "glyph-check--manure-heap--inashiro"
    assert owed.Unit("glyph-check", "manure heap", "", "x").slug == "glyph-check--manure-heap"


def test_one_element_redrawn_on_two_maps_is_two_units(clone: Path) -> None:
    _tasks(clone, ["glyph-redrawn: farmhouse on inashiro", "glyph-redrawn: farmhouse on sawada"])
    assert sorted(units(clone)) == [("glyph-check", "farmhouse", "inashiro"), ("glyph-check", "farmhouse", "sawada")]


def test_pool_map_names_lists_maps_and_sheets_of_both_trees(clone: Path) -> None:
    assert owed.pool_map_names(clone) == ["furu", "hayakawa", "inashiro", "sawada"]


def test_main_prints_slugs_units_the_ruling_and_the_declaration(clone: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "well": 1}, renders=True)
    assert owed.main(["--root", str(clone)]) == 0
    assert capsys.readouterr().out.strip() == "", "no feature: the glyph unit is owed, and due only at landing (amendment 9)"
    assert owed.main(["--root", str(clone), "--landing"]) == 0
    assert capsys.readouterr().out.strip() == "glyph-check--well--inashiro"
    owed.main(["--root", str(clone), "--landing", "--units"])
    assert capsys.readouterr().out.strip().split("\t")[:4] == ["glyph-check--well--inashiro", "glyph-check", "well", "inashiro"]
    owed.main(["--root", str(clone), "--landing", "--why"])
    assert "glyph-check:well on inashiro" in capsys.readouterr().out
    owed.main(["--root", str(clone), "--why"])
    assert "glyph-check--well--inashiro (at landing)" in capsys.readouterr().out
    (clone / "l7r" / "engine.py").write_text("X = 9\n")
    assert owed.main(["--root", str(clone), "--check-declared"]) == 1
    _tasks(clone, ["none: test"])
    assert owed.main(["--root", str(clone), "--check-declared"]) == 0


def test_main_refuses_a_directory_that_is_not_a_repository(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert owed.main(["--root", str(tmp_path)]) == 1
    assert "not a git repository" in capsys.readouterr().err


# ---- the snapshot, per unit ---------------------------------------------------------------------------------


@pytest.fixture
def pair(tmp_path: Path) -> tuple[Path, Path]:
    """A mirror with a clone under its `.clones/`, the clone drawing a well Inashiro did not have."""
    mirror = tmp_path / "mirror"
    mirror.mkdir()
    git(mirror.parent, "init", "-q", str(mirror))
    git(mirror, "config", "user.email", "t@t")
    git(mirror, "config", "user.name", "t")
    _map(mirror, "pool", "inashiro", {"farmhouse": 9}, renders=True)
    git(mirror, "add", "-A")
    git(mirror, "commit", "-qm", "main")
    inner = mirror / ".clones" / "s"
    subprocess.run(["git", "clone", "-q", str(mirror), str(inner)], check=True)
    git(inner, "update-ref", "refs/remotes/origin/main", git(inner, "rev-parse", "HEAD"))
    _map(inner, "pool", "inashiro", {"farmhouse": 9, "well": 1}, renders=True)
    return mirror, inner


def test_the_snapshot_takes_both_sides_and_writes_the_checks_prompt(pair: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    _, inner = pair
    assert snap.main(["--root", str(inner), "--key", "abc", "glyph-check--well--inashiro"]) == 0
    out = capsys.readouterr().out
    base = inner / ".git" / "review-snapshot" / "glyph-check--well--inashiro"
    assert (base / "clone" / "inashiro.json").is_file() and (base / "main" / "inashiro.json").is_file()
    prompt = (base / "dispatch.md").read_text()
    assert prompt.startswith("UNIT: glyph-check--well--inashiro\n") and "'well'" in prompt and "UNIT=glyph-check--well--inashiro" in prompt
    assert "prompt" in out and "on inashiro" in out


def test_a_unit_not_owed_is_refused(pair: tuple[Path, Path], capsys: pytest.CaptureFixture[str]) -> None:
    assert snap.main(["--root", str(pair[1]), "glyph-check--privy"]) == 2
    assert "not owed" in capsys.readouterr().err


def test_a_missing_render_is_named_and_a_sheet_owes_no_manifest(tmp_path: Path) -> None:
    root = tmp_path / "r"
    _map(root, "pool", "inashiro", {"farmhouse": 1})
    sheet = _sheet(root, "hayakawa", ["residence"])
    recs = snap.snapshot(root, None, [owed.Unit("glyph-check", "farmhouse", "inashiro", "x"), owed.Unit("size-audit", "residence", "hayakawa", "y")])
    assert recs[0]["missing"] == [".svg", ".png", ".html"]
    assert ".json" not in recs[1]["missing"] and sheet.is_dir()
    assert recs[0]["main"] is None and "unavailable" in snap.describe(recs[0])
    assert "regenerate it" in snap.describe(recs[0])


def test_a_unit_with_no_map_says_so(tmp_path: Path) -> None:
    rec = snap.snapshot(tmp_path, None, [owed.Unit("glyph-check", "tannery", "", "declared")])[0]
    assert rec["clone"] is None and "no map draws it" in Path(rec["dispatch"]).read_text()


def test_a_previous_snapshot_of_the_same_unit_is_cleared(tmp_path: Path) -> None:
    root = tmp_path / "r"
    _map(root, "pool", "inashiro", {"farmhouse": 1}, renders=True)
    unit = owed.Unit("fix-check", "inashiro", "inashiro", "declared gm-fix")
    stale = root / ".git" / "review-snapshot" / unit.slug / "stale.txt"
    stale.parent.mkdir(parents=True)
    stale.write_text("old")
    snap.snapshot(root, None, [unit])
    assert not stale.exists()


@pytest.mark.parametrize("check", ["settlement-review", "building-review", "glyph-check", "size-audit", "fix-check"])
def test_every_check_has_its_ask(check: str, tmp_path: Path) -> None:
    rec = snap.snapshot(tmp_path, None, [owed.Unit(check, "s", "", "o")])[0]
    assert Path(rec["dispatch"]).read_text().startswith(f"UNIT: {check}--s\n{check} - ")


def test_the_ci_dispatcher_is_not_drawing_or_placement_code() -> None:
    """A refusal-text edit in l7r/diagram/ci/ was asked to declare its occasions (2026-10-09); it draws nothing."""
    assert not owed._CODE.match("l7r/diagram/ci/features.py")
    assert owed._CODE.match("l7r/diagram/overlap/taxonomy.py") and owed._CODE.match("pool/hamlet/x/x.gen.py")


# ---- feature 375 amendment 9 (the GM 2026-10-12): a glyph check is due on the feature's hour, all owed units together --------


def _feature(root: Path, started: float, *, tasks: str = "- [ ] T01 a task\n", status: str = "In progress") -> None:
    """A live feature 999 with its event log beginning at `started`."""
    import datetime

    d = root / "specs" / "999-test"
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(f"# Feature 999\n\n**Status**: {status}\n")
    (d / "tasks.md").write_text("# Tasks\n\n## Occasions\n\n- none: fixture\n\n## Work\n\n" + tasks)
    (root / ".specify").mkdir(exist_ok=True)
    (root / ".specify" / "feature.json").write_text(json.dumps({"feature_directory": "specs/999-test"}))
    ev = root / ".git" / "l7r-events"
    ev.mkdir(parents=True, exist_ok=True)
    t = datetime.datetime.fromtimestamp(started, datetime.UTC).isoformat().replace("+00:00", "Z")
    (ev / "999-test.jsonl").write_text(json.dumps({"t": t, "ev": ""}) + "\n")


def _dispatch(root: Path, slug: str, at: float) -> None:
    p = root / ".git" / "pairing-state.json"
    d = json.loads(p.read_text()) if p.exists() else {}
    d.setdefault("dispatched", {})[slug] = {"key": "k", "at": int(at)}
    p.write_text(json.dumps(d))


def _glyph(root: Path, *elements: str) -> list:
    classes = {"farmhouse": 9, "privy": 4, **{e: 1 for e in elements}}
    _map(root, "pool", "inashiro", classes, renders=True)
    return [u for u in owed.all_owed(root)[1] if u.check == "glyph-check"]


def _due(root: Path, now: float) -> tuple[set[str], set[str]]:
    due, waiting = owed.glyph_due(root, owed.all_owed(root)[1], now)
    return {u.subject for u in due}, {u.subject for u, _w in waiting}


def test_a_glyph_unit_waits_for_the_features_hour_and_the_other_checks_do_not(clone: Path) -> None:
    """SC-032, SC-034: before the hour the glyph unit is owed, not due; a building-review, size-audit or settlement-review unit
    is due at once (FR-041) - here a sheet new to the pool and a kind new to a sheet."""
    t0 = 1_800_000_000.0
    _feature(clone, t0)
    _glyph(clone, "wood shed")
    _sheet(clone, "ochiba", ["residence"])
    _map(clone, "pool", "kawa", {"farmhouse": 2})
    assert _due(clone, t0 + 600) == (set(), {"wood shed"})
    others = {u.check for u in owed.all_owed(clone)[1] if u.check != "glyph-check"}
    assert {"building-review", "settlement-review"} <= others
    due, _ = owed.glyph_due(clone, owed.all_owed(clone)[1], t0 + 600)
    assert due == []
    assert _due(clone, t0 + 3600) == ({"wood shed", "residence"} & _due(clone, t0 + 3600)[0] | {"wood shed"}, set())


def test_units_owed_in_an_hour_are_all_due_at_it_and_a_batch_stays_due_until_each_is_dispatched(clone: Path) -> None:
    t0 = 1_800_000_000.0
    _feature(clone, t0)
    by = {u.subject: u for u in _glyph(clone, "wood shed", "kiln")}
    shed, kiln = by["wood shed"], by["kiln"]
    assert _due(clone, t0 + 3599) == (set(), {"wood shed", "kiln"}), "owed at minute 5 or 59, both wait"
    assert _due(clone, t0 + 3600) == ({"wood shed", "kiln"}, set()), "...and are due together at the hour"
    owed.open_batch(clone, owed.all_owed(clone)[1], t0 + 3600)
    _dispatch(clone, shed.slug, t0 + 3600)
    assert _due(clone, t0 + 3605) == ({"kiln"}, {"wood shed"}), "the batch's second unit stays due after the first's dispatch"
    _dispatch(clone, kiln.slug, t0 + 3610)
    assert _due(clone, t0 + 4200) == (set(), {"wood shed", "kiln"}), "re-owed by a fix ten minutes on: the next hour"
    assert _due(clone, t0 + 7200) == ({"wood shed", "kiln"}, set())


def test_an_old_dispatch_does_not_start_the_features_hour(clone: Path) -> None:
    """A clone's glyph dispatches from before the feature began (October's, never cleared) do not make its units due."""
    t0 = 1_800_000_000.0
    _dispatch(clone, "glyph-check--wood-shed--inashiro", t0 - 86_400)
    _feature(clone, t0)
    _glyph(clone, "wood shed")
    assert _due(clone, t0 + 60) == (set(), {"wood shed"})


@pytest.mark.parametrize(
    ("how", "tasks", "status"),
    [
        ("no feature", None, None),
        ("Done", "- [ ] T01 a task\n", "Done 2026-10-12"),
        ("every task ticked under Draft", "- [x] T01 a task\n", "Draft"),
        ("only its GM-review box open", "- [x] T01 a task\n- [ ] GM review (make gm-reviewed F=999) [lands-open]\n", "Draft"),
    ],
)
def test_with_no_live_feature_glyph_units_are_due_only_at_landing(clone: Path, how: str, tasks: str | None, status: str | None) -> None:
    t0 = 1_800_000_000.0
    if tasks is not None:
        _feature(clone, t0 - 86_400 * 3, tasks=tasks, status=status or "")
        if "GM review" in tasks:
            (clone / "specs" / "999-test" / "gm-review.jsonl").write_text('{"kind": "accept", "finding": "x"}\n')
    _glyph(clone, "wood shed")
    due, waiting = owed.glyph_due(clone, owed.all_owed(clone)[1], t0)
    assert due == [] and [w for _u, w in waiting] == ["at landing"], how
    owed.mark_landing(clone, True)
    assert _due(clone, t0) == ({"wood shed"}, set()), "landing: every owed glyph unit due"
    owed.mark_landing(clone, False)
    assert _due(clone, t0)[0] == set(), "a clean push clears the mark"


def test_the_cli_gates_an_early_dispatch_opens_a_batch_on_the_hour_and_on_the_escape(clone: Path, capsys: pytest.CaptureFixture[str]) -> None:
    import time

    now = time.time()
    _feature(clone, now - 600)
    (shed,) = _glyph(clone, "wood shed")
    assert owed.main(["--root", str(clone), "--glyph-gate", shed.slug]) == 1 and "not yet due" in capsys.readouterr().out
    assert owed.main(["--root", str(clone), "--glyph-gate", shed.slug, "--escaped"]) == 0
    assert owed.main(["--root", str(clone), "--glyph-gate", "settlement-review--x"]) == 0, "not a glyph unit: the gate is not this"
    assert owed.main(["--root", str(clone), "--glyph-dispatched", shed.slug]) == 0
    assert not (clone / ".git" / owed.CLOCK).exists(), "an early dispatch without the escape opens no batch"
    assert owed.main(["--root", str(clone), "--glyph-dispatched", shed.slug, "--escaped"]) == 0
    clock = json.loads((clone / ".git" / owed.CLOCK).read_text())["999-test"]
    assert clock["batch"] == [shed.slug] and clock["batch_at"] >= int(now), "the escape opens a batch: the clock restarts"
    _feature(clone, now - 7200)
    (clone / ".git" / owed.CLOCK).unlink()
    assert owed.main(["--root", str(clone), "--glyph-gate", shed.slug]) == 0
    assert owed.main(["--root", str(clone), "--glyph-dispatched", shed.slug]) == 0 and (clone / ".git" / owed.CLOCK).exists(), "on the hour"
    _dispatch(clone, shed.slug, time.time() + 1)
    capsys.readouterr()
    assert owed.main(["--root", str(clone), "--why"]) == 0 and "not yet due" in capsys.readouterr().out
    assert owed.main(["--root", str(clone), "--landing"]) == 0 and shed.slug in capsys.readouterr().out
    assert owed.main(["--root", str(clone), "--landing-mark", "on"]) == 0 and (clone / ".git" / owed.LANDING).exists()


# ---- feature 375 amendment 10 (the GM 2026-10-12): a reopened feature's hour counts from its most recent reopening ---------


def _commit_feature(root: Path, when: float, *, status: str, tasks: str, gm_row: bool = False) -> None:
    """Write feature 999's spec, tasks (and a GM-review row) and commit them dated `when`."""
    d = root / "specs" / "999-test"
    d.mkdir(parents=True, exist_ok=True)
    (d / "spec.md").write_text(f"# Feature 999\n\n**Status**: {status}\n")
    (d / "tasks.md").write_text("# Tasks\n\n## Occasions\n\n- none: fixture\n\n## Work\n\n" + tasks)
    if gm_row:
        (d / "gm-review.jsonl").write_text('{"kind": "accept", "finding": "x"}\n')
    elif (d / "gm-review.jsonl").exists():
        (d / "gm-review.jsonl").unlink()
    env = {**__import__("os").environ, "GIT_COMMITTER_DATE": f"@{int(when)} +0000", "GIT_AUTHOR_DATE": f"@{int(when)} +0000"}
    subprocess.run(["git", "-C", str(root), "add", "-A", "specs"], check=True, capture_output=True, env=env)
    subprocess.run(["git", "-C", str(root), "commit", "-qm", status], check=True, capture_output=True, env=env)


_REOPENS = [
    ("by its status line", dict(status="Done 2026-10-01", tasks="- [x] T01 a task\n"), dict(status="Reopened for an amendment", tasks="- [x] T01 a task\n- [ ] T02 more\n")),
    ("by every task ticked", dict(status="Draft", tasks="- [x] T01 a task\n"), dict(status="Draft", tasks="- [x] T01 a task\n- [ ] T02 more\n")),
    (
        "GM review pending",
        dict(status="Draft", tasks="- [x] T01 a task\n- [ ] GM review (make gm-reviewed F=999) [lands-open]\n", gm_row=True),
        dict(status="Draft", tasks="- [x] T01 a task\n- [ ] GM review (make gm-reviewed F=999) [lands-open]\n- [ ] T02 more\n", gm_row=True),
    ),
]


@pytest.mark.parametrize(("how", "closed", "reopened"), _REOPENS, ids=[r[0] for r in _REOPENS])
def test_a_reopened_features_hour_counts_from_its_reopening(clone: Path, how: str, closed: dict, reopened: dict) -> None:
    """SC-035 (FR-042): the event log began days ago, the feature closed, and was reopened ten minutes ago - its glyph unit is
    due an hour after the reopening, not at once (amendment 9 counted from the first event, the GM did not like that)."""
    now = time.time()
    _feature(clone, now - 4 * 86_400)  # the clone's first event, days ago; the files are written again by the commits below
    _commit_feature(clone, now - 3 * 86_400, status="In progress", tasks="- [ ] T01 a task\n")
    _commit_feature(clone, now - 2 * 86_400, **closed)
    _commit_feature(clone, now - 600, **reopened)
    _glyph(clone, "wood shed")
    assert owed.feature_start(clone, "999-test") == pytest.approx(now - 600, abs=2), how
    assert _due(clone, now) == (set(), {"wood shed"}), f"{how}: not due at once"
    assert _due(clone, now + 3100) == ({"wood shed"}, set()), f"{how}: due an hour after the reopening"


def test_with_no_reopening_or_an_older_one_the_first_event_starts_the_hour(clone: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    now = time.time()
    _feature(clone, now - 7200)
    _commit_feature(clone, now - 7000, status="In progress", tasks="- [ ] T01 a task\n")
    assert owed.feature_start(clone, "999-test") == pytest.approx(now - 7200, abs=2), "no reopening: the first event"
    assert owed.last_reopening(clone, "999-test", now - 7200) is None
    _commit_feature(clone, now - 6 * 86_400, status="Done", tasks="- [x] T01 a task\n")
    _commit_feature(clone, now - 5 * 86_400, status="Reopened", tasks="- [x] T01\n- [ ] T02\n")
    _feature(clone, now - 4 * 86_400)
    _commit_feature(clone, now - 600, status="Reopened", tasks="- [x] T01\n- [ ] T02\n- [ ] T03\n")  # still open: no new reopening
    assert owed.feature_start(clone, "999-test") == pytest.approx(now - 4 * 86_400, abs=2), "a reopening before the first event loses to it"
    calls: list[str] = []
    import hm_approval  # the module the walk reads states with, on the path once owed has walked

    real = hm_approval._state_at
    monkeypatch.setattr(hm_approval, "_state_at", lambda *a: calls.append(a[1]) or real(*a))
    owed.feature_start(clone, "999-test")
    assert calls == [], "the kept answer is reused while the directory's newest commit is unchanged"


def test_verify_renders_a_map_whose_render_is_missing_or_older_than_the_map(tmp_path: Path) -> None:
    """Feature 385 T26 (plan D48; the round arbiter's fix on hour:385-approach-checklist@12): a pool roll writes no renders, and
    `make verify` once wrote three glyph prompts on maps whose `.png` and `.html` were missing."""
    import os
    import types

    d = tmp_path / "pool" / "hamlets" / "m"
    d.mkdir(parents=True)
    for s in (".gen.py", ".json"):
        (d / f"m{s}").write_text("x")
    unit = types.SimpleNamespace(on="m")
    assert snap.stale_renders(tmp_path, [unit]) == ["pool/hamlets/m/m.gen.py"], "no render at all"
    for s in (".png", ".html"):
        (d / f"m{s}").write_text("x")
    past = time.time() - 60
    os.utime(d / "m.gen.py", (past, past))
    os.utime(d / "m.json", (past, past))
    assert snap.stale_renders(tmp_path, [unit]) == [], "renders newer than the map"
    os.utime(d / "m.json", (time.time() + 60, time.time() + 60))
    assert snap.stale_renders(tmp_path, [unit, unit]) == ["pool/hamlets/m/m.gen.py"], "a manifest rolled after its render, listed once"
    sheet = tmp_path / "pool" / "sheets" / "s"
    sheet.mkdir(parents=True)
    (sheet / "s.svg").write_text("x")
    assert snap.stale_renders(tmp_path, [types.SimpleNamespace(on="s"), types.SimpleNamespace(on="")]) == ["sheet:pool/sheets/s/s.svg"], "a sheet with no generator and no render is listed, to be refused"
    (sheet / "s.png").write_text("x")
    assert snap.stale_renders(tmp_path, [types.SimpleNamespace(on="s")]) == [], "...and not once it has one"
