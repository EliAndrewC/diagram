//! Settled choices stay settled (451 T190, the GM 2026-11-23, request.md "the convergence talk"): an EDIT that puts back the words an
//! earlier round's EDIT replaced - the A -> B -> A the event log's reversal wire names, here read off the rounds' own EDIT blocks - is
//! refused before it is applied, unless its finding states the factual error with its evidence. Measured 2026-11-23 over the 1,670 EDIT
//! blocks the clone's kept replies hold: 3 put back an earlier EDIT's words exactly. The looser test the round marks use (`near_reversal`,
//! two content words back) named 17 more, most of them a factual round widening a sentence, so it marks a round and never refuses one.

use std::collections::{BTreeMap, HashSet};
use std::path::{Path, PathBuf};
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_bundle::arbiter::bundle::marks::reply_of;
use l7r_shared::checks::reply::{categorized, factual};
use l7r_shared::checks::{load, state_path};
use l7r_shared::py_text::strip;
use serde_json::Value;

use super::{resolve, Block, Edit};
use crate::record::owed;

static REVERSES: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r"(?i)\bREVERSES round \d+:").unwrap_or_else(|e| unreachable!("{e}"))
});
static EVIDENCE: LazyLock<Regex> = LazyLock::new(|| {
    l7r_shared::regex::build(r#"(?i)\bevidence:[^\n]*?(?:["\u{201c}\u{300c}][^"\u{201d}\u{300d}\n]{4,}["\u{201d}\u{300d}]|research/\S+)"#)
        .unwrap_or_else(|e| unreachable!("{e}"))
});

/// An earlier round's EDIT: its file, its old and new text, and its check.
struct Earlier {
    file: PathBuf,
    old: String,
    new: String,
    check: String,
}

/// Every EDIT of the rounds the check state holds but `report`'s own.
fn earlier(root: &Path, report: &str) -> Vec<Earlier> {
    let Some(path) = state_path(&root.to_string_lossy()).filter(|p| p.is_file()) else {
        return Vec::new();
    };
    let state = load(&path);
    let mine = strip(report);
    state
        .get("dispatches")
        .and_then(Value::as_object)
        .into_iter()
        .flat_map(serde_json::Map::values)
        .flat_map(|v| {
            let reply = reply_of(v);
            let check = v
                .get("check")
                .and_then(Value::as_str)
                .unwrap_or("")
                .to_owned();
            let theirs = if strip(&reply) == mine {
                Vec::new()
            } else {
                categorized(&reply)
            };
            theirs.into_iter().filter_map(move |(p, old, new, _)| {
                resolve(root, &p).map(|file| Earlier {
                    file,
                    old,
                    new,
                    check: check.clone(),
                })
            })
        })
        .collect()
}

/// The earlier EDIT whose words `e` puts back: its new text replaced by that EDIT's old, exactly.
fn reversed<'a>(root: &Path, e: &Edit, earlier: &'a [Earlier]) -> Option<&'a Earlier> {
    let file = resolve(root, &e.path)?;
    earlier.iter().find(|x| {
        x.file == file
            && !strip(&x.old).is_empty()
            && strip(&x.new) == strip(&e.old)
            && strip(&x.old) == strip(&e.new)
    })
}

/// Whether `e`'s finding states a factual error with its evidence: `REVERSES round <n>:`, an `evidence:` quoting the words or naming
/// the page, and a factual category of its reply's check (a reply naming no check counts as factual, as T188 reads it).
fn stated(e: &Edit, checks: &[String]) -> bool {
    let hit = |r: &Regex| r.is_match(&e.finding).unwrap_or(false);
    hit(&REVERSES)
        && hit(&EVIDENCE)
        && (checks.is_empty() || checks.iter().all(|c| factual(c, &e.category)))
}

/// The refusal of each EDIT of `found` (by its number) that puts back what an earlier round replaced and states no factual error.
pub(super) fn refusals(
    root: &Path,
    report: &str,
    found: &[Block],
    skip: &HashSet<usize>,
) -> BTreeMap<usize, String> {
    let edits: Vec<&Edit> = found
        .iter()
        .filter_map(|b| {
            if let Block::Edit(e) = b {
                Some(e)
            } else {
                None
            }
        })
        .filter(|e| !skip.contains(&e.n))
        .collect();
    if edits.is_empty() {
        return BTreeMap::new();
    }
    let before = earlier(root, report);
    let checks = owed::reply_checks(report);
    edits
        .into_iter()
        .filter_map(|e| {
            let x = reversed(root, e, &before)?;
            (!stated(e, &checks)).then(|| {
                (e.n, format!(
                    "REFUSED - it puts back the words an earlier {} round's EDIT replaced ({}), a settled choice (451 T190): only a factual finding reverses one - open it `REVERSES round <n>: <the factual error>` with `evidence: <the page or source and its words, quoted>`; a wording finding never does",
                    x.check,
                    l7r_shared::py_text::repr(l7r_gate_core::record::bundle::head(&x.old, 80))
                ))
            })
        })
        .collect()
}
