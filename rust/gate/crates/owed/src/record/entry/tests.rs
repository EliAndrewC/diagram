//! The entry-drift report on a scratch record (feature 449 T149; the lines and words `entry_owed.py`'s). FR-008's tenth of a second a
//! test: the fixture holds four kinds' files, not the registry's 160, built once a test binary and copied; the report is handed those
//! four kinds as its registries (`owed_from`'s `load`), and the two tests of the real loading write the other files uncommitted.

use std::path::Path;

use super::{base_of, cli, owed, owed_from, Loaded};
use crate::record::repo::Fail;
use crate::record::testkit::{commit, git, put};
use l7r_gate_registry::kinds::{Registry, HAMLET_REGISTRY, SHEET_REGISTRY};

const Q: &str = "research/questions";

/// The fixture's kinds: three of the hamlet vocabulary and one of the Mode A kinds, the key both registries hold.
const HAMLET: [&str; 3] = ["alder", "barley", "byre"];
const SHEET: [&str; 1] = ["well"];

fn args(list: &[&str]) -> Vec<String> {
    list.iter().map(|s| (*s).to_owned()).collect()
}

fn page(heading: &str, intro: &str, body: &str) -> String {
    format!("<h2 id=\"x\">{heading}</h2>\n<p class=\"intro\">{intro}</p>\n<p>{body}</p>\n")
}

fn entry() -> String {
    format!("{Q}/0001-a.html, {Q}/0005-old-slug.html, {Q}/0006-old-slug.html")
}

fn modal_rel(registry: &Registry, key: &str) -> String {
    l7r_gate_registry::about::modal_rel(registry, key)
}

/// The fixture's kinds as the report's registries, read from their files as the real loading reads them.
fn few(root: &Path) -> Result<Loaded, Fail> {
    let read = |registry: &Registry, keys: &[&str]| -> Result<Vec<_>, Fail> {
        keys.iter()
            .map(|key| {
                let (_, kind) = registry
                    .kinds()
                    .into_iter()
                    .find(|(_, k)| k.key == *key)
                    .unwrap();
                l7r_gate_registry::about::feature(root, registry, kind.class, kind.key)
                    .map_err(|e| e.message)
            })
            .collect()
    };
    Ok(vec![
        (HAMLET_REGISTRY, read(&HAMLET_REGISTRY, &HAMLET)?),
        (SHEET_REGISTRY, read(&SHEET_REGISTRY, &SHEET)?),
    ])
}

/// The repository every test starts from, built once a test binary (FR-006's fixture built once) in the directory the test runner
/// removes whole when the crate's run ends (`beside_binary`): the four kinds written from questions 0001, 0005 and 0006, committed once
/// and set as its own origin/main.
fn template() -> &'static Path {
    static DIR: std::sync::OnceLock<std::path::PathBuf> = std::sync::OnceLock::new();
    DIR.get_or_init(|| {
        let root = l7r_shared::tempdir::beside_binary("owed-entry-template");
        git(&root, &["init", "-q"]);
        // the committer named in the config file itself: two `git config` processes fewer
        let config = root.join(".git/config");
        let text = std::fs::read_to_string(&config).unwrap();
        std::fs::write(&config, text + "[user]\n\temail = t@t\n\tname = t\n").unwrap();
        for (registry, keys) in [
            (&HAMLET_REGISTRY, &HAMLET[..]),
            (&SHEET_REGISTRY, &SHEET[..]),
        ] {
            for key in keys {
                put(
                    &root,
                    &modal_rel(registry, key),
                    &l7r_gate_registry::testkit::modal(key, &entry()),
                );
            }
        }
        put(
            &root,
            &format!("{Q}/0001-a.html"),
            &page("A", "why", "a finding"),
        );
        put(
            &root,
            &format!("{Q}/0005-old-slug.html"),
            &page("Old", "why", "old finding"),
        );
        put(&root, &format!("{Q}/0007-empty.html"), "");
        put(&root, "research/sources/x.html", "<p>w</p>\n");
        let base = commit(&root, "base");
        git(&root, &["update-ref", "refs/remotes/origin/main", &base]);
        root
    })
}

fn copy_tree(from: &Path, to: &Path) {
    std::fs::create_dir_all(to).unwrap();
    for e in std::fs::read_dir(from).unwrap().flatten() {
        let (src, dest) = (e.path(), to.join(e.file_name()));
        if e.file_type().unwrap().is_dir() {
            copy_tree(&src, &dest);
        } else {
            std::fs::copy(&src, &dest).unwrap();
        }
    }
}

/// A copy of the template repository a test owns.
fn repo(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = crate::checks::scratch(tag);
    copy_tree(template(), &root);
    root
}

/// The findings of question 0001 moved in the working tree.
fn move_findings(root: &Path) {
    put(
        root,
        &format!("{Q}/0001-a.html"),
        &page("A", "why", "a new finding"),
    );
}

#[test]
fn nothing_moved_names_nothing_and_an_intro_a_write_up_or_a_new_page_moves_nothing() {
    let root = repo("entry-quiet");
    let short: String = git(&root, &["rev-parse", "HEAD"]).chars().take(8).collect();
    assert_eq!(
        owed(&root).unwrap(),
        (format!("origin/main (merge base {short})"), vec![])
    );
    put(
        &root,
        &format!("{Q}/0001-a.html"),
        &page("A", "a new why", "a finding"),
    );
    put(&root, "research/sources/x.html", "<p>w2</p>\n");
    put(&root, &format!("{Q}/0009-new.html"), &page("New", "", "n"));
    assert!(owed_from(&root, &root, &few).unwrap().1.is_empty());
}

#[test]
fn a_kind_is_named_when_its_section_s_findings_moved_and_its_prose_did_not() {
    let root = repo("entry-named");
    move_findings(&root);
    put(&root, &format!("{Q}/0001-a.notes.html"), "<ol></ol>\n");
    // one kind's prose moved with them, so it is not named
    let byre = modal_rel(&HAMLET_REGISTRY, "byre");
    put(
        &root,
        &byre,
        &l7r_gate_registry::testkit::modal("byre", &entry())
            .replace("About: A byre.", "About: A byre, rewritten."),
    );
    let (_, lines) = owed_from(&root, &root, &few).unwrap();
    assert_eq!(
        lines,
        [
            format!("alder - 0001-a.html - prose at l7r/diagram/interactive/assets/modals/hamlet/alder.md\n      read: {Q}/0001-a.html"),
            format!("barley - 0001-a.html - prose at l7r/diagram/interactive/assets/modals/hamlet/barley.md\n      read: {Q}/0001-a.html"),
            format!("well - 0001-a.html - prose at l7r/diagram/interactive/assets/modals/sheet/well.md\n      read: {Q}/0001-a.html"),
        ]
    );
    // with no fragment under the working directory the line names none
    assert!(!owed_from(&root, &root.join("elsewhere"), &few).unwrap().1[0].contains("read:"));
}

#[test]
fn a_registry_that_does_not_load_fails_the_report() {
    // the real loading: the fixture holds four of the 160 kinds' files, so the import the Python made fails
    let root = repo("entry-broken");
    move_findings(&root);
    assert!(owed(&root).is_err());
    std::fs::remove_file(root.join(modal_rel(&SHEET_REGISTRY, "well"))).unwrap();
    assert!(owed_from(&root, &root, &few).is_err());
}

#[test]
fn a_renumbered_page_is_compared_with_the_one_it_was() {
    let root = repo("entry-renamed");
    git(
        &root,
        &[
            "mv",
            &format!("{Q}/0005-old-slug.html"),
            &format!("{Q}/0006-old-slug.html"),
        ],
    );
    put(
        &root,
        &format!("{Q}/0006-old-slug.html"),
        &page("Old", "why", "a moved finding"),
    );
    let (_, lines) = owed_from(&root, &root, &few).unwrap();
    assert!(lines[0].starts_with("alder - 0006-old-slug.html - prose at "));
}

#[test]
fn two_pages_of_the_old_slug_name_no_page_it_was() {
    let root = repo("entry-renamed-two");
    put(
        &root,
        &format!("{Q}/0008-old-slug.html"),
        &page("Old", "why", "old finding"),
    );
    commit(&root, "a second page of the slug");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    git(
        &root,
        &[
            "mv",
            &format!("{Q}/0005-old-slug.html"),
            &format!("{Q}/0006-old-slug.html"),
        ],
    );
    put(
        &root,
        &format!("{Q}/0006-old-slug.html"),
        &page("Old", "why", "a moved finding"),
    );
    // a page empty at the base is read as the page it was, and compared
    put(&root, &format!("{Q}/0007-empty.html"), &page("E", "", "e"));
    assert!(owed_from(&root, &root, &few).unwrap().1.is_empty());
}

#[test]
fn a_page_deleted_a_drawing_renumbered_and_a_kind_with_no_text_then() {
    let root = repo("entry-edges");
    // at the base, one kind had no file and one a text that does not parse: neither had prose then, so neither is named
    let (alder, barley) = (
        modal_rel(&HAMLET_REGISTRY, "alder"),
        modal_rel(&HAMLET_REGISTRY, "barley"),
    );
    let alder_text = std::fs::read_to_string(root.join(&alder)).unwrap();
    let barley_text = std::fs::read_to_string(root.join(&barley)).unwrap();
    std::fs::remove_file(root.join(&alder)).unwrap();
    put(&root, &barley, "Name: no About\n");
    put(
        &root,
        &format!("{Q}/0003-d.drawing.html"),
        &page("D", "", "drawn"),
    );
    commit(&root, "edges");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    put(&root, &alder, &alder_text);
    put(&root, &barley, &barley_text);
    git(&root, &["rm", "-q", &format!("{Q}/0005-old-slug.html")]);
    git(
        &root,
        &[
            "mv",
            &format!("{Q}/0003-d.drawing.html"),
            &format!("{Q}/0004-d.drawing.html"),
        ],
    );
    put(
        &root,
        &format!("{Q}/0004-d.drawing.html"),
        &page("D", "", "drawn anew"),
    );
    move_findings(&root);
    let (_, lines) = owed_from(&root, &root, &few).unwrap();
    let keys: Vec<&str> = lines
        .iter()
        .map(|l| l.split(" - ").next().unwrap())
        .collect();
    assert_eq!(keys, ["byre", "well"]);
}

#[test]
fn the_base_is_the_merge_base_or_head() {
    let fresh = crate::checks::scratch("entry-fresh");
    git(&fresh, &["init", "-q"]);
    assert_eq!(
        base_of(&fresh),
        (String::new(), "no commits yet".to_owned())
    );
    assert_eq!(owed(&fresh).unwrap(), ("no commits yet".to_owned(), vec![]));
    git(&fresh, &["config", "user.email", "t@t"]);
    git(&fresh, &["config", "user.name", "t"]);
    put(&fresh, "a.txt", "a\n");
    let head = commit(&fresh, "one");
    let short: String = head.chars().take(8).collect();
    assert_eq!(base_of(&fresh).1, format!("HEAD ({short}; no origin/main)"));
    // an origin/main with no history in common: HEAD
    git(&fresh, &["checkout", "-q", "--orphan", "other"]);
    let other = commit(&fresh, "unrelated");
    git(&fresh, &["update-ref", "refs/remotes/origin/main", &other]);
    git(&fresh, &["checkout", "-q", "-f", &head]);
    assert!(base_of(&fresh).1.ends_with("; no origin/main)"));
}

#[test]
fn the_command_line_says_why() {
    let root = repo("entry-cli-why");
    let r = root.to_string_lossy().into_owned();
    let why = cli(&args(&["--root", &r, "--why"]));
    assert!(
        why.code == 0
            && why
                .stdout
                .starts_with("no modal's research section moved against origin/main (merge base ")
    );
    assert_eq!(cli(&args(&[&format!("--root={r}")])).stdout, "");
}

#[test]
fn the_command_line_names_the_kinds() {
    // the real loading, every kind's file written in the working tree; the four at the base, unchanged, are the ones named
    let root = repo("entry-cli-named");
    l7r_gate_registry::testkit::modals(&root, &entry());
    move_findings(&root);
    let named = cli(&args(&["--root", &root.to_string_lossy(), "--why"]));
    assert!(named.stdout.starts_with("research moved under 4 unchanged modal(s) against origin/main (merge base ")
        && named.stdout.ends_with(" - dispatch `entry-drift` at each, then rewrite the prose or record why not in dev/bypass-log/\n"));
}

#[test]
fn the_command_line_s_refusals() {
    assert_eq!(cli(&args(&["--root"])).code, 2);
    assert_eq!(cli(&args(&["--bogus"])).code, 2);
    let not = cli(&args(&["--root", "/nonexistent/at/all"]));
    assert_eq!(
        (not.code, not.stderr.as_str()),
        (
            1,
            "_entry_owed: /nonexistent/at/all is not a git repository\n"
        )
    );
    let root = repo("entry-cli-broken");
    move_findings(&root);
    let failed = cli(&args(&["--root", &root.to_string_lossy(), "--why"]));
    // the small fixture has no sibling table: the hamlet registry's first refusal, as the Python's import raised it
    assert!(failed.code == 1 && failed.stderr.starts_with("OSError: "));
}
