//! The census, on scratch transcripts.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::{cli, parse, read_run, rounded, rows, transcripts, Asked};

fn words(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

fn turn(id: &str, model: &str, n: i64) -> String {
    json!({"type": "assistant", "timestamp": "2026-09-10T00:00:00Z", "message": {"id": id, "model": model, "usage": {"input_tokens": n, "cache_read_input_tokens": 1000, "output_tokens": n, "output_tokens_details": {"thinking_tokens": 2}}}}).to_string()
}

/// A projects directory: one check run, two ad-hoc ones, a run outside the repository and one that never answered.
fn projects(tag: &str) -> PathBuf {
    let root = crate::checks::scratch(tag);
    let run = "-diagram-x/s1/subagents";
    put(
        &root,
        &format!("{run}/agent-1.jsonl"),
        &format!(
            "{}\nnot json\n{}\n",
            turn("m1", "m-opus", 1500),
            turn("m1", "m-opus", 1600)
        ),
    );
    put(
        &root,
        &format!("{run}/agent-1.meta.json"),
        r#"{"agentType": "spec-fidelity"}"#,
    );
    put(
        &root,
        &format!("{run}/agent-2.jsonl"),
        &turn("m2", "claude-fable-1", 10),
    );
    put(
        &root,
        &format!("{run}/agent-2.meta.json"),
        r#"{"agentType": "Explore"}"#,
    );
    put(
        &root,
        &format!("{run}/agent-3.jsonl"),
        &turn("m3", "m-sonnet", 10),
    );
    put(
        &root,
        &format!("{run}/agent-3.meta.json"),
        r#"{"agentType": "Explore", "model": "sonnet"}"#,
    );
    put(
        &root,
        &format!("{run}/agent-4.jsonl"),
        &turn("m4", "m-opus", 10),
    );
    put(
        &root,
        &format!("{run}/agent-4.meta.json"),
        r#"{"agentType": "fork", "model": "INHERIT"}"#,
    );
    put(&root, "-diagram/s2/subagents/agent-5.jsonl", "");
    put(
        &root,
        "-other/s3/subagents/agent-6.jsonl",
        &turn("m6", "m-opus", 10),
    );
    put(
        &root,
        "-diagram-x/s1/subagents/other.jsonl",
        &turn("m7", "m-opus", 10),
    );
    root
}

#[test]
fn the_transcripts_are_this_repositorys_only() {
    let root = projects("ac-find");
    let names: Vec<String> = transcripts(&root)
        .iter()
        .map(|p| p.strip_prefix(&root).unwrap().display().to_string())
        .collect();
    assert_eq!(names.len(), 5);
    assert!(names[0].starts_with("-diagram/s2"), "{names:?}");
    assert!(transcripts(&root.join("no-such")).is_empty());
}

#[test]
fn a_run_is_its_meta_and_its_fold_a_bad_line_skipped_and_a_raw_line_separator_costs_its_record() {
    let root = crate::checks::scratch("ac-run");
    let t = root.join("agent-1.jsonl");
    put(
        &root,
        "agent-1.jsonl",
        &format!(
            "{}\nnot json\n{{\"type\": \"user\", \"x\": \"a\u{2028}b\"}}\n{}\n",
            turn("a", "m", 5),
            turn("b", "m", 3)
        ),
    );
    put(&root, "agent-1.meta.json", r#"{"agentType": "k"}"#);
    let (meta, usage) = read_run(&t);
    assert_eq!(meta["agentType"], "k");
    assert_eq!(
        (usage["turns"].as_i64(), usage["output"].as_i64()),
        (Some(2), Some(8))
    );
    let (bare, _) = read_run(&root.join("agent-2.jsonl"));
    assert_eq!(bare, json!({}));
}

#[test]
fn the_census_renders_each_agent_with_its_means_and_the_adhoc_block() {
    let root = projects("ac-render");
    let at = root.display().to_string();
    let got = cli(&words(&["--root", &at]), Path::new("/nonexistent"));
    assert_eq!(got.code, 0);
    let expected = "agent                   runs   turns      fresh in       cached in      output   thinking      in/run   out/run  models\n-----------------------------------------------------------------------------------------------------------------------\nspec-fidelity              1       1         1,600           1,000       1,600          2       2,600     1,600  m-opus x1\nExplore                    2       2            20           2,000          20          4       1,010        10  claude-fable-1 x1, m-sonnet x1\nfork                       1       1            10           1,000          10          2       1,010        10  m-opus x1\nunknown                    1       0             0               0           0          0           0         0  none x1\n\nad-hoc agents (no file pins their model) - runs dispatched with no model, and what they ran on:\n  Explore                 2 runs,    1 with no model: claude-fable-1 x1\n  fork                    1 runs,    1 with no model: m-opus x1\n";
    assert_eq!(got.stdout, expected);
}

#[test]
fn a_census_with_nothing_is_the_header_and_an_adhoc_row_with_a_named_model_shows_a_dash() {
    let root = crate::checks::scratch("ac-empty");
    let got = cli(
        &words(&["--root", &root.display().to_string()]),
        Path::new("/x"),
    );
    assert_eq!(got.stdout.lines().count(), 2);
    put(
        &root,
        "-diagram/s/subagents/agent-1.jsonl",
        &turn("a", "m", 1),
    );
    put(
        &root,
        "-diagram/s/subagents/agent-1.meta.json",
        r#"{"agentType": "Plan", "model": "opus"}"#,
    );
    let named = cli(
        &words(&["--root", &root.display().to_string()]),
        Path::new("/x"),
    );
    assert!(
        named
            .stdout
            .ends_with("  Plan                    1 runs,    0 with no model: -\n"),
        "{}",
        named.stdout
    );
}

#[test]
fn the_default_root_is_under_home() {
    let home = crate::checks::scratch("ac-home");
    let root = home.join(".claude/projects");
    put(
        &root,
        "-diagram/s/subagents/agent-1.jsonl",
        &turn("a", "m", 1),
    );
    assert!(cli(&[], &home).stdout.contains("unknown"));
}

#[test]
fn since_is_inclusive_and_until_exclusive() {
    let run = |started: &str| {
        (
            json!({"agentType": "k"}),
            json!({"started": started, "turns": 1, "fresh": 1, "cached": 0, "output": 0, "thinking": 0, "model": "m"}),
        )
    };
    let runs = [
        run("2026-09-10T01"),
        run("2026-09-11T01"),
        run("2026-09-12T01"),
    ];
    let count =
        |since: &str, until: &str| rows(&runs, since, until).0.first().map_or(0, |r| r.runs);
    assert_eq!(count("", ""), 3);
    assert_eq!(count("2026-09-11", ""), 2);
    assert_eq!(count("", "2026-09-12"), 2);
    assert_eq!(count("2026-09-11", "2026-09-12"), 1);
    assert_eq!(count("2026-09-13", ""), 0);
}

#[test]
fn ties_keep_first_seen_order_and_models_go_by_count() {
    let run = |kind: &str, model: &str, fresh: i64| {
        (
            json!({"agentType": kind}),
            json!({"started": "", "turns": 1, "fresh": fresh, "cached": 0, "output": 0, "thinking": 0, "model": model}),
        )
    };
    let runs = [
        run("b", "x", 5),
        run("a", "y", 5),
        run("a", "z", 0),
        run("a", "z", 0),
        run("c", "x", 9),
    ];
    let (table, _) = rows(&runs, "", "");
    let agents: Vec<&str> = table.iter().map(|r| r.agent.as_str()).collect();
    assert_eq!(agents, ["c", "b", "a"]);
    assert_eq!(
        table[2].models,
        vec![("z".to_owned(), 2), ("y".to_owned(), 1)]
    );
}

#[test]
fn a_mean_rounds_half_to_even() {
    assert_eq!(rounded(5, 2), 2);
    assert_eq!(rounded(7, 2), 4);
    assert_eq!(rounded(9, 4), 2);
    assert_eq!(rounded(11, 4), 3);
    assert_eq!(rounded(0, 1), 0);
}

#[test]
fn the_json_and_the_record_are_written_as_python_writes_them() {
    let root = projects("ac-json");
    let (json_file, record_file) = (root.join("out.json"), root.join("m.json"));
    put(&root, "m.json", "{\n \"keep\": {\n  \"value\": 1.5,\n  \"note\": \"caf\\u00e9\"\n },\n \"census.old\": {\n  \"value\": 1,\n  \"command\": \"\"\n}\n}\n");
    let (a, b, c) = (
        root.display().to_string(),
        json_file.display().to_string(),
        record_file.display().to_string(),
    );
    let got = cli(
        &words(&[
            "--root",
            &a,
            "--until",
            "2026-09-19",
            "--since=2026-01-01",
            "--json",
            &b,
            "--record",
            &c,
        ]),
        Path::new("/x"),
    );
    assert_eq!(got.code, 0, "{}", got.stderr);
    let written = std::fs::read_to_string(&json_file).unwrap();
    assert!(written.starts_with("{\n \"since\": \"2026-01-01\",\n \"agents\": [\n  {\n   \"agent\": \"spec-fidelity\",\n   \"runs\": 1,\n   \"turns\": 1,\n   \"fresh\": 1600,\n   \"cached\": 1000,\n   \"output\": 1600,\n   \"thinking\": 2,\n   \"models\": {\n    \"m-opus\": 1\n   }\n  },"), "{written}");
    assert!(written.contains("\"adhoc\": [\n  {\n   \"agent\": \"Explore\",\n   \"runs\": 2,\n   \"no_model\": 1,\n   \"inherited\": {\n    \"claude-fable-1\": 1\n   }\n  },"), "{written}");
    let kept = std::fs::read_to_string(&record_file).unwrap();
    assert!(kept.starts_with("{\n \"keep\": {\n  \"value\": 1.5,\n  \"note\": \"caf\\u00e9\"\n },\n \"census.spec-fidelity.runs\": {\n  \"value\": 1,"), "{kept}");
    assert!(!kept.contains("census.old"));
    assert!(kept.contains(&format!("\"command\": \"scripts/gates/l7r-gate.sh record agent-census --until 2026-09-19 --record {c}\"")));
    assert!(kept.contains("\"census.adhoc.Explore.on_fable\": {\n  \"value\": 1,"));
    assert!(kept.contains("\"census.Explore.input_per_run\": {\n  \"value\": 1010,"));
}

#[test]
fn a_record_with_no_until_has_no_command_and_a_new_file_is_made() {
    let root = projects("ac-new");
    let file = root.join("new.json");
    let (a, b) = (root.display().to_string(), file.display().to_string());
    assert_eq!(
        cli(&words(&["--root", &a, "--record", &b]), Path::new("/x")).code,
        0
    );
    assert!(std::fs::read_to_string(&file)
        .unwrap()
        .contains("\"command\": \"\""));
}

#[test]
fn a_write_or_a_bad_record_that_fails_keeps_the_table_and_exits_1() {
    let root = projects("ac-fail");
    let a = root.display().to_string();
    let nowhere = root.join("no/such/out.json").display().to_string();
    let json_failed = cli(&words(&["--root", &a, "--json", &nowhere]), Path::new("/x"));
    assert_eq!(json_failed.code, 1);
    assert!(json_failed.stdout.contains("spec-fidelity"));
    assert!(json_failed.stderr.starts_with("agent-census: "));
    let failed = cli(
        &words(&["--root", &a, "--record", &nowhere]),
        Path::new("/x"),
    );
    assert_eq!(failed.code, 1);
    for (tag, body) in [("bad.json", "not json"), ("list.json", "[]")] {
        put(&root, tag, body);
        let path = root.join(tag).display().to_string();
        assert_eq!(
            cli(&words(&["--root", &a, "--record", &path]), Path::new("/x")).code,
            1
        );
    }
    std::fs::write(root.join("binary.json"), [0xff_u8]).unwrap();
    let path = root.join("binary.json").display().to_string();
    assert_eq!(
        cli(&words(&["--root", &a, "--record", &path]), Path::new("/x")).code,
        1
    );
}

#[test]
fn the_flags_are_the_pythons_and_anything_else_is_the_usage() {
    let asked: Asked = parse(
        &words(&[
            "--root",
            "r",
            "--since",
            "s",
            "--until=u",
            "--json",
            "j",
            "--record",
            "x",
        ]),
        "d".to_owned(),
    )
    .unwrap();
    assert_eq!(
        [
            asked.root,
            asked.since,
            asked.until,
            asked.json,
            asked.record
        ],
        ["r", "s", "u", "j", "x"]
    );
    assert_eq!(parse(&[], "d".to_owned()).unwrap().root, "d");
    for bad in [
        &["--nope"][..],
        &["pos"][..],
        &["--since"][..],
        &["--since", "--until"][..],
    ] {
        assert_eq!(cli(&words(bad), Path::new("/x")).code, 2, "{bad:?}");
    }
}
