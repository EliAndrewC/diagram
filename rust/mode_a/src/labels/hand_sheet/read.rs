//! Reading a hand-drawn sheet (feature 449 T151, `labels/hand_sheet.py`'s `read_sheet` and what it reads with): every drawn element as a
//! [`Shape`] in sheet coordinates - its transforms multiplied out, its stroke and fill inherited as SVG inherits them - read off the tree
//! `ElementTree` built ([`crate::etree`]), each element numbered in `root.iter()` order so a caption's text is found in the source by
//! [`crate::hand_sheet::start_tags`].
//!
//! Research: the sheet's reading - NONE: SVG geometry and paint read as drawn, deciding nothing about where a caption stands

#![expect(
    clippy::many_single_char_names,
    reason = "an affine matrix's six entries, a to f, as SVG names them"
)]

use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::py_text::strip;

use super::super::geom::{bbox, rect, Pt};
use super::super::placer::{Cap, Join};
use super::super::standard::{block_half, CENTER_ABOVE_BASELINE_EM, PITCH_EM};
use super::{char_w_of, luma, Attrs, Shape, BUSY_FILLS, DARK, DISC_SAG_PX};
use crate::etree::Element;
use crate::py::{hypot, max};

/// The SVG namespace, `ElementTree`'s `{...}` key of a tag.
pub const SVG_NS: &str = "http://www.w3.org/2000/svg";

/// An SVG transform as one affine matrix `(a, b, c, d, e, f)`.
pub type Affine = (f64, f64, f64, f64, f64, f64);

/// A sheet's view `(x0, y0, x1, y1)`.
pub type View = (f64, f64, f64, f64);

/// The identity matrix.
///
/// Research: identity transform - NONE: the identity affine matrix.
pub const IDENTITY: Affine = (1.0, 0.0, 0.0, 1.0, 0.0, 0.0);

/// `m` then `n`.
#[must_use]
pub fn mul(m: Affine, n: Affine) -> Affine {
    let (a, b, c, d, e, f) = m;
    let (a2, b2, c2, d2, e2, f2) = n;
    (
        a * a2 + c * b2,
        b * a2 + d * b2,
        a * c2 + c * d2,
        b * c2 + d * d2,
        a * e2 + c * f2 + e,
        b * e2 + d * f2 + f,
    )
}

static TRANSFORM: LazyLock<Regex> = LazyLock::new(|| py(r"(\w+)\s*\(([^)]*)\)"));
static SEPARATORS: LazyLock<Regex> = LazyLock::new(|| py(r"[\s,]+"));
static NUMBER: LazyLock<Regex> = LazyLock::new(|| py(r"-?\d*\.?\d+"));
static PATH_STEP: LazyLock<Regex> =
    LazyLock::new(|| py(r"([MmLlHhVvCcSsQqTtAaZz])([^MmLlHhVvCcSsQqTtAaZz]*)"));
static PATH_NUMBER: LazyLock<Regex> = LazyLock::new(|| py(r"-?\d*\.?\d+(?:e-?\d+)?"));

/// `re.split(pattern, text)`: the pieces between the matches, an empty piece kept at either end.
fn split<'t>(re: &Regex, text: &'t str) -> Vec<&'t str> {
    let mut out = Vec::new();
    let mut at = 0;
    for m in re.find_iter(text).map_while(Result::ok) {
        out.push(&text[at..m.start()]);
        at = m.end();
    }
    out.push(&text[at..]);
    out
}

fn numbers(re: &Regex, text: &str) -> Result<Vec<f64>, Error> {
    re.find_iter(text)
        .map_while(Result::ok)
        .map(|m| crate::py::float(m.as_str()))
        .collect()
}

fn index_error() -> Error {
    Error::new("IndexError", "list index out of range")
}

/// An SVG `transform` list as one affine matrix: translate, rotate (about a point too), scale and matrix; any other is passed over.
///
/// # Errors
/// A value that is no number (Python's `ValueError`), or a transform short of the values it needs (its `IndexError`).
pub fn parse_transform(t: Option<&str>) -> Result<Affine, Error> {
    let mut m = IDENTITY;
    let t = t.unwrap_or_default();
    for c in TRANSFORM.captures_iter(t).map_while(Result::ok) {
        let args = c.get(2).map_or("", |a| a.as_str());
        let v: Vec<f64> = split(&SEPARATORS, strip(args))
            .into_iter()
            .filter(|x| !x.is_empty())
            .map(crate::py::float)
            .collect::<Result<_, _>>()?;
        let at = |i: usize| v.get(i).copied().ok_or_else(index_error);
        match &c[1] {
            "translate" => {
                let dy = v.get(1).copied().unwrap_or(0.0);
                m = mul(m, (1.0, 0.0, 0.0, 1.0, at(0)?, dy));
            }
            "scale" => {
                let x = at(0)?;
                m = mul(m, (x, 0.0, 0.0, v.get(1).copied().unwrap_or(x), 0.0, 0.0));
            }
            "rotate" => {
                let a = at(0)?.to_radians();
                let mut r: Affine = (a.cos(), a.sin(), -a.sin(), a.cos(), 0.0, 0.0);
                if v.len() == 3 {
                    r = mul(
                        mul((1.0, 0.0, 0.0, 1.0, v[1], v[2]), r),
                        (1.0, 0.0, 0.0, 1.0, -v[1], -v[2]),
                    );
                }
                m = mul(m, r);
            }
            "matrix" => m = mul(m, (at(0)?, at(1)?, at(2)?, at(3)?, at(4)?, at(5)?)),
            _ => {}
        }
    }
    Ok(m)
}

/// The matrix that undoes `m` (an SVG transform is always invertible when anything is drawn through it).
#[must_use]
pub fn inverse(m: Affine) -> Affine {
    let (a, b, c, d, e, f) = m;
    let det = a * d - b * c;
    (
        d / det,
        -b / det,
        -c / det,
        a / det,
        (c * f - d * e) / det,
        (b * e - a * f) / det,
    )
}

/// `p` through `m`.
#[must_use]
pub fn apply(m: Affine, p: Pt) -> Pt {
    (m.0 * p.0 + m.2 * p.1 + m.4, m.1 * p.0 + m.3 * p.1 + m.5)
}

/// The angle `m` turns by, in degrees.
#[must_use]
pub fn angle(m: Affine) -> f64 {
    m.1.atan2(m.0).to_degrees()
}

/// `float(el.get(name))`, or `default` where it is absent or no number.
#[must_use]
pub fn attr_f(attrs: &Attrs, name: &str, default: f64) -> f64 {
    attrs
        .get(name)
        .map_or(default, |v| crate::py::float(v).unwrap_or(default))
}

/// A path's subpaths as SVG draws them (the Python's `_path_points`), each its points and whether a `Z` closed it: absolute and relative
/// move, line, horizontal and vertical steps, and every curve - cubic and quadratic Beziers, their smooth forms reflecting the control
/// point before, and elliptical arcs - flattened finely enough that no chord stands more than `tol` inside it. A move starts a new
/// subpath, and a step after a `Z` starts one at the closed subpath's start (feature 449 T194: a curve was kept by its end points alone, so
/// Hoshigaoka's sacred-tree rope, a ring drawn in two arcs, was read as a 10 px line doubled back, and a second move was joined to the
/// first by a segment nobody drew).
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 6 (SVG C-command argument count); 7 (SVG A-command argument count)
///
/// # Errors
/// None the patterns let through: a number they match is always one.
pub fn path_points(d: &str, tol: f64) -> Result<Vec<(Vec<Pt>, bool)>, Error> {
    let mut subs = Vec::new();
    let mut pts: Vec<Pt> = Vec::new();
    let mut closed = false;
    let (mut x, mut y, mut sx, mut sy) = (0.0, 0.0, 0.0, 0.0);
    // the last cubic's second control point, or the last quadratic's control point, which S and T reflect
    let mut ctrl: Option<Pt> = None;
    let mut last = ' ';
    for c in PATH_STEP.captures_iter(d).map_while(Result::ok) {
        let cmd = c[1].chars().next().unwrap_or('Z');
        let up = cmd.to_ascii_uppercase();
        if up == 'Z' {
            closed = closed || !pts.is_empty();
            (x, y, last) = (sx, sy, 'Z');
            continue;
        }
        let v = numbers(&PATH_NUMBER, &c[2])?;
        let step = match up {
            'M' | 'L' | 'T' => 2,
            'H' | 'V' => 1,
            'C' => 6,
            'S' | 'Q' => 4,
            _ => 7,
        };
        let rel = cmd.is_ascii_lowercase();
        for (i, ch) in v.chunks_exact(step).enumerate() {
            let (ox, oy) = if rel { (x, y) } else { (0.0, 0.0) };
            let moved = up == 'M' && i == 0;
            if moved || closed {
                // a move, or a step after a `Z`, starts a new subpath (at the closed one's start)
                if !pts.is_empty() {
                    subs.push((std::mem::take(&mut pts), closed));
                }
                closed = false;
                if moved {
                    (x, y) = (ox + ch[0], oy + ch[1]);
                    (sx, sy, last) = (x, y, 'M');
                    pts = vec![(x, y)];
                    continue;
                }
                pts = vec![(x, y)];
            }
            if pts.is_empty() {
                pts.push((x, y));
            }
            let p0 = (x, y);
            let reflect = |of: &[char]| match ctrl {
                Some(q) if of.contains(&last) => (2.0 * x - q.0, 2.0 * y - q.1),
                _ => p0,
            };
            match up {
                'H' => {
                    x = ox + ch[0];
                    pts.push((x, y));
                }
                'V' => {
                    y = oy + ch[0];
                    pts.push((x, y));
                }
                'M' | 'L' => {
                    (x, y) = (ox + ch[0], oy + ch[1]);
                    pts.push((x, y));
                }
                'C' | 'S' => {
                    let c1 = if up == 'C' {
                        (ox + ch[0], oy + ch[1])
                    } else {
                        reflect(&['C', 'S'])
                    };
                    let (c2, e) = (
                        (ox + ch[step - 4], oy + ch[step - 3]),
                        (ox + ch[step - 2], oy + ch[step - 1]),
                    );
                    pts.extend(bezier(&[p0, c1, c2, e], tol));
                    ((x, y), ctrl) = (e, Some(c2));
                }
                'Q' | 'T' => {
                    let q = if up == 'Q' {
                        (ox + ch[0], oy + ch[1])
                    } else {
                        reflect(&['Q', 'T'])
                    };
                    let e = (ox + ch[step - 2], oy + ch[step - 1]);
                    pts.extend(bezier(&[p0, q, e], tol));
                    ((x, y), ctrl) = (e, Some(q));
                }
                _ => {
                    let e = (ox + ch[5], oy + ch[6]);
                    let flags = (ch[3] != 0.0, ch[4] != 0.0);
                    pts.extend(arc(p0, (ch[0], ch[1], ch[2]), flags, e, tol));
                    (x, y) = e;
                }
            }
            last = up;
        }
    }
    if !pts.is_empty() {
        subs.push((pts, closed));
    }
    Ok(subs)
}

/// A cubic or quadratic Bezier's points after its start (the Python's `_bezier`), in the fewest equal steps of its parameter whose chords
/// stand within `tol` of the curve: Wang's bound, n(n - 1) / 8 times the largest second difference of the control points, over the
/// square of the steps.
fn bezier(cp: &[Pt], tol: f64) -> Vec<Pt> {
    let deg = cp.len() - 1;
    let dd = (0..deg - 1)
        .map(|k| {
            hypot(
                cp[k].0 - 2.0 * cp[k + 1].0 + cp[k + 2].0,
                cp[k].1 - 2.0 * cp[k + 1].1 + cp[k + 2].1,
            )
        })
        .fold(f64::NEG_INFINITY, max);
    #[expect(clippy::cast_precision_loss, reason = "a curve's degree, 2 or 3")]
    let n = steps((deg * (deg - 1)) as f64 / 8.0 * dd / tol);
    let mut out: Vec<Pt> = (1..=n)
        .map(|k| {
            #[expect(clippy::cast_precision_loss, reason = "a step count, far under 2^52")]
            let t = k as f64 / n as f64;
            let w: Vec<f64> = (0..=deg)
                .map(|j| binom(deg, j) * t.powi(pow(j)) * (1.0 - t).powi(pow(deg - j)))
                .collect();
            (
                w.iter().zip(cp).map(|(wj, p)| wj * p.0).sum(),
                w.iter().zip(cp).map(|(wj, p)| wj * p.1).sum(),
            )
        })
        .collect();
    if let Some(end) = out.last_mut() {
        *end = cp[deg];
    }
    out
}

/// `max(1, ceil(sqrt(x)))`: the steps Wang's bound asks for.
fn steps(x: f64) -> usize {
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a positive whole count of a drawn curve's steps"
    )]
    let n = x.sqrt().ceil() as usize;
    n.max(1)
}

/// `math.comb(n, k)` for a Bezier's degree, 2 or 3.
fn binom(n: usize, k: usize) -> f64 {
    match (n, k) {
        (3, 1 | 2) => 3.0,
        (2, 1) => 2.0,
        _ => 1.0,
    }
}

/// A power's exponent as `powi` takes it (a Bezier's degree is at most 3).
fn pow(j: usize) -> i32 {
    i32::try_from(j).unwrap_or(i32::MAX)
}

/// An elliptical arc's points after its start, as SVG draws it (the Python's `_arc`, SVG 1.1 appendix F.6): none where it ends where it
/// starts, a straight step where a radius is 0, its radii scaled up where they cannot reach the end, and its center found from its flags
/// (`large`, `sweep`); flattened in equal steps of its angle whose chords stand within `tol` of the curve, R(1 - cos(half a step)), R its
/// larger radius. `radii` is `(rx, ry, rotation in degrees)`.
fn arc(p0: Pt, radii: (f64, f64, f64), (large, sweep): (bool, bool), e: Pt, tol: f64) -> Vec<Pt> {
    if p0 == e {
        return Vec::new();
    }
    let (mut rx, mut ry) = (radii.0.abs(), radii.1.abs());
    if rx == 0.0 || ry == 0.0 {
        return vec![e];
    }
    let phi = radii.2.to_radians();
    let (cp, sp) = (phi.cos(), phi.sin());
    let (dx, dy) = ((p0.0 - e.0) / 2.0, (p0.1 - e.1) / 2.0);
    let (x1, y1) = (cp * dx + sp * dy, -sp * dx + cp * dy);
    let lam = x1 * x1 / (rx * rx) + y1 * y1 / (ry * ry);
    if lam > 1.0 {
        (rx, ry) = (rx * lam.sqrt(), ry * lam.sqrt());
    }
    let num = rx * rx * ry * ry - rx * rx * y1 * y1 - ry * ry * x1 * x1;
    let mut co = max(0.0, num / (rx * rx * y1 * y1 + ry * ry * x1 * x1)).sqrt();
    if large == sweep {
        co = -co;
    }
    // the center in the arc's own frame, then on the sheet
    let own = (co * rx * y1 / ry, -co * ry * x1 / rx);
    let (cx, cy) = (
        cp * own.0 - sp * own.1 + f64::midpoint(p0.0, e.0),
        sp * own.0 + cp * own.1 + f64::midpoint(p0.1, e.1),
    );
    let (ux, uy, vx, vy) = (
        (x1 - own.0) / rx,
        (y1 - own.1) / ry,
        (-x1 - own.0) / rx,
        (-y1 - own.1) / ry,
    );
    let t1 = uy.atan2(ux);
    let mut dt = (ux * vy - uy * vx).atan2(ux * vx + uy * vy);
    if sweep && dt < 0.0 {
        dt += 2.0 * std::f64::consts::PI;
    } else if !sweep && dt > 0.0 {
        dt -= 2.0 * std::f64::consts::PI;
    }
    let r = max(rx, ry);
    let step = 2.0 * max(-1.0, 1.0 - tol / r).acos();
    #[expect(
        clippy::cast_possible_truncation,
        clippy::cast_sign_loss,
        reason = "a positive whole count of an arc's steps"
    )]
    let n = ((dt.abs() / step).ceil() as usize).max(1);
    let mut out: Vec<Pt> = (1..=n)
        .map(|k| {
            #[expect(clippy::cast_precision_loss, reason = "a step count, far under 2^52")]
            let t = t1 + dt * k as f64 / n as f64;
            (
                cx + rx * t.cos() * cp - ry * t.sin() * sp,
                cy + rx * t.cos() * sp + ry * t.sin() * cp,
            )
        })
        .collect();
    if let Some(end) = out.last_mut() {
        *end = e;
    }
    out
}

/// How far `m` stretches a unit length at most (the Python's `_stretch`) - its linear part's largest singular value.
#[must_use]
pub fn stretch(m: Affine) -> f64 {
    let (a, b, c, d) = (m.0, m.1, m.2, m.3);
    let s = a * a + b * b + c * c + d * d;
    let det = a * d - b * c;
    f64::midpoint(s, max(0.0, s * s - 4.0 * det * det).sqrt()).sqrt()
}

/// A `stroke-dasharray` as SVG reads it (the Python's `_dasharray`): `none`, or lengths of no sum, solid (empty); an odd count repeated to
/// an even one; a value SVG does not read - a negative or no number, a percentage - ignored, so the inherited pattern `up` stands.
fn dasharray(v: Option<&str>, up: &[f64]) -> Vec<f64> {
    let Some(v) = v else {
        return up.to_vec();
    };
    if strip(v) == "none" {
        return Vec::new();
    }
    let vals: Result<Vec<f64>, _> = split(&SEPARATORS, strip(v))
        .into_iter()
        .filter(|x| !x.is_empty())
        .map(crate::py::float)
        .collect();
    let Ok(vals) = vals else {
        return up.to_vec();
    };
    if vals.is_empty() || vals.iter().any(|&x| x < 0.0) {
        return up.to_vec();
    }
    if vals.iter().sum::<f64>() == 0.0 {
        return Vec::new();
    }
    if vals.len() % 2 == 1 {
        return [vals.as_slice(), vals.as_slice()].concat();
    }
    vals
}

/// What a walk inherits from the elements around: the matrix, the kind and its group, the stroke's width and whether one is drawn, the
/// (stroke, fill), the texture mark, the `data-id`s and the stroke's cap.
#[derive(Clone)]
struct Inherited {
    m: Affine,
    kind: String,
    stroke_w: f64,
    stroked: bool,
    group: usize,
    ink: (String, String),
    texture: bool,
    ids: BTreeSet<String>,
    cap: Cap,
    join: Join,
    miter: f64,
    dash: Vec<f64>,
    offset: f64,
}

/// The tag as the Python compared it: `el.tag.replace("{SVG}", "")` - an SVG or unprefixed element by its name, any other namespace's
/// kept whole (and so no shape).
fn tag_of(el: &Element) -> String {
    if el.ns.is_empty() || el.ns == SVG_NS {
        el.tag.clone()
    } else {
        format!("{{{}}}{}", el.ns, el.tag)
    }
}

/// Every drawn element of a sheet as a Shape, and the sheet's view `(x0, y0, x1, y1)`.
///
/// # Errors
/// The sheet is no XML `ElementTree` reads, its view box or a transform no numbers, or a coordinate that is no finite number, which the
/// placer's grid could not file (the Python raised on a NaN there and spun on an infinity).
pub fn read_sheet(src: &str) -> Result<(Vec<Shape>, View), Error> {
    let root = crate::etree::fromstring(src)?;
    let vb_text = root
        .get("viewBox")
        .filter(|v| !v.is_empty())
        .unwrap_or("0 0 0 0");
    let vb: Vec<f64> = split(&SEPARATORS, strip(vb_text))
        .into_iter()
        .map(crate::py::float)
        .collect::<Result<_, _>>()?;
    if vb.len() < 4 {
        return Err(index_error());
    }
    let view = (vb[0], vb[1], vb[0] + vb[2], vb[1] + vb[3]);
    let mut shapes = Vec::new();
    let top = Inherited {
        m: IDENTITY,
        kind: String::new(),
        stroke_w: 1.0,
        stroked: false,
        group: 0,
        ink: (String::new(), String::new()),
        texture: false,
        ids: BTreeSet::new(),
        cap: Cap::Butt,
        join: Join::Miter,
        miter: 4.0,
        dash: Vec::new(),
        offset: 0.0,
    };
    let mut at = 1; // the root is element 0 of `root.iter()`
    for c in &root.children {
        walk(c, &top, &mut at, &mut shapes)?;
    }
    if shapes
        .iter()
        .flat_map(|s| &s.poly)
        .any(|p| !p.0.is_finite() || !p.1.is_finite())
    {
        return Err(Error::new(
            "ValueError",
            "a drawn coordinate is no finite number",
        ));
    }
    Ok((shapes, view))
}

/// What `el` passes on to what it holds (and draws with itself): its matrix, kind and group, stroke and fill, texture and `data-id`s.
fn inherit(el: &Element, up: &Inherited, here: usize) -> Result<Inherited, Error> {
    let attrs = &el.attrib;
    let mut h = up.clone();
    if let Some(id) = el.get("data-id").filter(|i| !i.is_empty()) {
        h.ids.insert(id.to_owned());
    }
    h.m = mul(up.m, parse_transform(el.get("transform"))?);
    if let Some(kind) = el.get("data-kind") {
        // the tagged element a caption and its subject share, numbered by its place in the document
        (h.kind, h.group) = (kind.to_owned(), here);
    }
    h.stroke_w = attr_f(attrs, "stroke-width", up.stroke_w);
    if let Some(stroke) = el.get("stroke") {
        h.stroked = stroke != "none";
    }
    h.ink = (
        el.get("stroke")
            .map_or_else(|| up.ink.0.clone(), str::to_owned),
        el.get("fill")
            .map_or_else(|| up.ink.1.clone(), str::to_owned),
    );
    h.texture = up.texture || el.get("data-texture") == Some("1");
    // a stroke's cap, join and miter limit, inherited as SVG inherits them, a value SVG does not know ignored, as SVG ignores it, so the one
    // inherited stands (feature 449 T193, T194)
    if let Some(cap) = el.get("stroke-linecap").and_then(Cap::of) {
        h.cap = cap;
    }
    if let Some(join) = el.get("stroke-linejoin").and_then(Join::of) {
        h.join = join;
    }
    let limit = attr_f(attrs, "stroke-miterlimit", 0.0);
    if limit >= 1.0 {
        h.miter = limit;
    }
    h.dash = dasharray(el.get("stroke-dasharray"), &up.dash);
    h.offset = attr_f(attrs, "stroke-dashoffset", up.offset);
    Ok(h)
}

fn walk(
    el: &Element,
    up: &Inherited,
    at: &mut usize,
    shapes: &mut Vec<Shape>,
) -> Result<(), Error> {
    let here = *at;
    *at += 1;
    let attrs = &el.attrib;
    let h = inherit(el, up, here)?;
    let tag = tag_of(el);
    let f = |name: &str| attr_f(attrs, name, 0.0);
    let (subs, line): (Vec<(Vec<Pt>, bool)>, bool) = match tag.as_str() {
        "rect" => {
            let (x, y, w, hh) = (f("x"), f("y"), f("width"), f("height"));
            (
                vec![(
                    vec![(x, y), (x + w, y), (x + w, y + hh), (x, y + hh)],
                    false,
                )],
                false,
            )
        }
        "circle" | "ellipse" => {
            let (cx, cy) = (f("cx"), f("cy"));
            let (rx, ry) = if tag == "circle" {
                (f("r"), f("r"))
            } else {
                (f("rx"), f("ry"))
            };
            (
                vec![(
                    vec![
                        (cx - rx, cy - ry),
                        (cx + rx, cy - ry),
                        (cx + rx, cy + ry),
                        (cx - rx, cy + ry),
                    ],
                    false,
                )],
                false,
            )
        }
        "polygon" | "polyline" => {
            let v = numbers(&NUMBER, el.get("points").unwrap_or_default())?;
            let pts = v.chunks_exact(2).map(|p| (p[0], p[1])).collect();
            // a polyline is a stroke unless a fill is set on it or inherited, as SVG fills it (feature 449 T194)
            (
                vec![(pts, false)],
                tag == "polyline" && (h.ink.1.is_empty() || h.ink.1 == "none"),
            )
        }
        "line" => (
            vec![(vec![(f("x1"), f("y1")), (f("x2"), f("y2"))], false)],
            true,
        ),
        // each subpath its own shape, as SVG strokes each alone, flattened within the drawn sag on the sheet; a stroke where its fill, its
        // own or inherited, is none (feature 449 T194: a group's `fill="none"` was not read, and its strokes read as boxes)
        "path" => (
            path_points(
                el.get("d").unwrap_or_default(),
                DISC_SAG_PX / max(stretch(h.m), 1e-9),
            )?,
            h.stroked && h.ink.1 == "none",
        ),
        "text" => {
            shapes.push(text_shape(el, &h, up.m, here));
            *at += el.elements().len() - 1; // its `<tspan>`s are elements of `root.iter()` too
            return Ok(());
        }
        _ => (Vec::new(), false),
    };
    push_shapes(el, &h, &tag, here, (subs, line), shapes);
    for c in &el.children {
        walk(c, &h, at, shapes)?;
    }
    Ok(())
}

/// Each subpath of a drawn element, read as `line` or not, as a Shape: a stroke its polyline (closed back to its start where a `Z` closed it)
/// with its paint; a closed shape its outline, or its box where it has fewer than three points.
fn push_shapes(
    el: &Element,
    h: &Inherited,
    tag: &str,
    here: usize,
    (subs, line): (Vec<(Vec<Pt>, bool)>, bool),
    shapes: &mut Vec<Shape>,
) {
    // the pattern in sheet px: its lengths scaled as the element's own are (exact for a turn and an even scale)
    let attrs = &el.attrib;
    let scale = (h.m.0 * h.m.3 - h.m.1 * h.m.2).abs().sqrt();
    for (pts, closed) in subs {
        if pts.len() < 2 {
            continue;
        }
        let mut tp: Vec<Pt> = pts.iter().map(|&p| apply(h.m, p)).collect();
        let base = Shape {
            tag: tag.to_owned(),
            kind: h.kind.clone(),
            attrs: Some(attrs.clone()),
            group: h.group,
            texture: h.texture,
            at: here,
            ids: h.ids.clone(),
            frame: IDENTITY,
            ..Shape::default()
        };
        if line {
            if closed && tp.first() != tp.last() {
                tp.push(tp[0]);
            }
            shapes.push(Shape {
                poly: tp,
                half: h.stroke_w / 2.0,
                line: true,
                leader: el.get("data-leader") == Some("1"),
                dark: luma(Some(&h.ink.0)) < DARK,
                cap: h.cap,
                join: h.join,
                miter: h.miter,
                closed,
                dash: h.dash.iter().map(|v| v * scale).collect(),
                offset: h.offset * scale,
                ..base
            });
        } else {
            let (x0, y0, x1, y1) = bbox(&tp);
            let poly = if tp.len() >= 3 {
                tp
            } else {
                vec![(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
            };
            shapes.push(Shape {
                poly,
                edge: if h.stroked { h.stroke_w / 2.0 } else { 0.0 },
                filled: h.ink.1 != "none",
                dark: luma(Some(&h.ink.1)) < DARK,
                busy: BUSY_FILLS.contains(&h.ink.1.as_str()),
                join: h.join,
                miter: h.miter,
                ..base
            });
        }
    }
}

/// A caption's `<text>` as a shape: its lines (its `<tspan>`s', else its own text), its block measured at its face, centered as `label()`
/// centers it, turned with the sheet.
///
/// Research:
///     its drawn sizes - CONVENTION: sizes on the sheet, not in the world - 12 (default font size)
fn text_shape(el: &Element, h: &Inherited, parent: Affine, here: usize) -> Shape {
    let (m, kind) = (h.m, h.kind.as_str());
    let attrs = &el.attrib;
    let size = attr_f(attrs, "font-size", 12.0);
    let spans: Vec<&Element> = el
        .elements()
        .into_iter()
        .skip(1)
        .filter(|t| t.tag == "tspan" && t.ns == SVG_NS)
        .collect();
    let mut lines: Vec<String> = if spans.is_empty() {
        vec![strip(&el.text).to_owned()]
    } else {
        spans.iter().map(|t| strip(&t.text).to_owned()).collect()
    };
    lines.retain(|l| !l.is_empty());
    if lines.is_empty() {
        lines.push(String::new());
    }
    let (x, y) = (attr_f(attrs, "x", 0.0), attr_f(attrs, "y", 0.0));
    let anchor = el.get("text-anchor").unwrap_or("start");
    let text = lines.join(" ");
    let (bw, bh) = block_half(&lines, size, char_w_of(Some(attrs), &text, size));
    let pitch = PITCH_EM * size;
    let cx = match anchor {
        "middle" => x,
        "end" => x - bw,
        _ => x + bw,
    };
    #[expect(clippy::cast_precision_loss, reason = "a caption's line count")]
    let cy = y + (lines.len() as f64 - 1.0) * pitch / 2.0 - CENTER_ABOVE_BASELINE_EM * size;
    let c = apply(m, (cx, cy));
    let ang = angle(m);
    Shape {
        tag: "text".to_owned(),
        kind: kind.to_owned(),
        poly: rect(c.0, c.1, bw, bh, ang),
        text,
        size,
        attrs: Some(attrs.clone()),
        lines,
        // its PARENT matrix (its groups' transforms, not its own): the frame a rewrite writes in
        frame: parent,
        group: h.group,
        at: here,
        ids: h.ids.clone(),
        names: l7r_guard::shared::py_text::split(el.get("data-names").unwrap_or_default())
            .into_iter()
            .map(str::to_owned)
            .collect(),
        cont: el.get("data-cont") == Some("1"),
        ..Shape::default()
    }
}
