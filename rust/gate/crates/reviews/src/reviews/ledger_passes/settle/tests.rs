//! The log read, the passes costed and kept, the repeats folded, the answered ones dropped.

use std::path::{Path, PathBuf};

use serde_json::{json, Value};

use super::super::super::tests::put;
use super::super::tests::{as_pass, pass, world};
use super::{distinct, load_passes, same_stat, settled, unanswered, Pass};

fn passes(lines: &[String]) -> Vec<Pass> {
    lines.iter().map(|l| as_pass(l)).collect()
}

fn projects(env: &super::super::Env) -> PathBuf {
    Path::new(&env.home).join(".claude/projects")
}

#[test]
fn a_logged_line_is_a_pass_only_with_its_check_and_wall() {
    let (_d, env) = world("settle-load", &[]);
    let log = env.cwd.join("log.jsonl");
    assert!(load_passes(&log).unwrap().is_empty());
    put(&env.cwd, "log.jsonl", "[1]\nnot json\n{\"check\": \"\", \"wall\": 1}\n{\"check\": \"c\", \"wall\": 5, \"n\": null, \"l\": [1, \"a\"]}\n");
    let got = load_passes(&log).unwrap();
    assert_eq!(got.len(), 1);
    assert_eq!(
        Value::Object(got[0].clone()),
        json!({"check": "c", "wall": "5", "n": "None", "l": "[1, 'a']"})
    );
}

#[test]
fn a_kept_cost_is_served_while_its_transcript_stands() {
    let (_d, env) = world("settle-kept", &[]);
    let root = projects(&env);
    let t = root.join("p/s/subagents/agent-a1.jsonl");
    let meta = std::fs::metadata(&t).unwrap();
    let stat = json!([meta.len(), l7r_guard::shared::ledger::cost::py_mtime(&meta)]);
    let kept_file = env.cwd.join(".git/l7r-cache/ledger-settled.json");
    let ps = passes(&[
        pass("quote-check", "a1", "s", &json!({})),
        pass("glyph-check", "a1", "s", &json!({})),
        pass("record-format", "a1", "s", &json!({})),
        pass("intro-check", "a1", "s", &json!({})),
        pass("fix-check", "", "s", &json!({})),
    ]);
    let kept = json!({
        "a1#0#quote-check#5 s": {"path": t.to_string_lossy(), "stat": stat, "cells": {"wall": "kept"}},
        "a1#0#glyph-check#5 s": {"path": "/gone/x", "cells": {}},
        "a1#0#record-format#5 s": {"path": t.to_string_lossy(), "stat": [meta.len(), true], "cells": {"wall": "stale"}},
        "a1#0#intro-check#5 s": 3,
    });
    put(
        &env.cwd,
        ".git/l7r-cache/ledger-settled.json",
        &kept.to_string(),
    );
    let got = settled(&ps, &root, Some(&kept_file)).unwrap();
    assert_eq!(got[0]["wall"], json!("kept"));
    assert_eq!(got[1]["wall"], json!("5 s"));
    assert_eq!(got[2]["wall"], json!("12 s"));
    assert_eq!(
        got[3]["logged"],
        json!("5 s | 1k in (0k cached) / 0.5k out")
    );
    assert!(!got[4].contains_key("logged"));
    let now: Value = serde_json::from_str(&std::fs::read_to_string(&kept_file).unwrap()).unwrap();
    assert_eq!(
        now["a1#0#record-format#5 s"]["cells"]["wall"],
        json!("12 s")
    );
    let bad = |entry: Value| {
        put(
            &env.cwd,
            ".git/l7r-cache/ledger-settled.json",
            &json!({"a1#0#quote-check#5 s": entry}).to_string(),
        );
        settled(&ps[..1], &root, Some(&kept_file))
    };
    assert!(bad(json!({"path": 5})).unwrap_err().contains("TypeError"));
    assert!(bad(json!({"path": "/gone", "cells": [1]}))
        .unwrap_err()
        .contains("TypeError"));
    // no path is the working directory, which stands, but no stat matches it: costed again, as the Python did
    assert_eq!(
        bad(json!({"cells": {"wall": "here"}})).unwrap()[0]["wall"],
        json!("12 s")
    );
    put(&env.cwd, ".git/l7r-cache/ledger-settled.json", "[1]");
    assert_eq!(
        settled(&ps[..1], &root, Some(&kept_file)).unwrap()[0]["wall"],
        json!("12 s")
    );
    let blocked = env.cwd.join("dev/review-ledger.md/kept.json");
    assert_eq!(settled(&ps[..1], &root, Some(&blocked)).unwrap().len(), 1);
    assert!(!same_stat(&[json!(1)], Some(&json!(["1"]))));
}

#[test]
fn the_newest_transcript_its_segment_and_a_raise() {
    let (_d, env) = world("settle-find", &[]);
    let root = projects(&env);
    let older = root.join("q/t/subagents/agent-a1.jsonl");
    put(&root, "q/t/subagents/agent-a1.jsonl", "x\n");
    std::fs::File::options()
        .write(true)
        .open(&older)
        .unwrap()
        .set_modified(std::time::UNIX_EPOCH)
        .unwrap();
    put(&root, "q/t/subagents/notes.txt", "x");
    put(&root, "q/t/subagents/agent-bad.jsonl", "[1]\n");
    std::fs::create_dir_all(root.join("q/t/subagents/agent-dir.jsonl")).unwrap();
    let ps = passes(&[
        pass("quote-check", "a1", "s", &json!({"segment": "7x"})),
        pass(
            "quote-check",
            "a1",
            "s",
            &json!({"segment": "99999999999999999999999"}),
        ),
        pass("quote-check", "nobody", "s", &json!({})),
    ]);
    let got = settled(&ps, &root, None).unwrap();
    assert_eq!(got[0]["wall"], json!("12 s"));
    assert_eq!(got[1]["wall"], json!("5 s"));
    assert!(settled(&passes(&[pass("c", "bad", "s", &json!({}))]), &root, None).is_err());
    assert!(settled(&passes(&[pass("c", "dir", "s", &json!({}))]), &root, None).is_err());
}

#[test]
fn a_repeat_is_one_pass_and_a_row_answers_by_its_cells() {
    let ps = passes(&[
        pass("c", "a", "s", &json!({})),
        pass("c", "a", "other", &json!({})),
        pass("c", "a", "s", &json!({"segment": null, "wall": " 5   s"})),
        pass("c", "a", "s", &json!({"segment": null, "wall": "5 s"})),
    ]);
    let mut legacy = ps.clone();
    for p in &mut legacy[2..] {
        p.remove("segment");
    }
    assert_eq!(distinct(&legacy).len(), 2);
    let row = "| d | c | s | v | f | nothing | - | - | 9 s | t |\n| short |\n";
    let text = format!("{}{row}", super::super::tests::HEAD);
    let mut logged = ps[0].clone();
    logged.insert("wall".to_owned(), json!("9 s"));
    logged.insert("tokens".to_owned(), json!("u"));
    logged.insert("logged".to_owned(), json!("9 s | t"));
    assert!(unanswered(&[logged], &text).unwrap().is_empty());
    assert_eq!(unanswered(&ps[..1], &text).unwrap().len(), 1);
}
