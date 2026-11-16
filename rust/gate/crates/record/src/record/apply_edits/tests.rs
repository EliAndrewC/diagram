//! Applying a check's EDIT and GLOSSARY blocks, and the round's settling (feature 449 T145; the T145 differential holds them to
//! `apply_edits.py` on the real record, these tests every branch on the testkit's).

use std::os::unix::fs::PermissionsExt as _;
use std::path::Path;

use l7r_gate_core::record::testkit::{edit_everything, put, record, NOTES, PAGE};

use super::{blocks, cli, Block};

const ONCE: &str = "<p>A short way apart.<sup class=\"fn\" data-note=\"k\"></sup> More here.</p>";

/// A scratch record's own file, spelled so the pointer check does not read it as a built page of the real record.
fn scratch(name: &str) -> String {
    format!("research/{name}.html")
}

fn edit(path: &str, old: &str, new: Option<&str>) -> String {
    let mut s = format!("EDIT {path}\n<<<\n{old}\n===\n");
    if let Some(n) = new {
        s.push_str(n);
        s.push('\n');
    }
    s + ">>>\n"
}

fn run(root: &Path, reply: &str, extra: &[&str]) -> l7r_gate_core::Reply {
    put(root, "reply.md", reply);
    let mut args = vec![
        "reply.md".to_owned(),
        "--root".to_owned(),
        root.to_string_lossy().into_owned(),
    ];
    args.extend(extra.iter().map(|s| (*s).to_owned()));
    cli(&args, root)
}

fn page(root: &Path) -> String {
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
    let line = "<p>An unmarked claim.</p>";
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, line, None)),
        &[],
    );
    assert!(!page(&root).contains(line) && !page(&root).contains("\n\n"));
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, "More here.", None)),
        &[],
    );
    run(
        &root,
        &format!("record-format: 0094\n{}", edit(PAGE, "A short", Some(""))),
        &[],
    );
    assert!(page(&root).contains("<p>\n\n way apart"), "{}", page(&root));
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
#[expect(
    clippy::too_many_lines,
    reason = "one round through every way it settles, in order"
)]
fn a_round_settles_and_a_reply_with_no_check_says_so() {
    let root = record("apply-edits-round");
    edit_everything(&root);
    let kyakhta =
        "<p>A short distance apart.<sup class=\"fn\" data-note=\"k\"></sup> More here, now.</p>";
    let current = page(&root);
    let old = current
        .lines()
        .find(|l| l.contains("A short distance apart"))
        .unwrap()
        .to_owned();
    let none = run(
        &root,
        &format!(
            "a reply with no counts line\n{}",
            edit(PAGE, &old, Some(kyakhta))
        ),
        &[],
    );
    assert!(none
        .stdout
        .contains("apply-edits: the reply names no check, so the units it answered stay owed"));
    let back = run(
        &root,
        &format!(
            "quote-check: 0094 - 1 finding\n{}",
            edit(PAGE, kyakhta, Some(&old))
        ),
        &[],
    );
    assert!(
        back.stdout
            .contains("apply-edits: the quote-check round's own EDITs, applied verbatim:"),
        "{}",
        back.stdout
    );
    // a record-format round reads the prepass, which needs the registry assembled; this record's has no front matter
    let unread = run(
        &root,
        &format!(
            "record-format: 0094 - 1 finding\n{}",
            edit(PAGE, &old, Some(kyakhta))
        ),
        &[],
    );
    assert!(
        unread
            .stdout
            .contains("apply-edits: could not read the round's units (RecordError: "),
        "{}",
        unread.stdout
    );
    run(
        &root,
        &format!("quote-check: 0094\n{}", edit(PAGE, kyakhta, Some(&old))),
        &[],
    );
    std::fs::write(root.join(PAGE), current.replace(&old, kyakhta)).unwrap();
    let hand = run(
        &root,
        &format!("quote-check: 0094 - 1\n{}", edit(PAGE, &old, Some(kyakhta))),
        &[],
    );
    assert!(hand
        .stdout
        .contains("found applied by hand - settled through its reply"));
    let notes = std::fs::read_to_string(root.join(NOTES)).unwrap();
    let note_line = notes
        .lines()
        .find(|l| l.contains("data-note=\"n\""))
        .unwrap()
        .to_owned();
    let moved = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(NOTES, &note_line, Some(&note_line.replace("<li", "<li  ")))
        ),
        &[],
    );
    assert_eq!(moved.code, 0, "{}", moved.stdout);
    let skipped = run(
        &root,
        &format!("quote-check: x\n{}", edit(PAGE, "no such", Some("x"))),
        &["--skip", "1"],
    );
    assert!(skipped.stdout.contains("  1. skipped (--skip)"));
    assert_eq!(run(&root, "quote-check: x\n", &[]).code, 2);
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(PAGE, "a", Some("b"))),
            &["--skip", "1,x"]
        )
        .code,
        1
    );
    assert_eq!(cli(&["none.md".to_owned()], &root).code, 1);
    assert_eq!(cli(&[], &root).code, 2);
    assert_eq!(cli(&["r".to_owned(), "--bogus".to_owned()], &root).code, 2);
    std::fs::remove_dir_all(root.join(".git")).unwrap();
    let plain = run(
        &root,
        &format!("quote-check: 0094\n{}", edit(PAGE, kyakhta, Some(&old))),
        &[],
    );
    assert!(!plain.stdout.contains("round's own EDITs"));
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
fn assemblable(root: &Path) {
    put(root, "research/sources/_front.html", "<h1>Sources</h1>\n");
    put(root, "research/sources/_tail.html", "\n");
    put(
        root,
        "research/sources/010-works-cited/0001-key-a.html",
        "<h3 id=\"key-a\"><code>key-a</code></h3>\n<p>Write-up A.</p>\n",
    );
    let _ = std::fs::remove_file(root.join("research/sources/010-works-cited/README.md"));
}

#[test]
fn a_round_settles_what_its_blocks_alone_moved() {
    use crate::record::owed::{self, answers};
    let root = record("apply-edits-settle");
    edit_everything(&root);
    assemblable(&root);
    let store = answers::store(&root);
    let research: Vec<(String, String)> =
        owed::fingerprints(&root, &["modal-accuracy".to_owned()]).unwrap();
    for (slug, fp) in &research {
        answers::write_answer(&store, slug, fp, "1 finding", None).unwrap();
    }
    let well = l7r_gate_core::record::testkit::WELL;
    let depiction = run(
        &root,
        &format!(
            "modal-depiction: well - 1 finding\n{}",
            edit(well, "It is deep.", Some("It is very deep."))
        ),
        &[],
    );
    assert!(depiction.stdout.contains("modal-accuracy:hamlet/well: settled with its answer - the modal-depiction round's blocks alone moved it (it runs before them)"), "{}", depiction.stdout);
    assert!(depiction.stdout.contains(
        "modal-gaps:hamlet/well: still owed - not answered at the words before these blocks"
    ));
    let quotes: Vec<(String, String)> =
        owed::fingerprints(&root, &["quote-check".to_owned()]).unwrap();
    for (slug, fp) in quotes.iter().take(1) {
        answers::write_answer(&store, slug, fp, "0 findings", None).unwrap();
    }
    let notes = std::fs::read_to_string(root.join(NOTES)).unwrap();
    let blocks: String = notes
        .lines()
        .filter(|l| l.starts_with("<li"))
        .map(|l| edit(NOTES, l, Some(&l.replace("</li>", " Grounds: more.</li>"))))
        .collect();
    let format = run(
        &root,
        &format!(
            "record-format: 0094 - 2 findings\n{blocks}{}",
            edit(PAGE, "More here.", Some("More here. Grounds: added."))
        ),
        &[],
    );
    assert!(format.stdout.contains("record-format:0094: still owed - its prepass now raises Grounds:, added, grounds, which the round never ruled on"), "{}", format.stdout);
    assert!(format.stdout.contains(
        "quote-check:0094#k: settled - another check's fix, outside its quotation and its claim"
    ));
    assert!(format.stdout.contains(
        "quote-check:0094#n: still owed - not answered at the words before these blocks"
    ));
    let calm = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More here. Grounds: added.", Some("More here."))
        ),
        &[],
    );
    assert!(
        calm.stdout
            .contains("record-format:0094: settles when `make record-checked` records this round"),
        "{}",
        calm.stdout
    );
    // a round whose answer already stands at the words before its blocks settles with it
    let kept = page(&root);
    for (slug, fp) in owed::fingerprints(&root, &["record-format".to_owned()]).unwrap() {
        answers::write_answer(&store, &slug, &fp, "1 finding", None).unwrap();
    }
    let answered = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(PAGE, "More here.", Some("Here."))
        ),
        &[],
    );
    assert!(
        answered
            .stdout
            .contains("record-format:0094: settled with its answered round"),
        "{}",
        answered.stdout
    );
    std::fs::write(root.join(PAGE), kept).unwrap();
    let inside: String = std::fs::read_to_string(root.join(NOTES))
        .unwrap()
        .lines()
        .filter(|l| l.contains("data-note=\"n\""))
        .map(|l| edit(NOTES, l, Some(&l.replace("\"new\"", "\"newer\""))))
        .collect();
    let moved = run(&root, &format!("intro-check: 0094 - 1\n{inside}"), &[]);
    assert!(
        moved
            .stdout
            .contains("quote-check:0094#n: still owed - its quotation or its claim changed"),
        "{}",
        moved.stdout
    );
}

#[test]
#[expect(
    clippy::too_many_lines,
    reason = "the rarer paths of a run, one after another on one record"
)]
fn the_rarer_paths_of_a_run() {
    let root = record("apply-edits-rare");
    assemblable(&root);
    assert_eq!(
        super::round::named("plain words"),
        "ValueError: plain words"
    );
    assert_eq!(super::round::named("KeyError: 'x'"), "KeyError: 'x'");
    // a modal-form EDIT on a record file: no pop-up, so nothing research fixed
    let not_modal = run(
        &root,
        &format!(
            "modal-form: x - 1\n{}",
            edit(PAGE, "More here.", Some("More, here."))
        ),
        &[],
    );
    assert!(not_modal.stdout.contains("applied to 0094-trade.html"));
    put(
        &root,
        "l7r/diagram/interactive/assets/modals/classes/y.md",
        "About: a fixed fact and more.\n",
    );
    super::HELD
        .with(|h| *h.borrow_mut() = Some(vec!["a fixed fact".to_owned(), "and more".to_owned()]));
    let y = "l7r/diagram/interactive/assets/modals/classes/y.md";
    let dropped = run(
        &root,
        &format!(
            "modal-form: y - 1\n{}",
            edit(y, "a fixed fact and more", Some("a fixed fact"))
        ),
        &[],
    );
    assert!(
        dropped.stdout.contains(
            "REFUSED - a modal-form EDIT drops wording a research round fixed ('and more')"
        ),
        "{}",
        dropped.stdout
    );
    let kept = run(
        &root,
        &format!("modal-form: y - 1\n{}", edit(y, "About:", Some("About -"))),
        &[],
    );
    assert!(kept.stdout.contains("applied to y.md"));
    super::HELD.with(|h| *h.borrow_mut() = None);
    // a dry run reads and writes nothing
    let dry = run(
        &root,
        &format!(
            "quote-check: x\n{}",
            edit(PAGE, "More, here.", Some("More here."))
        ),
        &["--dry-run"],
    );
    assert!(
        dry.stdout.contains("applied to 0094-trade.html") && page(&root).contains("More, here.")
    );
    // a record-format round whose blocks raise no new word settles its unit
    let calm = run(
        &root,
        &format!(
            "record-format: 0094 - 1\nGLOSSARY quiet | | a def\n{}",
            edit(PAGE, "More, here.", Some("More here."))
        ),
        &[],
    );
    assert!(
        calm.stdout
            .contains("apply-edits: 2 block(s), 0 refused - then `make glossary`"),
        "{}",
        calm.stdout
    );
    // another check's fix outside a quotation on a note nothing owed: settled, its earlier answer none
    let note = std::fs::read_to_string(root.join(NOTES))
        .unwrap()
        .lines()
        .find(|l| l.contains("data-note=\"k\""))
        .unwrap()
        .to_owned();
    let fresh = run(
        &root,
        &format!(
            "record-format: 0094 - 1\n{}",
            edit(NOTES, &note, Some(&note.replace("</li>", " Also.</li>")))
        ),
        &[],
    );
    assert!(
        fresh
            .stdout
            .contains("quote-check:0094#k: settled - another check's fix"),
        "{}",
        fresh.stdout
    );
    // the store cannot be written: the round cannot settle, and the edits stand
    let store = crate::record::owed::answers::store(&root);
    let _ = std::fs::remove_dir_all(&store);
    std::fs::write(&store, "a file where the store goes").unwrap();
    let unsettled = run(
        &root,
        &format!(
            "quote-check: 0094 - 1\n{}",
            edit(PAGE, "More here.", Some("More here, now."))
        ),
        &[],
    );
    assert!(unsettled.stdout.contains("could not settle ("));
    std::fs::remove_file(&store).unwrap();
    // a glossary term another clone holds, and a ledger that cannot be read
    std::fs::create_dir_all(root.join(".specify")).unwrap();
    std::fs::write(
        root.join(".specify/prefixes.jsonl"),
        "{\"kind\": \"glossary\", \"key\": \"held\", \"prefix\": 5, \"clone\": \"/elsewhere\"}\n",
    )
    .unwrap();
    assert!(
        run(&root, "record-format: 0094\nGLOSSARY held | | d\n", &[])
            .stdout
            .contains("REFUSED - 'held' is already being defined in /elsewhere")
    );
    std::fs::write(root.join(".specify/prefixes.jsonl"), "[1]\n").unwrap();
    assert_eq!(
        run(&root, "record-format: 0094\nGLOSSARY other | | d\n", &[]).code,
        1
    );
    // files that cannot be read or written
    put(&root, &scratch("bad"), "x");
    std::fs::write(root.join(scratch("bad")), [0xff]).unwrap();
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(&scratch("bad"), "a", Some("b"))),
            &["--dry-run"]
        )
        .code,
        1
    );
    assert_eq!(
        run(
            &root,
            &format!("quote-check: x\n{}", edit(&scratch("bad"), "a", Some("b"))),
            &[]
        )
        .code,
        1
    );
    put(&root, &scratch("locked"), "old\n");
    std::fs::set_permissions(
        root.join(scratch("locked")),
        std::fs::Permissions::from_mode(0o444),
    )
    .unwrap();
    assert_eq!(
        run(
            &root,
            &format!(
                "quote-check: x\n{}",
                edit(&scratch("locked"), "old", Some("new"))
            ),
            &[]
        )
        .code,
        1
    );
    std::fs::write(root.join(scratch("locked2")), "new\n").unwrap();
    std::fs::set_permissions(
        root.join(scratch("locked2")),
        std::fs::Permissions::from_mode(0o444),
    )
    .unwrap();
    assert_eq!(
        run(
            &root,
            &format!(
                "quote-check: x\n{}",
                edit(&scratch("locked2"), "old", Some("new"))
            ),
            &[]
        )
        .code,
        1
    );
}
