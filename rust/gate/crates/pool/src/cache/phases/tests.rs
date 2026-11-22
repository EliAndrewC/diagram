//! `make map`'s Phase lines (feature 451 T153): a drawn map's steps cut at its artifacts' mtimes, a CACHED hit its own step, on the
//! cache's fixture pool with its stand-in engines.
//!
//! Research: the cache's tests - NONE: fixtures and assertions, deciding nothing about a map

use std::time::{Duration, SystemTime, UNIX_EPOCH};

use serde_json::Value;

use super::super::tests::fixture;
use super::drawn;

/// Every Phase line of the fixture's logs, `(step, name)`.
fn lines(root: &std::path::Path) -> Vec<(String, String, i64)> {
    let mut out = Vec::new();
    let dir = std::fs::read_dir(root.join(".git/l7r-events")).unwrap();
    for f in dir.flatten() {
        for l in std::fs::read_to_string(f.path()).unwrap().lines() {
            let v: Value = serde_json::from_str(l).unwrap();
            let src = v["src"].as_str().unwrap_or("");
            if v["ev"] == "Phase" && src == "map" {
                out.push((
                    v["step"].as_str().unwrap().to_owned(),
                    v["name"].as_str().unwrap().to_owned(),
                    v["code"].as_i64().unwrap(),
                ));
            }
        }
    }
    out
}

fn owned(rows: &[(&str, &str, i64)]) -> Vec<(String, String, i64)> {
    rows.iter()
        .map(|(a, b, c)| ((*a).to_owned(), (*b).to_owned(), *c))
        .collect()
}

#[test]
fn a_drawn_map_writes_its_steps_and_a_hit_its_cached_line() {
    let mut f = fixture("phases");
    f.verdicts(&["c", "h", "s"]);
    let first = lines(&f.root);
    let want = owned(&[
        ("generate", "pool/magistracies/c", 0),
        ("render", "pool/magistracies/c", 0),
        ("page", "pool/magistracies/c", 0),
        ("generate", "pool/hamlets/h", 0),
        ("render", "pool/magistracies/s", 0),
        ("page", "pool/magistracies/s", 0),
    ]);
    let mut sorted = first.clone();
    sorted.sort();
    let mut want_sorted = want;
    want_sorted.sort();
    assert_eq!(sorted, want_sorted);
    f.verdicts(&["c"]);
    let after = lines(&f.root);
    let last = after.last().cloned();
    let hit = ("cached".to_owned(), "pool/magistracies/c".to_owned(), 0);
    assert_eq!(last, Some(hit));
}

#[test]
fn the_steps_are_cut_at_each_artifact_and_the_last_runs_to_the_exit() {
    let f = fixture("phases-cut");
    let m = f.maps(&["c"]).remove(0);
    let staging = f.root.join("staging");
    std::fs::create_dir_all(&staging).unwrap();
    let at = |s: u64| UNIX_EPOCH + Duration::from_secs(s);
    for (name, t) in [
        ("c.svg", 12),
        ("c.png", 15),
        ("c.html", 16),
        ("c.compound.json", 11),
    ] {
        let file = std::fs::File::create(staging.join(name)).unwrap();
        file.set_modified(at(t)).unwrap();
    }
    let got = drawn(&m, &staging, (at(10), at(20)));
    let want = [
        ("generate", at(10), at(12)),
        ("render", at(12), at(15)),
        ("page", at(15), at(20)),
    ];
    assert_eq!(got, want);
    // a picture skipped: the page follows the sheet; an mtime outside the run is clamped into it
    std::fs::remove_file(staging.join("c.png")).unwrap();
    std::fs::File::options()
        .write(true)
        .open(staging.join("c.svg"))
        .unwrap()
        .set_modified(at(5))
        .unwrap();
    let skipped = drawn(&m, &staging, (at(10), at(20)));
    let want_skipped = [("generate", at(10), at(10)), ("page", at(10), at(20))];
    assert_eq!(skipped, want_skipped);
    // no staging folder: no step
    let none: Vec<(&str, SystemTime, SystemTime)> =
        drawn(&m, &f.root.join("gone"), (at(10), at(20)));
    assert!(none.is_empty());
}

/// A test's starting options file their lines by no environment at all.
#[test]
fn the_default_options_read_no_environment() {
    let env = super::super::Options::default().env;
    assert_eq!(env("L7R_EVENTS_DIR"), None);
}
