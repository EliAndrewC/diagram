//! What a page edit changed, on small pages: the tool's clears, the pairing, a split's moves and its pointer.

use std::collections::HashSet;

use super::{
    block_words, blocks_change, claim_words, echo_rewritten, follow, md_words, page_change,
    pointer_targets, word_diff, Change,
};

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

/// A new finding's headline is read (the claims' triage passes it), and a cited key gone from the page sends; a single-case phrase in the
/// reader sends nothing by itself (451 T212: the addition rule reads what the new block says).
#[test]
fn a_new_finding_is_read_and_a_key_gone_sends() {
    let old = "<li><strong>Old.</strong> x</li>";
    let fresh = "<li><strong>Old.</strong> x</li><li> <strong>New finding.</strong> y</li>";
    let found = super::new_findings(old, fresh);
    assert_eq!(found, vec!["New finding.".to_owned()]);
    let c = change("", "<p>A new block of words.</p>");
    let none = none();
    assert!(super::fires(&c, &[], &none, "It rests on the one case found.", &found).is_none());
    let gone = Change {
        keys_gone: vec!["k".to_owned()],
        ..Change::default()
    };
    assert!(super::fires(&gone, &[], &none, "", &[])
        .unwrap()
        .contains("Sources key k"));
}

/// Feature 451 T191: a procedure section's Markdown read as a page's words - a link's text kept, ticks and emphasis dropped, a
/// `snake_case` name kept whole - so a markup edit of a section pairs equal and is cleared.
#[test]
fn a_section_s_markdown_reads_as_a_page_s_words() {
    assert_eq!(
        md_words(
            "**Walls** [stand](x.md) `inner_garden` *here* and __there__, ![a](b.png) <b>c</b>."
        ),
        "Walls stand inner_garden here and there, a c."
    );
    assert_eq!(
        md_words("snake_case_name and 2 * 3 * 4"),
        "snake_case_name and 2 * 3 * 4"
    );
    let was = vec![md_words("**Walls** stand.")];
    let c = blocks_change(
        &was,
        &[md_words("Walls `stand`.")],
        &[],
        &none(),
        &none(),
        &[],
    );
    assert!(c.is_clear() && c.keys_gone.is_empty());
}

/// Feature 451 T191: the echo read from a rewrite's new side - a claim repeating the words a rewritten block gained (a label the page
/// now gives) fires; one repeating only words both sides hold does not.
#[test]
fn the_echo_fires_on_words_a_rewrite_gained_that_the_claim_repeats() {
    let c = change(
        "<p>Our maps set the shrine where a household's stood, and give it the tree as well.</p>",
        "<p>Our maps set the shrine where a household's stood. That they give it a tree beside it as well is a GUESS.</p>",
    );
    assert_eq!(c.pairs.len(), 1);
    let hit = echo_rewritten(&c, "the shrine stands in a corner with a tree beside it");
    assert_eq!(
        hit.as_deref(),
        Some("that they give it a tree beside it as well is a guess.")
    );
    assert_eq!(
        echo_rewritten(&c, "our maps set the shrine in a corner"),
        None
    );
}

/// Feature 451 T194, red first (T184's split of 0009 to 0332): a note key whose marked block moved to the page a pointer reaches is
/// not gone; on no page the reader reaches, it is.
#[test]
fn a_note_key_moved_with_its_block_is_not_gone() {
    let old = format!("<p>Kept.</p><p>The rick stood on a barley paddy.{MARK}</p>");
    let fresh = "<p>Kept.</p><p>Now at <a class=\"moved\" href=\"0332-w.html\">where</a>.</p>";
    let dest = format!("<p>The rick stood on a barley paddy.{MARK}</p>");
    let c = page_change(&old, fresh, &block_words(&dest), &none(), &[]);
    assert!(c.keys_gone.is_empty() && c.is_clear(), "{c:?}");
    assert_eq!(change(&old, fresh).keys_gone, vec!["k".to_owned()]);
}

/// Feature 451 T194, red first (T184's split of 0059 to 0333): a sentence moved with a small edit is compared with its moved self, so
/// only its changed words count; an inserted gloss marks its neighbors, the echo rule as written (T184's "(seki)", a measured edge).
#[test]
fn a_sentence_moved_with_an_edit_is_compared_with_its_moved_self() {
    let old = vec!["The yard well was lined with cedar planks long ago.".to_owned()];
    let page_now = vec!["An unrelated sentence of the source page stays.".to_owned()];
    let reached: HashSet<String> =
        ["The yard well was lined with cedar planks in old times.".to_owned()].into();
    assert!(super::echo(&old, &page_now, &reached, "It is lined with cedar planks.").is_none());
    assert!(super::echo(
        &old,
        &page_now,
        &reached,
        "Lined with cedar planks long ago."
    )
    .is_some());
    let first = vec!["The first wells were dug of whatever stone lay near.".to_owned()];
    let glossed: HashSet<String> =
        ["The first wells (ido) were dug of whatever stone lay near.".to_owned()].into();
    assert!(super::echo(
        &first,
        &page_now,
        &glossed,
        "The first wells were dug here."
    )
    .is_some());
}

/// Feature 451 T194: a block moved with an edit is shown as moved, paired with its version on the reached page, and stays owed; one
/// whose only edit is a marker is moved whole; a block on the reached page before is no arrival.
#[test]
fn a_block_moved_with_an_edit_is_paired_with_its_moved_self() {
    let old = "<p>Kept.</p><p>The first wells were dug of whatever stone lay near.</p>";
    let fresh = "<p>Kept.</p><p>Now at <a class=\"moved\" href=\"0332-w.html\">where</a>.</p>";
    let moved = "The first wells were dug of whatever stone lay near.".to_owned();
    let glossed = "The first wells (ido) were dug of whatever stone lay near.".to_owned();
    let farther = "The first wells (ido) were dug of whatever stone lay near here.".to_owned();
    let dest: HashSet<String> = [glossed.clone(), farther, "Far off.".to_owned()].into();
    let c = page_change(old, fresh, &dest, &none(), &[]);
    assert_eq!(c.moved_edited, vec![(moved.clone(), glossed)]);
    assert_eq!(c.removed, vec![moved.clone()]);
    assert!(page_change(old, fresh, &dest, &dest, &[])
        .moved_edited
        .is_empty());
    let marked: HashSet<String> = [format!("{moved} [^k]")].into();
    let c = page_change(old, fresh, &marked, &none(), &[]);
    assert!(c.is_clear() && c.moved == 1, "{c:?}");
}

/// 451 T196: a split's target split again is followed, each page once, a cycle ending.
#[test]
fn a_split_s_target_split_again_is_followed_each_page_once() {
    let page = |to: &str| format!("<p>Now at <a class=\"moved\" href=\"{to}\">it</a>.</p>");
    let read = |f: &str| match f {
        "0001-a.html" => page("0002-b.html"),
        "0002-b.html" => page("0003-c.html"),
        _ => page("0001-a.html"),
    };
    let name = |t: &str| t.rsplit('/').next().unwrap_or(t).to_owned();
    assert_eq!(
        follow(&["0001-a.html".to_owned()], read, name),
        ["0001-a.html", "0002-b.html", "0003-c.html"]
    );
}

/// 0108.drawing before the cascade test's T403 write (2026-11-23), its stall items abridged.
const STABLE_PAGE: &str = "<p>An official's compound on our maps keeps its horses in a small stable of its own, a few bays long, \
with quarters in it for the grooms and an earth-floored passage before the stalls.</p>\n<ul>\n<li><strong>The stalls are drawn about one \
ken (~6 ft) wide, on board floors.</strong><br>A warrior's stall was one bay wide, on a raised timber floor.</li>\n";
/// The block T403 added, a pure addition (the cascade test's stables Depiction miss).
const ONE_DOOR: &str = "<li><strong>Our plans draw the passage with one door, at one gable end, and that is our own guess.</strong><br>A \
dictionary of Japanese architecture gives the classic warrior stable of the sixteenth and seventeenth centuries, three, five or seven \
bays long, large sliding doors at each gable end of its passage, and a Japanese encyclopedia calls the most formal stable of its time \
gable-entered. No page we read says whether a small provincial stable kept a door at both ends, so the two doors are attested only for \
the classic stable, and the one door is a GUESS.</li>\n";

fn added_to(page: &str, block: &str) -> (Change, Vec<String>) {
    let (old, fresh) = (format!("{page}</ul>"), format!("{page}{block}</ul>"));
    let c = change(&old, &fresh);
    let now = l7r_shared::checks::pages::read_page(&fresh)
        .blocks
        .into_iter()
        .map(|b| b.words)
        .collect();
    (c, now)
}

/// 451 T209 (the cascade test, 2026-11-24): a block new outright that bears on what a pop-up states is sent on - stables' Depiction ("the
/// door at its end") and the new one-gable-door GUESS - while one that shares no subject with it is still cleared.
#[test]
fn a_pure_addition_that_bears_on_a_pop_up_s_statement_is_sent() {
    let (c, now) = added_to(STABLE_PAGE, ONE_DOOR);
    assert_eq!((c.pairs.len(), c.removed.len(), c.added.len()), (0, 0, 1));
    let stables = "The classic warrior stables of the 16th and 17th centuries were three, five or seven bays long, the most formal of \
them three bays and entered at the gable end.\nThe plan draws the stable as a warrior's small stable, a few bays long: a row of stalls \
one ken (about 6 ft) wide at the back, the earth-floored passage before them running its length with the door at its end.";
    let why =
        super::fires(&c, &now, &none(), stables, &[]).expect("the one-gable-door addition sent");
    assert_eq!(
        (
            why.contains("new on the page"),
            why.contains("\"classic warrior stable\"")
        ),
        (true, true)
    );
    let drum = "Every plan's gate keeps a grievance drum under its roof, as the Chinese county offices at Pingyao and Neixiang did.";
    assert_eq!(super::fires(&c, &now, &none(), drum, &[]), None);
}

/// The 0097 finding T394 added (abridged), a pure addition.
const ROWHOUSE_FABRIC: &str = "<li><strong>What was a staff rowhouse built of?</strong><br>A country jin'ya's staff rows could be \
thatched. The Shibata row of 1842 has a hipped thatched roof. Of the four rows' pages, only Obata's gives its walls, earth walls in \
their present state.</li>\n";
/// A block 0097 added in cce80ca436 (abridged): it answers what retainers' quarters says no source says (needed.md's arm (c)).
const WHO_LIVED: &str = "<li><strong>Who lived inside a rural office?</strong><br>The sources name the junior officials' quarters \
and a storehouse keepers' rowhouse, but not who else lived inside.</li>\n";

/// 451 T212 (the cascade test, 2026-11-24): a pop-up's single-case phrase sends nothing on a new finding that shares no subject with it
/// (main-gate's "Every plan's gate", servants' quarters' "the one case recorded"), while a new block that answers what a pop-up says is
/// not recorded is still sent, whatever words the pop-up uses for its absence.
#[test]
fn a_single_case_phrase_alone_sends_nothing_and_a_broken_absence_still_sends() {
    let (c, now) = added_to(STABLE_PAGE, ROWHOUSE_FABRIC);
    let found = ["What was a staff rowhouse built of?".to_owned()];
    let drum = "Every plan's gate keeps a grievance drum under its roof.";
    assert_eq!(super::fires(&c, &now, &none(), drum, &found), None);
    let miwa = "That a small household's few servants slept under the main roof: the one case recorded, the Miwa house, kept its \
chugen in a hut by the kitchen.";
    assert_eq!(super::fires(&c, &now, &none(), miwa, &found), None);
    let (c, now) = added_to(STABLE_PAGE, WHO_LIVED);
    let retainers = "An intendant governed with about ten retainers of the shogunate and a few local hires, but no source says who \
else lived inside.";
    let why = super::fires(&c, &now, &none(), retainers, &[]).expect("the answered absence sent");
    assert!(why.contains("\"else lived inside\""), "{why}");
}
