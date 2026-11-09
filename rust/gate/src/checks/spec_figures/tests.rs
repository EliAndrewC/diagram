//! Check 5: a measured figure is derived, not typed.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::scratch;
use super::{appears, check_measured_figures, figure_source, is_check5, recorded_numbers, FIGURE};

fn entries() -> Value {
    json!({
        "spawn": {"value": 144, "unit": "ms", "varies": true, "quantity": "560 commands", "command": "x"},
        "window": {"value": 1034, "unit": "commands", "command": "x"},
        "in-process": {"value": 7.0, "unit": "ms", "varies": true, "quantity": "560 commands", "command": "x"},
    })
}

fn measured(spec: &str, recorded: &Value, research: Option<&str>, number: u32) -> PathBuf {
    let dir = scratch("figures").join(format!("specs/{number}-a-feature"));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("spec.md"), spec).unwrap();
    std::fs::write(dir.join("tasks.md"), "- [ ] T01 the thing (FR-001)\n").unwrap();
    std::fs::write(dir.join("measurements.json"), recorded.to_string()).unwrap();
    if let Some(text) = research {
        std::fs::write(dir.join("research.md"), text).unwrap();
    }
    dir
}

fn check(spec: &str) -> Vec<String> {
    check_measured_figures(&measured(spec, &entries(), None, 239))
}

#[test]
fn a_figure_with_no_key_fails_and_the_keyed_form_matches_numerically() {
    assert!(
        check("## Summary\n\nIt costs 144 ms per command.\n")[0].contains("carries no `m:<key>`")
    );
    assert_eq!(check("## Summary\n\nIt costs 144 ms (`m:spawn`) against 7 ms (`m:in-process`) over 1,034 commands (`m:window`).\n"), Vec::<String>::new());
}

#[test]
fn a_key_whose_value_is_not_stated_and_an_unknown_key_fail() {
    assert!(check("## Summary\n\nIt costs 160 ms (`m:spawn`).\n")[0].contains("records 144"));
    assert!(check("## Summary\n\nIt costs 144 ms (`m:nowhere`).\n")[0]
        .contains("not in measurements.json"));
}

#[test]
fn it_reaches_research_and_the_review_history() {
    let got = check_measured_figures(&measured(
        "## Summary\n\nNothing measured.\n\n## Review history\n\nRound 1 saw 145 ms.\n",
        &entries(),
        Some("## R1\n\nIt took 81 s.\n"),
        239,
    ));
    assert!(
        got.iter().any(|x| x.contains("spec.md")) && got.iter().any(|x| x.contains("research.md"))
    );
    assert!(got[0].contains("or as a round's own run"));
}

#[test]
fn it_reaches_a_nested_functional_requirements_section_and_requirements_with_no_subsection() {
    for body in [
        "## Requirements\n\n### Functional Requirements\n\n**FR-001** It costs 144 ms.\n\n### Key Entities\n\nA 3 s thing.\n",
        "## Requirements\n\n- **FR-001** It costs 144 ms.\n\n### Key Entities\n\nA 3 s thing.\n",
    ] {
        let got = check(body);
        assert!(got.len() == 1 && got[0].contains("144 ms"), "{got:?}");
    }
}

#[test]
fn a_round_label_passes_in_the_review_history_only() {
    assert_eq!(
        check("## Review history\n\nIt measured 145 ms on round 2's own run.\n"),
        Vec::<String>::new()
    );
    assert_eq!(
        check("## Summary\n\nIt measured 145 ms on round 2's own run.\n").len(),
        1
    );
}

#[test]
fn a_backtick_span_names_a_figure_and_a_heading_names_a_section() {
    assert_eq!(
        check("## Summary\n\nThe old claim was `2.2 s` and it was never measured.\n"),
        Vec::<String>::new()
    );
    assert_eq!(
        check("## Summary\n\nThis section narrates. The old claim was 2.2 s.\n").len(),
        1
    );
    assert_eq!(
        check("## Summary\n\n### Where 208 min went\n\nNothing else measured here.\n"),
        Vec::<String>::new()
    );
}

#[test]
fn a_labeled_one_shot_passes_and_its_label_may_open_a_sentence() {
    assert_eq!(check("## Summary\n\nThe container ran at 5 s per call (observed 2026-09-13; method: a stopwatch).\n"), Vec::<String>::new());
    assert_eq!(check("## Summary\n\nThe container ran at 5 s per call (Observed 2026-09-13; Method: a stopwatch).\n"), Vec::<String>::new());
    assert_eq!(
        check("## Summary\n\nThe container ran at 5 s per call.\n").len(),
        1
    );
}

#[test]
fn it_reaches_an_old_feature_a_draft_with_no_tasks_and_passes_the_number_claim() {
    let old = measured(
        "## Summary\n\nIt costs 144 ms per command.\n",
        &entries(),
        None,
        236,
    );
    assert_eq!(check_measured_figures(&old).len(), 1);
    std::fs::remove_file(old.join("tasks.md")).unwrap();
    assert_eq!(check_measured_figures(&old).len(), 1);
    let claimed = scratch("claimed");
    assert_eq!(check_measured_figures(&claimed), Vec::<String>::new());
}

#[test]
fn the_spec_template_does_not_trip_it() {
    let dir = scratch("template");
    let template =
        Path::new(env!("CARGO_MANIFEST_DIR")).join("../../.specify/templates/spec-template.md");
    std::fs::copy(template, dir.join("spec.md")).unwrap();
    assert_eq!(check_measured_figures(&dir), Vec::<String>::new());
}

#[test]
fn varies_on_a_count_and_a_timing_with_no_quantity_fail() {
    let recorded = json!({"n": {"value": 560, "unit": "commands", "varies": true}, "t": {"value": 144, "unit": "ms", "varies": true}, "still": {"varies": false}, "zero": {"varies": 0}, "blank": {"varies": ""}, "none": {"varies": []}, "empty": {"varies": {}}, "null": {"varies": null}});
    let got = check_measured_figures(&measured("## Summary\n\nNothing.\n", &recorded, None, 239));
    assert_eq!(got.len(), 3);
    assert!(got[0].contains("'commands' counts things"));
    assert!(got[1].contains("no `quantity`"));
    let truthy = json!({"a": {"varies": [1], "unit": "ms", "quantity": "x"}, "b": {"varies": {"k": 1}, "unit": "s", "quantity": "x"}, "c": {"varies": "yes", "unit": "h", "quantity": "x"}, "d": {"varies": 2, "unit": "x", "quantity": "x"}});
    assert_eq!(
        check_measured_figures(&measured("## Summary\n\nNothing.\n", &truthy, None, 239)),
        Vec::<String>::new()
    );
}

#[test]
fn invalid_json_is_named_and_a_message_set_aside_by_what_it_says() {
    let dir = measured("## Summary\n\nNothing.\n", &entries(), None, 239);
    std::fs::write(dir.join("measurements.json"), "{").unwrap();
    let got = check_measured_figures(&dir);
    assert!(got[0].contains("not valid JSON") && is_check5(&got[0]) && !is_check5("anything else"));
}

#[test]
fn a_figure_appears_in_a_table_valued_record() {
    let value = json!({"drawn box at 1 ft/px": {"before": [16, 6], "after": [20, 10]}, "note": "the footing", "flag": true});
    assert!(appears(&value, "the frame 20 x 10 ft on its footing"));
    assert!(!appears(&value, "a 2 ft margin"));
    assert!(appears(&json!(3.26), "about 3.3 acres"));
    assert!(!appears(&json!("n/a"), "3 ft"));
    assert_eq!(recorded_numbers(&json!("1,034")), [1034.0]);
}

#[test]
fn a_size_in_gigabytes_is_a_figure_and_a_superscript_ends_none() {
    assert!(FIGURE.is_match("transcripts total 2.5 GB").unwrap());
    assert!(!FIGURE.is_match("a basin of 2,179 px\u{b2} here").unwrap());
    assert!(figure_source().contains("(?:minutes|"));
}
