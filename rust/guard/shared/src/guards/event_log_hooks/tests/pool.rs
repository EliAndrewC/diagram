//! Feature 451 T332, T344: a tool's line written from a builder-pool tree names the task the pool says holds the tree. WHY: on
//! 2026-11-26 all 179 `Phase` lines of T315's check runs in `diagram-backlog-t269` carried T285 - the tree's last `make task-start`,
//! five handouts old - and `make task-time` booked five tasks' build and test seconds to one (T344's line; method: the 451 log's
//! `Phase` lines of that tree counted by their task field, against `builder-pool.log`).

use serde_json::{json, Map, Value};

use super::super::append_row_in;
use super::{last_line, none, Builders};
use crate::builder_pool::{self, Tree};

fn phase() -> Map<String, Value> {
    let mut row = Map::new();
    row.insert("ev".into(), json!("Phase"));
    row.insert("step".into(), json!("build"));
    row
}

impl Builders {
    /// The pool's registry naming this tree held by `tasks` of `feature` since `since`.
    fn held(&self, feature: &str, tasks: &[&str], since: &str) {
        let tree = Tree {
            tree: self.d.to_path_buf(),
            feature: feature.to_owned(),
            tasks: tasks.iter().map(|t| (*t).to_owned()).collect(),
            since: since.to_owned(),
        };
        builder_pool::write(&self.d.join(".git"), &[tree]).unwrap();
    }

    /// The task a `Phase` line written in the tree now carries.
    fn phase_task(&self) -> Value {
        let log = append_row_in(&self.d, None, phase(), "T", &none).unwrap();
        last_line(&log)["task"].clone()
    }

    fn started_at(&self, feature: &str, task: &str, utc: &str) {
        let path = self.d.join(".git/task-starts.jsonl");
        let mut text = std::fs::read_to_string(&path).unwrap();
        text.push_str(&json!({"feature": feature, "task": task, "utc": utc}).to_string());
        text.push('\n');
        std::fs::write(path, text).unwrap();
    }
}

/// The tree's last start is 449-b's T236 (2026-11-20T08:00:01Z), which no handout moves: each handout's lines carry that
/// handout's first task, the second handout's the second task.
#[test]
fn a_second_handouts_phase_line_carries_the_second_task() {
    let b = Builders::new("pool-second-handout");
    assert_eq!(b.phase_task(), json!("T236"));
    b.held("449", &["T300"], "2026-11-21T00:00:00Z");
    assert_eq!(b.phase_task(), json!("T300"));
    b.held("449", &["T315", "T316"], "2026-11-22T00:00:00Z");
    assert_eq!(b.phase_task(), json!("T315"));
    // the registry's feature as a directory name reads the same
    b.held("449-b", &["T317"], "2026-11-22T01:00:00Z");
    assert_eq!(b.phase_task(), json!("T317"));
}

/// What the pool does not answer stays the start log's: a free tree, a tree held for another feature or for none, a tree the
/// registry does not list - and a `make task-start` the builder ran after the handout is its own word, a bundle's member named.
#[test]
fn the_start_in_force_stands_where_the_pool_names_no_holder_or_the_builder_started_later() {
    let b = Builders::new("pool-no-holder");
    b.held("", &[], "");
    assert_eq!(b.phase_task(), json!("T236"));
    b.held("44", &["T26"], "2026-11-22T00:00:00Z");
    assert_eq!(b.phase_task(), json!("T236"));
    b.held("", &["T26"], "2026-11-22T00:00:00Z");
    assert_eq!(b.phase_task(), json!("T236"));
    let other = Tree {
        tree: b.d.join("elsewhere"),
        feature: "449".to_owned(),
        tasks: vec!["T300".to_owned()],
        since: "2026-11-22T00:00:00Z".to_owned(),
    };
    builder_pool::write(&b.d.join(".git"), &[other]).unwrap();
    assert_eq!(b.phase_task(), json!("T236"));
    // a start after the handout names the task; one before it, and one with no time, do not
    b.held("449", &["T315", "T316"], "2026-11-22T00:00:00Z");
    b.started_at("449-b", "T316", "2026-11-22T00:05:00Z");
    assert_eq!(b.phase_task(), json!("T316"));
    b.held("449", &["T320"], "2026-11-23T00:00:00Z");
    assert_eq!(b.phase_task(), json!("T320"));
    b.started_at("449-b", "T321", "");
    assert_eq!(b.phase_task(), json!("T320"));
    // a handout whose time does not read is older than every timed start
    b.started_at("449-b", "T322", "2026-11-23T00:05:00Z");
    b.held("449", &["T320"], "when");
    assert_eq!(b.phase_task(), json!("T322"));
}

impl Builders {
    /// The log and the task a `Phase` line written in the tree now is filed under, and whether it is marked a fallback.
    fn phase_filed(&self, env: &dyn Fn(&str) -> Option<String>) -> (String, Value, Value) {
        let log = append_row_in(&self.d, None, phase(), "T", env).unwrap();
        let line = last_line(&log);
        let name = log.file_stem().unwrap().to_string_lossy().into_owned();
        (name, line["task"].clone(), line["fallback"].clone())
    }
}

/// Feature 451 T529: a held tree's line is its holder's feature's, whatever the tree's own `feature.json` says or lacks. WHY: the
/// pool tree `diagram-backlog-b1` has no `.specify/feature.json`, so its lines' feature read empty, the pool was never asked, and 647
/// of its `Phase` lines of 2026-11-27 (T417's builder-checks and rust-test runs among them) went to `_unassigned.jsonl` with no task
/// and `fallback: true`; and `diagram-backlog-t269`, held for 461 T08, filed 6 lines in the 451 log under T285 by its stale
/// `feature.json` (observed 2026-11-27, method: every log's `Phase` lines counted by clone, log, task and fallback).
#[test]
fn a_held_trees_line_is_filed_under_its_holders_feature_and_task() {
    let b = Builders::new("pool-holder-feature");
    // the tree's feature.json names 449-b; the pool holds it for 451
    b.held("451", &["T26"], "2026-11-22T00:00:00Z");
    assert_eq!(
        b.phase_filed(&none),
        ("451-a".into(), json!("T26"), Value::Null)
    );
    // no feature.json at all (b1): the holder's still
    std::fs::remove_file(b.d.join(".specify/feature.json")).unwrap();
    b.held("450-c", &["T40"], "2026-11-22T00:00:00Z");
    assert_eq!(
        b.phase_filed(&none),
        ("450-c".into(), json!("T40"), Value::Null)
    );
    // the session's environment declaring another feature does not move a held tree's line
    let declared = |k: &str| (k == "SPECIFY_FEATURE").then(|| "449-b".to_owned());
    assert_eq!(b.phase_filed(&declared).0, "450-c");
    // a free tree, and a holder naming no feature directory, leave the fallback as it was
    b.held("", &[], "");
    assert_eq!(
        b.phase_filed(&none),
        ("_unassigned".into(), Value::Null, json!(true))
    );
    b.held("44", &["T26"], "2026-11-22T00:00:00Z");
    assert_eq!(
        b.phase_filed(&none),
        ("_unassigned".into(), Value::Null, json!(true))
    );
}
