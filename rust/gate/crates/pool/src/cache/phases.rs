//! `make map`'s PHASE LINES (feature 451 T153; the GM 2026-11-22: "we want everything measured so we know where our time goes, especially
//! for compiling, running tests, and generating maps"): a map's generation, its render and its page were one span of a Bash call, and a
//! CACHED hit was not told from a draw. Each map now writes its steps through the one Phase writer (`phase_row`, `append_row_with`), `src:
//! map`, `name` the map:
//!
//! - `cached`: the key held and the map served, from the entry's read to its last artifact linked;
//! - `generate`, `render`, `page`: a drawn map's engine run, cut where each artifact was last written. THE ENGINE IS NOT ASKED (a
//!   deliberate reading): the engine runs as one program, writing a Mode A sheet's svg, then its png (unless the picture switch is set),
//!   then its page (`compound/cli.rs`'s `draw`), so each file's mtime in the staging folder is the end of its step, and an edit of the
//!   engine to report its own timings would move every map's engine id and redraw the pool for a measurement. A hamlet's driver writes
//!   its svg and manifest at once, all `generate`; a hand sheet has no svg of its own to generate, its first step `render`. A step whose
//!   file is not there writes none; the last step runs to the engine's exit, whatever it wrote after its file.

use std::path::Path;
use std::time::SystemTime;

use l7r_shared::guards::event_log_hooks::{append_row_with, phase_row};
use serde_json::Value;

use super::Run;
use crate::walk::{Kind, Map};

/// Each step of `kind`'s engine run and the artifact ending it, in the order the engine writes them.
fn steps(kind: Kind) -> &'static [(&'static str, &'static str)] {
    match kind {
        Kind::Hamlet => &[("generate", ".driver.json")],
        Kind::Compound => &[("generate", ".svg"), ("render", ".png"), ("page", ".html")],
        _ => &[("render", ".png"), ("page", ".html")],
    }
}

/// A drawn map's spans: each step from the last one's end to its artifact's mtime in `staging` (the last to the engine's exit `t1`),
/// clamped inside the run `[t0, t1]`; a step whose artifact is not there is skipped.
#[must_use]
pub fn drawn(
    m: &Map,
    staging: &Path,
    (t0, t1): (SystemTime, SystemTime),
) -> Vec<(&'static str, SystemTime, SystemTime)> {
    let at = |end: &str| {
        let name = std::fs::read_dir(staging)
            .ok()?
            .flatten()
            .find(|e| e.file_name().to_string_lossy().ends_with(end))?;
        name.metadata().ok()?.modified().ok()
    };
    let found: Vec<(&str, SystemTime)> = steps(m.kind)
        .iter()
        .filter_map(|(step, end)| at(end).map(|t| (*step, t.clamp(t0, t1))))
        .collect();
    let mut out = Vec::new();
    let mut from = t0;
    for (i, (step, end)) in found.iter().enumerate() {
        let to = if i + 1 == found.len() { t1 } else { *end };
        out.push((*step, from, to.max(from)));
        from = to.max(from);
    }
    out
}

impl Run<'_> {
    /// One step of map `m`'s, its line written now. It feeds the task time breakdown (`make task-time`, 451 T243).
    pub(super) fn phase(&self, m: &Map, step: &str, span: (SystemTime, SystemTime), code: i32) {
        let mut row = phase_row("map", step, span, code, &self.make, &self.root);
        row.insert("name".into(), Value::from(m.rel()));
        let _ = append_row_with(&self.root, None, row, &self.opts.env);
    }
}

#[cfg(test)]
mod tests;
