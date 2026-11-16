//! One fetch (feature 449 T146): each expected value `archive.py`'s on the same input (HEAD's Python, 2026-11-16).

use serde_json::json;

use super::{
    ext_of, failure, fetch, pdf_text, py_type, revision, served_text, snapshot_raw, suffix,
    url_path, wayback, Fetched,
};
use crate::testkit::{Fake, World, PDF};

#[test]
fn the_extension_comes_from_the_type_then_the_url() {
    assert_eq!(
        ext_of("text/html; charset=utf-8", "http://h/x.pdf"),
        ".html"
    );
    assert_eq!(ext_of("application/XHTML+xml", "http://h/"), ".html");
    assert_eq!(ext_of("application/pdf", "http://h/x"), ".pdf");
    assert_eq!(ext_of("image/jpeg", "http://h/x"), ".jpg");
    assert_eq!(ext_of("application/octet-stream", "http://h/x.pdf"), ".bin");
    assert_eq!(ext_of(" Text/Plain ; x", "http://h/x"), ".txt");
    assert_eq!(ext_of("", "http://h/a/b.TAR.Gz?q=1#f"), ".gz");
    assert_eq!(
        ext_of("application/x-l7r-unknown", "http://h/r.dat"),
        ".dat"
    );
    assert_eq!(
        ext_of("application/x-l7r-unknown", "http://h/r.toolong"),
        ".bin"
    );
    assert_eq!(ext_of("", "http://h/a.b;params"), ".b");
    assert_eq!(ext_of("", "http://h/a."), ".bin");
    assert_eq!(ext_of("", "http://h/.bashrc"), ".bin");
    assert_eq!(ext_of("", "http://h/x.d_t"), ".bin");
    assert_eq!(suffix("/a/..b.c/"), ".c");
    assert_eq!(suffix("/x/./"), "");
    assert_eq!(url_path("http://h/a;p/b;q?x"), "/a;p/b");
}

#[test]
fn a_pdfs_text_and_a_pages_served_text() {
    assert_eq!(pdf_text(PDF), "Hello PDF\n\u{c}");
    assert_eq!(pdf_text(b"%PDF-1.4 not really"), "");
    let page = b"<html><head><SCRIPT>var x = '<p>no</p>';</script><style>p{}</style></head><body><p>One &amp;   two</p>\n \n<NoScript>z</noscript><b>three</b>\t \n</body></html>";
    assert_eq!(served_text(page), "One & two\n three");
    assert_eq!(served_text(b"\xff<p>bad</p>"), "\u{fffd} bad");
    assert_eq!(revision(br#"{"wgRevisionId" :	 12345,"#), "12345");
    assert_eq!(revision(b"no wiki"), "");
    assert_eq!(
        snapshot_raw("https://web.archive.org/web/20200101000000/http://x/"),
        "https://web.archive.org/web/20200101000000id_/http://x/"
    );
    assert_eq!(
        snapshot_raw("https://other/web/20200101000000/x"),
        "https://other/web/20200101000000/x"
    );
}

fn got(status: Option<i64>, ct: &str, body: &[u8], final_url: &str) -> Fetched {
    Fetched {
        url: "http://h/deep/page".into(),
        status,
        final_url: final_url.into(),
        content_type: ct.into(),
        body: body.to_vec(),
        ..Fetched::default()
    }
}

#[test]
fn a_failure_is_dead_or_refused_as_plan_d10_reads_it() {
    let cited = "http://h/deep/page";
    assert_eq!(
        failure(cited, &Fetched::failed(cited, "boom")),
        ("dead", "boom".to_owned())
    );
    assert_eq!(
        failure(cited, &got(Some(403), "", b"x", "")),
        ("refused", "HTTP 403".to_owned())
    );
    assert_eq!(
        failure(cited, &got(None, "", b"x", "")),
        ("dead", "HTTP None".to_owned())
    );
    assert_eq!(
        failure(cited, &got(Some(500), "", b"x", "")),
        ("dead", "HTTP 500".to_owned())
    );
    assert_eq!(
        failure(cited, &got(Some(200), "", b"", "")),
        ("dead", "an empty response".to_owned())
    );
    assert_eq!(
        failure(cited, &got(Some(200), "text/plain", b"x", "http://h/")),
        (
            "dead",
            "redirected to the site's front page (http://h/)".to_owned()
        )
    );
    assert_eq!(
        failure(cited, &got(Some(200), "text/html", b"x", "")),
        ("refused", "the page showed no text".to_owned())
    );
    let mut shown = got(Some(200), "text/html", b"x", "");
    shown.text = " words ".into();
    assert_eq!(failure(cited, &shown), ("", String::new()));
    assert_eq!(
        failure(
            "http://h/",
            &got(Some(200), "text/plain", b"x", "http://h/")
        ),
        ("", String::new())
    );
}

#[test]
fn a_fetch_renders_a_page_reads_a_pdf_and_a_text_and_refuses_a_blocked_url() {
    let w = World::new("fetch");
    let mut fake = Fake::default();
    fake.serve("http://h/page", 200, "text/html", b"<p>served</p>");
    fake.renders
        .insert("http://h/page".into(), ("MHTML".into(), "rendered".into()));
    fake.serve("http://h/norender", 200, "text/html", b"<p>served only</p>");
    fake.serve("http://h/doc", 200, "application/octet-stream", PDF);
    fake.serve("http://h/typed.pdf", 200, "application/pdf", b"broken");
    fake.serve("http://h/t", 200, "text/plain", b"plain \xff");
    fake.serve("http://h/img", 200, "image/png", b"\x89PNG");
    fake.serve("http://h/gone", 404, "text/html", b"<p>gone</p>");
    let r = w.research();
    let page = fetch(&mut fake, "http://h/page", &r).unwrap();
    assert_eq!(
        (page.mhtml.as_str(), page.text.as_str()),
        ("MHTML", "rendered")
    );
    assert_eq!(
        fetch(&mut fake, "http://h/norender", &r).unwrap().text,
        "served only"
    );
    assert_eq!(
        fetch(&mut fake, "http://h/doc", &r).unwrap().text,
        "Hello PDF\n\u{c}"
    );
    assert_eq!(fetch(&mut fake, "http://h/typed.pdf", &r).unwrap().text, "");
    assert_eq!(
        fetch(&mut fake, "http://h/t", &r).unwrap().text,
        "plain \u{fffd}"
    );
    assert_eq!(fetch(&mut fake, "http://h/img", &r).unwrap().text, "");
    assert_eq!(fetch(&mut fake, "http://h/gone", &r).unwrap().text, "");
    assert!(fetch(&mut fake, "http://h/dead", &r)
        .unwrap()
        .error
        .contains("ECONNREFUSED"));
    let blocked = fetch(&mut fake, "https://grokipedia.com/page/X", &r).unwrap_err();
    assert_eq!(blocked.kind, "Blocked");
    assert!(!fake.asked.iter().any(|a| a.contains("grokipedia")));
}

#[test]
fn the_wayback_machine_names_its_newest_snapshot_or_none() {
    let mut fake = Fake::default();
    let ask = |u: &str| {
        format!(
            "https://archive.org/wayback/available?url={}",
            l7r_gate_research::verbatim::fetch::quote(u, "")
        )
    };
    let answer = |fake: &mut Fake, u: &str, body: serde_json::Value| {
        fake.serve(
            &ask(u),
            200,
            "application/json",
            body.to_string().as_bytes(),
        );
    };
    answer(
        &mut fake,
        "http://h/a",
        json!({"archived_snapshots": {"closest": {"available": true, "url": "http://web.archive.org/web/1/x", "timestamp": "20200101000000"}}}),
    );
    answer(
        &mut fake,
        "http://h/b",
        json!({"archived_snapshots": {"closest": {"available": true, "url": "http://web.archive.org/web/1/y"}}}),
    );
    answer(&mut fake, "http://h/c", json!({"archived_snapshots": {}}));
    answer(
        &mut fake,
        "http://h/d",
        json!({"archived_snapshots": {"closest": {"available": false, "url": "u"}}}),
    );
    answer(&mut fake, "http://h/e", json!({"archived_snapshots": []}));
    answer(&mut fake, "http://h/f", json!([1]));
    answer(
        &mut fake,
        "http://h/g",
        json!({"archived_snapshots": {"closest": "x"}}),
    );
    fake.serve(&ask("http://h/bad"), 200, "application/json", b"{not json");
    fake.serve(&ask("http://h/bytes"), 200, "application/json", b"\xff");
    fake.serve(&ask("http://h/busy"), 503, "text/html", b"busy");
    assert_eq!(
        wayback(&mut fake, "http://h/a").unwrap(),
        Some((
            "https://web.archive.org/web/1/x".into(),
            "20200101000000".into()
        ))
    );
    assert_eq!(
        wayback(&mut fake, "http://h/b").unwrap(),
        Some(("https://web.archive.org/web/1/y".into(), String::new()))
    );
    for none in [
        "http://h/c",
        "http://h/d",
        "http://h/bad",
        "http://h/bytes",
        "http://h/busy",
        "http://h/unasked",
    ] {
        assert_eq!(wayback(&mut fake, none).unwrap(), None, "{none}");
    }
    assert_eq!(
        wayback(&mut fake, "http://h/e").unwrap_err().message,
        "'list' object has no attribute 'get'"
    );
    assert_eq!(
        wayback(&mut fake, "http://h/f").unwrap_err().kind,
        "AttributeError"
    );
    assert_eq!(
        wayback(&mut fake, "http://h/g").unwrap_err().message,
        "'str' object has no attribute 'get'"
    );
    assert_eq!(
        [json!(null), json!(true), json!(1.5), json!(1), json!({})]
            .iter()
            .map(py_type)
            .collect::<Vec<_>>(),
        ["NoneType", "bool", "float", "int", "dict"]
    );
}
