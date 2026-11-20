//! The landing's phase lines (feature 451 T06, plan D5, FR-003): each step of a landing - its first pass, its gate, the cohort, the
//! claims wait, its push - writes one `Phase` line to the event log with its wall-clock span, and the landing a last `end` line with its
//! exit code and the tasks it was asked to land, refused or raised as much as landed.

use std::path::{Path, PathBuf};
use std::time::SystemTime;

use l7r_gate_core::ci::fixtures::{put, scratch};
use serde_json::Value;

use super::super::tests::{fx, tool, Fx, NOTE};

/// Every landing line in the tree's event logs, in the order written (the log a line is filed in is its task's feature's, else the
/// process's, so every log is read).
fn lines(root: &Path) -> Vec<Value> {
    let mut logs: Vec<PathBuf> = std::fs::read_dir(root.join(".git/l7r-events"))
        .into_iter()
        .flatten()
        .flatten()
        .map(|e| e.path())
        .collect();
    logs.sort();
    logs.iter()
        .flat_map(|p| {
            std::fs::read_to_string(p)
                .unwrap_or_default()
                .lines()
                .filter_map(|l| serde_json::from_str::<Value>(l).ok())
                .collect::<Vec<_>>()
        })
        .filter(|v| v["ev"] == "Phase" && v["src"] == "land")
        .collect()
}

/// The steps written, each with its code.
fn steps(root: &Path) -> Vec<(String, i64)> {
    lines(root)
        .iter()
        .map(|l| {
            (
                l["step"].as_str().unwrap_or_default().to_owned(),
                l["code"].as_i64().unwrap_or(-99),
            )
        })
        .collect()
}

fn owned(t: &[&str]) -> Vec<String> {
    t.iter().map(|s| (*s).to_owned()).collect()
}

/// The landing of `tasks`, its `end` line written.
fn landing(fx: &Fx, tasks: &[&str]) -> Result<i32, String> {
    fx.land.landing(
        &fx.root.join("specs/449-x"),
        &owned(tasks),
        NOTE,
        SystemTime::now(),
    )
}

/// The one `end` line.
fn end_of(root: &Path) -> Value {
    let ends: Vec<Value> = lines(root)
        .into_iter()
        .filter(|l| l["step"] == "end")
        .collect();
    assert_eq!(ends.len(), 1, "{ends:?}");
    ends[0].clone()
}

fn s(step: &str, code: i64) -> (String, i64) {
    (step.to_owned(), code)
}

#[test]
fn a_clean_landing_writes_each_step_in_order_and_its_end() {
    let fx = fx("phase-clean");
    let began = SystemTime::now();
    let d = fx.root.join("specs/449-x");
    assert_eq!(fx.land.landing(&d, &owned(&["T1"]), NOTE, began), Ok(0));
    assert_eq!(
        steps(&fx.root),
        [
            s("cheap", 0),
            s("gate", 0),
            s("claims", 0),
            s("push", 0),
            s("end", 0),
            s("after-push", 0)
        ]
    );
    let all = lines(&fx.root);
    // each a span of its own, the steps one after another inside the end's
    let at = |l: &Value, k: &str| l[k].as_str().unwrap().to_owned();
    for l in &all {
        assert!(at(l, "t0") <= at(l, "t1"));
        assert_eq!(at(l, "t"), at(l, "t1"));
        assert_eq!(l["make"], "land");
        assert_eq!(l["clone"], fx.root.display().to_string());
        assert_eq!(l["task"], "T1");
    }
    for pair in all[..4].windows(2) {
        assert!(at(&pair[0], "t1") <= at(&pair[1], "t0"));
    }
    // the end written the moment the push went out, before the push's tail (its own step)
    let end = &all[4];
    assert!(at(end, "t0") <= at(&all[0], "t0"));
    assert!(at(end, "t1") >= at(&all[3], "t1"));
    assert!(at(end, "t1") <= at(&all[5], "t0"));
    assert_eq!(
        at(end, "t0"),
        l7r_guard::guards::event_log_hooks::now_stamp(began)
    );
    assert_eq!(end["tasks"], serde_json::json!(["T1"]));
    assert_eq!(end["landed"], true);
    assert!(all
        .iter()
        .filter(|l| l["step"] != "end")
        .all(|l| l.get("tasks").is_none()));
}

#[test]
fn a_refused_first_pass_writes_its_line_and_the_end_with_its_code() {
    let fx = fx("phase-cheap");
    put(&fx.root, "untracked.txt", "x");
    assert_eq!(landing(&fx, &["T1"]), Ok(2));
    assert_eq!(steps(&fx.root), [s("cheap", 2), s("end", 2)]);
    assert_eq!(end_of(&fx.root)["landed"], false);
}

/// The lines are filed in the landed feature's log, whatever feature.json names - a task never started in the clone too, which T26's
/// chain alone filed by feature.json's feature, marked `fallback`.
#[test]
fn the_lines_are_filed_in_the_landed_feature_even_unstarted() {
    let fx = fx("phase-filed");
    put(
        &fx.root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/450-other\"}\n",
    );
    std::fs::create_dir_all(fx.root.join("specs/450-other")).unwrap();
    put(&fx.root, "untracked.txt", "x");
    assert_eq!(landing(&fx, &["T1"]), Ok(2));
    let log = std::fs::read_to_string(fx.root.join(".git/l7r-events/449-x.jsonl")).unwrap();
    let filed: Vec<Value> = log
        .lines()
        .map(|l| serde_json::from_str(l).unwrap())
        .collect();
    assert_eq!(filed.len(), 2);
    assert!(filed
        .iter()
        .all(|l| l.get("fallback").is_none() && l["task"] == "T1"));
}

/// `main`'s refusal files its `end` in the feature its `F=` names, the task never started.
#[test]
fn main_s_refusal_is_filed_by_its_feature_word() {
    let fx = fx("phase-main-filed");
    put(
        &fx.root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/450-other\"}\n",
    );
    std::fs::create_dir_all(fx.root.join("specs/450-other")).unwrap();
    let nothing = || {};
    let args = owned(&["449", "T1"]);
    assert_eq!(
        super::super::main(&args, &fx.root, " ", &super::super::scripts_of, &nothing),
        Ok(2)
    );
    let log = std::fs::read_to_string(fx.root.join(".git/l7r-events/449-x.jsonl")).unwrap();
    assert!(log.contains("\"step\":\"end\""), "{log}");
}

#[test]
fn a_first_pass_that_raises_writes_code_one() {
    let fx = fx("phase-raise");
    std::fs::write(fx.root.join("specs/449-x/tasks.md"), [0xff]).unwrap();
    assert!(landing(&fx, &["T1"]).is_err());
    assert_eq!(steps(&fx.root), [s("cheap", 1), s("end", 1)]);
}

#[test]
fn a_red_gate_writes_its_code_and_nothing_after_but_the_end() {
    let fx = fx("phase-red");
    fx.answer(
        &format!("{} stamp --check origin/main", tool("gates/l7r-gate.sh")),
        "rc",
        "1",
    );
    fx.answer("make --no-print-directory done NO_CUTOFF=1", "rc", "2");
    assert_eq!(landing(&fx, &["T1"]), Ok(1));
    assert_eq!(steps(&fx.root), [s("cheap", 0), s("gate", 1), s("end", 1)]);
}

#[test]
fn a_claims_wait_that_runs_out_writes_its_code() {
    let fx = fx("phase-claims");
    fx.answers.flight.borrow_mut().push("bundle".to_owned());
    fx.answer(&tool("gates/claims-gate.sh"), "rc", "1");
    fx.answer(
        &tool("gates/claims-gate.sh"),
        "out",
        "claims-gate: REFUSED owed (impl-drift) k\n",
    );
    assert_eq!(landing(&fx, &["T1"]), Ok(2));
    assert_eq!(
        steps(&fx.root),
        [s("cheap", 0), s("gate", 0), s("claims", 2), s("end", 2)]
    );
}

#[test]
fn a_failed_push_writes_its_code_and_lands_nothing() {
    let fx = fx("phase-push");
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "1");
    assert_eq!(landing(&fx, &["T1"]), Ok(1));
    assert_eq!(
        steps(&fx.root),
        [
            s("cheap", 0),
            s("gate", 0),
            s("claims", 0),
            s("push", 1),
            s("end", 1)
        ]
    );
    assert_eq!(end_of(&fx.root)["landed"], false);
}

/// THE PUSH IS THE LANDING (T06's plan review, T06-stop-after-push): the `end` is written the moment the push goes out, so a landing
/// stopped in the push's tail (the fresh block's start, the work-budget view) still reads landed; the tail is its own step, and its
/// raise its own line's code, the `end` standing at the push's.
#[test]
fn the_end_is_written_at_the_push_and_the_tail_is_its_own_step() {
    let fx = super::super::tests::fx_engine_with_budget("phase-tail", "{");
    assert!(landing(&fx, &["T1"]).is_err());
    let steps = steps(&fx.root);
    assert_eq!(
        steps[steps.len() - 3..],
        [s("push", 0), s("end", 0), s("after-push", 1)]
    );
    assert_eq!(end_of(&fx.root)["landed"], true);
}

/// A push whose pull merged other sessions' edits exits 3 with its ticks standing: a landing, which `landed` says, its code apart.
#[test]
fn a_push_that_merged_is_a_landing_whatever_its_code() {
    let fx = fx("phase-merged");
    fx.answer(&format!("{} done", tool("sync-with-main.sh")), "rc", "3");
    assert_eq!(landing(&fx, &["T1"]), Ok(3));
    let end = end_of(&fx.root);
    assert_eq!(
        (end["code"].as_i64(), &end["landed"]),
        (Some(3), &Value::Bool(true))
    );
}

/// Two tasks landed at once: the `end` names both (T13 and T14 read a landing of a task from it); here the second's tick refuses.
#[test]
fn a_landing_of_two_tasks_names_both_in_its_end() {
    let fx = fx("phase-two");
    assert_eq!(landing(&fx, &["T1", "T2"]), Ok(2));
    assert_eq!(steps(&fx.root).last(), Some(&s("end", 2)));
    assert_eq!(steps(&fx.root)[3], s("push", 2));
    assert_eq!(end_of(&fx.root)["tasks"], serde_json::json!(["T1", "T2"]));
}

/// `main`'s own refusals are refused landings too, their tasks split as the landing splits them; a usage refusal names no landing.
#[test]
fn main_s_refusals_write_an_end() {
    let fx = fx("phase-main");
    // no refusal here reaches the landing, so the gate tree is never asked
    let scripts = super::super::scripts_of;
    let args = |a: &[&str]| owned(a);
    let nothing = || {};
    assert_eq!(
        super::super::main(&args(&["449"]), &fx.root, NOTE, &scripts, &nothing),
        Ok(2)
    );
    assert!(lines(&fx.root).is_empty());
    assert_eq!(
        super::super::main(&args(&["449", "T1 T2"]), &fx.root, " ", &scripts, &nothing),
        Ok(2)
    );
    assert_eq!(end_of(&fx.root)["tasks"], serde_json::json!(["T1", "T2"]));
    assert_eq!(end_of(&fx.root)["code"], 2);
    let other = scratch("phase-main-none");
    put(&other, "x", "");
    l7r_gate_core::ci::fixtures::git(&other, &["init", "-q"]);
    assert_eq!(
        super::super::main(&args(&["7", "T3"]), &other, NOTE, &scripts, &nothing),
        Ok(2)
    );
    assert_eq!(end_of(&other)["tasks"], serde_json::json!(["T3"]));
}

fn gate(rest: &str) -> String {
    format!("{} {rest}", tool("gates/l7r-gate.sh"))
}

/// An engine delta with no landing cohort, 8 GB free, whose stamp names `make done` (the second pass's own fixture, `named`).
fn engine(tag: &str) -> Fx {
    let fx = fx(tag);
    fx.in_delta("l7r/diagram/a.py", "x = 1\n");
    fx.answer(&gate("cohort rust-owed"), "rc", "1");
    fx.answer(&gate("cohort check"), "rc", "1");
    fx.answer(
        &gate("stamp --check origin/main"),
        "out",
        "stale (make done again)\n",
    );
    std::fs::write(&fx.land.meminfo, "MemAvailable: 8192000 kB\n").unwrap();
    fx
}

/// The cohort beside the gate: its line spans its own run, from its start to its wait, its code its own.
#[test]
fn a_cohort_beside_the_gate_writes_its_own_line() {
    let fx = engine("phase-cohort");
    fx.answer(&gate("stamp --check origin/main"), "rcs", "1\n0\n");
    fx.answer("make --no-print-directory cohort-landing JOBS=8", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert_eq!(steps(&fx.root), [s("cohort", 1)]);
}

/// A red gate stops the cohort beside it: its line is still written, its code the signal that stopped it.
#[test]
fn a_cohort_a_red_gate_stopped_writes_its_line() {
    let fx = engine("phase-cohort-stopped");
    fx.answer(&gate("stamp --check origin/main"), "rcs", "1\n");
    fx.answer(
        "make --no-print-directory cohort-landing JOBS=8",
        "sh",
        "sleep 20\n",
    );
    fx.answer("make --no-print-directory done NO_CUTOFF=1", "rc", "2");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert_eq!(steps(&fx.root), [s("cohort", -15)]);
}

/// The cohort after a gate the stamp covered: its line, then the second pass's.
#[test]
fn a_cohort_run_alone_writes_its_line() {
    let fx = fx("phase-cohort-alone");
    fx.in_delta("pool/a.json", "{}\n");
    fx.answer(&gate("cohort rust-owed"), "rc", "1");
    fx.answer(&gate("cohort check"), "rc", "1");
    fx.answer("make --no-print-directory cohort-landing", "rc", "1");
    assert_eq!(fx.land.long_runs(), Ok(1));
    assert_eq!(steps(&fx.root), [s("cohort", 1)]);
}

/// A fake `/proc`: each process's `stat` (its parent the fourth field), `comm` and NUL-joined `cmdline`.
fn proc(dir: &Path, pid: u32, parent: u32, comm: &str, cmdline: &[&str]) {
    put(
        dir,
        &format!("{pid}/stat"),
        &format!("{pid} ({comm}) S {parent} 1 1 0\n"),
    );
    put(dir, &format!("{pid}/comm"), &format!("{comm}\n"));
    put(dir, &format!("{pid}/cmdline"), &(cmdline.join("\0") + "\0"));
}

#[test]
fn the_make_target_is_the_outermost_make_s_first_goal() {
    let p = scratch("phase-proc");
    proc(&p, 40, 1, "bash", &["bash"]);
    proc(
        &p,
        30,
        40,
        "make",
        &["make", "land-batch", "F=451", "NOTE=two words", "T=T1"],
    );
    proc(&p, 20, 30, "make", &["make", "-C", "x", "inner"]);
    proc(&p, 10, 20, "l7r-gate", &["l7r-gate", "land"]);
    assert_eq!(super::run_target(&p, 10), "land-batch");
    // a goal-less make, and no make at all
    proc(&p, 31, 40, "make", &["make", "F=451"]);
    proc(&p, 11, 31, "l7r-gate", &["l7r-gate", "land"]);
    assert_eq!(super::run_target(&p, 11), "land");
    proc(&p, 12, 40, "l7r-gate", &["l7r-gate", "land"]);
    assert_eq!(super::run_target(&p, 12), "land");
    assert_eq!(super::run_target(&p, 99), "land");
}
