//! The tools of a scratch repository and their numbers; `repo` is the fixture `fix_yield`'s and the step-back's tests build on.

use std::path::Path;

use super::*;

/// A file written under `root`, its directories made.
///
/// # Panics
///
/// Where the file cannot be written.
pub fn put(root: &Path, rel: &str, text: &str) {
    let path = root.join(rel);
    std::fs::create_dir_all(path.parent().unwrap()).unwrap();
    std::fs::write(path, text).unwrap();
}

/// A repository with one tool of each kind and a record of each.
///
/// # Panics
///
/// Where a file cannot be written.
pub fn repo(r: &Path) {
    put(
        r,
        ".claude/settings.json",
        r#"{"hooks":{"PreToolUse":[{"hooks":[{"command":"scripts/hooks/foo-hooks.sh x"}]}]}}"#,
    );
    put(
        r,
        "scripts/hooks/foo-hooks.sh",
        "python3 scripts/hooks/lib/helper.py\nrun util.sh\n",
    );
    put(r, "scripts/hooks/lib/helper.py", "");
    put(r, "scripts/util.sh", "");
    put(
        r,
        "scripts/gates/gatey.py",
        "if __name__ == \"__main__\":\n    pass\n",
    );
    put(r, "scripts/tools/lint.py", "");
    put(
        r,
        "Makefile",
        "done: lint\nlint:\n\t@python3 scripts/tools/lint.py\nbuild:\n\t@sh scripts/util.sh\n",
    );
    put(r, ".claude/agents/rev.md", "");
    put(r, ".claude/agents/silent.md", "");
    put(
        r,
        "scripts/tool-registry.json",
        r#"{"tools":{"stepper":{"kind":"step","what":"scripts/step.py does it"},"hooky":{"kind":"hook"},"plain":{}}}"#,
    );
    put(
        r,
        "dev/review-ledger.md",
        "x\n| date | check | subject | verdict | a | b | c | acted |\n|---|\n| 2026-01-05 | rev | s | BLOCK | a | MISSED-BY-REVIEWER | c | declined |\n| 2026-01-01 | rev | s | 0 findings | a | b | c | fixed |\n| 2025-01-01 | rev | s | BLOCK | a | b | c | x |\n| 2026-01-02 | other | s | 1 FIX | a | b | c | x |\n| 2026-01-01 | other | s | x | a | b | c | x |\n| nodate | rev | s | BLOCK | a | b | c | x |\n",
    );
    put(r, "specs/001-x/arbiter.jsonl", "{\"ruling\": \"change-route\", \"utc\": \"2026-01-03T00:00:00Z\"}\n{\"ruling\": \"continue\", \"utc\": \"2026-01-03T00:00:00Z\", \"tooling_fix\": \"x\"}\n{\"utc\": \"2026-01-03T00:00:00Z\"}\n");
    put(
        r,
        "dev/bypass-log/d/a.json",
        r#"{"target": "lint now", "utc": "2026-01-04T00:00:00Z"}"#,
    );
    put(
        r,
        "dev/bypass-log/d/b.json",
        r#"{"target": "", "utc": "2026-01-04T00:00:00Z"}"#,
    );
    put(r, "dev/bypass-log/d/c.json", "nope");
    put(r, "dev/bypass-log/d/e.json", r#"{"target": "nosuch"}"#);
    std::fs::create_dir_all(r.join("dev/bypass-log/d/g.json")).unwrap();
    put(
        r,
        ".git/tool-usage.jsonl",
        "{\"utc\": \"2026-01-02T00:00:00Z\", \"kind\": \"check\", \"tool\": \"gatey\", \"outcome\": \"refused\"}\n{\"utc\": \"2026-01-03T00:00:00Z\", \"kind\": \"target\", \"tool\": \"lint\", \"outcome\": \"ran\"}\n{\"utc\": \"2026-01-03T00:00:00Z\", \"kind\": \"hook\", \"tool\": \"foo\"}\n{\"utc\": \"2026-01-03T00:00:00Z\"}\n",
    );
    put(
        r,
        ".git/l7r-events/x.jsonl",
        "{\"t\": \"2026-01-01T00:00:00Z\", \"ev\": \"PreToolUse\", \"id\": \"a\", \"make\": \"lint\"}\n{\"t\": \"2026-01-01T00:00:01Z\", \"ev\": \"PostToolUse\", \"id\": \"a\", \"make\": \"lint\"}\n{\"t\": \"2026-01-04T00:00:00Z\", \"ev\": \"PreToolUse\", \"id\": \"b\", \"make\": \"lint\"}\n{\"t\": \"2026-01-04T00:00:00Z\", \"ev\": \"PreToolUse\", \"id\": \"b\", \"make\": \"lint\"}\n{\"t\": \"2026-01-04T00:00:01Z\", \"ev\": \"PostToolUseFailure\", \"id\": \"b\", \"make\": \"lint\"}\n{\"t\": \"2026-01-04T00:00:00Z\", \"ev\": \"SubagentStart\", \"agent\": \"rev\"}\n{\"t\": \"2026-01-04T00:00:00Z\", \"ev\": \"Stop\", \"make\": \"x\"}\n{\"t\": \"2026-01-04T00:00:00Z\", \"ev\": \"PreToolUse\", \"make\": \"build\"}\n",
    );
    put(
        r,
        "guard-log/20260101T000000-a.json",
        r#"{"guard": "foo", "event": "blocked", "utc": "2026-01-01T00:00:00Z"}"#,
    );
    put(
        r,
        "guard-log/20260102T000000-a.json",
        r#"{"guard": "foo", "event": "escaped", "utc": "2026-01-02T00:00:00Z"}"#,
    );
    put(r, "guard-log/20260103T000000-a.json", "[1]");
    put(r, "guard-log/20260104T000000-a.json", "{}");
}

#[test]
fn a_tally_counts_since_and_restarts_on_an_unread_time() {
    let mut t = Tally::new("guard", "g");
    t.use_at(5.0);
    t.use_at(0.0);
    assert!(t.first == 0.0);
    t.use_at(7.0);
    assert!((t.first - 7.0).abs() < f64::EPSILON);
    t.hit(6.0, true);
    t.hit(1.0, false);
    t.miss(8.0, true);
    t.miss(1.0, false);
    assert_eq!(t.since(6.0), (1, 1, 1));
    assert_eq!(guard_kind("hook"), "guard");
    assert!(registry_kind(&serde_json::json!([])).is_err());
    assert_eq!(registry_kind(&serde_json::json!({})).unwrap(), "step");
}

#[test]
fn a_change_maps_to_its_tools() {
    let r = crate::checks::scratch("ty-tools");
    repo(&r);
    let files: Vec<String> = [
        "scripts/hooks/foo-hooks.sh",
        "scripts/hooks/lib/helper.py",
        "scripts/util.sh",
        "scripts/gates/gatey.py",
        ".claude/agents/rev.md",
        "scripts/step.py",
        "scripts/tools/lint.py",
        "l7r/x.py",
    ]
    .map(str::to_owned)
    .to_vec();
    let diff = "@@ -1 +1 @@ build:\n+lint: x\n-nosuch: y\n context\n";
    let got: Vec<(String, String)> = tools_of(&r, &files, diff).unwrap().into_iter().collect();
    let want: Vec<(String, String)> = [
        ("check", "gatey"),
        ("check", "lint"),
        ("guard", "foo"),
        ("review", "rev"),
        ("step", "stepper"),
        ("target", "build"),
        ("target", "lint"),
    ]
    .iter()
    .map(|(a, b)| ((*a).to_owned(), (*b).to_owned()))
    .collect();
    assert_eq!(got, want);
    put(&r, "scripts/tool-registry.json", r#"{"tools":{"bad":[]}}"#);
    assert!(tools_of(&r, &files, "").is_err());
    std::fs::remove_file(r.join("Makefile")).unwrap();
    assert!(tools_of(&r, &files, "").is_err());
    std::fs::remove_file(r.join(".claude/settings.json")).unwrap();
    assert!(tools_of(&r, &files, "").is_err());
}

#[test]
fn every_tool_is_counted_and_reported() {
    let r = crate::checks::scratch("ty-collect");
    repo(&r);
    let t = collect(&r, &r.join("guard-log")).unwrap();
    let foo = &t[&("guard".to_owned(), "foo".to_owned())];
    assert_eq!((foo.uses.len(), foo.hits, foo.misses), (3, 1, 1));
    let lint = &t[&("target".to_owned(), "lint".to_owned())];
    assert_eq!(
        (lint.uses.len(), lint.hits, lint.misses, lint.unseen),
        (2, 1, 1, 0)
    );
    assert!(t[&("review".to_owned(), "rev".to_owned())].outcome_record);
    assert!(!t[&("step".to_owned(), "stepper".to_owned())].outcome_record);
    assert!(!t[&("review".to_owned(), "silent".to_owned())].outcome_record);
    assert_eq!(t[&("step".to_owned(), "None".to_owned())].uses.len(), 1);
    let now = utc_now_of("2026-01-06T00:00:00Z");
    let all = table(&t, "", now);
    assert!(all.contains("| guard | foo | 2026-01-01 | 3 | 3 | 1 | 1 | too new |"));
    let later = table(&t, "check", now + 30.0 * DAY);
    assert!(later.contains("| check | gatey | 2026-01-02 | 0 | 1 | 1 | no outcome record |  |"));
    assert!(
        later.contains("| check | lint | - | 0 | 0 | 0 | no outcome record | no outcome record |")
    );
    assert!(!later.contains("| guard |"));
    put(
        &r,
        ".git/tool-usage.jsonl",
        "{\"utc\": \"2026-01-05T00:00:00Z\", \"kind\": \"target\", \"tool\": \"build\"}\n",
    );
    let t = collect(&r, &r.join("guard-log")).unwrap();
    assert!(table(&t, "target", now + 30.0 * DAY).contains(
        "| target | build | 2026-01-04 | 0 | 2 | 1 | 0 | 1 run(s) with no outcome record |"
    ));
    put(&r, "dev/bypass-log/d/f.json", "[1]");
    assert!(collect(&r, &r.join("guard-log")).is_err());
    put(&r, "scripts/tool-registry.json", r#"{"tools":{"bad":[]}}"#);
    assert!(collect(&r, &r.join("guard-log")).is_err());
    put(&r, "Makefile", "");
    std::fs::write(r.join("dev/review-ledger.md"), b"\xff").unwrap();
    put(&r, "scripts/tool-registry.json", "{}");
    assert!(collect(&r, &r.join("guard-log")).is_err());
}

fn utc_now_of(text: &str) -> f64 {
    records::utc(text)
}

#[test]
fn a_day_rounds_its_microseconds_and_the_command_line() {
    assert_eq!(day_rounded(86_399.999_999_7), "1970-01-02");
    assert_eq!(day_rounded(-0.000_000_7), "1970-01-01");
    assert_eq!(day_rounded(0.5), "1970-01-01");
    assert!(now() > 0.0);
    let r = crate::checks::scratch("ty-cli");
    repo(&r);
    let ask = |words: &[&str], root: &Path| {
        cli(
            &words.iter().map(|s| (*s).to_owned()).collect::<Vec<_>>(),
            root,
            &r,
        )
    };
    assert_eq!(ask(&["--kind", "nope"], &r).code, 2);
    assert_eq!(ask(&["--bogus"], &r).code, 2);
    let ok = ask(&["--kind=guard"], &r);
    assert!(ok.code == 0 && ok.stdout.contains("| guard | foo |"));
    let other = r.display().to_string();
    assert_eq!(ask(&["--root", &other], Path::new("/nonexistent")).code, 0);
    assert_eq!(ask(&[], Path::new("/nonexistent")).code, 1);
}
