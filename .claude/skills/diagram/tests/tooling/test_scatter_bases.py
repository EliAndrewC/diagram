"""`scripts/_scatter_bases.py` (feature 256, FR-009): the wrapper `make scatter-bases` runs for `settlement-review`.

WHAT THESE PROVE. A map is found by folder, stem or file; the counts come from the parse it is handed (a stand-in
here - the engine's `parse_bases` is tested where it lives, and once below on a real fragment); a box lists only the
bases inside it, in either corner order, and truncates at the limit; a missing render and a malformed box are usage
errors that say what is wrong; and nothing printed is a verdict.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_scatter_bases", REPO / "scripts" / "_scatter_bases.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


sb = _load()
BASES = {"blade": [(10.0, 10.0), (50.0, 50.0), (55.0, 52.0)], "pine": [], "reed": [(51.0, 51.0)]}


def _fake(_svg: str) -> dict:
    return BASES


def _map(tmp_path: pathlib.Path) -> pathlib.Path:
    folder = tmp_path / "pool" / "hamlets" / "sawada"
    folder.mkdir(parents=True)
    (folder / "sawada.svg").write_text("<svg/>", encoding="utf-8")
    return folder


def test_locate(tmp_path: pathlib.Path) -> None:
    folder = _map(tmp_path)
    want = folder / "sawada.svg"
    assert sb.locate(str(folder)) == want and sb.locate(str(folder / "sawada")) == want and sb.locate(str(want)) == want


def test_render_counts_and_a_box() -> None:
    text = sb.render("sawada", BASES, None, 40)
    assert "blade        3" in text and "pine         0" in text and "inside the box" not in text
    boxed = sb.render("sawada", BASES, (40.0, 40.0, 60.0, 60.0), 1)
    assert "blade        2  (50.0,50.0) ..." in boxed and "reed         1  (51.0,51.0)" in boxed
    assert "verdict" in boxed.splitlines()[0] and "VIOLATION" not in boxed


def test_main(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    folder = _map(tmp_path)
    assert sb.main([str(folder), "--box", "60,60,40,40"], parse=_fake) == 0, "the corners may come in either order"
    assert "inside the box (40.0, 40.0, 60.0, 60.0)" in capsys.readouterr().out
    assert sb.main([str(folder), "--box", "1,2,3"], parse=_fake) == 2
    assert "x0,y0,x1,y1" in capsys.readouterr().err
    assert sb.main([str(tmp_path / "pool" / "hamlets" / "absent")], parse=_fake) == 2
    assert "no render" in capsys.readouterr().err


def test_the_engines_own_parse_is_what_runs(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    folder = _map(tmp_path)
    (folder / "sawada.svg").write_text('<svg><g stroke="#A7A860"><line x1="12.0" y1="34.0" x2="13" y2="30"/></g></svg>', encoding="utf-8")
    assert sb.main([str(folder)]) == 0
    assert "blade        1" in capsys.readouterr().out, "non-vacuity: the real parse found the one blade"
