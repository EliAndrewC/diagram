//! AT A HAND-IN, THE OWED CLAIMS ARE THE BUILDER'S OWN (feature 461 T40). WHY: the claims gate refuses every claim owed a check with no
//! row, or whose code or research moved since its row, and none of that reads a base (`index::owed`). At a builder's hand-in in phase 1
//! the base is the clone's HEAD, every staged batch below it; a claim another task's staged code left owed refused the builder's
//! hand-in, a refusal only that task's claims round can cure. So at a hand-in that names its base (`delta_base::named`), an owed claim
//! the work leaves exactly as the base held it is the landing's to ask, not the builder's.
//!
//! The ruling it holds to: spec-fidelity's MODE 1 exception, 2026-11-27, LEGITIMATE with three bounds. (1) A claim whose unit's code,
//! claim text or cited research page the work touches, or one it adds or moves, is the builder's, never excused as "owed at the base
//! too": the test is the fingerprints `owed` itself compares, base row against the row now, so whatever would owe the claim from the
//! work owes it here; no base row under the key (added, or moved to a new key) is the builder's. (2) With no base named, or one that
//! names no commit, nothing is scoped. (3) Only the owed refusal is scoped: introduced findings, form problems and carries are not, and
//! a landing names no base, so it asks every owed claim.

use std::path::Path;

use super::index::{siblings_of, Cur, Index, Row};

/// What the hand-in's base held: its claim rows, its index and its tree.
pub(super) struct Base<'a> {
    pub rows: &'a Cur,
    pub index: &'a Index,
    /// The base tree's root, where its engine's sources are read.
    pub tree: &'a Path,
}

/// Is the claim of `now` as the base held it, in everything an owed reason reads? Its code (the unit's core and the claim's own text),
/// its research (every page it cites, as followed), the constants its unit reads, its unit's other claims and its index row; `engine`
/// says whether the Mode A engine is as the base held it, asked only of a section's finding owed because the engine moved.
fn kept(
    now: &Row,
    at_now: &Index,
    base: &Base<'_>,
    why: &str,
    engine: &mut dyn FnMut() -> bool,
) -> bool {
    let Some(was) = base.rows.get(&now.key) else {
        return false;
    };
    now.code == was.code
        && now.claim.normalized() == was.claim.normalized()
        && now.research == was.research
        && now.unit.reads == was.unit.reads
        && siblings_of(&now.unit) == siblings_of(&was.unit)
        && at_now.get(&now.key) == base.index.get(&now.key)
        && (why != super::drawn::DRAWN || engine())
}

/// Owed claims, each (key, why).
type Owed = Vec<(String, String)>;

/// `due` split at a hand-in: (the builder's, the landing's). `root` is the tree now; `due` every owed (key, why).
pub(super) fn split(
    root: &Path,
    due: Owed,
    cur: &Cur,
    at_now: &Index,
    base: &Base<'_>,
) -> (Owed, Owed) {
    let mut same_engine = None;
    let mut engine = || {
        *same_engine.get_or_insert_with(|| {
            super::drawn::drawn_by(root) == super::drawn::drawn_by(base.tree)
        })
    };
    due.into_iter().partition(|(k, why)| {
        !cur.get(k)
            .is_some_and(|row| kept(row, at_now, base, why, &mut engine))
    })
}

#[cfg(test)]
mod tests;
