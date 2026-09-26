"""A hand-drawn sheet read back as the page's two lists (feature 262).

The GM's constraint is that the drawing is the one source: *"changing that source in one place is enough to
change it downstream"*. So every test here takes a sheet as a plain string and asserts what the reader makes of
its `data-kind` tags - which kind each piece of ink belongs to, that nothing is drawn in a different order or
with different attributes, and that ink nobody tagged is reported by name.
"""

from __future__ import annotations

import os

import pytest

from l7r.diagram.interactive.classes import NOT_HIGHLIGHTED, FeatureClass
from l7r.diagram.interactive.sheet import census, element_kinds, flatten, parse, title_of, write_sheet_page

HEAD = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100">'


def _fc(key: str) -> FeatureClass:
    return FeatureClass(key=key, name=key.title(), covers="-", what="What it is.", why="Why it is here.", label="accurate", label_note="Read.", sources=("not recorded",), entry="research/buildings.html (no dedicated entry - recorded as silent)")


REG = {k: _fc(k) for k in ("granary", "dais", "office hall", "wall")}


def test_a_flat_sheet_is_one_fragment_per_top_level_element_in_order() -> None:
    svg = HEAD + '\n  <!-- a note -->\n  <rect x="0" y="0" width="100" height="100" fill="#EEE" data-kind="-"/>\n  <g data-kind="granary"><rect x="1" y="1" width="5" height="5" fill="#C00"/><text x="2" y="3">granary</text></g>\n</svg>'
    strings, tags = flatten(svg)
    assert strings[0] == HEAD and strings[-1] == "</svg>"
    assert tags[0] == NOT_HIGHLIGHTED and tags[-1] == NOT_HIGHLIGHTED
    assert strings[1:-1] == ['<rect x="0" y="0" width="100" height="100" fill="#EEE" data-kind="-"/>', '<g data-kind="granary"><rect x="1" y="1" width="5" height="5" fill="#C00"/><text x="2" y="3">granary</text></g>']
    assert tags[1:-1] == [NOT_HIGHLIGHTED, "granary"]


def test_a_nested_tag_wins_for_its_subtree_and_the_group_keeps_the_rest() -> None:
    svg = HEAD + '<g data-kind="office hall" stroke="#000"><rect x="1" y="1" width="9" height="9"/><rect data-kind="dais" x="3" y="3" width="2" height="2"/><text x="1" y="1">office hall</text></g></svg>'
    strings, tags = flatten(svg)
    assert tags[1:-1] == ["office hall", "dais", "office hall"]
    # each piece is re-wrapped in the group's own opening tag, so the inherited stroke still applies
    assert strings[2] == '<g data-kind="office hall" stroke="#000"><rect data-kind="dais" x="3" y="3" width="2" height="2"/></g>'


def test_an_untagged_group_holding_tagged_children_passes_its_transform_to_each() -> None:
    svg = HEAD + '<g transform="translate(5, 5)"><circle data-kind="granary" cx="0" cy="0" r="1"/><circle data-kind="wall" cx="2" cy="0" r="1"/></g></svg>'
    strings, tags = flatten(svg)
    assert tags[1:-1] == ["granary", "wall"]
    assert all(s.startswith('<g transform="translate(5, 5)">') and s.endswith("</g>") for s in strings[1:-1])


def test_an_id_on_a_reopened_ancestor_rides_on_its_first_copy_only() -> None:
    svg = HEAD + '<g id="grp"><rect data-kind="granary" x="0" y="0" width="1" height="1"/><rect data-kind="wall" x="0" y="0" width="1" height="1"/></g></svg>'
    strings, _ = flatten(svg)
    assert strings[1].startswith('<g id="grp">') and strings[2].startswith("<g>")


def test_defs_are_ruled_out_and_whitespace_and_comments_vanish() -> None:
    svg = HEAD + '\n<defs><pattern id="p"><rect width="2" height="2" fill="#000"/></pattern></defs>\n<!-- c -->\n</svg>'
    strings, tags = flatten(svg)
    assert strings[1:-1] == ['<defs><pattern id="p"><rect width="2" height="2" fill="#000"/></pattern></defs>']
    assert tags[1:-1] == [NOT_HIGHLIGHTED]


def test_loose_text_inherits_the_enclosing_kind() -> None:
    svg = HEAD + '<g data-kind="granary"><text x="0" y="0">a<tspan data-kind="wall">b</tspan>c</text></g></svg>'
    _, tags = flatten(svg)
    assert tags[1:-1] == ["granary", "wall", "granary"]


def test_the_census_names_untagged_ink_and_unknown_kinds() -> None:
    svg = HEAD + '<rect x="0" y="0" width="1" height="1" fill="#000"/><circle data-kind="kiln" cx="1" cy="1" r="1"/><g data-kind="granary"><rect x="0" y="0" width="1" height="1"/></g></svg>'
    c = census(svg, REG)
    assert c.counts == {"kiln": 1, "granary": 1}
    assert len(c.unclassed) == 1 and "<rect>" in c.unclassed[0]
    assert c.unregistered == ["kiln"]


def test_element_kinds_keys_every_tagged_or_inheriting_element_by_its_offset() -> None:
    svg = HEAD + '<g data-kind="granary"><text x="0" y="0">granary</text></g><text x="1" y="1">loose</text></svg>'
    kinds = element_kinds(svg)
    assert kinds[svg.index('<text x="0"')] == "granary"
    assert svg.index('<text x="1"') not in kinds


@pytest.mark.parametrize(
    ("svg", "why"),
    [
        ("<g></g>", "no <svg> element"),
        (HEAD + "<g>", "ends inside"),
        (HEAD + "</g></svg>", "unbalanced"),
    ],
)
def test_a_malformed_sheet_is_refused_by_name(svg: str, why: str) -> None:
    with pytest.raises(ValueError, match=why):
        parse(svg)


def test_the_title_is_the_file_name_in_title_case() -> None:
    assert title_of("/x/pool/magistracies/ochiba-magistracy/ochiba-magistracy.svg") == "Ochiba Magistracy"


def test_the_page_is_written_beside_the_sheet_with_the_sheet_s_kinds(tmp_path: pytest.TempPathFactory) -> None:
    path = os.path.join(str(tmp_path), "demo-sheet.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEAD + '<rect data-kind="-" x="0" y="0" width="100" height="100" fill="#EEE"/><g data-kind="granary"><rect x="1" y="1" width="5" height="5" fill="#C00"/></g></svg>')
    c = write_sheet_page(path, REG, with_raster=False)
    with open(path[:-4] + ".html", encoding="utf-8") as fh:
        page = fh.read()
    assert c.unclassed == [] and c.unregistered == []
    assert 'data-k="granary"' in page and "<title>Demo Sheet - interactive map</title>" in page
    assert '"Granary"' in page


def test_the_render_condition_picks_the_raster_default(tmp_path: pytest.TempPathFactory, monkeypatch: pytest.MonkeyPatch) -> None:
    path = os.path.join(str(tmp_path), "s.svg")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write(HEAD + '<g data-kind="granary"><rect x="1" y="1" width="5" height="5" fill="#C00"/></g></svg>')
    monkeypatch.setenv("DIAGRAM_SKIP_RENDER", "1")
    write_sheet_page(path, REG)
    with open(path[:-4] + ".html", encoding="utf-8") as fh:
        assert '"raster": {"r": 0}' in fh.read()
