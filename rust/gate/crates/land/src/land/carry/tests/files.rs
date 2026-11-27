//! The carry's rules for files outside a feature's spec directory (451 T300, part 2): the generated target page regenerated, a
//! prose hunk merged by words, two added blocks kept both, a line-per-record file's records kept - each a stop of 2026-11-26 the
//! session resolved by hand (`dev/measurements/2026-11-26/carry-replay/`).

use std::path::{Path, PathBuf};

use l7r_shared::tempdir::TempDir;

use super::super::super::tests::has;
use super::super::words::Prose;
use super::super::{added, records, words};
use super::{carried, commit, git, trees};

const PAGE: &str = "docs/make-targets.html";
const ALPHA: &str = "alpha:  ## [project] does alpha\n\t@true\n\n";

fn read(root: &Path, rel: &str) -> String {
    std::fs::read_to_string(root.join(rel)).unwrap()
}

/// Files both trees changed from one base - each `(path, [base, the clone's, the builder's])` - the builder's commit holding a code
/// file too: the clone and the carry's reply.
fn met(tag: &str, files: &[(&str, [&str; 3])]) -> (TempDir, PathBuf, (i32, String, String)) {
    let (dir, root, builder) = trees(tag);
    let side =
        |n: usize| -> Vec<(&str, &str)> { files.iter().map(|(rel, t)| (*rel, t[n])).collect() };
    commit(&root, "the base", &side(0));
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    let mut theirs = side(2);
    theirs.push(("rust/held.rs", "fn held() {}\n"));
    commit(&builder, "T9: built", &theirs);
    commit(&root, "landed here first", &side(1));
    let said = carried(&root, &builder);
    (dir, root, said)
}

/// A target's block of a Makefile.
fn target(name: &str) -> String {
    format!(
        "# {name}'s own comment\n.PHONY: {name}\n{name}:  ## [project] does {name}\n\t@true\n\n"
    )
}

#[test]
fn the_generated_page_is_regenerated_from_the_merged_makefile_never_merged() {
    // RED FIRST (451 T300, 2026-11-26): before the page's rule this carry exits 2 on `Makefile` and `docs/make-targets.html` -
    // the stop of T274, T285, T334 and T336's carries. The shape of 022170716b against b1d4a453fe's parent: each tree added a
    // target's block at one place of the Makefile and regenerated the page from its own
    let (ours, theirs) = (target("sampler"), target("builder-brief"));
    let (_dir, root, (code, out, err)) = met(
        "carry-page",
        &[
            (
                "Makefile",
                [
                    ALPHA,
                    &format!("{ALPHA}{ours}"),
                    &format!("{ALPHA}{theirs}"),
                ],
            ),
            (
                PAGE,
                [
                    "the base's page\n",
                    "the clone's page\n",
                    "the builder's page\n",
                ],
            ),
        ],
    );
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert_eq!(out.lines().count(), 1);
    has(
        &out,
        "; resolved Makefile (both sides' added blocks), docs/make-targets.html (regenerated)\n",
    );
    assert_eq!(read(&root, "Makefile"), format!("{ALPHA}{ours}{theirs}"));
    assert_eq!(l7r_gate_cohort::make_docs::check(&root).code, 0);
    let page = read(&root, PAGE);
    assert!(page.contains("sampler") && page.contains("builder-brief"));
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn a_page_regenerated_to_the_clones_own_text_is_still_verified() {
    // RED FIRST: the end's check held a non-spec file of the commit to "moved by the carry, or at the commit's content" - a page
    // regenerated to what the clone already held is neither (the handoff's `missing()` trap)
    let (dir, root, builder) = trees("carry-page-ours");
    commit(
        &root,
        "the base",
        &[("Makefile", ALPHA), (PAGE, "the base's page\n")],
    );
    git(&builder, &["merge", "-q", "--ff-only", "main"]);
    commit(
        &builder,
        "T9: built",
        &[(PAGE, "the builder's stale page\n")],
    );
    assert_eq!(l7r_gate_cohort::make_docs::write(&root).code, 0);
    let current = read(&root, PAGE);
    commit(&root, "the page regenerated here", &[]);
    let (code, out, err) = carried(&root, &builder);
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(
        &out,
        "its 1 non-spec file(s) in HEAD; resolved docs/make-targets.html (regenerated)\n",
    );
    assert_eq!(read(&root, PAGE), current);
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
    drop(dir);
}

#[test]
fn prose_lines_both_sides_added_words_to_are_merged_by_words() {
    // RED FIRST: before the word merge this carry exits 2 on all three files. The shapes: `rust/gate/CLAUDE.md`'s `task` row
    // (022170716b against b1d4a453fe's parent), the Makefile's `builder-tree:` help line and a module's `//!` line (7037420458
    // against f5007f94d3's parent) - one long line each side added words to
    let row = "| crate | what |\n|---|---|\n| `task` | the task gate: `tick` (`tick.rs`) and `task-add` (`add.rs`) |\n| `land` | the landing |\n";
    let help = "builder-tree:   ## [project] a builder's worktree from the pool: a free tree held by the task   T=<task>\n\t@true\n";
    let doc =
        "//! The pool: a tree is handed out warm and released at the landing.\nfn pool() {}\n";
    let ours = |text: &str| {
        text.replace("(`tick.rs`)", "(`tick.rs`, its `--resolve` kept as a form)")
            .replace("held by the task", "held by the task (feature 451 T285)")
            .replace("out warm", "out warm (451 T285)")
    };
    let theirs = |text: &str| {
        text.replace(
            "(`add.rs`)",
            "(`add.rs`) and `builder-tree` (`builder_tree.rs`, T285)",
        )
        .replace("a free tree", "a free tree brought to HEAD")
        .replace("The pool:", "The pool of the clone:")
    };
    let both = |text: &str| theirs(&ours(text));
    let (_dir, root, (code, out, err)) = met(
        "carry-words",
        &[
            ("Makefile", [help, &ours(help), &theirs(help)]),
            ("rust/gate/CLAUDE.md", [row, &ours(row), &theirs(row)]),
            ("rust/pool.rs", [doc, &ours(doc), &theirs(doc)]),
        ],
    );
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    assert_eq!(out.lines().count(), 1);
    has(
        &out,
        "; resolved Makefile (by words), rust/gate/CLAUDE.md (by words), rust/pool.rs (by words)\n",
    );
    for (rel, base) in [
        ("Makefile", help),
        ("rust/gate/CLAUDE.md", row),
        ("rust/pool.rs", doc),
    ] {
        assert_eq!(read(&root, rel), both(base), "{rel}");
    }
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn lines_one_side_added_beside_a_line_the_other_reworded_are_merged_by_words_and_a_list_takes_both_bullets(
) {
    // RED FIRST: this carry exits 2 on both files. `scripts/container/builder-brief.md` in 022170716b's carry: the clone added a
    // bullet above the line the builder reworded (ours 3 lines, the base 1, theirs 1); and a list each tree appended a bullet to
    let brief = "- Two builders at once.\n- A builder FILES what it found (451 T289; the block's line): `make task-add` allots the\n  id under the feature's lock.\n";
    let sampler = "- The sampler starts with a handout: `make builder-tree` starts it where none runs, and\n  the shell loop is retired (451 T274).\n";
    let ours = brief.replace("- A builder", &format!("{sampler}- A builder"));
    let theirs = brief.replace(
        "block's line)",
        "block's line, and this file's last paragraph)",
    );
    let list = "# Notes\n\n- one\n- two\n";
    let (_dir, root, (code, out, err)) = met(
        "carry-mixed",
        &[
            ("docs/brief.md", [brief, &ours, &theirs]),
            (
                "docs/list.md",
                [
                    list,
                    &format!("{list}- three, the clone's\n"),
                    &format!("{list}- four, the builder's\n  with its second line\n"),
                ],
            ),
        ],
    );
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(
        &out,
        "; resolved docs/brief.md (by words), docs/list.md (both sides' added blocks)\n",
    );
    assert_eq!(
        read(&root, "docs/brief.md"),
        ours.replace(
            "block's line)",
            "block's line, and this file's last paragraph)"
        )
    );
    assert_eq!(
        read(&root, "docs/list.md"),
        format!("{list}- three, the clone's\n- four, the builder's\n  with its second line\n")
    );
}

#[test]
fn words_both_sides_changed_stop_and_nothing_is_resolved() {
    let row = "| `task` | the task gate: `tick` (`tick.rs`) |\n";
    let list = "- one\n";
    let (_dir, root, (code, out, err)) = met(
        "carry-words-stop",
        &[
            ("docs/list.md", [list, "- one\n- two\n", "- one\n- three\n"]),
            (
                "docs/row.md",
                [
                    row,
                    &row.replace("gate:", "gate (T1):"),
                    &row.replace("gate:", "gate (T2):"),
                ],
            ),
        ],
    );
    assert_eq!((code, out.as_str()), (2, ""), "{err}");
    has(&err, "a conflict this command does not resolve, in docs/row.md (both sides changed the same words: `gate:`) - nothing was resolved\n");
    assert!(read(&root, "docs/list.md").contains("<<<<<<<"));
    assert!(root.join(".git/CHERRY_PICK_HEAD").exists());
}

#[test]
fn a_line_per_record_file_keeps_both_sides_appended_records_and_drops_what_either_pruned() {
    // RED FIRST: this carry exits 2 on both files. `dev/claims-triage-skips.jsonl` (a480ff8848 against 240c7d89f9's parent: each
    // tree appended records, one of the clone's the very line the builder appended) and `dev/gm-attribution-baseline.jsonl`
    // (1bd5b1721d against e3922827ac's parent: each tree pruned its own records of one stretch)
    let line = |n: u32| format!("{{\"n\": {n}}}\n");
    let of = |ns: &[u32]| ns.iter().map(|n| line(*n)).collect::<String>();
    let (_dir, root, (code, out, err)) = met(
        "carry-records",
        &[
            (
                "dev/pruned.jsonl",
                [
                    &of(&[1, 2, 3, 4, 5, 6]),
                    &of(&[1, 4, 5, 6]),
                    &of(&[1, 2, 3, 6]),
                ],
            ),
            (
                "dev/skips.jsonl",
                [&of(&[1, 2]), &of(&[1, 2, 3, 3]), &of(&[1, 2, 3])],
            ),
        ],
    );
    assert_eq!((code, err.as_str()), (0, ""), "{out}");
    has(&out, "; resolved dev/pruned.jsonl (both sides' records), dev/skips.jsonl (both sides' records)\n");
    assert_eq!(read(&root, "dev/pruned.jsonl"), of(&[1, 6]));
    assert_eq!(read(&root, "dev/skips.jsonl"), of(&[1, 2, 3, 3, 3]));
    assert_eq!(git(&root, &["status", "--porcelain"]), "");
}

#[test]
fn a_page_that_cannot_be_regenerated_and_a_file_with_no_rule_stop_with_the_pick_standing() {
    // no Makefile to generate the page from
    let (_dir, root, (code, out, err)) = met(
        "carry-page-stop",
        &[(
            PAGE,
            [
                "the base's page\n",
                "the clone's page\n",
                "the builder's page\n",
            ],
        )],
    );
    assert_eq!((code, out.as_str()), (2, ""), "{err}");
    has(&err, "carry: docs/make-targets.html was not regenerated, the pick's other conflicts resolved and staged - make-docs: no Makefile at ");
    has(&err, " - regenerate it (`make docs`), `git add` it and `git -c core.editor=true cherry-pick --continue`\n");
    assert!(root.join(".git/CHERRY_PICK_HEAD").exists());
    let (_dir, root, (code, _, err)) =
        met("carry-no-rule", &[("notes.txt", ["a\n", "b\n", "c\n"])]);
    assert_eq!(code, 2);
    has(
        &err,
        "in notes.txt (a file the carry has no rule for) - nothing was resolved\n",
    );
    assert!(read(&root, "notes.txt").contains("<<<<<<<"));
}

#[test]
fn a_files_kind_is_read_from_its_name() {
    let kinds: Vec<Option<Prose>> = [
        "Makefile",
        "rust/gate/Makefile",
        "docs/a.md",
        "rust/a.rs",
        "dev/a.jsonl",
        "LICENSE",
    ]
    .iter()
    .map(|path| words::kind(path))
    .collect();
    let (make, md, rs) = (
        Some(Prose::Makefile),
        Some(Prose::Markdown),
        Some(Prose::Rust),
    );
    assert_eq!(kinds, [make, make, md, rs, None, None]);
}

#[test]
fn words_are_merged_only_in_prose_and_never_by_choosing() {
    let md =
        |base: &str, ours: &str, theirs: &str| words::merged(base, ours, theirs, Prose::Markdown);
    assert_eq!(words::tokens("a  b\n c"), ["a", "  ", "b", "\n ", "c"]);
    assert!(words::tokens("").is_empty());
    // the same change made by both sides is made once, beside one only the builder made
    assert_eq!(
        md("one two three\n", "one 2 three\n", "one 2 three four\n"),
        Ok("one 2 three four\n".to_owned())
    );
    // each side's words added at one point are both kept, the clone's first
    assert_eq!(
        md("one |\n", "one ours |\n", "one theirs |\n"),
        Ok("one ours theirs |\n".to_owned())
    );
    // one side's insertion inside what the other replaced stops; beside it (the words between unchanged), both are made
    let inside = md(
        "one two three four\n",
        "one two 2.5 three four\n",
        "one 2 four\n",
    );
    assert_eq!(
        inside,
        Err("both sides changed the same words: `three`".to_owned())
    );
    let beside = md(
        "one two three four\n",
        "one two 2.5 three four\n",
        "one 2 3 four\n",
    );
    assert_eq!(beside, Ok("one 2 2.5 3 four\n".to_owned()));
    // a Makefile: a comment line and a help line are prose, a recipe's line and a variable's are not, and a help line keeps its target
    let make =
        |base: &str, ours: &str, theirs: &str| words::merged(base, ours, theirs, Prose::Makefile);
    assert_eq!(
        make(
            "# why\na: b  ## does a\n",
            "# why, said\na: b  ## does a\n",
            "# why\na: b  ## does a well\n"
        ),
        Ok("# why, said\na: b  ## does a well\n".to_owned())
    );
    assert_eq!(
        make(
            "a: b  ## does a\n",
            "a: b c  ## does a\n",
            "a: b  ## does a well\n"
        ),
        Err("a side changed a help line's target, not only its words".to_owned())
    );
    for code in ["\t@true\n", "X := 1\n", "\n"] {
        let stop = make(code, "# ours\n", "# theirs\n");
        assert_eq!(
            stop,
            Err(format!("a line that is not prose: `{}`", code.trim()))
        );
    }
    // a Rust source: an indented comment is prose
    let rust = words::merged(
        "    // a b\n",
        "    // a b c\n",
        "    // z a b\n",
        Prose::Rust,
    );
    assert_eq!(rust, Ok("    // z a b c\n".to_owned()));
}

/// A diff3 merge's text: `plain`, then one conflict of the three sides.
fn conflict(plain: &str, ours: &str, base: &str, theirs: &str) -> String {
    format!("{plain}<<<<<<< ours\n{ours}||||||| base\n{base}=======\n{theirs}>>>>>>> theirs\n")
}

#[test]
fn added_blocks_are_kept_both_only_where_the_files_kind_says_what_a_block_is() {
    let make =
        |ours: &str, theirs: &str| added::merged(&conflict("", ours, "", theirs), Prose::Makefile);
    // no blank line where neither side ended with one
    assert_eq!(
        make("a:  ## does a\n\t@true\n", "b:  ## does b\n\t@true\n"),
        Ok((
            "a:  ## does a\n\t@true\n\nb:  ## does b\n\t@true\n".to_owned(),
            "both sides' added blocks"
        ))
    );
    assert_eq!(
        make("a:\n\t@true\n", "# a comment\n"),
        Err("both sides added lines at one place, not each a target's whole block".to_owned())
    );
    assert_eq!(
        make("a:\n\t@true\n", "\t@false\nb:\n"),
        Err("both sides added lines at one place, not each a target's whole block".to_owned())
    );
    assert_eq!(
        make("a:\n\t@true\n", "b:\n\t@true\na: b\n"),
        Err("both sides added the target `a`".to_owned())
    );
    let rust = added::merged(&conflict("", "fn a() {}\n", "", "fn b() {}\n"), Prose::Rust);
    assert_eq!(
        rust,
        Err("both sides added lines at one place of a source file".to_owned())
    );
    // a file with a hunk of each kind names both rules
    let text = conflict("# Notes\n", "- one, ours\n", "", "- two, theirs\n")
        + &conflict("\nplain\n", "a b c\n", "a b\n", "z a b\n");
    assert_eq!(
        added::merged(&text, Prose::Markdown),
        Ok((
            "# Notes\n- one, ours\n- two, theirs\n\nplain\nz a b c\n".to_owned(),
            "by words and both sides' added blocks"
        ))
    );
}

#[test]
fn a_record_changed_in_place_or_added_inside_the_file_stops() {
    let stop = Err("a record changed in place or added inside the file, not appended".to_owned());
    assert_eq!(
        records::merged("1\n2\n3\n", "1\n2\n3\n4\n", "1\ntwo\n3\n"),
        stop
    );
    assert_eq!(records::merged("1\n2\n", "0\n1\n2\n", "1\n2\n3\n"), stop);
    // the last record changed where it stood: no append, and the other side's appended record would stand before it
    assert_eq!(records::merged("1\n2\n", "1\n3\n", "1\n2\n4\n"), stop);
    assert_eq!(records::merged("1\n", "", ""), Ok(String::new()));
}
