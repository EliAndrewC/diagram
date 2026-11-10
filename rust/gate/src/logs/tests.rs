//! Each record's shape and every refusal.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{json_field, log_cli, ruff_cli, ruff_toml, run_record, RunEnv};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn repo(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    for args in [
        &["init", "-q"][..],
        &["config", "user.email", "t@t"],
        &["config", "user.name", "t"],
        &["commit", "-q", "--allow-empty", "-m", "a"],
    ] {
        assert!(std::process::Command::new("git")
            .arg("-C")
            .arg(&root)
            .args(args)
            .status()
            .unwrap()
            .success());
    }
    root
}

fn one_record(root: &Path, log: &str) -> Value {
    let months: Vec<_> = std::fs::read_dir(root.join("dev").join(log))
        .unwrap()
        .flatten()
        .collect();
    let files: Vec<_> = std::fs::read_dir(months[0].path())
        .unwrap()
        .flatten()
        .collect();
    assert_eq!(files.len(), 1);
    serde_json::from_str(&std::fs::read_to_string(files[0].path()).unwrap()).unwrap()
}

fn none() -> RunEnv {
    RunEnv {
        mode: None,
        selected: String::new(),
        stats: String::new(),
    }
}

#[test]
fn a_run_is_recorded_with_its_mode_cache_and_stats_and_the_pointer_to_it() {
    let root = repo("logs-run");
    let env = RunEnv {
        mode: Some("full".to_owned()),
        selected: "7".to_owned(),
        stats: "{\"selected\": 7048, \"host\": {\"load\": [1.5]}}".to_owned(),
    };
    run_record(
        &words(&["done", "reference", "139", "green", "warm"]),
        &env,
        &root,
    )
    .unwrap();
    let r = one_record(&root, "run-log");
    let keys: Vec<&String> = r.as_object().unwrap().keys().collect();
    assert_eq!(
        keys,
        [
            "utc", "target", "scope", "seconds", "result", "commit", "cache", "mode", "selected",
            "host"
        ]
    );
    assert_eq!(
        (r["seconds"].as_i64(), r["selected"].as_i64()),
        (Some(139), Some(7048))
    );
    let pointer = std::fs::read_to_string(root.join(".git/last-run-record")).unwrap();
    assert!(
        pointer.contains("dev/run-log/")
            && pointer.starts_with('/')
            && Path::new(&pointer).is_file()
    );
}

#[test]
fn a_run_needs_no_cache_or_mode_and_bad_stats_are_none() {
    let root = repo("logs-run-plain");
    let env = RunEnv {
        stats: "not json".to_owned(),
        ..none()
    };
    run_record(
        &words(&["done", "reference", "1", "failed: x", "already-verified"]),
        &env,
        &root,
    )
    .unwrap();
    let r = one_record(&root, "run-log");
    assert!(r.get("cache").is_none() && r.get("mode").is_none());
    assert_eq!(r["result"], "failed: x");
}

#[test]
fn a_malformed_run_is_refused() {
    let root = repo("logs-run-bad");
    assert!(run_record(&words(&["done"]), &none(), &root).is_err());
    assert!(
        run_record(&words(&["done", "r", "soon", "green"]), &none(), &root)
            .unwrap_err()
            .contains("not a number")
    );
}

#[test]
fn a_run_or_a_bypass_that_cannot_be_written_says_so() {
    let root = repo("logs-nowrite");
    std::fs::write(root.join("dev"), "a file where the log's folder goes").unwrap();
    assert!(run_record(&words(&["d", "r", "1", "g"]), &none(), &root).is_err());
    let got = log_cli(&words(&["bypass", "t", "o", "w"]), &root);
    assert_eq!(got.code, 1);
}

#[test]
fn a_bypass_records_its_outcome_and_why() {
    let root = repo("logs-bypass");
    assert_eq!(
        log_cli(
            &words(&["bypass", "done FULL", "permitted", "the reason"]),
            &root
        )
        .code,
        0
    );
    let r = one_record(&root, "bypass-log");
    assert_eq!(
        (
            r["target"].as_str(),
            r["outcome"].as_str(),
            r["why"].as_str()
        ),
        (Some("done FULL"), Some("permitted"), Some("the reason"))
    );
    assert!(r["commit"].as_str().unwrap().len() >= 7);
    assert_eq!(log_cli(&words(&["bypass", "x"]), &root).code, 1);
}

#[test]
fn a_gate_bypass_lands_in_the_folder_named() {
    let root = repo("logs-gate");
    let dir = root.join("bl");
    std::fs::create_dir(&dir).unwrap();
    let there = dir.display().to_string();
    for _ in 0..2 {
        assert_eq!(
            log_cli(
                &words(&["gate-bypass", "cohort-gate", &there, "COHORT_OK: why"]),
                &root
            )
            .code,
            0
        );
    }
    let files: Vec<_> = std::fs::read_dir(&dir).unwrap().flatten().collect();
    assert_eq!(files.len(), 2);
    let r: Value =
        serde_json::from_str(&std::fs::read_to_string(files[0].path()).unwrap()).unwrap();
    assert_eq!(
        r.as_object().unwrap().keys().collect::<Vec<_>>(),
        ["utc", "target", "commit", "why"]
    );
    assert_eq!(r["target"], "cohort-gate");
    assert!(files[0].file_name().to_string_lossy().contains("Z-"));
    assert_eq!(log_cli(&words(&["gate-bypass", "g"]), &root).code, 1);
    assert_eq!(
        log_cli(&words(&["gate-bypass", "g", "/nonexistent/x", "w"]), &root).code,
        1
    );
}

#[test]
fn a_landing_names_the_task_last_started() {
    let dir = crate::checks::scratch("logs-land");
    std::fs::write(
        dir.join("task-starts.jsonl"),
        format!(
            "{}\n{}\n",
            json!({"feature": "1", "task": "T1"}),
            json!({"feature": "449", "task": "T069"})
        ),
    )
    .unwrap();
    let there = dir.display().to_string();
    for outcome in ["died", "push-exit-0"] {
        assert_eq!(
            log_cli(&words(&["land-tooling", &there, "a b", outcome]), &dir).code,
            0
        );
    }
    let text = std::fs::read_to_string(dir.join("land-tooling.jsonl")).unwrap();
    let last: Value = serde_json::from_str(text.lines().last().unwrap()).unwrap();
    assert_eq!(text.lines().count(), 2);
    assert_eq!(last["feature"], "449");
    assert_eq!(last["task"], "T069");
    assert_eq!(last["files"], json!(["a", "b"]));
    assert_eq!(last["outcome"], "push-exit-0");
    assert!(last["log"].as_str().unwrap().ends_with("/land-tooling.log"));
    assert_eq!(log_cli(&words(&["land-tooling", &there]), &dir).code, 1);
    let bare = crate::checks::scratch("logs-land-bare");
    assert_eq!(
        log_cli(
            &words(&["land-tooling", &bare.display().to_string(), "", "died"]),
            &bare
        )
        .code,
        0
    );
    assert_eq!(
        log_cli(
            &words(&["land-tooling", "/nonexistent/x", "", "died"]),
            &bare
        )
        .code,
        1
    );
}

#[test]
fn a_field_is_its_text_or_a_dash() {
    let d = crate::checks::scratch("logs-field");
    let f = d.join("r.json");
    std::fs::write(
        &f,
        json!({"verdict": "CLEAR", "engine_key": "", "n": 3}).to_string(),
    )
    .unwrap();
    let path = f.display().to_string();
    let got = json_field(&words(&[
        &path,
        "verdict",
        "engine_key",
        "content_key",
        "n",
    ]));
    assert_eq!((got.code, got.stdout.as_str()), (0, "CLEAR - - 3\n"));
    assert_eq!(json_field(&words(&["/nonexistent/x", "a"])).code, 1);
    assert_eq!(json_field(&[]).code, 2);
}

#[test]
fn only_the_ruff_sections_are_kept_their_prefix_dropped() {
    let text = "[project]\nname = \"x\"\n\n[tool.ruff]\nline-length = 160\n[tool.ruff.lint]\nselect = [\n  \"E\",\n]\n[tool.ruffle]\nno = 1\n[[tool.ruff.other]]\nno = 2\n[tool.pytest]\nno = 3\n";
    assert_eq!(
        ruff_toml(text),
        "\nline-length = 160\n[lint]\nselect = [\n  \"E\",\n]\n"
    );
    let got = ruff_cli(&mut "[tool.ruff]\na = 1\n".as_bytes());
    assert_eq!(got.stdout, "\na = 1\n");
}

#[test]
fn a_verb_this_module_does_not_know_is_refused() {
    let d = crate::checks::scratch("logs-other");
    assert_eq!(log_cli(&[], &d).code, 1);
    assert_eq!(log_cli(&words(&["frob"]), &d).code, 1);
}

#[test]
fn the_run_environment_is_read() {
    let env = RunEnv::read();
    assert_eq!(
        env.mode.is_some(),
        !std::env::var("RUN_MODE").unwrap_or_default().is_empty()
    );
}
