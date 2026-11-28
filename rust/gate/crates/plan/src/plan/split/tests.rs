//! `plan split` over scratch features (462 T545, T555): a closed feature's finished sections moved, its review cut to the live entries
//! with the closed ones in parts and read back by task, its report cut; an open feature's unreviewed section left; a rerun moves nothing.

use std::fmt::Write as _;

use serde_json::{json, Value};

use super::super::tests::{current, feature_at, repo, run, write_json};
use l7r_shared::speckit::archive;

/// A plan with a general block, a section whose heading names example ids (451 T18's form) and a task's section with an unreviewed
/// part B.
const PLAN: &str = "# Plan\n\n## Summary\n\nsum\n\n### T05 (`T=\"T1,T2\"` read as one task)\n\nfive\n\n### T06 (the sixth)\n\nsix\n\n### T06 part B (2026-11-27T07:20Z)\n\nowed\n";

fn record() -> Value {
    json!({
        "feature": "451-x",
        "blocks": {
            "## Summary": {"sha256": "s", "verdict": "CLEAR"},
            "### T04 (gone)": {"sha256": "g", "verdict": "CLEAR"},
            "### T05 (`T=\"T1,T2\"` read as one task)": {"sha256": "f", "verdict": "CLEAR"},
            "## Old heading": {"sha256": "o", "verdict": "CLEAR"}
        },
        "tasks": {
            "T04": {"verdict": "CLEAR", "reviewed": "2026-11-20"},
            "T05": {"verdict": "CLEAR", "reviewed": "2026-11-21"},
            "T07": {"verdict": "CLEAR", "reviewed": "2026-11-22"}
        },
        "block_reviews": [
            {"blocks": ["## Summary", "### T04 (gone)"], "verdict": "CLEAR"},
            {"blocks": ["### T04 (gone)"], "tasks": ["T04", "T05"], "verdict": "BLOCKED"},
            {"blocks": ["## Old heading"], "verdict": "CLEAR"},
            {"verdict": "CLEAR"}
        ]
    })
}

fn read(dir: &std::path::Path, name: &str) -> String {
    std::fs::read_to_string(dir.join(name)).unwrap_or_default()
}

#[test]
fn a_closed_feature_s_split_moves_its_sections_and_cuts_its_review_and_report() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN), Some(&record()), "451-x");
    std::fs::write(
        dir.join("tasks.md"),
        "# tasks\n\n- [x] T04 four\n- [x] T05 five\n- [x] T06 six\n- [x] T07 seven\n",
    )
    .unwrap();
    let mut report = String::from(
        "# Feature report - 451-x\n\n## Small\n\n- one\n\n## Rows\n\n| task | n |\n|---|---|\n",
    );
    for n in 0..3000 {
        let _ = writeln!(report, "| T{n} | {n} {} |", "y".repeat(20));
    }
    std::fs::write(dir.join("report.md"), &report).unwrap();
    let split = run(&root, &["split", "451"]);
    assert_eq!(split.code, 0, "{}", split.stderr);
    assert!(
        split.stdout.contains(
            "split: 2 finished section(s) of the closed feature moved from plan.md first: T05, T06"
        ),
        "{}",
        split.stdout
    );
    let plan = read(&dir, "plan.md");
    assert!(plan.contains("## Summary") && !plan.contains("### T05") && !plan.contains("### T06"));
    // the live record: the block plan.md holds, no task, the round naming a live block
    let live: Value = serde_json::from_str(&read(&dir, "plan-review.json")).unwrap();
    assert_eq!(live["feature"], "451-x");
    assert_eq!(
        live["blocks"]
            .as_object()
            .unwrap()
            .keys()
            .collect::<Vec<_>>(),
        ["## Summary"]
    );
    assert!(live["tasks"].as_object().unwrap().is_empty());
    assert_eq!(
        live["block_reviews"],
        json!([{"blocks": ["## Summary", "### T04 (gone)"], "verdict": "CLEAR"}])
    );
    // the closed entries, read back by task; every entry in the parts or the flat record, once
    let files = archive::files(&dir);
    let t04 = archive::review(&files, "T04");
    assert_eq!(t04["tasks"]["T04"]["reviewed"], "2026-11-20");
    assert_eq!(t04["blocks"]["### T04 (gone)"]["sha256"], "g");
    assert_eq!(
        archive::review(&files, "T05")["block_reviews"]
            .as_array()
            .unwrap()
            .len(),
        4
    );
    let index: Value = serde_json::from_str(&read(&dir, "archive/index.json")).unwrap();
    let parts: Vec<String> =
        serde_json::from_value(index["parts"]["plan-review.json"].clone()).unwrap();
    let mut whole = json!({"blocks": {}, "tasks": {}, "block_reviews": []});
    for p in &parts {
        let v: Value = serde_json::from_str(&read(&dir, &format!("archive/{p}"))).unwrap();
        assert!(v["part"]
            .as_str()
            .unwrap()
            .starts_with("451-x - plan-review.json, the closed tasks' entries "));
        for m in ["blocks", "tasks"] {
            for (k, e) in v[m].as_object().unwrap() {
                assert!(whole[m].get(k).is_none());
                whole[m][k] = e.clone();
            }
        }
        whole["block_reviews"]
            .as_array_mut()
            .unwrap()
            .extend(v["block_reviews"].as_array().unwrap().iter().cloned());
    }
    assert_eq!(whole["blocks"].as_object().unwrap().len() + 1, 4);
    assert_eq!(whole["tasks"].as_object().unwrap().len(), 3);
    assert_eq!(whole["block_reviews"].as_array().unwrap().len() + 1, 4);
    assert!(read(&dir, "archive/INDEX.md").contains("| plan-review.json | `plan-review/001-"));
    // the report: an index naming its parts
    let index_md = read(&dir, "report.md");
    assert!(index_md.contains(archive::report::MARK) && index_md.contains("`report/02-rows-1.md`"));
    // a rerun moves nothing more and keeps the report's parts
    let again = run(&root, &["split", "451"]);
    assert!(
        again.stdout.starts_with("split: 0 part(s) written"),
        "{}",
        again.stdout
    );
    assert!(dir.join("report/02-rows-1.md").is_file());
}

#[test]
fn an_open_feature_keeps_an_unreviewed_section_and_a_bad_record_is_named() {
    let root = repo();
    let dir = feature_at(&root, Some(PLAN), None, "451-x");
    std::fs::write(dir.join("tasks.md"), "- [x] T05 five\n- [ ] T06 six\n").unwrap();
    std::fs::write(dir.join("plan-review.json"), "[1]").unwrap();
    let refused = run(&root, &["split", "451"]);
    assert_eq!(refused.code, 1);
    assert!(
        refused
            .stderr
            .contains("plan-review.json: not a JSON object, left whole"),
        "{}",
        refused.stderr
    );
    assert!(read(&dir, "plan.md").contains("### T06 part B"));
    // a record with nothing closed is left as it stands, the report under the bound too
    std::fs::write(
        dir.join("plan-review.json"),
        "{\"blocks\": {\"## Summary\": {}}}",
    )
    .unwrap();
    std::fs::write(dir.join("report.md"), "# small\n").unwrap();
    assert_eq!(run(&root, &["split", "451"]).code, 0);
    assert_eq!(
        read(&dir, "plan-review.json"),
        "{\"blocks\": {\"## Summary\": {}}}"
    );
    assert_eq!(read(&dir, "report.md"), "# small\n");
    // an open task's review entry stays live; a record that cannot be rewritten is the verb's failure
    std::fs::write(
        dir.join("plan-review.json"),
        "{\"tasks\": {\"T04\": {}, \"T06\": {}}}",
    )
    .unwrap();
    let record = dir.join("plan-review.json");
    let mut perm = std::fs::metadata(&record).unwrap().permissions();
    perm.set_readonly(true);
    std::fs::set_permissions(&record, perm.clone()).unwrap();
    let unwritable = run(&root, &["split", "451"]);
    #[expect(
        clippy::permissions_set_readonly_false,
        reason = "the record is made writable again for the report step below"
    )]
    perm.set_readonly(false);
    std::fs::set_permissions(&record, perm).unwrap();
    assert_eq!(unwritable.code, 1);
    assert!(unwritable.stderr.contains("plan-review.json: "));
    assert!(read(&dir, "plan-review.json").contains("T04"));
    // a report part that cannot be written is the verb's failure
    let big = format!("# r\n\n## Big\n\n{}\n", "word ".repeat(20_000));
    std::fs::write(dir.join("report.md"), big).unwrap();
    std::fs::write(dir.join("report"), "in the way").unwrap();
    let failed = run(&root, &["split", "451"]);
    assert_eq!(failed.code, 1);
    assert!(failed.stderr.contains("report"), "{}", failed.stderr);
}

/// 462 T555: a ticked, reviewed section whose heading names example ids (451 T18's `T="T1,T2"`) is moved by the tick's archive; the
/// heading's own leading ids are its tasks.
#[test]
fn a_heading_s_example_ids_hold_no_section_back() {
    let root = repo();
    let plan = "### T05 (`T=\"T1,T2\"` read as one task)\n\nfive\n";
    let dir = feature_at(&root, Some(plan), None, "375-x");
    std::fs::write(dir.join("tasks.md"), "- [x] T05 five\n- [ ] T06 six\n").unwrap();
    let src = write_json(&root, "w.json", &current(&[], "CLEAR", plan));
    assert_eq!(
        run(&root, &["record", "375", &src, "--as", "spec-fidelity"]).code,
        0
    );
    let said = run(&root, &["archive", "375"]).stdout;
    assert!(said.contains("1 task section(s) moved to 375-x/plan-done.md: T05"));
    assert_eq!(
        super::super::task::heading_ids("### T18 (FR-011: `T=\"T1,T2\"` read as one task)"),
        ["T18"]
    );
    assert_eq!(
        super::super::task::heading_ids("### T409, T406 Approach (checklist part A)"),
        ["T409", "T406"]
    );
    assert_eq!(
        super::super::task::heading_ids("### Wave 1 (T01, T02)"),
        ["T01", "T02"]
    );
}
