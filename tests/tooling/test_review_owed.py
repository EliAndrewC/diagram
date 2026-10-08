"""`scripts/_review_owed.py` and `scripts/_review_snapshot.py` - the scripted answer to "which review checks are owed",
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
from pathlib import Path
from typing import Any

import pytest

REPO = Path(__file__).resolve().parents[2]


def _mod(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), REPO / "scripts" / f"{name}.py")
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
    _, got, problems = owed.owed(root)
    assert not problems, problems
    return [(u.check, u.subject, u.on) for u in got]


def test_nothing_changed_owes_nothing(clone: Path) -> None:
    desc, got, _ = owed.owed(clone)
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
    _, got, problems = owed.owed(clone)
    assert [u.subject for u in got] == ["tannery"]
    assert "drawn on no pool map" in problems[0]
    assert "PROBLEMS" in owed.ruling("x", got, problems)


def test_an_unknown_occasion_is_a_problem(clone: Path) -> None:
    _tasks(clone, ["repainted: privy"])
    _, got, problems = owed.owed(clone)
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


def test_a_map_new_to_the_pool_owes_the_whole_map_review_and_only_elements_new_to_the_legend(clone: Path) -> None:
    _map(clone, "pool", "kuwabata", {"farmhouse": 5, "privy": 2, "fish pond": 3})
    assert units(clone) == [("settlement-review", "kuwabata", "kuwabata"), ("glyph-check", "fish pond", "kuwabata")]


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
    _, got, _ = owed.owed(root)
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
    _, got, _ = owed.owed(inner)
    assert [(u.check, u.subject, u.on) for u in got] == [("glyph-check", "well", "example"), ("size-audit", "well", "example")]


def test_a_malformed_census_is_no_elements() -> None:
    assert owed.ink_classes("not json") == set()
    assert owed.ink_classes(json.dumps({"ink_classes": [1, 2]})) == set()


def test_the_slug_is_file_safe() -> None:
    assert owed.Unit("glyph-check", "manure heap", "inashiro", "x").slug == "glyph-check--manure-heap"


def test_pool_map_names_lists_maps_and_sheets_of_both_trees(clone: Path) -> None:
    assert owed.pool_map_names(clone) == ["furu", "hayakawa", "inashiro", "sawada"]


def test_main_prints_slugs_units_the_ruling_and_the_declaration(clone: Path, capsys: pytest.CaptureFixture[str]) -> None:
    _map(clone, "pool", "inashiro", {"farmhouse": 9, "privy": 4, "well": 1}, renders=True)
    assert owed.main(["--root", str(clone)]) == 0
    assert capsys.readouterr().out.strip() == "glyph-check--well"
    owed.main(["--root", str(clone), "--units"])
    assert capsys.readouterr().out.strip().split("\t")[:4] == ["glyph-check--well", "glyph-check", "well", "inashiro"]
    owed.main(["--root", str(clone), "--why"])
    assert "glyph-check:well on inashiro" in capsys.readouterr().out
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
    assert snap.main(["--root", str(inner), "--key", "abc", "glyph-check--well"]) == 0
    out = capsys.readouterr().out
    base = inner / ".git" / "review-snapshot" / "glyph-check--well"
    assert (base / "clone" / "inashiro.json").is_file() and (base / "main" / "inashiro.json").is_file()
    prompt = (base / "dispatch.md").read_text()
    assert prompt.startswith("UNIT: glyph-check--well\n") and "'well'" in prompt and "UNIT=glyph-check--well" in prompt
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
