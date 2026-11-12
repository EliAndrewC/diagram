//! `ledger-owed` end to end over a scratch repository, its pass log, a projects directory of transcripts and a gate tree whose usage
//! log records a write; `world` is shared with the submodules' tests.

use std::path::{Path, PathBuf};

use serde_json::json;

use super::super::tests::{dir, put, sh};
use super::{cli, passes_cli, resolve, Env};

pub(super) const HEAD: &str = "## Review checks, measured (feature 294 on)\n\n| date | check | subject | verdict | finding | class | author missed? | acted on | wall | tokens |\n|---|---|---|---|---|---|---|---|---|---|\n";

pub(super) fn args(words: &[&str]) -> Vec<String> {
    words.iter().map(|w| (*w).to_owned()).collect()
}

/// A transcript of one return: `prompt`, then a reply of `reply` 12 seconds on with 1,650 output tokens over two streamed lines.
pub(super) fn transcript(prompt: &serde_json::Value, reply: &str) -> String {
    [
        json!({"type": "user", "timestamp": "2026-11-01T00:00:00Z", "message": {"role": "user", "content": prompt}}),
        json!({"requestId": "r", "timestamp": "2026-11-01T00:00:07Z", "message": {"usage": {"input_tokens": 1000, "output_tokens": 1}, "content": [{"type": "text", "text": reply}]}}),
        json!({"requestId": "r", "timestamp": "2026-11-01T00:00:12Z", "message": {"usage": {"input_tokens": 1000, "output_tokens": 1650}, "content": [{"type": "text", "text": reply}]}}),
    ]
    .iter()
    .map(ToString::to_string)
    .collect::<Vec<_>>()
    .join("\n")
}

/// A log line read as the log reader reads it: every value its `str()`.
pub(super) fn as_pass(line: &str) -> super::Pass {
    serde_json::from_str::<serde_json::Value>(line)
        .unwrap()
        .as_object()
        .unwrap()
        .iter()
        .map(|(k, v)| (k.clone(), json!(crate::record::bundle::py_str(v))))
        .collect()
}

/// A pass's log line.
pub(super) fn pass(check: &str, agent: &str, subject: &str, extra: &serde_json::Value) -> String {
    let mut v = json!({"date": "2026-11-01", "check": check, "subject": subject, "agent": agent, "segment": 0, "wall": "5 s", "tokens": "1k in (0k cached) / 0.5k out"});
    for (k, x) in extra.as_object().unwrap() {
        v[k] = x.clone();
    }
    v.to_string()
}

/// The scratch world: `<d>/repo` (a repository with its ledger, the feature's records and the pass log), `<d>/tree` (the gate's tree,
/// a repository), `<d>/home/.claude/projects` (the transcripts).
pub(super) fn world(tag: &str, log: &[String]) -> (l7r_guard::shared::tempdir::Held<PathBuf>, Env) {
    let d = dir(&format!("ledger-{tag}"));
    let (repo, tree) = (d.join("repo"), d.join("tree"));
    for r in [&repo, &tree] {
        std::fs::create_dir_all(r).unwrap();
        sh(r, "git init -q");
    }
    put(&repo, "dev/review-ledger.md", HEAD);
    put(&repo, "specs/449-x/plan-review.json", &json!({"tasks": {"T6": {"reviewed": "2026-11-01"}}, "blocks": {"b": {"reviewed": "2026-11-02"}, "c": 1}}).to_string());
    put(
        &repo,
        "specs/449-x/implementation-check.md",
        "- 0094: a claim\n",
    );
    put(&repo, "specs/449-x/briefs/a.md", "SECTION=0077\n");
    put(
        &repo,
        concat!("research/questions/", "0094-a.html"),
        "cites smith-1990",
    );
    put(
        &repo,
        ".specify/feature.json",
        r#"{"feature_directory": "specs/449-x"}"#,
    );
    put(
        &repo,
        "sheet.md",
        "| feature | questions |\n| 449 | 0123 |\n",
    );
    put(
        &repo,
        ".git/check-passes.jsonl",
        &format!("{}\n", log.join("\n")),
    );
    let sub = d.join("home/.claude/projects/p/s/subagents");
    put(
        &sub,
        "agent-a1.jsonl",
        &transcript(&json!("Check /tmp/l7r-check/q1/ please"), "PASS - fine"),
    );
    put(
        &sub,
        "agent-a3.jsonl",
        &transcript(
            &json!("MODE 4: PLAN REVIEW of feature 449-x task T5"),
            "CLEAR recorded for T5",
        ),
    );
    put(
        &sub,
        "workflows/run/agent-w1.jsonl",
        &transcript(
            &json!([{"type": "text", "text": "bundle specs/449-x/b"}]),
            "x",
        ),
    );
    let env = Env {
        cwd: repo.clone(),
        tree,
        home: d.join("home").to_string_lossy().into_owned(),
        cache_off: false,
        claims_sheet: Some("sheet.md".to_owned()),
    };
    (d, env)
}

fn ledger(env: &Env) -> String {
    std::fs::read_to_string(env.cwd.join("dev/review-ledger.md")).unwrap()
}

fn usage_lines(env: &Env) -> String {
    std::fs::read_to_string(env.tree.join(".git/tool-usage.jsonl")).unwrap_or_default()
}

const L: [&str; 2] = ["--ledger", "dev/review-ledger.md"];

#[test]
fn the_owed_passes_are_reported_refused_and_kept() {
    let log = [
        pass(
            "quote-check",
            "a1",
            "Check /tmp/l7r-check/q1/ please",
            &json!({}),
        ),
        pass("glyph-check", "", "no agent", &json!({"segment": null})),
        "not json".to_owned(),
    ];
    let (_d, env) = world("report", &log);
    let got = cli(&args(&L), &env);
    assert_eq!(got.code, 0);
    assert!(got
        .stdout
        .starts_with("ledger-owed: 2 check pass(es) have no row"));
    assert!(got.stdout.contains("| 2026-11-01 | quote-check | Check /tmp/l7r-check/q1/ please | ? | ? | ? | ? | ? | 12 s | 1k in (0k cached) / 1.6k out |"));
    let kept = std::fs::read_to_string(env.cwd.join(".git/l7r-cache/ledger-settled.json")).unwrap();
    assert!(kept.contains("\"a1#0#quote-check#5 s\": {\"path\": "));
    let refused = cli(&args(&[&L[..], &["--refuse"]].concat()), &env);
    assert_eq!((refused.code, refused.stdout.as_str()), (1, ""));
    assert!(refused.stderr.contains("LEDGER_ROWS_OK"));
    put(&env.cwd, "dev/review-ledger.md", &format!("{HEAD}| 2026-11-01 | quote-check | s | PASS | - | nothing | - | nothing | 12 s | 1k in (0k cached) / 1.6k out |\n| 2026-11-01 | glyph-check | s | PASS | - | nothing | - | nothing | 5 s | 1k in (0k cached) / 0.5k out |\n"));
    assert_eq!(cli(&args(&L), &env).stdout, "");
    let passes: serde_json::Value = serde_json::from_str(&passes_cli(&[], &env).stdout).unwrap();
    assert_eq!(passes[0]["wall"], json!("12 s"));
}

#[test]
fn a_write_traces_its_passes_to_the_feature_and_records_the_step() {
    let log = [
        pass(
            "quote-check",
            "a1",
            "Check /tmp/l7r-check/q1/ please",
            &json!({}),
        ),
        pass(
            "quote-check",
            "w1",
            "[Workflow harness - computed task] x",
            &json!({}),
        ),
        pass(
            "quote-check",
            "zz",
            "question 0123 here",
            &json!({"wall": "6 s"}),
        ),
        pass(
            "quote-check",
            "zz",
            "about feature 500-other",
            &json!({"segment": 1, "wall": "7 s"}),
        ),
    ];
    // a1's logged wall differs from w1's, so w1's row does not answer a1 by a1's logged cells
    let mut log = log;
    log[0] = log[0].replace("\"wall\":\"5 s\"", "\"wall\":\"4 s\"");
    let (_d, env) = world("write", &log);
    let got = cli(
        &args(&[&L[..], &["--write", "specs/449-x/checks.md"]].concat()),
        &env,
    );
    assert_eq!(got.stdout, "ledger-owed: 2 row(s) written for feature 449; 2 pass(es) not traced to it stay owed for the feature that ran them\n");
    assert!(ledger(&env).contains("| 2026-11-01 | quote-check | [Workflow harness - computed task] x | see reply | - | judgment | - | applied or filed as specs/449-x/checks.md records | 5 s |"));
    assert!(usage_lines(&env)
        .contains("\"tool\": \"ledger-owed-write\", \"kind\": \"step\", \"outcome\": \"changed\""));
    let all = cli(&args(&[&L[..], &["--write", "the brief"]].concat()), &env);
    assert_eq!(
        all.stdout,
        "ledger-owed: 2 row(s) written for every session\n"
    );
    assert!(ledger(&env).contains("| q1 | PASS | PASS - fine | nothing |"));
    let none = cli(
        &args(&[&L[..], &["--write", "x", "--session", "s"]].concat()),
        &env,
    );
    assert_eq!(none.stdout, "ledger-owed: 0 row(s) written for s\n");
    assert!(usage_lines(&env).contains("\"outcome\": \"unchanged\""));
}

#[test]
fn a_sessions_write_takes_only_its_own_agents() {
    let log = [
        pass("quote-check", "a1", "one", &json!({})),
        pass("quote-check", "gone", "two", &json!({})),
    ];
    let (_d, env) = world("session", &log);
    let got = cli(
        &args(&[&L[..], &["--write", "specs/449-x/b", "--session", "s"]].concat()),
        &env,
    );
    assert_eq!(got.stdout, "ledger-owed: 1 row(s) written for s; 1 pass(es) not traced to it stay owed for the feature that ran them\n");
}

#[test]
fn a_plan_review_that_recorded_itself_gets_its_row() {
    let log = [
        pass(
            "spec-fidelity",
            "a3",
            "MODE 4: PLAN REVIEW of feature 449-x task T5",
            &json!({}),
        ),
        pass(
            "spec-fidelity",
            "zz",
            "MODE 4: PLAN REVIEW of feature 449-x task T6",
            &json!({}),
        ),
        pass(
            "spec-fidelity",
            "zz",
            "MODE 4: PLAN REVIEW of feature 449-x blocks",
            &json!({"segment": 1}),
        ),
        pass("quote-check", "a1", "not a plan review", &json!({})),
    ];
    let (_d, env) = world("plan", &log);
    let got = cli(&args(&[&L[..], &["--write-plan-reviews"]].concat()), &env);
    assert_eq!(got.stdout, "ledger-owed: 2 plan review row(s) written\n");
    assert!(ledger(&env).contains("| CLEAR | CLEAR recorded for T5 | judgment | - | applied or filed as the plan-verdict record (make plan-verdict) records |"));
    let again = cli(&args(&[&L[..], &["--write-plan-reviews"]].concat()), &env);
    assert_eq!(again.stdout, "ledger-owed: 0 plan review row(s) written\n");
}

#[test]
fn what_the_python_raised_fails_the_run() {
    let (_d, env) = world(
        "raise",
        &[json!({"check": "glyph-check", "wall": "5 s"}).to_string()],
    );
    let got = cli(&args(&L), &env);
    assert_eq!(got.code, 1);
    assert!(got.stderr.starts_with(
        "Traceback (most recent call last):\n  l7r-gate reviews ledger-owed\nKeyError: 'tokens'"
    ));
    let (_d, env) = world("nodir", &[pass("quote-check", "a1", "x", &json!({}))]);
    assert_eq!(
        cli(&args(&["--ledger", "no/dir/l.md", "--write", "x"]), &env).code,
        1
    );
    std::fs::write(env.cwd.join("dev/review-ledger.md"), [0xff_u8]).unwrap();
    assert_eq!(cli(&args(&L), &env).code, 1);
    std::fs::write(env.cwd.join(".git/check-passes.jsonl"), [0xff_u8]).unwrap();
    assert_eq!(passes_cli(&[], &env).code, 1);
    assert_eq!(cli(&args(&["--bogus"]), &env).code, 2);
    assert_eq!(passes_cli(&args(&["x"]), &env).code, 2);
    let (_d, env) = world("costraise", &[pass("quote-check", "bad", "x", &json!({}))]);
    put(
        Path::new(&env.home),
        ".claude/projects/p/s/subagents/agent-bad.jsonl",
        "[1]\n",
    );
    assert!(cli(&args(&L), &env).stderr.contains("no object"));
    let mut full = std::fs::File::options()
        .append(true)
        .open("/dev/full")
        .unwrap();
    assert!(super::write_row(&mut full, "x").is_err());
    assert!(super::cache_off(Some("1")) && !super::cache_off(Some("0")) && !super::cache_off(None));
}

#[test]
fn the_log_and_the_kept_costs_follow_the_working_directory() {
    let (d, mut env) = world("where", &[pass("quote-check", "a1", "x", &json!({}))]);
    env.cache_off = true;
    assert!(cli(&args(&L), &env).stdout.contains("1 check pass(es)"));
    assert!(!env.cwd.join(".git/l7r-cache").exists());
    let other = d.join("plain");
    std::fs::create_dir_all(&other).unwrap();
    put(
        &d,
        "log.jsonl",
        &format!("{}\n", pass("quote-check", "a1", "x", &json!({}))),
    );
    let away = Env {
        cwd: PathBuf::from("/"),
        tree: other,
        cache_off: false,
        ..world("where2", &[]).1
    };
    assert_eq!(away.kept_file(), None);
    assert_eq!(
        away.default_log(),
        PathBuf::from("/.git/check-passes.jsonl")
    );
    let log = d.join("log.jsonl").to_string_lossy().into_owned();
    let ledger = env
        .cwd
        .join("dev/review-ledger.md")
        .to_string_lossy()
        .into_owned();
    let got = cli(
        &args(&["--ledger", &ledger, "--log", &log, "--write", "w"]),
        &away,
    );
    assert_eq!(
        got.stdout,
        "ledger-owed: 1 row(s) written for every session\n"
    );
    let process = Env::of_process();
    assert!(process.cwd.is_absolute());
}

#[test]
fn a_path_resolves_as_pathlib_resolves_it() {
    let d = dir("ledger-resolve");
    let real = std::fs::canonicalize(&*d).unwrap();
    assert_eq!(resolve(&d.join("a/b")), real.join("a/b"));
    assert_eq!(resolve(&d.join("a/..")), real);
    assert_eq!(resolve(Path::new("")), PathBuf::new());
}
