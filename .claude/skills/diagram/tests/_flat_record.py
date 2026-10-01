"""A small record in the flat layout of feature 303, for the tests to build, break and read.

Two sections under two containers, one leaf a container's only child; four stems: a research page with its drawing page,
a research page alone, a research page in the other section carrying a subject that is no section, and a second drawing
page that says which question it draws. A registry with one group of two entries, the assets, one confusable pair.
"""

from __future__ import annotations

import json
import pathlib

TAGS = {
    "subject": {
        "ways": {"name": "Ways", "description": "Roads and lanes."},
        "fabric": {"name": "Urban fabric", "description": "A city's streets."},
        "samurai": {"name": "Samurai", "description": "Where samurai lived."},
    },
    "setting": {"countryside": {"name": "The countryside", "description": "Villages."}, "city": {"name": "Cities", "description": "Cities."}},
    "level": [{"id": "foundational", "name": "Foundational", "description": "First."}, {"id": "detail", "name": "Details", "description": "Then."}],
}
CONTENTS = {
    "sections": [
        {
            "id": "countryside",
            "title": "The countryside",
            "description": "<p><em>The land.</em></p>",
            "drawing_description": "<p><em>Drawn land.</em></p>",
            "takes": [],
            "sections": [
                {"id": "ways", "title": "Ways", "description": "<p><em>Roads.</em></p>", "drawing_description": "", "takes": [{"primary": "ways"}], "sections": []},
            ],
        },
        {
            "id": "cities",
            "title": "Cities",
            "description": "",
            "drawing_description": "",
            "takes": [],
            "sections": [
                {"id": "fabric", "title": "Urban fabric", "description": "", "drawing_description": "", "takes": [{"primary": "fabric"}], "sections": []},
            ],
        },
    ]
}
TAIL = "</main>\n</body>\n</html>\n"
FRONT = '<!DOCTYPE html>\n<html>\n<body>\n<main>\n<h1 id="{0}">{1}</h1>\n<p id="{0}-intro"><em>{1}, the intro.</em></p>\n<hr>\n'
QUESTIONS = {
    "0001-lanes.html": (
        '<h2 id="lanes">Lanes</h2>\n<!-- tags: subject=ways; setting=countryside; level=foundational -->\n'
        '<p>A lane is narrow.<sup class="fn" data-note="alpha"></sup> See <a href="0003-rows.html">the rows</a> and'
        ' <a href="0002-bridges.html#span">a span</a> and <a href="https://x.org">out</a>.<!-- <a href="nowhere.html">x</a> --></p>\n'
    ),
    "0001-lanes.notes.html": '<li data-note="alpha"><a href="https://a"><code>alpha</code></a> - 「q」</li>\n',
    "0001-lanes.drawing.html": '<h2 id="drawing-lanes">How our maps draw lanes</h2>\n<p>Our maps draw a lane thin.<sup class="fn" data-note="beta"></sup></p>\n',
    "0001-lanes.drawing.notes.html": '<li data-note="beta"><a href="../SOURCES.html#beta"><code>beta</code></a> - 「r」</li>\n',
    "0002-bridges.html": (
        '<h2 id="bridges">Bridges</h2>\n<!-- tags: subject=ways; setting=countryside; level=detail -->\n'
        '<p id="span">One span.<sup class="fn" data-note="beta"></sup> Again.<sup class="fn" data-note="beta"></sup>'
        ' <a href="#span">here</a> <a href="../SOURCES.html#alpha">a source</a> <img src="../assets/x.png"></p>\n'
    ),
    "0002-bridges.notes.html": '<li data-note="beta"><a href="../SOURCES.html#beta"><code>beta</code></a> - 「r」</li>\n',
    "0003-rows.html": ('<h2 id="rows">Rows</h2>\n<!-- tags: subject=fabric,samurai; setting=city; level=foundational -->\n<p>Shops in a row. <a href="0002-bridges.html">b</a></p>\n'),
    "0004-wide-lanes.drawing.html": '<h2 id="wide-lanes">How our maps draw a wide lane</h2>\n<!-- about: 0001-lanes -->\n<p>Wider.</p>\n',
}


def write(tmp: pathlib.Path) -> pathlib.Path:
    """The record, written under `tmp`; returns `tmp`."""
    (tmp / "tags.json").write_text(json.dumps(TAGS), encoding="utf-8")
    (tmp / "contents.json").write_text(json.dumps(CONTENTS), encoding="utf-8")
    (tmp / "confusables.json").write_text(json.dumps([{"a": "0001-lanes.html#lanes", "b": "0003-rows.html#rows", "why": "both narrow"}]), encoding="utf-8")
    q = tmp / "questions"
    q.mkdir(parents=True)
    for name, text in QUESTIONS.items():
        (q / name).write_text(text, encoding="utf-8")
    src = tmp / "sources"
    (src / "010-works-cited").mkdir(parents=True)
    (src / "_front.html").write_text(FRONT.format("sources", "Sources"), encoding="utf-8")
    (src / "_tail.html").write_text(TAIL, encoding="utf-8")
    (src / "010-works-cited.html").write_text('<h2 id="works-cited">Works cited</h2>\n<p>Every work.</p>\n', encoding="utf-8")
    for n, key, url in ((10, "alpha", "https://a"), (20, "beta", "https://b; SUMMARY-ONLY")):
        (src / "010-works-cited" / f"00{n}-{key}.html").write_text(
            f'<h3 id="{key}"><code>{key}</code></h3>\n<p>{key.title()}, a work ({url})</p>\n<p><em>What it is:</em> a work.</p>\n<p><em>Why it applies, and its limits:</em> it does.</p>\n',
            encoding="utf-8",
        )
    (tmp / "assets").mkdir()
    for name in ("record.css", "record.js", "site.css", "site.js"):
        (tmp / "assets" / name).write_text(f"/* {name} */", encoding="utf-8")
    return tmp


def edit(rec: pathlib.Path, name: str, old: str, new: str) -> None:
    """Replace `old` with `new` in one question file, refusing when `old` is not there."""
    path = rec / "questions" / name
    text = path.read_text(encoding="utf-8")
    assert old in text, (name, old)
    path.write_text(text.replace(old, new), encoding="utf-8")
