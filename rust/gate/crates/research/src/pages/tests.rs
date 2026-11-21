//! The page cache (feature 449 T145; the saved forms `sources.py`'s `wrapped` and `parts` on the same text, 2026-11-16).

use std::os::unix::fs::PermissionsExt as _;
use std::path::Path;

use l7r_shared::tempdir::TempDir;
use serde_json::json;

use super::{
    archived_text, cached, entry_dir, parts, put, refresh_wanted, wrapped, CachedPages, Inner,
    Stored,
};
use crate::verbatim::fetch::{Pages, Response, Transport};

const LIST: &str = r#"{"domains": [{"domain": "bad.example", "reason": "machine text", "approved": {"date": "2026-10-02", "words": "block it"}}]}"#;

fn record(d: &Path) -> std::path::PathBuf {
    let r = d.join("research");
    std::fs::create_dir_all(&r).unwrap();
    std::fs::write(r.join("blocked-domains.json"), LIST).unwrap();
    r
}

#[test]
fn a_page_is_saved_a_sentence_to_a_line_in_parts() {
    assert_eq!(
        wrapped("One. Two!  Three? 3.5 m\u{3002}\u{6b21}\u{306e}\u{6587}\u{3002} last"),
        "One.\nTwo!\nThree?\n3.5 m\u{3002}\n\u{6b21}\u{306e}\u{6587}\u{3002}\nlast\n"
    );
    assert_eq!(wrapped("  "), "\n");
    assert_eq!(
        parts("ab\ncdefgh\nij\r\nk\x1cl", 4),
        ["ab\n", "cdef", "gh\n", "ij\r\n", "k\x1cl"]
    );
    assert!(parts("", 4).is_empty());
    assert_eq!(parts("abc", 4), ["abc"]);
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "one page through the cache's whole life, stored, aged and read again"
)]
fn a_page_is_stored_and_read_back_while_it_is_young() {
    let d = TempDir::new("research-cache");
    let rec = record(&d);
    let home = d.join("home");
    let how = Stored {
        fetched: None,
        exact: true,
        origin: "fetch",
    };
    let long = "A sentence. ".repeat(4000);
    let got = put(&home, "https://www.a.org/p/", &long, &how, &rec).unwrap();
    assert_eq!(
        got.files,
        (1..=3)
            .map(|k| format!("page.p{k}.txt"))
            .collect::<Vec<_>>()
    );
    let short = put(&home, "https://a.org/p", "short", &how, &rec).unwrap();
    assert_eq!(short.files, ["page.txt"]);
    let hit = cached(&home, "http://a.org/p", 7.0, true).unwrap().unwrap();
    assert_eq!(
        (hit.text.as_str(), hit.files.clone()),
        ("short", vec!["page.txt".to_owned()])
    );
    assert!(hit.fetched().ends_with("+00:00"));
    assert_eq!(hit.meta["chars"], json!(5));
    assert!(cached(&home, "https://none.org", 7.0, false)
        .unwrap()
        .is_none());
    assert!(put(&home, "https://bad.example/x", "t", &how, &rec)
        .unwrap_err()
        .message
        .contains("the page cache refused"));
    let dir = entry_dir(&home, "https://a.org/p");
    let meta = |m: serde_json::Value| std::fs::write(dir.join("meta.json"), m.to_string()).unwrap();
    meta(json!({"fetched": "2020-01-01T00:00:00+00:00", "exact": true}));
    assert!(cached(&home, "https://a.org/p", 7.0, false)
        .unwrap()
        .is_none());
    meta(json!({"fetched": "2099-01-01T00:00:00+00:00", "exact": false}));
    assert!(cached(&home, "https://a.org/p", 7.0, true)
        .unwrap()
        .is_none());
    assert!(cached(&home, "https://a.org/p", 7.0, false)
        .unwrap()
        .is_some());
    std::fs::write(dir.join("page.p10.txt"), "x").unwrap();
    std::fs::write(dir.join("page.p2.txt"), "x").unwrap();
    assert_eq!(
        cached(&home, "https://a.org/p", 7.0, false)
            .unwrap()
            .unwrap()
            .files,
        ["page.txt", "page.p2.txt", "page.p10.txt"]
    );
    for (bad, kind) in [
        (json!([1]), "TypeError"),
        (json!({}), "KeyError"),
        (json!({"fetched": 5}), "TypeError"),
        (json!({"fetched": "nope"}), "ValueError"),
        (json!({"fetched": "2026-01-01T00:00:00"}), "TypeError"),
    ] {
        meta(bad);
        assert_eq!(
            cached(&home, "https://a.org/p", 7.0, false)
                .unwrap_err()
                .kind,
            kind
        );
    }
    std::fs::write(dir.join("meta.json"), "{").unwrap();
    assert!(cached(&home, "https://a.org/p", 7.0, false)
        .unwrap()
        .is_none());
    std::fs::write(dir.join("meta.json"), [0xff]).unwrap();
    assert_eq!(
        cached(&home, "https://a.org/p", 7.0, false)
            .unwrap_err()
            .kind,
        "UnicodeDecodeError"
    );
    meta(json!({"fetched": "2099-01-01T00:00:00+00:00"}));
    std::fs::remove_file(dir.join("text.txt")).unwrap();
    assert!(cached(&home, "https://a.org/p", 7.0, false)
        .unwrap()
        .is_none());
    std::fs::create_dir_all(dir.join("page.txt.d")).unwrap();
    std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o500)).unwrap();
    assert_eq!(
        put(&home, "https://a.org/p", "t", &how, &rec)
            .unwrap_err()
            .kind,
        "OSError"
    );
    std::fs::set_permissions(&dir, std::fs::Permissions::from_mode(0o755)).unwrap();
    std::fs::create_dir_all(dir.join("text.txt/inner")).unwrap();
    assert_eq!(
        put(&home, "https://a.org/p", "t", &how, &rec)
            .unwrap_err()
            .kind,
        "OSError"
    );
    std::fs::write(d.join("blocker"), "").unwrap();
    assert_eq!(
        put(&d.join("blocker"), "https://a.org/q", "t", &how, &rec)
            .unwrap_err()
            .kind,
        "OSError"
    );
}

#[test]
fn the_archive_behind_a_page() {
    let d = TempDir::new("research-archived");
    let uid = l7r_shared::cited_url::url_id("https://a.org/doc.pdf");
    let row = d.join("root/research/archive").join(&uid[..2]);
    std::fs::create_dir_all(&row).unwrap();
    std::fs::create_dir_all(d.join("store/cap")).unwrap();
    std::fs::write(d.join("store/cap/text.txt"), "the text\r\nof it").unwrap();
    std::fs::write(
        row.join(format!("{uid}.json")),
        json!({"path": "cap", "captured": "20261002T121317Z"}).to_string(),
    )
    .unwrap();
    let got = archived_text(
        "https://a.org/doc.pdf#p2",
        &d.join("root"),
        &d.join("store"),
    )
    .unwrap();
    assert_eq!(got, ("the text\nof it".to_owned(), "20261002T1".to_owned()));
    std::fs::write(d.join("store/cap/text.txt"), "  ").unwrap();
    assert!(archived_text("https://a.org/doc.pdf", &d.join("root"), &d.join("store")).is_none());
    std::fs::write(row.join(format!("{uid}.json")), "{\"path\": 5}").unwrap();
    assert!(archived_text("https://a.org/doc.pdf", &d.join("root"), &d.join("store")).is_none());
    assert!(archived_text("https://none.org", &d.join("root"), &d.join("store")).is_none());
}

/// One canned answer: the content type and body, or the failure.
type Answer = Result<(&'static str, &'static [u8]), &'static str>;

struct Answers(Vec<(&'static str, Answer)>);

impl Transport for Answers {
    fn open(&mut self, url: &str) -> Result<Response, String> {
        let (_, got) = self
            .0
            .iter()
            .find(|(u, _)| *u == url)
            .copied()
            .unwrap_or(("", Err("URLError: x")));
        got.map(|(t, b)| Response {
            content_type: t.into(),
            charset: String::new(),
            body: b.to_vec(),
        })
        .map_err(str::to_owned)
    }
}

#[test]
fn the_cache_before_the_network_and_the_archive_behind_it() {
    let d = TempDir::new("research-cached-pages");
    let rec = record(&d);
    let home = d.join("home");
    let net = Answers(vec![
        ("http://a.org/p", Ok(("text/html", b"<p>live</p>"))),
        ("http://a.org/d.pdf", Ok(("application/pdf", b""))),
    ]);
    let mut pages = CachedPages::new(
        Inner::Pages(Pages::new(None, Box::new(net))),
        &home,
        false,
        false,
        &d,
        &rec,
    );
    let blocked = pages.get("https://bad.example/x").unwrap();
    assert!(blocked.blocked && blocked.why.starts_with("a fetch refused"));
    assert_eq!(pages.get("http://a.org/p").unwrap().text, "live");
    assert!(pages.get("http://a.org/p").unwrap().cached.is_some());
    let uid = l7r_shared::cited_url::url_id("http://a.org/d.pdf");
    std::fs::create_dir_all(d.join("research/archive").join(&uid[..2])).unwrap();
    std::fs::write(
        d.join("research/archive")
            .join(&uid[..2])
            .join(format!("{uid}.json")),
        r#"{"path": "c", "captured": "2026-10-02"}"#,
    )
    .unwrap();
    std::fs::create_dir_all(home.join("source-archive/c")).unwrap();
    std::fs::write(home.join("source-archive/c/text.txt"), "kept text").unwrap();
    let kept = pages.get("http://a.org/d.pdf").unwrap();
    assert_eq!(
        (kept.text.as_str(), kept.archived.as_deref(), kept.live),
        ("kept text", Some("2026-10-02"), true)
    );
    assert_eq!(pages.get("http://z.org/").unwrap().state, "UNFETCHABLE");
    assert_eq!(
        pages.refused(),
        vec![("z.org".to_owned(), "URLError: x".to_owned())]
    );
    assert!(pages.get("research/x").unwrap().state == "OWN");
    assert!(pages.get("http://[bad/x").is_err());
    let mut none = CachedPages::new(Inner::NotCached, &home, true, false, &d, &rec);
    assert_eq!(none.get("http://a.org/p").unwrap().state, "NOT-CACHED");
    assert!(none.refused().is_empty());
    std::fs::write(rec.join("blocked-domains.json"), "{").unwrap();
    assert!(none.get("http://a.org/p").is_err());
    std::fs::write(rec.join("blocked-domains.json"), LIST).unwrap();
    std::fs::write(entry_dir(&home, "http://a.org/p").join("meta.json"), "[]").unwrap();
    assert!(
        CachedPages::new(Inner::NotCached, &home, false, false, &d, &rec)
            .get("http://a.org/p")
            .is_err()
    );
    let failing = Answers(vec![("http://w.org/p", Ok(("text/html", b"<p>w</p>")))]);
    let mut store_fails = CachedPages::new(
        Inner::Pages(Pages::new(None, Box::new(failing))),
        &d.join("blocked-home"),
        false,
        false,
        &d,
        &rec,
    );
    std::fs::write(d.join("blocked-home"), "a file").unwrap();
    assert!(store_fails.get("http://w.org/p").is_err());
    assert!(!refresh_wanted());
}
