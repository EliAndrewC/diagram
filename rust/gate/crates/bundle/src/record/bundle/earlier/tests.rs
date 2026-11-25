//! The earlier rounds a bundle carries: the rounds kept, the rulings, the replies beside the MANIFEST.

use serde_json::json;

use super::*;

// Each test reads its own environment, never the session's exports (feature 451 T38): this `section` shadows the crate's, which
// the first test also asks, on a tree with no check state.
fn section(root: &Path, out: &Path, manifest: &str) -> Result<String, Fail> {
    section_in(&Rooted::with(root, &[]), out, manifest)
}
use crate::record::bundle::tests::{scratch, state};
use crate::record::testkit::{commit, put};

#[test]
fn the_rounds_rulings_and_replies_of_a_unit() {
    let root = scratch("bundle-earlier");
    let out = root.join("out");
    let manifest = "owed-checks: quote-check, record-format\nunit: quote-check:0094#k fp\nunit: record-format:0094 fp\n";
    assert_eq!(section(&root, &out, manifest).unwrap(), "");
    assert_eq!(super::section(&root, &out, manifest).unwrap(), "");
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    let (one, two) = (root.join("one.md"), root.join("two.md"));
    put(&root, "one.md", "Verdict: findings\n1. the first finding of the round, long enough\nEDIT research/questions/0094-trade.html\n<<<\nold words here\n===\nnew words here\n>>>\n");
    put(&root, "two.md", "clean - 0 findings\n- a pass kept\n");
    put(
        &root,
        "specs/500-f/arbiter.jsonl",
        &format!(
            "{}\n{}\n",
            json!({"trigger": "round:quote-check|q:0094@3", "ruling": "continue", "why": "more", "what": "the notes"}),
            json!({"trigger": "round:quote-check|q:0094@2", "ruling": "accept"})
        ),
    );
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy(), "notes": ["k"]},
            "b": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.5, "state": "returned", "reply": two.to_string_lossy()},
            "c": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.6, "state": "returned", "notes": ["other"]},
            "d": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.7, "state": "running"},
            "e": {"check": "record-format", "subjects": ["q:0094"], "t": 9_999_999_999.8, "state": "returned", "reply": two.to_string_lossy()},
            "f": {"check": "quote-check", "subjects": ["q:0094"], "t": 1.0, "state": "returned", "reply": two.to_string_lossy()},
            "g": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.9, "state": "returned", "aid": "none-such"}
        }}),
    );
    let text = section(&root, &out, manifest).unwrap();
    assert!(text.starts_with("\n## Earlier rounds (feature 393)\n\n"));
    assert!(
        text.contains("**Round 1** - verdict: none read")
            && text.contains("- NEW: the first finding")
            && text.contains("- NOT APPLIED: research/questions/0094-trade.html:")
    );
    assert!(text.contains("**Round 3** - no reply kept") && text.contains("- the round arbiter on `round:quote-check|q:0094@2`: **accept** - (no reason recorded)\n- the round arbiter on `round:quote-check|q:0094@3`: **continue** - more | what the next round looks at: the notes"));
    assert!(out.join("earlier/quote-check-q-0094-round-1.md").is_file());
    assert_eq!(
        section(&root, &out, "owed-checks: bogus\nunit: x:0094 f\n").unwrap(),
        ""
    );
    assert_eq!(
        section(
            &root,
            &out,
            "owed-checks: quote-check\nunit: quote-check:0095 fp\n"
        )
        .unwrap(),
        ""
    );
    std::fs::write(root.join("blocked"), "a file").unwrap();
    assert!(section(&root, &root.join("blocked"), manifest).is_err());
    put(&root, ".specify/feature.json", "{}");
    assert!(feature_start(&Rooted::with(root.to_path_buf(), &[])) == 0.0);
}

#[test]
fn a_ruling_with_no_word_and_a_unit_with_no_round() {
    let root = scratch("bundle-earlier-bare");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    put(
        &root,
        "specs/500-f/arbiter.jsonl",
        &format!("{}\n", json!({"trigger": "round:quote-check|q:0094@3"})),
    );
    state(&root, &json!({"dispatches": {}}));
    let text = section(
        &root,
        &root.join("out"),
        "owed-checks: quote-check\nunit: quote-check:0094#k fp\n",
    )
    .unwrap();
    assert!(text.contains("**?** - (no reason recorded)"));
}

#[test]
fn a_later_round_whose_last_bundle_was_not_kept_gets_no_change_section_and_reads_unscoped() {
    let root = scratch("bundle-earlier-change");
    let out = root.join("out");
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    put(
        &root,
        "research/questions/0094-trade.html",
        "<p>new words here</p>\n",
    );
    let one = root.join("one.md");
    put(&root, "one.md", "quote-check: 0094 - 1\nEDIT research/questions/0094-trade.html\n<<<\nold words here\n===\nnew words here\n>>>\n");
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    let text = section(
        &root,
        &out,
        "owed-checks: quote-check\nunit: quote-check:0094#k fp\n",
    )
    .unwrap();
    assert!(text.contains("**Round 1**") && !text.contains("The change since round"));
}

#[test]
fn a_later_round_is_handed_every_change_since_what_the_last_round_was_bundled_a_hand_edit_too() {
    let root = scratch("bundle-earlier-seen");
    let out = root.join("out");
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    let page = "research/questions/0094-trade.html";
    put(
        &root,
        page,
        "<p>One line.</p>\n<p>A line a hand will change.</p>\n<p>The last.</p>\n",
    );
    let manifest = "owed-checks: quote-check\nunit: quote-check:0094#k fp\n";
    // round 1's bundle: no earlier round, and what it was bundled kept (a regeneration before its dispatch keeps the later text)
    put(
        &root,
        page,
        "<p>One line.</p>\n<p>A line a hand will change.</p>\n<p>The last.</p>\n",
    );
    state(&root, &json!({"dispatches": {}}));
    assert_eq!(section(&root, &out, manifest).unwrap(), "");
    assert_eq!(section(&root, &out, manifest).unwrap(), "");
    let one = root.join("one.md");
    put(&root, "one.md", "quote-check: 0094 - 0 findings\n");
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    put(
        &root,
        page,
        "<p>One line.</p>\n<p>A line the hand changed.</p>\n<p>The last.</p>\n",
    );
    let text = section(&root, &out, manifest).unwrap();
    assert!(text.contains("### The change since round 1 (451 T189)"));
    assert!(text.contains("judge ONLY whether this change made something wrong"));
    assert!(text.contains(&format!(
        "- `{page}`, before:\n```\n<p>A line a hand will change.</p>\n```\nafter:\n```\n<p>A line the hand changed.</p>\n```"
    )));
    assert!(!text.contains("before:\n```\n<p>One line."));
    // what rounds 1 and 2 were bundled is kept
    let kept =
        std::fs::read_to_string(root.join(".git/record-checks/seen/quote-check-q-0094.json"))
            .unwrap();
    assert!(kept.contains("\"1\"") && kept.contains("\"2\""));
    // round 2 went out on that bundle and nothing changed since: no change section
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()},
            "b": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.5, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    let calm = section(&root, &out, manifest).unwrap();
    assert!(calm.contains("**Round 2**") && !calm.contains("The change since round"));
}

/// 451 T196, T184's split of 0059 to 0333 in small: a later round pairs a change on a page the subject's pointer now reaches, the target
/// diffed against the page it left, so a line moved verbatim is no change and one restated as it moved is paired with its old self.
#[test]
fn a_later_round_pairs_a_change_on_a_split_s_target_page() {
    let root = scratch("bundle-earlier-split");
    let out = root.join("out");
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    let page = "research/questions/0059-intake.html";
    put(
        &root,
        page,
        "<p>The intake.</p>\n<p>Weirs were staked.</p>\n<p>An official handbook says so.</p>\n",
    );
    let manifest = "owed-checks: quote-check\nunit: quote-check:0059#k fp\n";
    state(&root, &json!({"dispatches": {}}));
    assert_eq!(section(&root, &out, manifest).unwrap(), "");
    let one = root.join("one.md");
    put(&root, "one.md", "quote-check: 0059 - 0 findings\n");
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0059"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    put(&root, page, "<p>The intake.</p>\n<p>Now at <a class=\"moved\" href=\"0333-weir.html\">the weir</a>.</p>\n");
    let target = "research/questions/0333-weir.html";
    put(
        &root,
        target,
        "<p>Weirs were staked.</p>\n<p>A Japanese encyclopedia says so.</p>\n",
    );
    let text = section(&root, &out, manifest).unwrap();
    let paired = format!("- `{target}`, before:\n```\n<p>An official handbook says so.</p>\n```\nafter:\n```\n<p>A Japanese encyclopedia says so.</p>\n```");
    let (has_pair, has_moved) = (
        text.contains(&paired),
        text.contains("after:\n```\n<p>Weirs were staked."),
    );
    assert!(has_pair && !has_moved, "{text}");
}

/// 451 T249, the guest-quarters round of 2026-11-24 in small: a later round whose last round's bundle kept no snapshot (bundled
/// before 451 T189) gets no change section, and its MANIFEST says so in one line under its title, the check told to judge the whole
/// unit; a first round, a unit with rulings only, and a later round whose last bundle was kept get no such line, and a rebuild
/// before the dispatch keeps it.
#[test]
fn a_later_round_with_no_kept_snapshot_says_at_its_head_that_it_judges_the_whole_unit() {
    let root = scratch("bundle-earlier-scope");
    let out = root.join("out");
    put(&root, "specs/500-f/spec.md", "spec");
    commit(&root, "the feature");
    put(
        &root,
        ".specify/feature.json",
        "{\"feature_directory\": \"specs/500-f\"}",
    );
    put(
        &root,
        "research/questions/0094-trade.html",
        "<p>Words.</p>\n",
    );
    let manifest = "# Check bundle - 0094\n\nWritten today.\nowed-checks: quote-check, record-format\nunit: quote-check:0094#k fp\nunit: record-format:0094 fp\n";
    let at = |m: &str| headed_in(&Rooted::with(&*root, &[]), &out, m).unwrap();
    // a first round: no earlier round, no line
    state(&root, &json!({"dispatches": {}}));
    assert!(!at(manifest).contains("451 T249"));
    std::fs::remove_dir_all(root.join(".git/record-checks/seen")).unwrap();
    // rulings only: no round, no line
    put(
        &root,
        "specs/500-f/arbiter.jsonl",
        &format!(
            "{}\n",
            json!({"trigger": "round:quote-check|q:0094@3", "ruling": "continue"})
        ),
    );
    assert!(!at(manifest).contains("451 T249"));
    std::fs::remove_dir_all(root.join(".git/record-checks/seen")).unwrap();
    // a later round of each check, neither last bundle kept: one line naming both, under the title, and no change section
    let one = root.join("one.md");
    put(&root, "one.md", "quote-check: 0094 - 0 findings\n");
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()},
            "b": {"check": "record-format", "subjects": ["q:0094"], "t": 9_999_999_999.1, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    let text = at(manifest);
    let line = "**Scope: the whole unit (451 T249).** No snapshot was kept of what the last round of quote-check on q:0094, record-format on q:0094 was bundled (a round bundled before 451 T189), so this bundle has no change section: judge the whole unit, every block, as in a first round - not only what an earlier round named.";
    let head = format!("# Check bundle - 0094\n\n{line}\n\nWritten today.\n");
    let headed = text.starts_with(&head);
    assert!(headed, "{text}");
    assert_eq!(text.matches("451 T249").count(), 1, "{text}");
    assert!(!text.contains("The change since round"), "{text}");
    // a rebuild before the dispatch keeps the line: what it keeps is the next round's bundle, not the last
    assert!(at(manifest).contains(line));
    // the next round, its last bundle kept: no line, whether or not anything changed
    state(
        &root,
        &json!({"dispatches": {
            "a": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.0, "state": "returned", "reply": one.to_string_lossy()},
            "b": {"check": "record-format", "subjects": ["q:0094"], "t": 9_999_999_999.1, "state": "returned", "reply": one.to_string_lossy()},
            "c": {"check": "quote-check", "subjects": ["q:0094"], "t": 9_999_999_999.2, "state": "returned", "reply": one.to_string_lossy()},
            "d": {"check": "record-format", "subjects": ["q:0094"], "t": 9_999_999_999.3, "state": "returned", "reply": one.to_string_lossy()}
        }}),
    );
    assert!(!at(manifest).contains("451 T249"));
    put(
        &root,
        "research/questions/0094-trade.html",
        "<p>Other words.</p>\n",
    );
    let changed = at(manifest);
    let scoped = !changed.contains("451 T249") && changed.contains("The change since round 2");
    assert!(scoped, "{changed}");
}
