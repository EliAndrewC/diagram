"""Feature 294 B5: the classes a page draws see-through (`tools/see_through.py`)."""

from __future__ import annotations

from l7r.diagram.tools.see_through import translucent_marks

PAGE = (
    '<svg id="map"><defs><pattern id="p"><rect opacity="0.1"/></pattern></defs>'
    '<g class="f f-well" data-k="well"><rect opacity="0.55"/><rect/></g>'
    '<g opacity="0.5"><g class="f f-pond" data-k="pond"><circle r="3" fill-opacity="0.9"/></g></g>'
    '<g class="f f-field-grave" data-k="field grave"><circle r="2" opacity="0.9"/></g>'
    '<g class="f f-bund" data-k="bund"><path d="M0,0" class="hit" opacity="0.1" style="pointer-events: stroke"/><path d="M0,0"/></g>'
    '<text opacity="0.5">a caption</text>'
    "</svg>"
)


def test_the_faintest_mark_of_each_class_through_its_enclosing_groups() -> None:
    """Seeded: the recorded case - a field grave's mound drawn at 0.9, a class no table declares."""
    got = translucent_marks(PAGE)
    assert got == {"well": 0.55, "pond": 0.45, "field grave": 0.9, "(no class)": 0.5}


def test_a_broadleaf_painted_over_a_conifer_is_found_in_paint_order() -> None:
    """Seeded: the recorded case (269 B30) - a later clump's broadleaf inked over an earlier clump's conifer."""
    from l7r.diagram.tools.see_through import broadleaf_over_conifer, crowns_in_paint_order

    svg = (
        '<svg><defs><circle cx="0" cy="0" r="9" fill="#496733" stroke="#000"/></defs>'
        '<g transform="translate(100,100)"><circle cx="0" cy="0" r="8" fill="#496733" stroke="#3C5526"/>'
        '<circle cx="2" cy="0" r="1" fill="#7C9A4E" stroke="#3C5526"/></g>'
        '<g transform="translate(110,100)"><circle cx="0" cy="0" r="7" fill="#7C9A4E" stroke="#3C5526"/></g>'
        '<g><circle cx="300" cy="300" r="8" fill="#6E8B43" stroke="#3C5526"/><circle cx="305" cy="300" r="8" fill="#4A6733" stroke="#3C5526"/></g>'
        "</g></svg>"
    )
    crowns = crowns_in_paint_order(svg)
    assert crowns == [(100.0, 100.0, 8.0, True), (110.0, 100.0, 7.0, False), (300.0, 300.0, 8.0, False), (305.0, 300.0, 8.0, True)]
    assert broadleaf_over_conifer(crowns) == [(0, 1)], "the broadleaf painted after its conifer; the one painted before it is under it"
    assert broadleaf_over_conifer([(0.0, 0.0, 5.0, False)]) == []
