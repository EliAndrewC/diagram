"""`scripts/_source_entries.py` (feature 255, FR-002): what `source-applicability` is handed instead of the registry.

WHAT THESE PROVE. A key's entry is its own paragraphs and stops at the next heading; a key is found by its anchor
or by its `<code>`; a key the registry lacks is SAID to be lacking (the agent is told to open the registry for
exactly that); a footnote is matched on any key it carries, not only its first, and arrives with its passages and
the assertion it is attached to; a citations page in a subdirectory is read beside its own research page.

NO NETWORK and no real record: the fixture is a three-entry registry and two citations pages built under tmp_path.
"""

from __future__ import annotations

import importlib.util
import pathlib

REPO = pathlib.Path(__file__).resolve().parents[5]


def _load():  # noqa: ANN202
    spec = importlib.util.spec_from_file_location("_source_entries", REPO / "scripts" / "_source_entries.py")
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


se = _load()

REGISTRY = """<h2 id="works-cited">Works cited</h2>
<h3 id="alpha-survey"><code>alpha-survey</code></h3>
<p>Alpha, a survey (https://example.org/alpha)<!-- READ 2026-09-01 --></p>
<p><em>What it is:</em> A village survey.</p>
<p><em>Why it applies, and its limits:</em> One village only.</p>
<p><em>Used for:</em> the lot sizes</p>
<h3 id="beta-anchor"><code>beta-treatise</code></h3>
<p>Beta, a treatise (https://example.org/beta)</p>
<h2 id="other">Other</h2>
<p>never part of an entry</p>
"""
CITES = """<ol>
<li id="fn-1"><a href="https://example.org/alpha"><code>alpha-survey</code></a> - 「lots of thirty bu」 <a class="fnback" href="../hamlets.html#r1">back</a></li>
<li id="fn-2"><a href="https://example.org/beta"><code>beta-treatise</code></a> - 「a wall of earth」; and <code>alpha-survey</code> again <a class="fnback" href="#">back</a></li>
<li id="fn-3">no publicly readable source (searched the archive)</li>
</ol>"""
PAGE = '<p>Lots were small.<sup class="fn"><a href="citations/hamlets.html#fn-1">1</a></sup> Walls were earth.<sup class="fn"><a href="citations/hamlets.html#fn-2">2</a></sup></p>'


def _tree(tmp_path: pathlib.Path) -> pathlib.Path:
    research = tmp_path / se.RESEARCH
    (research / "citations" / "cities").mkdir(parents=True)
    (research / "cities").mkdir()
    (research / "SOURCES.html").write_text(REGISTRY, encoding="utf-8")
    (research / "hamlets.html").write_text(PAGE, encoding="utf-8")
    (research / "citations" / "hamlets.html").write_text(CITES, encoding="utf-8")
    # a citations page with no research page beside it still yields its note, with no assertion
    (research / "citations" / "cities" / "tango.html").write_text('<li id="fn-9"><code>alpha-survey</code> - 「a city lot」</li>', encoding="utf-8")
    return tmp_path


def test_an_entry_is_its_own_paragraphs_and_stops_at_the_next_heading() -> None:
    got = se.entry(REGISTRY, "alpha-survey")
    assert got == ["Alpha, a survey (https://example.org/alpha)", "What it is: A village survey.", "Why it applies, and its limits: One village only.", "Used for: the lot sizes"]
    assert se.entry(REGISTRY, "beta-treatise") == ["Beta, a treatise (https://example.org/beta)"]  # by <code>, and the h2's paragraph is not its
    assert se.entry(REGISTRY, "beta-anchor") == ["Beta, a treatise (https://example.org/beta)"]  # by anchor
    assert se.entry(REGISTRY, "gamma") == []


def test_a_note_is_matched_on_any_key_it_carries() -> None:
    got = se.citing(CITES, PAGE, {"alpha-survey"})
    assert [n["id"] for n in got] == ["fn-1", "fn-2"]
    assert got[0]["assertion"] == "Lots were small." and got[0]["passages"][0]["quote"] == "lots of thirty bu"
    assert got[1]["keys"] == ["alpha-survey"] and got[1]["assertion"] == "Walls were earth."
    assert se.citing(CITES, PAGE, {"gamma"}) == []


def test_gather_and_render_over_a_tree(tmp_path: pathlib.Path) -> None:
    found = se.gather(_tree(tmp_path), ["alpha-survey", "gamma"])
    assert [(n["page"], n["id"]) for n in found["notes"]["alpha-survey"]] == [("cities/tango", "fn-9"), ("hamlets", "fn-1"), ("hamlets", "fn-2")]
    text = se.render(found)
    assert "== alpha-survey" in text and "Used for: the lot sizes" in text and "-- cited by 3 footnotes" in text
    assert "hamlets fn-1  ASSERTION: Lots were small." in text and "QUOTES: lots of thirty bu" in text
    assert "cities/tango fn-9  ASSERTION: (none found beside the note)" in text
    assert "== gamma" in text and "NOT IN THE REGISTRY" in text and "-- cited by 0 footnotes" in text


def test_a_translated_passage_carries_its_original() -> None:
    cites = '<li id="fn-4"><a href="https://example.org/k"><code>k</code></a> -「a wet field」 (translated from the Japanese by this project; original: 「湿田」)</li>'
    text = se.render({"entries": {"k": ["K"]}, "notes": {"k": [{**se.citing(cites, "", {"k"})[0], "page": "fields"}]}})
    assert "QUOTES: a wet field  [original, the Japanese: 湿田]" in text and "-- cited by 1 footnote\n" in text


def test_main(tmp_path: pathlib.Path, capsys) -> None:  # noqa: ANN001
    root = _tree(tmp_path)
    assert se.main(["alpha-survey, alpha-survey", "--root", str(root)]) == 0
    assert capsys.readouterr().out.count("== alpha-survey") == 1
    assert se.main([" , ", "--root", str(root)]) == 2
    assert "no key given" in capsys.readouterr().err
