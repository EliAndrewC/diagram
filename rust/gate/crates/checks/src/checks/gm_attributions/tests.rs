//! The check, on scratch trees: a constructed page comment and a constructed claim, each naming a ruling of the GM's.

use std::path::Path;

use super::{cli, BASELINE, NAMES};
use crate::checks::tests::{based, commit, put, repo};

fn run(root: &Path, mode: &[&str]) -> crate::checks::Outcome {
    let mut args: Vec<String> = mode.iter().map(|s| (*s).to_owned()).collect();
    args.push(root.display().to_string());
    cli(&args)
}

const PAGE: &str = "research/questions/0001-a.drawing.html";
const RUST: &str = "rust/phases/src/x.rs";

/// A page whose second comment attributes a rule to the GM with no record, and a claim that does the same.
fn tree(tag: &str) -> l7r_shared::tempdir::TempDir {
    let root = repo(tag);
    put(&root, PAGE, "<p>the GM's ruling in prose is not a comment</p>\n<!-- Grounds: a source -->\n<!-- the GM's ruling, 2026-07:\n dry plots are rectangles -->\n");
    put(&root, RUST, "/// Research:\n///     square - CANON: the GM's ruling of 2026-07-25\n///     plain - research/questions/0001-a.drawing.html: the GM's ruling, not CANON\n");
    put(
        &root,
        "rust/gate/src/t.rs",
        "\"x - CANON: the GM's ruling\"\n",
    );
    put(&root, "dev/x", "");
    put(
        &root,
        "research/questions/notes.md",
        "<!-- the GM's ruling, not a page -->\n",
    );
    root
}

#[test]
fn an_attribution_with_no_record_is_refused_where_it_stands() {
    let root = tree("gma-red");
    let out = run(&root, &[]);
    assert_eq!(out.code, 1);
    assert!(out.stderr.contains(&format!(
        "{PAGE}:3: a comment names a ruling of the GM's (\"the GM's ruling\")"
    )));
    assert!(out.stderr.contains(&format!("{RUST}:2: a claim")));
    assert!(out.stderr.contains(
        "specs/<NNN-slug>/request.md, docs/gm-rulings.md, specs/<NNN-slug>/gm-review.jsonl (a make gm-reviewed row) or a dated specs/<NNN-slug>/rulings-YYYY-MM-DD.md"
    ));
    assert_eq!(out.stderr.lines().count(), 2);
}

#[test]
fn a_pointer_that_resolves_backs_it_and_one_that_does_not_is_named() {
    let root = tree("gma-ptr");
    put(&root, PAGE, "<!-- the GM's ruling (specs/001-a/request.md) -->\n<!-- GM, 2026-08-11 (docs/gm-rulings.md) -->\n");
    put(
        &root,
        RUST,
        "///     square - CANON: the GM ruled it, specs/002-b/gm-review.jsonl\n",
    );
    put(&root, "docs/gm-rulings.md", "x");
    put(&root, "specs/002-b/gm-review.jsonl", "{}");
    let out = run(&root, &[]);
    assert_eq!(out.code, 1);
    assert!(out
        .stderr
        .contains("(specs/001-a/request.md does not exist)"));
    assert_eq!(out.stderr.lines().count(), 1);
    put(&root, "specs/001-a/request.md", "his words");
    assert_eq!(run(&root, &[]).code, 0);
}

/// 451 T265: his verbatim words also stand in a feature's dated rulings file; a file that quotes him second-hand backs nothing.
#[test]
fn a_dated_rulings_file_backs_it_and_a_second_hand_file_does_not() {
    let root = tree("gma-rulings");
    put(&root, RUST, "");
    for held in [
        "audit.md",
        "tasks.md",
        "rulings-notes.md",
        "rulings-2026-09-28.md",
    ] {
        put(&root, &format!("specs/269-b/{held}"), "> his words");
    }
    for second_hand in ["audit.md", "tasks.md", "rulings-notes.md"] {
        put(
            &root,
            PAGE,
            &format!("<!-- the GM's ruling (specs/269-b/{second_hand}) -->\n"),
        );
        let out = run(&root, &[]);
        assert_eq!(out.code, 1, "{second_hand}");
        assert!(!out.stderr.contains("does not exist"), "{second_hand}");
    }
    put(
        &root,
        PAGE,
        "<!-- the GM's ruling (specs/270-c/rulings-2026-09-28.md) -->\n",
    );
    assert!(run(&root, &[])
        .stderr
        .contains("(specs/270-c/rulings-2026-09-28.md does not exist)"));
    put(
        &root,
        PAGE,
        "<!-- the GM's ruling (specs/269-b/rulings-2026-09-28.md) -->\n",
    );
    assert_eq!(run(&root, &[]).code, 0);
}

/// 451 T265: the wording that slipped past the pattern, on a claim line as `docs/building-programs.md` carried it.
#[test]
fn a_gm_ruling_is_read_as_the_gms_ruling_is() {
    let root = tree("gma-a");
    put(&root, PAGE, "");
    put(
        &root,
        RUST,
        "///     dedication knob - CANON: Inari the ordinary rural dedication, a GM ruling of 2026-09-20\n",
    );
    let out = run(&root, &[]);
    assert_eq!(out.code, 1);
    assert!(out.stderr.contains(&format!(
        "{RUST}:1: a claim names a ruling of the GM's (\"a GM ruling\")"
    )));
}

#[test]
fn each_naming_form_is_matched_and_a_plain_mention_is_not() {
    for said in [
        "the GM's catch",
        "The GM's words",
        "the GM's decisions",
        "the GM ruled",
        "GM 2026-07-21",
        "the GM, 2026-08",
        "the GM's rule of",
        "the GM's doctrine",
        "the GM's correction",
        "a GM ruling of 2026-09-20",
        "A GM decision",
    ] {
        assert!(NAMES.is_match(said).unwrap(), "{said}");
    }
    for said in ["the GM's notes", "asked the GM", "GM review", "a GM review"] {
        assert!(!NAMES.is_match(said).unwrap(), "{said}");
    }
}

#[test]
fn the_baseline_lists_the_old_ones_and_only_shrinks() {
    let root = tree("gma-base");
    assert_eq!(run(&root, &["--seed"]).code, 0);
    assert_eq!(run(&root, &[]).code, 0);
    let seeded = std::fs::read_to_string(root.join(BASELINE)).unwrap();
    assert_eq!(seeded.lines().count(), 2);
    assert!(seeded.contains("\"kind\":\"claim\""));
    assert_eq!(run(&root, &["--seed"]).code, 1);
    // a line moved keeps it listed; its text edited owes the pointer
    put(
        &root,
        PAGE,
        "<p>new</p>\n\n<!-- the GM's ruling, 2026-07:\n dry plots are rectangles -->\n",
    );
    assert_eq!(run(&root, &[]).code, 0);
    put(
        &root,
        PAGE,
        "<!-- the GM's ruling, 2026-07: dry plots are squares -->\n",
    );
    let out = run(&root, &[]);
    assert!(out.stderr.contains(&format!("{PAGE}:1: a comment")));
    assert!(out.stderr.contains("no longer found (fixed or edited) - drop it: scripts/gates/l7r-gate.sh check gm-attributions --prune"));
    // the fix: the pointer, then the prune
    put(
        &root,
        PAGE,
        "<!-- the GM's ruling, 2026-07: dry plots are squares (docs/gm-rulings.md) -->\n",
    );
    put(&root, "docs/gm-rulings.md", "x");
    assert_eq!(run(&root, &[]).code, 1);
    assert_eq!(run(&root, &["--prune"]).code, 0);
    assert_eq!(
        std::fs::read_to_string(root.join(BASELINE))
            .unwrap()
            .lines()
            .count(),
        1
    );
    assert_eq!(run(&root, &[]).code, 0);
}

#[test]
fn an_entry_the_merge_base_lacks_is_refused() {
    let root = tree("gma-grow");
    commit(&root);
    based(&root);
    assert_eq!(run(&root, &["--seed"]).code, 0); // no baseline at the base: the first one is free
    assert_eq!(run(&root, &[]).code, 0);
    commit(&root);
    based(&root);
    put(
        &root,
        RUST,
        "///     square - CANON: the GM's ruling of 2026-07-26\n",
    );
    let gone = std::fs::read_to_string(root.join(BASELINE)).unwrap();
    std::fs::remove_file(root.join(BASELINE)).unwrap();
    assert_eq!(run(&root, &["--seed"]).code, 0);
    let out = run(&root, &[]);
    assert_eq!(out.code, 1);
    assert!(out
        .stderr
        .contains("which the merge base's copy does not list - the baseline only shrinks"));
    assert!(gone.lines().count() == 2);
}

#[test]
fn a_bad_command_line_and_an_unwritable_baseline_are_told() {
    let root = tree("gma-usage");
    assert_eq!(cli(&["--nope".to_owned()]).code, 2);
    assert_eq!(cli(&["a".to_owned(), "b".to_owned()]).code, 2);
    let none = repo("gma-none");
    assert_eq!(run(&none, &["--seed"]).code, 1);
    assert_eq!(run(&none, &["--prune"]).code, 0);
    assert!(!none.join(BASELINE).exists());
    assert_eq!(run(&root, &["--prune"]).code, 0);
}
