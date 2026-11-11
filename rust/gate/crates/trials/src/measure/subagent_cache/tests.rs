//! Where each agent type's tokens are written against read.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::{at, back_to_back, cli, commas, families, family, long_lines, repeated, runs, spend};

fn guide() -> String {
    (0..30).map(|i| format!("Rule {i}: a modal says what the map draws and why, in the voice its reader expects.")).collect::<Vec<_>>().join("\n")
}

fn run(
    root: &Path,
    session: &str,
    agent: &str,
    kind: &str,
    start: &str,
    calls: &[(i64, i64, i64)],
    manifest: &str,
) {
    let d = root.join(session).join("subagents");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(
        d.join(format!("agent-{agent}.meta.json")),
        json!({"agentType": kind, "description": "Claims triage 12"}).to_string(),
    )
    .unwrap();
    let mut lines = vec![
        json!({"type": "user", "timestamp": start, "message": {"role": "user", "content": "go"}}),
    ];
    for (i, (read, write, out)) in calls.iter().enumerate() {
        let content = if i == 0 && !manifest.is_empty() {
            json!([{"type": "tool_use", "id": format!("r{i}"), "name": "Read", "input": {"file_path": "/tmp/b/MANIFEST.md"}}, "text"])
        } else {
            json!([])
        };
        let usage = json!({"input_tokens": 2, "cache_read_input_tokens": read, "cache_creation_input_tokens": write, "output_tokens": out});
        let row = json!({"type": "assistant", "requestId": format!("q{i}"), "timestamp": start, "message": {"id": format!("m{i}"), "usage": usage, "content": content}});
        lines.push(row.clone());
        lines.push(row);
        if i == 0 && !manifest.is_empty() {
            lines.push(json!({"type": "user", "timestamp": start, "message": {"content": [{"type": "tool_result", "tool_use_id": "r0", "content": [{"type": "text", "text": manifest}]}]}}));
            lines.push(json!({"type": "user", "timestamp": start, "message": {"content": [{"type": "tool_result", "tool_use_id": "r0", "content": "a later read"}]}}));
        }
    }
    std::fs::write(
        d.join(format!("agent-{agent}.jsonl")),
        lines
            .iter()
            .map(Value::to_string)
            .collect::<Vec<_>>()
            .join("\n")
            + "\nnot json\n",
    )
    .unwrap();
}

fn root() -> PathBuf {
    let t = crate::checks::scratch("subagent-cache");
    run(
        &t,
        "s1",
        "a",
        "modal-form",
        "2026-10-17T10:00:00Z",
        &[(0, 9000, 100), (9000, 4000, 200)],
        &format!(
            "{}\nunit one, its own text that no other holds at all",
            guide()
        ),
    );
    run(
        &t,
        "s1",
        "b",
        "modal-form",
        "2026-10-17T10:02:00Z",
        &[(6000, 2500, 100)],
        &format!(
            "{}\nunit two, its own text that no other holds at all",
            guide()
        ),
    );
    run(
        &t,
        "s1",
        "c",
        "modal-form",
        "2026-10-17T11:00:00Z",
        &[(0, 9000, 100)],
        "",
    );
    run(
        &t,
        "s2",
        "d",
        "general-purpose",
        "2026-10-17T10:01:00Z",
        &[(4000, 29000, 50)],
        "",
    );
    run(
        &t,
        "s2",
        "e",
        "general-purpose",
        "2026-10-09T10:01:00Z",
        &[(4000, 29000, 50)],
        "",
    );
    std::fs::create_dir_all(t.join("s3/subagents")).unwrap();
    std::fs::write(t.join("s3/subagents/agent-x.jsonl"), "{}\n").unwrap();
    let d = t.join("s4/subagents");
    std::fs::create_dir_all(&d).unwrap();
    std::fs::write(d.join("agent-y.meta.json"), "{}").unwrap();
    std::fs::write(d.join("agent-y.jsonl"), "{}\n").unwrap();
    t
}

#[test]
fn a_run_counts_each_request_once_and_keeps_its_first_manifest_and_back_to_back_is_the_cache_window(
) {
    let rs = runs(&root(), "2026-10-10");
    assert_eq!(
        rs.iter().map(|r| r.kind.as_str()).collect::<Vec<_>>(),
        ["modal-form", "general-purpose", "modal-form", "modal-form"]
    );
    assert_eq!(rs[0].calls.len(), 2);
    assert!(rs[0].manifest.starts_with("Rule 0"));
    let pairs = back_to_back(&rs);
    assert_eq!(
        pairs["modal-form"]
            .iter()
            .map(|r| r.start.as_str())
            .collect::<Vec<_>>(),
        ["2026-10-17T10:02:00Z"]
    );
    assert!(!pairs.contains_key("general-purpose"));
}

#[test]
fn repeated_lines_are_counted_and_the_read_tool_s_numbers_dropped() {
    let line = "x".repeat(50);
    let a = format!("     1\t{line}\nshort");
    let b = format!("{line}\nanother short one");
    assert_eq!(long_lines(&a).len(), 1);
    assert_eq!(repeated(&[&a]), 0);
    assert_eq!(repeated(&[&a, &b, &a]), 50);
    let other = "y".repeat(50);
    assert_eq!(repeated(&[&a, &other, &other]), 0);
}

#[test]
fn the_report_names_each_type_s_fresh_write_its_repetition_and_the_spend() {
    let t = root();
    let arg = |words: &[&str]| -> Vec<String> {
        words
            .iter()
            .map(|s| (*s).to_owned())
            .chain(["--root".to_owned(), t.display().to_string()])
            .collect()
    };
    let got = cli(
        &arg(&["--since", "2026-10-10"]),
        Path::new("/nonexistent"),
        "1999",
    )
    .stdout;
    let row = got.lines().find(|l| l.starts_with("modal-form")).unwrap();
    let cells: Vec<&str> = row.split_whitespace().collect();
    assert_eq!(cells[1..5], ["3", "1", "6000", "2500"]);
    assert!(cells[5].parse::<usize>().unwrap() >= guide().len() - 200);
    assert!(
        got.contains("base-input units")
            && got.contains("a write 1.25x")
            && got.contains("output 5.0x")
    );
    assert!(cli(
        &arg(&["--since", "2027-01-01"]),
        Path::new("/nonexistent"),
        "1999"
    )
    .stdout
    .contains("no subagent runs"));
    let fam = cli(
        &arg(&["--since", "2026-10-01", "--families", "2026-10-15"]),
        Path::new("/nonexistent"),
        "1999",
    )
    .stdout;
    assert!(fam.contains("claims triage") && fam.contains("by family"));
    assert!(cli(&[], Path::new("/nonexistent"), "1999")
        .stdout
        .contains("no subagent runs"));
}

#[test]
fn spend_weighs_writes_reads_and_output_and_the_helpers_hold() {
    let t = root();
    let rs = runs(&t, "2026-10-10");
    let every: Vec<_> = rs.iter().collect();
    let (write, read, output, units) = spend(&every);
    assert!(write > 0 && read > 0 && output > 0 && units > 0.0);
    assert_eq!(family("Claims triage 12 round 2"), "claims triage");
    assert_eq!(family("Research pass: well on a roji"), "research pass");
    assert_eq!(family("1 2"), "?");
    assert_eq!(commas(1_234_567), "1,234,567");
    assert!((at("2026-10-17T10:02:00Z") - at("2026-10-17T10:00:00Z") - 120.0).abs() < 1e-9);
    assert!((at("1970-01-01T00:00:00Z")).abs() < 1e-9);
    assert!(
        (at("1969-02-01T00:00:00Z") + 28.0 * 86_400.0 * 12.0 + 33.0 * 86_400.0 * 1.0).abs() < 1e7
    );
    assert!((at("nonsense")).abs() < f64::EPSILON);
    let list = families(&rs, "2026-10-15");
    assert_eq!(list[0].0, "claims triage");
}

fn plain(kind: &str, description: &str, start: &str) -> super::Run {
    super::Run {
        kind: kind.to_owned(),
        session: "s".to_owned(),
        start: start.to_owned(),
        calls: vec![json!({})],
        manifest: String::new(),
        description: description.to_owned(),
    }
}

#[test]
fn families_sort_and_a_body_reads_every_shape() {
    let rs = [
        plain("general-purpose", "alpha one", "2026-10-01"),
        plain("?", "beta two", "2026-10-20"),
        plain("?", "beta two", "2026-10-21"),
        plain("modal-form", "gamma", "2026-10-22"),
    ];
    let got = families(&rs, "2026-10-15");
    assert_eq!(
        got.iter().map(|f| f.0.as_str()).collect::<Vec<_>>(),
        ["beta two", "alpha one"]
    );
    assert_eq!(super::body_text(&json!("x")), "x");
    assert_eq!(super::body_text(&json!(3)), "");
}

#[test]
fn a_negative_count_keeps_its_sign() {
    assert_eq!(commas(-1_234_567), "-1,234,567");
}
