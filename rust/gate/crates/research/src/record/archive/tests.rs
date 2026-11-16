//! The source archive as the build sees it (feature 449 T144; each expected value `archive.py`'s on the same record, 2026-11-16).

use serde_json::json;

use super::{
    cited, copy_link, covered, entry_bodies, entry_line, iso_day, load, refusals, today_utc,
    url_id, urls_in, Cited,
};
use crate::fixture::{put, record};

#[test]
fn what_the_record_cites_and_what_the_archive_holds() {
    let dir = record();
    let got = cited(&dir).unwrap();
    let urls: Vec<&str> = got.iter().map(|(u, _)| u.as_str()).collect();
    assert_eq!(
        urls,
        [
            "https://e.org/a",
            "https://e.org/a2",
            "https://github.com/x/l7r.md",
            "https://grokipedia.com/page/X"
        ]
    );
    assert_eq!(
        got[0].1,
        Cited {
            keys: vec!["work-src-a".into()],
            notes: vec!["0001-paddies.notes.html".into()]
        }
    );
    assert_eq!(
        urls_in(
            "a https://e.org/x). <!-- https://h.org --> https://e.org/x",
            false
        ),
        ["https://e.org/x"]
    );
    assert_eq!(urls_in("<!-- https://h.org -->", true), ["https://h.org"]);
    let mut want = vec![
        "archive: https://e.org/a2 (work-src-a) has no archived copy - `make archive URL='https://e.org/a2'` archives it (feature 309)".to_owned(),
        "archive: https://github.com/x/l7r.md (l7r-notes) has no archived copy - `make archive URL='https://github.com/x/l7r.md'` archives it (feature 309)".to_owned(),
        "archive: https://grokipedia.com/page/X (work-grok) has no archived copy - `make archive URL='https://grokipedia.com/page/X'` archives it (feature 309)".to_owned(),
    ];
    let uid = url_id("https://e.org/a");
    assert_eq!(uid, "870874689b29");
    put(
        &dir,
        &format!("archive/{}/{uid}.json", &uid[..2]),
        "{\"outcome\": \"pending-upload\", \"captured\": \"2026-11-01T00:00:00Z\"}",
    );
    want.insert(0, "archive: https://e.org/a (work-src-a) has its upload pending since 2026-11-01 - `make archive URL='https://e.org/a'` archives it (feature 309)".to_owned());
    assert_eq!(refusals(&dir, Some("2026-11-20")).unwrap(), want);
    assert_eq!(refusals(&dir, Some("2026-11-02")).unwrap().len(), 3);
    // a URL only a footnote links is named by its notes file
    put(
        &dir,
        "questions/0002-coins.notes.html",
        "<li data-note=\"m\">https://n.org/only</li>",
    );
    assert!(refusals(&dir, Some("2026-11-02")).unwrap()[3]
        .starts_with("archive: https://n.org/only (0002-coins.notes.html) has no archived copy"));
    std::fs::remove_file(dir.join("questions/0002-coins.notes.html")).unwrap();
    assert!(refusals(&dir, None).is_ok());
    put(&dir, "archive/e1/e1.json", "{}");
    put(&dir, "archive/e1/Z.json", "{}");
    put(&dir, "archive/zz/a.json", "{}");
    put(&dir, "archive/e1/.a.json", "{}");
    put(&dir, "archive/ab", "a file where a shard would be");
    let ids: Vec<String> = load(&dir).unwrap().keys().cloned().collect();
    assert_eq!(
        ids,
        [uid.clone(), "a1b2c3d4e5f6".to_owned(), "e1".to_owned()]
    );
    put(&dir, "archive/e1/e2.json", "nope");
    assert_eq!(load(&dir).unwrap_err().kind, "JSONDecodeError");
    assert_eq!(refusals(&dir, None).unwrap_err().kind, "JSONDecodeError");
    std::fs::remove_dir_all(dir.join("archive")).unwrap();
    assert!(refusals(&dir, None).unwrap().is_empty());
    std::fs::remove_dir_all(dir.join("sources")).unwrap();
    assert_eq!(cited(&dir).unwrap_err().kind, "RecordError");
}

#[test]
fn a_row_covers_its_url_and_names_its_copy() {
    let pending = json!({"outcome": "pending-upload", "captured": "2026-11-01T00:00"});
    assert!(covered(&pending, "2026-11-08").unwrap());
    assert!(!covered(&pending, "2026-11-09").unwrap());
    assert!(!covered(&json!({"outcome": "weird"}), "2026-01-01").unwrap());
    assert!(covered(&json!({"outcome": "partial"}), "2026-01-01").unwrap());
    assert_eq!(
        covered(&json!({"outcome": "pending-upload"}), "2026-01-01")
            .unwrap_err()
            .message,
        "'captured'"
    );
    for (day, message) in [
        ("2026-13-01", "month must be in 1..12, not 13"),
        ("nope", "Invalid isoformat string: 'nope'"),
        (
            "2026-02-30",
            "day 30 must be in range 1..28 for month 2 in year 2026",
        ),
        ("0000-01-01", "year must be in 1..9999, not 0"),
    ] {
        assert_eq!(iso_day(day).unwrap_err().message, message);
    }
    assert_eq!(
        iso_day("2024-02-29").unwrap() + 1,
        iso_day("2024-03-01").unwrap()
    );
    assert_eq!(iso_day("1970-01-01").unwrap(), 0);
    assert_eq!(today_utc().len(), 10);
    assert!(iso_day(&today_utc()).is_ok());
    let rows: serde_json::Map<String, serde_json::Value> = [
        (url_id("https://x.org/a"), json!({"outcome": "unreachable", "captured": "2026-10-02", "gm_copies": ["g/1.pdf", "g/1.pdf"]})),
        (url_id("https://y.org/b"), json!({"outcome": "partial", "path": "p/q", "captured": "2026-10-03"})),
        (url_id("https://z.org/c"), json!({"outcome": "archived", "path": "a&b", "captured": "2026-10-04", "reason": "x"})),
    ]
    .into_iter()
    .collect();
    assert_eq!(
        entry_line("<a href=\"https://x.org/a\">x</a> https://y.org/b <!-- https://z.org/c --> https://w.org/none", &rows),
        "<p class=\"archived\"><em>Archived:</em> no copy could be archived (unreachable, 2026-10-02); <a href=\"https://github.com/EliAndrewC/diagram-research/blob/main/g/1.pdf\" target=\"_blank\" rel=\"noopener\">the GM's downloaded copy</a>; <a href=\"https://github.com/EliAndrewC/diagram-research/tree/main/p/q\" target=\"_blank\" rel=\"noopener\">archived partial copy, 2026-10-03</a>; <a href=\"https://github.com/EliAndrewC/diagram-research/tree/main/a&amp;b\" target=\"_blank\" rel=\"noopener\">archived copy, 2026-10-04</a> (private)</p>\n"
    );
    assert_eq!(entry_line("no urls", &rows), "");
    assert_eq!(
        copy_link(&json!({"path": "p"})),
        "https://github.com/EliAndrewC/diagram-research/tree/main/p"
    );
    // the registry's reader takes no entry that nothing follows; the archive's census runs it to the end
    assert!(entry_bodies("<h3 id=\"a\">x</h3> body", false).is_empty());
    assert_eq!(
        entry_bodies("<h3 id=\"a\">x</h3> body", true),
        [("a".to_owned(), "body")]
    );
}
