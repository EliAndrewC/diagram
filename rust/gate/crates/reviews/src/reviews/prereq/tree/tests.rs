//! A review's gate is its snapshot's (451 T164), on scratch repositories: the verdict, the gate state, the content key and the check of
//! a unit the review tree snapshotted, judged on that snapshot whatever the clone holds.

use std::path::Path;

use serde_json::{json, Value};

use super::super::super::tests::{put, repo, sheet};
use super::super::{cli, Reply};
use super::*;

const UNIT: &str = "building-review--c";

fn run_in(root: &Path, a: &[&str]) -> Reply {
    let mut all: Vec<String> = a.iter().map(|s| (*s).to_owned()).collect();
    all.extend(["--clone".to_owned(), root.to_string_lossy().into_owned()]);
    cli(&all)
}

/// The review tree's snapshot of `UNIT` at commit `c1`, key `K1`, its copy whole.
fn snapped(root: &Path) {
    let dir = format!(".git/review-snapshot/{UNIT}");
    put(
        root,
        &format!("{dir}/tree.json"),
        &json!({"commit": "c1", "key": "K1", "tree": "/r", "on": "c"}).to_string(),
    );
    for ext in [".svg", ".png", ".html"] {
        put(root, &format!("{dir}/clone/c{ext}"), "<svg/>");
    }
}

fn gate_rec(root: &Path, rec: &Value) {
    put(root, ".git/review-trees/c1.json", &rec.to_string());
}

fn state(root: &Path) -> String {
    run_in(root, &["gate-state", "--unit", UNIT]).stdout
}

/// RED FIRST (451 T164): the clone's stamp red (another builder's edit), the snapshot's gate green - the verdict was recorded
/// NOT-REVIEWABLE at the clone's last dispatch key; it is the review's verdict at the snapshot's key now.
#[test]
fn a_verdict_is_judged_by_its_snapshots_gate_not_the_clones() {
    let r = repo("tree-verdict");
    sheet(&r, "pool", "c", &["gate"]);
    put(
        &r,
        ".git/pairing-state.json",
        r#"{"review_dispatch_key": "CLONE"}"#,
    );
    snapped(&r);
    gate_rec(&r, &json!({"state": "green", "key": "K1"}));
    // no .git/green: the clone's own stamp reads red
    assert_eq!(run_in(&r, &["gate-state"]).stdout, "red\n");
    assert_eq!(state(&r), "green\n");
    let said = run_in(&r, &["verdict", "--unit", UNIT, "--verdict", "PASS"]);
    assert_eq!(
        said.stdout,
        format!("recorded PASS for {UNIT} (engine key K1, gate green)\n")
    );
    let rec: Value = serde_json::from_str(
        &std::fs::read_to_string(r.join(format!(".git/review-verdicts/{UNIT}.json"))).unwrap(),
    )
    .unwrap();
    // its content key is the snapshot's copy, not the clone's sheet, which a builder may have moved since
    let copy = r.join(format!(".git/review-snapshot/{UNIT}/clone"));
    let want = json!(super::super::folder_key(&copy, "c"));
    assert_eq!(rec["content_key"], want);
    assert_ne!(
        rec["content_key"],
        json!(super::super::content_key(&r, "c"))
    );
    let got = run_in(&r, &["content-key", "--unit", UNIT]).stdout;
    let want = format!("{}\n", rec["content_key"].as_str().unwrap());
    assert_eq!(got, want);
}

/// The snapshot's gate: green only on its own key, running while its runner lives, else red.
#[test]
fn the_snapshots_gate_is_green_on_its_key_running_while_alive_else_red() {
    let r = repo("tree-gate");
    snapped(&r);
    assert_eq!(state(&r), "red\n", "no record");
    gate_rec(&r, &json!({"state": "green", "key": "OTHER"}));
    assert_eq!(state(&r), "red\n", "another key");
    gate_rec(&r, &json!({"state": "running", "pid": std::process::id()}));
    assert_eq!(state(&r), "running\n");
    gate_rec(&r, &json!({"state": "running", "pid": 0}));
    assert_eq!(state(&r), "red\n", "a runner gone");
    gate_rec(&r, &json!({"state": "red", "key": "K1"}));
    let said = run_in(&r, &["verdict", "--unit", UNIT, "--verdict", "PASS"]);
    let want = format!("recorded NOT-REVIEWABLE for {UNIT} (engine key K1");
    assert!(said.stdout.starts_with(&want), "{}", said.stdout);
}

/// A record with no commit or key, or no unit asked, is no snapshot.
#[test]
fn a_partial_record_is_no_snapshot() {
    let r = repo("tree-partial");
    assert_eq!(of_unit(&r, ""), None);
    put(
        &r,
        &format!(".git/review-snapshot/{UNIT}/tree.json"),
        r#"{"commit": "c1"}"#,
    );
    assert_eq!(of_unit(&r, UNIT), None);
    assert_eq!(lacking(&r, UNIT), None);
}

/// A snapshotted unit's check asks nothing of the clone: not whether it is owed there, nor its currency - only that its copy is whole.
#[test]
fn a_snapshotted_unit_is_checked_on_its_snapshot_alone() {
    let r = repo("tree-check");
    snapped(&r);
    put(
        &r,
        ".git/p.md",
        &format!("UNIT: {UNIT}\nreview-snapshot/{UNIT}/clone\n"),
    );
    let p = r.join(".git/p.md").to_string_lossy().into_owned();
    // the clone holds no such map and owes no such unit: a clone-judged check would refuse both
    let said = run_in(&r, &["check", "--maps", UNIT, "--prompt-file", &p]);
    let got = (said.code, said.stdout.as_str());
    assert_eq!(got, (0, ""), "{}", said.stderr);
    std::fs::remove_file(r.join(format!(".git/review-snapshot/{UNIT}/clone/c.png"))).unwrap();
    let said = run_in(&r, &["check", "--maps", UNIT, "--prompt-file", &p]);
    assert_eq!(said.code, 1);
    let want = format!("FR-005 {UNIT}: its review snapshot lacks .png");
    assert!(said.stdout.contains(&want), "{}", said.stdout);
    // a map's snapshot owes its manifest too
    std::fs::remove_file(r.join(format!(".git/review-snapshot/{UNIT}/clone/c.svg"))).unwrap();
    assert!(lacking(&r, UNIT).unwrap().contains("lacks .json .svg .png"));
}
