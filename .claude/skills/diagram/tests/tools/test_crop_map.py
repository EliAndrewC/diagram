"""Cropping a rendered map by WORLD coordinates (`tools/crop_map.py`).

Feature 174, under the GM's 2026-09-02 ruling that every engine module owes 100% coverage. This one
had never been measured. It exists because the world-to-pixel conversion "got hand-written from
scratch five times in one session, once with the arithmetic wrong" - so the conversion is what these
tests pin, on a real PNG whose pixels have known values rather than on a mock.

`tooling`: it writes image files.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from l7r.diagram.tools import crop_map

pytestmark = pytest.mark.tooling

_VIEWBOX = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="100 200 400 300" width="800" height="600">'


def _map(tmp_path: Path, w: int = 800, h: int = 600, viewbox: str = _VIEWBOX) -> str:
    """A rendered map on disk: an .svg carrying the viewBox and a .png of the matching size.

    The PNG is painted in four quadrants so a crop's CONTENT identifies where it came from - a test
    that only checked the output's size would pass on a crop taken from the wrong corner.
    """
    from PIL import Image

    base = str(tmp_path / "amap")
    Path(base + ".svg").write_text(viewbox + "</svg>")
    im = Image.new("RGB", (w, h))
    for x in range(w):
        for y in range(h):
            im.putpixel((x, y), ((255, 0, 0) if x < w // 2 else (0, 255, 0)) if y < h // 2 else ((0, 0, 255) if x < w // 2 else (255, 255, 0)))
    im.save(base + ".png")
    return base


def test_the_viewBox_is_the_window_of_world_coordinates_the_png_shows(tmp_path: Path) -> None:
    base = _map(tmp_path)
    assert crop_map.view_box(base + ".svg") == (100.0, 200.0, 400.0, 300.0)


def test_a_file_with_no_viewBox_is_refused_by_name(tmp_path: Path) -> None:
    """ "is it a rendered map?" - the honest question, because the usual cause is a path typo."""
    p = tmp_path / "notamap.svg"
    p.write_text("<svg></svg>")
    with pytest.raises(SystemExit, match="no viewBox"):
        crop_map.view_box(str(p))


def test_a_world_region_lands_on_the_RIGHT_PIXELS_not_merely_the_right_size(tmp_path: Path) -> None:
    """The conversion this module exists for: png_px = (world - viewBox_origin) * png_width/viewBox_width.
    Here that scale is 800/400 = 2. A region in the world's top-left quadrant must come back RED; if
    the origin offset were dropped or the scale inverted the crop would be a different colour, which
    is what a size-only assertion would have missed."""
    from PIL import Image

    base = _map(tmp_path)
    out = crop_map.crop(base, [(110, 210, 190, 290)], 1.0, str(tmp_path / "out"))
    assert len(out) == 1
    im = Image.open(out[0])
    assert im.size == (160, 160), "80 world units at 2 px each"
    assert im.getpixel((5, 5)) == (255, 0, 0), "the top-left quadrant is red"

    far = crop_map.crop(base, [(410, 410, 490, 490)], 1.0, str(tmp_path / "out2"))
    assert Image.open(far[0]).getpixel((5, 5)) == (255, 255, 0), "the bottom-right quadrant is yellow"


def test_a_region_off_the_edge_is_CLAMPED_and_one_wholly_outside_is_skipped_with_a_reason(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """Clamping rather than erroring is the point - "a region near the edge crops to what exists".
    A region with nothing to crop is named on stderr rather than silently producing no file."""
    from PIL import Image

    base = _map(tmp_path)
    out = crop_map.crop(base, [(50, 150, 200, 300)], 1.0, str(tmp_path / "out"))
    assert len(out) == 1 and Image.open(out[0]).size == (200, 200), "clamped to the rendered view"

    none = crop_map.crop(base, [(9000, 9000, 9100, 9100)], 1.0, str(tmp_path / "out3"))
    assert none == []
    assert "outside the rendered view" in capsys.readouterr().err


def test_zoom_resizes_the_piece_and_never_to_nothing(tmp_path: Path) -> None:
    from PIL import Image

    base = _map(tmp_path)
    big = crop_map.crop(base, [(110, 210, 190, 290)], 2.0, str(tmp_path / "o1"))
    assert Image.open(big[0]).size == (320, 320)
    small = crop_map.crop(base, [(110, 210, 190, 290)], 0.001, str(tmp_path / "o2"))
    assert Image.open(small[0]).size == (1, 1), "a floor of one pixel, never a zero-size image"


def test_main_parses_every_region_form_and_prints_ONE_PATH_PER_LINE(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """ "Prints one output path per line - feed those straight to Read." Taking MANY regions in one
    invocation is the whole point (the review loop is "crop everything you want, then look at it"),
    so the two region forms are asserted together in one call: `x,y,radius` and `--box x0,y0,x1,y1`."""
    base = _map(tmp_path)
    rc = crop_map.main(["crop_map", base, "150,250,40", "--box", "300,300,400,400", "--out", str(tmp_path / "o")])
    assert rc == 0
    lines = [ln for ln in capsys.readouterr().out.splitlines() if ln.strip()]
    assert len(lines) == 2, f"one path per region, in order: {lines}"
    assert all(Path(ln).is_file() for ln in lines)


def test_main_defaults_to_the_WHOLE_map_when_no_region_is_named(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """`--whole` and "no regions at all" are the same request, and both take the viewBox itself."""
    from PIL import Image

    base = _map(tmp_path)
    assert crop_map.main(["crop_map", base, "--out", str(tmp_path / "a")]) == 0
    implied = capsys.readouterr().out.strip()
    assert crop_map.main(["crop_map", base, "--whole", "--out", str(tmp_path / "b")]) == 0
    explicit = capsys.readouterr().out.strip()
    assert Image.open(implied).size == Image.open(explicit).size == (800, 600)


def test_main_takes_the_base_path_with_OR_without_an_extension(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    """A reader pastes whatever path they have - the .png, the .svg or the .json - and all three name
    the same map. Stripping the extension here is what saves them noticing."""
    base = _map(tmp_path)
    for suffix in ("", ".png", ".svg", ".json"):
        assert crop_map.main(["crop_map", base + suffix, "--whole", "--out", str(tmp_path / "o")]) == 0
        assert capsys.readouterr().out.strip().endswith("-0.png")


def test_main_with_no_arguments_prints_the_usage_and_with_no_MAP_says_so(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert crop_map.main(["crop_map"]) == 1
    assert "crop" in capsys.readouterr().out.lower()
    with pytest.raises(SystemExit, match="give a map path"):
        crop_map.main(["crop_map", "--zoom", "2"])


def test_main_honours_zoom_and_the_CROP_OUT_environment_default(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from PIL import Image

    base = _map(tmp_path)
    monkeypatch.setenv("CROP_OUT", str(tmp_path / "fromenv"))
    assert crop_map.main(["crop_map", base, "--whole", "--zoom", "0.5"]) == 0
    out = capsys.readouterr().out.strip()
    assert out.startswith(str(tmp_path / "fromenv")), "the env var sets the default outdir"
    assert Image.open(out).size == (400, 300), "and --zoom scaled it"
