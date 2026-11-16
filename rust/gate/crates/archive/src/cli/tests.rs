//! `l7r-gate record archive ...` (feature 449 T146), through [`cli_with`] on the tests' world.

use std::path::Path;
use std::sync::Mutex;

use serde_json::Value;

use super::{archive_one, cli_with, print_now, Reach};
use crate::fetch::Client;
use crate::store::Archive;
use crate::testkit::{Fake, World};
use crate::{Error, Reply};

#[expect(
    clippy::unnecessary_wraps,
    reason = "a browser's start, as the commands take it: this one always starts"
)]
fn browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    let mut fake = Fake::default();
    fake.serve("https://e.org/a", 200, "text/html", b"<p>a</p>");
    fake.renders
        .insert("https://e.org/a".into(), ("M".into(), "shown".into()));
    Ok(Box::new(fake))
}

fn no_browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    Err(Error::new("Error", "BrowserType.launch: none"))
}

type Start = dyn Fn(&Path) -> crate::Result<Box<dyn Client>> + Sync;

fn run(w: &World, args: &[&str], start: &Start, _input: &str) -> (Reply, Vec<String>, String) {
    let said = Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = |_: &Path| w.store();
    let reach = Reach {
        store: &store,
        start,
        say: &say,
    };
    let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    let reply = cli_with(&args, &w.root.join("research"), &reach);
    let lines = said.into_inner().unwrap();
    (reply, lines, String::new())
}

#[test]
fn url_archives_one_url_and_logs_the_attempt() {
    let w = World::new("cli-url");
    let (r, _, _) = run(
        &w,
        &["url", "https://e.org/a", "--key", "fresh-key"],
        &browser,
        "",
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(
        r.stdout.starts_with("archive: archived - https://e.org/a\n  https://github.com/EliAndrewC/diagram-research/tree/main/"),
        "{}",
        r.stdout
    );
    let row: Value = serde_json::from_str(
        &std::fs::read_to_string(crate::manifest::row_path(&w.root, "https://e.org/a")).unwrap(),
    )
    .unwrap();
    assert_eq!(row["keys"], serde_json::json!(["fresh-key", "work-src-a"]));
    let attempts = std::fs::read_to_string(w.research().join("source-attempts.jsonl")).unwrap();
    assert!(attempts.contains("\"sought\": \"archived for fresh-key (make archive)\""));
    assert!(attempts.contains("\"route\": \"archive\""));
    let (r, _, _) = run(
        &w,
        &["url", "https://e.org/a", "--key", "work-src-a"],
        &browser,
        "",
    );
    assert_eq!(r.code, 0);
    let (r, _, _) = run(&w, &["url", "https://e.org/dead"], &browser, "");
    assert_eq!(
        r.stdout,
        "archive: unreachable - https://e.org/dead (APIRequestContext.get: connect ECONNREFUSED)\n"
    );
    let attempts = std::fs::read_to_string(w.research().join("source-attempts.jsonl")).unwrap();
    assert!(attempts.contains("\"sought\": \"archived (make archive)\""));
    let (r, _, _) = run(&w, &["url", "https://e.org/a"], &no_browser, "");
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (1, "Error: BrowserType.launch: none\n")
    );
    for bad in [&["url"][..], &["url", "a", "b"], &["url", "a", "--nope"]] {
        let (r, _, _) = run(&w, bad, &browser, "");
        assert_eq!((r.code, r.stdout.as_str()), (2, ""));
        assert!(
            r.stderr.starts_with("l7r-gate record archive: error: "),
            "{}",
            r.stderr
        );
    }
    std::fs::write(w.research().join("blocked-domains.json"), "{").unwrap();
    let (r, _, _) = run(&w, &["url", "https://e.org/b"], &browser, "");
    assert_eq!(r.code, 1);
    let mut out = String::new();
    let store = |_: &Path| -> Archive { w.store() };
    std::fs::remove_dir_all(w.research().join("sources")).unwrap();
    assert!(archive_one(&w.root, "https://e.org/a", "", &browser, &store, &mut out).is_err());
    assert_eq!(store(&w.root).home, w.home);
}

#[test]
fn backfill_report_and_the_gms_copies_and_each_refusal() {
    let w = World::new("cli-more");
    std::fs::remove_file(w.research().join("sources/010-works-cited/0030-grok.html")).unwrap();
    let (r, _, _) = run(&w, &["report"], &browser, "");
    assert_eq!(r.code, 1);
    assert!(r.stdout.starts_with("archive coverage: "));
    let (r, lines, _) = run(&w, &["backfill", "--workers", " 2 "], &browser, "");
    assert_eq!((r.code, r.stderr.as_str()), (0, ""));
    assert!(lines[0].ends_with("in up to 2 lane(s)"));
    let (r, _, _) = run(&w, &["backfill", "--workers", "-3"], &browser, "");
    assert_eq!(r.code, 0);
    let (r, _, _) = run(&w, &["backfill", "--workers", "x"], &browser, "");
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            2,
            "l7r-gate record archive: error: argument --workers: invalid int value: 'x'\n"
        )
    );
    let (r, _, _) = run(&w, &["backfill", "--nope"], &browser, "");
    assert_eq!(r.code, 2);
    let (r, _, _) = run(&w, &["gm-copies"], &browser, "");
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (0, "archive: 0 row(s) given the GM's copies\n")
    );
    for extra in [&["report", "x"][..], &["gm-copies", "x"], &[], &["nope"]] {
        assert_eq!(run(&w, extra, &browser, "").0.code, 2);
    }
    std::fs::write(w.research().join("archive/gm-copies.json"), "{").unwrap();
    assert_eq!(run(&w, &["gm-copies"], &browser, "").0.code, 1);
    std::fs::remove_dir_all(w.research().join("sources")).unwrap();
    assert_eq!(run(&w, &["report"], &browser, "").0.code, 1);
    let (r, _, _) = run(&w, &["backfill"], &browser, "");
    assert_eq!(r.code, 1);
    print_now("print_now: a line printed at once");
}

#[test]
fn the_one_door_left_is_reached_through_the_command_line() {
    let w = World::new("cli-doors");
    let home = w.home.to_string_lossy().into_owned();
    let (r, _, _) = run(&w, &["push", "--home", &home], &browser, "");
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
    // the eight T147 retired are no command now
    for gone in [
        "serve",
        "settle",
        "ensure",
        "place-gm",
        "url-row",
        "lane",
        "sync-gm",
        "write-row",
    ] {
        assert_eq!(run(&w, &[gone], &browser, "").0.code, 2, "{gone}");
    }
}
