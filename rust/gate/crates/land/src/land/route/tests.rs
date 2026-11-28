//! The one route (461 T29) on the landing's scratch clone: refused outside the lane's tree naming the route, the lane's own tree let
//! through unrecorded, the escape recorded with its reason and refused without one; and `main` refusing before the landing.

use std::path::{Path, PathBuf};

use l7r_shared::builder_pool::{write, Tree, LANE};
use l7r_shared::env::Rooted;

use super::super::tests::{fx, has, NOTE};
use super::{rule, Route, ESCAPE, GUARD};

/// The registry of `root`'s clone holding `tree` as the lane's.
pub(in super::super) fn adopt(root: &Path, tree: &Path) {
    let lane = Tree {
        tree: tree.to_path_buf(),
        feature: String::new(),
        tasks: vec![LANE.to_owned()],
        since: "2026-11-28T00:00:00Z".to_owned(),
    };
    write(&root.join(".git"), &[lane]).unwrap();
}

/// The route's guard-log entries in `logs` (one file each), in the order written, each `(event, rule, detail)`.
fn records(logs: &Path) -> Vec<(String, String, String)> {
    let mut files: Vec<PathBuf> = std::fs::read_dir(logs)
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    files.sort();
    files
        .iter()
        .filter_map(|p| {
            serde_json::from_str::<serde_json::Value>(
                &std::fs::read_to_string(p).unwrap_or_default(),
            )
            .ok()
        })
        .filter(|v| v["guard"] == GUARD)
        .map(|v| {
            let s = |k: &str| v[k].as_str().unwrap_or_default().to_owned();
            (s("event"), s("rule"), s("detail"))
        })
        .collect()
}

/// The root with its own guard log and `vars`.
fn rooted(root: &Path, logs: &Path, vars: &[(&str, &str)]) -> Rooted {
    let mut all = vec![("GUARD_LOG_DIR", logs.to_str().unwrap())];
    all.extend_from_slice(vars);
    Rooted::with(root.to_path_buf(), &all)
}

/// A refusal's text, "" where the route was not refused.
fn refusal(r: Route) -> String {
    if let Route::Refused(s) = r {
        s
    } else {
        String::new()
    }
}

fn tasks() -> Vec<String> {
    vec!["T1".to_owned(), "T2".to_owned()]
}

#[test]
fn a_landing_outside_the_lane_s_tree_is_refused_naming_the_route() {
    let fx = fx("route-outside");
    let logs = fx.dir.join("logs");
    // no lane adopted: the adoption named
    let none = refusal(rule(&rooted(&fx.root, &logs, &[]), "461", &tasks()));
    has(&none, "a landing runs only in the landing lane's tree");
    has(&none, "make builder-tree-adopt TREE=<clone>-land");
    has(&none, "make lane-start");
    has(&none, "make builder-done T=<task> F=461");
    has(
        &none,
        "LAND_HERE_OK=\"<why the lane cannot>\" make land F=461 T=\"T1 T2\"",
    );
    // a lane adopted elsewhere: its tree named
    let lane: PathBuf = fx.dir.join("lane");
    std::fs::create_dir_all(&lane).unwrap();
    adopt(&fx.root, &lane);
    let other = refusal(rule(&rooted(&fx.root, &logs, &[]), "461", &tasks()));
    has(&other, &format!("its tree is {}", lane.display()));
    let rows = records(&logs);
    assert_eq!(rows.len(), 2);
    assert!(rows.iter().all(|(e, r, d)| e == "blocked"
        && r == "outside-the-lane"
        && d.starts_with("461 T1 T2 in ")));
}

#[test]
fn the_lane_s_own_tree_passes_unrecorded() {
    let here = fx("route-lane");
    let logs = here.dir.join("logs");
    adopt(&here.root, &here.root);
    assert_eq!(
        rule(&rooted(&here.root, &logs, &[]), "461", &tasks()),
        Route::Lane
    );
    assert_eq!(
        refusal(rule(&rooted(&here.root, &logs, &[]), "461", &tasks())),
        ""
    );
    // the lane's variables are no escape: the tree decides
    let elsewhere = fx("route-lane-vars");
    let vars = [
        ("L7R_LANE_BATCH", "461-1"),
        (super::super::alone::INNER, "1"),
    ];
    assert!(matches!(
        rule(&rooted(&elsewhere.root, &logs, &vars), "461", &tasks()),
        Route::Refused(_)
    ));
    assert_eq!(records(&logs).len(), 1);
}

#[test]
fn the_escape_is_recorded_with_its_reason_and_refused_without_one() {
    let fx = fx("route-escape");
    let logs = fx.dir.join("logs");
    let why = "the lane cannot carry its own fix";
    let said = rule(&rooted(&fx.root, &logs, &[(ESCAPE, why)]), "461", &tasks());
    assert_eq!(
        said,
        Route::Escaped(format!(
            "land: LAND_HERE_OK - landing outside the lane's tree, recorded: {why}"
        ))
    );
    let thin = refusal(rule(
        &rooted(&fx.root, &logs, &[(ESCAPE, "x")]),
        "461",
        &tasks(),
    ));
    has(&thin, "LAND_HERE_OK needs a REASON, not just a value");
    let rows = records(&logs);
    assert_eq!(rows[0].0, "escaped");
    assert_eq!(rows[0].1, "land-here-ok");
    let detail = &rows[0].2;
    assert!(detail.starts_with("461 T1 T2 in "));
    assert!(detail.ends_with(why));
    assert_eq!(
        (rows[1].0.as_str(), rows[1].1.as_str(), rows[1].2.as_str()),
        ("blocked", "LAND_HERE_OK-no-reason", "x")
    );
}

#[test]
fn main_refuses_outside_the_lane_before_the_landing_and_writes_its_end() {
    let fx = fx("route-main");
    let logs = fx.dir.join("logs");
    let scripts = |_: &Path| fx.dir.join("tree/scripts");
    let args = vec!["449".to_owned(), "T1".to_owned()];
    let nothing = || {};
    let code = super::super::main(
        &args,
        &fx.root,
        NOTE,
        &scripts,
        &nothing,
        &rooted(Path::new("."), &logs, &[]),
    );
    assert_eq!(code, Ok(2));
    // nothing of the landing ran: no stub was called
    assert_eq!(fx.log(), "");
    let log = std::fs::read_to_string(fx.root.join(".git/l7r-events/449-x.jsonl")).unwrap();
    assert!(log.contains("\"step\":\"end\""), "{log}");
    // the escape lets it on to the landing, whose unreadable tasks.md then raises in the first pass
    std::fs::write(fx.root.join("specs/449-x/tasks.md"), [0xff]).unwrap();
    let why = [
        (ESCAPE, "the lane is down for repair"),
        (super::super::alone::INNER, "1"),
    ];
    assert!(super::super::main(
        &args,
        &fx.root,
        NOTE,
        &scripts,
        &nothing,
        &rooted(Path::new("."), &logs, &why)
    )
    .is_err());
}
