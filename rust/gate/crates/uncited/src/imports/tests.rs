//! The imported copies (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record), on a browser
//! answering from tables.

use l7r_gate_archive::testkit::Fake;
use serde_json::json;

use super::*;
use crate::testkit::{long, quiet, starter, Said, W};

#[test]
fn a_read_less_than_its_copy_and_two_texts_of_one_page() {
    assert!(garbled(&format!(
        "{}{}",
        "a".repeat(98),
        "\u{fffd}\u{fffd}"
    )));
    assert!(!garbled(&format!("{}{}", "a".repeat(99), "\u{fffd}")));
    assert!(!garbled("\u{fffd}"));
    assert!(worse_read(&"x".repeat(100), &"x".repeat(49)));
    assert!(!worse_read(&"x".repeat(100), &"x".repeat(50)));
    assert!(worse_read(
        &"日本語のページ".repeat(10),
        &format!("{}{}", "english ".repeat(30), "日本")
    ));
    assert!(!worse_read(&"日本語".repeat(10), &"日本語".repeat(10)));
    assert!(same_page(&long("one page", 50), &long("one page", 40)));
    assert!(!same_page(&long("one page", 50), "another text entirely"));
    assert!(!same_page("", "x"));
}

fn fake() -> Fake {
    let mut f = Fake::default();
    f.serve(
        "https://i.org/same",
        200,
        "text/plain",
        "alpha beta gamma ".repeat(160).as_bytes(),
    );
    f.serve(
        "https://i.org/other",
        200,
        "text/plain",
        "zebra quantum ".repeat(250).as_bytes(),
    );
    f.serve("https://i.org/short", 200, "text/plain", b"short");
    f.serve(
        "https://i.org/garbled",
        200,
        "text/plain",
        "\u{fffd}".repeat(200).as_bytes(),
    );
    f
}

#[test]
fn verify_reads_each_imported_copy_live() {
    let w = W::new("imports-verify");
    for (u, t) in [
        ("https://i.org/same", "alpha beta gamma ".repeat(150)),
        ("https://i.org/other", "imported ".repeat(300)),
        ("https://i.org/short", long("short", 10)),
        ("https://i.org/garbled", long("g", 100)),
    ] {
        w.page(u, &t, "import-288");
    }
    w.page("https://i.org/fetched", "a fetched page", "fetch");
    let said = Said::default();
    let start = starter(fake);
    let urls: Vec<String> = [
        "https://i.org/same",
        "https://i.org/other",
        "https://i.org/short",
        "https://i.org/garbled",
        "https://i.org/fetched",
        "https://i.org/none",
    ]
    .iter()
    .map(|u| (*u).to_owned())
    .collect();
    assert_eq!(
        verify(w.root(), &urls, &start, &|l| said.say(l)).unwrap(),
        [1, 1, 2]
    );
    assert_eq!(
        said.all(),
        [
            "same       https://i.org/same",
            "misfiled   https://i.org/other",
            "unread     https://i.org/short",
            "unread     https://i.org/garbled"
        ]
    );
    let d = l7r_gate_research::pages::entry_dir(w.home(), "https://i.org/other");
    assert_eq!(
        std::fs::read_to_string(d.join("imported.txt")).unwrap(),
        "imported ".repeat(300)
    );
    assert_eq!(imported(w.home(), "https://i.org/other").unwrap(), None);
    assert!(imported(w.home(), "https://i.org/short").unwrap().is_some());
    let checks = w.read(MISFILED);
    assert_eq!(checks.lines().count(), 4);
    assert!(checks.contains("\"result\": \"misfiled\""));
    // the lanes summed; a blocked page is the run's error, as the Python's pool raised it
    w.page(
        "https://i.org/same",
        &"alpha beta gamma ".repeat(150),
        "import-288",
    );
    let total = verify_all(
        w.root(),
        &["https://i.org/same".to_owned()],
        3,
        &start,
        &quiet,
    )
    .unwrap();
    assert_eq!(total, json!({"same": 1, "misfiled": 0, "unread": 0}));
    // a blocked page the import once saved (the cache's writer refuses one now, so it is written as it was)
    let d = l7r_gate_research::pages::entry_dir(w.home(), "https://grokipedia.com/p");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(
        d.join("meta.json"),
        r#"{"fetched": "2026-01-01T00:00:00+00:00", "origin": "import-288"}"#,
    )
    .unwrap();
    std::fs::write(d.join("text.txt"), "x").unwrap();
    assert!(verify_all(
        w.root(),
        &["https://grokipedia.com/p".to_owned()],
        1,
        &start,
        &quiet
    )
    .is_err());
}

#[test]
fn the_imported_urls_and_the_verdicts_that_blame_a_copy() {
    let w = W::new("imports-verdicts");
    w.page(
        "https://i.org/a",
        &long("a page read live", 300),
        "import-288",
    );
    w.page("https://i.org/b", "short", "fetch");
    w.page("ftp://i.org/c", "x", "import-288");
    std::fs::create_dir_all(w.home().join("page-cache/00/no-meta")).unwrap();
    assert_eq!(imported_urls(w.home()).unwrap(), ["https://i.org/a"]);
    w.lines(NOT_KEPT, &[
        json!({"url": "i.org/a", "raw": "https://i.org/a", "reasons": ["unreadable"], "note": "mojibake in the saved copy", "basis": "source-filter"}),
        json!({"url": "i.org/b", "raw": "https://i.org/b", "reasons": ["off-topic"], "note": "a shell", "basis": "source-filter"}),
        json!({"url": "i.org/d", "raw": "https://i.org/d", "reasons": ["off-topic"], "note": "fine", "basis": "rule"}),
        json!({"url": "i.org/e", "raw": "https://i.org/e", "reasons": ["off-topic"], "note": "a garbled shell", "basis": "source-filter"}),
    ]);
    w.lines(
        MISFILED,
        &[
            json!({"url": "i.org/a", "raw": "https://i.org/a", "result": "misfiled"}),
            json!({"url": "i.org/b", "raw": "https://i.org/b", "result": "same"}),
            json!({"url": "i.org/d", "raw": "https://i.org/d", "result": "same"}),
            json!({"url": "i.org/e", "raw": "https://i.org/e", "result": "unread"}),
        ],
    );
    assert_eq!(
        copy_verdicts(w.root()).unwrap(),
        ["https://i.org/a  (unreadable: mojibake in the saved copy)"]
    );
    stands(w.root(), "https://i.org/a", "read: it stands").unwrap();
    assert!(copy_verdicts(w.root()).unwrap().is_empty());
    assert!(w
        .read(MISFILED)
        .contains("\"result\": \"verdict-stands\", \"note\": \"read: it stands\""));
    w.lines(MISFILED, &[json!({"url": "i.org/a"})]);
    assert_eq!(copy_verdicts(w.root()).unwrap_err().kind, "KeyError");
    let meta = l7r_gate_research::pages::entry_dir(w.home(), "https://i.org/a").join("meta.json");
    std::fs::write(&meta, "[]").unwrap();
    assert_eq!(imported_urls(w.home()).unwrap_err().kind, "AttributeError");
}
