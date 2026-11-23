//! THE UNITS A MAP NOT CURRENT HIDES (feature 451 T164). A live hamlet's or compound's legend is known only from a current drawing, so a
//! map the generation cache does not serve owes none of the reviews its new elements owe - and on 2026-11-22 the 449 T289 bundle's
//! reviews waited hours on a Mode A binary another bundle's edit had left older than its sources, the new genkan's glyph-check and
//! size-audit dropped with no word but a generic "not current" line. So the problem line names the stale engine (the launcher's own
//! words, asked once an engine, building none) and the units the map's last drawing already shows it hides: the elements that drawing
//! holds and its base legend lacks. A drawing older than the change can hide more than it shows, which the line says too, so a reader
//! never takes the list for the whole.
//!
//! Research: plumbing - NONE: says which owed units a stale drawing hides, deciding nothing about a map

use std::collections::{BTreeMap, BTreeSet};
use std::path::{Path, PathBuf};

use l7r_gate_pool::cache::engine::{Binaries, Engine, Launcher};
use l7r_gate_pool::Kind;

use super::{
    has_census, ink_classes, sheet_kinds, Folder, Legends, Tree, Unit, DRIVER, NOT_ELEMENTS,
};

/// Each engine's staleness, asked of the launcher once a run and building none.
pub(super) struct Engines {
    probe: Box<dyn Binaries>,
    known: BTreeMap<Engine, Option<String>>,
}

impl Engines {
    /// The launcher of the tree at `root`, told to build nothing.
    pub(super) fn new(root: &Path) -> Self {
        Self::with(Box::new(Launcher {
            root: root.to_path_buf(),
            build: false,
        }))
    }

    /// Over `probe`'s binaries (a stand-in in a test).
    pub(super) fn with(probe: Box<dyn Binaries>) -> Self {
        Self {
            probe,
            known: BTreeMap::new(),
        }
    }

    /// Why the engine drawing a map of `kind` names no fresh binary, or None (fresh, or no engine draws it).
    pub(super) fn stale(&mut self, kind: Kind) -> Option<String> {
        let engine = Engine::of(kind)?;
        let probe = &mut self.probe;
        self.known
            .entry(engine)
            .or_insert_with(|| probe.binary(engine).err())
            .clone()
    }
}

/// A folder's legend as last drawn, whatever its spec or engine says now: a hamlet's driver census, a sheet's kinds.
fn last_drawing(d: &Folder) -> BTreeSet<String> {
    let read = |p: PathBuf| {
        std::fs::read(p)
            .ok()
            .map(|b| String::from_utf8_lossy(&b).into_owned())
    };
    if d.kind == Kind::Hamlet {
        let text = read(d.file(DRIVER));
        return if has_census(text.as_deref()) {
            ink_classes(text.as_deref())
        } else {
            BTreeSet::new()
        };
    }
    sheet_kinds(read(d.file(".svg")).as_deref())
}

/// The tree's problem lines, each folder whose legend is not known told the units its last drawing shows it hides.
pub(super) fn named(tree: &Tree, before: &Legends) -> Vec<String> {
    let mut problems = tree.problems.clone();
    let pool: BTreeSet<String> = before.0.iter().flat_map(|(_, s)| s.clone()).collect();
    // every unknown name is a folder's (`legends` took it from one)
    for (at, d) in tree
        .unknown
        .iter()
        .filter_map(|(at, name)| Some((at, tree.folders.iter().find(|d| &d.name == name)?)))
    {
        let name = &d.name;
        let was = before.get(name).unwrap_or(&pool);
        let units: Vec<String> = (&last_drawing(d) - was)
            .iter()
            .filter(|e| !NOT_ELEMENTS.contains(&e.as_str()))
            .flat_map(|e| {
                let glyph = Unit::new("glyph-check", e, name, String::new()).slug();
                let size = d
                    .is_sheet()
                    .then(|| Unit::new("size-audit", e, name, String::new()).slug());
                std::iter::once(glyph).chain(size)
            })
            .collect();
        let told = if units.is_empty() {
            "; the units its new elements owe are HIDDEN until it is drawn (its last drawing holds none its base lacks)".to_owned()
        } else {
            format!(
                "; the units it HIDES until it is drawn, at least (its last drawing's; a drawing older than the change hides more): {}",
                units.join(", ")
            )
        };
        if let Some(line) = problems.get_mut(*at) {
            line.push_str(&told);
        }
    }
    problems
}

#[cfg(test)]
mod tests;
