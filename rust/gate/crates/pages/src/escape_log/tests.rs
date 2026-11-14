//! An escape taken, refused or not set, each logged entry read back in the guard log's own form.

use std::collections::HashMap;
use std::path::Path;

use serde_json::{json, Value};

use super::{cli, escape, log_at, Env};

fn entries(dir: &Path) -> Vec<Value> {
    let mut names: Vec<_> = std::fs::read_dir(dir)
        .map(|d| d.filter_map(Result::ok).map(|e| e.path()).collect())
        .unwrap_or_default();
    names.sort();
    names
        .iter()
        .map(|p| serde_json::from_str(&std::fs::read_to_string(p).unwrap()).unwrap())
        .collect()
}

fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

#[test]
fn an_escape_is_taken_refused_or_not_set_and_logged() {
    let d = l7r_gate_core::ci::fixtures::scratch("escape-log");
    let logs = d.join("log");
    let vars: HashMap<&str, String> = [
        ("GUARD_LOG_DIR", logs.to_string_lossy().into_owned()),
        ("CLAUDE_SESSION_ID", "s-1".to_owned()),
        ("GOOD", "  a reason worth \u{e9} logging ".to_owned()),
        ("THIN", "short".to_owned()),
    ]
    .into_iter()
    .collect();
    let var = |k: &str| vars.get(k).cloned();
    let env = Env {
        var: &var,
        cwd: d.join("clone-x"),
        command: "reserve-prefix.py registry k".to_owned(),
    };
    assert_eq!(escape("UNSET", "g", "r", None, &env), Ok(false));
    assert!(entries(&logs).is_empty());
    let ctx = json!({"key": "k", "reserved": 10});
    assert_eq!(
        escape("GOOD", "reserve", "key-cap", Some(&ctx), &env),
        Ok(true)
    );
    assert_eq!(
        escape("THIN", "reserve", "key-cap", None, &env),
        Err("THIN needs a REASON, not just a value - two words and eight characters; say why this case is legitimate".to_owned())
    );
    let got = entries(&logs);
    assert_eq!(got.len(), 2);
    let taken = got.iter().find(|e| e["event"] == "escaped").unwrap();
    assert_eq!(taken["detail"], "a reason worth \u{e9} logging");
    assert_eq!(taken["session"], "s-1");
    assert_eq!(taken["session_name"], "clone-x");
    assert_eq!(taken["context"], ctx);
    assert_eq!(taken["command"], "reserve-prefix.py registry k");
    let blocked = got.iter().find(|e| e["event"] == "blocked").unwrap();
    assert_eq!(
        (blocked["rule"].as_str(), blocked["context"].is_null()),
        (Some("THIN-no-reason"), true)
    );
    // the text is Python's `json.dumps(entry, indent=2)`: the non-ASCII escaped, the keys in its order
    let raw: Vec<String> = std::fs::read_dir(&logs)
        .unwrap()
        .map(|e| std::fs::read_to_string(e.unwrap().path()).unwrap())
        .collect();
    let text = raw.iter().find(|t| t.contains("escaped")).unwrap();
    assert!(text.starts_with("{\n  \"utc\": \"") && text.contains("worth \\u00e9 logging"));
}

#[test]
fn the_log_falls_back_to_home_and_never_fails() {
    let d = l7r_gate_core::ci::fixtures::scratch("escape-home");
    let home = d.to_string_lossy().into_owned();
    let vars: HashMap<&str, String> = [
        ("GUARD_LOG_DIR", String::new()),
        ("HOME", home.clone()),
        ("L7R_PAGE_SESSION", "page-1".to_owned()),
        ("CLAUDE_SESSION_ID", "s-1".to_owned()),
    ]
    .into_iter()
    .collect();
    let var = |k: &str| vars.get(k).cloned();
    let env = Env {
        var: &var,
        cwd: d.to_path_buf(),
        command: String::new(),
    };
    log_at(
        "g",
        "escaped",
        "why",
        "r",
        None,
        &env,
        std::time::SystemTime::now(),
    );
    let got = entries(&d.join(".claude/guard-log"));
    assert_eq!(got[0]["session"], "page-1");
    // nothing set: the session is unknown; a directory that cannot be made logs nothing and raises nothing
    std::fs::write(d.join("file"), "").unwrap();
    let none = |k: &str| (k == "GUARD_LOG_DIR").then(|| format!("{home}/file/sub"));
    let env = Env {
        var: &none,
        cwd: d.to_path_buf(),
        command: String::new(),
    };
    log_at(
        "g",
        "escaped",
        "why",
        "r",
        None,
        &env,
        std::time::SystemTime::now(),
    );
    let env = Env {
        var: &unset_var,
        cwd: d.join("x"),
        command: String::new(),
    };
    assert_eq!(escape("T", "g", "r", None, &env), Ok(false));
    let own = Env::of_process();
    assert!(!own.command.is_empty() && (own.var)("PATH").is_some());
}

#[test]
fn the_command_answers_by_its_exit() {
    let d = l7r_gate_core::ci::fixtures::scratch("escape-cli");
    let logs = d.join("log").to_string_lossy().into_owned();
    let vars: HashMap<&str, String> = [
        ("GUARD_LOG_DIR", logs.clone()),
        ("KEY_CAP_OK", "a deliberate larger load".to_owned()),
        ("THIN", "x".to_owned()),
    ]
    .into_iter()
    .collect();
    let var = |k: &str| vars.get(k).cloned();
    let env = Env {
        var: &var,
        cwd: d.to_path_buf(),
        command: "l7r-gate escape take".to_owned(),
    };
    let run = |a: &[&str]| cli(&args(a), &env);
    let base = ["--guard", "reserve", "--rule", "key-cap"];
    let ok = run(&[
        &[
            "--token",
            "KEY_CAP_OK",
            "--context",
            "{\"key\": \"k\"}",
            "--command",
            "reserve-prefix.py a",
        ],
        &base[..],
    ]
    .concat());
    assert_eq!((ok.code, ok.stderr.as_str()), (0, ""));
    assert_eq!(run(&[&["--token", "UNSET"], &base[..]].concat()).code, 1);
    let thin = run(&[&["--token", "THIN"], &base[..]].concat());
    assert_eq!(thin.code, 3);
    assert!(thin.stderr.starts_with("THIN needs a REASON"));
    for bad in [
        vec!["--bogus"],
        vec!["--token", "T"],
        vec![
            "--token",
            "T",
            "--guard",
            "g",
            "--rule",
            "r",
            "--context",
            "{",
        ],
    ] {
        let got = run(&bad);
        assert_eq!(got.code, 2, "{bad:?}");
        assert!(got.stderr.starts_with("usage: l7r-gate escape take"));
    }
    let got = entries(Path::new(&logs));
    let commands: Vec<&str> = got.iter().map(|e| e["command"].as_str().unwrap()).collect();
    assert!(
        commands.contains(&"reserve-prefix.py a") && commands.contains(&"l7r-gate escape take")
    );
}

pub(super) fn unset_var(_: &str) -> Option<String> {
    None
}
