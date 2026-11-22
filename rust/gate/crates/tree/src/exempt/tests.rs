//! The record's rules; the entries a stage's landing makes stale, and the entry no stage can name.

use std::path::Path;

use super::{cli, load, split};

fn scratch(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = l7r_shared::tempdir::TempDir::new(&format!("gate-exempt-{tag}"));
    std::fs::create_dir_all(dir.join("dev")).unwrap();
    dir
}

fn record(dir: &Path, entries: &str) {
    std::fs::write(
        dir.join("dev/coverage-exempt.json"),
        format!("{{\"ruling\": \"r\", \"entries\": [{entries}]}}"),
    )
    .unwrap();
}

fn file(dir: &Path, rel: &str) {
    std::fs::write(dir.join(rel), "x\n").unwrap();
}

fn accepted(dir: &Path, names: &str) {
    std::fs::write(
        dir.join("dev/work-budget.json"),
        format!("{{\"stages\": {{{names}}}}}"),
    )
    .unwrap();
}

fn ask(dir: &Path, args: &[&str]) -> crate::Reply {
    cli(
        &args.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
        dir,
    )
}

const LIVE: &str = r#"{"path": "a.py", "stages": ["seat", "hem"]}"#;
const DONE: &str = r#"{"path": "b.py", "stages": ["sink"]}"#;
const GONE: &str = r#"{"path": "gone.py", "stages": ["seat"]}"#;

fn three(tag: &str) -> l7r_shared::tempdir::TempDir {
    let dir = scratch(tag);
    record(&dir, &[LIVE, DONE, GONE].join(","));
    file(&dir, "a.py");
    file(&dir, "b.py");
    accepted(
        &dir,
        r#""sink": {"status": "accepted"}, "seat": {"status": "budgeted"}, "hem": null"#,
    );
    dir
}

#[test]
fn no_record_exempts_nothing() {
    let dir = scratch("none");
    std::fs::remove_dir(dir.join("dev")).unwrap();
    assert_eq!(ask(&dir, &["omit"]).stdout, "\n");
    assert_eq!(ask(&dir, &["exempt"]).stdout, "");
    assert_eq!(load(&dir).unwrap()["entries"], serde_json::json!([]));
}

#[test]
fn an_entry_naming_no_stages_refuses_rather_than_reading_as_accepted() {
    let dir = scratch("nostage");
    file(&dir, "a.py");
    for bad in [r#"{"path": "a.py", "stages": []}"#, r#"{"path": "a.py"}"#] {
        record(&dir, bad);
        let refused = ask(&dir, &["omit"]);
        assert_eq!(refused.code, 1);
        assert!(refused.stderr.contains("a.py names no stages"));
    }
    std::fs::write(dir.join("dev/coverage-exempt.json"), "not json").unwrap();
    assert!(load(&dir).is_err());
    record(&dir, LIVE);
    std::fs::write(dir.join("dev/work-budget.json"), "not json").unwrap();
    assert_eq!(ask(&dir, &["exempt"]).code, 1);
}

#[test]
fn an_entry_is_stale_when_its_file_is_gone_or_every_stage_it_serves_is_accepted() {
    let dir = three("stale");
    let (live, stale) = split(&dir).unwrap();
    assert_eq!(live.len(), 1);
    assert_eq!(live[0]["path"], "a.py");
    let whys: Vec<(&str, &str)> = stale
        .iter()
        .map(|(e, w)| (e["path"].as_str().unwrap(), w.as_str()))
        .collect();
    assert_eq!(
        whys,
        [
            (
                "b.py",
                "every stage it serves is accepted in Rust (sink); the thin door keeps the floor"
            ),
            ("gone.py", "the file is gone")
        ]
    );
    assert_eq!(ask(&dir, &["omit"]).stdout, "--omit=a.py\n");
    assert_eq!(ask(&dir, &["exempt"]).stdout, "a.py\n");
    assert_eq!(ask(&dir, &["stale"]).stdout, "b.py\tevery stage it serves is accepted in Rust (sink); the thin door keeps the floor\ngone.py\tthe file is gone\n");
}

#[test]
fn the_list_names_each_and_a_prune_drops_the_stale_ones_and_keeps_the_rest() {
    let dir = three("list");
    let listed = ask(&dir, &["list"]).stdout;
    assert!(
        listed.starts_with("a.py  (seat, hem)\nSTALE b.py - ")
            && listed.ends_with("coverage-exempt: 1 exempt, 2 stale\n"),
    );
    let pruned = ask(&dir, &["list", "--prune"]).stdout;
    assert!(
        pruned.contains("coverage-exempt: dropped gone.py - the file is gone\n")
            && pruned.ends_with("coverage-exempt: 1 exempt, 0 stale\n")
    );
    let text = std::fs::read_to_string(dir.join("dev/coverage-exempt.json")).unwrap();
    assert!(
        text.starts_with("{\n \"ruling\": \"r\",\n \"entries\": [\n  {") && text.ends_with("}\n")
    );
}

/// `report` left with `codeid.py`'s coverage.py reader (feature 449 T247): it is refused as any unknown verb is.
#[test]
fn the_report_is_gone_and_an_unknown_verb_is_refused() {
    let dir = three("py");
    assert_eq!(ask(&dir, &["report"]).code, 2);
    assert_eq!(ask(&dir, &["nonsense"]).code, 2);
}
