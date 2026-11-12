//! A scratch repository's fixes, their commits, tools and readings, and the command line.

use std::path::Path;
use std::process::Command;

use serde_json::json;

use super::super::tool_yield::tests::{put, repo};
use super::*;

fn git_at(r: &Path, args: &[&str]) -> String {
    let out = Command::new("git")
        .arg("-C")
        .arg(r)
        .args(args)
        .env("GIT_AUTHOR_DATE", "2026-01-01T12:00:00Z")
        .env("GIT_COMMITTER_DATE", "2026-01-01T12:00:00Z")
        .env("GIT_AUTHOR_NAME", "t")
        .env("GIT_AUTHOR_EMAIL", "t@t")
        .env("GIT_COMMITTER_NAME", "t")
        .env("GIT_COMMITTER_EMAIL", "t@t")
        .output()
        .unwrap();
    assert!(out.status.success());
    String::from_utf8(out.stdout).unwrap().trim().to_owned()
}

fn commit(r: &Path, message: &str) -> String {
    git_at(r, &["add", "-A"]);
    git_at(r, &["commit", "-q", "--allow-empty", "-m", message]);
    git_at(r, &["rev-parse", "--short", "HEAD"])
}

/// The fixture repository with its history: a base, a fix to `util.sh` naming hour 2, a landing of `lint.py` naming it, a records-only
/// commit naming hour 3.
pub fn history(r: &Path) -> String {
    repo(r);
    git_at(r, &["init", "-q"]);
    commit(r, "base");
    put(r, "scripts/util.sh", "1\n");
    let fix = commit(r, "fix for hour:9-x@2 here");
    put(r, "scripts/tools/lint.py", "1\n");
    commit(r, "Tooling from clone: hour:9-x@2");
    put(r, "specs/009-x/notes.md", "1\n");
    commit(r, "records for hour:9-x@3");
    put(
        r,
        "Makefile",
        "done: lint\nlint:\n\t@python3 scripts/tools/lint.py\nbuild:\n\t@sh scripts/util.sh x\n",
    );
    commit(r, "the build recipe for hour:9-x@7");
    fix
}

fn arbiter(r: &Path, fix: &str) {
    let rows = [
        json!({"trigger": "hour:9-x@2", "tooling_fix": "a", "fix_minutes": 5, "utc": "2026-01-01T00:00:00Z"}),
        json!({"fix_of": "hour:9-x@2", "status": "done", "utc": "2026-01-02T00:00:00Z", "note": "", "test": "scripts/util.sh"}),
        json!({"trigger": "hour:9-x@3", "tooling_fix": "b", "fix_minutes": 2.5}),
        json!({"fix_of": "hour:9-x@3", "status": "done", "utc": "2026-01-02T00:00:00Z", "note": "deadbeef0 made make lint and util.sh and helper.run() better"}),
        json!({"trigger": "hour:9-x@4", "tooling_fix": "c"}),
        json!({"tooling_fix": "no trigger"}),
        json!({"trigger": "odd^.(x)", "tooling_fix": "g"}),
        json!({"fix_of": "odd^.(x)", "status": "done", "utc": "2026-01-02T00:00:00Z", "note": "nothing"}),
        json!({"trigger": "hour:9-x@5", "tooling_fix": "d"}),
        json!({"fix_of": "hour:9-x@5", "status": "done", "utc": "2026-01-02T00:00:00Z", "note": format!("{fix} the fix")}),
        json!({"trigger": "hour:9-x@6", "tooling_fix": "e"}),
        json!({"fix_of": "hour:9-x@6", "status": "declined", "utc": "2026-01-02T00:00:00Z"}),
        json!({"trigger": "hour:9-x@7", "tooling_fix": "f"}),
        json!({"fix_of": "hour:9-x@7", "status": "done", "utc": "2026-01-02T00:00:00Z", "note": "it"}),
        json!({"fix_of": "hour:9-x@7", "status": "done", "utc": "2026-01-03T00:00:00Z", "note": "it"}),
    ];
    let text: String = rows.iter().map(|v| v.to_string() + "\n").collect();
    put(r, "specs/009-x/arbiter.jsonl", &text);
}

#[test]
fn a_fix_takes_its_settling_and_its_commits() {
    let r = crate::checks::scratch("fy-commits");
    let fix = history(&r);
    arbiter(&r, &fix);
    let fx = fixes(&lines(&r.join("specs/009-x/arbiter.jsonl")).unwrap());
    assert_eq!(fx.len(), 8);
    assert_eq!(fx[2]["status"], "open");
    assert_eq!(fx[7]["settled"], "2026-01-03T00:00:00Z");
    assert!(candidates(&r, &fx[4]).unwrap().is_empty());
    let two = candidates(&r, &fx[0]).unwrap();
    assert!(two.len() >= 2);
    assert_eq!(two[0], fix);
    let tools = tools_of_fix(&r, &fx[0]).unwrap();
    assert!(tools.contains(&("guard".to_owned(), "foo".to_owned())));
    let three = tools_of_fix(&r, &fx[1]).unwrap();
    assert!(three.contains(&("target".to_owned(), "lint".to_owned())));
    assert!(three.contains(&("guard".to_owned(), "foo".to_owned())));
    assert_eq!(candidates(&r, &fx[5]).unwrap()[0], fix);
    assert!(tools_of_fix(&r, &fx[7])
        .unwrap()
        .contains(&("target".to_owned(), "build".to_owned())));
    let mut none = Row::new();
    none.insert("note".to_owned(), json!("make nosuch"));
    assert!(candidates(&r, &none).unwrap().is_empty());
    assert!(tools_of_fix(&r, &none).unwrap().is_empty());
    assert_eq!(
        named_files(&r, "util.sh, helper.run"),
        ["scripts/hooks/lib/helper.py", "scripts/util.sh"]
    );
    put(&r, "scripts/__pycache__/util.py", "");
    assert_eq!(named_files(&r, "util.py"), ["scripts/util.sh"]);
}

#[test]
fn the_report_reads_each_fix() {
    let r = crate::checks::scratch("fy-report");
    let fix = history(&r);
    arbiter(&r, &fix);
    let made = super::super::turn_time::ts_of(&json!("2026-01-02T00:00:00Z")).unwrap();
    let text = report(
        &r,
        &r.join("specs/009-x"),
        made + 3.0 * DAY,
        &r.join("guard-log"),
    )
    .unwrap();
    assert!(text.contains("| hour:9-x@2 | 2026-01-02 | 5 | too new to say |"));
    assert!(text.contains("| hour:9-x@4 | - | - | not made (open) | - |"));
    assert!(text.contains("| hour:9-x@6 | - | - | not made (declined) | - |"));
    assert!(text.contains("| hour:9-x@3 | 2026-01-02 | 2.5 |"));
    let later = report(
        &r,
        &r.join("specs/009-x"),
        made + 300.0 * DAY,
        &r.join("guard-log"),
    )
    .unwrap();
    assert!(later.contains("| hour:9-x@3 | 2026-01-02 | 2.5 | doing something |"));
    assert!(later.contains("| odd^.(x) | 2026-01-02 | - | no outcome record (no tool found in its settling commit) | - |"));
    put(&r, "specs/010-y/arbiter.jsonl", "{}\n");
    assert_eq!(
        report(&r, &r.join("specs/010-y"), 0.0, &r).unwrap(),
        "(no tooling fix ruled)\n"
    );
    put(&r, "specs/011-z/arbiter.jsonl", "{\"trigger\": \"t\", \"tooling_fix\": 1}\n{\"fix_of\": \"t\", \"status\": \"done\", \"utc\": \"bad\"}\n");
    assert!(report(&r, &r.join("specs/011-z"), 0.0, &r).is_err());
}

#[test]
fn the_readings_in_their_order() {
    let tally = |kind: &str, first: f64, hits: usize, misses: usize, recorded: bool| {
        let mut t = Tally::new(kind, "n");
        t.use_at(first);
        for _ in 0..hits {
            t.hit(first, true);
        }
        for _ in 0..misses {
            t.miss(first, true);
        }
        t.outcome_record = recorded;
        t
    };
    let mut fix = Row::new();
    fix.insert("status".to_owned(), json!("done"));
    fix.insert("settled".to_owned(), json!("1970-01-02T00:00:00Z"));
    let key = ("guard".to_owned(), "n".to_owned());
    let read = |t: &Tally, now: f64| verdict(&fix, &[(&key, t)], now).unwrap()["reading"].clone();
    let now = 100.0 * DAY;
    assert_eq!(read(&tally("guard", DAY, 1, 1, true), now), "doing nothing");
    assert_eq!(
        read(&tally("guard", DAY, 2, 1, true), now),
        "doing something"
    );
    assert_eq!(
        read(&tally("guard", DAY, 0, 0, false), now),
        "no outcome record"
    );
    assert_eq!(
        read(&tally("guard", DAY, 0, 0, true), 4.0 * DAY),
        "too new to say"
    );
    assert_eq!(
        read(&tally("guard", 95.0 * DAY, 0, 0, true), now),
        "record too new"
    );
    assert_eq!(
        read(&tally("guard", DAY, 0, 0, true), 200.0 * DAY),
        "doing nothing"
    );
    assert_eq!(
        verdict(&Row::new(), &[], 0.0).unwrap()["reading"],
        "not made (None)"
    );
    let check = ("check".to_owned(), "n".to_owned());
    let row = verdict(
        &fix,
        &[(&check, &tally("check", DAY, 0, 0, true))],
        200.0 * DAY,
    )
    .unwrap();
    let text = table(&[row]);
    assert!(text.contains("check n (first seen 1970-01-02): 1 / 0 / no outcome record"));
    assert_eq!(day(-5.0), "1970-01-01");
}

#[test]
fn a_path_resolves_as_pathlib_resolves_it() {
    let r = crate::checks::scratch("fy-resolve");
    std::fs::create_dir_all(r.join("real/sub")).unwrap();
    std::os::unix::fs::symlink(r.join("real"), r.join("link")).unwrap();
    std::os::unix::fs::symlink(r.join("gone"), r.join("dangling")).unwrap();
    let real = std::fs::canonicalize(r.join("real")).unwrap();
    assert_eq!(resolve(&r.join("link/sub/../x/./y")), real.join("x/y"));
    assert!(resolve(&r.join("dangling")).ends_with("dangling"));
    assert!(resolve(Path::new("rel")).is_absolute());
}

#[test]
fn the_command_line() {
    let r = crate::checks::scratch("fy-cli");
    let fix = history(&r);
    arbiter(&r, &fix);
    put(&r, "specs/0091-other/x", "");
    let root = r.display().to_string();
    let ask = |words: &[&str]| {
        cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            &r,
        )
    };
    assert_eq!(ask(&[]).code, 2);
    assert_eq!(ask(&["9", "--bogus"]).code, 2);
    let many = ask(&["009", "--root", &root]);
    assert_eq!(
        (many.code, many.stderr.as_str()),
        (2, "fix-yield: no single specs/009* directory\n")
    );
    let ok = ask(&["009-", "--root", &root]);
    assert!(ok.code == 0 && ok.stdout.starts_with("| fix (trigger) |"));
    put(&r, "specs/012-bad/arbiter.jsonl", "{\"trigger\": \"t\", \"tooling_fix\": 1}\n{\"fix_of\": \"t\", \"status\": \"done\", \"utc\": \"bad\"}\n");
    assert_eq!(ask(&["012", "--root", &root]).code, 1);
}
