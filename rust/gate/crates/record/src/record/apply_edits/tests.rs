//! Applying a check's EDIT and GLOSSARY blocks, and the round's settling (feature 449 T145; the T145 differential holds them to
//! `apply_edits.py` on the real record, these tests every branch on the testkit's).

use std::path::Path;

use l7r_gate_core::record::testkit::{put, record, PAGE};

use super::{blocks, Block};

mod rare;
mod rounds;
mod settled;

const ONCE: &str = "<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>";

/// A scratch record's own file, spelled so the pointer check does not read it as a built page of the real record.
pub(super) fn scratch(name: &str) -> String {
    format!("research/{name}.html")
}

pub(super) fn edit(path: &str, old: &str, new: Option<&str>) -> String {
    let mut s = format!("EDIT {path}\n<<<\n{old}\n===\n");
    if let Some(n) = new {
        s.push_str(n);
        s.push('\n');
    }
    s + ">>>\n"
}

pub(super) fn run(root: &Path, reply: &str, extra: &[&str]) -> l7r_gate_core::Reply {
    put(root, "reply.md", reply);
    let mut args = vec![
        "reply.md".to_owned(),
        "--root".to_owned(),
        root.to_string_lossy().into_owned(),
    ];
    args.extend(extra.iter().map(|s| (*s).to_owned()));
    // the test's own environment (feature 451 T38): its round settles into its own store, never a session's exported one
    super::cli_in(&args, &l7r_shared::env::Rooted::with(root, &[]))
}

pub(super) fn page(root: &Path) -> String {
    std::fs::read_to_string(root.join(PAGE)).unwrap()
}

#[test]
fn the_blocks_of_a_reply_in_its_order() {
    let reply = format!("  GLOSSARY  t | a, -, b | the def  \n{}   EDIT `x.html`\n   <<<\n   old\n   ===\n\n   >>>\n", edit("p", "o", Some("n")));
    let found = blocks(&reply);
    assert_eq!(found.len(), 3);
    assert!(
        matches!(&found[0], Block::Glossary(t) if t.n == 1 && t.term == "t" && t.variants == ["a", "b"] && t.def == "the def")
    );
    assert!(matches!(&found[1], Block::Edit(e) if e.n == 2 && e.path == "p" && !e.brk));
    assert!(
        matches!(&found[2], Block::Edit(e) if e.n == 3 && e.path == "x.html" && e.old == "old" && e.new.is_empty() && e.brk)
    );
}

#[test]
fn each_edit_is_applied_once_or_refused() {
    let root = record("apply-edits-each");
    let kyakhta = ONCE.replace("apart", "apart, the col\u{6f}ur of it");
    let said = run(
        &root,
        &format!(
            "quote-check: 0094 - 1 finding\n{}",
            edit(PAGE, ONCE, Some(&kyakhta))
        ),
        &[],
    );
    assert_eq!(said.code, 0, "{}", said.stdout);
    // styled in the house spelling
    assert!(page(&root).contains("the color of it"));
    assert!(said
        .stdout
        .contains("  1. applied to 0094-trade.html   (research/questions/0094-trade.html)"));
    assert!(
        said.stdout
            .contains("apply-edits: the quote-check round's own EDITs, applied verbatim:")
            || said.stdout.contains("apply-edits: 1 block(s), 0 refused")
    );
    let refused = run(
        &root,
        &format!(
            "quote-check: x\n{}{}{}",
            edit(PAGE, "<p", Some("q")),
            edit("Makefile", "a", Some("b")),
            edit(&scratch("none"), "a", Some("b"))
        ),
        &[],
    );
    assert_eq!(refused.code, 1);
    assert!(
        refused
            .stdout
            .contains("REFUSED - the old text occurs 3 times in 0094-trade.html, not once"),
        "{}",
        refused.stdout
    );
    assert!(refused.stdout.contains("REFUSED - Makefile is not under research/, l7r/diagram/interactive/assets/modals/, l7r/diagram/interactive/classes/ or l7r/diagram/interactive/compound_kinds/"));
    assert!(refused
        .stdout
        .contains(&format!("REFUSED - no file {}", scratch("none"))));
}

// The parts of the edits' test after its first, each on a record of its own (feature 449 T167): every round with EDITs reads what is
// owed before and after its blocks, nine git processes a reading, and the one test that held them all took over FR-008's tenth of a
// second; each part starts from the record as the parts before it left the lines it reads.

#[test]
fn an_edit_applied_twice_is_said_already_applied() {
    let root = record("apply-edits-again");
    let again = run(
        &root,
        &format!(
            "quote-check: x\n{}",
            edit(PAGE, "way apart", Some("way apart, then"))
        ),
        &[],
    );
    assert!(again.stdout.contains("applied to"));
    let applied = run(
        &root,
        &format!(
            "quote-check: x\n{}",
            edit(PAGE, "way apart", Some("way apart, then"))
        ),
        &[],
    );
    assert!(applied
        .stdout
        .contains("already applied to 0094-trade.html"));
}

#[test]
fn an_edit_with_no_new_text_takes_its_line_out() {
    let root = record("apply-edits-cut");
    let line = "<p>An unmarked claim.</p>";
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, line, None)),
        &[],
    );
    assert!(!page(&root).contains(line) && !page(&root).contains("\n\n"));
}

#[test]
fn an_edit_with_no_new_text_inside_a_line_takes_the_text_out() {
    let root = record("apply-edits-cut-inside");
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, "More here.", None)),
        &[],
    );
    // the implicit check of the original made explicit: the text is gone
    assert!(!page(&root).contains("More here."), "{}", page(&root));
}

#[test]
fn an_edit_to_an_empty_new_line_leaves_the_line() {
    let root = record("apply-edits-empty");
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, "A short", Some(""))),
        &[],
    );
    assert!(page(&root).contains("<p>\n\n way apart"), "{}", page(&root));
}

#[test]
fn a_file_s_whole_text_edited_to_nothing_leaves_its_newline() {
    let root = record("apply-edits-whole");
    put(&root, "solo.html", "x");
    put(&root, &scratch("solo"), "whole\n");
    run(
        &root,
        &format!(
            "record-format: x\n{}",
            edit(&scratch("solo"), "whole", Some(""))
        ),
        &[],
    );
    assert_eq!(
        std::fs::read_to_string(root.join(scratch("solo"))).unwrap(),
        "\n"
    );
}

#[test]
fn a_glossary_block_reserves_its_file() {
    let root = record("apply-edits-terms");
    put(
        &root,
        "l7r/diagram/interactive/assets/glossary/0010-kiln.json",
        "{\"term\": \"Kiln\"}",
    );
    let said = run(&root, "record-format: 0094\nGLOSSARY kiln | | already\nGLOSSARY new term | new terms, new term | a def\n", &[]);
    assert!(said
        .stdout
        .contains("1. skipped - 'kiln' is already a glossary term"));
    assert!(said.stdout.contains("2. added 0020-new term.json"));
    assert!(said
        .stdout
        .ends_with("apply-edits: 2 block(s), 0 refused - then `make glossary`\n"));
    let dry = run(
        &root,
        "record-format: 0094\nGLOSSARY other | | d\n",
        &["--dry-run"],
    );
    assert!(
        dry.stdout.contains("would add a file for 'other'")
            && dry.stdout.contains("(dry run, nothing written)")
    );
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(root.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    std::fs::write(
        root.join("l7r/diagram/interactive/assets/glossary/0030-bad.json"),
        "{",
    )
    .unwrap();
    assert_eq!(
        run(&root, "record-format: 0094\nGLOSSARY x | | d\n", &[]).code,
        1
    );
}

#[test]
fn a_modal_form_edit_keeps_what_research_fixed() {
    let root = record("apply-edits-modal");
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/classes/x.md",
        "About: a fixed fact.\n",
    );
    let said = run(
        &root,
        &format!(
            "modal-form: x - 1 finding\n{}",
            edit(
                "l7r/diagram/interactive/assets/modals/classes/x.md",
                "a fixed fact",
                Some("a fact")
            )
        ),
        &[],
    );
    assert!(said.stdout.contains("applied to x.md"), "{}", said.stdout);
    let missing = run(
        &root,
        &format!(
            "modal-form: x\n{}",
            edit(
                "l7r/diagram/interactive/assets/modals/classes/none.md",
                "a",
                Some("b")
            )
        ),
        &[],
    );
    assert!(missing.stdout.contains("REFUSED - no file"));
}

/// The registry's fragments the record-format prepass assembles (the testkit's registry has neither front nor tail).
pub(super) fn assemblable(root: &Path) {
    put(root, "research/sources/_front.html", "<h1>Sources</h1>\n");
    put(root, "research/sources/_tail.html", "\n");
    put(
        root,
        "research/sources/010-works-cited/0001-key-a.html",
        "<h3 id=\"key-a\"><code>key-a</code></h3>\n<p>Write-up A.</p>\n",
    );
    let _ = std::fs::remove_file(root.join("research/sources/010-works-cited/README.md"));
}
