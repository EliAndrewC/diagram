//! THE INDEX AS A LANDING READS IT (feature 451 T223, the round arbiter's `ask:mixed-build-241-claims`). WHY: a triage clear recorded
//! by an l7r-gate holding another builder's uncommitted code (its row's `build`, T197) was owed a full impl-drift at the landing,
//! because the clear had already overwritten the row's fingerprints with the tree it judged - the landing had no "before" left to
//! triage again. Measured 2026-11-24: 241 doc claims whose text, pages and code never changed were offered a full check as the only
//! route, after a 920 s green landing was refused. The before is still in the repository: the index's own history holds the row as
//! the last clean build left it, and the store's history its page and section snapshots. So a landing alone reads each mixed row at
//! its fingerprints of that earlier answer - the mixed answer withdrawn, nothing else of the row touched - and the claim is owed
//! whatever the landing's own build finds between that answer and the tree: nothing, a triage (the mechanical clears first, then the
//! claims-triage agent), or impl-drift where the change is one a triage never judges. A row with no clean answer in the walk stays
//! mixed and owes impl-drift ([`super::index::owed`]). Outside a landing the index is read as it stands.

use std::collections::BTreeMap;
use std::path::Path;

use serde_json::{Map, Value};

use super::index::{load_map, Index, Landing, Store, INDEX, STORE};
use crate::record::repo::{git, Fail};

/// How far back the index's history is read for a row's last clean answer, as [`super::triage::checked_at`] reads it.
const WALK: &str = "-n60";
/// What a triage clear writes of a row ([`super::triage::record_triage`], `record_cleared`, `clear_page_moves`): the fields a mixed
/// answer is withdrawn by. The verdict, its note and date, the claim as said and its rests are no triage's and stay.
const ANSWER: [&str; 10] = [
    "research", "pages", "section", "code", "core", "reads", "triaged", "cleared", "triage",
    "build",
];

/// The index and the page snapshots as this run reads them, and each claim whose mixed answer was withdrawn with the uncommitted
/// files its build held.
pub struct Read {
    pub index: Index,
    pub store: Store,
    pub mixed: BTreeMap<String, Vec<String>>,
}

/// `row` with its triage answer put back to `base`'s.
fn withdraw(row: &mut Map<String, Value>, base: &Value) {
    for f in ANSWER {
        match base.get(f) {
            Some(v) => row.insert(f.to_owned(), v.clone()),
            None => row.shift_remove(f),
        };
    }
}

/// The tracked file `path` as the commit `sha` holds it; empty where it holds none or it does not parse.
fn at(root: &Path, sha: &str, path: &str) -> Index {
    serde_json::from_str(&git(root, &["show", &format!("{sha}:{path}")])).unwrap_or_default()
}

/// The index and store of `root`; in a landing alone, each row a mixed build answered read at its last clean answer in the index's
/// history, and that commit's snapshots beside today's.
pub fn read(root: &Path) -> Result<Read, Fail> {
    let mut read = Read {
        index: load_map(&root.join(INDEX))?,
        store: load_map(&root.join(STORE))?,
        mixed: BTreeMap::new(),
    };
    let Some(mut landing) = Landing::at(root) else {
        return Ok(read);
    };
    let mut left: BTreeMap<String, Vec<String>> = read
        .index
        .iter()
        .map(|(k, row)| (k.clone(), landing.paths(row)))
        .filter(|(_, paths)| !paths.is_empty())
        .collect();
    if left.is_empty() {
        return Ok(read);
    }
    for sha in git(root, &["log", WALK, "--format=%H", "--", INDEX]).split_whitespace() {
        let then = at(root, sha, INDEX);
        let before = read.mixed.len();
        left.retain(|key, paths| {
            // a commit with no row of the claim ends its walk: no answer before the mixed one
            let Some(base) = then.get(key) else {
                return false;
            };
            if !landing.paths(base).is_empty() {
                return true;
            }
            if let Some(row) = read.index.get_mut(key).and_then(Value::as_object_mut) {
                withdraw(row, base);
            }
            read.mixed.insert(key.clone(), std::mem::take(paths));
            false
        });
        if read.mixed.len() > before {
            for (digest, blocks) in at(root, sha, STORE) {
                read.store.entry(digest).or_insert(blocks);
            }
        }
        if left.is_empty() {
            break;
        }
    }
    Ok(read)
}

/// The page snapshots alone, for a reader handed its index: today's, and in a landing alone [`read`]'s.
pub fn store(root: &Path) -> Result<Store, Fail> {
    if l7r_gate_core::build::landing() {
        return Ok(read(root)?.store);
    }
    load_map(&root.join(STORE))
}
