//! The triage bundle over each kind of change: a page's new, changed and removed blocks (from the kept snapshot, from the history, or
//! lost), a section's, a unit's diff; its reply recorded; a reply's outside rows filed.

use std::collections::{HashMap, HashSet};

use serde_json::{json, Map, Value};

use super::{checked_at, keep_texts, kept_text, record_triage, removed_words, triage_bundle, vet};
use crate::claims::index::{current, load_map};
use crate::claims::tests::{commit_as_origin, fixture, record_all, write_recorded};
use crate::record::testkit::{commit, git, put};

/// The fixture recorded, then a page, a section and three units changed, and the index and snapshots as a
/// triage reads them: (root, index, store).
fn changed_everything() -> (
    l7r_shared::tempdir::TempDir,
    Map<String, Value>,
    Map<String, Value>,
) {
    // the recorded index committed as `origin/main` with the loose ref copied: git processes saved (feature 449 T167, FR-008's tenth
    // of a second); the claimed dictionary, a `.py` unit, left with the engine's Python (feature 449 T158)
    let root = fixture("claims-triage-bundle");
    // the recording written as `record_all` writes it, pinned by `the_recorded_state_is_what_record_all_writes`: a bundle and a record
    // most of the test's time against FR-008's tenth of a second (feature 449 T167)
    write_recorded(&root, "{}", "{}");
    commit_as_origin(&root, "recorded");
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A new block.</p>\n");
    let buildings = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        buildings
            .replace("Walls stand.\n", "Walls stand, rebuilt.\n")
            .replace("- a list item\n  continued\n", ""),
    )
    .unwrap();
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace(
            "let y = 3.25; // a number",
            "let y = \"reach - research/questions/0001-gap.html: within GAP\";",
        )
        .replace("a[1] + 42", "a[1] + 43")
        .replace("    1\n}", "    2\n}"),
    )
    .unwrap();
    let mut ix = load_map(&root.join("dev/claims-index.json")).unwrap();
    for (k, v) in &mut ix {
        if k.starts_with("rust/phases/src/lib.rs::GAP")
            || k.starts_with("docs/buildings.md::Walls#wall height")
        {
            v.as_object_mut().unwrap().remove("rests");
        }
    }
    ix.shift_remove("rust/phases/src/lib.rs::helper#plumbing");
    let mut store = load_map(&root.join("dev/claims-pages.json")).unwrap();
    let gap_fp = ix["rust/phases/src/lib.rs::GAP#gap"]["pages"]["0001-gap.html"]
        .as_str()
        .unwrap()
        .to_owned();
    store[&gap_fp]
        .as_array_mut()
        .unwrap()
        .push(json!("lost-digest"));
    (root, ix, store)
}

#[test]
fn each_kind_of_change_is_shown_and_its_reply_recorded() {
    let (root, ix, store) = changed_everything();
    let cur = current(&root, &root.join("research/questions")).unwrap();
    let keys: Vec<String> = [
        "rust/phases/src/lib.rs::GAP#gap",
        "rust/phases/src/lib.rs::reach#reach",
        "rust/phases/src/lib.rs::Thing.m#method guess",
        "rust/phases/src/lib.rs::helper#plumbing",
        "docs/buildings.md::Walls#walls",
    ]
    .map(str::to_owned)
    .to_vec();
    let out = root.join("t");
    std::fs::create_dir_all(&out).unwrap();
    let manifest = triage_bundle(
        &cur,
        &ix,
        &store,
        &keys,
        &root.join("research/questions"),
        &out,
    )
    .unwrap();
    let text = std::fs::read_to_string(manifest).unwrap();
    // the section's edit is cleared by the tool: no claim in it repeats a word it changed (feature 451 T191)
    assert!(!text.contains("## docs/buildings.md::Walls"), "{text}");
    for want in [
        "## rust/phases/src/lib.rs::Thing.m (a unit of code; its diff against origin/main)\n\n```diff\n@@",
        "## research/questions/0001-gap.html\n\n(against the version these claims were last checked at,",
        "New or changed blocks:\n\n> A new block.\n",
        "Removed blocks (no longer on the page):\n\n> A second block.\n",
        "- KEY `rust/phases/src/lib.rs::helper#plumbing`",
        "last verdict None: ",
    ] {
        assert!(text.contains(want), "{want}\n----\n{text}");
    }
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(out.join("triage.json")).unwrap()).unwrap();
    let forced: Vec<&str> = data["forced"]
        .as_array()
        .unwrap()
        .iter()
        .map(|v| v.as_str().unwrap())
        .collect();
    assert_eq!(
        forced,
        vec![
            "rust/phases/src/lib.rs::GAP#gap",
            "rust/phases/src/lib.rs::helper#plumbing",
            "rust/phases/src/lib.rs::reach#reach"
        ]
    );
    let units = data["units"].as_object().unwrap().clone();
    let (new, msgs) = record_triage(
        &ix,
        &units,
        "TOUCHES rust/phases/src/lib.rs::Thing.m#method guess - it does",
        "d",
        &[
            "rust/phases/src/lib.rs::GAP#gap".to_owned(),
            "elsewhere".to_owned(),
        ],
    );
    assert_eq!(msgs.len(), 2);
    assert!(data["cleared"]
        .as_object()
        .unwrap()
        .contains_key("docs/buildings.md::Walls#walls"));
    assert_ne!(
        new["docs/buildings.md::Walls#walls"].get("triaged"),
        Some(&json!("d"))
    );
    assert_eq!(new["rust/phases/src/lib.rs::GAP#gap"]["triage"], "touched");
}

/// Feature 451 T185: a split of a cited page - a block moved verbatim to the page its pointer names - shows neither the moved block as
/// removed nor the pointer as new.
#[test]
fn a_split_of_a_cited_page_shows_no_removal_and_no_pointer() {
    let (root, ix, store) = changed_everything();
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>Now at <a class=\"moved\" href=\"0002-moved.html\">Moved</a>.</p>\n");
    put(
        &root,
        "research/questions/0002-moved.html",
        "<h2 id=\"moved\">Moved</h2>\n<p>A second block.</p>\n",
    );
    let cur = current(&root, &root.join("research/questions")).unwrap();
    let keys = vec!["rust/phases/src/lib.rs::GAP#gap".to_owned()];
    let out = root.join("t");
    std::fs::create_dir_all(&out).unwrap();
    let manifest = triage_bundle(
        &cur,
        &ix,
        &store,
        &keys,
        &root.join("research/questions"),
        &out,
    )
    .unwrap();
    let text = std::fs::read_to_string(manifest).unwrap();
    assert!(!text.contains("A second block.") && !text.contains("Now at Moved."));
}

#[test]
fn a_page_s_snapshot_is_kept_and_its_removed_words_found() {
    let root = fixture("claims-triage-words");
    let q = root.join("research/questions");
    let fp = crate::claims::index::findings_of(
        &std::fs::read_to_string(q.join("0001-gap.html")).unwrap(),
    );
    let units = json!({"k": {"pages": {"0001-gap.html": fp, "0009-none.html": "x"}}, "j": {}})
        .as_object()
        .unwrap()
        .clone();
    assert_eq!(keep_texts(&q, &units).unwrap(), 1);
    assert_eq!(keep_texts(&q, &units).unwrap(), 0);
    assert_eq!(keep_texts(&q, &Map::new()).unwrap(), 0);
    let stale = json!({"k": {"pages": {"0001-gap.html": "not-the-page"}}})
        .as_object()
        .unwrap()
        .clone();
    assert_eq!(keep_texts(&q, &stale).unwrap(), 0);
    assert!(kept_text(&q, &fp).unwrap().contains("A second block."));
    assert_eq!(kept_text(&q, "nothing").unwrap(), "");
    let plain = crate::checks::scratch("claims-triage-plain");
    assert_eq!(keep_texts(&plain, &units).unwrap(), 0);
    assert_eq!(kept_text(&plain, &fp).unwrap(), "");
    let second = crate::record::units::digest(&["A second block."]);
    put(
        &root,
        "research/questions/0001-gap.html",
        "<h2 id=\"gap\">The gap</h2>\n<p>Only this.</p>\n",
    );
    let found = removed_words(&q, "0001-gap.html", &HashSet::from([second.clone()]), "").unwrap();
    assert_eq!(found[&second], "A second block.");
    let found = removed_words(
        &q,
        "0001-gap.html",
        &HashSet::from([second.clone(), "lost".to_owned()]),
        &fp,
    )
    .unwrap();
    assert_eq!(found.len(), 1);
    let (mut seen, mut log) = (HashMap::new(), None);
    assert_eq!(
        checked_at(&root, "k", "c", &mut seen, &mut log),
        "origin/main"
    );
    put(&root, "dev/claims-index.json", "{\"k\": {\"code\": \"c\"}}");
    commit(&root, "index");
    put(&root, "dev/claims-index.json", "{");
    commit(&root, "broken index");
    let (mut seen, mut log) = (HashMap::new(), None);
    let at = checked_at(&root, "k", "c", &mut seen, &mut log);
    assert_eq!(at, git(&root, &["rev-parse", "HEAD~1"]));
}

#[test]
fn a_reply_s_lines_are_vetted_and_its_outside_rows_filed() {
    let root = fixture("claims-triage-vet");
    let units = json!({"a::b#c": {}}).as_object().unwrap().clone();
    let (mut said, mut warned) = (String::new(), String::new());
    let reply = "VERDICT a::b#c IN-STEP - fine\nVERDICT a::b#c IN-STEP - research/questions/0001-gap.html fine\n\n## OUTSIDE THE CHANGE\n- `x.py` | the block | a finding | effect: sheet - a wrong door\n- `y.py` | a block | a difference; effect: none\n";
    let (kept, bad) = vet(reply, &units, &root, &mut said, &mut warned).unwrap();
    assert!(bad.is_empty() && kept.contains("OUTSIDE"));
    assert_eq!(
        said,
        "claims-checked: filed, not fixed - x.py | the block | a finding | effect: sheet - a wrong door\nclaims-checked: listed, not filed - y.py | a block | a difference; effect: none\nclaims-checked: a note outside the change is filed only where it ends `| effect: <map|sheet|page|tool> - <the wrong outcome its reader or user meets>` (451 T219); the rest are dropped\n"
    );
    assert!(warned.is_empty());
}

/// A DRIFTED line is recorded only with its fix named, the claim or the code (constitution XIV v2.36.0, feature 449 T196): a drift
/// with no visible effect is fixed by restating the claim, so the check must say which side moves.
#[test]
fn a_drifted_line_without_its_fix_is_refused_with_the_form() {
    let root = fixture("claims-triage-fix");
    let units = json!({"a::b#c": {}, "a::d#e": {}, "a::f#g": {}})
        .as_object()
        .unwrap()
        .clone();
    let (mut said, mut warned) = (String::new(), String::new());
    let reply = "VERDICT a::b#c DRIFTED - ends 0.4 px short [§2]\nVERDICT a::d#e DRIFTED - ends 0.4 px short; fix: claim; effect: none [§2]\nVERDICT a::f#g DRIFTED - [outside the change] the wrong form drawn; fix: code; effect: a thatched roof drawn tiled [§1]\n";
    let (kept, bad) = vet(reply, &units, &root, &mut said, &mut warned).unwrap();
    assert_eq!(bad.len(), 1, "{bad:?}");
    assert!(bad[0].starts_with("a DRIFTED note names no fix (`fix: claim` or `fix: code`"));
    assert!(bad[0].ends_with("VERDICT a::b#c DRIFTED - ends 0.4 px short [§2]"));
    assert!(!kept.contains("a::b#c") && kept.contains("a::d#e") && kept.contains("a::f#g"));
    assert!(warned.contains("REFUSED line - a DRIFTED note names no fix"));
    assert!(warned.contains("a DRIFTED note's `fix: claim` or `fix: code`"));
}

/// The fixture recorded and committed as origin/main, the index's GAP row resting on no block: (root, index, store).
fn recorded() -> (
    l7r_shared::tempdir::TempDir,
    Map<String, Value>,
    Map<String, Value>,
) {
    // no Python unit, so no Python half to start, and `origin/main` written as the fixture writes it (feature 449 T167: these tests sat at
    // FR-008's tenth of a second)
    let root = fixture("claims-triage-only");
    record_all(&root);
    commit_as_origin(&root, "recorded");
    let mut ix = load_map(&root.join("dev/claims-index.json")).unwrap();
    ix["rust/phases/src/lib.rs::GAP#gap"]
        .as_object_mut()
        .unwrap()
        .remove("rests");
    let store = load_map(&root.join("dev/claims-pages.json")).unwrap();
    (root, ix, store)
}

fn manifest_of(
    root: &std::path::Path,
    ix: &Map<String, Value>,
    store: &Map<String, Value>,
    keys: &[&str],
) -> String {
    let cur = current(root, &root.join("research/questions")).unwrap();
    let keys: Vec<String> = keys.iter().map(|k| (*k).to_owned()).collect();
    let out = root.join("t");
    let m = triage_bundle(
        &cur,
        ix,
        store,
        &keys,
        &root.join("research/questions"),
        &out,
    )
    .unwrap();
    std::fs::read_to_string(m).unwrap()
}

/// Feature 451 T191: an addition alone owes no claim its triage - none of these states a single case a new block could falsify - so
/// both are cleared by the tool and the MANIFEST names neither.
#[test]
fn a_change_that_only_adds_is_cleared_by_the_tool() {
    let (root, ix, store) = recorded();
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n<p>Added.</p>\n");
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", "Walls stand.\n\nAdded too.\n"),
    )
    .unwrap();
    let keys = [
        "rust/phases/src/lib.rs::GAP#gap",
        "docs/buildings.md::Walls#walls",
    ];
    let text = manifest_of(&root, &ix, &store, &keys);
    assert!(!text.contains("Added"), "{text}");
    assert_eq!(cleared_of(&root), keys);
}

/// The keys a triage bundle at `root/t` cleared by the tool.
fn cleared_of(root: &std::path::Path) -> Vec<String> {
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    let mut keys: Vec<String> = data["cleared"]
        .as_object()
        .unwrap()
        .keys()
        .cloned()
        .collect();
    keys.sort();
    keys.reverse();
    keys
}

#[test]
fn a_change_that_only_removes_shows_none_new_and_a_lost_block_owes_in_full() {
    let (root, mut ix, mut store) = recorded();
    put(
        &root,
        "research/questions/0001-gap.html",
        "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n",
    );
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", ""),
    )
    .unwrap();
    let lib = std::fs::read_to_string(root.join("rust/phases/src/lib.rs")).unwrap();
    std::fs::write(
        root.join("rust/phases/src/lib.rs"),
        lib.replace("x + GAP + y", "x + GAP + y + 1.0"),
    )
    .unwrap();
    let section = ix["docs/buildings.md::Walls#walls"]["section"]
        .as_str()
        .unwrap()
        .to_owned();
    store[&section].as_array_mut().unwrap().push(json!("lost"));
    ix["rust/phases/src/lib.rs::reach#reach"]["verdict"] = json!(3);
    ix["rust/phases/src/lib.rs::reach#reach"]["code"] = json!(5);
    let text = manifest_of(
        &root,
        &ix,
        &store,
        &[
            "rust/phases/src/lib.rs::GAP#gap",
            "docs/buildings.md::Walls#walls",
            "rust/phases/src/lib.rs::reach#reach",
        ],
    );
    assert!(text.contains("New or changed blocks:\n\n(none)\n\nRemoved blocks (no longer in the section):\n\n> Walls stand.\n"));
    // the page's removal is no sentence the gap claim repeats: cleared by the tool (feature 451 T191)
    assert!(!text.contains("A second block."));
    assert_eq!(cleared_of(&root), ["rust/phases/src/lib.rs::GAP#gap"]);
    assert!(text.contains("last verdict 3: "));
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    assert!(data["forced"]
        .as_array()
        .unwrap()
        .contains(&json!("docs/buildings.md::Walls#walls")));
    // forced, a block of its page the history no longer shows: the page's removal shown to the agent with it
    let fp = ix["rust/phases/src/lib.rs::GAP#gap"]["pages"]["0001-gap.html"]
        .as_str()
        .unwrap()
        .to_owned();
    store[&fp].as_array_mut().unwrap().push(json!("lost"));
    let text = manifest_of(&root, &ix, &store, &["rust/phases/src/lib.rs::GAP#gap"]);
    assert!(text.contains("New or changed blocks:\n\n(none)\n\nRemoved blocks (no longer on the page):\n\n> A second block.\n"));
}

/// Feature 451 T191: with no kept text of the page as it was checked, an added block counts as a new finding - here none the claim's
/// single case meets, so the addition is cleared.
#[test]
fn with_no_kept_text_an_added_block_counts_as_a_finding() {
    let (root, ix, store) = recorded();
    std::fs::remove_file(root.join(".git").join(super::BLOBS)).unwrap();
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is 12 ft.</p>\n<p>A second block.</p>\n<p>Every plan keeps 12 ft here.</p>\n");
    let text = manifest_of(&root, &ix, &store, &["rust/phases/src/lib.rs::GAP#gap"]);
    assert!(!text.contains("Every plan"));
    assert_eq!(cleared_of(&root), ["rust/phases/src/lib.rs::GAP#gap"]);
}

/// Feature 451 T191, red on 604541c046: a link, emphasis, code-tick or note-marker edit of a section or a cited page is cleared by the
/// tool (T186's clears, shared), no agent.
#[test]
fn a_markup_link_tick_or_marker_edit_is_cleared_by_the_tool() {
    let (root, ix, store) = recorded();
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is <a href=\"x.html\">12 ft</a>.<sup class=\"fn\" data-note=\"k\"></sup></p>\n<p>A <em>second</em> block.</p>\n");
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", "**Walls** [stand](x.md)`.`\n")
            .replace("- a list item\n", "- a _list_ item\n"),
    )
    .unwrap();
    let keys = [
        "rust/phases/src/lib.rs::GAP#gap",
        "docs/buildings.md::Walls#walls",
        "docs/buildings.md::Walls#wall height",
    ];
    let text = manifest_of(&root, &ix, &store, &keys);
    assert!(!text.contains("## "), "{text}");
    assert_eq!(cleared_of(&root), keys);
}

/// Feature 451 T191: a rewritten block goes to the agent for the claim that repeats a three-word run over its changed words, on either
/// side of the rewrite (`gap`'s "kept 12 ft", `wall height`'s "wall height 12 ft"), shown paired; the claims citing the same text that
/// do not are cleared by the tool.
#[test]
fn a_rewrite_goes_to_the_agent_only_for_the_claim_repeating_its_changed_words() {
    let (root, ix, store) = recorded();
    put(&root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is kept 12 ft wide.</p>\n<p>A second block.</p>\n");
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("  continued\n", "  continued to wall height 12 ft\n"),
    )
    .unwrap();
    let text = manifest_of(
        &root,
        &ix,
        &store,
        &[
            "rust/phases/src/lib.rs::GAP#gap",
            "rust/phases/src/lib.rs::reach#reach",
            "docs/buildings.md::Walls#walls",
            "docs/buildings.md::Walls#wall height",
        ],
    );
    for want in [
        "New or changed blocks:\n\n> The gap is kept 12 ft wide.\n\nRemoved blocks (no longer on the page):\n\n> The gap is 12 ft.\n",
        "New or changed blocks:\n\n> - a list item continued to wall height 12 ft\n\nRemoved blocks (no longer in the section):\n\n> - a list item continued\n",
        "- KEY `rust/phases/src/lib.rs::GAP#gap`",
        "- KEY `docs/buildings.md::Walls#wall height`",
    ] {
        assert!(text.contains(want), "{want}\n----\n{text}");
    }
    assert_eq!(
        cleared_of(&root),
        [
            "rust/phases/src/lib.rs::reach#reach",
            "docs/buildings.md::Walls#walls"
        ]
    );
}

/// Feature 451 T191: a cleared claim recorded as a triage clears it, at the text as it stands, saying the tool cleared it.
#[test]
fn a_claim_the_tool_cleared_is_recorded_cleared() {
    let ix: Map<String, Value> =
        serde_json::from_value(json!({"k": {"triage": "touched", "verdict": "IN-STEP"}})).unwrap();
    let cleared: Map<String, Value> = serde_json::from_value(
        json!({"k": {"research": "r", "pages": {"p": "f"}, "section": "s"}}),
    )
    .unwrap();
    let out = super::record_cleared(&ix, &cleared, "d");
    assert_eq!(
        out["k"],
        json!({"verdict": "IN-STEP", "research": "r", "pages": {"p": "f"}, "triaged": "d", "section": "s", "cleared": super::TOOL_CLEARED})
    );
}

/// 451 T196, the fixtures T184's split of 0059 to 0333 is shaped like: `0001-gap.html`'s rested-on block moved to `0003-moved.html`,
/// a pointer left in its place, with `moved` as the block on the target (verbatim, or edited).
fn split(root: &std::path::Path, moved: &str) {
    put(root, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>A second block.</p>\n<p>Now at <a class=\"moved\" href=\"0003-moved.html\">Moved</a>.</p>\n");
    put(
        root,
        "research/questions/0003-moved.html",
        &format!("<h2 id=\"moved\">Moved</h2>\n<p>{moved}</p>\n"),
    );
}

fn owed_now(root: &std::path::Path) -> Vec<(String, String)> {
    let q = root.join("research/questions");
    let cur = current(root, &q).unwrap();
    let ix = load_map(&root.join("dev/claims-index.json")).unwrap();
    let store = load_map(&root.join("dev/claims-pages.json")).unwrap();
    crate::claims::index::owed(&cur, &ix, Some(&q), Some(&store)).unwrap()
}

/// 451 T196: a claim reads the pages its cited page's pointers reach. A pure split owes it a triage, not a full round (its rest stands
/// verbatim on the target; the target is new to it); its bundle reads the target; once checked there, an edit of the target re-owes it.
#[test]
fn a_claim_follows_its_page_s_pointers() {
    let root = fixture("claims-follow");
    record_all(&root);
    let gap = "rust/phases/src/lib.rs::GAP#gap";
    split(&root, "The gap is 12 ft.");
    let due = owed_now(&root);
    let why = due.iter().find(|(k, _)| k == gap).map(|(_, w)| w.as_str());
    assert_eq!(why, Some("triage"), "{due:?}");
    let out = root.join("b-split");
    let cur = current(&root, &root.join("research/questions")).unwrap();
    super::super::bundle::bundle(&root, &cur, &[gap.to_owned()], &out, &[], &[]).unwrap();
    assert!(out.join("questions/0003-moved.html.txt").is_file());
    let units = std::fs::read_to_string(out.join("units.json")).unwrap();
    assert!(units.contains("\"0003-moved.html\""), "{units}");
    put(
        &root,
        "reply-split.txt",
        &format!("VERDICT {gap} IN-STEP - fine [§1]"),
    );
    let got = crate::claims::tests::claims(
        &root,
        &[
            "record",
            "--bundle",
            &out.to_string_lossy(),
            "--reply",
            &root.join("reply-split.txt").to_string_lossy(),
        ],
    );
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    assert!(owed_now(&root).iter().all(|(k, _)| k != gap));
    put(
        &root,
        "research/questions/0003-moved.html",
        "<h2 id=\"moved\">Moved</h2>\n<p>The gap is 14 ft.</p>\n",
    );
    assert!(owed_now(&root).iter().any(|(k, _)| k == gap));
    // a page with no pointer reads as itself alone: no unsplit claim's fingerprint moves
    let q = root.join("research/questions");
    let names = vec!["0002-other.drawing.html".to_owned()];
    assert_eq!(super::super::bundle::follow_names(&names, &q), names);
}

/// 451 T196, T194's for the claims: a block moved with an edit to a page the pointers reach is shown as moved, with its diff, never
/// as removed.
#[test]
fn a_block_moved_with_an_edit_is_shown_moved_with_its_diff() {
    let root = crate::claims::tests::fixture_with("claims-moved-edited", &|r| {
        put(r, "research/questions/0001-gap.html", "<h2 id=\"gap\">The gap</h2>\n<p class=\"intro\">Why.</p>\n<p>The gap is kept 12 ft.</p>\n<p>A second block.</p>\n");
    });
    record_all(&root);
    let ix = load_map(&root.join("dev/claims-index.json")).unwrap();
    let store = load_map(&root.join("dev/claims-pages.json")).unwrap();
    split(&root, "The gap is kept 14 ft.");
    let text = manifest_of(&root, &ix, &store, &["rust/phases/src/lib.rs::GAP#gap"]);
    let moved = text.contains("Moved with edits (to a page its pointers reach):\n  OLD: The gap is kept 12 ft.\n  NEW: The gap is kept 14 ft.\n  WORD DIFF: ");
    assert!(moved && !text.contains("Removed blocks"), "{text}");
}

/// 451 T196: a pure split owes no dispatch - its claims, every rest standing verbatim on the page the pointer reaches, are cleared by
/// `claims triage` mechanically (feature 432) and recorded reading the target.
#[test]
fn a_pure_split_is_cleared_without_a_dispatch() {
    let root = fixture("claims-pure-split");
    record_all(&root);
    split(&root, "The gap is 12 ft.");
    let out = root.join("t-split");
    let got = crate::claims::tests::claims(&root, &["triage", "--out", &out.to_string_lossy()]);
    let said = format!("{}{}", got.stdout, got.stderr);
    let cleared = said.contains("claim(s) cleared without a triage");
    let dispatched = out.join("MANIFEST.md").exists();
    assert!(cleared && !dispatched, "{said}");
    assert!(owed_now(&root).is_empty());
    let ix = load_map(&root.join("dev/claims-index.json")).unwrap();
    assert!(ix["rust/phases/src/lib.rs::GAP#gap"]["pages"]
        .get("0003-moved.html")
        .is_some());
}

/// Feature 451 T211 (the cascade test's 22 forced claims): a section claim recorded with its class word, then made to name its item
/// (T192's `#item` anchor, the class kept), has the code it was judged at - `claims-owed` reads it so (T204) - and the triage reads it
/// the same: its own line in the section's diff is no code change, so a visible edit elsewhere in its section forces nothing, and an
/// edit no claim repeats is cleared by the tool.
#[test]
fn a_claim_that_only_named_its_item_is_no_code_change_at_the_triage() {
    const CLAIM: &str = "other size - GUESS research/questions/0002-other.drawing.html";
    let root = crate::claims::tests::fixture_with("claims-triage-anchor", &|r| {
        let b = crate::claims::tests::BUILDINGS.replace(
            "<!-- Research: walls - CONVENTION -->\n",
            &format!(
                "<!-- Research: walls - CONVENTION -->\n<!-- Research: {CLAIM}: drawn 40 ft -->\n"
            ),
        );
        put(r, "docs/buildings.md", &b);
    });
    record_all(&root);
    commit_as_origin(&root, "recorded");
    let (ix, store) = (
        load_map(&root.join("dev/claims-index.json")).unwrap(),
        load_map(&root.join("dev/claims-pages.json")).unwrap(),
    );
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace(&format!("{CLAIM}:"), &format!("{CLAIM}#other:"))
            .replace("Walls stand.\n", "Walls stand, rebuilt.\n"),
    )
    .unwrap();
    let key = "docs/buildings.md::Walls#other size";
    let owed: Vec<(String, String)> = owed_now(&root);
    let why = crate::claims::index::SECTION_TRIAGE.to_owned();
    assert!(owed.contains(&(key.to_owned(), why)), "{owed:?}");
    manifest_of(&root, &ix, &store, &[key]);
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    let forced = data["forced"].as_array().unwrap();
    assert!(!forced.contains(&json!(key)), "{data}");
    assert_eq!(cleared_of(&root), [key]);
}

/// Feature 451 T210 (the cascade test's 147 forced claims): `claims-checked` over a section holding words that never reach a commit (a
/// hand edit of a generated row), then the words put back (the row regenerated). The snapshot's words are kept when it is recorded, so
/// the triage shows the edit as a pair and the filter judges it per claim - here no claim repeats its words, so both are cleared by the
/// tool - where before every claim of the section was forced to impl-drift, its removed words in no commit.
#[test]
fn a_section_snapshot_s_uncommitted_words_are_kept_so_putting_them_back_forces_nothing() {
    let (root, _, _) = recorded();
    let committed = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        committed.replace("Walls stand.\n", "Walls stand, as a hand edit had it.\n"),
    )
    .unwrap();
    let keys = [
        "docs/buildings.md::Walls#walls",
        "docs/buildings.md::Walls#wall height",
    ];
    let o = root.join("b-hand");
    let o = o.to_string_lossy();
    let got = crate::claims::tests::claims(
        &root,
        &[
            "bundle",
            "--units",
            &keys.join(","),
            "--out",
            &o,
            "--reason",
            "a re check",
        ],
    );
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    let reply = root.join("reply-hand.txt");
    std::fs::write(
        &reply,
        keys.map(|k| format!("VERDICT {k} IN-STEP - fine [§1]\n"))
            .concat(),
    )
    .unwrap();
    let got = crate::claims::tests::claims(
        &root,
        &[
            "record",
            "--bundle",
            &o,
            "--reply",
            &reply.to_string_lossy(),
        ],
    );
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    std::fs::write(root.join("docs/buildings.md"), &committed).unwrap();
    let owed = owed_now(&root);
    let why = crate::claims::index::SECTION_TRIAGE;
    for k in keys {
        let pair = (k.to_owned(), why.to_owned());
        assert!(owed.contains(&pair), "{owed:?}");
    }
    let (ix, store) = (
        load_map(&root.join("dev/claims-index.json")).unwrap(),
        load_map(&root.join("dev/claims-pages.json")).unwrap(),
    );
    manifest_of(&root, &ix, &store, &keys);
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    assert_eq!(data["forced"], json!([]), "{data}");
    assert_eq!(cleared_of(&root), keys);
}

/// Feature 451 T210: where no kept words hold a section's snapshot (one recorded before T210 kept them), its removed words are found
/// in its history, so an edit of committed words is shown as a pair and forces nothing.
#[test]
fn with_no_kept_words_a_section_s_removed_block_is_found_in_its_history() {
    let (root, ix, store) = recorded();
    std::fs::remove_file(root.join(super::kept::SECTION_WORDS)).unwrap();
    let b = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        b.replace("Walls stand.\n", "Walls stand, rebuilt.\n"),
    )
    .unwrap();
    let text = manifest_of(&root, &ix, &store, &["docs/buildings.md::Walls#walls"]);
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    assert_eq!(data["forced"], json!([]), "{text}");
}

/// Feature 451 T215: the T210 case triaged in another clone - the snapshot's words recorded, then the clone's own `.git` blob map gone
/// (a fresh clone holds none). The words live in the repository beside the index (`dev/claims-section-words.jsonl`), so putting the
/// hand edit back still forces nothing; with them kept only in the clone, both claims were forced.
#[test]
fn a_section_snapshot_s_words_live_in_the_repository_so_another_clone_forces_nothing() {
    let (root, _, _) = recorded();
    let committed = std::fs::read_to_string(root.join("docs/buildings.md")).unwrap();
    std::fs::write(
        root.join("docs/buildings.md"),
        committed.replace("Walls stand.\n", "Walls stand, as a hand edit had it.\n"),
    )
    .unwrap();
    let keys = [
        "docs/buildings.md::Walls#walls",
        "docs/buildings.md::Walls#wall height",
    ];
    let o = root.join("b-hand");
    let o = o.to_string_lossy();
    let args = [
        "bundle",
        "--units",
        &keys.join(","),
        "--out",
        &o,
        "--reason",
        "a re check",
    ];
    let got = crate::claims::tests::claims(&root, &args);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    let reply = root.join("reply-hand.txt");
    let text = keys
        .map(|k| format!("VERDICT {k} IN-STEP - fine [§1]\n"))
        .concat();
    std::fs::write(&reply, text).unwrap();
    let args = [
        "record",
        "--bundle",
        &o,
        "--reply",
        &reply.to_string_lossy(),
    ];
    let got = crate::claims::tests::claims(&root, &args);
    assert_eq!(got.code, 0, "{}{}", got.stdout, got.stderr);
    std::fs::write(root.join("docs/buildings.md"), &committed).unwrap();
    // another clone: no blob map of its own
    let _ = std::fs::remove_file(root.join(".git").join(super::BLOBS));
    let (ix, store) = (
        load_map(&root.join("dev/claims-index.json")).unwrap(),
        load_map(&root.join("dev/claims-pages.json")).unwrap(),
    );
    manifest_of(&root, &ix, &store, &keys);
    let data: Value =
        serde_json::from_str(&std::fs::read_to_string(root.join("t/triage.json")).unwrap())
            .unwrap();
    assert_eq!(data["forced"], json!([]), "{data}");
    assert_eq!(cleared_of(&root), keys);
}

/// Feature 451 T215: the repository's section words hold the blocks of the snapshots the index names and no more - a regenerated block
/// adds one line and its replaced block's line goes once no named snapshot holds it - written only when they change; a line that does
/// not parse, or whose words do not hash to its digest, is not read.
#[test]
fn the_section_words_are_pruned_to_the_named_snapshots_one_line_a_block() {
    use crate::record::units::digest;
    let dir = l7r_shared::tempdir::TempDir::new("claims-section-words");
    let root = dir.path();
    std::fs::create_dir_all(root.join("dev")).unwrap();
    let (a, b, c) = ("A row.", "B row.", "B row, regenerated.");
    let (da, db, dc) = (digest(&[a]), digest(&[b]), digest(&[c]));
    let ix = |core: &str| {
        json!({"k#x": {"section": core}, "k#y": {"pages": {}}})
            .as_object()
            .unwrap()
            .clone()
    };
    let store = json!({"old": [da, db], "new": [da, dc]})
        .as_object()
        .unwrap()
        .clone();
    let texts = |core: &str, w: &[&str]| json!({super::SECTION_TEXTS: {core: w}});
    assert_eq!(
        super::keep_sections(root, &texts("old", &[a, b]), &ix("old"), &store).unwrap(),
        2
    );
    let path = root.join(super::kept::SECTION_WORDS);
    let first = std::fs::read_to_string(&path).unwrap();
    assert_eq!(first.lines().count(), 2);
    // nothing new: the file is not written again
    std::fs::write(&path, &first).unwrap();
    let stamp = std::fs::metadata(&path).unwrap().modified().unwrap();
    assert_eq!(
        super::keep_sections(root, &json!({}), &ix("old"), &store).unwrap(),
        2
    );
    assert_eq!(std::fs::metadata(&path).unwrap().modified().unwrap(), stamp);
    // the row regenerated and re-checked: its new block in, its old one out
    assert_eq!(
        super::keep_sections(root, &texts("new", &[a, c]), &ix("new"), &store).unwrap(),
        2
    );
    let second = std::fs::read_to_string(&path).unwrap();
    let lines = |t: &str| t.lines().map(str::to_owned).collect::<HashSet<_>>();
    assert_eq!(lines(&first).difference(&lines(&second)).count(), 1);
    assert_eq!(lines(&second).difference(&lines(&first)).count(), 1);
    assert!(second.contains(c) && !second.contains(b));
    // a hand-edited line, a broken one and a line of another key are not read; the next write drops them
    let bad = format!(
        "{second}{{\"block\": \"{db}\", \"words\": \"not B\"}}\nnot json\n{{\"words\": 3}}\n"
    );
    std::fs::write(&path, bad).unwrap();
    let want: HashSet<String> = [db.clone(), dc.clone()].into();
    let got = super::section_words(root, "docs/x.md", "X", &want);
    assert_eq!(got.keys().collect::<Vec<_>>(), [&dc]);
    super::keep_sections(root, &json!({}), &ix("new"), &store).unwrap();
    assert_eq!(std::fs::read_to_string(&path).unwrap(), second);
}

/// Feature 451 T223: a block the kept words were pruned of, in no commit of its document, is found in the kept words' own history - a
/// landing reads a row at an earlier answer, and that answer's snapshot was named, and its words kept, when it was recorded.
#[test]
fn a_pruned_block_s_words_are_found_in_the_kept_words_history() {
    use crate::record::units::digest;
    let root = fixture("claims-section-words-history");
    let (a, b) = ("A row never committed.", "B row never committed.");
    let line = |w: &str| format!("{{\"block\": \"{}\", \"words\": \"{w}\"}}\n", digest(&[w]));
    put(&root, super::kept::SECTION_WORDS, &(line(a) + &line(b)));
    commit(&root, "the kept words");
    put(&root, super::kept::SECTION_WORDS, "");
    commit(&root, "pruned");
    let want: HashSet<String> = [digest(&[a]), digest(&[b]), digest(&["never kept"])].into();
    let got = super::section_words(&root, "docs/buildings.md", "Walls", &want);
    assert_eq!(got.values().collect::<Vec<_>>().len(), 2);
    assert_eq!(got[&digest(&[a])], a);
    let one: HashSet<String> = [digest(&[b])].into();
    assert_eq!(
        super::section_words(&root, "docs/buildings.md", "Walls", &one)[&digest(&[b])],
        b
    );
}
