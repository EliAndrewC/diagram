"""Feature 200 - the low-zoom raster, the class id map and the off-map drop (`interactive/raster.py`).

The mechanics on strings, and the two renders on a tiny real document - resvg is a hard requirement of
the engine, so the render is exercised for real rather than faked."""

from __future__ import annotations

import io
import re

import pytest
from PIL import Image

from l7r.diagram.interactive import raster
from l7r.diagram.interactive.raster import OFFMAP_MARGIN, PALETTE_STEP, class_keys, data_uri, drop_offmap, id_map, picture, resvg_png, viewbox_of

VB = (100.0, 200.0, 300.0, 400.0)  # x 100-400, y 200-600; the margin reaches 24 px past each edge


def test_viewbox_is_read_from_the_svg_open_tag_or_is_none() -> None:
    assert viewbox_of('<svg xmlns="http://www.w3.org/2000/svg" viewBox="1678 353 1070 1928" font-family="serif">') == (1678.0, 353.0, 1070.0, 1928.0)
    assert viewbox_of('<svg viewBox="0,0 10 10">') == (0.0, 0.0, 10.0, 10.0)
    assert viewbox_of("<svg>") is None


# ---- the drop (FR-001) ---------------------------------------------------------------------------


def test_a_line_outside_the_margin_is_dropped_and_one_inside_or_crossing_is_kept() -> None:
    inside = '<line x1="150" y1="250" x2="152" y2="253"/>'
    crossing = '<line x1="90" y1="250" x2="110" y2="253"/>'  # reaches in
    near = f'<line x1="{100 - OFFMAP_MARGIN + 1:g}" y1="250" x2="{100 - OFFMAP_MARGIN + 3:g}" y2="253"/>'  # inside the margin
    far = '<line x1="10" y1="250" x2="12" y2="253"/>'
    below = '<line x1="150" y1="700" x2="152" y2="703"/>'
    out = drop_offmap(f'<g stroke="#000">{inside}{crossing}{near}{far}{below}</g>', VB)
    assert inside in out and crossing in out and near in out
    assert far not in out and below not in out


def test_every_absolute_primitive_is_judged_by_its_own_box() -> None:
    kept = [
        '<circle cx="410" cy="300" r="20"/>',  # center outside, disc reaches to 390: kept
        '<ellipse cx="90" cy="300" rx="15" ry="5"/>',  # reaches to 105
        '<rect x="380" y="590" width="30" height="30"/>',
        '<polygon points="50,300 120,300 120,320"/>',
        '<polyline points="150,650 150,600"/>',
    ]
    dropped = [
        '<circle cx="450" cy="300" r="20"/>',  # 430 is past 424
        '<ellipse cx="60" cy="300" rx="15" ry="5"/>',
        '<rect x="425" y="300" width="30" height="30"/>',
        '<polygon points="50,300 70,300 70,320"/>',
        '<polyline points="150,650 150,640"/>',
    ]
    out = drop_offmap("".join(kept + dropped), VB)
    assert all(k in out for k in kept), out
    assert not any(d in out for d in dropped), out


def test_a_merged_path_loses_only_its_outside_subpaths_and_an_all_outside_path_goes() -> None:
    d_in, d_out = "M150,250L152,253", "M10,250L12,253"
    part = f'<path d="{d_in}{d_out}{d_in}" fill="none"/>'
    gone = f'<path d="{d_out}{d_out}" fill="none"/>'
    disc_in = "M120,300a5,5 0 1 0 10,0a5,5 0 1 0 -10,0"  # center 125
    disc_out = "M40,300a5,5 0 1 0 10,0a5,5 0 1 0 -10,0"  # center 45, reaches 50
    discs = f'<path d="{disc_in}{disc_out}" fill="#0a0"/>'
    out = drop_offmap(part + gone + discs, VB)
    assert f'<path d="{d_in}{d_in}" fill="none"/>' in out
    assert gone not in out and d_out not in out
    assert f'<path d="{disc_in}" fill="#0a0"/>' in out


def test_what_is_not_judged_passes_through_untouched() -> None:
    transformed = '<g transform="translate(10,10)"><line x1="0" y1="0" x2="1" y2="1"/></g>'
    assert drop_offmap(transformed, VB) == transformed
    relative = '<path d="M10,10h5v5Z" fill="#000"/>'
    assert drop_offmap(relative, VB) == relative
    curve = '<path d="M10,10 Q20,20 30,30" fill="none"/>'
    assert drop_offmap(curve, VB) == curve
    odd = '<circle cx="10" r="5"/><polygon points=""/><rect x="a" y="1" width="2" height="2"/>'
    assert drop_offmap(odd, VB) == odd, "a shape missing an attribute, or empty, is not judged"


# ---- the renders (FR-003, FR-007) ----------------------------------------------------------------

TINY = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40">'
    '<rect width="40" height="40" fill="#EFE3C2"/>'
    '<g class="f f-farmhouse" data-k="farmhouse"><rect x="2" y="2" width="10" height="10" fill="#8B7355"/></g>'
    '<g opacity="0.5"><g class="f f-pond" data-k="pond"><circle cx="30" cy="30" r="6" fill="url(#water)"/></g></g>'
    '<g class="f f-bund" data-k="bund"><path d="M2,30L12,30" fill="none" stroke="#5A4A2A" stroke-width="0.5"/>'
    '<path d="M2,30L12,30" fill="none" class="hit" style="pointer-events: stroke; stroke-width: 6.0px"/></g>'
    '<g class="f f-scrub-and-rough-grazing" data-k="scrub and rough grazing"><g class="hit" fill="none" style="pointer-events: fill"><rect x="20" y="2" width="10" height="10" fill="none"/></g></g>'
    '<g class="f f-marsh" data-k="marsh"><polygon class="hit" points="20,14 30,14 30,20" fill="none" style="pointer-events: fill"/></g>'
    '<g class="f f-bund-beans" data-k="bund beans"><circle cx="35" cy="5" r="0.5" fill="#2F4F2F"/><circle cx="35" cy="5" r="2.0" fill="none" class="hit" style="pointer-events: fill"/></g>'
    "</svg>"
)


def _png(data: bytes) -> Image.Image:
    return Image.open(io.BytesIO(data)).convert("RGBA")


def test_the_picture_is_a_lossless_webp_at_r_px_per_map_px() -> None:
    data = picture(TINY, 2.0)
    assert data is not None
    im = Image.open(io.BytesIO(data))
    assert im.format == "WEBP" and im.size == (80, 80)
    assert im.convert("RGB").getpixel((10, 10)) == (0x8B, 0x73, 0x55), "the farmhouse's own color, exactly - lossless"


def test_class_keys_are_derived_in_order_of_first_appearance() -> None:
    assert class_keys(TINY) == ["farmhouse", "pond", "bund", "scrub and rough grazing", "marsh", "bund beans"]
    assert class_keys("<svg/>") == []


def test_the_id_map_paints_every_class_and_its_hit_geometry_flat_and_nothing_else() -> None:
    keys = class_keys(TINY)
    png, palette = id_map(TINY, keys)
    assert png is not None
    im = _png(png)
    assert im.size == (40, 40)
    red = {k: (i + 1) * PALETTE_STEP for i, k in enumerate(keys)}
    assert palette == {str(v): k for k, v in red.items()}
    assert im.getpixel((5, 5))[0] == red["farmhouse"], "a fill"
    assert im.getpixel((30, 30))[0] == red["pond"], "a pattern fill, its opacity wrapper stripped"
    assert im.getpixel((7, 28))[0] == red["bund"], "the widened copy's 6 px stroke, not the 0.5 px mark"
    assert im.getpixel((25, 5))[0] == red["scrub and rough grazing"], "a marks-region rectangle carrying its own fill=none"
    assert im.getpixel((27, 15))[0] == red["marsh"], "a region polygon"
    assert im.getpixel((36, 5))[0] == red["bund beans"], "a widened bead"
    assert im.getpixel((15, 38)) == (0, 0, 0, 0), "the sheet paints nothing"
    for x in range(40):
        for y in range(40):
            v = im.getpixel((x, y))[0]
            assert v % PALETTE_STEP == 0, f"a value off the palette's grid at {x},{y}: anti-aliasing or an opacity survived"


def test_the_id_map_refuses_a_page_past_its_palette() -> None:
    with pytest.raises(ValueError, match="past the id map"):
        id_map(TINY, [f"k{i}" for i in range(64)])


def test_without_resvg_the_page_carries_no_raster(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(raster.shutil, "which", lambda _name: None)
    assert resvg_png("<svg/>") is None
    assert picture(TINY) is None
    assert id_map(TINY, class_keys(TINY))[0] is None
    assert "resvg not found" in capsys.readouterr().err


def test_a_bare_test_svg_gets_the_namespace_resvg_needs() -> None:
    assert resvg_png('<svg viewBox="0 0 4 4"><rect width="4" height="4" fill="#fff"/></svg>', "--zoom", "1") is not None


def test_data_uri() -> None:
    assert data_uri("image/png", b"\x89PNG") == "data:image/png;base64,iVBORw=="
    assert re.fullmatch(r"data:image/webp;base64,[A-Za-z0-9+/=]+", data_uri("image/webp", b"RIFF"))


def test_a_class_group_nested_in_another_takes_the_outer_class_and_is_painted_once() -> None:
    """The writer never nests one class group in another (wrap emits siblings), so the id map's walk
    treats an inner group as part of the outer's text: painted in the outer's color, and never appended a
    second time by the walk resuming inside it. Asserted here so the guard that keeps it so is not dead."""
    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20">'
        '<g class="f f-outer" data-k="outer"><g class="f f-inner" data-k="inner"><rect x="0" y="0" width="20" height="20" fill="#123456"/></g></g>'
        "</svg>"
    )
    png, palette = id_map(doc, class_keys(doc))
    assert png is not None and palette == {"4": "outer", "8": "inner"}
    assert _png(png).getpixel((10, 10))[0] == 4, "the outer class's color"


# ---- feature 201: text is never in the picture --------------------------------------------------------


def test_without_text_strips_every_text_element_and_nothing_else() -> None:
    from l7r.diagram.interactive.raster import without_text

    doc = '<svg><text x="1" y="2" class="c">Kuwa\nbata</text><rect x="0" y="0" width="1" height="1"/><g><text>a</text><text font-size="3">b</text></g></svg>'
    assert without_text(doc) == '<svg><rect x="0" y="0" width="1" height="1"/><g></g></svg>'
    assert without_text("<svg/>") == "<svg/>"


def test_the_picture_carries_no_text_while_the_id_map_paints_it() -> None:
    """FR-001: the placard's name and the scale are drawn by the browser once, never by resvg under it; a
    caption still hits as its class."""
    from l7r.diagram.interactive.raster import without_text

    doc = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 60 40">'
        '<rect width="60" height="40" fill="#EFE3C2"/>'
        '<g class="f f-place" data-k="place"><text x="4" y="30" font-size="28" font-family="serif" fill="#FF00FF">MM</text></g>'
        "</svg>"
    )
    magenta = lambda data: any(px[:3] == (255, 0, 255) for px in _png(data).getdata())  # noqa: E731
    with_text, no_text = picture(doc, 2.0), picture(without_text(doc), 2.0)
    assert with_text is not None and no_text is not None
    assert magenta(with_text), "resvg does draw the text when it is there (fonts-dejavu is installed)"
    assert not magenta(no_text), "the picture the page carries has none of it"
    png, palette = id_map(doc, class_keys(doc))
    assert png is not None
    reds = {px[0] for px in _png(png).getdata()}
    assert PALETTE_STEP in reds, "the caption is painted in its class's color, so it hits as its class"
