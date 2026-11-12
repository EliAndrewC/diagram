//! The carry record, the switch, the known drifts and the push's verdict at `report` and at `clean`.

use std::path::Path;

use serde_json::{json, Value};

use super::{
    carry, claims_mode, file_into, key_of, new_box, open_ids, recorded_known, rows, spec_glob,
    touches_engine,
};
use crate::claims::tests::{claims, fixture, py_units, record_all};
use crate::record::testkit::{commit, git, put};

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
    let (boxed, task) = new_box(&text, &["a".into(), "b".into()], "");
    assert_eq!(task, "T04");
    assert!(boxed.contains("- [ ] T04 Carried by the claims gate (385 FR-013): findings on code the change left unchanged - fix the code or the claim and re-check each: a, b [lands-open]\n      research: rendering\n- [ ] GM review"));
    let (boxed, task) = new_box("- [ ] T7 x", &["a".into()], "ask:r");
    assert_eq!((task.as_str(), boxed.ends_with("findings it carried - fix the code or the claim and re-check each: a [lands-open]\n      research: rendering\n")), ("T08", true));
    assert_eq!(key_of("DRIFTED        a::b#c - note - more"), "a::b#c");
    assert_eq!(key_of("DRIFTED        a::b#c -"), "a::b#c -");
    assert_eq!(spec_glob(&root, "405", None), vec![d.clone()]);
    assert!(spec_glob(&root, "407", Some("tasks.md")).is_empty());
    assert!(recorded_known(&root).unwrap().is_empty());
}

#[test]
fn a_carry_is_filed_only_where_the_switch_and_the_delta_allow() {
    let root = fixture("claims-carry-file");
    feature(&root);
    commit(&root, "features");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    assert!(carry(&root, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("the claims switch is at report"));
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    assert!(!touches_engine(&root).unwrap());
    assert!(carry(&root, "405", "", &["k".into()], "ask:none")
        .unwrap_err()
        .contains("RULING=ask:none is no trigger in 405-claims/arbiter.jsonl"));
    assert_eq!(
        carry(&root, "405", "", &[], "ask:x").unwrap(),
        "claims-carry: no carried finding is unfiled"
    );
    assert!(carry(&root, "405", "T03", &["k".into()], "ask:x")
        .unwrap()
        .contains("1 finding(s) filed into 405-claims T03"));
    let text = std::fs::read_to_string(root.join("specs/405-claims/tasks.md")).unwrap();
    assert!(text.contains("T03 open one; carried by the round arbiter's ruling ask:x: k"));
    assert!(
        std::fs::read_to_string(root.join("specs/405-claims/claims-carried.jsonl"))
            .unwrap()
            .contains("\"ruling\": \"ask:x\"")
    );
    assert!(carry(&root, "405", "", &["k2".into()], "")
        .unwrap()
        .contains("filed into 405-claims T04"));
    assert!(carry(&root, "406", "", &["k3".into()], "")
        .unwrap()
        .contains("filed into 405-claims T05"));
    assert!(carry(&root, "999", "", &["k".into()], "").unwrap_err().contains("filed only into the claims feature's - this delta holds no engine code (405-claims), not 999"));
    put(&root, "rust/phases/src/new.rs", "pub fn x() {}\n");
    assert!(touches_engine(&root).unwrap());
    assert!(carry(&root, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("filed only into the active task's (406-other), not 405"));
    put(&root, "specs/406-other/tasks.md", "- [ ] T01 open\n");
    assert!(carry(&root, "406", "", &["k".into()], "")
        .unwrap()
        .contains("filed into 406-other T02"));
    std::fs::remove_file(root.join("rust/phases/src/new.rs")).unwrap();
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
    assert!(carry(&root, "405", "", &["k".into()], "")
        .unwrap_err()
        .contains("(none: `make task-start F=<n> T=<Txx>` first), not 405"));
}

#[test]
fn the_push_reads_carries_known_drifts_and_open_findings() {
    let root = fixture("claims-carry-gate");
    feature(&root);
    py_units(&root, &[], &[]);
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("within GAP", "within GAP (feature 405 T01)"),
    )
    .unwrap();
    commit(&root, "named its task");
    let got = claims(&root, &["gate"]);
    assert_eq!(got.code, 1);
    assert!(got
        .stdout
        .contains("claims-gate: REFUSED owed (code changed): rust/phases/src/lib.rs::reach#reach"),);
    let reach = "rust/phases/src/lib.rs::reach#reach";
    let o = root.join("b").to_string_lossy().into_owned();
    claims(&root, &["bundle", "--units", reach, "--out", &o]);
    let r = root.join("r.txt");
    std::fs::write(&r, format!("VERDICT {reach} DRIFTED - departs [§]\nVERDICT rust/phases/src/lib.rs::GAP#gap DRIFTED - [outside the change] a carry [§]\n")).unwrap();
    claims(
        &root,
        &["record", "--bundle", &o, "--reply", &r.to_string_lossy()],
    );
    let gap = "rust/phases/src/lib.rs::GAP#gap";
    let ix: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("dev/claims-index.json")).unwrap())
            .unwrap();
    let mut row = ix[gap].clone();
    row["verdict"] = json!("DRIFTED");
    row["outside"] = json!(true);
    row["note"] = json!("a carry");
    index_set(&root, gap, row);
    let got = claims(&root, &["gate"]);
    assert_eq!(got.code, 0, "{}", got.stdout);
    assert!(got.stdout.contains("claims-gate: carry: DRIFTED        rust/phases/src/lib.rs::GAP#gap - a carry - a finding on code the change left unchanged: file it with `make claims-carry F=406`"), "{}", got.stdout);
    assert!(got.stdout.contains("claims-gate: known: DRIFTED        rust/phases/src/lib.rs::reach#reach - departs - a known drift (405 T01) to record for the GM"), "{}", got.stdout);
    let got = claims(&root, &["known"]);
    assert_eq!(got.stdout, "claims-known: no known drift is unrecorded\n");
    at_clean(&root, reach);
}

/// The same tree with the switch at `clean`: the known drift recorded, the carry filed, every open finding refused.
fn at_clean(root: &Path, reach: &str) {
    let root = root.to_path_buf();
    put(
        &root,
        "dev/switches.json",
        "{\"claims\": {\"state\": \"clean\"}}",
    );
    let got = claims(&root, &["gate"]);
    assert!(got.stdout.contains("claims-gate: REFUSED known: DRIFTED        rust/phases/src/lib.rs::reach#reach - departs - a known drift (405 T01) to record for the GM"), "{}", got.stdout);
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
    assert!(recorded_known(&root).unwrap().contains(reach));
    let written = std::fs::read_to_string(root.join("specs/405-claims/gm-review.jsonl")).unwrap();
    let utc = written.rsplit("\"utc\": \"").next().unwrap();
    assert_eq!(
        written.replace(utc, "<utc>\"}\n"),
        "{\"kind\": \"known-drift\", \"claim\": \"rust/phases/src/lib.rs::reach#reach\", \"task\": \"T01\", \"finding\": \"DRIFTED        rust/phases/src/lib.rs::reach#reach - departs\", \"utc\": \"<utc>\"}\n"
    );
    assert_eq!(
        std::fs::read_to_string(root.join("specs/405-claims/tasks.md")).unwrap(),
        "# Tasks\n\n- [ ] T01 fix `reach` [lands-open]\n- [x] T02 done\n- [ ] T03 open one\n- [ ] GM review (make gm-reviewed F=405) [lands-open]\n      research: rendering\n      verify: the GM reviewed every row (make gm-review lists them)\n"
    );
    // the queue unwritable (a link to a directory that is not there, which the reading of the recorded drifts passes over): the command
    // fails, as the Python's raise through the runner did
    let q = root.join("specs/405-claims/gm-review.jsonl");
    std::fs::remove_file(&q).unwrap();
    std::os::unix::fs::symlink(root.join("no-such-dir/gm-review.jsonl"), &q).unwrap();
    let got = claims(&root, &["known"]);
    let said = format!("{}{}", got.stdout, got.stderr);
    let failed = got.code != 0 && said.contains("gm-review: OSError");
    assert!(failed, "{said}");
    std::fs::remove_file(&q).unwrap();
    put(&root, "specs/405-claims/gm-review.jsonl", &written);
    let got = claims(&root, &["gate"]);
    assert!(got
        .stdout
        .contains("claims-gate: pre-existing: known drift (405 T01): DRIFTED"),);
    let got = claims(&root, &["carry", "--feature", "405"]);
    assert!(got
        .stderr
        .contains("filed only into the active task's (406-other), not 405"),);
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
    let got = claims(&root, &["carry", "--feature", "406"]);
    assert!(got.stdout.contains("1 finding(s) filed into 406-other T04"),);
    let got = claims(&root, &["gate"]);
    assert!(
        got.stdout
            .contains("claims-gate: carried (406-other T04): DRIFTED")
            && got
                .stdout
                .contains("REFUSED open (DRIFTED): rust/phases/src/lib.rs::GAP#gap - a carry"),
    );
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
