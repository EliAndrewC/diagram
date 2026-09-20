"""`scripts/_record_prepass.py` and `scripts/_size_table.py` (feature 251, FR-005 and FR-006).

Both take the mechanical first step out of a subagent check and hand the agent a list. WHAT THESE PROVE:
the pre-pass finds each session-note shape `record-format` names, reads VISIBLE text only (a note inside
an HTML comment is already where it belongs), drops a term the glossary covers as a term or a variant,
and does not mistake a quoted ruling's "make sure" for a make target; the size table converts at
3 px = 1 ft, applies an ancestor's translate, FLAGS a rotation instead of applying it, skips a pattern's
tile, inherits a group's stroke width, and finds the gate as the gap between two wall segments. Each
matcher is asserted to FIND something (non-vacuity), and the real tree is read once for each.
"""

from __future__ import annotations

import importlib.util
import json
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]
SKILL = REPO / ".claude/skills/diagram"


def _load(name: str):  # noqa: ANN202
    spec = importlib.util.spec_from_file_location(name, REPO / "scripts" / f"{name}.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


rp = _load("_record_prepass")
st = _load("_size_table")

PAGE = """<html><head><style>.x{}</style></head><body>
<p><em>The findings behind the lanes.</em> Intro names <em>aze</em> and <em>tameike</em>.</p>
<h2>How wide is a lane?</h2>
<p>Grounds: lane_width, the L-belt. The GM said <em>"I just want to make sure that we did not set it"</em>.
Feature 143 set it in T41 (specs/143-research/plan.md); run make quick or make quote-verbatim. The knob is
<code>lane_width_ft</code> in settlement/ways.py, verdict SUMMARY-ONLY. <a href="x"><code>lane-source_key</code></a>
is a source key. The cart (大八車, <em>daihachiguruma</em>) and <em>Bidens tripartita</em> and <em>Carex dispalata</em>.</p>
<!-- Evidence: attested. Feature 999, T99 - a session note where it belongs -->
<h3>And a bund?</h3>
<p>Nothing to report here.</p>
</body></html>"""
GLOSSARY = {"bund": {"def": "a paddy dike", "variants": ["aze", "bunds"]}, "Bidens tripartita": {"def": "a weed", "variants": ["Bidens"]}}


def _by_label(items: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for it in items:
        out.setdefault(it["label"], []).append(it["match"])
    return out


def test_every_session_note_shape_is_found_in_visible_text_only():
    listing = rp.prepass(PAGE, GLOSSARY)
    assert [s["section"] for s in listing] == ["(top)", "How wide is a lane?", "And a bund?"]
    got = _by_label(listing[1]["items"])
    assert got["field"] == ["Grounds:"]
    assert got["feature number"] == ["Feature 143"] and got["task id"] == ["T41"], "the commented-out 999 and T99 are not visible"
    assert got["spec path"] == ["specs/143-research"]
    assert got["make target"] == ["make quick", "make quote-verbatim"], '"make sure" in a quoted ruling is not a target'
    assert "settlement/ways.py" in got["file path"] and "specs/143-research/plan.md" in got["file path"]
    assert got["fetch verdict"] == ["SUMMARY-ONLY"]
    assert got["engine identifier"] == ["lane_width_ft"], "a <code> inside a link is a source key, not an identifier"
    assert listing[2]["items"] == []


def test_vocabulary_drops_what_the_glossary_covers_and_a_quoted_ruling():
    listing = rp.prepass(PAGE, GLOSSARY)
    top = _by_label(listing[0]["items"])
    assert top == {"italic term": ["tameike"]}, "`aze` is a glossary variant; the long italic sentence is not a term"
    lane = _by_label(listing[1]["items"])
    assert lane["CJK term"] == ["大八車"] and lane["italic term"] == ["daihachiguruma"]
    assert lane["binomial"] == ["Carex dispalata"], "Bidens tripartita is in the glossary"
    assert rp.known_terms({"x": {"def": "d"}}) == {"x"}, "an entry with no variants still counts"


def test_render_and_main_over_a_fixture_tree(tmp_path, capsys):
    research = tmp_path / rp.RESEARCH
    research.mkdir(parents=True)
    (research / "lanes.html").write_text(PAGE, encoding="utf-8")
    out = tmp_path / "pre.json"
    assert rp.main(["lanes", "--root", str(tmp_path), "--json", str(out)]) == 0, "a tree with no glossary still runs"
    text = capsys.readouterr().out
    assert "3 sections" in text and "## How wide is a lane?" in text and "## And a bund?" not in text
    assert json.loads(out.read_text(encoding="utf-8"))["page"] == "lanes"
    gloss = tmp_path / rp.GLOSSARY
    gloss.parent.mkdir(parents=True)
    gloss.write_text(json.dumps(GLOSSARY), encoding="utf-8")
    assert rp.main(["lanes.html", "--root", str(tmp_path)]) == 0
    assert "'aze'" not in capsys.readouterr().out
    assert rp.main(["absent", "--root", str(tmp_path)]) == 2


def test_the_prepass_reads_the_real_record():
    glossary = json.loads((REPO / rp.GLOSSARY).read_text(encoding="utf-8"))
    listing = rp.prepass((SKILL / "research" / "ways.html").read_text(encoding="utf-8"), glossary)
    assert len(listing) >= 3 and any(s["items"] for s in listing), "non-vacuity: the real page yields sections and candidates"


SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="600" height="400">
<defs><pattern id="p"><rect width="14" height="14"/></pattern></defs>
<rect x="30" y="30" width="300" height="150" fill="url(#p)"/>
<g transform="translate(100, 200)"><rect x="0" y="0" width="60" height="30"/><rect x="0" y="0" width="0" height="9"/></g>
<g transform="rotate(30)"><rect x="400" y="10" width="33" height="33"/><line x1="0" y1="0" x2="50" y2="0"/></g>
<text x="130" y="215">kitchen</text><text x="180" y="105">OUTER <tspan>COURT</tspan></text><text x="1" y="1">  </text>
<g stroke="#333" stroke-width="9">
<line x1="30" y1="300" x2="120" y2="300"/><line x1="150" y1="300" x2="330" y2="300"/>
<line x1="30" y1="300" x2="30" y2="340"/><line x1="30" y1="370" x2="30" y2="390"/><line x1="30" y1="390" x2="30.5" y2="390.5"/>
</g>
<path d="M0 0" stroke-width="1.5"/>
</svg>"""


def test_the_table_converts_translates_flags_and_finds_the_gate():
    data = st.table(SVG)
    court, kitchen, rotated = data["rects"]
    assert (court["w_ft"], court["h_ft"], court["area_sqft"], court["label"]) == (100.0, 50.0, 5000, "OUTER COURT")
    assert (kitchen["x_px"], kitchen["y_px"], kitchen["w_ft"], kitchen["h_ft"], kitchen["label"]) == (100.0, 200.0, 20.0, 10.0, "kitchen")
    assert kitchen["label_ft_away"] == 0.0 and kitchen["note"] == ""
    assert rotated["note"] == "transform not applied", "a rotation is flagged, never silently ignored"
    assert len(data["rects"]) == 3, "the pattern tile and the zero-width rect are not drawn things"
    assert data["gaps"] == [
        {"axis": "h", "at_px": 300.0, "from_px": 120.0, "gap_ft": 10.0, "wall_ft": 3.0},
        {"axis": "v", "at_px": 30.0, "from_px": 340.0, "gap_ft": 10.0, "wall_ft": 3.0},
    ], "the gate is the gap between two collinear wall segments; the wall's 9 px is inherited from its group"
    assert data["strokes_ft"] == {0.5: 1, 3.0: 5}
    assert st.shift_of("translate(5) scale(2)") == (5.0, 0.0, True)
    assert st.num(None) == 0.0 and st.num("12.5px") == 12.5


def test_a_sheet_with_no_labels_and_no_gaps_still_renders(tmp_path, capsys):
    bare = '<svg xmlns="http://www.w3.org/2000/svg"><rect x="0" y="0" width="30" height="30"/></svg>'
    data = st.table(bare)
    assert data["rects"][0]["label"] == "" and data["rects"][0]["label_ft_away"] is None
    text = st.render("bare.svg", data)
    assert "none found" in text and " - " not in text.splitlines()[2][:3]
    plan = tmp_path / "plan.svg"
    plan.write_text(SVG, encoding="utf-8")
    out = tmp_path / "t.json"
    assert st.main([str(plan), "--json", str(out)]) == 0
    assert "OUTER COURT" in capsys.readouterr().out and json.loads(out.read_text())["gaps"]
    assert st.main([str(plan)]) == 0
    assert st.main([str(tmp_path / "absent.svg")]) == 2


def test_the_table_reads_a_real_pool_plan():
    plans = sorted((SKILL / "pool" / "magistracies").glob("*/*.svg"))
    assert plans, "non-vacuity: the pool holds Mode A plans"
    data = st.table(plans[0].read_text(encoding="utf-8"))
    assert len(data["rects"]) > 20 and data["gaps"] and any(w >= 2.0 for w in data["strokes_ft"])


def test_a_scoped_prepass_lists_one_section(tmp_path, capsys):
    research = tmp_path / rp.RESEARCH
    research.mkdir(parents=True)
    (research / "lanes.html").write_text(PAGE, encoding="utf-8")
    assert rp.main(["lanes", "--root", str(tmp_path), "--section", "how wide"]) == 0
    text = capsys.readouterr().out
    assert "1 sections" in text and "Grounds:" in text and "tameike" not in text



# --------------------------------------------------------------- feature 260: the candidate words


def test_a_rare_undefined_word_is_a_candidate_and_an_ordinary_one_is_not() -> None:
    """FR-001: the model should rule on a list, not notice an open one (specs/260, the GM's option C)."""
    text = "The girder bears on an abutment sill, and the deck is wide."
    defined = {"abutment", "sill", "deck"}
    frequency = {"the": 900, "girder": 1, "bears": 40, "on": 900, "an": 900, "and": 900, "is": 900,
                 "wide": 120, "abutment": 9, "sill": 9, "deck": 30}
    got = rp.rare_words(text, defined, frequency, cutoff=2)
    assert [w for w, _n in got] == ["girder"], got
    assert got[0][1] == 1, "the count travels with the word, so a reader sees why it is there"


def test_a_word_the_record_uses_often_is_not_a_candidate() -> None:
    """R3: `embankment` is in 23 fragments and is not raised - which is why the contract asks the
    model to add what it notices (FR-008)."""
    got = rp.rare_words("the embankment holds", set(), {"the": 900, "embankment": 23, "holds": 88})
    assert got == []


def test_a_registry_source_key_is_not_a_candidate() -> None:
    """FR-004: a citation key is an identifier, not a word a reader is asked to know.

    A floor rather than a saving - R3 measured that the cutoff already keeps every key in the record
    off every list - so this test states the guarantee on a key rare enough to survive the cutoff.
    """
    text = "as ritter-timber-bridges puts it, the girder bears"
    freq = {"as": 900, "ritter-timber-bridges": 1, "puts": 90, "it": 900, "the": 900, "girder": 1, "bears": 40}
    got = rp.rare_words(text, set(), freq, keys={"ritter-timber-bridges"})
    assert [w for w, _n in got] == ["girder"], got


def test_the_candidate_list_over_the_real_entry() -> None:
    """SC-001: 34 where the prepass reports 0 today, on the entry feature 259 measured three times."""
    record = SKILL / "research"
    text = rp.text_of(rp.strip_comments(
        (record / "ways" / "010-how-far-past-the-bank-does-a-bridge-land.html").read_text(encoding="utf-8")
        + (record / "ways" / "010-how-far-past-the-bank-does-a-bridge-land.notes.html").read_text(encoding="utf-8")))
    got = rp.rare_words(text, rp.defined_words(str(record)), rp.corpus_frequency(str(record)),
                             keys=rp.registry_keys(str(record)))
    words = [w for w, _n in got]
    assert 20 <= len(words) <= 50, f"{len(words)} candidates - tens, not hundreds (R1, R2)"
    assert "girder" in words and "obliquity" in words and "stringers" in words
    assert "and" not in words and "the" not in words


def test_a_corpus_that_has_never_seen_the_words_raises_nothing() -> None:
    """FAILS CLOSED: with no corpus every word looks rare, which is R1's 314-of-324 failure. A
    candidate list is evidence, and a list built from no evidence is worse than none."""
    assert rp.rare_words("the girder bears on an abutment sill", set(), {}) == []
