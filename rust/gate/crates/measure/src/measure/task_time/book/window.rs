//! The window's sweeps beside the walk: how many actors worked at once, and the review agents' and page sessions' minutes.

use std::collections::{HashMap, HashSet};

use super::{review_cat, Cell, Ix, Key, Ledger, What, World, PAGES};

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

/// Each task's builders' seconds in the window and their count: every agent that is no review agent, under the task its lines name
/// (its own, before any batch takes its later time; 451 T298).
pub(super) fn builder_minutes(w: &World, ix: &Ix, l: &mut Ledger) {
    let (lo, hi) = w.window;
    for (i, a) in w.agents.iter().enumerate() {
        let secs: f64 = a
            .spans
            .iter()
            .map(|s| (s.1.min(hi) - s.0.max(lo)).max(0.0))
            .sum();
        if review_cat(&a.kind).is_none() && secs > 0.0 {
            let e = l.builders.entry(ix.agent_own[i].clone()).or_default();
            e.0 += secs;
            e.1 += 1;
        }
    }
}

/// (key, category, target) -> seconds, as the own path and its stopped stretches are read back.
type Own = HashMap<(Key, String, String), f64>;

/// THE OWN PATH (451 T512, the GM 2026-11-27): each builder's own clock, descended as a main session's is (`Ix::book_seg`) into a
/// ledger of its own, its blocking seconds read back as (key, category, target) -> seconds; a review agent's span is no builder's.
/// Each segment is clipped to its builder's spans and booked to its builder's own task, as [`builder_minutes`] counts them, so the
/// path sums to its builder minutes; a line of a bundle's builder naming the bundle's other task is still its own task's path (the
/// overnight window's T428, 0.3 own-path minutes with no builder of its own). Unclipped, that window's 83 tasks read 1,947.3
/// own-path minutes against 1,728.3 builder minutes, T455 62.4 against 20.5. The pieces outside its spans - the builder STOPPED,
/// on its own work in flight or waiting to be resumed - are booked by the same descent into the second map, shown beside the path:
/// by the GM's blocking (request.md, 2026-11-25 (l)) a builder stopped on its own review is waiting on it (T512's plan review).
pub(super) fn own_path(w: &World, ix: &Ix, order: &[String]) -> (Own, Own) {
    let (lo, hi) = w.window;
    let (mut own, mut stopped) = (Ledger::default(), Ledger::default());
    let builders = order
        .iter()
        .filter_map(|who| Some((who, *ix.agent_of.get(who.as_str())?)))
        .filter(|(_, i)| review_cat(&w.agents[*i].kind).is_none());
    for (who, i) in builders {
        let key = Some(&ix.agent_own[i]);
        for s in &ix.segs[who] {
            let (x0, y0) = (s.t0.max(lo), s.t1.min(hi));
            let mut at = x0;
            for sp in &w.agents[i].spans {
                let (x, y) = (x0.max(sp.0), y0.min(sp.1));
                if y > x {
                    if x > at {
                        ix.book_seg(&mut stopped, s, (at, x), key, 0);
                    }
                    ix.book_seg(&mut own, s, (x, y), key, 0);
                    at = y;
                }
            }
            if y0 > at {
                ix.book_seg(&mut stopped, s, (at, y0), key, 0);
            }
        }
    }
    let read = |l: Ledger| l.cells.into_iter().map(|(k, c)| (k, c.block)).collect();
    (read(own), read(stopped))
}
