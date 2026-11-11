//! The depiction replay over a scratch history of pop-up edits.

use serde_json::{json, Value};

use super::cli;
use crate::record::testkit::{commit, put, record, WELL};

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn edits_are_counted_under_both_rules_and_recorded() {
    let root = record("depiction-replay");
    put(&root, WELL, "Name: Well\nAbout: Changed about.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn round.\nDrawing: research/questions/0094-trade.drawing.html\n");
    commit(&root, "about only");
    put(&root, WELL, "Name: Well\nAbout: Changed about.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn square.\nDrawing: research/questions/0094-trade.drawing.html\n");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/hamlet/new.md",
        "Name: New\nAbout: x\n",
    );
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/hamlet/notes.txt",
        "x",
    );
    commit(&root, "depiction");
    put(&root, WELL, "Name: Well\nAbout: Changed about.\nEntry: research/questions/0094-trade.html\nDepiction: Drawn square.\nDrawing: research/questions/0094-trade.drawing.html\n\n");
    commit(&root, "no tag moved");
    let r = cli(&args(&["--since", "2000-01-01"]), &root);
    assert_eq!(r.code, 0);
    let got: Value = serde_json::from_str(&r.stdout).unwrap();
    assert_eq!(got["edits to existing pop-ups"], json!(2));
    assert_eq!(got["owed modal-depiction, amendment 1"], json!(2));
    assert_eq!(got["owed modal-depiction, amendment 6"], json!(1));
    assert_eq!(got["About-only edits (owed before, not now)"], json!(1));
    let rec = root.join("rec.json");
    std::fs::write(
        &rec,
        json!({"k": {"note": "kept"}, "x": "\u{e9}"}).to_string(),
    )
    .unwrap();
    let path = rec.to_string_lossy().into_owned();
    assert_eq!(cli(&args(&["--record", &path]), &root).code, 2);
    assert_eq!(
        cli(&args(&["--record", &path, "--key", "k"]), &root).code,
        0
    );
    assert_eq!(
        cli(&args(&["--record", &path, "--key", "fresh"]), &root).code,
        0
    );
    let saved: Value = serde_json::from_str(&std::fs::read_to_string(&rec).unwrap()).unwrap();
    assert!(
        saved["k"]["note"] == json!("kept")
            && saved["fresh"]["value"]["since"] == json!("2026-10-05")
    );
    assert_eq!(
        cli(&args(&["--record", &path, "--key", "x"]), &root).code,
        1
    );
    std::fs::write(&rec, "[]").unwrap();
    assert_eq!(
        cli(&args(&["--record", &path, "--key", "k"]), &root).code,
        1
    );
    assert_eq!(
        cli(&args(&["--record", "/no/such.json", "--key", "k"]), &root).code,
        1
    );
    assert_eq!(cli(&args(&["--bogus"]), &root).code, 2);
}
