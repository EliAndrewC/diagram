//! The carry record, the switch, the known drifts and the push's verdict at `report` and at `clean`.

use std::path::Path;

use serde_json::{json, Value};

use super::{
    carry, claims_mode, file_into, key_of, new_box, open_ids, recorded_known, rows, spec_glob,
    target, touches_engine,
};
use crate::claims::tests::{claims, commit_as_origin, fixture};
use crate::record::testkit::{git, put};

fn feature(root: &Path) {
    put(root, "specs/405-claims/tasks.md", "# Tasks\n\n- [ ] T01 fix `reach` [lands-open]\n- [x] T02 done\n- [ ] T03 open one\n\n- [ ] GM review (make gm-reviewed F=405) [lands-open]\n");
    put(
        root,
        "specs/405-claims/arbiter.jsonl",
        "{\"trigger\": \"ask:x\"}\nnot json\n",
    );
    put(root, "specs/406-other/tasks.md", "- [x] T01 done\n");
    put(
        root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/406-other\"}",
    );
}

fn index_set(root: &Path, key: &str, row: Value) {
    let p = root.join("dev/claims-index.json");
    let mut ix: Value = serde_json::from_str(&std::fs::read_to_string(&p).unwrap()).unwrap();
    ix[key] = row;
    std::fs::write(p, ix.to_string()).unwrap();
}

#[test]
fn the_switch_and_the_record() {
    let root = fixture("claims-carry-switch");
    assert_eq!(claims_mode(&root), "report");
    for (text, mode) in [
        ("{", "clean"),
        ("[]", "clean"),
        ("{}", "report"),
        ("{\"claims\": {}}", "report"),
        ("{\"claims\": 3}", "clean"),
        ("{\"claims\": {\"state\": \"clean\"}}", "clean"),
        ("{\"claims\": {\"state\": \"odd\"}}", "clean"),
        ("{\"claims\": {\"state\": \"report\"}}", "report"),
    ] {
        put(&root, "dev/switches.json", text);
        assert_eq!(claims_mode(&root), mode, "{text}");
    }
    feature(&root);
    let d = root.join("specs/405-claims");
    assert_eq!(open_ids(&d).unwrap().len(), 2);
    assert!(rows(&d).unwrap().is_empty());
    put(
        &root,
        "specs/405-claims/claims-carried.jsonl",
        "{\"task\": \"T01\", \"keys\": [\"k\"]}\n\n",
    );
    assert_eq!(rows(&d).unwrap().len(), 1);
    put(&root, "specs/405-claims/claims-carried.jsonl", "{");
    assert!(rows(&d).is_err());
    let text = std::fs::read_to_string(d.join("tasks.md")).unwrap();
    assert!(file_into(&text, "T01", &["a".into()], "me")
        .unwrap()
        .contains("- [ ] T01 fix `reach`; carried by me: a [lands-open]"));
    assert!(file_into(&text, "T03", &["a".into()], "me")
        .unwrap()
        .contains("- [ ] T03 open one; carried by me: a\n"));
    assert!(file_into(&text, "T02", &["a".into()], "me")
        .unwrap_err()
        .contains("T02 is ticked"));
    assert_eq!(
        file_into(&text, "T09", &["a".into()], "me").unwrap_err(),
        "no task T09 in tasks.md"
    );
    let (boxed, task) = new_box(&text, "", &["a".into(), "b".into()], "");
    assert_eq!(task, "T04");
    assert!(boxed.contains("- [ ] T04 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: a, b [lands-open]\n      research: rendering\n- [ ] GM review"));
    // an id archived in tasks-done.md is taken (feature 449 T142)
    assert_eq!(
        new_box(&text, "# h\n\n- [x] T11 x\n", &["a".into()], "").1,
        "T12"
    );
    let (boxed, task) = new_box("- [ ] T7 x", "", &["a".into()], "ask:r");
    assert_eq!((task.as_str(), boxed.ends_with("findings it carried - fix the code or the claim and re-check each: a [lands-open]\n      research: rendering\n")), ("T08", true));
    assert_eq!(key_of("DRIFTED        a::b#c - note - more"), "a::b#c");
    assert_eq!(key_of("DRIFTED        a::b#c -"), "a::b#c -");
    assert_eq!(spec_glob(&root, "405", None), vec![d.clone()]);
    assert!(spec_glob(&root, "407", Some("tasks.md")).is_empty());
    assert!(recorded_known(&root).unwrap().is_empty());
}

/// The carry's tree: the claims feature and the active one committed as `origin/main` (feature 449 T167 split the test of where a carry is
/// filed, over FR-008's tenth of a second, into three, each on a tree of its own).
fn filing(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = fixture(tag);
    feature(&root);
    commit_as_origin(&root, "features");
    root
}

/// [`filing`] with the switch at `clean`.
fn filing_clean(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = filing(tag);
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    root
}

#[test]
fn a_carry_is_filed_only_where_the_switch_and_the_delta_allow() {
    let root = filing("claims-carry-file");
    assert!(carry(&root, &target, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("the claims switch is at report"));
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    assert!(!touches_engine(&root).unwrap());
    assert!(carry(&root, &target, "405", "", &["k".into()], "ask:none")
        .unwrap_err()
        .contains("RULING=ask:none is no trigger in 405-claims/arbiter.jsonl"));
    assert_eq!(
        carry(&root, &target, "405", "", &[], "ask:x").unwrap(),
        "claims-carry: no carried finding is unfiled"
    );
    assert!(carry(&root, &target, "405", "T03", &["k".into()], "ask:x")
        .unwrap()
        .contains("1 finding(s) filed into 405-claims T03"));
    let text = std::fs::read_to_string(root.join("specs/405-claims/tasks.md")).unwrap();
    assert!(text.contains("T03 open one; carried by the round arbiter's ruling ask:x: k"));
    assert!(
        std::fs::read_to_string(root.join("specs/405-claims/claims-carried.jsonl"))
            .unwrap()
            .contains("\"ruling\": \"ask:x\"")
    );
    // a task archived in tasks-done.md is ticked, and its id is taken (feature 449 T142)
    put(
        &root,
        "specs/405-claims/tasks-done.md",
        "- [x] T04 archived\n",
    );
    assert!(carry(&root, &target, "405", "T04", &["k".into()], "ask:x")
        .unwrap_err()
        .contains("T04 is ticked"));
    assert!(carry(&root, &target, "405", "", &["k2".into()], "")
        .unwrap()
        .contains("filed into 405-claims T05"));
    std::fs::remove_file(root.join("specs/405-claims/tasks-done.md")).unwrap();
    let text = std::fs::read_to_string(root.join("specs/405-claims/tasks.md")).unwrap();
    std::fs::write(
        root.join("specs/405-claims/tasks.md"),
        text.replace("- [ ] T05 ", "- [ ] T04 "),
    )
    .unwrap();
    assert!(carry(&root, &target, "406", "", &["k3".into()], "")
        .unwrap()
        .contains("filed into 405-claims T05"));
    assert!(carry(&root, &target, "999", "", &["k".into()], "").unwrap_err().contains("filed only into the claims feature's - this delta holds no engine code (405-claims), not 999"));
}

#[test]
fn a_delta_with_engine_code_files_into_the_active_feature() {
    let root = filing_clean("claims-carry-engine");
    put(&root, "rust/phases/src/new.rs", "pub fn x() {}\n");
    assert!(touches_engine(&root).unwrap());
    assert!(carry(&root, &target, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("filed only into the active task's (406-other), not 405"));
    put(&root, "specs/406-other/tasks.md", "- [ ] T01 open\n");
    assert!(carry(&root, &target, "406", "", &["k".into()], "")
        .unwrap()
        .contains("filed into 406-other T02"));
}

#[test]
fn a_python_change_is_engine_code_only_where_its_code_id_moves() {
    let root = filing_clean("claims-carry-python");
    put(&root, "l7r/diagram/m.py", "GAP = 12  # a comment\n");
    assert!(!touches_engine(&root).unwrap());
    put(&root, "l7r/diagram/m.py", "GAP = 13\n");
    put(
        &root,
        "scripts/gates/codeid.py",
        "import sys\nsys.exit(1)\n",
    );
    assert!(touches_engine(&root).is_err());
    put(&root, "scripts/gates/codeid.py", "import hashlib, sys\nfor p in sys.argv[2:]:\n    print(hashlib.sha256(open(p, 'rb').read()).hexdigest())\n");
    assert!(touches_engine(&root).unwrap());
    put(&root, "l7r/diagram/added.py", "x = 1\n");
    put(&root, "l7r/diagram/m.py", "GAP = 12\n");
    assert!(touches_engine(&root).unwrap());
    put(&root, ".specify/feature.json", "{}");
    std::fs::remove_file(root.join("l7r/diagram/added.py")).unwrap();
    put(&root, "rust/phases/src/new.rs", "pub fn x() {}\n");
    assert!(carry(&root, &target, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("(none: `make task-start F=<n> T=<Txx>` first), not 405"));
}

// THE PUSH'S TEST IN PARTS (feature 449 T167): one test read the push through every step, gate after gate on one tree, near four tenths
// of a second against FR-008's one; each part below builds the tree its steps read - the claims recorded on `origin/main` and `reach`
// renamed for its task, the two findings recorded, the switch thrown, the GM's queue and box written - and asks its own steps of it.
// The tree has no Python module: its Python half answered nothing, and its start cost 16 ms a part.

const REACH: &str = "rust/phases/src/lib.rs::reach#reach";
const GAP: &str = "rust/phases/src/lib.rs::GAP#gap";
/// The GM's queue row `make claims-known` writes for `reach`, its `utc` a fixed one.
const KNOWN_ROW: &str = "{\"kind\": \"known-drift\", \"claim\": \"rust/phases/src/lib.rs::reach#reach\", \"task\": \"T01\", \"finding\": \"DRIFTED        rust/phases/src/lib.rs::reach#reach - departs; fix: code\", \"utc\": \"2026-11-17T00:00:00Z\"}\n";
/// The claims feature's tasks as `make claims-known` leaves them: the GM's box added.
const KNOWN_TASKS: &str = "# Tasks\n\n- [ ] T01 fix `reach` [lands-open]\n- [x] T02 done\n- [ ] T03 open one\n- [ ] GM review (make gm-reviewed F=405) [lands-open]\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n";

/// Every claim recorded on `origin/main`, then `reach` named for the claims feature's T01 in a commit of its own.
fn pushed(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = crate::claims::tests::fixture_rust_only(tag);
    feature(&root);
    // the recording written as `record_all` writes it, pinned by `the_recorded_rust_units_are_what_record_all_writes`: a bundle and a
    // record through the Python half, half of each carry test's time against FR-008's tenth of a second (feature 449 T167)
    crate::claims::tests::write_recorded(&root, "{}", "{}");
    commit_as_origin(&root, "recorded");
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("within GAP", "within GAP (feature 405 T01)"),
    )
    .unwrap();
    git(&root, &["commit", "-qam", "named its task"]);
    root
}

/// [`pushed`] with `reach` checked DRIFTED and `GAP` recorded a DRIFTED finding outside the change.
fn drifted(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = pushed(tag);
    let o = root.join("b").to_string_lossy().into_owned();
    claims(&root, &["bundle", "--units", REACH, "--out", &o]);
    let r = root.join("r.txt");
    std::fs::write(&r, format!("VERDICT {REACH} DRIFTED - departs; fix: code [§]\nVERDICT {GAP} DRIFTED - [outside the change] a carry; fix: code [§]\n")).unwrap();
    claims(
        &root,
        &["record", "--bundle", &o, "--reply", &r.to_string_lossy()],
    );
    let ix: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
            .unwrap();
    let mut row = ix[GAP].clone();
    row["verdict"] = json!("DRIFTED");
    row["outside"] = json!(true);
    row["note"] = json!("a carry");
    index_set(&root, GAP, row);
    root
}

/// [`drifted`] with the switch at `clean`.
fn at_clean(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = drifted(tag);
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    root
}

/// [`at_clean`] with the known drift recorded for the GM, as `make claims-known` records it.
fn known_recorded(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = at_clean(tag);
    put(&root, "specs/405-claims/tasks.md", KNOWN_TASKS);
    put(&root, "specs/405-claims/gm-review.jsonl", KNOWN_ROW);
    root
}

#[test]
fn the_push_reads_carries_known_drifts_and_open_findings() {
    let root = pushed("claims-carry-gate");
    let got = claims(&root, &["gate"]);
    assert_eq!(got.code, 1);
    assert!(got
        .stdout
        .contains("claims-gate: REFUSED owed (code changed): rust/phases/src/lib.rs::reach#reach"),);
}

#[test]
fn a_drift_the_change_names_is_known_and_one_outside_it_a_carry() {
    let root = drifted("claims-carry-gate-drifted");
    let got = claims(&root, &["gate"]);
    assert_eq!(got.code, 0, "{}", got.stdout);
    assert!(got.stdout.contains("claims-gate: carry: DRIFTED        rust/phases/src/lib.rs::GAP#gap - a carry - a finding on code the change left unchanged: file it with `make claims-carry F=406`"), "{}", got.stdout);
    assert!(got.stdout.contains("claims-gate: known: DRIFTED        rust/phases/src/lib.rs::reach#reach - departs; fix: code - a known drift (405 T01) to record for the GM"), "{}", got.stdout);
}

#[test]
fn at_report_a_known_drift_is_not_recorded_for_the_gm() {
    let root = drifted("claims-carry-gate-report");
    let got = claims(&root, &["known"]);
    assert_eq!(got.stdout, "claims-known: no known drift is unrecorded\n");
}

#[test]
fn at_clean_a_known_drift_unrecorded_is_refused() {
    let root = at_clean("claims-carry-gate-clean");
    let got = claims(&root, &["gate"]);
    assert!(got.stdout.contains("claims-gate: REFUSED known: DRIFTED        rust/phases/src/lib.rs::reach#reach - departs; fix: code - a known drift (405 T01) to record for the GM"), "{}", got.stdout);
}

#[test]
fn at_clean_the_known_drift_is_recorded_for_the_gm() {
    let root = at_clean("claims-carry-gate-known");
    // the GM-review queue's one writer, in process (feature 449 T91): the row and the GM's box, the bytes HEAD's `gm_review.add_row`
    // wrote for this row and these tasks (the differential's `scratchpad/t91/diff2.py`, its `utc` aside)
    let tasks =
        "# Tasks\n\n- [ ] T01 fix `reach` [lands-open]\n- [x] T02 done\n- [ ] T03 open one\n\n\n";
    put(&root, "specs/405-claims/tasks.md", tasks);
    let got = claims(&root, &["known"]);
    assert_eq!(
        got.stdout,
        "claims-known: recorded 405-claims T01: rust/phases/src/lib.rs::reach#reach\n",
    );
    assert!(recorded_known(&root).unwrap().contains(REACH));
    let written = std::fs::read_to_string(root.join("specs/405-claims/gm-review.jsonl")).unwrap();
    let utc = written.rsplit("\"utc\": \"").next().unwrap();
    assert_eq!(
        written.replace(utc, "<utc>\"}\n"),
        "{\"kind\": \"known-drift\", \"claim\": \"rust/phases/src/lib.rs::reach#reach\", \"task\": \"T01\", \"finding\": \"DRIFTED        rust/phases/src/lib.rs::reach#reach - departs; fix: code\", \"utc\": \"<utc>\"}\n"
    );
    assert_eq!(
        std::fs::read_to_string(root.join("specs/405-claims/tasks.md")).unwrap(),
        KNOWN_TASKS
    );
}

#[test]
fn an_unwritable_queue_fails_the_known() {
    let root = known_recorded("claims-carry-gate-queue");
    // the queue unwritable (a link to a directory that is not there, which the reading of the recorded drifts passes over): the command
    // fails, as the Python's raise through the runner did
    let q = root.join("specs/405-claims/gm-review.jsonl");
    std::fs::remove_file(&q).unwrap();
    std::os::unix::fs::symlink(root.join("no-such-dir/gm-review.jsonl"), &q).unwrap();
    let got = claims(&root, &["known"]);
    let said = format!("{}{}", got.stdout, got.stderr);
    let failed = got.code != 0 && said.contains("gm-review: OSError");
    assert!(failed, "{said}");
}

#[test]
fn a_known_drift_recorded_is_pre_existing() {
    let root = known_recorded("claims-carry-gate-pre");
    let got = claims(&root, &["gate"]);
    assert!(got
        .stdout
        .contains("claims-gate: pre-existing: known drift (405 T01): DRIFTED"),);
}

#[test]
fn a_carry_is_filed_into_the_active_feature_only() {
    let root = known_recorded("claims-carry-gate-carry");
    let got = claims(&root, &["carry", "--feature", "405"]);
    assert!(got
        .stderr
        .contains("filed only into the active task's (406-other), not 405"),);
}

/// The active feature with a task three and the round arbiter's trigger.
fn active(root: &Path) {
    put(
        root,
        "specs/406-other/tasks.md",
        "- [ ] T01 open\n- [ ] T03 three\n",
    );
    put(
        root,
        "specs/406-other/arbiter.jsonl",
        "{\"trigger\": \"ask:x\"}\n",
    );
}

#[test]
fn a_carry_files_the_finding_outside_the_change_into_a_task_of_its_own() {
    let root = known_recorded("claims-carry-gate-filed");
    active(&root);
    let got = claims(&root, &["carry", "--feature", "406"]);
    assert!(got.stdout.contains("1 finding(s) filed into 406-other T04"),);
    // the bytes the next test starts from, written by the carry itself
    assert_eq!(
        std::fs::read_to_string(root.join("specs/406-other/tasks.md")).unwrap(),
        CARRIED_TASKS
    );
    let rows = std::fs::read_to_string(root.join("specs/406-other/claims-carried.jsonl")).unwrap();
    assert!(rows.starts_with(&CARRIED_ROW[..CARRIED_ROW.find("\"utc\"").unwrap()]));
}

/// The active feature's tasks and carried row as the carry above writes them, its `utc` a fixed one.
const CARRIED_TASKS: &str = "- [ ] T01 open\n- [ ] T03 three\n- [ ] T04 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: rust/phases/src/lib.rs::GAP#gap [lands-open]\n      research: rendering\n";
const CARRIED_ROW: &str = "{\"task\": \"T04\", \"keys\": [\"rust/phases/src/lib.rs::GAP#gap\"], \"utc\": \"2026-11-17T00:00:00Z\"}\n";

#[test]
fn a_carried_finding_is_named_with_its_task_and_stays_open() {
    let root = known_recorded("claims-carry-gate-carried");
    active(&root);
    put(&root, "specs/406-other/tasks.md", CARRIED_TASKS);
    put(&root, "specs/406-other/claims-carried.jsonl", CARRIED_ROW);
    let got = claims(&root, &["gate"]);
    assert!(
        got.stdout
            .contains("claims-gate: carried (406-other T04): DRIFTED")
            && got
                .stdout
                .contains("REFUSED open (DRIFTED): rust/phases/src/lib.rs::GAP#gap - a carry"),
    );
}

/// A ruling's carry, and the recorded drifts read as the Python read them: the engine change in the working tree, nothing recorded -
/// the carry files the keys it is given (feature 449 T167: the push's last part, on a tree of its own).
#[test]
fn a_ruling_s_carry_needs_its_keys_and_the_recorded_drifts_read_as_python_read_them() {
    let root = filing_clean("claims-carry-ruling");
    put(
        &root,
        "specs/406-other/tasks.md",
        "- [ ] T01 open\n- [ ] T03 three\n",
    );
    put(
        &root,
        "specs/406-other/arbiter.jsonl",
        "{\"trigger\": \"ask:x\"}\n",
    );
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("within GAP", "within GAP (feature 405 T01)"),
    )
    .unwrap();
    let got = claims(&root, &["carry", "--feature", "406", "--keys", "a"]);
    assert_eq!((got.code, got.stderr.as_str()), (2, "claims-carry: KEYS= and RULING= go together: the findings a round-arbiter ruling carried, and that ruling's trigger\n"));
    let got = claims(
        &root,
        &[
            "carry",
            "--feature",
            "406",
            "--keys",
            "a; b",
            "--ruling",
            "ask:x",
            "--task",
            "T03",
        ],
    );
    assert!(got.stdout.contains("2 finding(s) filed into 406-other T03"),);
    put(
        &root,
        "specs/405-claims/gm-review.jsonl",
        "not json\n\n{\"kind\": \"known-drift\", \"claim\": 7}\n",
    );
    assert!(recorded_known(&root).unwrap().contains("7"));
    put(&root, "specs/405-claims/gm-review.jsonl", "3\n");
    assert!(recorded_known(&root)
        .unwrap_err()
        .starts_with("AttributeError"));
}
