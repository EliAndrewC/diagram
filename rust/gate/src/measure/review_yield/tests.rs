//! Each review check's yield, from the ledger's measured rows.

use serde_json::Value;

use super::{cli, has_finding, outcome, render, rows, table};

const LEDGER: &str = "
| date | check | subject | verdict | finding | class | missed | acted on | wall | tokens |
|---|---|---|---|---|---|---|---|---|---|
| 2026-09-20 | glyph-check | 300 well | FINDINGS 1 | too old | judgment | yes | fixed | 60 s | 10k in / 1.0k out |
| 2026-10-01 | glyph-check | 310 well | FINDINGS 1 | the well reads as a pond | geometric | yes | applied | 1800 s | 100k in / 2.0k out |
| 2026-10-01 | glyph-check | 311 byre | FINDINGS 1 | a shade too dark | judgment | no | verified (it is the convention) | 1800 s | 100k in / 3.0k out |
| 2026-10-02 | glyph-check | 311 byre | FINDINGS 1 | a size question | judgment | yes | put to the GM | 1800 s | 100k in / 1.0k out |
| 2026-10-02 | spec-fidelity | feature 312 spec | FAITHFUL | - | nothing | no | verified | 600 s | 50k in / 4.0k out |
| 2026-10-03 | spec-fidelity | feature 312 plan | BLOCKED 1 | a decision unrecorded | judgment | yes | re-dispatched | 600 s | 50k in / 4.0k out |
| 2026-10-03 | quote-check | 0021 | PASS | - | nothing | no | - | ? | ? |
| 2026-10-04 | a short row | 9 cells | x | x | x | x | x | 1 s |
";

fn check<'a>(t: &'a [(String, Value)], name: &str) -> &'a Value {
    &t.iter().find(|(k, _)| k == name).unwrap().1
}

#[test]
fn each_column_is_counted_from_its_cells() {
    let rs = rows(LEDGER, "2026-09-26");
    assert_eq!(rs.len(), 5);
    let t = table(&rs);
    let g = check(&t, "glyph-check");
    assert_eq!(
        (
            g["passes"].as_i64(),
            g["with a finding"].as_i64(),
            g["acted on"].as_i64(),
            g["dismissed"].as_i64(),
            g["deferred"].as_i64(),
            g["author missed"].as_i64()
        ),
        (Some(3), Some(3), Some(1), Some(1), Some(1), Some(2))
    );
    assert!(
        g["hours"] == 1.5
            && g["k tokens out"] == 6.0
            && g["features"] == 2
            && g["acted on per hour"] == 0.7
    );
    let s = check(&t, "spec-fidelity");
    assert!(
        s["with a finding"] == 1
            && s["acted on"] == 0
            && s["not acted on"] == 1
            && s["features"] == 1
    );
    let out = render(&t, "2026-09-26", rs.len());
    assert!(out.find("| glyph-check |") < out.find("| spec-fidelity |"));
    assert!(!has_finding(
        &vec![String::new(); 5]
            .into_iter()
            .chain(["x".to_owned()])
            .collect::<Vec<_>>()
    ));
}

#[test]
fn each_kind_of_acted_on_cell_is_read() {
    let cases = [
        ("applied", "acted on"),
        ("fixed (the EDIT applied)", "acted on"),
        ("index recorded; round 2", "acted on"),
        ("filed as rows", "acted on"),
        ("to the follow-up", "acted on"),
        ("not applied: carried in specs/335/briefs", "acted on"),
        ("nothing", "dismissed"),
        ("nothing for the GM", "dismissed"),
        ("answered in feature 328", "dismissed"),
        ("left: the reason is the GM's allowance", "dismissed"),
        ("verified", "dismissed"),
        ("spec accepted", "dismissed"),
        ("none", "dismissed"),
        ("accepted (the drift already on the report)", "dismissed"),
        ("plan accepted", "dismissed"),
        ("declined: contradicts FR-015", "dismissed"),
        ("no change", "dismissed"),
        ("no-change", "dismissed"),
        ("put to the GM", "deferred"),
        ("left for the next session", "deferred"),
        ("not applied: needs a new passage", "deferred"),
        ("-", "not acted on"),
        ("re-dispatched; engine frozen", "not acted on"),
    ];
    for (cell, want) in cases {
        assert_eq!(outcome(cell), want, "{cell}");
    }
}

#[test]
fn the_table_is_recorded_and_needs_its_key() {
    let dir = crate::checks::scratch("review-yield");
    let (ledger, m) = (dir.join("ledger.md"), dir.join("m.json"));
    std::fs::write(&ledger, LEDGER).unwrap();
    std::fs::write(&m, "{\"k\": {\"note\": 1}}").unwrap();
    let args = |extra: &[&str]| -> Vec<String> {
        [
            "--ledger",
            ledger.to_str().unwrap(),
            "--record",
            m.to_str().unwrap(),
        ]
        .iter()
        .chain(extra)
        .map(|s| (*s).to_owned())
        .collect()
    };
    assert_eq!(cli(&args(&["--key", "k"]), &dir).code, 0);
    let back: Value = serde_json::from_str(&std::fs::read_to_string(&m).unwrap()).unwrap();
    assert!(back["k"]["value"]["by check"]["glyph-check"]["passes"] == 3 && back["k"]["note"] == 1);
    assert_eq!(cli(&args(&["--key", "new"]), &dir).code, 0);
    assert_eq!(cli(&args(&[]), &dir).code, 2);
    assert!(cli(&[], &dir)
        .stdout
        .contains("review yield since 2026-09-26: 0 measured rows"));
}

#[test]
fn a_check_with_no_hours_acts_at_no_rate() {
    let t = table(&rows(
        "| 2026-10-05 | q | s | v | f | c | no | applied | 0 s | t |\n",
        "2026-09-26",
    ));
    assert_eq!(check(&t, "q")["acted on per hour"], 0.0);
}
