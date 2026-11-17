//! `archive_ops.py`'s commands through `l7r-gate record archive` (feature 449 T147): flags, refusals and each command's lines.

use std::path::Path;
use std::sync::Mutex;

use serde_json::json;

use super::super::{cli_with, Reach};
use crate::fetch::Client;
use crate::testkit::{git, Fake, World, PDF};
use crate::{Error, Reply};

#[expect(
    clippy::unnecessary_wraps,
    reason = "a browser's start, as the commands take it: this one always starts"
)]
fn browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    let mut fake = Fake::default();
    fake.serve("https://k.org/1", 200, "text/plain", b"a kept page");
    Ok(Box::new(fake))
}

fn no_browser(_: &Path) -> crate::Result<Box<dyn Client>> {
    Err(Error::new("Error", "BrowserType.launch: none"))
}

type Start = dyn Fn(&Path) -> crate::Result<Box<dyn Client>> + Sync;

fn run(w: &World, args: &[&str], start: &Start) -> (Reply, Vec<String>) {
    let said = Mutex::new(Vec::new());
    let say = |l: &str| said.lock().unwrap().push(l.to_owned());
    let store = |_: &Path| w.store();
    let reach = Reach {
        store: &store,
        start,
        say: &say,
    };
    let args: Vec<String> = args.iter().map(|a| (*a).to_owned()).collect();
    let reply = cli_with(&args, &w.root, &reach);
    let lines = said.into_inner().unwrap();
    (reply, lines)
}

fn world(tag: &str) -> World {
    let w = World::new(tag);
    l7r_gate_research::fixture::put(
        &w.research(),
        "archive/a1/a1b2c3d4e5f6.json",
        r#"{"url": "https://e.org/a", "outcome": "archived", "keys": ["src-a"], "path": "a1/x"}"#,
    );
    w
}

/// The inbox's lines and refusals: what was one test of every command, split into one a command - each its own world, the five
/// commands' pushes together past FR-008's tenth of a second (feature 449 T167); the name kept on the first.
#[test]
fn each_command_and_its_refusals() {
    let w = world("cli-ops");
    // the inbox: a word with no `=` passed over, a NONE file archived, a list that will not load refused at an entry id
    std::fs::write(w.gm.join("a.pdf"), PDF).unwrap();
    let (r, _) = run(
        &w,
        &["inbox", "--match", "noequals", "--none", "a.pdf"],
        &browser,
    );
    assert_eq!(r.code, 0, "{}", r.stderr);
    assert!(r.stdout.contains("  a.pdf -> gm-copies/a.pdf\n"));
    let (r, _) = run(&w, &["inbox", "--match=x=#4"], &browser);
    assert_eq!((r.code, r.stdout.as_str()), (1, ""));
    assert!(r.stderr.starts_with("access-tags: REFUSED - ") && r.stderr.ends_with('\n'));
    std::fs::write(w.gm.join("b.txt"), "b").unwrap();
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", "/no/such.git"],
    );
    let (r, _) = run(&w, &["inbox", "--none", "b.txt"], &browser);
    assert_eq!(
        (r.code, r.stderr.split(':').next()),
        (1, Some("RuntimeError"))
    );
    git(
        &w.home.join("source-archive"),
        &["remote", "set-url", "origin", &w.remote.to_string_lossy()],
    );
    assert_eq!(run(&w, &["inbox", "extra"], &browser).0.code, 2);
}

#[test]
fn find_and_its_refusals() {
    let w = world("cli-ops-find");
    let (r, _) = run(&w, &["find", "--key", "src-a"], &browser);
    assert_eq!(r.code, 0);
    assert!(r
        .stdout
        .starts_with("archived                   https://e.org/a\n"));
    let (r, _) = run(&w, &["find", "--key", "none"], &browser);
    assert_eq!(
        (r.code, r.stdout.starts_with("archive: nothing held")),
        (1, true)
    );
    std::fs::write(w.research().join("blocked-domains.json"), "{").unwrap();
    assert_eq!(
        run(&w, &["find", "--url", "https://x.org"], &browser)
            .0
            .code,
        1
    );
}

/// consulted: the flags read as int, refused as argparse refused them
#[test]
fn consulted_and_its_refusals() {
    let w = world("cli-ops-consulted");
    let (r, lines) = run(
        &w,
        &["consulted", "--limit", "1", "--workers", "2"],
        &browser,
    );
    assert_eq!((r.code, r.stdout.as_str()), (0, ""));
    assert!(lines[0].starts_with("archive: 0 kept uncited URL(s)"));
    for bad in [
        &["consulted", "--limit", "x"][..],
        &["consulted", "--workers", "1.5"],
    ] {
        let (r, _) = run(&w, bad, &browser);
        assert_eq!(r.code, 2);
        assert!(r.stderr.contains("invalid int value"), "{}", r.stderr);
    }
    l7r_gate_research::fixture::put(
        &w.root,
        crate::ops::KEPT,
        &(json!({"url": "k.org/1", "raw": "https://k.org/1"}).to_string() + "\n"),
    );
    let (r, _) = run(&w, &["consulted"], &no_browser);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (1, "Error: BrowserType.launch: none\n")
    );
}

#[test]
fn urls_and_their_refusals() {
    let w = world("cli-ops-urls");
    let (r, _) = run(
        &w,
        &["urls", "https://k.org/1", "https://e.org/a"],
        &browser,
    );
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (0, "archive: archived - https://k.org/1\n")
    );
    let (r, _) = run(&w, &["urls", "https://k.org/9"], &no_browser);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (1, "Error: BrowserType.launch: none\n")
    );
    let (r, _) = run(&w, &["urls"], &browser);
    assert_eq!(
        (r.code, r.stderr.as_str()),
        (
            2,
            "l7r-gate record archive: error: the following arguments are required: urls\n"
        )
    );
}

#[test]
fn relayout_and_its_refusals() {
    let w = world("cli-ops-relayout");
    let (r, _) = run(&w, &["relayout"], &browser);
    assert_eq!(
        (r.code, r.stdout.as_str()),
        (0, "archive: 0 row(s) moved to the sharded layout\n")
    );
    l7r_gate_research::fixture::put(&w.research(), "archive/0e.json", "{}");
    assert_eq!(run(&w, &["relayout"], &browser).0.code, 1);
    assert_eq!(run(&w, &["relayout", "--x"], &browser).0.code, 2);
}
