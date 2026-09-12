"""`tools/picture_diff.py` - two renders compared, and the differing pixels attributed to a class's ink
(feature 231). The arithmetic runs on synthetic images; the SVG paths run through resvg on a tiny document,
as `tests/interactive/test_raster.py` does."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from l7r.diagram.tools import picture_diff as pd

pytestmark = pytest.mark.renders  # the SVG cases render a 40x40 document (feature 213)

#: two classes side by side, each a flat square - the id map gives them distinct palette values
TINY = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40" width="40" height="40">'
    '<rect width="40" height="40" fill="#EFE3C2"/>'
    '<g class="f f-paddy" data-k="paddy"><rect x="0" y="0" width="20" height="40" fill="#A6C398"/></g>'
    '<g class="f f-pond" data-k="pond"><rect x="20" y="0" width="20" height="40" fill="#6C9CBE"/></g>'
    "</svg>"
)
#: the same document with the pond a shade different - a change confined to the pond's own ink
TINY_B = TINY.replace('fill="#6C9CBE"', 'fill="#5C8CAE"')


def _img(fill: tuple[int, int, int], size: tuple[int, int] = (8, 6)) -> Image.Image:
    return Image.new("RGB", size, fill)


def test_identical_images_differ_nowhere() -> None:
    s = pd.diff_stats(_img((10, 20, 30)), _img((10, 20, 30)))
    assert s["differing"] == 0 and s["share"] == 0.0 and s["bbox"] is None and s["max_delta"] == 0
    assert "identical" in pd.report(s)


def test_a_change_under_the_threshold_is_not_a_difference() -> None:
    """A lit edge moves a fringe pixel by a few units; that is antialiasing, not a moved feature."""
    a, b = _img((100, 100, 100)), _img((100, 100, 106))
    assert pd.diff_stats(a, b)["differing"] == 0
    assert pd.diff_stats(a, b, threshold=2)["differing"] == 48


def test_the_bbox_bounds_exactly_the_changed_pixels() -> None:
    a = _img((0, 0, 0))
    b = a.copy()
    b.putpixel((2, 1), (255, 255, 255))
    b.putpixel((5, 4), (255, 255, 255))
    s = pd.diff_stats(a, b)
    assert s["differing"] == 2 and s["bbox"] == (2, 1, 5, 4) and s["max_delta"] == 255
    assert "bbox: (2, 1, 5, 4)" in pd.report(s)


def test_renders_of_different_sizes_are_refused_with_the_remedy() -> None:
    with pytest.raises(ValueError, match="render the SVG at the other"):
        pd.diff_stats(_img((0, 0, 0), (8, 6)), _img((0, 0, 0), (9, 6)))


def test_a_png_loads_as_it_is(tmp_path: Path) -> None:
    p = tmp_path / "a.png"
    _img((1, 2, 3)).save(p)
    assert pd.load(str(p)).size == (8, 6)


def test_an_svg_renders_at_the_width_it_is_given(tmp_path: Path) -> None:
    p = tmp_path / "t.svg"
    p.write_text(TINY)
    assert pd.load(str(p)).size == (40, 40)
    assert pd.load(str(p), width=80).size == (80, 80)


def test_without_resvg_an_svg_says_so(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pd.raster, "resvg_png", lambda *_a, **_k: None)
    p = tmp_path / "t.svg"
    p.write_text(TINY)
    with pytest.raises(SystemExit, match="resvg is not installed"):
        pd.load(str(p))


def test_the_id_map_attributes_each_differing_pixel_to_the_class_it_lies_on() -> None:
    a, b = pd.load_from_text(TINY), pd.load_from_text(TINY_B)
    stats = pd.diff_stats(a, b)
    ids = pd.id_map_of(TINY_B)
    assert ids is not None
    red, palette = ids
    classes = pd.by_class(stats["mask"], red, palette, a.size[0] / red.shape[1])
    assert classes["pond"] == stats["differing"], classes
    assert classes[pd.OFF_CLASS] == 0 and "paddy" not in classes
    assert "on the ink of:" in pd.report(stats, classes)


def test_a_pixel_outside_the_id_map_counts_as_off_any_class() -> None:
    """The renders may be larger than the id map (a picture at 2 px per map px); nothing off it is attributed."""
    mask = np.zeros((4, 4), dtype=bool)
    mask[3, 3] = True
    red = np.zeros((2, 2), dtype=np.int64)
    out = pd.by_class(mask, red, {4: "paddy"}, scale=1.0)
    assert out == {pd.OFF_CLASS: 1}


def test_without_resvg_there_is_no_attribution(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(pd.raster, "id_map", lambda *_a, **_k: (None, {}))
    assert pd.id_map_of(TINY) is None


def test_main_reports_the_diff_and_the_classes(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a, b, svg = tmp_path / "a.png", tmp_path / "b.svg", tmp_path / "b.svg"
    pd.load_from_text(TINY).save(a)
    b.write_text(TINY_B)
    assert pd.main([str(a), str(b), "--svg", str(svg)]) == 0
    out = capsys.readouterr().out
    assert "differing:" in out and "pond" in out


def test_main_takes_the_svg_in_either_position(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a, b = tmp_path / "a.svg", tmp_path / "b.png"
    a.write_text(TINY)
    pd.load_from_text(TINY_B).save(b)
    assert pd.main([str(a), str(b)]) == 0
    assert "differing:" in capsys.readouterr().out


def test_main_on_identical_renders_attributes_nothing(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    im = pd.load_from_text(TINY)
    im.save(a)
    im.save(b)
    assert pd.main([str(a), str(b), "--svg", str(tmp_path / "none.svg")]) == 0
    out = capsys.readouterr().out
    assert "identical" in out and "on the ink of" not in out


def test_a_document_with_no_classes_attributes_nothing_rather_than_everything(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A source that names no class cannot say where a pixel lies: the diff is reported, the attribution is not."""
    bare = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 8 8" width="8" height="8"><rect width="8" height="8" fill="#000"/></svg>'
    other = bare.replace("#000", "#fff")
    a, b, svg = tmp_path / "a.png", tmp_path / "b.png", tmp_path / "b.svg"
    pd.load_from_text(bare).save(a)
    pd.load_from_text(other).save(b)
    svg.write_text(other)
    assert pd.main([str(a), str(b), "--svg", str(svg)]) == 0
    out = capsys.readouterr().out
    assert "differing:" in out and "on the ink of" not in out


def test_a_map_svg_carries_no_class_groups_and_is_refused_as_an_attribution_source() -> None:
    """The drawn `.svg` is byte-identical to the pre-feature-134 target: the class groups live only in the
    page. Handing this a map's own SVG used to yield an empty palette and attribute every pixel to nothing."""
    bare = TINY.replace('<g class="f f-paddy" data-k="paddy">', "<g>").replace('<g class="f f-pond" data-k="pond">', "<g>")
    assert pd.id_map_of(bare) is None


def test_a_page_answers_the_attribution_from_the_id_map_it_already_carries(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    from l7r.diagram.interactive.page import render_page

    strings = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">',
        '<rect width="40" height="40" fill="#EFE3C2"/>',
        '<rect x="0" y="0" width="20" height="40" fill="#A6C398"/>',
        '<rect x="20" y="0" width="20" height="40" fill="#6C9CBE"/>',
        "</svg>",
    ]
    page = tmp_path / "m.html"
    page.write_text(render_page(strings, [None, "-", "paddy", "fish pond", None], "Tiny", {"ftpx": 1.0}, {}))
    ids = pd.id_map_of_page(page.read_text())
    assert ids is not None and sorted(ids[1].values()) == ["fish pond", "paddy"]
    a, b = tmp_path / "a.png", tmp_path / "b.png"
    pd.load_from_text(TINY).save(a)
    pd.load_from_text(TINY_B).save(b)
    assert pd.main([str(a), str(b), "--page", str(page)]) == 0
    out = capsys.readouterr().out
    assert "fish pond" in out and "paddy" not in out


def test_a_page_with_no_id_map_attributes_nothing(tmp_path: Path) -> None:
    assert pd.id_map_of_page("<html>no payload</html>") is None
