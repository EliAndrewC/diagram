//! `l7r-gate reviews ledger-lint`, `ledger-rows` and `review-cost` (feature 449 T83, `ask:449-T83-scope`): the command lines of
//! `scripts/reviews/ledger_lint.py` and `review_cost.py`, and the measured rows `review_census.py` read (its port, `census.rs`, reads them in process since feature 449 T136; the command form stays). The lint and the cost themselves
//! are the guard's `shared::ledger` (one implementation, FR-003): the guards call them in process, and the guard crate cannot reach these.
//!
//! What the Python raised (an unreadable ledger or transcript, a cost the transcript cannot give) is answered with exit 1 and a
//! `Traceback` line, as T82's ports answer one; argparse's own usage text is not kept (`ask:449-usage-text`), its exit 2 is.

use std::fmt::Write as _;
use std::path::{Path, PathBuf};

use l7r_guard::shared::ledger::cost::{cells, cost, read_segments, transcript};
use l7r_guard::shared::ledger::{measured_rows, problems, COLUMNS};
use serde_json::json;

use super::reply;
use crate::record::args::{parse, Spec};
use crate::Reply;

/// The reply the Python's uncaught raise gave: exit 1, what it had printed, and its message after a `Traceback` line.
#[must_use]
pub fn raised(printed: String, cmd: &str, why: &str) -> Reply {
    reply(
        printed,
        format!("Traceback (most recent call last):\n  l7r-gate reviews {cmd}\n{why}\n"),
        1,
    )
}

/// `ledger_lint.py [LEDGER]`: each measured row short of a cell, exit 1 when one is. The default ledger is the tree's own (`tree`, the
/// directory the Python's `__file__` stood in).
#[must_use]
pub fn lint_cli(args: &[String], tree: &Path) -> Reply {
    let ledger = args
        .first()
        .map_or_else(|| tree.join("dev/review-ledger.md"), PathBuf::from);
    match std::fs::read_to_string(&ledger) {
        Ok(text) => {
            let found = problems(&text);
            let out: String = found.iter().flat_map(|p| [p.as_str(), "\n"]).collect();
            reply(out, String::new(), i32::from(!found.is_empty()))
        }
        Err(e) => raised(
            String::new(),
            "ledger-lint",
            &format!("{}: {e}", ledger.display()),
        ),
    }
}

/// `ledger-rows [LEDGER]`: the measured rows of the ledger (its text on `input` when none is named), as `{"columns": [...], "rows":
/// [[line, [cells]], ...]}` - what `review_census.py` read of `ledger_lint` by import, until feature 449 T136's port asked `measured_rows` in process.
#[must_use]
pub fn rows_cli(args: &[String], input: &mut dyn std::io::Read) -> Reply {
    let mut text = String::new();
    let read = match args.first() {
        Some(path) => std::fs::read_to_string(path).map(|t| text = t),
        None => input.read_to_string(&mut text).map(|_| ()),
    };
    if let Err(e) = read {
        return raised(String::new(), "ledger-rows", &e.to_string());
    }
    let rows: Vec<serde_json::Value> = measured_rows(&text)
        .into_iter()
        .map(|(n, cells)| json!([n, cells]))
        .collect();
    reply(
        format!("{}\n", json!({"columns": COLUMNS, "rows": rows})),
        String::new(),
        0,
    )
}

/// `review_cost.py --agent <id> [--root DIR] [--last]`: the ledger's two cost cells of the agent's newest transcript, one line a return
/// when it was resumed (feature 371), only the latest with `--last`.
#[must_use]
pub fn cost_cli(args: &[String], home: &str) -> Reply {
    let usage = |why: &str| {
        reply(
            String::new(),
            format!("usage: l7r-gate reviews review-cost --agent ID [--root DIR] [--last]\nl7r-gate reviews review-cost: error: {why}\n"),
            2,
        )
    };
    let p = match parse(
        args,
        &[
            Spec::value("--agent"),
            Spec::value("--root"),
            Spec::flag("--last"),
        ],
    ) {
        Ok(p) => p,
        Err(why) => return usage(&why),
    };
    if !p.has("--agent") {
        return usage("the following arguments are required: --agent");
    }
    let default_root = format!("{home}/.claude/projects");
    let (agent, root) = (p.text("--agent", ""), p.text("--root", &default_root));
    let Some(path) = transcript(agent, Path::new(root)) else {
        return reply(
            String::new(),
            format!("_review_cost: no transcript for agent {agent} under {root}\n"),
            1,
        );
    };
    let parts = match read_segments(&path) {
        Ok(parts) => parts,
        Err(why) => return raised(String::new(), "review-cost", &why),
    };
    let chosen: Vec<&Vec<String>> = if p.on("--last") {
        parts.last().into_iter().collect()
    } else {
        parts.iter().collect()
    };
    let mut out = String::new();
    for (n, part) in chosen.iter().enumerate() {
        match cost(part) {
            Ok(c) if chosen.len() == 1 => {
                let _ = writeln!(out, "{}", cells(&c));
            }
            Ok(c) => {
                let _ = writeln!(out, "return {}: {}", n + 1, cells(&c));
            }
            Err(why) => return raised(out, "review-cost", &why),
        }
    }
    reply(out, String::new(), 0)
}

#[cfg(test)]
mod tests;
