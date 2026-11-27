//! EVERY TOKEN FIGURE BY MODEL (feature 451 T532; the GM's fifteenth process-reviewer message, 2026-11-27, kept in
//! `specs/449-rust-codebase/port-talk-gm-goal.md`: a day on Fable "really don't want that to make it look like everything was twice as
//! expensive that day"). The counts stay the raw `usage` fields the report already reads - never dollars, never weighted by a
//! model's rate against the weekly quota, and no rate stored here - split by each call's `message.model`: a landed task's by actor
//! and model, each actor's window totals by model, and the window's model mix with its concurrency (the pool trees held,
//! time-weighted, 461 FR-010), so a window is compared with one alike in both. One session's transcript held both models
//! (observed 2026-11-27, method: counting `message.model` in c6fd72d1's transcript - 16,248 calls on `claude-opus-5-5`, 2,583 on
//! `claude-fable-5-2`). A row naming no model (none was seen but `<synthetic>`, which names its own) is [`NO_MODEL`]'s.

use std::fmt::Write as _;

use super::super::events::fixed;
use super::super::where_time::columns::spent::{add_models, Models, Tok, NO_MODEL};
use super::beside::Extra;
use super::book::Key;
use super::cross::Cross;
use super::pct;
use super::turns::ByModel;

/// The pool trees held over `window`, time-weighted: the tree-seconds `cross` counted over the window's seconds.
#[must_use]
pub fn trees(cross: &Cross, (lo, hi): (f64, f64)) -> f64 {
    if hi > lo {
        cross.held / (hi - lo)
    } else {
        0.0
    }
}

/// Every token a call's usage names.
fn all(t: &Tok) -> f64 {
    t.out + t.fresh + t.cached + t.created
}

/// Tokens in thousands.
fn kilo(x: f64) -> String {
    format!("{}k", fixed(x / 1000.0, 1))
}

/// Every token of every actor of `b`.
fn whole(b: &ByModel) -> f64 {
    [&b.builders, &b.agents, &b.session]
        .iter()
        .flat_map(|m| m.values())
        .map(|(_, t)| all(t))
        .sum()
}

/// One table row a model of each actor of `b`, `who` its first cell, each total its share of `b`'s.
fn rows(out: &mut String, who: &str, b: &ByModel) {
    let of = whole(b);
    for (actor, m) in [
        ("builders", &b.builders),
        ("review agents", &b.agents),
        ("session", &b.session),
    ] {
        for (model, (n, t)) in m {
            let _ = writeln!(
                out,
                "| {who} | {actor} | {model} | {n} | {} | {} | {} | {} | {} ({}) |",
                kilo(t.out),
                kilo(t.fresh),
                kilo(t.cached),
                kilo(t.created),
                kilo(all(t)),
                pct(all(t), of)
            );
        }
    }
}

/// The window's model mix: each model's calls and tokens over every actor, the most tokens first, with its concurrency.
#[must_use]
pub fn mix(b: &ByModel, held: f64) -> String {
    let mut by = Models::new();
    for m in [&b.builders, &b.agents, &b.session] {
        add_models(&mut by, m);
    }
    let of = whole(b);
    let mut models: Vec<(&String, &(usize, Tok))> = by.iter().collect();
    models.sort_by(|a, b| all(&b.1 .1).total_cmp(&all(&a.1 .1)).then(a.0.cmp(b.0)));
    let each: Vec<String> = models
        .iter()
        .map(|(model, (n, t))| {
            format!(
                "{model} {n} calls, {} tokens ({})",
                kilo(all(t)),
                pct(all(t), of)
            )
        })
        .collect();
    format!(
        "The window's model mix (451 T532): {} - at {} pool trees held, time-weighted over the window (461 FR-010's concurrency, \
         from the pool's log), so a window is compared with one alike in both.\n",
        if each.is_empty() {
            "no calls".to_owned()
        } else {
            each.join("; ")
        },
        fixed(held, 2)
    )
}

/// The tokens-by-model table: each landed task's actors by model, then the window's, then its model mix.
pub fn table(out: &mut String, landed: &[(f64, Key)], x: &Extra) {
    let _ = write!(
        out,
        "## Tokens by model (451 T532: each call's `message.model`, the raw usage counts - never dollars, never weighted by a \
         model's rate against the quota; {NO_MODEL} where a row names none)\n\n\
         | task | actor | model | calls | output | fresh input | cache read | cache write | tokens (% of the task's) |\n\
         |---|---|---|---|---|---|---|---|---|\n"
    );
    let none = ByModel::default();
    for (_, k) in landed {
        rows(
            out,
            &format!("{} {}", k.0, k.1),
            x.models.0.get(k).unwrap_or(&none),
        );
    }
    rows(out, "the window", &x.models.1);
    let _ = writeln!(out, "\n{}", mix(&x.models.1, x.trees));
}
