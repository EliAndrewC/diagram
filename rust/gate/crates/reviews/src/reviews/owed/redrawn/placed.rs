//! THE RUST ENGINES' PLACEMENT CODE (feature 449 T238): a change to it owes no review the change itself shows - an engine change that
//! moves things under rules already judged owes nothing (`docs/reviews.md`) - but whether it re-places an element by substantially
//! different rules is the feature's to DECLARE (`placement-changed:`, or `none: <why>`), and the push is refused until it does, as a
//! change to the deleted Python's placement code (`l7r/**/*.py`, `CODE`) was. Before this, a Rust stage's change owed nothing and refused
//! nothing (T237's plan, measured 2026-11-20: `CODE` names no `rust/` path, and `redrawn` reads only the drawing code). The code:
//!
//! - a STAGE: every `.rs` file under `rust/phases/src/` and `rust/mode_a/src/compound/` that is no engine's drawing code (`ENGINES`)
//!   and no test file (a name holding `tests`: `seat/tests.rs`, `compound/gen_tests_seat.rs`) - the hamlet's stages (field, sink, seat,
//!   hem, waterward, course, the random source the stages draw from) and the compound's layout, parts, fixtures, ground and spec; its
//!   change is any non-test item whose comment-free tokens differ (a `#[cfg(test)]` module, a comment, an import is none);
//! - the DRAWING CODE's part that redraws no element: a changed item of an engine's drawing files whose change reaches no element - a
//!   stage function inside the driver, a roll's line that hands the stages their ground (T239's seat ring in `roll_polder`), a mark
//!   drawn under the placeholder `-` - where a change that redraws an element owes its glyph-check from the change and asks nothing,
//!   and a type (a struct only the drawing fills, T234's `SluiceFrame`) is no placement by itself.
//!
//! A file the delta only moved is set aside by the caller (`touched_code`'s `moved_only`), as `CODE`'s are.

use std::collections::BTreeSet;
use std::path::Path;

use super::{engine_reach, items, sides, sides_of, tokens, Files, Item, ENGINES};

/// The stages' roots (recursive), measured 2026-11-20 (`ls` of `rust/phases/src/` and `rust/mode_a/src/compound/`, tests aside): the
/// hamlet's stages outside the driver and the compound's layout beside its marks.
const STAGES: [&str; 2] = ["rust/phases/src/", "rust/mode_a/src/compound/"];

fn is_stage(path: &str) -> bool {
    let name = path.rsplit('/').next().unwrap_or(path);
    Path::new(path).extension().is_some_and(|x| x == "rs")
        && STAGES.iter().any(|s| path.starts_with(s))
        && !name.contains("tests")
        && !ENGINES.iter().any(|e| e.holds(path))
}

/// Each non-test item of `file` in `files`, by name, with its comment-free tokens.
fn shape(files: &Files, file: &str) -> Vec<(String, Vec<u8>)> {
    let mut found: Vec<Item> = Vec::new();
    for (path, text) in files.iter().filter(|(p, _)| p == file) {
        items(text, path, None, &mut found);
    }
    let mut out: Vec<(String, Vec<u8>)> =
        found.iter().map(|i| (i.name.clone(), tokens(i))).collect();
    out.sort();
    out
}

/// The placement code among the delta's files (`touched`: committed, staged, unstaged or untracked): each stage file whose code
/// changed, and each engine drawing file with a change that redraws no element.
pub(in crate::reviews::owed) fn placed(
    root: &Path,
    base: &str,
    touched: &BTreeSet<String>,
) -> BTreeSet<String> {
    let mut out = BTreeSet::new();
    if base.is_empty() {
        return out;
    }
    let staged: Vec<&str> = touched
        .iter()
        .map(String::as_str)
        .filter(|p| is_stage(p))
        .collect();
    if !staged.is_empty() {
        let (now, was) = sides_of(root, base, &staged, &is_stage);
        out.extend(
            staged
                .into_iter()
                .filter(|f| shape(&now, f) != shape(&was, f))
                .map(str::to_owned),
        );
    }
    for e in &ENGINES {
        let mine: BTreeSet<String> = touched.iter().filter(|p| e.holds(p)).cloned().collect();
        if mine.is_empty() {
            continue;
        }
        let (now, was) = sides(root, base, e);
        out.extend(engine_reach(e, &now, &was, &mine).silent);
    }
    out
}
