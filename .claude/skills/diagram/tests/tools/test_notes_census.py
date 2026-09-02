# ---- feature 174: the census body and the rewriter ----------------------------------------------
import json as _json

from l7r.diagram.tools import notes_census as nc


def test_the_census_counts_what_the_map_DREW_including_the_clumps_off_the_page() -> None:
    """The block exists because a stated count and a drawn count drifted apart three times. Off-page
    windbreak clumps are counted separately rather than dropped: they are drawn, they cost the
    generator work, and a reader comparing "42 clumps" against the sheet needs to know some are
    outside the frame."""
    M = {
        "village_groves": [
            {"role": "windbreak", "clumps": [[0, 0], [1, 1]], "clumps_offpage": [[9, 9]]},
            {"role": "copse", "clumps": [[2, 2]]},
        ],
        "houses": [{"x": 10.0, "y": 10.0}, {"x": 20.0, "y": 20.0}],
        "farm_fixtures": [{"form": "rack"}, {"form": "rack"}, {"kind": "trough"}],
    }
    body = nc.census(M)
    assert "windbreak: **2** clumps drawn, **1** off the page" in body
    assert "copse: **1** clumps drawn" in body
    assert "farmhouses: **2**" in body
    assert "rack **2**" in body and "trough **1**", "fixtures are counted by form, falling back to kind"


def test_a_map_with_no_fixtures_says_NONE_rather_than_printing_an_empty_list() -> None:
    assert "farmstead fixtures: none" in nc.census({"houses": []})


def test_a_notice_board_row_reports_how_many_farmhouses_it_actually_serves() -> None:
    """The board's whole justification is that the households can read it, so the row carries the
    count within 250 ft rather than just the coordinates."""
    M = {"houses": [{"x": 0.0, "y": 0.0}, {"x": 100.0, "y": 0.0}, {"x": 9000.0, "y": 0.0}], "kosatsuba": [{"x": 0.0, "y": 0.0}]}
    assert "**2** of 3 farmhouses within 250 ft" in nc.census(M)


def test_replace_refreshes_only_between_the_MARKERS_and_leaves_a_file_without_them_alone() -> None:
    """The block is generated and the prose around it is the GM's, so the rewriter must not touch a
    byte outside the markers - and a notes file that carries no block is returned unchanged rather
    than having one appended."""
    M = {"houses": [{"x": 1.0, "y": 1.0}]}
    text = f"# Notes\n\nprose above\n\n{nc.BEGIN}\nstale body\n{nc.END}\n\nprose below\n"
    out = nc.replace(text, M)
    assert out.startswith("# Notes\n\nprose above\n") and out.endswith("prose below\n")
    assert "stale body" not in out and "farmhouses: **1**" in out
    assert nc.replace("# Notes\n\nno block here\n", M) == "# Notes\n\nno block here\n"


def test_main_rewrites_each_map_and_distinguishes_missing_absent_and_current(tmp_path, capsys) -> None:
    """Three outcomes a reader has to be able to tell apart: no notes file at all, a notes file with
    no census block, and one already current. Reporting them identically is how a map silently stops
    being censused."""

    def _map(name: str, notes: str | None) -> str:
        p = tmp_path / f"{name}.json"
        p.write_text(_json.dumps({"houses": [{"x": 1.0, "y": 1.0}]}))
        if notes is not None:
            (tmp_path / f"{name}.notes.md").write_text(notes)
        return str(p)

    stale = _map("a", f"{nc.BEGIN}\nold\n{nc.END}\n")
    none = _map("b", None)
    blockless = _map("c", "# just prose\n")
    assert nc.main([stale, none, blockless]) == 0
    out = capsys.readouterr().out
    assert "a.notes.md: census refreshed" in out
    assert "b.notes.md: no notes file" in out
    assert "c.notes.md: no census block" in out
    assert "1 file(s) rewritten" in out

    assert nc.main([stale]) == 0, "a second run over the same map"
    assert "already current" in capsys.readouterr().out


def test_main_with_no_arguments_says_how_to_use_it_and_refuses(capsys) -> None:
    assert nc.main([]) == 2
    assert "usage:" in capsys.readouterr().err
