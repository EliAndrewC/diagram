//! A size edit never changes a claim: the 2026-11-23 trims of 0009 and 0059 (cce80ca436), as excerpts of their real
//! blocks, red; the restore-and-split that repairs them, green.

use super::{is_size_edit, lost, removed_bytes, Kind};

/// 0009's block "Was any depth of paddy water recorded before modern times?" before and after the trim: "So every depth
/// above is modern extension guidance." went, and its `every` stands in no other sentence of the block.
const DEPTH_OLD: &str = r#"<li><strong>Was any depth of paddy water recorded before modern times?</strong><br>None was found. Neither Chinese manual gives one, and searches in Japanese and Chinese found none.<sup class="fn" data-note="the-paddy"></sup> So every depth above is modern extension guidance. That the plant's need for shallow, warm water was the same in older centuries is reasoning, not evidence, and is not asserted here.</li>"#;
const DEPTH_NEW: &str = r#"<li><strong>Was any depth of paddy water recorded before modern times?</strong><br>None was found. Neither Chinese manual gives one, and searches in Japanese and Chinese found none.<sup class="fn" data-note="the-paddy"></sup> That the plant's need for shallow, warm water was the same in older centuries is reasoning, not evidence, and is not asserted here.</li>"#;

/// 0059's block on the Sengoku-period intakes: its body lost "were mostly small, of timber frames packed with stone".
const SENGOKU_OLD: &str = r#"<li><strong>Until the late sixteenth century most intake works were small cribs of timber packed with stone.</strong><br>A Japanese engineering lecture on head works says intake works up to the end of the Sengoku period, in the late sixteenth century, were mostly small, of timber frames packed with stone.<sup class="fn" data-note="shimane-toshuko-lecture"></sup></li>"#;
const SENGOKU_NEW: &str = r#"<li><strong>Until the late sixteenth century most intake works were small cribs of timber packed with stone.</strong><br>So says a Japanese engineering lecture on head works, of the works up to the end of the Sengoku period.<sup class="fn" data-note="shimane-toshuko-lecture"></sup></li>"#;

/// 0059's 1902 treatise block: the quoted passage changed under the trim.
const TREATISE_OLD: &str = r#"<li><strong>A Japanese treatise of the early twentieth century put the head works where the river leaves the mountains.</strong><br>A land-improvement treatise of 1902 advised: "It is best to place the head works generally where the river issues from the mountains."<sup class="fn" data-note="maff-toshuko-history-6"></sup></li>"#;
const TREATISE_NEW: &str = r#"<li><strong>A Japanese treatise of 1902 put the head works where the river leaves the mountains.</strong><br>The land-improvement treatise advised: "It is advisable to place the head works generally where the river issues from the mountains."<sup class="fn" data-note="maff-toshuko-history-6"></sup></li>"#;

/// 0009's lead before and after: "already" went from the only sentence that carried it.
const LEAD_OLD: &str = r#"<p>The shape of that year is old - a Chinese farm manual of 544 already lets the water out to firm the roots and again before the rice ripens<sup class="fn" data-note="qimin-yaoshu-juan2"></sup>. Every depth, though, is modern.</p>"#;
const LEAD_NEW: &str = r#"<p>The shape of that year is old - a Chinese farm manual of 544<sup class="fn" data-note="qimin-yaoshu-enwiki"></sup> drains to firm the roots and again before ripening<sup class="fn" data-note="qimin-yaoshu-juan2"></sup>. Every depth, though, is modern.</p>"#;

fn page(blocks: &[&str]) -> String {
    let mut out = String::from("<h2 id=\"q\">Q</h2>\n");
    for b in blocks {
        out.push_str(b);
        out.push('\n');
    }
    out
}

fn kinds(old: &str, new: &str, linked: &[String]) -> Vec<(Kind, String)> {
    lost(old, new, linked)
        .into_iter()
        .map(|l| (l.kind, l.token))
        .collect()
}

#[test]
fn the_0009_trim_dropped_a_qualifier_from_its_block_and_is_refused() {
    let old = page(&[LEAD_OLD, DEPTH_OLD]);
    let new = page(&[LEAD_NEW, DEPTH_NEW]);
    let found = kinds(&old, &new, &[]);
    assert!(found.contains(&(Kind::Qualifier, "every".to_owned())));
    assert!(found.contains(&(Kind::Qualifier, "already".to_owned())));
}

#[test]
fn the_0059_trim_dropped_a_qualifier_and_changed_a_quoted_passage_and_is_refused() {
    let old = page(&[SENGOKU_OLD, TREATISE_OLD]);
    let new = page(&[SENGOKU_NEW, TREATISE_NEW]);
    let found = kinds(&old, &new, &[]);
    assert!(found.contains(&(Kind::Qualifier, "mostly".to_owned())));
    assert!(found
        .iter()
        .any(|(k, t)| *k == Kind::Quote && t.contains("It is best")));
}

#[test]
fn a_token_standing_elsewhere_on_the_page_is_not_lost() {
    // "1902" leaves the treatise's body but stands in its heading; a number is judged page-wide.
    let old = page(&[
        r"<li><strong>A treatise put the head works there.</strong><br>The treatise of 1902 advised it.</li>",
        "<p>Written in 1902.</p>",
    ]);
    let new = page(&[
        r"<li><strong>A treatise put the head works there.</strong><br>The treatise advised it.</li>",
        "<p>Written in 1902.</p>",
    ]);
    assert!(kinds(&old, &new, &[]).is_empty());
}

#[test]
fn a_split_keeps_its_tokens_on_the_page_the_source_now_points_to() {
    let old = page(&[LEAD_OLD, SENGOKU_OLD]);
    let new = page(&[
        LEAD_OLD,
        r#"<p>How the old weirs were built is told at <a href="0400-how-a-weir-was-built.html">its own page</a>.</p>"#,
    ]);
    assert!(!kinds(&old, &new, &[]).is_empty());
    let moved = page(&[SENGOKU_OLD]);
    assert!(kinds(&old, &new, &[moved]).is_empty());
}

#[test]
fn a_restored_page_loses_nothing_and_an_unchanged_block_is_never_read() {
    let old = page(&[LEAD_OLD, DEPTH_OLD, SENGOKU_OLD]);
    assert!(kinds(&old, &old, &[]).is_empty());
    let grown = page(&[LEAD_OLD, DEPTH_OLD, SENGOKU_OLD, TREATISE_NEW]);
    assert!(kinds(&old, &grown, &[]).is_empty());
}

#[test]
fn a_size_edit_is_a_page_over_its_limit_or_one_the_removed_words_would_put_back_over_it() {
    assert!(is_size_edit(20_044, 19_853, 191, 20_000));
    assert!(is_size_edit(19_500, 19_900, 300, 20_000));
    assert!(!is_size_edit(12_000, 11_000, 1_000, 20_000));
    assert!(!is_size_edit(20_044, 21_000, 0, 24_000));
    let old = page(&[DEPTH_OLD]);
    let new = page(&[DEPTH_NEW]);
    let gone = removed_bytes(&old, &new);
    assert!(gone >= "So every depth above is modern extension guidance.".len() - 8 && gone < 80);
    assert_eq!(removed_bytes(&old, &old), 0);
}

#[test]
fn every_kind_of_claim_bearing_token_is_named_when_it_goes() {
    let old = page(&[
        r#"<li><strong>The weir.</strong><br>Built in 1183 at Tatai on the Takahashi, a GUESS, of <em>shigarami</em> "woven of split bamboo and brush".</li>"#,
    ]);
    let new = page(&["<li><strong>The weir.</strong><br>Built at a river.</li>"]);
    let found = kinds(&old, &new, &[]);
    for (kind, token) in [
        (Kind::Number, "1183"),
        (Kind::Label, "GUESS"),
        (Kind::Name, "shigarami"),
        (Kind::Name, "Tatai"),
        (Kind::Quote, "\"woven of split bamboo and brush\""),
    ] {
        assert!(found.contains(&(kind, token.to_owned())));
    }
    let words: Vec<&str> = [
        Kind::Number,
        Kind::Label,
        Kind::Quote,
        Kind::Name,
        Kind::Qualifier,
    ]
    .iter()
    .map(|k| k.word())
    .collect();
    assert_eq!(
        words,
        ["number", "label", "quoted passage", "name", "qualifier"]
    );
}
