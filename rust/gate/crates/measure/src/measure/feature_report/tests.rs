//! The report over a scratch feature (its git history, run log, event log, task starts and review passes), and its command line; the
//! differential holds it to the Python over the real ones (`diff.py`).

use std::path::Path;
use std::process::Command;

use l7r_gate_reviews::reviews::ledger_passes::Env;
use l7r_guard::shared::tempdir::TempDir;
use serde_json::{json, Value};

use super::{cli, report, Ask, Stop};

/// `git -C dir <args>` with a fixed author and date.
///
/// # Panics
///
/// Where git fails.
#[expect(
    clippy::must_use_candidate,
    reason = "most calls run git for its effect, not its output"
)]
pub fn git(dir: &Path, when: &str, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(dir)
        .args(["-c", "user.name=a", "-c", "user.email=a@b"])
        .args(args)
        .env("GIT_AUTHOR_DATE", when)
        .env("GIT_COMMITTER_DATE", when)
        .output()
        .unwrap();
    assert!(out.status.success(), "{args:?}");
    String::from_utf8(out.stdout).unwrap().trim().to_owned()
}

/// A file written, its directory made.
///
/// # Panics
///
/// Where it cannot be written.
pub fn put(dir: &Path, rel: &str, text: &str) {
    let p = dir.join(rel);
    std::fs::create_dir_all(p.parent().unwrap()).unwrap();
    std::fs::write(p, text).unwrap();
}

fn commit(dir: &Path, msg: &str, when: &str) -> String {
    git(dir, when, &["add", "-A"]);
    git(dir, when, &["commit", "-q", "--allow-empty", "-m", msg]);
    git(dir, when, &["rev-parse", "HEAD"])
}

fn at(hms: &str) -> String {
    format!("2026-11-01T{hms}Z")
}

/// The scratch feature `901-s`: two tasks, one ticked, a plan review BLOCKED then passed, three gate runs, a day of events.
///
/// # Panics
///
/// Where git or a write fails.
#[expect(
    clippy::too_many_lines,
    reason = "one fixture, its files and events in order"
)]
pub fn tree(tag: &str) -> TempDir {
    let d = crate::checks::scratch(tag);
    git(&d, "2026-11-01T08:00:00Z", &["init", "-q"]);
    let s = "specs/901-s";
    put(&d, &format!("{s}/spec.md"), "- Round 1 (2026-11-01): CHANGES REQUIRED - x\n- spec-fidelity, Mode 2, round 2 (2026-11-01): FAITHFUL. ok\n");
    put(&d, &format!("{s}/tasks.md"), "- [ ] T01\n- [ ] T02\n");
    put(
        &d,
        &format!("{s}/plan.md"),
        "### T01 part B (2026-11-01T08:05Z)\n",
    );
    put(
        &d,
        &format!("{s}/plan-review.json"),
        "{\"verdict\": \"BLOCKED\"}",
    );
    put(&d, "l7r/x.py", "a\n");
    put(&d, "dev/claims-index.json", "{}\n");
    let s1 = commit(&d, "Feature 901: the spec", "2026-11-01T08:05:00+00:00");
    put(
        &d,
        &format!("{s}/plan-review.json"),
        "{\"verdict\": \"PASS\"}",
    );
    put(&d, &format!("{s}/tasks.md"), "- [x] T01\n- [ ] T02\n");
    put(&d, "l7r/x.py", "a\nb\nc\n");
    let s2 = commit(&d, "901 T01: ticked", "2026-11-01T11:00:15-04:00");
    commit(&d, "Feature 9010 is not ours", "2026-11-01T11:51:00+00:00");
    for (i, (sha, utc, result)) in [
        (&s1, "2026-11-01T08:16:00Z", "failed: x"),
        (&s2, "2026-11-01T08:17:00Z", "failed: y"),
        (&s2, "2026-11-01T08:18:00Z", "passed"),
        (&s2, "2026-11-01T08:19:00Z", "already-verified"),
    ]
    .into_iter()
    .enumerate()
    {
        put(
            &d,
            &format!("dev/run-log/m/{i}.json"),
            &json!({"target": "done", "commit": &sha[..9], "utc": utc, "result": result})
                .to_string(),
        );
    }
    let ev = |v: Value| v.to_string();
    let events = [
        ev(json!({"t": at("08:00:00"), "sid": "s", "ev": "UserPromptSubmit", "gm": true})),
        ev(
            json!({"t": at("08:01:00"), "sid": "s", "ev": "PreToolUse", "tool": "Edit", "id": "e1", "cat": "edit", "path": "a.md", "old": "A", "new": "B"}),
        ),
        ev(
            json!({"t": at("08:01:01"), "sid": "s", "ev": "PostToolUse", "tool": "Edit", "id": "e1", "cat": "edit"}),
        ),
        ev(
            json!({"t": at("08:02:00"), "sid": "s", "ev": "PreToolUse", "tool": "Edit", "id": "e2", "cat": "edit", "path": "a.md", "old": "B", "new": "A"}),
        ),
        ev(
            json!({"t": at("08:02:01"), "sid": "s", "ev": "PostToolUse", "tool": "Edit", "id": "e2", "cat": "edit"}),
        ),
        ev(
            json!({"t": at("08:03:00"), "sid": "s", "ev": "PreToolUse", "tool": "Bash", "id": "b1", "cat": "other tool", "make": "map"}),
        ),
        ev(
            json!({"t": at("08:04:00"), "sid": "s", "ev": "PostToolUse", "tool": "Bash", "id": "b1", "cat": "other tool", "make": "map"}),
        ),
        ev(
            json!({"t": at("08:05:00"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "q1", "cat": "record check", "agent": "quote-check", "manifest": "/tmp/l7r-check/0105-quote-check/MANIFEST.md"}),
        ),
        ev(
            json!({"t": at("08:05:01"), "sid": "s", "ev": "PostToolUse", "tool": "Agent", "id": "q1", "aid": "qa1"}),
        ),
        ev(
            json!({"t": at("08:05:02"), "sid": "s", "ev": "SubagentStart", "aid": "qa1", "agent": "quote-check"}),
        ),
        ev(json!({"t": at("08:05:03"), "sid": "s", "ev": "Stop"})),
        ev(
            json!({"t": at("08:15:00"), "sid": "s", "ev": "SubagentStop", "aid": "qa1", "agent": "quote-check", "verdict": "clean"}),
        ),
        ev(
            json!({"t": at("08:16:00"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "q2", "cat": "record check", "agent": "quote-check", "manifest": "/tmp/l7r-check/0105-quote-check/MANIFEST.md"}),
        ),
        ev(
            json!({"t": at("08:16:01"), "sid": "s", "ev": "SubagentStop", "aid": "sf", "agent": "spec-fidelity", "verdict": "BLOCKED"}),
        ),
        ev(
            json!({"t": at("08:16:02"), "sid": "s", "ev": "PreToolUse", "tool": "Agent", "id": "g1", "cat": "review check", "agent": "glyph-check", "manifest": "/tmp/l7r-check/mill/MANIFEST.md"}),
        ),
        ev(json!({"t": at("10:00:00"), "sid": "s", "ev": "UserPromptSubmit", "gm": true})),
    ];
    put(
        &d,
        ".git/l7r-events/901-s.jsonl",
        &(events.join("\n") + "\n"),
    );
    put(
        &d,
        ".git/task-starts.jsonl",
        &[
            json!({"feature": "901-s", "task": "T01", "utc": at("08:00:30")}),
            json!({"feature": "901-s", "task": "T02", "utc": at("09:00:00")}),
            json!({"feature": "901-s", "task": "T03", "utc": at("12:00:00")}),
        ]
        .map(|v| v.to_string())
        .join("\n"),
    );
    put(&d, ".git/check-passes.jsonl", &json!({"check": "quote-check", "agent": "qa1", "wall": "60 s", "tokens": "2k in / 1k out"}).to_string());
    d
}

/// The review passes read from `dir`, with no transcripts to cost and the kept costs off.
#[must_use]
pub fn env(dir: &Path) -> Env {
    Env {
        cwd: dir.to_path_buf(),
        tree: dir.to_path_buf(),
        home: dir.join("home").display().to_string(),
        cache_off: true,
        claims_sheet: None,
    }
}

fn ask<'a>(root: &'a Path, feature: &'a str, env: &'a Env) -> Ask<'a> {
    Ask {
        root,
        feature,
        transcripts: &[],
        since: "",
        until: "",
        clones: Path::new("/nonexistent"),
        env,
    }
}

#[test]
fn a_feature_reports_where_its_time_went() {
    let d = tree("measure-report-full");
    let e = env(&d);
    let (text, dir) = report(&ask(&d, "901", &e)).ok().unwrap();
    assert_eq!(dir, d.join("specs/901-s"));
    for want in [
        "Written by `make feature-report F=901` from 16 events (2026-11-01T08:00 to 2026-11-01T10:00 UTC), 2 commits",
        "| idle (over an hour) | 1 h 44 min | - |",
        "| waiting: quote-check | 10 min | 62% |",
        "## Inside `other tool` (the five largest)",
        "| make map | 1 min |",
        "| quote-check | 2 | clean 1 |",
        "| quote-check | 0105 | 2 |",
        "- gates: already-verified 1, passed 1, red 2",
        "- spec rounds: CHANGES REQUIRED 1, FAITHFUL 1",
        "- plan reviews BLOCKED: 1 recorded in commits, 1 returned",
        "- reversals (A -> B -> A): 1 - a.md 08:02",
        "- 08:02 reversal:a.md",
        "- 08:17 red-gate",
        "| T01 | 08:00-08:16 | spec-fidelity BLOCKED | 5 | 6 | 10 | 0 | quote-check x1 (10 min) |",
        "| T01 | 7 h 00 min | 16 min | 6 h 44 min | 1 | 16, 404 |",
        "| T02 | 1 h 00 min (open) |",
        "| T01 | 08:05 | part B written | |",
        "## What each check cost, per changed line (3 lines)",
        "| quote-check | 1 | 1 min | 2k | 1.0k | 0.333 | 0.7k |",
    ] {
        assert!(text.contains(want), "{want}\n{text}");
    }
}

#[test]
fn a_feature_with_nothing_logged_still_reports() {
    let d = tree("measure-report-empty");
    std::fs::create_dir_all(d.join("specs/902-e")).unwrap();
    let e = env(&d);
    let (text, _) = report(&ask(&d, "902", &e)).ok().unwrap();
    for want in [
        "from 0 events (no event log",
        "| - | - | - |",
        "- gates: none recorded",
        "- none",
        "cascade ratio 0.00",
        "tasks ticked: 0 of 0",
    ] {
        assert!(text.contains(want), "{want}\n{text}");
    }
    assert!(!text.contains("## Each task"));
    // a start but no events and no tick: the task's span is empty, so no phases and no skeleton rows
    std::fs::write(d.join(".git/l7r-events/901-s.jsonl"), "").unwrap();
    std::fs::write(
        d.join(".git/task-starts.jsonl"),
        json!({"feature": "901-s", "task": "T03", "utc": at("12:00:00")}).to_string(),
    )
    .unwrap();
    let (text, _) = report(&ask(&d, "901", &e)).ok().unwrap();
    assert!(text.contains("## Each task's phases (plan D32)"));
    assert!(!text.contains("| T03 | 12:"));
    assert!(
        matches!(report(&ask(&d, "903", &e)), Err(Stop::Exit(m)) if m == "feature-report: no specs/903-* directory")
    );
    assert!(matches!(report(&ask(&d, "x", &e)), Err(Stop::Raised(_))));
    // the passes raise where the pass log is not UTF-8, as `ledger-passes` exited 1 under the Python's `check=True`
    std::fs::write(d.join(".git/check-passes.jsonl"), b"\xff").unwrap();
    assert!(matches!(report(&ask(&d, "902", &e)), Err(Stop::Raised(_))));
}

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

#[test]
fn the_command_line_prints_writes_and_refuses() {
    let d = tree("measure-report-cli");
    let e = env(&d);
    let root = d.display().to_string();
    let none = Path::new("/nonexistent");
    assert_eq!(cli(&[], &e, none).code, 2);
    assert_eq!(cli(&args(&["901", "--bogus"]), &e, none).code, 2);
    let missing = cli(&args(&["--root", &root, "903"]), &e, none);
    assert_eq!(
        (missing.code, missing.stderr.as_str()),
        (1, "feature-report: no specs/903-* directory\n")
    );
    assert!(cli(&args(&["--root", &root, "x"]), &e, none)
        .stderr
        .starts_with("Traceback"));
    let printed = cli(
        &args(&[
            "--root",
            &root,
            "901",
            "--since",
            "2026-11-01T08:00",
            "--until",
            "2026-11-01T09",
            "--transcript",
            "/nonexistent",
        ]),
        &e,
        none,
    );
    assert_eq!(printed.code, 1);
    let window = cli(
        &args(&[
            "--root",
            &root,
            "901",
            "--since",
            "2026-11-01T08:00",
            "--until",
            "2026-11-01T09",
        ]),
        &e,
        none,
    );
    assert_eq!(window.code, 0);
    let printed = cli(&args(&["--root", &root, "901"]), &e, none);
    assert_eq!(printed.code, 0);
    assert!(!d.join("specs/901-s/report.md").exists());
    let written = cli(&args(&["--root", &root, "901", "--write"]), &e, none);
    assert!(written
        .stdout
        .ends_with("\nfeature-report: written to specs/901-s/report.md\n"));
    assert!(d.join("specs/901-s/report.md").is_file());
    std::fs::write(d.join("specs/904-file.md"), "").unwrap();
    let failed = cli(&args(&["--root", &root, "904", "--write"]), &e, none);
    assert_eq!(failed.code, 1);
    assert!(failed.stdout.starts_with("# Feature report - 904-file.md"));
}
