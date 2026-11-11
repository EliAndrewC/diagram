//! The glyph hour on scratch repositories: the active feature, its start and reopening, the landing mark, the batch.

use serde_json::{json, Value};

use super::super::tests::{commit, events, feature, map, put, repo, sh};
use super::*;

fn glyph_unit() -> Unit {
    Unit {
        check: "glyph-check".to_owned(),
        subject: "well".to_owned(),
        on: "m".to_owned(),
        occasion: "x".to_owned(),
    }
}

fn clock(root: &Path) -> Value {
    serde_json::from_str(&std::fs::read_to_string(root.join(".git").join(CLOCK)).unwrap()).unwrap()
}

#[test]
fn the_active_feature_is_the_open_one_the_pointer_names() {
    let r = repo("active");
    assert_eq!(active_feature(&r), "");
    feature(&r, "900-x", "- [ ] T1\n");
    assert_eq!(active_feature(&r), "900-x");
    let c = repo("closed");
    feature(&c, "901-y", "- [x] T1\n");
    put(&c, "specs/901-y/.state", "closed\n");
    assert_eq!(active_feature(&c), "");
    let n = repo("nospec");
    put(
        &n,
        ".specify/feature.json",
        r#"{"feature_directory": "specs/902-z"}"#,
    );
    assert_eq!(active_feature(&n), "");
}

#[test]
fn the_start_is_the_first_event_or_the_last_reopening() {
    let r = repo("start");
    assert_eq!(first_event(&r, "900-x"), None);
    assert_eq!(feature_start(&r, "900-x"), None);
    put(
        &r,
        ".git/l7r-events/900-x.jsonl",
        "{\"t\": \"1970-01-01T00:01:00Z\"}\n{\"t\": 5}\n",
    );
    assert_eq!(first_event(&r, "900-x"), Some(60.0));
    // no commit to specs/900-x
    // kept, keyed by the newest commit
    // the hour is up
    // due on the hour
    assert_eq!(last_reopening(&r, "900-x", 0.0), None);
    assert_eq!(feature_start(&r, "900-x"), Some(60.0));
    put(&r, ".git/l7r-events/900-y.jsonl", "not json\n");
    assert_eq!(first_event(&r, "900-y"), None);
    // open, then closed, then reopened: the reopening is the commit after which it is open again
    put(&r, "specs/900-x/tasks.md", "- [ ] T1\n");
    commit(&r, "filed");
    put(&r, "specs/900-x/tasks.md", "- [x] T1\n");
    commit(&r, "closed");
    put(&r, "specs/900-x/tasks.md", "- [x] T1\n- [ ] T2\n");
    sh(
        &r,
        "git add -A && GIT_COMMITTER_DATE='2030-01-01T00:00:00Z' git commit -q -m reopened",
    );
    put(&r, "specs/900-x/tasks.md", "- [x] T1\n- [ ] T2\n- [ ] T3\n");
    sh(
        &r,
        "git add -A && GIT_COMMITTER_DATE='2030-01-02T00:00:00Z' git commit -q -m worked",
    );
    put(
        &r,
        ".git/glyph-clock.json",
        r#"{"900-x": {"reopened": {"key": "an older commit", "at": 1}}}"#,
    );
    let at = last_reopening(&r, "900-x", 0.0);
    assert_eq!(at, Some(1_893_456_000.0));
    let kept = clock(&r);
    assert_eq!(kept["900-x"]["reopened"]["at"], json!(1_893_456_000.0));
    assert_eq!(last_reopening(&r, "900-x", 0.0), at);
    assert_eq!(feature_start(&r, "900-x"), Some(1_893_456_000.0));
    // the walk stops at a change older than the feature's first event
    std::fs::remove_file(r.join(".git").join(CLOCK)).unwrap();
    assert_eq!(last_reopening(&r, "900-x", 2.0e9), None);
    assert_eq!(clock(&r)["900-x"]["reopened"]["at"], Value::Null);
    // a clock entry that is not an object is replaced
    put(&r, ".git/glyph-clock.json", r#"{"900-x": 3}"#);
    let mut c = read_object(Some(&r.join(".git").join(CLOCK)));
    entry(&mut c, "900-x").insert("k".to_owned(), json!(1));
    assert_eq!(c["900-x"], json!({"k": 1}));
}

#[test]
fn the_landing_mark_names_its_feature() {
    let r = repo("landing");
    assert!(!landing(&r, ""));
    mark_landing(&r, true);
    assert!(landing(&r, ""));
    assert!(!landing(&r, "900-x"));
    let mark: Value =
        serde_json::from_str(&std::fs::read_to_string(r.join(".git/glyph-landing")).unwrap())
            .unwrap();
    assert_eq!(mark["feature"], json!(""));
    mark_landing(&r, false);
    assert!(!landing(&r, ""));
    let nowhere = super::super::tests::dir("nogit");
    assert!(!landing(&nowhere, ""));
    mark_landing(&nowhere, true);
    assert!(!nowhere.join(".git").exists());
}

#[test]
fn a_glyph_unit_is_due_on_the_hour_in_its_batch_or_at_landing() {
    let r = repo("due");
    let u = glyph_unit();
    let other = Unit {
        check: "settlement-review".to_owned(),
        ..glyph_unit()
    };
    assert_eq!(
        glyph_due(&r, std::slice::from_ref(&other), None),
        (Vec::new(), Vec::new())
    );
    // no feature: waits for the landing
    let (due, waiting) = glyph_due(&r, std::slice::from_ref(&u), None);
    assert!(due.is_empty() && waiting[0].1 == "at landing");
    mark_landing(&r, true);
    assert_eq!(
        glyph_due(&r, std::slice::from_ref(&u), None).0,
        vec![u.clone()]
    );
    mark_landing(&r, false);
    feature(&r, "900-x", "- [ ] T1\n");
    events(&r, "900-x", &[(600, "PreToolUse", false)]);
    let (due, waiting) = glyph_due(&r, std::slice::from_ref(&u), None);
    assert!(due.is_empty());
    assert!(waiting[0].1.starts_with("at ") && waiting[0].1.len() == 8);
    let t = now();
    assert_eq!(
        glyph_due(&r, std::slice::from_ref(&u), Some(t + 3600.0))
            .0
            .len(),
        1
    );
    // an open batch keeps its units due until dispatched
    put(
        &r,
        ".git/glyph-clock.json",
        &json!({"900-x": {"batch_at": int_of(t) - 60, "batch": [u.slug()]}}).to_string(),
    );
    assert_eq!(glyph_due(&r, std::slice::from_ref(&u), None).0.len(), 1);
    put(
        &r,
        ".git/pairing-state.json",
        &json!({"dispatched": {u.slug(): {"at": t}}}).to_string(),
    );
    assert!(glyph_due(&r, std::slice::from_ref(&u), None).0.is_empty());
}

#[test]
fn a_dispatch_on_the_hour_or_escaped_opens_a_batch() {
    let r = repo("batch");
    map(&r, "pool", "m", &["well"]);
    let slug = "glyph-check--well--m";
    assert_eq!(
        glyph_cli(&r, "glyph-check--nope", true, false),
        (0, String::new())
    );
    assert_eq!(
        glyph_cli(&r, "settlement-review--m", true, false),
        (0, String::new())
    );
    assert_eq!(glyph_cli(&r, slug, true, true), (0, String::new()));
    let (code, said) = glyph_cli(&r, slug, true, false);
    assert_eq!(code, 1);
    assert!(said.contains("due at landing"));
    // no feature: a dispatch opens nothing
    assert_eq!(glyph_cli(&r, slug, false, true), (0, String::new()));
    assert!(!r.join(".git").join(CLOCK).exists());
    feature(&r, "900-x", "- [ ] T1\n");
    events(&r, "900-x", &[(600, "PreToolUse", false)]);
    assert_eq!(glyph_cli(&r, slug, false, false), (0, String::new()));
    assert!(!r.join(".git").join(CLOCK).exists() || clock(&r)["900-x"].get("batch").is_none());
    assert_eq!(glyph_cli(&r, slug, false, true), (0, String::new()));
    assert_eq!(clock(&r)["900-x"]["batch"], json!([slug]));
    events(&r, "900-x", &[(7200, "PreToolUse", false)]);
    std::fs::remove_file(r.join(".git").join(CLOCK)).unwrap();
    assert_eq!(glyph_cli(&r, slug, true, false), (0, String::new()));
    assert_eq!(glyph_cli(&r, slug, false, false), (0, String::new()));
    assert_eq!(clock(&r)["900-x"]["batch"], json!([slug]));
    let nogit = super::super::tests::dir("nogit-batch");
    open_batch(&nogit, &[glyph_unit()], 1.0);
}
