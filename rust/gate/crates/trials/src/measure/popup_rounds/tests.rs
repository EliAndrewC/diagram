//! Each number the count gives, and every way of asking for it.

use serde_json::{json, Value};

use super::{cli, counts, two_places};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn dispatches() -> Value {
    json!({
        "a": {"check": "modal-form", "t": 10.0, "subjects": ["p1", "p2"]},
        "b": {"check": "modal-form", "t": 20.0, "subjects": ["p1"]},
        "c": {"check": "modal-form", "t": 30.0, "subjects": ["p1"]},
        "d": {"check": "modal-depiction", "t": 40.0, "subjects": ["p1"]},
        "e": {"check": "impl-drift", "t": 50.0, "subjects": ["p9"]},
        "f": {"check": "modal-research", "t": 60.0}
    })
}

fn refs(d: &Value) -> Vec<&Value> {
    d.as_object().unwrap().values().collect()
}

#[test]
fn a_unit_is_a_popup_and_a_check_and_its_rounds_are_its_dispatches() {
    let d = dispatches();
    let c = counts(&refs(&d), 0.0);
    assert_eq!(c["units"], 3);
    assert_eq!(c["dispatches"], 5);
    assert_eq!(c["per unit"], 1.67);
    assert_eq!(c["units with a 2nd round"], 1);
    assert_eq!(c["units with a 3rd"], 1);
    assert_eq!(c["pop-ups"], 2);
    assert_eq!(
        c["by check"]
            .as_object()
            .unwrap()
            .keys()
            .collect::<Vec<_>>(),
        ["modal-form", "modal-depiction"]
    );
    assert_eq!(c["by check"]["modal-form"]["dispatches"], 4);
}

#[test]
fn since_counts_only_what_came_after() {
    let d = dispatches();
    assert_eq!(counts(&refs(&d), 35.0)["dispatches"], 1);
    assert_eq!(counts(&[], 0.0)["per unit"], 0.0);
}

#[test]
fn a_tie_rounds_as_python_rounds() {
    assert!((two_places(1.125) - 1.12).abs() < f64::EPSILON);
    assert!((two_places(1.5) - 1.5).abs() < f64::EPSILON);
}

fn clone(tag: &str) -> l7r_guard::shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    let done = std::process::Command::new("git")
        .arg("-C")
        .arg(&root)
        .args(["init", "-q"])
        .status()
        .unwrap();
    assert!(done.success());
    std::fs::write(
        root.join(".git/checks-open.json"),
        json!({"feature": "375-x", "dispatches": dispatches()}).to_string(),
    )
    .unwrap();
    root
}

#[test]
fn a_clone_is_reported_in_words_or_as_json() {
    let root = clone("popup-clone");
    let there = root.display().to_string();
    let got = cli(&words(&[&there]));
    assert_eq!(got.code, 0);
    assert_eq!(
        got.stdout,
        "popup-rounds: 375-x: 5 dispatches over 3 units (1.67 per unit), 1 with a second round, 1 with a third; 2 pop-ups\n  modal-form: 4 over 2 (2.0), 1 second, 1 third\n  modal-depiction: 1 over 1 (1.0), 0 second, 0 third\n"
    );
    let shown: Value = serde_json::from_str(
        &cli(&words(&[
            "--json",
            &there,
            "--since",
            "1970-01-01T00:00:30Z",
        ]))
        .stdout,
    )
    .unwrap();
    assert_eq!(shown["dispatches"], 2);
}

#[test]
fn a_clone_with_no_state_counts_nothing() {
    let root = crate::checks::scratch("popup-empty");
    let got = cli(&words(&[&root.display().to_string()]));
    assert!(
        got.stdout.starts_with("popup-rounds: ?: 0 dispatches"),
        "{}",
        got.stdout
    );
}

#[test]
fn a_snapshot_is_recorded_under_its_label() {
    let root = crate::checks::scratch("popup-record");
    let (m, snap) = (root.join("m.json"), root.join("s.json"));
    std::fs::write(&m, "{\"k\": {\"other\": 1}}\n").unwrap();
    std::fs::write(&snap, json!({"dispatches": dispatches()}).to_string()).unwrap();
    let (mf, label) = (m.display().to_string(), format!("374={}", snap.display()));
    assert_eq!(
        cli(&words(&["--record", &mf, "--key", "k", &label])).code,
        0
    );
    let got: Value = serde_json::from_str(&std::fs::read_to_string(&m).unwrap()).unwrap();
    assert_eq!(got["k"]["other"], 1);
    assert_eq!(got["k"]["value"]["374"]["dispatches"], 5);
    let gone = format!("374={}", root.join("none").display());
    assert_eq!(cli(&words(&["--record", &mf, "--key", "k", &gone])).code, 1);
    std::fs::write(root.join("bad"), "{").unwrap();
    let bad = format!("374={}", root.join("bad").display());
    assert_eq!(cli(&words(&["--record", &mf, "--key", "k", &bad])).code, 1);
}

#[test]
fn a_malformed_request_is_refused() {
    assert_eq!(cli(&[]).code, 2);
    assert_eq!(cli(&words(&["a", "b"])).code, 2);
    assert_eq!(cli(&words(&["--record", "m", "a=b"])).code, 2);
    assert_eq!(
        cli(&words(&["--record", "m", "--key", "k", "nolabel"])).code,
        2
    );
    assert_eq!(cli(&words(&["--record", "m", "--key", "k"])).code, 2);
    let got = cli(&words(&["x", "--since", "soon"]));
    assert_eq!(got.code, 1);
    assert_eq!(got.stdout, "");
    assert_eq!(got.stderr.lines().count(), 1);
    assert!(got.stderr.contains("soon"));
    assert!(got.stderr.contains("not an ISO time"));
}
