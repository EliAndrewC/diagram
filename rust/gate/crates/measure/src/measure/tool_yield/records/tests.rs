//! The records' readers on scratch files.

use std::path::Path;

use super::super::tests::put;
use super::*;

#[test]
fn the_readers_take_what_the_python_took() {
    assert!(utc("nope").abs() < f64::EPSILON);
    assert!((utc("1970-01-01T00:00:10Z") - 10.0).abs() < f64::EPSILON);
    let r = crate::checks::scratch("ty-records");
    assert!(jsonl(&r.join("missing")).is_empty());
    put(&r, "a.jsonl", "{\"a\": 1}\n[2]\nnope\n");
    assert_eq!(jsonl(&r.join("a.jsonl")).len(), 1);
    assert_eq!(parent(Path::new("x")), Path::new("."));
    assert_eq!(parent(Path::new("/")), Path::new("/"));
    assert!(ledger_rows(&r).unwrap().is_empty());
    put(&r, "dev/review-ledger.md", "no table\n");
    assert!(ledger_rows(&r).unwrap().is_empty());
    assert!(guard_rows(&r.join("nowhere")).is_empty());
    std::fs::create_dir_all(r.join("logs/d.json")).unwrap();
    assert!(guard_rows(&r.join("logs")).is_empty());
}

#[test]
fn a_clone_reads_every_clone_beside_the_mirror() {
    let r = crate::checks::scratch("ty-dirs");
    for d in [".git", ".clones/a/.git", ".clones/.b/.git", ".clones/c"] {
        std::fs::create_dir_all(r.join(d)).unwrap();
    }
    put(&r, ".clones/f", "");
    let mut got = git_dirs(&r.join(".clones/a"));
    got.sort();
    assert_eq!(got, vec![r.join(".clones/a/.git"), r.join(".git")]);
    assert_eq!(git_dirs(&r), git_dirs(&r.join(".clones/c")));
}

#[test]
fn the_arbiter_counts_from_its_first_dispatch() {
    let mut t = Tools::new();
    let events = jsonl_of("{\"t\": \"2026-01-10T00:00:00Z\", \"ev\": \"SubagentStart\", \"agent\": \"round-arbiter\"}\n");
    tally_events(&mut t, &events, 0.0);
    let r = crate::checks::scratch("ty-arbiter");
    put(&r, "specs/1/arbiter.jsonl", "{\"ruling\": \"process-fault\", \"utc\": \"2026-01-01T00:00:00Z\"}\n{\"ruling\": \"process-fault\", \"utc\": \"2026-01-10T00:00:00Z\"}\n");
    assert!(tally_arbiter(&mut t, &r));
    assert_eq!(
        t[&("review".to_owned(), "round-arbiter".to_owned())].hits,
        1
    );
}

fn jsonl_of(text: &str) -> Vec<Row> {
    objects(text)
}
