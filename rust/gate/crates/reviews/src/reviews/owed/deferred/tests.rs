//! The set-aside record on scratch repositories: a unit set aside at rust-only and landed is owed once the switch is thrown back, until
//! its review is recorded; a hamlet whose units were not known owes what it draws new since; what no longer stands is owed no more.

use std::path::Path;

use super::super::super::tests::{commit, drawn, hamlet, put, repo, sh};
use super::super::all_owed;
use super::*;

fn args(a: &[&str]) -> Vec<String> {
    a.iter().map(|s| (*s).to_owned()).collect()
}

fn run(root: &Path, verb: &str, utc: &str, more: &[&str]) -> Reply {
    let r = root.to_string_lossy();
    let mut a = vec![verb, "--root", &r, "--utc", utc];
    a.extend_from_slice(more);
    cli(&args(&a))
}

fn owed_slugs(root: &Path) -> Vec<String> {
    all_owed(root).1.iter().map(Unit::slug).collect()
}

fn port(root: &Path, state: &str) {
    put(
        root,
        "dev/switches.json",
        &format!("{{\"port\": {{\"state\": \"{state}\"}}}}"),
    );
}

/// Main holds `m` drawing a farmhouse at rust-only; the work draws a well too.
fn gained(name: &str) -> l7r_guard::shared::tempdir::Held<std::path::PathBuf> {
    let r = repo(name);
    hamlet(&r, "m", &["farmhouse"]);
    port(&r, "rust-only");
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    hamlet(&r, "m", &["farmhouse", "well"]);
    commit(&r, "the well");
    r
}

/// The push lands: origin/main moves to HEAD, so the delta no longer holds what it pushed.
fn landed(root: &Path) {
    commit(root, "the record");
    sh(root, "git update-ref refs/remotes/origin/main HEAD");
}

#[test]
fn a_unit_set_aside_and_landed_is_owed_at_the_throw_back_until_its_review_is_recorded() {
    let r = gained("landed");
    assert_eq!(owed_slugs(&r), ["glyph-check--well--m"]);
    let said = run(
        &r,
        "set-aside",
        "2026-11-19T10:00:00Z",
        &["glyph-check--well--m", "glyph-check--nothing--m"],
    );
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (
            0,
            "deferred: glyph-check--well--m recorded, owed at the throw back\n"
        )
    );
    // set aside again while it is held: no second row
    assert!(run(
        &r,
        "set-aside",
        "2026-11-19T10:05:00Z",
        &["glyph-check--well--m"]
    )
    .stdout
    .is_empty());
    assert_eq!(rows(&r).len(), 1);
    landed(&r);
    // RED FIRST (T232): the delta holds nothing now, so without the record nothing is owed at the throw back
    port(&r, "integrated");
    let (_, units, _) = all_owed(&r);
    assert_eq!(units.len(), 1);
    assert_eq!(units[0].slug(), "glyph-check--well--m");
    let head = git(&r, &["rev-parse", "HEAD~1"]).unwrap();
    assert_eq!(
        units[0].occasion,
        format!(
            "set aside at rust-only 2026-11-19T10:00:00Z ({}): 'well' is new to m",
            &head[..8]
        )
    );
    // at rust-only it waits, and the review gate sets it aside again from what the delta owes
    port(&r, "rust-only");
    assert!(owed_slugs(&r).is_empty());
    port(&r, "integrated");
    // a review recorded before it was set aside does not clear it; one at or after it does
    put(
        &r,
        RECORD,
        &format!(
            "{}{}\n",
            std::fs::read_to_string(r.join(RECORD)).unwrap(),
            json!({"reviewed": "glyph-check--well--m", "utc": "2026-11-18T00:00:00Z"})
        ),
    );
    assert_eq!(owed_slugs(&r), ["glyph-check--well--m"]);
    let said = run(
        &r,
        "reviewed",
        "2026-11-20T00:00:00Z",
        &["glyph-check--well--m", "glyph-check--other--m"],
    );
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (0, "deferred: glyph-check--well--m reviewed, recorded\n")
    );
    assert!(owed_slugs(&r).is_empty());
    // reviewed twice: nothing more to record
    assert!(run(
        &r,
        "reviewed",
        "2026-11-21T00:00:00Z",
        &["glyph-check--well--m"]
    )
    .stdout
    .is_empty());
    // set aside again later (the element came back): owed again
    put(
        &r,
        RECORD,
        &format!(
            "{}{}\n",
            std::fs::read_to_string(r.join(RECORD)).unwrap(),
            json!({"unit": "glyph-check--well--m", "check": "glyph-check", "subject": "well", "on": "m", "occasion": "o", "utc": "2026-11-22T00:00:00Z", "commit": "c"})
        ),
    );
    assert_eq!(owed_slugs(&r), ["glyph-check--well--m"]);
}

#[test]
fn a_unit_that_no_longer_stands_is_owed_no_more() {
    let r = repo("standing");
    hamlet(&r, "m", &["farmhouse"]);
    port(&r, "integrated");
    let row = |check: &str, subject: &str, on: &str| {
        json!({"unit": Unit::new(check, subject, on, String::new()).slug(), "check": check, "subject": subject, "on": on,
            "occasion": "o", "utc": "2026-11-19T00:00:00Z", "commit": "abc"})
    };
    let lines = [
        row("glyph-check", "farmhouse", "m"),
        row("glyph-check", "well", "m"),
        row("glyph-check", "well", "gone"),
        row("settlement-review", "m", "m"),
    ];
    let mut text = String::new();
    for l in &lines {
        text.push_str(&l.to_string());
        text.push_str("\nnot json\n[1]\n");
    }
    put(&r, RECORD, &text);
    commit(&r, "record");
    assert_eq!(rows(&r).len(), 4);
    // the element gone from the map and the map gone from the pool owe nothing; the rest is owed
    assert_eq!(
        owed_slugs(&r),
        ["settlement-review--m", "glyph-check--farmhouse--m"]
    );
    // a drawing not current keeps an element's check owed: what it draws is not known
    put(&r, "pool/hamlets/m/m.spec.json", "{\"seed\": 2}");
    assert_eq!(
        owed_slugs(&r),
        [
            "settlement-review--m",
            "glyph-check--farmhouse--m",
            "glyph-check--well--m"
        ]
    );
}

#[test]
fn a_hamlet_whose_units_were_not_known_owes_what_it_draws_new_since() {
    let r = repo("unknown");
    hamlet(&r, "m", &["farmhouse"]);
    hamlet(&r, "n", &["pond"]);
    put(&r, "pool/compounds/c/c.compound.json", "{}");
    port(&r, "rust-only");
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    let said = run(
        &r,
        "set-aside",
        "2026-11-19T00:00:00Z",
        &[
            "--unknown",
            "pool/hamlets/m",
            "--unknown",
            "pool/compounds/c",
        ],
    );
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (0, "deferred: pool/hamlets/m recorded with its elements at the base, its units owed at the throw back\n")
    );
    let row = &rows(&r)[0];
    assert_eq!(
        (field(row, "name"), row["was"].clone()),
        ("m", json!(["farmhouse"]))
    );
    // the same elements again: no second row; another hamlet's elements: its own row
    assert!(run(
        &r,
        "set-aside",
        "2026-11-19T01:00:00Z",
        &["--unknown", "pool/hamlets/m"]
    )
    .stdout
    .is_empty());
    assert_eq!(
        run(
            &r,
            "set-aside",
            "2026-11-19T01:00:00Z",
            &["--unknown", "pool/hamlets/n"]
        )
        .code,
        0
    );
    assert_eq!(rows(&r).len(), 2);
    landed(&r);
    port(&r, "integrated");
    // drawn as it was: nothing new; drawn with a well: its glyph-check owed
    assert!(owed_slugs(&r).is_empty());
    drawn(&r, "m", &["farmhouse", "well"]);
    commit(&r, "redrawn, main's drawing caught up");
    put(
        &r,
        "pool/hamlets/m/m.json",
        &std::fs::read_to_string(r.join("pool/hamlets/m/m.driver.json")).unwrap(),
    );
    landed(&r);
    let (_, units, _) = all_owed(&r);
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        ["glyph-check--well--m"]
    );
    assert!(units[0]
        .occasion
        .contains("'well' is new to m since its units were not known"));
    assert_eq!(
        run(
            &r,
            "reviewed",
            "2026-11-20T00:00:00Z",
            &["glyph-check--well--m"]
        )
        .code,
        0
    );
    assert!(owed_slugs(&r).is_empty());
    // a hamlet whose drawing is not known names nothing
    put(&r, "pool/hamlets/n/n.spec.json", "{\"seed\": 2}");
    assert!(owed_slugs(&r).is_empty());
}

#[test]
fn the_command_line_refuses_what_it_cannot_read_and_says_why_a_write_failed() {
    let r = repo("cli");
    for bad in [
        args(&[]),
        args(&["set-aside"]),
        args(&["unknown-verb", "--utc", "t"]),
        args(&["set-aside", "--utc"]),
        args(&["set-aside", "--utc", "t", "--nope"]),
    ] {
        let said = cli(&bad);
        assert_eq!(said.code, 2, "{bad:?}");
        let usage = said.stderr.starts_with("usage: l7r-gate reviews deferred");
        assert!(usage, "{bad:?}");
    }
    let said = cli(&args(&[
        "reviewed",
        "--root",
        "/proc/nonexistent",
        "--utc",
        "t",
    ]));
    assert_eq!(said.code, 1);
    assert!(said.stderr.contains("is not a git repository"));
    // `dev` a file: the record cannot be written, and both verbs say so
    hamlet(&r, "m", &["farmhouse"]);
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    hamlet(&r, "m", &["farmhouse", "well"]);
    put(&r, "dev", "a file");
    let said = run(&r, "set-aside", "t", &["glyph-check--well--m"]);
    assert_eq!(said.code, 1);
    assert!(said.stderr.contains(RECORD), "{}", said.stderr);
    std::fs::remove_file(r.join("dev")).unwrap();
    assert_eq!(run(&r, "set-aside", "t", &["glyph-check--well--m"]).code, 0);
    port(&r, "integrated");
    std::fs::set_permissions(
        r.join(RECORD),
        std::os::unix::fs::PermissionsExt::from_mode(0o444),
    )
    .unwrap();
    let said = run(&r, "reviewed", "u", &["glyph-check--well--m"]);
    assert_eq!(said.code, 1, "{}", said.stdout);
    assert!(said.stderr.contains(RECORD));
}
