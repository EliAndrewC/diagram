//! The fetch (feature 449 T147; the port's answers on hand-made input, read against the Python's code; the T147 differential (`make diff-run`) holds them to the Python on the real record), on a browser answering from
//! tables. The lane meeting a blocked page mid-way is the round arbiter's `ask:449-T146-browser` case, held here: the page refused before
//! any request, said as an error, the browser replaced, and the lane goes on.

use std::path::Path;

use l7r_gate_archive::testkit::Fake;
use serde_json::json;

use super::*;
use crate::testkit::{long, no_browser, quiet, starter, Said, W};

fn snapshot_ask(url: &str) -> String {
    format!(
        "https://archive.org/wayback/available?url={}",
        l7r_gate_research::verbatim::fetch::quote(url, "")
    )
}

fn fake() -> Fake {
    let mut f = Fake::default();
    f.serve(
        "https://a.org/live",
        200,
        "text/plain",
        long("a live page", 200).as_bytes(),
    );
    f.serve(
        "https://a.org/short",
        200,
        "text/plain",
        b"short text, under the empty bar",
    );
    f.serve("https://a.org/403", 403, "text/html", b"no");
    f.serve("https://a.org/401", 401, "text/html", b"no");
    f.serve("https://a.org/snap", 404, "text/html", b"gone");
    f.serve(&snapshot_ask("https://a.org/snap"), 200, "application/json",
            json!({"archived_snapshots": {"closest": {"available": true, "url": "http://web.archive.org/web/1/s", "timestamp": "1"}}}).to_string().as_bytes());
    f.serve(
        "https://web.archive.org/web/1/s",
        200,
        "text/plain",
        long("the snapshot", 30).as_bytes(),
    );
    f.serve(
        &snapshot_ask("https://a.org/odd"),
        200,
        "application/json",
        b"[]",
    );
    f.serve("https://a.org/odd", 500, "text/plain", b"");
    f
}

fn urls(list: &[&str]) -> Vec<String> {
    list.iter().map(|u| (*u).to_owned()).collect()
}

#[test]
fn a_lane_reads_rules_and_goes_on_past_a_failed_page() {
    let w = W::new("fetch-lane");
    w.page("https://a.org/shell", "a shell", "fetch");
    w.page("https://a.org/saved", &long("saved whole", 200), "fetch");
    let said = Said::default();
    let start = starter(fake);
    let got = lane(
        w.root(),
        &urls(&[
            "https://a.org/live",
            "https://a.org/search?q=x",
            "https://a.org/saved",
            "https://grokipedia.com/page/x",
            "https://a.org/403",
            "https://a.org/401",
            "https://a.org/snap",
            "https://a.org/short",
            "https://a.org/shell",
            "https://a.org/odd",
        ]),
        &start,
        &|l| said.say(l),
    )
    .unwrap();
    assert_eq!(
        got,
        Counts {
            read: 2,
            unreadable: 4,
            error: 2
        }
    );
    assert_eq!(said.all()[0], "read                   https://a.org/live");
    let lines = said.all();
    // the blocked page mid-lane (`ask:449-T146-browser`): its refusal's words, cut at 120 characters as the Python cut `str(err)`
    let refusal = l7r_gate_research::record::blocked::check(
        "https://grokipedia.com/page/x",
        "an archive fetch",
        &w.root().join("research"),
    )
    .unwrap_err()
    .message;
    assert!(
        refusal.starts_with(
            "an archive fetch refused: https://grokipedia.com/page/x is on the blocked list"
        ) && refusal.chars().count() > 120
    );
    assert_eq!(
        lines[1],
        format!(
            "error                  https://grokipedia.com/page/x - Blocked: {}",
            crate::first(&refusal, 120)
        )
    );
    assert_eq!(lines[2], "unreadable bot-refused https://a.org/403");
    assert_eq!(lines[3], "unreadable paywalled   https://a.org/401");
    assert_eq!(lines[4], "read                   https://a.org/snap");
    assert_eq!(lines[5], "unreadable down        https://a.org/short");
    assert_eq!(lines[6], "unreadable down        https://a.org/shell");
    assert_eq!(lines[7], "error                  https://a.org/odd - AttributeError: 'list' object has no attribute 'get'");
    let nk = w.read(crate::NOT_KEPT);
    assert!(nk.contains("\"note\": \"HTTP 403\", \"basis\": \"rule\""),);
    assert!(nk.contains("\"note\": \"an empty page\""), "{nk}");
    assert_eq!(
        text_of(w.home(), "https://a.org/snap").unwrap().unwrap(),
        crate::strip(&long("the snapshot", 30))
    );
    assert_eq!(
        l7r_gate_research::pages::cached(w.home(), "https://a.org/snap", 1.0, false)
            .unwrap()
            .unwrap()
            .meta["origin"],
        "wayback"
    );
    assert_eq!(
        text_of(w.home(), "https://a.org/short").unwrap().unwrap(),
        "short text, under the empty bar"
    );
    let log = std::fs::read_to_string(w.root().join("research/source-attempts.jsonl")).unwrap();
    assert_eq!(log.matches("\"route\": \"uncited-fetch\"").count(), 6);
}

#[test]
fn a_browser_that_will_not_start_is_each_pages_error_and_the_lanes_recycle() {
    static STARTS: std::sync::atomic::AtomicUsize = std::sync::atomic::AtomicUsize::new(0);
    let w = W::new("fetch-nobrowser");
    let said = Said::default();
    let got = lane(
        w.root(),
        &urls(&["https://a.org/x", "https://a.org/y"]),
        &no_browser,
        &|l| said.say(l),
    )
    .unwrap();
    assert_eq!(
        got,
        Counts {
            read: 0,
            unreadable: 0,
            error: 2
        }
    );
    assert_eq!(
        said.all()[0],
        "error                  https://a.org/x - Error: BrowserType.launch: none"
    );
    // twenty-six pages: a fresh browser at the twenty-fifth
    let counting = |_: &Path| {
        STARTS.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
        Ok(Box::new(fake()) as Box<dyn l7r_gate_archive::fetch::Client>)
    };
    let many: Vec<String> = (0..26).map(|i| format!("https://a.org/dead/{i}")).collect();
    let got = lane(w.root(), &many, &counting, &quiet).unwrap();
    assert_eq!(got.unreadable, 26);
    assert_eq!(STARTS.load(std::sync::atomic::Ordering::SeqCst), 2);
}

#[test]
fn the_lanes_sum_and_a_lanes_own_failure_is_the_runs() {
    let w = W::new("fetch-all");
    let start = starter(fake);
    let total = fetch_all(
        w.root(),
        &urls(&["https://a.org/live", "https://b.org/x", "https://a.org/403"]),
        0,
        &start,
        &quiet,
    )
    .unwrap();
    assert_eq!(total, json!({"read": 1, "unreadable": 2, "error": 0}));
    // the attempts log will not take the line: the lane stops, and so does the run
    std::fs::remove_file(w.root().join("research/source-attempts.jsonl")).ok();
    std::fs::create_dir_all(w.root().join("research/source-attempts.jsonl")).unwrap();
    assert!(fetch_all(w.root(), &urls(&["https://a.org/403"]), 2, &start, &quiet).is_err());
    let bad = l7r_gate_research::pages::entry_dir(w.home(), "https://a.org/live");
    std::fs::create_dir_all(&bad).unwrap();
    std::fs::write(bad.join("meta.json"), "{}").unwrap();
    std::fs::write(bad.join("text.txt"), "x").unwrap();
    assert_eq!(
        lane(w.root(), &urls(&["https://a.org/live"]), &start, &quiet)
            .unwrap_err()
            .kind,
        "KeyError"
    );
    let mut lazy = Lazy::new(&start, w.root());
    assert!(lazy.get().is_ok());
    lazy.recycle();
    assert!(lazy.get().is_ok());
    let got = l7r_gate_archive::fetch::Fetched {
        text: "t".into(),
        status: Some(0),
        ..Default::default()
    };
    assert_eq!(live_text(&got), "");
    // the not-kept list will not take an unreadable page's line: the lane stops
    let w = W::new("fetch-notkept");
    std::fs::create_dir_all(w.root().join(crate::NOT_KEPT)).unwrap();
    assert_eq!(
        lane(w.root(), &urls(&["https://a.org/403"]), &start, &quiet)
            .unwrap_err()
            .kind,
        "IsADirectoryError"
    );
}
