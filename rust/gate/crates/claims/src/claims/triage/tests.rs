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
    let reply = "VERDICT a::b#c IN-STEP - fine\nVERDICT a::b#c IN-STEP - research/questions/0001-gap.html fine\n\n## OUTSIDE THE CHANGE\n- `x.py` | the block | a finding\n";
    let (kept, bad) = vet(reply, &units, &root, &mut said, &mut warned).unwrap();
    assert!(bad.is_empty() && kept.contains("OUTSIDE"));
    assert_eq!(
        said,
        "claims-checked: filed, not fixed - x.py | the block | a finding\n"
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
