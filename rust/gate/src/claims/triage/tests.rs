//! The triage bundle over each kind of change: a page's new, changed and removed blocks (from the kept snapshot, from the history, or
//! lost), a section's, a claimed dictionary's, a unit's diff; its reply recorded; a reply's outside rows filed.

use std::collections::{HashMap, HashSet};

use serde_json::{json, Map, Value};

use super::{checked_at, keep_texts, kept_text, record_triage, removed_words, triage_bundle, vet};
use crate::claims::index::{current, load_map};
use crate::claims::scope::Reader;
use crate::claims::tests::{fixture, record_all};
use crate::record::testkit::{commit, git, put};

fn units_doc(qual: &str, blocks: &[&str]) -> String {
    json!([{"path": "l7r/diagram/m.py", "qualname": qual, "kind": "constant", "lineno": 1, "end_lineno": 1, "claims": [], "inherited": false,
            "core": "c", "errors": [], "names": [], "blocks": blocks, "module_errors": []}])
    .to_string()
}

#[test]
fn each_kind_of_change_is_shown_and_its_reply_recorded() {
    let root = fixture("claims-triage-bundle");
    let table = units_doc("TABLE", &["'a': 1", "'gone': 2"]);
    put(&root, "l7r/diagram/m.py", &table);
    put(&root, "l7r/py-units.json", &json!([[], [{"path": "l7r/diagram/m.py", "qualname": "TABLE", "kind": "constant", "lineno": 1, "end_lineno": 1,
        "claims": ["table - NONE"], "inherited": false, "core": "core-1", "errors": [], "names": [], "blocks": ["'a': 1", "'gone': 2"], "module_errors": []}]]).to_string());
    commit(&root, "table");
    record_all(&root);
    commit(&root, "recorded");
    git(&root, &["update-ref", "refs/remotes/origin/main", "HEAD"]);
    put(&root, "l7r/diagram/m.py", &units_doc("TABLE", &["'a': 1"]));
    put(&root, "l7r/py-units.json", &json!([[], [{"path": "l7r/diagram/m.py", "qualname": "TABLE", "kind": "constant", "lineno": 1, "end_lineno": 1,
        "claims": ["table - NONE"], "inherited": false, "core": "core-2", "errors": [], "names": [], "blocks": ["'a': 1", "'new': 3"], "module_errors": []}]]).to_string());
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
    let mut reader = Reader::new(&root, &root);
    let cur = current(&mut reader, &root, &root.join("research/questions")).unwrap();
    let keys: Vec<String> = [
        "rust/phases/src/lib.rs::GAP#gap",
        "rust/phases/src/lib.rs::reach#reach",
        "rust/phases/src/lib.rs::Thing.m#method guess",
        "rust/phases/src/lib.rs::helper#plumbing",
        "docs/buildings.md::Walls#walls",
        "l7r/diagram/m.py::TABLE#table",
    ]
    .map(str::to_owned)
    .to_vec();
    let out = root.join("t");
    std::fs::create_dir_all(&out).unwrap();
    let manifest = triage_bundle(
        &mut reader,
        &cur,
        &ix,
        &store,
        &keys,
        &root.join("research/questions"),
        &out,
    )
    .unwrap();
    let text = std::fs::read_to_string(manifest).unwrap();
    for want in [
        "## docs/buildings.md::Walls (a procedure section; the claims' own lines did not change)\n\nNew or changed blocks:\n\n> Walls stand, rebuilt.\n",
        "Removed blocks (no longer in the section):\n\n> - a list item continued\n",
        "## l7r/diagram/m.py::TABLE (a procedure section",
        "> 'gone': 2\n",
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
    assert_eq!(new["docs/buildings.md::Walls#walls"]["triaged"], "d");
    assert_eq!(new["rust/phases/src/lib.rs::GAP#gap"]["triage"], "touched");
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
