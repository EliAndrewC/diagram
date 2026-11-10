use serde_json::{json, Map, Value};

use super::refusal;
use crate::shared::checks::testkit::dir;

fn rulings(rows: &[(&str, &str, &str)]) -> Map<String, Value> {
    rows.iter()
        .map(|(t, r, u)| ((*t).to_owned(), json!({"ruling": r, "utc": u})))
        .collect()
}

const PROMPT: &str = "Read /tmp/l7r-check/work-budget-budget-field/MANIFEST.md";

#[test]
fn a_stages_rounds_are_its_verdicts() {
    let d = dir("budget");
    let none = Map::new();
    assert_eq!(refusal(Some(&d), &none, "no stage"), "");
    assert_eq!(refusal(None, &none, PROMPT), "");
    assert_eq!(refusal(Some(&d), &none, PROMPT), "");
    let phases = d.join("phases");
    std::fs::create_dir_all(&phases).unwrap();
    std::fs::write(phases.join("field.verdict-1.txt"), "v").unwrap();
    std::fs::write(phases.join("track.verdict-1.txt"), "v").unwrap();
    std::fs::write(phases.join("field.other.txt"), "v").unwrap();
    assert_eq!(refusal(Some(&d), &none, PROMPT), "");
    let after = "2099-01-01T00:00:00Z";
    let accepted = rulings(&[
        ("ask:444-field-round-3", "accept", after),
        ("ask:444-trackfield-round-3", "accept", after),
    ]);
    let msg = refusal(Some(&d), &accepted, PROMPT);
    assert!(msg.contains("accepted field's derivation (ask:444-field-round-3)"));
    std::fs::write(phases.join("field.verdict-2.txt"), "v").unwrap();
    let msg = refusal(Some(&d), &none, PROMPT);
    assert!(
        msg.contains("round 3 of work-budget on field passes its cap of 2")
            && msg.contains("field.verdict-2.txt")
    );
    let cont = rulings(&[("ask:444-field-round-2", "continue", after)]);
    assert_eq!(refusal(Some(&d), &cont, PROMPT), "");
    let old = rulings(&[("ask:444-field-round-2", "accept", "1999-01-01T00:00:00Z")]);
    assert!(refusal(Some(&d), &old, PROMPT).contains("passes its cap"));
    let many = rulings(&[
        ("ask:444-field-round-1", "continue", after),
        ("ask:444-field-round-2", "accept", "2098-01-01T00:00:00Z"),
    ]);
    assert_eq!(refusal(Some(&d), &many, PROMPT), "");
    let bad = rulings(&[("ask:444-field-round-2", "continue", "not a date")]);
    assert!(refusal(Some(&d), &bad, PROMPT).contains("passes its cap"));
}
