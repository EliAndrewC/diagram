//! The tasks in flight as text (feature 451 T293): a block a builder's task, a block a landing, then one line each for the other
//! things running, the pool's free trees and the tasks staged in the clone.

use std::fmt::Write as _;

use l7r_shared::context::CAP_TOKENS;

use super::super::super::events::fixed;
use super::{AgentNow, Block, View};

/// Minutes, one decimal.
pub fn m(secs: f64) -> String {
    fixed(secs.max(0.0) / 60.0, 1)
}

/// A UTC time of day to the second.
pub fn hms(t: f64) -> String {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "seconds since the epoch, after it"
    )]
    let (_, _, _, h, mi, s) = l7r_shared::log::civil(t.max(0.0) as u64);
    format!("{h:02}:{mi:02}:{s:02}")
}

/// An agent's id as a reader can tell it from another: its first eight characters.
pub fn short(aid: &str) -> &str {
    aid.get(..8).unwrap_or(aid)
}

/// The category table of `rows`, each with its share of their sum.
fn table(out: &mut String, rows: &[(String, f64)]) {
    let all: f64 = rows.iter().map(|r| r.1).sum();
    out.push_str("| category | minutes | % |\n|---|---|---|\n");
    for (cat, s) in rows {
        let _ = writeln!(
            out,
            "| {cat} | {} | {}% |",
            m(*s),
            fixed(100.0 * s / all, 1)
        );
    }
    let _ = writeln!(out, "| all | {} | |\n", m(all));
}

/// One builder's line: its state, its dispatch, its context against the cap and how long since its last line.
fn agent(out: &mut String, a: &AgentNow, now: f64) {
    let state = match (a.running, a.resumed, a.stop) {
        (true, true, _) => "RUNNING, resumed after a stop (its later start and stop lines are not read, 451 T324: it may have stopped again since its last line)".to_owned(),
        (true, ..) => "RUNNING".to_owned(),
        (false, _, Some(t)) => format!("stopped {}", hms(t)),
        (false, ..) => "not running: no stop line, and its session's latest Stop does not name it in flight (cut off)".to_owned(),
    };
    #[expect(clippy::cast_precision_loss, reason = "a token count, far under 2^52")]
    let ctx = a.ctx.map_or_else(
        || "context not known (no transcript found, and no stop has logged it)".to_owned(),
        |(n, from)| {
            format!(
                "context {}k of the {}k cap ({}%, {from})",
                n / 1000,
                CAP_TOKENS / 1000,
                fixed(100.0 * n as f64 / CAP_TOKENS as f64, 0)
            )
        },
    );
    let _ = writeln!(
        out,
        "- builder {} ({}): {state}; dispatched {}, {} min ago; {ctx}; its last line {} min ago",
        short(&a.aid),
        a.kind,
        hms(a.t0),
        m(now - a.t0),
        m(now - a.last)
    );
}

fn block(out: &mut String, b: &Block, now: f64) {
    let tree = b.tree.as_ref().map_or_else(
        || "no pool tree is held for it".to_owned(),
        |(name, since)| {
            format!(
                "tree {name}, held since {} ({} min)",
                hms(*since),
                m(now - since)
            )
        },
    );
    let _ = writeln!(out, "## {} - {tree}\n", b.holder);
    if b.agents.is_empty() {
        out.push_str("- no builder has been dispatched for it since its tree was taken\n\n");
        return;
    }
    for a in &b.agents {
        agent(out, a, now);
    }
    for s in &b.steps {
        let _ = writeln!(out, "- {s}");
    }
    if let Some(at) = b.carried {
        let _ = writeln!(
            out,
            "- carried into the clone {}, {} min ago",
            hms(at),
            m(now - at)
        );
    }
    let _ = writeln!(
        out,
        "\nIts minutes so far{}, from its builders' dispatch:\n",
        if b.at_least {
            ", AT LEAST (a resumed builder's later spans are not read, 451 T324)"
        } else {
            ""
        }
    );
    table(out, &b.rows);
}

/// The report (the module's doc).
pub fn render(v: &View) -> String {
    let (lo, now) = v.span;
    let mut out = format!(
        "# The tasks in flight at {} UTC (lines read from {})\n\n\
         Minutes are machine minutes as `make task-time` books them, by its categories: a run and the turn beside it both count, so a \
         block's minutes can pass its clock. A phase has no line until it ends: the step named is the open run with its last finished \
         phase, and the phase running now is in the run's own category until then. A call open now is counted to this moment, and a \
         running builder's open turn is a row of its own.\n\n",
        hms(now),
        hms(lo)
    );
    for b in &v.blocks {
        block(&mut out, b, now);
    }
    if v.blocks.is_empty() {
        out.push_str("No pool tree is held and no builder is running.\n\n");
    }
    for l in &v.landings {
        let _ = writeln!(
            out,
            "## Landing in flight: {} - `make land` began {}, {} min in\n\n- {}\n\nIts minutes so far:\n",
            l.name,
            hms(l.t0),
            m(now - l.t0),
            l.phase.as_ref().map_or_else(
                || "no phase of it has finished".to_owned(),
                |(p, t)| format!("its last finished phase: {p}, ended {} ({} min ago)", hms(*t), m(now - t))
            )
        );
        table(&mut out, &l.rows);
    }
    let lines = |out: &mut String, head: &str, none: &str, list: &[String]| {
        let _ = writeln!(out, "## {head}\n");
        for l in list {
            let _ = writeln!(out, "- {l}");
        }
        if list.is_empty() {
            let _ = writeln!(out, "- {none}");
        }
        out.push('\n');
    };
    if v.landings.is_empty() {
        out.push_str("No landing is in flight.\n\n");
    }
    lines(
        &mut out,
        "Also running",
        "no page session, and no review agent of the session's own",
        &v.others,
    );
    let free: Vec<String> = v
        .free
        .iter()
        .map(|(t, since)| format!("{t}, free since {since}"))
        .collect();
    lines(&mut out, "The pool's free trees", "none", &free);
    lines(
        &mut out,
        "Staged in the clone, not landed",
        "none: every task carried has landed or is in a landing in flight",
        &v.staged,
    );
    out
}
