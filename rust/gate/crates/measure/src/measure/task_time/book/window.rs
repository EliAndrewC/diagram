//! The window's sweeps beside the walk: how many actors worked at once, and the review agents' and page sessions' minutes.

use std::collections::HashSet;

use super::{review_cat, Cell, Ix, Ledger, What, World, PAGES};

/// The window's seconds by how many actors worked at once: a main session in its own turn or run (never a wait, the GM's or idle),
/// an agent inside one of its spans, a page session in one of its phases.
pub(super) fn at_once(w: &World, ix: &Ix, order: &[String], paged: &HashSet<String>) -> [f64; 4] {
    let (lo, hi) = w.window;
    let mut edges: Vec<(f64, i32)> = Vec::new();
    let mut put = |a: f64, b: f64| {
        let (a, b) = (a.max(lo), b.min(hi));
        if b > a {
            edges.extend([(a, 1), (b, -1)]);
        }
    };
    for who in order
        .iter()
        .filter(|w| w.starts_with("s:") && !paged.contains(*w))
    {
        for s in &ix.segs[who] {
            let working = match &s.what {
                What::Own(c) => !c.starts_with("the GM") && !c.starts_with("idle"),
                What::Run(_) => true,
                What::Wait(..) => false,
            };
            if working {
                put(s.t0, s.t1);
            }
        }
    }
    for a in w.agents {
        for sp in &a.spans {
            put(sp.0, sp.1);
        }
    }
    for p in w.pages {
        put(p.t0, p.t1);
    }
    edges.sort_by(|a, b| a.0.total_cmp(&b.0).then(a.1.cmp(&b.1)));
    let mut out = [0.0; 4];
    let (mut n, mut at) = (0_i32, lo);
    for (t, d) in edges {
        out[usize::try_from(n).unwrap_or(0).min(3)] += t - at;
        at = t;
        n += d;
    }
    out[0] += hi - at;
    out
}

/// The minutes of every review agent's span and every page-session phase, clipped to the window.
pub(super) fn span_minutes(w: &World, ix: &Ix, l: &mut Ledger) {
    let (lo, hi) = w.window;
    for (i, a) in w.agents.iter().enumerate() {
        if let Some(cat) = review_cat(&a.kind) {
            let secs: f64 = a
                .spans
                .iter()
                .map(|s| (s.1.min(hi) - s.0.max(lo)).max(0.0))
                .sum();
            l.add(
                &ix.agent_key[i],
                cat,
                "",
                Cell {
                    min: secs,
                    ..Cell::default()
                },
            );
        }
    }
    for p in w.pages {
        l.add(
            &p.key,
            PAGES,
            "",
            Cell {
                min: (p.t1.min(hi) - p.t0.max(lo)).max(0.0),
                ..Cell::default()
            },
        );
    }
}
