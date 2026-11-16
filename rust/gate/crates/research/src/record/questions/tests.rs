//! The questions loaded, tagged and homed (feature 449 T144; each expected value `questions.py`'s on the same record, 2026-11-16).

use super::{digits_value, heading, load, text_of};
use crate::fixture::{put, record};

fn files(pages: &[&super::Page]) -> Vec<String> {
    pages.iter().map(|p| p.file.clone()).collect()
}

#[test]
fn the_fixture_record_loads_as_the_python_loads_it() {
    let dir = record();
    let r = load(&dir).unwrap();
    let q: Vec<(u64, &str, Option<&str>, Option<&str>)> = r
        .questions
        .iter()
        .map(|q| {
            (
                q.number,
                q.stem.as_str(),
                q.about.as_deref(),
                q.home.as_deref(),
            )
        })
        .collect();
    assert_eq!(
        q,
        [
            (1, "0001-paddies", None, Some("land")),
            (2, "0002-coins", None, Some("coin")),
            (3, "0003-more-drawn", Some("0001-paddies"), Some("land"))
        ]
    );
    let first = r.by_file("0001-paddies.html").unwrap();
    assert_eq!(
        first.title,
        "Paddies wet (researched 2026-08-27, feature 133)"
    );
    assert_eq!(
        (first.notes_file(), first.originals_file(), first.half()),
        (
            "0001-paddies.notes.html".into(),
            "0001-paddies.originals.html".into(),
            "research"
        )
    );
    assert_eq!(
        r.by_file("0001-paddies.drawing.html").unwrap().half(),
        "drawing"
    );
    assert_eq!(r.by_id("coins").unwrap().file, "0002-coins.html");
    assert!(r.by_stem("0009-none").is_none());
    assert_eq!(r.files().len(), 4);
    assert_eq!(r.ids()[0], (&"coins".to_owned(), "0002-coins.html"));
    assert_eq!(r.question_of(first).stem, "0001-paddies");
    assert_eq!(r.questions[2].tags, r.questions[0].tags);
    assert_eq!(
        files(&r.select("0001 coins, detail land nothing")),
        [
            "0001-paddies.html",
            "0001-paddies.drawing.html",
            "0003-more-drawn.drawing.html"
        ]
    );
    assert_eq!(files(&r.select("0002-coins.html")), ["0002-coins.html"]);
    assert_eq!(files(&r.select("coin")), ["0002-coins.html"]);
    assert_eq!(
        files(&r.in_section("land", "research")),
        ["0001-paddies.html"]
    );
    assert_eq!(r.pages(Some("drawing")).len(), 2);
    assert!(r.holds(&r.sections[0], "drawing"));
    assert!(!r.holds(&r.sections[1], "drawing"));
    let above = super::Section {
        id: "above".into(),
        sections: vec![r.sections[0].clone()],
        ..r.sections[1].clone()
    };
    assert!(r.holds(&above, "research"));
}

#[test]
fn the_page_readers() {
    assert_eq!(text_of("<a><span class=\"xref\">x</span>A \n b</a>"), "A b");
    assert_eq!(
        heading("<!-- <h2 id=\"c\">C</h2> --><h2 id=\"a\">A\nb</h2>"),
        Some(("a".into(), "A\nb".into()))
    );
    assert_eq!(heading("none"), None);
    assert_eq!(digits_value("0\u{0661}2"), 12);
}

/// Each broken record, the refusal the Python gave for it.
#[test]
fn every_refusal_is_gathered_and_named() {
    let cases: [(&str, &str, &str); 13] = [
        ("questions/0990-paddies-drawn.html", "<h2 id=\"paddies-drawn\">T</h2>\n<!-- tags: subject=money; setting=town; level=detail -->", "questions/0990-paddies-drawn.html: heading id `paddies-drawn` is also 0001-paddies.drawing.html's"),
        ("questions/README.txt", "x", "questions/README.txt: not a question's file - NNNN-<slug>.html, .drawing.html, and their .notes.html and .originals.html"),
        ("questions/0001-other.html", "<h2 id=\"other\">x</h2>", "questions/0001-paddies.drawing.html: number 0001 is already 0001-other - a number names one question"),
        ("questions/0999-nohead.html", "<p>none</p>", "questions/0999-nohead.html: no `<h2 id=...>` heading"),
        ("questions/0998-lonely.notes.html", "", "questions/0998-lonely.notes.html: beside no page - 0998-lonely.html does not exist"),
        ("questions/0997-one.html", "<h2 id=\"two\">T</h2>\n<!-- tags: subject=farming; setting=countryside; level=detail -->", "questions/0997-one.html: its name says `one` and its heading is `two` - the slug is the heading id"),
        ("questions/0996-untagged.html", "<h2 id=\"untagged\">T</h2>", "questions/0996-untagged.html: no tags - a research page states `<!-- tags: subject=<subject>; setting=<setting>; level=<level> -->` on the line after its heading"),
        ("questions/0995-ab.html", "<h2 id=\"ab\">T</h2>\n<!-- tags: subject=farming; setting=countryside; level=detail -->\n<!-- about: 0001-x -->", "questions/0995-ab.html: an `about:` on a research page - only a lone drawing page names the question it is about"),
        ("questions/0994-lb.drawing.html", "<h2 id=\"lb\">T</h2>\n<!-- tags: subject=farming; setting=countryside; level=detail -->\n<!-- about: 0001-x -->", "questions/0994-lb.drawing.html: states both tags and an `about:` - it inherits from the question it is about, or is a question of its own"),
        ("questions/0993-ln.drawing.html", "<h2 id=\"ln\">T</h2>", "questions/0993-ln.drawing.html: no tags and no `about:` - a drawing page alone in its stem says which question it draws, or states its own tags"),
        ("questions/0992-la.drawing.html", "<h2 id=\"la\">T</h2>\n<!-- about: 0002-nothing -->", "questions/0992-la.drawing.html: `about: 0002-nothing` names no research question"),
        ("questions/0002-coins.drawing.html", "<h2 id=\"cd\">T</h2>\n<!-- about: 0001-paddies -->", "questions/0002-coins.drawing.html: states an about: - a drawing page beside its research page inherits its tags"),
        ("questions/0991-coins.drawing.html", "<h2 id=\"coins\">T</h2>\n<!-- tags: subject=money; setting=town; level=detail -->", "questions/0991-coins.drawing.html: heading id `coins` is also 0002-coins.html's"),
    ];
    for (rel, text, want) in cases {
        let dir = record();
        put(&dir, rel, text);
        let e = load(&dir).unwrap_err();
        assert_eq!(e.kind, "QuestionError");
        assert!(e.message.contains(want), "{rel}: {}", e.message);
    }
    let dir = record();
    put(
        &dir,
        "questions/0990-bt.html",
        "<h2 id=\"bt\">T</h2>\n<!-- tags: subject=nope; setting=town; level=detail -->",
    );
    put(
        &dir,
        "questions/0989-ds.html",
        "<h2 id=\"ds\">T</h2>\n<!-- tags: subject=farming; setting=town; level=detail -->",
    );
    put(
        &dir,
        "questions/0989-ds.drawing.html",
        "<h2 id=\"ds-d\">T</h2>\n<!-- tags: subject=farming; setting=town; level=detail -->",
    );
    put(
        &dir,
        "questions/0988-lo.drawing.html",
        "<h2 id=\"lo\">T</h2>\n<!-- tags: subject=money; setting=countryside; level=detail -->",
    );
    let e = load(&dir).unwrap_err().message;
    assert!(e.starts_with("the questions do not load (2 refusal(s)):\n  "));
    assert!(e.contains("questions/0989-ds.drawing.html: states tags - a drawing page beside its research page inherits its tags"));
    let dir = record();
    put(&dir, "contents.json", "{\"sections\": [{\"id\": \"only\", \"title\": \"T\", \"takes\": [{\"primary\": \"money\"}]}]}");
    assert!(load(&dir).unwrap_err().message.contains("questions/0001-paddies: tags <!-- tags: subject=farming; setting=countryside; level=detail --> - no section of contents.json takes them"));
    let dir = record();
    std::fs::remove_file(dir.join("tags.json")).unwrap();
    assert_eq!(load(&dir).unwrap_err().kind, "ContentsError");
    let dir = record();
    std::fs::remove_dir_all(dir.join("questions")).unwrap();
    assert_eq!(
        load(&dir).unwrap_err().message,
        "the questions do not load (3 refusal(s)):\n  contents.json section `land`: the clause {\"primary\": [\"farming\"]} matches no question\n  contents.json section `fields`: the clause {\"level\": [\"detail\"], \"subject\": [\"farming\"]} matches no question\n  contents.json section `coin`: the clause {\"primary\": [\"money\"], \"setting\": [\"town\", \"countryside\"]} matches no question"
    );
    let dir = record();
    std::fs::write(dir.join("questions/0001-paddies.html"), [0xff_u8]).unwrap();
    assert_eq!(load(&dir).unwrap_err().kind, "OSError");
}
