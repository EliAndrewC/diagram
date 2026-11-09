//! A named, complete feature; the two rules asked of the Python are its stand-in's here.

use super::super::fixtures::{put, python, repo, scratch};
use super::{active_feature, feature_status, FeatureStatus};

#[test]
fn no_name_and_a_missing_directory_each_say_what_to_do() {
    let dir = scratch("none");
    assert!(FeatureStatus::default()
        .why()
        .contains("no spec-kit feature is named"));
    assert_eq!(feature_status(&dir, None, "x"), FeatureStatus::default());
    let missing = feature_status(&dir, Some("9-x"), "x");
    assert!(!missing.complete() && missing.why().contains("has no specs/9-x/"));
}

#[test]
fn the_environment_names_it_first_and_the_feature_json_after() {
    let dir = scratch("json");
    assert_eq!(active_feature(&dir, Some(" 9-x ")).as_deref(), Some("9-x"));
    assert_eq!(active_feature(&dir, Some(" ")), None);
    assert_eq!(active_feature(&dir, None), None);
    put(
        &dir,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/449-x/\"}",
    );
    assert_eq!(active_feature(&dir, None).as_deref(), Some("449-x"));
    put(&dir, ".specify/feature.json", "not json");
    assert_eq!(active_feature(&dir, None), None);
    put(&dir, ".specify/feature.json", "{}");
    assert_eq!(active_feature(&dir, None), None);
}

#[test]
fn only_the_held_box_counts_and_a_missing_verdict_is_named_beside_it() {
    let dir = repo("held");
    let py = python(&dir);
    put(&dir, "specs/9-x/tasks.md", "- [ ] T01 open and held\n- [ ] T02 open but nobody started it\n- [x] T03 done\n- [ ] not a task\n");
    put(
        &dir,
        "specs/9-x/.holding",
        "T01 open and held (land it with make land F=9 T=T01)\n",
    );
    let st = feature_status(&dir, Some("9-x"), &py);
    assert!(st.exists && !st.faithful && !st.complete());
    assert_eq!(st.open_tasks, ["T01 open and held"]);
    assert!(
        st.why().contains("no FAITHFUL verdict")
            && st.why().contains("1 open task(s) in tasks.md: T01")
    );
    put(&dir, "specs/9-x/.faithful", "");
    std::fs::remove_file(dir.join("specs/9-x/.holding")).unwrap();
    let done = feature_status(&dir, Some("9-x"), &py);
    assert!(done.complete() && done.why().contains("no task holds this landing"));
}

#[test]
fn a_long_list_is_cut_at_three_and_a_python_that_cannot_start_holds_nothing() {
    let many = FeatureStatus {
        name: Some("9-x".to_owned()),
        exists: true,
        faithful: true,
        open_tasks: vec![
            "a".to_owned(),
            "b".to_owned(),
            "c".to_owned(),
            "d".to_owned(),
        ],
    };
    assert!(many
        .why()
        .ends_with("4 open task(s) in tasks.md: a; b; c; +1 more"));
    let dir = repo("nopy");
    put(&dir, "specs/9-x/tasks.md", "- [ ] T01 x\n");
    assert_eq!(
        feature_status(&dir, Some("9-x"), "/no/such/python").open_tasks,
        Vec::<String>::new()
    );
}
