//! One capture in the order of plan D2 (feature 449 T146): each branch's outcome, files and record as `archive.py` made them.

use serde_json::json;

use super::{capture, files_of, from_snapshot, merged, record_of, split_large, with};
use crate::fetch::Fetched;
use crate::testkit::{Fake, World};

const WAY: &str = "https://archive.org/wayback/available?url=";

fn snapshot(fake: &mut Fake, url: &str, raw_status: i64) {
    let ask = format!(
        "{WAY}{}",
        l7r_gate_research::verbatim::fetch::quote(url, "")
    );
    let body = json!({"archived_snapshots": {"closest": {"available": true, "url": "http://web.archive.org/web/20200101000000/x", "timestamp": "20200101000000"}}});
    fake.serve(&ask, 200, "application/json", body.to_string().as_bytes());
    fake.serve(
        "https://web.archive.org/web/20200101000000id_/x",
        raw_status,
        "text/html",
        b"<p>old</p>",
    );
}

fn names(files: &[(String, Vec<u8>)]) -> Vec<&str> {
    files.iter().map(|(n, _)| n.as_str()).collect()
}

#[test]
fn a_live_page_is_archived_whole_or_partial() {
    let w = World::new("capture-live");
    let r = w.research();
    let mut fake = Fake::default();
    fake.serve(
        "http://h/p",
        200,
        "text/html",
        b"<html><script>{\"wgRevisionId\":7}</script></html>",
    );
    fake.renders
        .insert("http://h/p".into(), ("M".into(), "text".into()));
    let got = capture(&mut fake, "http://h/p", false, "", &r).unwrap();
    assert_eq!(got.outcome, "archived");
    assert_eq!(names(&got.files), ["served.html", "page.mhtml", "text.txt"]);
    assert_eq!(got.record["revision"], "7");
    assert_eq!(got.record["whole_page"], true);
    fake.serve("http://h/q", 200, "text/html", b"<p>shown</p>");
    let partial = capture(&mut fake, "http://h/q", false, "", &r).unwrap();
    assert_eq!(partial.outcome, "partial");
    assert_eq!(
        partial.reason,
        "the page would not render whole: its served HTML and text are kept"
    );
    assert_eq!(names(&partial.files), ["served.html", "text.txt"]);
}

#[test]
fn a_dead_page_takes_a_snapshot_then_the_gms_copy_else_is_unreachable() {
    let w = World::new("capture-dead");
    let r = w.research();
    let mut fake = Fake::default();
    snapshot(&mut fake, "http://h/snap", 200);
    // the snapshot rendered whole, its text the served one where the render shows none
    fake.renders.insert(
        "https://web.archive.org/web/20200101000000/x".into(),
        ("M".into(), String::new()),
    );
    let snap = capture(&mut fake, "http://h/snap", true, "cached", &r).unwrap();
    assert_eq!(snap.outcome, "archived-earlier-snapshot");
    assert_eq!(snap.record["origin"], "wayback 20200101000000");
    assert_eq!(
        snap.record["live_failure"],
        "APIRequestContext.get: connect ECONNREFUSED"
    );
    assert_eq!(
        names(&snap.files),
        ["served.html", "page.mhtml", "text.txt"]
    );
    assert_eq!(snap.files[2].1, b"old");
    let gm = capture(&mut fake, "http://h/nosnap", true, "cached", &r).unwrap();
    assert_eq!(gm.outcome, "archived-gm-copy");
    assert!(gm.files.is_empty());
    assert_eq!(gm.record, json!({"url": "http://h/nosnap", "live_failure": "APIRequestContext.get: connect ECONNREFUSED", "origin": "the GM's downloaded copy"}).as_object().unwrap().clone());
    let none = capture(&mut fake, "http://h/nosnap", false, "cached", &r).unwrap();
    assert_eq!(
        (none.outcome.as_str(), names(&none.files)),
        ("unreachable", vec!["page-cache-text.txt"])
    );
    assert!(capture(&mut fake, "http://h/nosnap", false, "", &r)
        .unwrap()
        .files
        .is_empty());
    // a snapshot that will not fetch is none
    snapshot(&mut fake, "http://h/snapdown", 404);
    assert_eq!(
        capture(&mut fake, "http://h/snapdown", false, "", &r)
            .unwrap()
            .outcome,
        "unreachable"
    );
    assert!(from_snapshot(&mut fake, "http://h/unasked", "why", &r)
        .unwrap()
        .is_none());
    // a snapshot whose render shows text: that text kept, not the served page's
    snapshot(&mut fake, "http://h/snap", 200);
    fake.renders.insert(
        "https://web.archive.org/web/20200101000000/x".into(),
        ("M".into(), "rendered old".into()),
    );
    let shown = from_snapshot(&mut fake, "http://h/snap", "why", &r)
        .unwrap()
        .unwrap();
    assert_eq!(shown.files[2].1, b"rendered old");
    // a snapshot that is no web page is not rendered
    fake.serve(
        "https://web.archive.org/web/20200101000000id_/x",
        200,
        "application/pdf",
        crate::testkit::PDF,
    );
    let pdf = from_snapshot(&mut fake, "http://h/snap", "why", &r)
        .unwrap()
        .unwrap();
    assert_eq!(names(&pdf.files), ["served.pdf", "text.txt"]);
}

#[test]
fn a_refused_page_takes_the_gms_copy_then_a_snapshot_else_is_partial() {
    let w = World::new("capture-refused");
    let r = w.research();
    let mut fake = Fake::default();
    fake.serve("http://h/wall", 403, "text/html", b"<p>no bots</p>");
    let gm = capture(&mut fake, "http://h/wall", true, "", &r).unwrap();
    assert_eq!(gm.outcome, "archived-gm-copy");
    assert_eq!(gm.record["origin"], "the GM's downloaded copy");
    assert_eq!(gm.record["status"], 403);
    assert_eq!(names(&gm.files), ["served.html"]);
    snapshot(&mut fake, "http://h/wall", 200);
    assert_eq!(
        capture(&mut fake, "http://h/wall", false, "", &r)
            .unwrap()
            .outcome,
        "archived-earlier-snapshot"
    );
    fake.serve("http://h/wall2", 403, "text/html", b"<p>no bots</p>");
    let partial = capture(&mut fake, "http://h/wall2", false, "cached", &r).unwrap();
    assert_eq!(
        (partial.outcome.as_str(), names(&partial.files)),
        ("partial", vec!["served.html", "page-cache-text.txt"])
    );
    assert_eq!(partial.reason, "HTTP 403");
    assert_eq!(
        capture(&mut fake, "https://grokipedia.com/x", false, "", &r)
            .unwrap_err()
            .kind,
        "Blocked"
    );
}

#[test]
fn the_files_and_the_record_in_the_pythons_order_and_parts_past_the_limit() {
    let got = Fetched {
        url: "u".into(),
        status: None,
        content_type: "application/pdf".into(),
        body: b"%PDF".to_vec(),
        text: "t".into(),
        ..Fetched::default()
    };
    assert_eq!(names(&files_of(&got)), ["served.pdf", "text.txt"]);
    let rec = record_of("c", &got, "live");
    assert_eq!(
        rec.keys().collect::<Vec<_>>(),
        [
            "url",
            "fetched_url",
            "final_url",
            "status",
            "content_type",
            "sha256",
            "bytes",
            "revision",
            "origin",
            "whole_page"
        ]
    );
    assert_eq!(
        (
            rec["final_url"].clone(),
            rec["status"].clone(),
            rec["revision"].clone()
        ),
        (json!("u"), json!(null), json!(""))
    );
    let moved = with(rec, "url", json!("again"));
    assert_eq!(moved.keys().next().unwrap(), "url");
    let (out, parts) = split_large(vec![("a".into(), vec![1; 5]), ("b".into(), vec![2; 2])], 2);
    assert_eq!(names(&out), ["a.part1", "a.part2", "a.part3", "b"]);
    assert_eq!(parts["a"]["parts"], 3);
    assert_eq!(parts["a"]["bytes"], 5);
    assert_eq!(
        names(&merged(
            vec![("x".into(), vec![1])],
            vec![("x".into(), vec![2]), ("y".into(), vec![])]
        )),
        ["x", "y"]
    );
}
