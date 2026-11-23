//! What a page edit changed, on small pages: the tool's clears, the pairing, a split's moves and its pointer.

use std::collections::HashSet;

use super::{block_words, claim_words, page_change, pointer_targets, word_diff, Change};

fn none() -> HashSet<String> {
    HashSet::new()
}

fn change(old: &str, fresh: &str) -> Change {
    page_change(old, fresh, &none(), &none(), &[])
}

const MARK: &str = r#"<sup class="fn" data-note="k"></sup>"#;

#[test]
fn a_footnote_marker_a_link_or_a_comment_is_cleared_by_the_tool() {
    let old = format!("<p>The bed was 8 shaku long.{MARK}</p>\n<p>A gate.</p>");
    let fresh = format!(
        "<p>The bed was 8 shaku long.{MARK}<sup class=\"fn\" data-note=\"j\"></sup></p>\n<p>A <a href=\"https://x\">gate</a>.<!-- \
         Evidence: guess --></p>"
    );
    let c = change(&old, &fresh);
    assert!(c.is_clear());
    assert_eq!(c.cleared, 1);
    assert_eq!(claim_words("A [^k] gate ( ) , here [^j]."), "A gate, here.");
}

/// An original-language quotation or term on a question page is not cleared: a corrected character changes what the page says a source
/// says (spec-fidelity MODE 4 on T186, 2026-11-23).
#[test]
fn an_original_language_quotation_or_term_goes_to_the_agent() {
    let c = change(
        "<p>Its name, 大八車, means a big cart.</p>",
        "<p>Its name, 大八輪, means a big cart.</p>",
    );
    assert_eq!(c.pairs.len(), 1);
    assert!(!change("<p>「旧い」</p>", "<p>「新しい」</p>").is_clear());
}

#[test]
fn a_changed_claim_is_paired_with_its_old_self_and_a_new_or_removed_block_is_kept() {
    let old = "<p>The joints were tied with rope at every post.</p>\n<p>A block removed.</p>";
    let fresh =
        "<p>Some joints were tied with rope at every post.</p>\n<p>Something wholly new here.</p>";
    let c = change(old, fresh);
    assert_eq!(
        c.pairs,
        vec![(
            "The joints were tied with rope at every post.".to_owned(),
            "Some joints were tied with rope at every post.".to_owned()
        )]
    );
    assert_eq!(c.added, vec!["Something wholly new here.".to_owned()]);
    assert_eq!(c.removed, vec!["A block removed.".to_owned()]);
    assert!(!c.is_clear());
    assert_eq!(
        word_diff(&c.pairs[0].0, &c.pairs[0].1),
        "[-The-] {+Some+} joints were tied with rope at every post."
    );
    assert_eq!(word_diff("a b c", "a c d"), "a [-b-] c {+d+}");
}

#[test]
fn a_note_key_gone_from_the_page_is_named() {
    let old = format!("<p>One.{MARK}</p><p>Two.{MARK}</p>");
    let c = change(&old, "<p>One.</p><p>Two.</p>");
    assert!(c.is_clear());
    assert_eq!(c.keys_gone, vec!["k".to_owned()]);
    let kept = change(&old, &format!("<p>One.</p><p>Two.{MARK}</p>"));
    assert!(kept.keys_gone.is_empty());
}

#[test]
fn a_block_of_only_markup_is_cleared_new_or_removed() {
    let c = change("<p>Kept.</p>", "<p>Kept.</p><p><b> </b>[^k]</p>");
    assert!(c.is_clear());
    assert_eq!(c.cleared, 1);
}

#[test]
fn a_split_with_its_pointer_re_owes_nothing() {
    let moved = "Staff lived in the town at one domain's distant office.";
    let old = format!("<p>Rowhouses stood inside.</p>\n<p>{moved}</p>");
    let fresh = "<p>Rowhouses stood inside.</p>\n<p>Where the staff lived is now told at <a class=\"moved\" \
                 href=\"0331-where-staff-lived.html\">Where an office's staff lived</a>.</p>";
    let dest = format!("<h2>Where</h2><p>{moved}</p>");
    assert_eq!(
        pointer_targets(fresh),
        vec!["research/questions/0331-where-staff-lived.html".to_owned()]
    );
    let c = page_change(&old, fresh, &block_words(&dest), &none(), &[]);
    assert!(c.is_clear(), "{c:?}");
    assert_eq!((c.moved, c.cleared), (1, 1));
    // on HEAD the same split sent the pointer and the removal to the agent
    let blind = change(&old, fresh);
    assert!(!blind.is_clear() && blind.removed == vec![moved.to_owned()]);
}

#[test]
fn a_pointer_appended_to_a_block_or_a_block_moved_in_is_cleared() {
    let old = "<p>Its staff lived in the town.</p>";
    let fresh =
        "<p>Its staff lived in the town (<a class=\"moved\" href=\"0331-w.html\">where</a>).</p>";
    assert!(change(old, fresh).is_clear());
    let before: HashSet<String> = ["A block from the old page.".to_owned()].into();
    let c = page_change(
        "",
        "<p>A block from the old page.</p>",
        &none(),
        &before,
        &[],
    );
    assert!(c.is_clear() && c.moved == 1);
}

#[test]
fn a_pointer_carrying_a_figure_or_a_long_claim_goes_to_the_agent() {
    let link = "<a class=\"moved\" href=\"0331-w.html\">where</a>";
    for text in [
        format!("<p>About 12 by 18 ft, told at {link}.</p>"),
        format!("<p>One two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen twenty twentyone twentytwo twentythree twentyfour twentyfive twentysix, {link}.</p>"),
        format!("<p>Told at {link}.{MARK}</p>"),
    ] {
        assert!(!change("", &text).is_clear(), "{text}");
    }
}

#[test]
fn a_block_moved_with_no_pointer_is_a_removal_named_with_its_page() {
    let old = "<p>Kept.</p><p>Moved away.</p>";
    let there: HashSet<String> = ["Moved away.".to_owned()].into();
    let c = page_change(
        old,
        "<p>Kept.</p>",
        &none(),
        &none(),
        &[("research/questions/0331-w.html".to_owned(), there)],
    );
    assert_eq!(c.removed, vec!["Moved away.".to_owned()]);
    assert_eq!(
        c.unpointed,
        vec![(
            "Moved away.".to_owned(),
            "research/questions/0331-w.html".to_owned()
        )]
    );
}

#[test]
fn the_replay_sorts_recorded_edits_into_cleared_and_sent() {
    let edits = serde_json::json!([
        {"id": "E1", "file": "q/0001-a.notes.html", "oldraw": "<li>x</li>", "newraw": "<li>y</li>"},
        {"id": "E2", "file": "q/0001-a.html", "oldraw": "<p>A gate.</p>", "newraw": "<p>A <a href=\"u\">gate</a>.<!-- c --></p>"},
        {"id": "E3", "file": "q/0001-a.drawing.html", "oldraw": "<p>The joints.</p>", "newraw": "<p>Some joints.</p>"},
    ]);
    let out = super::replay(&edits.to_string()).unwrap();
    assert_eq!(
        out,
        "E1\tcleared\tno pop-up reads it (Entry: and Drawing: name question and drawing pages)\nE2\tcleared\tno claim word changed (comment, markup, link or marker)\nE3\tsent\tits claim words changed\n"
    );
    assert!(super::replay("{").is_err());
}

#[test]
fn a_changed_block_pairs_with_its_closest_old_self() {
    let old = "<p>The joints were tied with rope at each post here.</p><p>The joints were tied with rope at every post.</p>";
    let c = change(old, "<p>Some joints were tied with rope at every post.</p>");
    assert_eq!(
        c.pairs[0].0,
        "The joints were tied with rope at every post."
    );
    assert_eq!(c.removed.len(), 1);
}

#[test]
fn a_claims_triage_reads_what_a_pointer_reaches() {
    let dir = std::env::temp_dir().join(format!("t185-reach-{}", std::process::id()));
    std::fs::create_dir_all(&dir).unwrap();
    std::fs::write(dir.join("0331-w.html"), "<p>Moved here.</p>").unwrap();
    let html = "<p>Now at <a class=\"moved\" href=\"0331-w.html\">where</a>.</p>";
    let reached = super::reached_by_pointers(html, &dir);
    assert!(reached.contains("Moved here."));
    assert!(super::is_pointer_block("Now at where.", html));
    assert!(!super::is_pointer_block("A claim of 12 ft.", html));
    let _ = std::fs::remove_dir_all(&dir);
}

#[test]
fn the_echo_rule_fires_only_on_changed_words_the_pop_up_repeats() {
    let none = none();
    let old = vec!["The residence stood beside the office, on the lot to the west.".to_owned()];
    let now = vec!["The residence stood at the back of the office.".to_owned()];
    let pop = "The residence stood beside the office.";
    assert!(super::echo(&old, &now, &none, pop).is_some());
    assert!(super::echo(&old, &now, &none, "The residence stood at the back.").is_none());
    // a sentence still standing, here or on a page the reader reaches, is no change
    let reached: HashSet<String> = old.iter().cloned().collect();
    assert!(super::echo(&old, &now, &reached, pop).is_none());
    // words inserted mark their neighbors; a sentence with nothing near it is changed whole
    let grown = vec!["The joints were tied with rope.".to_owned()];
    let longer = vec!["The joints were often tied with rope.".to_owned()];
    assert!(super::echo(&grown, &longer, &none, "the joints were tied").is_some());
    assert!(super::echo(&grown, &[], &none, "were tied with rope").is_some());
}

#[test]
fn a_new_finding_fires_where_the_pop_up_states_a_single_case() {
    let old = "<li><strong>Old.</strong> x</li>";
    let fresh = "<li><strong>Old.</strong> x</li><li> <strong>New finding.</strong> y</li>";
    let found = super::new_findings(old, fresh);
    assert_eq!(found, vec!["New finding.".to_owned()]);
    let c = change("", "<p>A new block of words.</p>");
    let none = none();
    let why = super::fires(&c, &[], &none, "It rests on the one case found.", &found).unwrap();
    assert!(why.starts_with("a new finding (\"New finding.\")"));
    assert!(super::fires(&c, &[], &none, "Its walls are not recorded.", &found).is_none());
    assert!(super::fires(&c, &[], &none, "It rests on the one case found.", &[]).is_none());
    let gone = Change {
        keys_gone: vec!["k".to_owned()],
        ..Change::default()
    };
    assert!(super::fires(&gone, &[], &none, "", &[])
        .unwrap()
        .contains("Sources key k"));
    assert!(super::says_absence("Every plan draws it."));
}
