//! A split adds its target to each pop-up whose `Drawing:` names the source and whose Depiction states a moved block, and owes
//! nothing (451 T234): P3b's pair, `hamlet/paddy` and 0005's rice-shoots section moved to 0346, in a scratch record.

use std::path::Path;

use super::{apply, owed_links, with_links};
use crate::record::modals::{depiction_fingerprint, modals_now, owed, Modal, DEPICTION_CHECK};
use crate::record::owed::answers;
use crate::record::testkit::{commit, git, put, record};

const PADDY: &str = "l7r/diagram/interactive/assets/modals/hamlet/paddy.md";
const STRIP: &str = "l7r/diagram/interactive/assets/modals/choice/plot_size--strip.md";
const SOURCE: &str = "research/questions/0005-rice-paddies-and-their-plots-suiden.drawing.html";
const TARGET: &str =
    "research/questions/0346-how-our-maps-draw-the-rice-inside-a-paddy.drawing.html";

/// 0005's drawing page after the split: its own rule, then the pointer P3b left.
const SOURCE_AFTER: &str = "<h2>How our maps draw rice paddies and their plots (suiden)</h2>\n<ul>\n<li><strong>Each basin is drawn small.</strong><br>The basins are drawn at their real size in feet, never the large rectangles of modern land consolidation.</li>\n</ul>\n<p>How the rice inside the bunds is drawn is at <a class=\"moved\" href=\"0346-how-our-maps-draw-the-rice-inside-a-paddy.drawing.html\">How our maps draw the rice inside a paddy</a>.</p>\n";

/// 0346 as P3b wrote it, its first three bullets (the moved section's).
const TARGET_TEXT: &str = "<h2 id=\"how-our-maps-draw-the-rice-inside-a-paddy\">How our maps draw the rice inside a paddy</h2>\n<p>How big a paddy is drawn and what shape it takes are at <a href=\"0005-rice-paddies-and-their-plots-suiden.drawing.html\">How our maps draw rice paddies and their plots (suiden)</a>.</p>\n<ul>\n<li><strong>The paddy is drawn with an unruled scatter of shoots.</strong><br>Until row planting came in during the Meiji period, rice was transplanted in \"disorderly planting\", not evenly spaced, so no paddy is drawn in ruled rows.</li>\n<li><strong>The scatter is a sample of the planting, not each plant.</strong><br>At today's spacing of about 30 cm (~12 in) between clumps of seedlings, one dot a plant on a map drawn at one foot to the pixel would be one dot a pixel, a solid fill, not a texture.</li>\n<li><strong>The rice among a polder's fish ponds takes a denser sample.</strong><br>There the shoots stand about 4.5 ft apart, so they land irregularly with no ruled row or column.</li>\n</ul>\n";

fn paddy(drawing: &str) -> String {
    format!("About: A rice paddy.\n\nDepiction: Each basin is drawn small, at its real size in feet. The rice is drawn as a loose scatter of shoots in no ruled\nrows: a sample of the planting, since at its real spacing one dot a plant would fill the basin solid.\n\nName: paddy\nEntry: research/questions/0094-trade.html\nDrawing: {drawing}\n")
}

/// A choice whose Depiction states only 0005's own rule: no shoots, so no link.
fn strip() -> String {
    format!("Name: Strip plots\nAbout: Long strips.\nDepiction: The plots are drawn as long strips, each at its real size in feet.\nDrawing: {SOURCE}\n")
}

fn scene(tag: &str) -> crate::checks::TempDir {
    let root = record(tag);
    put(&root, SOURCE, SOURCE_AFTER);
    put(&root, TARGET, TARGET_TEXT);
    put(&root, PADDY, &paddy(SOURCE));
    put(&root, STRIP, &strip());
    commit(&root, "the split");
    let head = git(&root, &["rev-parse", "HEAD"]);
    put(&root, ".git/refs/remotes/origin/main", &format!("{head}\n"));
    root
}

fn modal(root: &Path, uid: &str) -> Modal {
    modals_now(root, true)
        .unwrap()
        .into_iter()
        .find(|m| m.uid() == uid)
        .unwrap()
}

/// RED FIRST: P3b's pair - `hamlet/paddy` states the moved shoots, so it is owed 0346; the strip choice states none of them.
#[test]
fn a_split_owes_its_target_to_the_pop_up_stating_a_moved_block() {
    let root = scene("split-links-owed");
    assert_eq!(owed_links(&root, &modal(&root, "hamlet/paddy")), [TARGET]);
    assert!(owed_links(&root, &modal(&root, "choice/plot_size--strip")).is_empty());
    // listed already: owed nothing more
    put(&root, PADDY, &paddy(&format!("{SOURCE}, {TARGET}")));
    assert!(owed_links(&root, &modal(&root, "hamlet/paddy")).is_empty());
}

/// The added entry carries the condition of the listed page reaching it; an unconditional listing reaching it too drops it.
#[test]
fn the_link_keeps_its_source_s_condition() {
    let root = scene("split-links-condition");
    put(
        &root,
        PADDY,
        &paddy(&format!("{SOURCE} [winter_crop=none]")),
    );
    assert_eq!(
        owed_links(&root, &modal(&root, "hamlet/paddy")),
        [format!("{TARGET} [winter_crop=none]")]
    );
    let other = "research/questions/0094-trade.drawing.html";
    put(&root, other, SOURCE_AFTER);
    put(
        &root,
        PADDY,
        &paddy(&format!("{SOURCE} [winter_crop=none], {other}")),
    );
    assert_eq!(owed_links(&root, &modal(&root, "hamlet/paddy")), [TARGET]);
}

/// A Depiction sharing fewer than three phrases with the target is not owed it (`hamlet/well`'s two, measured).
#[test]
fn two_shared_phrases_owe_nothing() {
    let root = scene("split-links-two");
    put(
        &root,
        PADDY,
        &paddy(SOURCE).replace(
            " since at its real spacing one dot a plant would fill the basin solid",
            "",
        ),
    );
    assert!(owed_links(&root, &modal(&root, "hamlet/paddy")).is_empty());
}

/// A pop-up with no Depiction, and a pointer to a question page (M14's, not D5's), owe no link.
#[test]
fn no_depiction_or_a_question_target_owes_nothing() {
    let root = scene("split-links-none");
    put(&root, PADDY, &paddy(SOURCE).replace("Depiction:", "Note:"));
    assert!(owed_links(&root, &modal(&root, "hamlet/paddy")).is_empty());
    put(&root, PADDY, &paddy(SOURCE));
    let to_question = SOURCE_AFTER.replace(".drawing.html\">How our", ".html\">How our");
    put(&root, SOURCE, &to_question);
    put(
        &root,
        "research/questions/0346-how-our-maps-draw-the-rice-inside-a-paddy.html",
        TARGET_TEXT,
    );
    assert!(owed_links(&root, &modal(&root, "hamlet/paddy")).is_empty());
}

/// The line is extended where it ends, a continued line too; a file with no `Drawing:` line gains one.
#[test]
fn the_line_gains_the_links_at_its_end() {
    let links = [TARGET.to_owned()];
    assert_eq!(
        with_links("Name: x\nDrawing: a.html\nCovers: y\n", &links),
        format!("Name: x\nDrawing: a.html, {TARGET}\nCovers: y\n")
    );
    assert_eq!(
        with_links("Drawing: a.html,\n  b.html\n\nName: x", &links),
        format!("Drawing: a.html,\n  b.html, {TARGET}\n\nName: x")
    );
    assert_eq!(
        with_links("Drawing: a.html", &links),
        format!("Drawing: a.html, {TARGET}")
    );
    assert_eq!(
        with_links("Name: x\n", &links),
        format!("Name: x\nDrawing: {TARGET}\n")
    );
    assert_eq!(
        with_links("Name: x", &links),
        format!("Name: x\nDrawing: {TARGET}\n")
    );
    assert_eq!(with_links("", &links), format!("Drawing: {TARGET}\n"));
}

/// The tool writes the link and carries the pop-up's answer, so nothing is owed; a hand edit of the same line owes the check.
#[test]
fn the_tool_adds_the_link_and_owes_nothing() {
    let root = scene("split-links-apply");
    let base = git(&root, &["rev-parse", "HEAD"]);
    let store = root.join(".git/record-checks");
    let slug = format!("{DEPICTION_CHECK}:hamlet/paddy");
    let fp = depiction_fingerprint(&root, &modal(&root, "hamlet/paddy")).unwrap();
    answers::write_answer(&store, &slug, &fp, "clean", None).unwrap();
    // by hand: the line changed, the check owed at a fingerprint nothing answered
    put(&root, PADDY, &paddy(&format!("{SOURCE}, {TARGET}")));
    let rows = owed(&root, &base, "hamlet/paddy").unwrap();
    let row = rows.iter().find(|r| r.0 == slug).unwrap();
    assert_eq!(row.1, "its Depiction, Drawing: or Entry: changed");
    assert!(!answers::answered(&store, &slug, &row.2, ""));
    // by the tool
    put(&root, PADDY, &paddy(SOURCE));
    let said = apply(&root, &store).unwrap();
    assert_eq!(said, ["hamlet/paddy: Drawing: gained 0346-how-our-maps-draw-the-rice-inside-a-paddy.drawing.html (a split's target its Depiction states; D5, 451 T234)"]);
    assert_eq!(
        std::fs::read_to_string(root.join(PADDY)).unwrap(),
        paddy(&format!("{SOURCE}, {TARGET}"))
    );
    assert_eq!(std::fs::read_to_string(root.join(STRIP)).unwrap(), strip());
    let rows = owed(&root, &base, "hamlet/paddy").unwrap();
    let row = rows.iter().find(|r| r.0 == slug).unwrap();
    assert!(answers::answered(&store, &slug, &row.2, ""));
    // run again: nothing left to add
    assert!(apply(&root, &store).unwrap().is_empty());
}

/// Unanswered as it stands, the pop-up is left and named: the tool carries an answer, it never makes one, and never turns an owed triage
/// into a full check.
#[test]
fn an_unanswered_pop_up_is_left_and_named() {
    let root = scene("split-links-unanswered");
    let store = root.join(".git/record-checks");
    assert_eq!(
        apply(&root, &store).unwrap(),
        ["hamlet/paddy: Drawing: lacks 0346-how-our-maps-draw-the-rice-inside-a-paddy.drawing.html (a split's target its Depiction states) - left: its modal-depiction is owed, and adds it as a LINKS fix (D5, 451 T234)"]
    );
    assert_eq!(
        std::fs::read_to_string(root.join(PADDY)).unwrap(),
        paddy(SOURCE)
    );
}

/// `make modal-triage` makes the addition after its own clears and says so first.
#[test]
fn the_triage_makes_the_addition() {
    let root = scene("split-links-triage");
    let store = root.join(".git/record-checks");
    let slug = format!("{DEPICTION_CHECK}:hamlet/paddy");
    let fp = depiction_fingerprint(&root, &modal(&root, "hamlet/paddy")).unwrap();
    answers::write_answer(&store, &slug, &fp, "clean", None).unwrap();
    let r = root.to_string_lossy().into_owned();
    let out = root.join("bundle").to_string_lossy().into_owned();
    let said =
        crate::record::triage::cli(&["--root", &r, "bundle", "--out", &out].map(str::to_owned));
    assert_eq!(said.code, 0);
    assert!(
        said.stdout
            .starts_with("modal-triage: hamlet/paddy: Drawing: gained 0346-"),
        "{}",
        said.stdout
    );
    assert_eq!(
        std::fs::read_to_string(root.join(PADDY)).unwrap(),
        paddy(&format!("{SOURCE}, {TARGET}"))
    );
}
