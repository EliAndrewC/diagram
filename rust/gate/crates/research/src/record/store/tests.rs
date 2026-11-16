//! The record on disk (feature 449 T144; each expected value `store.py`'s on the same record, 2026-11-16).

use super::{
    entry_level, load, page_html, page_notes, read_fragments, registry_html, shared,
    split_originals, REGISTRY,
};
use crate::fixture::{put, record};

const PADDIES_HTML: &str = "<h2 id=\"paddies\"><span class=\"xref\"><a href=\"0001-paddies.drawing.html\">How it's drawn</a> - <a href=\"0003-more-drawn.drawing.html\">How it's drawn</a></span>Paddies <em>wet</em> (researched 2026-08-27, feature 133)</h2>\n<div class=\"confusables\"><p><em>Not to be confused with:</em></p>\n<ul>\n<li><a href=\"0002-coins.html\">Coins</a> - Coins are round&amp; flat!</li>\n</ul></div>\n<!-- tags: subject=farming; setting=countryside; level=detail -->\n<p>Paddies are wet. They hold water.<sup class=\"fn\" data-note=\"k\"></sup> See https://e.org/b).</p>\n<p>Again.<sup class=\"fn\" data-note=\"k\"></sup><sup class=\"fn\" data-note=\"n\"></sup></p>\n";

/// What the Python's `page_notes` gives the fixture's first page: the original put back, the passages listed, the absence's words.
pub const PADDIES_NOTES: [(&str, &str); 2] = [
    ("k", "<a href=\"https://e.org/a\"><code>src-a</code></a><span class=\"sep\"> - </span><span class=\"passages\"><span class=\"pass\">\"one\"</span><span class=\"sep\"> ; </span><span class=\"pass\">\"two\" <span class=\"orig\">original: \u{300c}\u{539f}\u{300d}</span></span></span>"),
    ("n", "<span class=\"sep\">no publicly readable source</span><span class=\"absence-lead\">Our research of publicly-available sources couldn't find anything conclusive:</span><!-- searched 2026-09-28 --> nothing"),
];

#[test]
fn a_question_page_and_its_notes() {
    let dir = record();
    let r = load(&dir).unwrap();
    let paddies = r.by_file("0001-paddies.html").unwrap();
    assert_eq!(page_html(&r, paddies, &dir, None).unwrap(), PADDIES_HTML);
    let tables = shared(&r, &dir).unwrap();
    assert_eq!(
        page_html(&r, r.by_file("0003-more-drawn.drawing.html").unwrap(), &dir, Some(&tables)).unwrap(),
        "<h2 id=\"more-drawn\"><span class=\"xref\"><a href=\"0001-paddies.html\">The history behind it</a></span>More drawn</h2>\n<!-- about: 0001-paddies -->\n<p>x</p>\n"
    );
    let notes = page_notes("0001-paddies.html", &dir).unwrap();
    let want: Vec<(String, String)> = PADDIES_NOTES
        .iter()
        .map(|(k, b)| ((*k).into(), (*b).into()))
        .collect();
    assert_eq!(notes, want);
    assert!(page_notes("0002-coins.html", &dir).unwrap().is_empty());
    assert_eq!(entry_level(REGISTRY), Some(3));
    assert_eq!(entry_level("x"), None);
}

#[test]
fn the_registry_assembles_from_its_fragments() {
    let dir = record();
    let html = registry_html(&dir).unwrap();
    assert!(html.starts_with(
        "<html><body><main>\n<h2 id=\"works-cited\">Works cited</h2>\n<h3 id=\"work-src-a\">"
    ));
    assert!(html.ends_with(
        "<p>https://banned.example.org/p and https://e.org/a.</p>\n\n</main>\n</body>\n</html>\n"
    ));
    let page = read_fragments(REGISTRY, &dir).unwrap();
    assert_eq!(page.sections[0].entries.len(), 3);
    std::fs::create_dir(dir.join("sources/zz-dir")).unwrap();
    assert!(read_fragments(REGISTRY, &dir).is_ok());
}

#[test]
fn every_registry_refusal() {
    let cases: [(&str, &str, &str); 6] = [
        ("sources/notes.txt", "x", "sources/notes.txt: not a fragment name. A page directory holds _front.html, _tail.html and <prefix>-<heading id>.html, and nothing else"),
        ("sources/010-again.html", "<h2 id=\"again\">x</h2>", "sources/: 010-again.html and 010-works-cited.html both claim prefix 010 - the assembly will not choose between them"),
        ("sources/010-works-cited/0001-aaa.html", "<h3 id=\"work-bbb\">x</h3>", "sources/010-works-cited/0001-aaa.html: its filename says `aaa` and its heading registers `bbb` - one of the two is wrong"),
        ("sources/010-works-cited/0001-ccc.html", "<h3>x</h3>", "a heading with no id at offset 0: '<h3>' - the record's anchors are heading ids, and a fragment is named for one"),
        ("sources/_front.html", "", ""),
        ("sources/010-works-cited/zzz.html", "x", "sources/010-works-cited/zzz.html: not a fragment name. A page directory holds _front.html, _tail.html and <prefix>-<heading id>.html, and nothing else"),
    ];
    for (rel, text, want) in cases {
        let dir = record();
        put(&dir, rel, text);
        let got = read_fragments(REGISTRY, &dir).map_or_else(|e| e.message, |_| String::new());
        assert_eq!(got, want, "{rel}");
    }
    let dir = record();
    std::fs::remove_file(dir.join("sources/_front.html")).unwrap();
    std::fs::remove_file(dir.join("sources/_tail.html")).unwrap();
    assert_eq!(
        registry_html(&dir).unwrap_err().message,
        "sources/: _front.html and _tail.html missing - a page's front matter and its closing are fragments like any other, and the assembly will not invent them"
    );
    std::fs::remove_dir_all(dir.join("sources")).unwrap();
    assert_eq!(
        registry_html(&dir).unwrap_err().message,
        "sources/: no fragment directory for SOURCES.html"
    );
}

#[test]
fn every_notes_refusal() {
    let cases: [(&str, Option<&str>, &str); 4] = [
        ("<li data-note=\"k\">\"a\" <span class=\"orig\" data-orig=\"k#1\"></span></li>", None, "questions/0001-paddies.notes.html: a note holds an original's placeholder and 0001-paddies.originals.html is missing"),
        ("<li data-note=\"k\">\"a\" <span class=\"orig\" data-orig=\"k#1\"></span></li>", Some("<li data-orig=\"k#2\">x</li>"), "questions/0001-paddies.notes.html: no original stored for `k#1` - its `.originals.html` lacks `<li data-orig=\"k#1\">`"),
        ("<li data-note=\"k\">a</li><li data-note=\"k\">b</li>", None, "questions/0001-paddies.notes.html: `k` is defined twice in one file"),
        ("<li data-note=\"Bad\">a</li>", None, "questions/0001-paddies.notes.html: `Bad` is not a note key - lower case, digits and hyphens"),
    ];
    for (notes, originals, want) in cases {
        let dir = record();
        put(&dir, "questions/0001-paddies.notes.html", notes);
        std::fs::remove_file(dir.join("questions/0001-paddies.originals.html")).unwrap();
        if let Some(o) = originals {
            put(&dir, "questions/0001-paddies.originals.html", o);
        }
        let e = page_notes("0001-paddies.html", &dir).unwrap_err();
        assert_eq!((e.kind, e.message.as_str()), ("RecordError", want));
    }
}

#[test]
fn an_inline_original_is_moved_once() {
    let dir = record();
    put(&dir, "questions/0002-coins.notes.html", "<li data-note=\"k\">\"a\" (translated; original: \u{300c}\u{539f}\u{6587}\u{300d}) and original: \u{300c}B\u{300d}</li>\n");
    assert_eq!(
        split_originals(&dir, false).unwrap(),
        ["questions/0002-coins.notes.html"]
    );
    assert_eq!(
        split_originals(&dir, true).unwrap(),
        ["questions/0002-coins.notes.html"]
    );
    assert!(split_originals(&dir, true).unwrap().is_empty());
    assert_eq!(
        std::fs::read_to_string(dir.join("questions/0002-coins.notes.html")).unwrap(),
        "<li data-note=\"k\">\"a\" (translated; <span class=\"orig\" data-orig=\"k#1\"></span>) and <span class=\"orig\" data-orig=\"k#2\"></span></li>\n"
    );
    assert_eq!(
        std::fs::read_to_string(dir.join("questions/0002-coins.originals.html")).unwrap(),
        "<li data-orig=\"k#1\">original: \u{300c}\u{539f}\u{6587}\u{300d}</li>\n<li data-orig=\"k#2\">original: \u{300c}B\u{300d}</li>\n"
    );
    put(
        &dir,
        "questions/0002-coins.originals.html",
        "<li data-orig=\"k\">o</li>",
    );
    assert_eq!(split_originals(&dir, false).unwrap_err().kind, "ValueError");
    std::fs::remove_dir_all(dir.join("questions")).unwrap();
    assert!(split_originals(&dir, false).unwrap().is_empty());
    // the originals file a directory: read as none, then written, which the file system refuses (Python's `IsADirectoryError`)
    let dir = record();
    put(
        &dir,
        "questions/0002-coins.notes.html",
        "<li data-note=\"k\">original: \u{300c}B\u{300d}</li>",
    );
    std::fs::create_dir(dir.join("questions/0002-coins.originals.html")).unwrap();
    assert_eq!(split_originals(&dir, true).unwrap_err().kind, "OSError");
}

#[test]
fn what_the_store_refuses_of_the_whole() {
    let dir = record();
    put(&dir, "contents.json", "nope");
    let e = load(&dir).unwrap_err();
    assert_eq!(e.kind, "RecordError");
    assert!(e.message.starts_with("contents.json: not JSON ("));
    let dir = record();
    std::fs::write(dir.join("questions/0001-paddies.html"), [0xff_u8]).unwrap();
    assert_eq!(load(&dir).unwrap_err().kind, "OSError");
    let dir = record();
    put(&dir, "confusables.json", "[{\"a\": \"nope.html#x\", \"b\": \"nope.html#x\"}, {\"a\": \"0002-coins.html#coins\", \"b\": \"0002-coins.html#wrong\"}]");
    let r = load(&dir).unwrap();
    assert_eq!(
        shared(&r, &dir).unwrap_err().message,
        "confusables.json names a section that does not exist:\n  `nope.html#x` is paired with itself\n  `nope.html#x` (paired with `nope.html#x`) - no such section\n  `nope.html#x` (paired with `nope.html#x`) - no such section\n  `0002-coins.html#wrong` (paired with `0002-coins.html#coins`) - no such section"
    );
    assert!(page_html(&r, r.by_file("0002-coins.html").unwrap(), &dir, None).is_err());
}
