//! *Not to be confused with:* (feature 449 T144; each expected value `confusables.py`'s on the same record, 2026-11-16).

use super::{definition, entries, load, title, write, Pair};
use crate::fixture::{put, record};
use crate::record::questions;

#[test]
fn a_pair_writes_an_entry_under_both_sections() {
    let dir = record();
    let r = questions::load(&dir).unwrap();
    let pairs = load(&dir).unwrap();
    assert_eq!(
        pairs,
        [Pair {
            a: "0001-paddies.html#paddies".into(),
            b: "0002-coins.html#coins".into()
        }]
    );
    let coins = r.by_file("0002-coins.html").unwrap();
    assert_eq!(
        entries("0002-coins.html", &pairs, &r),
        [("coins".to_owned(), vec!["<li><a href=\"0001-paddies.html\">Paddies wet (researched 2026-08-27, feature 133)</a> - Paddies are wet.</li>".to_owned()])]
    );
    assert_eq!(
        write(&coins.text, "0002-coins.html", &pairs, &r),
        "<h2 id=\"coins\">Coins</h2>\n<div class=\"confusables\"><p><em>Not to be confused with:</em></p>\n<ul>\n<li><a href=\"0001-paddies.html\">Paddies wet (researched 2026-08-27, feature 133)</a> - Paddies are wet.</li>\n</ul></div>\n<!-- tags: subject=money; setting=town; level=foundational -->\n<!-- a comment --><p>Coins are <b>round</b>&amp; flat! More.</p>\n"
    );
    // a pair naming no section writes an entry with no title or gloss, under a heading the page lacks, which is skipped
    let odd = [
        Pair {
            a: "0002-coins.html#nowhere".into(),
            b: "x.html#y".into(),
        },
        Pair {
            a: "0002-coins.html#coins".into(),
            b: "x.html#y".into(),
        },
    ];
    assert_eq!(
        entries("0002-coins.html", &odd, &r)[1].1,
        ["<li><a href=\"x.html\"></a></li>"]
    );
    assert!(write(&coins.text, "0002-coins.html", &odd, &r)
        .contains("<li><a href=\"x.html\"></a></li>"));
    let both = [
        Pair {
            a: "0002-coins.html#coins".into(),
            b: "0001-paddies.html#paddies".into(),
        },
        Pair {
            a: "0002-coins.html#coins".into(),
            b: "x.html#y".into(),
        },
    ];
    assert_eq!(entries("0002-coins.html", &both, &r)[0].1.len(), 2);
    assert_eq!(
        definition("<p>No sentence end here</p>"),
        "No sentence end here"
    );
    assert_eq!(definition("<h2 id='x'>T</h2>"), "");
    assert_eq!(title("none"), "");
}

#[test]
fn the_pairs_file_is_read_as_the_python_reads_it() {
    let dir = record();
    std::fs::remove_file(dir.join("confusables.json")).unwrap();
    assert!(load(&dir).unwrap().is_empty());
    for (text, kind, message) in [
        ("[5]", "TypeError", "'int' object is not subscriptable"),
        ("[{\"a\": \"x\"}]", "KeyError", "'b'"),
        (
            "{\"a\": \"x\", \"b\": \"y\"}",
            "TypeError",
            "string indices must be integers, not 'str'",
        ),
        (
            "\"ab\"",
            "TypeError",
            "string indices must be integers, not 'str'",
        ),
        (
            "[[1]]",
            "TypeError",
            "list indices must be integers or slices, not str",
        ),
        ("3", "TypeError", "'int' object is not iterable"),
        ("nope", "JSONDecodeError", ""),
    ] {
        put(&dir, "confusables.json", text);
        let e = load(&dir).unwrap_err();
        assert_eq!(e.kind, kind, "{text}");
        if !message.is_empty() {
            assert_eq!(e.message, message, "{text}");
        }
    }
}
