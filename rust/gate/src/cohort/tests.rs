//! The landing cohort, the seeds' standing and the seed report, on real repositories with a stand-in Python.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::known::{baselines, newly_failing, seeds_named, standing};
use super::{
    check, cli, needs_baseline, pick, port_mode, rate_line, room, rust_refusal, seeds, Repo,
};
use super::{int, rust_landing, text, truthy};
use crate::ci::fixtures::{commit, git, put, python, repo};

/// main's engine at the first return; a `work` commit changes it at the second.
fn work(tag: &str, port: Option<&str>) -> (PathBuf, String, String, String) {
    let root = repo(tag);
    if let Some(port) = port {
        commit(
            &root,
            "dev/switches.json",
            &json!({"port": {"state": port}}).to_string(),
        );
    }
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let base = git(&root, &["rev-parse", "--short", "HEAD"]);
    commit(&root, "l7r/diagram/m.py", "x = 2\n");
    let head = git(&root, &["rev-parse", "--short", "HEAD"]);
    let py = python(&root);
    (root, base, head, py)
}

fn seed(n: i64, bad: &[i64], fresh: bool) -> Value {
    let failing = bad.contains(&n);
    let mut s = json!({"seed": n, "verdict": if failing { "fail" } else { "pass" }, "failures": if failing { json!(["lane_knots"]) } else { json!([]) }, "counts": if failing { json!({"lane_knots": 1}) } else { json!({}) }});
    if fresh {
        s["fresh"] = json!(true);
    }
    s
}

/// A record as the cohort writes it: 48 fixed seeds from `first`, the pinned rows, `fresh` seeds from 20000.
fn rec(root: &Path, utc: &str, commit: &str, first: i64, bad: &[i64], fresh: i64) -> Value {
    let mut all: Vec<Value> = (first..first + 48)
        .chain(901..907)
        .map(|n| seed(n, bad, false))
        .collect();
    all.extend((20_000..20_000 + fresh).map(|n| seed(n, bad, true)));
    let r = json!({"utc": utc, "commit": commit, "first_seed": first, "households": null, "seeds": all});
    put(
        root,
        &format!("dev/cohort-log/2026{utc}-t.json"),
        &r.to_string(),
    );
    r
}

#[test]
fn the_fresh_seed_follows_the_engine_and_stays_above_the_fixed_range() {
    let (root, _, _, py) = work("fresh", Some("integrated"));
    let r = Repo::new(&root, &py);
    let one = r.fresh_seed(None);
    assert!(one == r.fresh_seed(None) && (10_000..1_000_000).contains(&one));
    put(&root, "pool/p.json", "[]\n");
    assert_ne!(r.fresh_seed(None), one);
    std::fs::remove_file(root.join("pool/p.json")).unwrap();
    put(&root, "README", "docs\n");
    assert_eq!(r.fresh_seed(None), one);
}

#[test]
fn which_records_count() {
    let (root, base, head, py) = work("count", Some("integrated"));
    let r = Repo::new(&root, &py);
    let mut dirty = rec(&root, "u3", &head, 1, &[], 48);
    dirty["engine_diff"] = json!("abc");
    let mut sized = rec(&root, "u6", &head, 1, &[], 48);
    sized["households"] = json!(40);
    let mut few = rec(&root, "u7", &head, 1, &[], 48);
    few["seeds"] = json!([{"seed": 1, "verdict": "pass"}]);
    let mut partial = rec(&root, "u10", &head, 1, &[], 48);
    partial["partial"] = json!(true);
    let mut recs = vec![
        rec(&root, "u1", &base, 1, &[], 48),
        rec(&root, "u2", &head, 15, &[], 48),
        dirty,
        rec(&root, "u4", "nosuchcommit", 1, &[], 48),
        sized,
        few,
        partial,
    ];
    assert_eq!(pick(&r, &recs), None);
    let landing = rec(&root, "u8", &head, 1, &[], 48);
    recs.push(landing.clone());
    assert_eq!(pick(&r, &recs), Some(&landing));
    let fixed_only = rec(&root, "u9", &head, 1, &[], 0);
    recs.pop();
    recs.push(fixed_only.clone());
    assert_eq!(pick(&r, &recs), Some(&fixed_only));
    assert!(rate_line(&fixed_only).contains("after the push"));
}

#[test]
fn the_check_refuses_a_regression_and_passes_a_pre_existing_failure() {
    let (root, base, head, py) = work("regress", Some("integrated"));
    let r = Repo::new(&root, &py);
    let (refusals, _) = check(&r);
    assert!(refusals.len() == 1 && refusals[0].contains("make cohort-landing"));
    assert!(needs_baseline(&r));
    rec(&root, "u1", &base, 1, &[], 0);
    assert!(!needs_baseline(&r));
    rec(&root, "u2", &head, 1, &[5, 20_001], 48);
    let (refusals, notes) = check(&r);
    assert!(!refusals.is_empty() && refusals.iter().all(|l| l.contains("seed 5 NEWLY FAILING")));
    assert!(notes
        .iter()
        .any(|n| n.contains("fresh block from seed 20000: 1 of 48 failed (2%) - seeds 20001")));
    rec(&root, "u4", &base, 1, &[5], 48);
    rec(&root, "u5", &head, 1, &[5], 48);
    let (refusals, notes) = check(&r);
    assert!(refusals.is_empty() && notes.iter().any(|n| n.contains("seed 5 PRE-EXISTING")));
}

#[test]
fn a_failing_seed_with_no_baseline_is_refused_and_main_s_is_asked_for() {
    let (root, _, head, py) = work("nobase", Some("integrated"));
    let r = Repo::new(&root, &py);
    rec(&root, "u1", &head, 1, &[9], 48);
    assert!(check(&r)
        .0
        .iter()
        .any(|l| l.contains("seed 9") && l.contains("NO BASELINE")));
    assert!(needs_baseline(&r));
}

#[test]
fn a_missing_cohort_names_the_pool_maps_the_gate_regenerated() {
    let (root, _, _, py) = work("maps", Some("integrated"));
    let r = Repo::new(&root, &py);
    assert!(!check(&r).0[0].contains("uncommitted pool maps"));
    put(&root, "pool/hamlets/x/x.json", "{}");
    assert!(check(&r).0[0].contains("uncommitted pool maps (pool/hamlets/x/x.json)"));
}

/// A stand-in `codeid.py` answering every pair `answer`, or failing with no answer.
fn answers(root: &Path, name: &str, body: &str) -> String {
    let path = root.join(".git").join(name);
    crate::write_executable(&path, &format!("#!/bin/sh\nshift 2\n{body}\n"));
    path.display().to_string()
}

const YES: &str = "while [ $# -gt 0 ]; do echo 1; shift 2; done";
const NO: &str = "while [ $# -gt 0 ]; do echo 0; shift 2; done";

#[test]
fn counter_only_needs_every_engine_file_a_modification_equal_but_for_counters() {
    let (root, base, _, py) = work("counters", Some("integrated"));
    assert!(!Repo::new(&root, &py).counter_only("nosuch", "HEAD"));
    let no = answers(&root, "no", NO);
    assert!(!Repo::new(&root, &no).counter_only(&base, "HEAD"));
    let yes_path = answers(&root, "yes", YES);
    let yes = Repo::new(&root, &yes_path);
    assert!(yes.counter_only(&base, "HEAD") && yes.counter_only(&base, "HEAD"));
    commit(&root, "rust/a.rs", "fn f() {}\n");
    assert!(!Repo::new(&root, &yes_path).counter_only(&base, "HEAD"));
    let docs = git(&root, &["rev-parse", "HEAD"]);
    commit(&root, "docs/a.md", "x");
    assert!(!Repo::new(&root, &yes_path).counter_only(&docs, "HEAD"));
    commit(&root, "rust/a.rs", "fn g() {}\n");
    let before = git(&root, &["rev-parse", "HEAD~1"]);
    assert!(!Repo::new(&root, &yes_path).counter_only(&before, "HEAD"));
    assert_eq!(cli(&["counter-only".to_owned()], &root, &yes_path).code, 1);
}

#[test]
fn the_rust_stage_gate_holds_every_engine_landing_and_the_port_switch_reads_it_as_a_rate() {
    let (root, _, _, py) = work("rust", Some("integrated"));
    let r = Repo::new(&root, &py);
    assert_eq!(rust_refusal(&r), None);
    commit(&root, "rust/phases/src/w.rs", "fn f() {}\n");
    assert!(rust_refusal(&r)
        .unwrap()
        .starts_with("no Rust stage gate record"));
    let key = r.engine_key(None);
    put(&root, "dev/rust-gate/failing.json", "[]\n");
    put(
        &root,
        "dev/rust-gate/1.json",
        &json!({"engine": "K0", "failing": 0}).to_string(),
    );
    put(&root, "dev/rust-gate/2.json", "not json");
    assert!(rust_refusal(&r)
        .unwrap()
        .starts_with("no Rust stage gate record"));
    put(
        &root,
        "dev/rust-gate/3.json",
        &json!({"engine": r.engine_key(None), "failing": 2}).to_string(),
    );
    let key_now = r.engine_key(None);
    assert_eq!(key, key_now);
    assert!(rust_refusal(&r).unwrap().contains("2 failing seed(s)"));
    let (refusals, notes) = check(&r);
    assert!(
        refusals.iter().all(|l| l.contains("Rust stage gate"))
            && notes
                .iter()
                .any(|n| n.contains("a Rust-stage landing, a rate"))
    );
    assert_eq!(cli(&["rust-owed".to_owned()], &root, &py).code, 0);
    put(
        &root,
        "dev/switches.json",
        &json!({"port": {"state": "rust-only"}}).to_string(),
    );
    let (refusals, notes) = check(&r);
    assert!(refusals.is_empty() && notes.iter().any(|n| n.contains("not a refusal")));
    assert_eq!(cli(&["rust-owed".to_owned()], &root, &py).code, 1);
    put(
        &root,
        "dev/rust-gate/4.json",
        &json!({"engine": key, "failing": 0}).to_string(),
    );
    assert_eq!(rust_refusal(&r), None);
}

#[test]
fn a_malformed_port_entry_closes_to_the_committed_state() {
    let (root, ..) = work("port", Some("integrated"));
    assert_eq!(port_mode(&root), "integrated");
    put(&root, "dev/switches.json", "not json");
    assert_eq!(port_mode(&root), "integrated");
    put(&root, "dev/switches.json", "[]");
    assert_eq!(port_mode(&root), "integrated");
    put(&root, "dev/switches.json", "{\"claims\": {}}");
    assert_eq!(port_mode(&root), "rust-only");
    put(
        &root,
        "dev/switches.json",
        "{\"port\": {\"state\": \"maybe\"}}",
    );
    assert_eq!(port_mode(&root), "integrated");
    let bare = repo("portbare");
    assert_eq!(port_mode(&bare), "rust-only");
    put(&bare, "dev/switches.json", "not json");
    assert_eq!(port_mode(&bare), "rust-only");
}

fn say(root: &Path, py: &str, words: &[&str]) -> crate::Reply {
    let owned: Vec<String> = words.iter().map(|s| (*s).to_owned()).collect();
    cli(&owned, root, py)
}

#[test]
fn the_command_line_answers_every_verb() {
    let (root, base, head, py) = work("cli", Some("integrated"));
    assert_eq!(say(&root, &py, &["check"]).code, 1);
    assert!(say(&root, &py, &[]).stdout.contains("REFUSED"));
    rec(&root, "u1", &base, 1, &[], 0);
    rec(&root, "u2", &head, 1, &[], 0);
    assert_eq!(say(&root, &py, &["check"]).code, 0);
    assert!(say(&root, &py, &["fresh-seed"])
        .stdout
        .trim()
        .parse::<u64>()
        .is_ok());
    assert_eq!(say(&root, &py, &["fresh-seed", "nosuch"]).code, 0);
    assert_eq!(say(&root, &py, &["engine-key", "nosuch"]).stdout, "\n");
    assert_eq!(
        say(&root, &py, &["engine-key", "HEAD"]).stdout,
        say(&root, &py, &["engine-key", "HEAD"]).stdout
    );
    assert_eq!(say(&root, &py, &["port"]).stdout, "integrated\n");
    assert_eq!(say(&root, &py, &["counter-only"]).code, 1);
    assert_eq!(say(&root, &py, &["needs-baseline"]).code, 1);
    assert_eq!(say(&root, &py, &["rust-owed"]).code, 1);
    assert_eq!(say(&root, &py, &["sideways"]).code, 2);
    assert_eq!(say(&root, &py, &["names-fit", "a typo"]).code, 1);
    assert_eq!(say(&root, &py, &["names-fit", "two knots here"]).code, 0);
    assert_eq!(say(&repo("nobase-cli"), &py, &["counter-only"]).code, 1);
}

#[test]
fn the_seeds_a_row_lists_are_read_from_its_words() {
    assert_eq!(
        seeds_named("(seeds 7, 2, 10, 8 under routes B-D)")
            .into_iter()
            .collect::<Vec<_>>(),
        [2, 7, 8, 10]
    );
    assert_eq!(
        seeds_named("valley seed 18 and 22 when")
            .into_iter()
            .collect::<Vec<_>>(),
        [18, 22]
    );
    assert!(seeds_named("no seed named, 40 households").is_empty());
}

#[test]
fn a_failing_seed_an_open_row_lists_is_named_and_a_closed_row_is_not() {
    let (root, _, _, py) = work("known", Some("integrated"));
    let rows = [
        json!({"key": "settle#re-deal", "tier": "E4", "fix": "x", "found": "seeds 7, 2, 10, 8"}),
        json!({"key": "closed#row", "tier": "E1", "fix": "x", "found": "seed 10 once"}),
        json!({"key": "untiered#row", "found": "seed 3"}),
    ];
    let audit = "specs/328-match-the-research/audit";
    put(
        &root,
        &format!("{audit}/found-wave149.jsonl"),
        &(rows
            .iter()
            .map(Value::to_string)
            .collect::<Vec<_>>()
            .join("\n")
            + "\n\n"),
    );
    put(
        &root,
        &format!("{audit}/waves.json"),
        "{\"closed#row\": \"150\"}",
    );
    put(&root, "dev/cohort-log/20261013T125506Z-x.json", &json!({"seeds": [{"seed": 10, "verdict": "fail"}, {"seed": 3, "verdict": "fail"}, {"seed": 7, "verdict": "pass"}]}).to_string());
    put(&root, "dev/cohort-log/features.json", "{}");
    let got = say(
        &root,
        &py,
        &["known", "--root", &root.display().to_string()],
    );
    assert!(got.stdout.contains("cohort: seed 10 is named by an open found row - settle#re-deal (E4); go to that row before probing"));
    assert!(got
        .stdout
        .contains("seed 3 is named by an open found row - untiered#row (?)"));
    assert!(!got.stdout.contains("closed#row"));
}

fn always(_: &str) -> bool {
    true
}

fn s(n: i64, verdict: &str, counts: &Value, failures: &Value) -> Value {
    json!({"seed": n, "verdict": verdict, "counts": counts, "failures": failures})
}

#[test]
fn each_failing_seed_is_read_against_its_baseline_on_mains_engine() {
    let one = json!({"lane_knots": 1});
    let none = json!([]);
    let empty = json!({});
    let base = json!({"utc": "20261017T1000Z", "commit": "main1", "households": null, "seeds": [s(17, "fail", &one, &none), s(21, "pass", &empty, &none), s(55, "fail", &one, &none), s(57, "fail", &one, &none), s(58, "fail", &empty, &json!(["refused:WebRefused"]))]});
    let other = json!({"utc": "20261017T1100Z", "commit": "clone9", "households": null, "seeds": [s(60, "pass", &empty, &none)]});
    let now = json!({"utc": "20261017T2000Z", "commit": "x", "households": null, "seeds": [s(17, "pass", &empty, &none), s(21, "fail", &json!({"fabric": 2}), &none), s(55, "fail", &one, &none), s(57, "fail", &json!({"lane_knots": 4}), &none), s(58, "refused", &empty, &json!(["refused:WebRefused", "lane_knots"])), s(59, "fail", &json!({"bends": 1}), &none), s(60, "fail", &json!({"bends": 1}), &none), s(61, "pass", &empty, &none)]});
    let earlier = [base, other];
    let got = standing(&now, &baselines(&now, &earlier, &|c| c.starts_with("main")));
    assert_eq!(got[0], "cohort: seed 17 FIXED (was: lane_knots 1)");
    assert_eq!(got[1], "cohort: seed 21 NEWLY FAILING (fabric 2)");
    assert_eq!(
        got[2],
        "cohort: seed 55 PRE-EXISTING (lane_knots 1; was: lane_knots 1)"
    );
    assert_eq!(
        got[3],
        "cohort: seed 57 WORSENED (lane_knots 4; was: lane_knots 1)"
    );
    assert!(got[4].starts_with("cohort: seed 58 WORSENED"));
    assert!(
        got[5].contains("seed 59 fails (bends 1) with NO BASELINE")
            && got[5].contains("make -C /tmp/base cohort N=1 SEED=59")
    );
    assert!(got[6].contains("seed 60 fails") && got.len() == 7);
    let mut stamped = earlier[0].clone();
    stamped["engine_diff"] = json!("d");
    assert!(baselines(&now, &[stamped], &always).is_empty());
    assert_eq!(
        newly_failing(&now, &earlier, &|c| c.starts_with("main")),
        [21]
    );
}

#[test]
fn a_seed_newly_failing_owes_part_b_and_a_baseless_one_is_no_news() {
    let empty = json!({});
    let none = json!([]);
    let now = json!({"utc": "b", "households": null, "seeds": [s(1, "fail", &empty, &none)]});
    let wrong = json!({"utc": "z", "households": null, "commit": "main", "seeds": [s(1, "pass", &empty, &none)]});
    let sized = json!({"utc": "a", "households": 3, "commit": "main", "seeds": [s(1, "pass", &empty, &none)]});
    let other_seed = json!({"utc": "a", "households": null, "commit": "main", "seeds": [s(2, "pass", &empty, &none)]});
    let dirty = json!({"utc": "a", "households": null, "commit": "main", "engine_diff": "d", "seeds": [s(1, "pass", &empty, &none)]});
    let failing = json!({"utc": "a", "households": null, "commit": "main", "seeds": [s(1, "fail", &empty, &none)]});
    assert!(newly_failing(&now, &[wrong, sized, other_seed, dirty], &always).is_empty());
    assert!(newly_failing(&now, &[failing], &always).is_empty());
}

#[test]
fn a_roll_over_an_uncommitted_engine_diff_is_stamped() {
    let (root, _, _, py) = work("stamp", Some("integrated"));
    let flag = |root: &Path| say(root, &py, &["known", "--stamp"]);
    assert_eq!(flag(&root).stdout, "");
    put(
        &root,
        "dev/cohort-log/20261018T0000Z-x.json",
        &json!({"utc": "u", "seeds": []}).to_string(),
    );
    assert_eq!(flag(&root).stdout, "");
    put(&root, "l7r/diagram/m.py", "x = 3\n");
    assert!(flag(&root)
        .stdout
        .contains("rolled over an uncommitted engine diff"));
    let back: Value = serde_json::from_str(
        &std::fs::read_to_string(root.join("dev/cohort-log/20261018T0000Z-x.json")).unwrap(),
    )
    .unwrap();
    assert_eq!(back["engine_diff"].as_str().unwrap().len(), 16);
    put(&root, "dev/cohort-log/20261019T0000Z-y.json", "not json");
    assert_eq!(flag(&root).stdout, "");
}

#[test]
fn a_cohort_with_a_newly_failing_seed_prints_what_is_owed_only_when_a_task_is_in_flight() {
    let (root, base, head, py) = work("owed", Some("integrated"));
    rec(&root, "u1", &base, 1, &[], 0);
    rec(&root, "u2", &head, 1, &[5], 0);
    let got = say(&root, &py, &["known"]);
    assert_eq!(got.code, 0, "{}", got.stderr);
    assert!(got.stdout.contains("seed 5 NEWLY FAILING"));
    assert_eq!(say(&repo("owed-none"), &py, &["known"]).stdout, "");
}

#[test]
fn the_room_table_renders_and_a_fit_failure_is_named() {
    let root = repo("room");
    put(&root, "scripts/gates/room_table.json", &json!({"rows": [{"knob": "gap", "where": "w", "value": 5, "label": "GUESS", "measures": "m", "ceiling": "c", "band": "grows"}]}).to_string());
    let out = say(&root, "python3", &["room-table"]).stdout;
    assert!(
        out.contains("| `gap` (w) | 5 | GUESS | m | c | grows |") && out.contains("DOES NOT GROW")
    );
    assert!(
        room::is_fit(&[json!("refused:WebRefused")])
            && room::is_fit(&[json!("lane_knots")])
            && !room::is_fit(&[json!("row_rules")])
    );
    assert!(room::names_fit("an unreached house") && !room::names_fit("a typo"));
}

#[test]
fn the_seed_report_names_each_failure_the_span_and_the_rate() {
    let root = repo("seeds");
    let log = "dev/cohort-log";
    put(&root, &format!("{log}/features.json"), "{\"c1\": \"386\"}");
    put(&root, &format!("{log}/1.json"), &json!({"commit": "c1", "first_seed": 1, "seeds": [{"seed": 3, "failures": ["refused:Web[2]"]}, {"seed": 901, "failures": ["pinned_only"]}]}).to_string());
    put(&root, &format!("{log}/2.json"), &json!({"commit": "c2", "feature": "400", "first_seed": 1, "seeds": [{"seed": 5, "failures": ["refused:Web"]}, {"seed": 20000, "fresh": true, "failures": ["x"]}, {"seed": 20001, "fresh": true, "verdict": "pass"}]}).to_string());
    put(
        &root,
        &format!("{log}/3.json"),
        &json!({"commit": "c3", "seeds": []}).to_string(),
    );
    put(
        &root,
        &format!("{log}/5.json"),
        &json!({"seeds": []}).to_string(),
    );
    put(&root, &format!("{log}/4.json"), &json!({"utc": "u", "commit": "c4", "first_seed": 10_000, "seeds": [{"seed": 10_000, "verdict": "fail"}, {"seed": 902, "verdict": "fail"}]}).to_string());
    let out = say(&root, "python3", &["seeds"]).stdout;
    assert!(
        out.contains("5 record(s) over 4 change(s): feature 386, feature 400, unattributed (?), unattributed (c3)")
    );
    assert!(out.contains("  refused:Web: seeds 3, 5 - on feature 386, feature 400"));
    assert!(out.contains("find every failure: 3 (and the pinned rows for pinned_only)"));
    assert!(out.contains(
        "fresh seeds (feature 386 - a rate on seeds never tuned on, never a refusal): 2 record(s)"
    ));
    assert!(out.contains("u c4 from 10000: 1 of 1 failed (100%) - seeds 10000"));
    assert!(out.contains("pooled: 2 of 3 failed (67%)"));
    let target = root.join("m.json").display().to_string();
    put(&root, "m.json", "{\"k\": {\"note\": 1}}");
    assert_eq!(
        say(
            &root,
            "python3",
            &["seeds", "--record", &target, "--key", "k"]
        )
        .code,
        0
    );
    let back: Value = serde_json::from_str(&std::fs::read_to_string(&target).unwrap()).unwrap();
    assert!(back["k"]["note"] == 1 && back["k"]["value"]["records"] == 5);
    assert_eq!(
        say(
            &root,
            "python3",
            &["seeds", "--record", &target, "--key", "new"]
        )
        .code,
        0
    );
    assert_eq!(
        say(&root, "python3", &["seeds", "--record", &target]).code,
        2
    );
    let none = repo("seeds-none");
    let empty = say(
        &none,
        "python3",
        &[
            "seeds",
            "--log",
            &none.join("nothing").display().to_string(),
        ],
    )
    .stdout;
    assert!(
        empty.contains("0 record(s) over 0 change(s): none")
            && empty.contains("no failures recorded")
    );
    assert_eq!(seeds::dumped(&json!({"a": 1})), "{\n \"a\": 1\n}\n");
}

fn record(utc: &str, commit: &str, verdicts: &[(i64, &str)], households: Option<i64>) -> Value {
    let all: Vec<Value> = verdicts
        .iter()
        .map(|(n, v)| json!({"seed": n, "verdict": v}))
        .collect();
    json!({"utc": utc, "commit": commit, "households": households, "seeds": all})
}

#[test]
fn a_seed_is_newly_failing_only_against_a_baseline_on_main() {
    let main = |c: &str| c == "m1" || c == "m2";
    let now = record(
        "20261017T2000Z",
        "c9",
        &[
            (1, "pass"),
            (2, "fail"),
            (3, "fail"),
            (4, "fail"),
            (5, "fail"),
        ],
        None,
    );
    let mut earlier = vec![
        record(
            "20261017T1000Z",
            "m1",
            &[(2, "pass"), (3, "pass"), (4, "fail")],
            None,
        ),
        record("20261017T1100Z", "m2", &[(3, "fail")], None),
        record("20261017T1200Z", "c8", &[(5, "pass")], None),
        record("20261017T1300Z", "m2", &[(2, "pass")], Some(40)),
        record("20261017T2100Z", "m2", &[(4, "pass")], None),
    ];
    assert_eq!(newly_failing(&now, &earlier, &main), [2]);
    let mut dirty = record("20261017T1500Z", "m2", &[(3, "fail")], None);
    dirty["engine_diff"] = json!("abc");
    earlier.push(dirty.clone());
    assert_eq!(newly_failing(&now, &earlier, &main), [2]);
    let mine = [record("20261017T1000Z", "m1", &[(3, "pass")], None), dirty];
    assert_eq!(newly_failing(&now, &mine, &main), [3]);
}

#[test]
fn a_cohort_with_a_newly_failing_seed_owes_part_b_and_a_fit_failure_the_room_table() {
    let root = repo("approach");
    let py = python(&root);
    put(
        &root,
        "docs/approach-checklist.md",
        "## A. x\n\n1. a\n\n## B. y\n\n1. b\n",
    );
    put(&root, "specs/999-x/plan.md", "## T01 x\n");
    put(&root, "specs/999-x/tasks.md", "- [ ] T01 x\n");
    put(&root, "scripts/gates/room_table.json", &json!({"rows": [{"knob": "grow_gap", "where": "w", "value": 5, "label": "GUESS", "measures": "m", "ceiling": "c", "band": "grows"}]}).to_string());
    commit(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/999-x\"}",
    );
    let head = git(&root, &["rev-parse", "HEAD"]);
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    let owed = |root: &Path| say(root, &py, &["known"]).stdout;
    assert_eq!(owed(&root), "");
    let log = "dev/cohort-log";
    put(
        &root,
        &format!("{log}/20261017T1000Z-a.json"),
        &record("20261017T1000Z", &head, &[(7, "pass"), (8, "pass")], None).to_string(),
    );
    let mut now = record(
        "20261017T2000Z",
        "feedface",
        &[(7, "fail"), (8, "pass")],
        None,
    );
    now["seeds"][0]["failures"] = json!(["row_rules"]);
    put(
        &root,
        &format!("{log}/20261017T2000Z-a.json"),
        &now.to_string(),
    );
    let msg = owed(&root);
    assert!(
        msg.contains("seed(s) 7 newly failing")
            && msg.contains("part B")
            && !msg.contains("room table")
    );
    let mut now = record(
        "20261017T2100Z",
        "feedface",
        &[(7, "pass"), (8, "refused")],
        None,
    );
    now["seeds"][1]["failures"] = json!(["refused:WebRefused"]);
    put(
        &root,
        &format!("{log}/20261017T2100Z-a.json"),
        &now.to_string(),
    );
    let msg = owed(&root);
    assert!(
        msg.contains("seed(s) 8 newly failing")
            && msg.contains("## The room table")
            && msg.contains("`grow_gap`")
    );
    put(
        &root,
        &format!("{log}/20261017T2200Z-a.json"),
        &record("20261017T2200Z", "feedface", &[(9, "fail")], None).to_string(),
    );
    assert!(!owed(&root).contains("newly failing"));
}

#[test]
fn a_record_s_values_read_as_python_read_them() {
    assert_eq!(int(&json!("5")), 5);
    assert_eq!(int(&json!("x")), 0);
    assert_eq!(text(&json!({}), "utc"), "None");
    assert_eq!(text(&json!({"utc": 7}), "utc"), "7");
    assert!(
        truthy(&json!(1)) && !truthy(&json!(0)) && truthy(&json!({"a": 1})) && !truthy(&json!({}))
    );
    assert!(
        truthy(&json!(true)) && !truthy(&Value::Null) && truthy(&json!([1])) && !truthy(&json!(""))
    );
}

#[test]
fn the_key_is_kept_a_same_text_is_equal_and_no_origin_reads_main() {
    let (root, ..) = work("kept", None);
    let py = python(&root);
    let r = Repo::new(&root, &py);
    assert_eq!(r.engine_key(Some("HEAD")), r.engine_key(Some("HEAD")));
    r.prime(&[]);
    git(&root, &["update-ref", "-d", "refs/remotes/origin/main"]);
    assert!(r.same_engine("HEAD"));
    assert!(!rust_landing(&root));
    let failed = json!({"seed": 1, "verdict": "fail", "failures": [3]});
    let now = json!({"seeds": [failed]});
    assert!(standing(&now, &std::collections::BTreeMap::new())[0].contains("(3)"));
}

#[test]
fn a_run_with_several_differing_records_starts_codeid_once() {
    let (root, base, head, py) = work("once", Some("integrated"));
    commit(&root, "l7r/diagram/m.py", "x = 3\n");
    let third = git(&root, &["rev-parse", "--short", "HEAD"]);
    commit(&root, "l7r/diagram/m.py", "x = 4\n");
    rec(&root, "u1", &base, 1, &[], 0);
    rec(&root, "u2", &head, 1, &[], 0);
    rec(&root, "u3", &third, 1, &[], 0);
    assert_eq!(say(&root, &py, &["known"]).code, 0);
    let calls = std::fs::read_to_string(format!("{py}.calls")).unwrap();
    assert_eq!(calls.lines().count(), 1);
}

#[test]
fn each_counter_question_has_its_own_scratch_directory() {
    assert_ne!(counter_dir(), counter_dir());
}

#[test]
fn codeid_failing_fails_the_gate_with_no_substitute_answer() {
    let (root, base, head, _) = work("failing", Some("integrated"));
    rec(&root, "u1", &base, 1, &[], 0);
    rec(&root, "u2", &head, 1, &[], 0);
    let dead = answers(&root, "dead", "exit 3");
    let got = say(&root, &dead, &["check"]);
    assert!(got.code == 2 && got.stderr.contains("codeid.py could not say"));
    let short = answers(&root, "short", "echo 1 2");
    assert_eq!(
        Repo::new(&root, &short).ask_counters(&[&(vec![1], vec![2])]),
        None
    );
}

#[test]
fn a_mode_change_alone_is_counter_only() {
    let (root, _, _, py) = work("mode", Some("integrated"));
    let before = git(&root, &["rev-parse", "HEAD"]);
    git(&root, &["config", "core.fileMode", "true"]);
    git(&root, &["update-index", "--chmod=+x", "l7r/diagram/m.py"]);
    git(&root, &["commit", "-qm", "mode"]);
    assert!(Repo::new(&root, &py).counter_only(&before, "HEAD"));
}
