//! The set-aside record on scratch repositories: a unit set aside at rust-only and landed is owed once the switch is thrown back, until
//! its review is recorded; a hamlet whose units were not known owes what it draws new since; what no longer stands is owed no more.

use std::path::Path;

use super::super::super::tests::{commit, drawn, hamlet, map, put, repo, sh};
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

/// The settlement-review feature 444 FR-019 owes every pool hamlet the port moved (449 T233): a hamlet already in the pool, moved by a
/// Rust stage at rust-only, owes no unit the delta detects (a settlement-review is detected only for a map new to the pool), so nothing
/// was set aside and the throw back owed nothing (measured 2026-11-19 in scratch: `review-gate: clean`).
#[test]
fn a_pool_hamlet_the_port_moved_owes_its_settlement_review_at_the_throw_back() {
    let r = repo("moved");
    hamlet(&r, "m", &["farmhouse"]);
    hamlet(&r, "n", &["pond"]);
    put(
        &r,
        "legacy-hand-authored-pool/hamlets/old/old.spec.json",
        "{}",
    );
    port(&r, "rust-only");
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    // the port moves both hamlets: nothing the delta detects
    drawn(&r, "m", &["farmhouse"]);
    commit(&r, "a Rust stage moves the hamlets");
    assert!(owed_slugs(&r).is_empty());
    // RED FIRST (T233): with no `--moved`, set-aside wrote no row, and at the throw back nothing was owed
    let said = run(&r, "set-aside", "2026-11-19T10:00:00Z", &["--moved"]);
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (
            0,
            "deferred: settlement-review--m recorded, owed at the throw back\n\
             deferred: settlement-review--n recorded, owed at the throw back\n"
        )
    );
    // held open: no second row
    assert!(run(&r, "set-aside", "2026-11-19T11:00:00Z", &["--moved"])
        .stdout
        .is_empty());
    assert_eq!(rows(&r).len(), 2);
    // a hamlet renamed at rust-only: its row carried to the new name (`a_row_is_carried_across_its_hamlets_rename`)
    sh(
        &r,
        "git mv pool/hamlets/n pool/hamlets/n2 && git mv pool/hamlets/n2/n.spec.json pool/hamlets/n2/n2.spec.json \
         && git mv pool/hamlets/n2/n.json pool/hamlets/n2/n2.json",
    );
    drawn(&r, "n2", &["pond"]);
    commit(&r, "renamed");
    let said = run(&r, "set-aside", "2026-11-19T12:00:00Z", &["--moved"]);
    assert_eq!(
        said.stdout,
        "deferred: settlement-review--n2 carried from n across its rename, owed at the throw back\n"
    );
    // a unit the delta owes and a moved hamlet on one call: one row each, never two for one slug
    map(&r, "pool", "p", &["well"]);
    put(&r, "pool/hamlets/p/p.spec.json", "{\"seed\": 9}");
    drawn(&r, "p", &["well"]);
    commit(&r, "a new hamlet");
    assert_eq!(
        owed_slugs(&r),
        ["settlement-review--p", "glyph-check--well--p"]
    );
    let said = run(
        &r,
        "set-aside",
        "2026-11-19T13:00:00Z",
        &["--moved", "settlement-review--p"],
    );
    assert_eq!(
        said.stdout,
        "deferred: settlement-review--p recorded, owed at the throw back\n"
    );
    landed(&r);
    port(&r, "integrated");
    let (_, units, _) = all_owed(&r);
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        [
            "settlement-review--m",
            "settlement-review--n2",
            "settlement-review--p"
        ]
    );
    assert!(units[0]
        .occasion
        .starts_with("set aside at rust-only 2026-11-19T10:00:00Z ("));
    assert!(units[0].occasion.ends_with(MOVED));
    // reviewed at the throw back: owed no more
    assert_eq!(
        run(
            &r,
            "reviewed",
            "2026-11-20T00:00:00Z",
            &["settlement-review--m", "settlement-review--p"]
        )
        .code,
        0
    );
    assert_eq!(owed_slugs(&r), ["settlement-review--n2"]);
}

/// RED FIRST (449 T233): a row is keyed by its hamlet's name, so a hamlet renamed at rust-only dropped every row it had - a glyph-check,
/// a settlement-review, a hamlet whose units were not known - and the throw back owed none (measured 2026-11-19 in a scratch fixture).
/// A rename is git's rename detection over the delta finding the folder's spec moved with it; each open row is owed under the new name
/// while the rename is in the delta, and set-aside writes it there, so it stands once the rename has landed.
#[test]
fn a_row_is_carried_across_its_hamlets_rename() {
    let r = repo("rename");
    hamlet(&r, "m", &["farmhouse", "well"]);
    port(&r, "rust-only");
    let rows_text = [
        json!({"unit": "glyph-check--well--m", "check": "glyph-check", "subject": "well", "on": "m", "occasion": "'well' is new to m",
            "utc": "2026-11-19T00:00:00Z", "commit": "abc"}),
        json!({"unit": "settlement-review--m", "check": "settlement-review", "subject": "m", "on": "m", "occasion": MOVED,
            "utc": "2026-11-19T00:00:00Z", "commit": "abc"}),
        json!({"hamlet": "pool/hamlets/m", "name": "m", "was": ["farmhouse", "well"], "utc": "2026-11-19T00:00:00Z", "commit": "abc"}),
        // reviewed under the old name before the rename: not carried
        json!({"unit": "glyph-check--farmhouse--m", "check": "glyph-check", "subject": "farmhouse", "on": "m", "occasion": "o",
            "utc": "2026-11-19T00:00:00Z", "commit": "abc"}),
        json!({"reviewed": "glyph-check--farmhouse--m", "utc": "2026-11-19T01:00:00Z"}),
    ]
    .iter()
    .fold(String::new(), |mut text, v| {
        text.push_str(&v.to_string());
        text.push('\n');
        text
    });
    put(&r, RECORD, &rows_text);
    commit(&r, "base");
    sh(&r, "git update-ref refs/remotes/origin/main HEAD");
    sh(
        &r,
        "git mv pool/hamlets/m pool/hamlets/m2 && git mv pool/hamlets/m2/m.spec.json pool/hamlets/m2/m2.spec.json \
         && git mv pool/hamlets/m2/m.json pool/hamlets/m2/m2.json",
    );
    drawn(&r, "m2", &["farmhouse", "well", "pond"]);
    commit(&r, "renamed");
    // the rename in the delta: each row owed under the new name, the hamlet row's new element too
    port(&r, "integrated");
    let (_, units, _) = all_owed(&r);
    assert_eq!(
        units.iter().map(Unit::slug).collect::<Vec<_>>(),
        [
            "settlement-review--m2",
            "glyph-check--pond--m2",
            "glyph-check--well--m2"
        ]
    );
    assert!(units[2]
        .occasion
        .ends_with("'well' is new to m (carried from m across its rename)"));
    // at rust-only, set-aside writes each under the new name, once
    port(&r, "rust-only");
    let said = run(&r, "set-aside", "2026-11-21T00:00:00Z", &["--moved"]);
    assert_eq!(
        (said.code, said.stdout.as_str()),
        (
            0,
            "deferred: glyph-check--well--m2 carried from m across its rename, owed at the throw back\n\
             deferred: settlement-review--m2 carried from m across its rename, owed at the throw back\n\
             deferred: pool/hamlets/m2 carried from pool/hamlets/m across its rename, its units owed at the throw back\n"
        )
    );
    assert!(run(&r, "set-aside", "2026-11-21T01:00:00Z", &["--moved"])
        .stdout
        .is_empty());
    // landed: the rename has left the delta, and the carried rows stand
    landed(&r);
    port(&r, "integrated");
    assert_eq!(
        owed_slugs(&r),
        [
            "settlement-review--m2",
            "glyph-check--pond--m2",
            "glyph-check--well--m2"
        ]
    );
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
