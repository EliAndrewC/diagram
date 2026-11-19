//! The sheet as the placer sees it (feature 449 T151, `labels/hand_sheet.py`'s `classify`, `soft_index`, `leader_blockers` and
//! `leader_to_ink`; feature 266 plan P4, feature 267's weights): each drawn shape an obstacle of the weight a reader meets it at, and what
//! a leader may not cross.
//!
//! Research: the sheet's ink as obstacles - NONE: the shapes filed by kind and paint, each weight's rule claimed where it is set

use std::collections::BTreeSet;

use super::super::geom::{bbox, dist, open_edges, ring_edges, Pt};
use super::super::obstacles::{Obstacle, ObstacleIndex, Way};
use super::super::placer::{nearest_ink, InkPart, Placement, Subject};
use super::super::standard::{WEIGHT_OBSTACLE, WEIGHT_WAY};
use super::seat::{area, box_within};
use super::{
    Shape, DISC_SAG_PX, GLYPH_MAX_PX, GROUND_KINDS, WALL_HALF_PX, WAY_KINDS, WEIGHT_DARK,
    WEIGHT_INNER, WEIGHT_TEXT,
};
use crate::py::{half_sum, hypot, max, min};

/// What one caption's classification is asked for: the captions being placed (not obstacles to themselves), the caption's own index (ink
/// painted after it hides it), its kind, its subject's outline, whether that subject is an area, whether its dark fill takes no name, and
/// every kind that carries a caption.
pub struct Seen<'a> {
    pub skip: &'a BTreeSet<usize>,
    pub after: Option<usize>,
    pub kind: &'a str,
    pub subject: Option<&'a [Pt]>,
    pub area: bool,
    pub dark_inside: bool,
    pub named: &'a BTreeSet<String>,
}

fn is_ground(kind: &str) -> bool {
    GROUND_KINDS.contains(&kind)
}

/// Is this the sheet's background: the one `-` rect covering the whole view?
///
/// Research: the background - CONVENTION: the one untagged-kind rect covering the whole view is free space to a caption (plan P4)
fn is_background(s: &Shape, view: (f64, f64, f64, f64)) -> bool {
    let (x0, y0, x1, y1) = bbox(&s.poly);
    s.kind == "-" && s.tag == "rect" && x0 <= view.0 && y0 <= view.1 && x1 >= view.2 && y1 >= view.3
}

/// Do two outlines share a box (within 1 unit) - a shape that IS the subject rather than a part inside it?
///
/// Research: the subject's own outline - CONVENTION: a shape whose box is the subject's within 1 unit is the subject itself, not ink inside it
pub(super) fn same_box(a: &[Pt], b: &[Pt]) -> bool {
    let (p, q) = (bbox(a), bbox(b));
    [(p.0, q.0), (p.1, q.1), (p.2, q.2), (p.3, q.3)]
        .iter()
        .all(|(x, y)| (x - y).abs() <= 1.0)
}

/// A segment as a band of half-width `half`.
#[must_use]
pub fn band(a: Pt, b: Pt, half: f64) -> Vec<Pt> {
    let (dx, dy) = (b.0 - a.0, b.1 - a.1);
    let h = hypot(dx, dy);
    let n = if h == 0.0 { 1.0 } else { h };
    let (nx, ny) = (-dy / n * half, dx / n * half);
    vec![
        (a.0 + nx, a.1 + ny),
        (b.0 + nx, b.1 + ny),
        (b.0 - nx, b.1 - ny),
        (a.0 - nx, a.1 - ny),
    ]
}

fn ring_bands(poly: &[Pt], half: f64) -> impl Iterator<Item = Vec<Pt>> + '_ {
    ring_edges(poly).map(move |(a, b)| band(a, b, half))
}

/// The sheet as the placer sees it (plan P4): the way kinds are ways, the ground kinds free space, the background free, everything else
/// an obstacle; ink as a reader meets it (feature 267) - another caption [`WEIGHT_TEXT`], dark ink [`WEIGHT_DARK`], anything painted after
/// the caption as much as a caption, ink inside what a caption names in full but nested ground and texture light ([`WEIGHT_INNER`]), a
/// ground's drawn border, an area's own outline; the building holding a named room waived. (The Python's `group` argument was read by
/// nothing and is not carried.)
///
/// Research:
///     what a hand sheet's caption may cover - CONVENTION: open ground and the background free, ways at a way's weight, nested ground and texture light, dark ink and anything painted over a caption at a caption's or dark ink's weight, every other drawn thing an obstacle (features 266 P4, 267, 283, 286)
#[must_use]
pub fn classify(shapes: &[Shape], view: (f64, f64, f64, f64), w: &Seen<'_>) -> ObstacleIndex {
    #[cfg(feature = "counters")]
    crate::work_counts::count("build@classify", 1);
    let mut obstacles: Vec<Obstacle> = Vec::new();
    let mut ways: Vec<Way> = Vec::new();
    let inner_ob = |poly: Vec<Pt>, weight: f64| Obstacle {
        inner: true,
        ..Obstacle::new(poly, weight)
    };
    for (i, s) in shapes.iter().enumerate() {
        if w.skip.contains(&i) || s.leader {
            continue;
        }
        let bg = is_background(s, view);
        let painted_after = w.after.is_some_and(|a| i > a) && s.filled;
        // ink INSIDE what the caption names is ink it must avoid (`Obstacle::inner`)
        let within = w.subject.is_some_and(|sub| {
            s.tag != "text" && box_within(&s.poly, sub) && !same_box(&s.poly, sub)
        });
        if within && !bg {
            // ground nested in the ground it names weighs light, and so does texture; ground painted AFTER the caption hides it
            let over = painted_after && !s.line;
            let light = (is_ground(&s.kind) && s.kind != w.kind && !over && !s.busy) || s.texture;
            // ink inside it that carries a name of its own weighs as that name (feature 286)
            let own_name = w.named.contains(&s.kind) && s.kind != w.kind && !s.texture;
            let weight = if own_name || over {
                WEIGHT_TEXT
            } else if light {
                WEIGHT_INNER
            } else {
                WEIGHT_OBSTACLE
            };
            if s.line {
                obstacles.extend(
                    open_edges(&s.poly)
                        .map(|(a, b)| inner_ob(band(a, b, max(s.half, 0.5)), weight)),
                );
            } else {
                obstacles.push(inner_ob(s.poly.clone(), weight));
            }
            continue;
        }
        if w.area
            && s.tag != "text"
            && !s.line
            && !painted_after
            && w.subject.is_some_and(|sub| box_within(sub, &s.poly))
        {
            // the area itself, or the building that holds the room an `area` caption names: the name is inside it by necessity - but
            // not on its drawn outline (feature 267 round 4)
            if s.edge != 0.0 {
                obstacles.extend(ring_bands(&s.poly, s.edge).map(|b| inner_ob(b, WEIGHT_OBSTACLE)));
            }
            if w.dark_inside
                && s.dark
                && s.filled
                && w.subject.is_some_and(|sub| same_box(&s.poly, sub))
            {
                // its own dark fill takes no name in the sheet's dark ink: the caption goes beside it (feature 286, plan D2)
                obstacles.push(inner_ob(s.poly.clone(), WEIGHT_DARK));
            }
            continue;
        }
        if s.tag == "text" || (painted_after && !s.line && !bg) {
            // another caption, or ink painted OVER the caption, which hides it as surely (feature 267)
            obstacles.push(Obstacle::new(s.poly.clone(), WEIGHT_TEXT));
        } else if s.busy && s.kind != w.kind {
            obstacles.push(Obstacle::new(s.poly.clone(), WEIGHT_OBSTACLE)); // ground in rows no other name can be read on
        } else if is_ground(&s.kind) || bg {
            // a ground's drawn border is ink even where its floor is free space; the border of the ground a caption names is its own
            if s.edge != 0.0 && !bg && !w.subject.is_some_and(|sub| same_box(&s.poly, sub)) {
                obstacles
                    .extend(ring_bands(&s.poly, s.edge).map(|b| Obstacle::new(b, WEIGHT_OBSTACLE)));
            }
            // a ground's name set on another ground that carries a name of its own reads as naming it (feature 286)
            if is_ground(w.kind) && w.named.contains(&s.kind) && s.kind != w.kind && !bg {
                obstacles.push(Obstacle::new(s.poly.clone(), WEIGHT_TEXT));
            }
        } else if WAY_KINDS.contains(&s.kind.as_str()) {
            if s.line {
                ways.push(Way {
                    pts: s.poly.clone(),
                    half_width: max(s.half, 0.5),
                    soft: false,
                });
            } else {
                obstacles.push(Obstacle::new(s.poly.clone(), WEIGHT_WAY));
            }
        } else if s.line {
            let weight = if s.dark { WEIGHT_DARK } else { WEIGHT_OBSTACLE };
            obstacles.extend(
                open_edges(&s.poly)
                    .map(|(a, b)| Obstacle::new(band(a, b, max(s.half, 0.5)), weight)),
            );
        } else if s.filled && w.named.contains(&s.kind) && s.kind != w.kind && !s.texture {
            // a thing that carries a name of its own: a caption set on it reads as naming it (feature 286)
            obstacles.push(Obstacle::new(s.poly.clone(), WEIGHT_TEXT));
        } else {
            obstacles.push(Obstacle::new(
                s.poly.clone(),
                if s.dark { WEIGHT_DARK } else { WEIGHT_OBSTACLE },
            ));
        }
    }
    soft_index(obstacles, ways)
}

/// A hand sheet's index with what a caption may be set on when nothing is free marked `soft` (feature 287, D10): light ink, nested ground
/// and the ways. What stays hard - another caption or ink painted over one, dark ink - the placer never draws while another seat exists.
///
/// Research: soft ink - CONVENTION: ink lighter than dark ink and every way may take a caption when no seat is free; a caption and dark ink never
#[must_use]
pub fn soft_index(obstacles: Vec<Obstacle>, ways: Vec<Way>) -> ObstacleIndex {
    let obstacles = obstacles
        .into_iter()
        .map(|o| Obstacle {
            soft: o.weight < WEIGHT_DARK,
            ..o
        })
        .collect();
    let ways = ways.into_iter().map(|w| Way { soft: true, ..w }).collect();
    ObstacleIndex::new(obstacles, ways)
}

/// What a caption's leader may not pass over or end against (feature 283): every other caption - the sheet's own drawn texts and those
/// already placed - every small glyph that is not part of what it names, every wall but one it names (feature 286), and every building it
/// would cross but the one it names or one holding it. `own_parts` are the shapes the caption names, by their index.
///
/// Research: what a leader may cross - CONVENTION: a leader crosses no caption, no wall but its own, no building but its own, and ends on no small glyph (features 283, 286)
#[must_use]
pub fn leader_blockers(
    shapes: &[Shape],
    skip: &BTreeSet<usize>,
    placed: &[&Placement],
    sub: &Subject,
    own_parts: &[usize],
) -> ObstacleIndex {
    #[cfg(feature = "counters")]
    crate::work_counts::count("build@leader_blockers", 1);
    let own = &sub.poly;
    let mine = |i: usize| own_parts.contains(&i);
    let mut out: Vec<Obstacle> = shapes
        .iter()
        .enumerate()
        .filter(|(i, s)| s.tag == "text" && !skip.contains(i))
        .map(|(_, s)| Obstacle::new(s.poly.clone(), WEIGHT_TEXT))
        .collect();
    out.extend(
        placed
            .iter()
            .map(|p| Obstacle::new(p.block.clone(), WEIGHT_TEXT)),
    );
    out.extend(
        shapes
            .iter()
            .filter(|s| {
                let a = area(&s.poly);
                s.tag != "text"
                    && s.filled
                    && !s.line
                    && !s.leader
                    && s.kind != "door"
                    && 0.0 < a
                    && a <= GLYPH_MAX_PX
                    && !box_within(&s.poly, own)
            })
            .map(|s| Obstacle::new(s.poly.clone(), WEIGHT_OBSTACLE)),
    );
    for (i, s) in shapes.iter().enumerate() {
        if s.line && s.dark && s.half >= WALL_HALF_PX && !s.leader && !mine(i) {
            out.extend(
                open_edges(&s.poly).map(|(a, b)| Obstacle::new(band(a, b, s.half), WEIGHT_TEXT)),
            );
        }
    }
    // and every building it would cross to reach its subject - not the one it names, nor one holding what it names (Ochiba's inner
    // garden was led across the kitchen)
    out.extend(
        shapes
            .iter()
            .enumerate()
            .filter(|(i, s)| {
                s.tag != "text"
                    && s.filled
                    && !s.line
                    && !s.leader
                    && !is_ground(&s.kind)
                    && s.kind != "-"
                    && area(&s.poly) > GLYPH_MAX_PX
                    && !mine(*i)
                    && !box_within(&s.poly, own)
                    && !box_within(own, &s.poly)
            })
            .map(|(_, s)| Obstacle::new(s.poly.clone(), WEIGHT_OBSTACLE)),
    );
    soft_index(out, Vec::new())
}

/// A leader ends on the drawn thing it names, not on the box around its parts (feature 283 - the tax barge's and the old pines' leaders
/// ended 5-6 ft short). A disc's ink is its drawn curve ([`drawn_ink`]), not the box the reader keeps as its outline (feature 449 T192:
/// three pool leaders ended 1.75 to 4.45 px off the curve); a stroke's is its band as the sheet draws it, its `stroke-linecap` read, and a
/// closed part's its outline drawn out by its own stroke (feature 449 T193: a leader past a butt end stopped up to the half-width short of
/// the ink, and one to a stroked building inside its stroke), their corners joined as the sheet joins them (T194). The tip is the
/// placer's own ([`nearest_ink`] from the leader's start; T194: this measured each part again with its own `ink_nearest`, the Python
/// with shapely's union, which drew each round end and corner as chords), so this leaves every leader a hand sheet's subject scores as it
/// was scored (`Subject::ink`, feature 449 T192). A leader whose start already lies on the ink it names ties nothing back - the caption
/// touches its subject - so it is dropped (feature 449 T184; the Python divided by the zero distance there); one to parts that draw no
/// ink is left as it was scored.
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 1.5 (leader already touching ink, left alone)
///     leader end trim - CONVENTION: a leader stops short of the ink it ends on by a quarter of its length, at most 1 px, so its end does not touch the ink; a drawn size on the sheet, not in the world
#[must_use]
pub fn leader_to_ink(p: Placement, parts: &[&Shape]) -> Placement {
    let Some((start, end)) = p.leader else {
        return p;
    };
    let ink: Vec<InkPart> = parts
        .iter()
        .filter(|s| s.poly.len() >= if s.line { 2 } else { 3 })
        .map(|s| drawn_ink(s))
        .collect();
    let Some(at_end) = nearest_ink(&[end], &ink) else {
        return p;
    };
    if dist(at_end.0, at_end.1) < 1.5 {
        return p;
    }
    let (a, tip) = nearest_ink(&[start], &ink).unwrap_or(at_end);
    let d = dist(a, tip);
    if d == 0.0 {
        return Placement { leader: None, ..p };
    }
    let trim = min(1.0, d / 4.0);
    let (ux, uy) = ((tip.0 - a.0) / d, (tip.1 - a.1) / d);
    Placement {
        leader: Some((start, (tip.0 - ux * trim, tip.1 - uy * trim))),
        ..p
    }
}

/// A drawn part as a leader ends on it (feature 449 T192, T193, the Python's `drawn_ink`): a stroke's polyline at its half-width, at least
/// half a pixel, and its cap (the band [`leader_to_ink`] measures); a disc's drawn curve - the image of the unit circle in the drawn box the
/// reader keeps as its outline, its center plus cos t of one half-side plus sin t of the other, so a turned or unequally scaled disc is
/// drawn as it is - sampled in [`disc_samples`] points; any other shape its outline; a closed part with the half-width of the stroke drawn
/// on it (`edge`).
///
/// Research: its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 0.5 (a stroke's least half-width, the band `leader_to_ink` buffers)
#[must_use]
#[expect(
    clippy::many_single_char_names,
    reason = "the Python's names, kept so each line reads against its original (c, u, v, n, t)"
)]
pub fn drawn_ink(s: &Shape) -> InkPart {
    if s.line {
        return InkPart {
            pts: s.poly.clone(),
            line: true,
            half: max(s.half, 0.5),
            cap: s.cap,
            join: s.join,
            miter: s.miter,
            closed: s.closed,
            dash: s.dash.clone(),
            offset: s.offset,
        };
    }
    let outline = |pts: Vec<Pt>| InkPart {
        pts,
        half: s.edge,
        join: s.join,
        miter: s.miter,
        ..InkPart::default()
    };
    let [p0, p1, p2, p3] = s.poly[..] else {
        return outline(s.poly.clone());
    };
    if s.tag != "circle" && s.tag != "ellipse" {
        return outline(s.poly.clone());
    }
    let c = (half_sum(p0.0, p2.0), half_sum(p0.1, p2.1));
    let (u, v) = (
        ((p1.0 - p0.0) / 2.0, (p1.1 - p0.1) / 2.0),
        ((p3.0 - p0.0) / 2.0, (p3.1 - p0.1) / 2.0),
    );
    let n = disc_samples(hypot(hypot(u.0, u.1), hypot(v.0, v.1)));
    outline(
        (0..n)
            .map(|k| {
                #[expect(clippy::cast_precision_loss, reason = "a sample count, far under 2^52")]
                let t = 2.0 * std::f64::consts::PI * k as f64 / n as f64;
                (
                    c.0 + t.cos() * u.0 + t.sin() * v.0,
                    c.1 + t.cos() * u.1 + t.sin() * v.1,
                )
            })
            .collect(),
    )
}

/// The least number of points sampling a curve whose half-axes `r` bounds with no chord more than [`DISC_SAG_PX`] inside it -
/// R(1 - cos(pi / n)) - at least 8 (a disc smaller than the sag).
///
/// Research: its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 8 (the least samples of a disc's curve)
#[must_use]
pub fn disc_samples(r: f64) -> usize {
    if r <= DISC_SAG_PX {
        return 8;
    }
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a positive whole count, under a few thousand for any drawn disc"
    )]
    let n = (std::f64::consts::PI / (1.0 - DISC_SAG_PX / r).acos()).ceil() as usize;
    n.max(8)
}
