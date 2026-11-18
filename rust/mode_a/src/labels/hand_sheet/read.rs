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
use super::super::standard::{block_half, CENTER_ABOVE_BASELINE_EM, PITCH_EM};
use super::{char_w_of, luma, Attrs, Shape, BUSY_FILLS, DARK};
use crate::etree::Element;

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
    for m in re.find_iter(text).flatten() {
        out.push(&text[at..m.start()]);
        at = m.end();
    }
    out.push(&text[at..]);
    out
}

fn numbers(re: &Regex, text: &str) -> Result<Vec<f64>, Error> {
    re.find_iter(text)
        .flatten()
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
    for c in TRANSFORM.captures_iter(t).flatten() {
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

/// A path's vertices - absolute and relative move, line, horizontal and vertical steps, and the end points of curves; enough for the
/// handful of paths the sheets draw (roads and banks).
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 6 (SVG C-command argument count); 7 (SVG A-command argument count)
///
/// # Errors
/// None the patterns let through: a number they match is always one.
pub fn path_points(d: &str) -> Result<Vec<Pt>, Error> {
    let mut pts = Vec::new();
    let (mut x, mut y) = (0.0, 0.0);
    for c in PATH_STEP.captures_iter(d).flatten() {
        let cmd = c[1].chars().next().unwrap_or('Z');
        let v = numbers(&PATH_NUMBER, &c[2])?;
        let step = match cmd.to_ascii_uppercase() {
            'M' | 'L' | 'T' => 2,
            'H' | 'V' => 1,
            'C' => 6,
            'S' | 'Q' => 4,
            'A' => 7,
            _ => continue,
        };
        let rel = cmd.is_ascii_lowercase();
        let mut i = 0;
        while i + step <= v.len() {
            let chunk = &v[i..i + step];
            match cmd.to_ascii_uppercase() {
                'H' => x = if rel { x + chunk[0] } else { chunk[0] },
                'V' => y = if rel { y + chunk[0] } else { chunk[0] },
                _ => {
                    let (ex, ey) = (chunk[step - 2], chunk[step - 1]);
                    (x, y) = if rel { (x + ex, y + ey) } else { (ex, ey) };
                }
            }
            pts.push((x, y));
            i += step;
        }
    }
    Ok(pts)
}

/// What a walk inherits from the elements around: the matrix, the kind and its group, the stroke's width and whether one is drawn, the
/// (stroke, fill), the texture mark and the `data-id`s.
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
    let (pts, line): (Vec<Pt>, bool) = match tag.as_str() {
        "rect" => {
            let (x, y, w, hh) = (f("x"), f("y"), f("width"), f("height"));
            (
                vec![(x, y), (x + w, y), (x + w, y + hh), (x, y + hh)],
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
                vec![
                    (cx - rx, cy - ry),
                    (cx + rx, cy - ry),
                    (cx + rx, cy + ry),
                    (cx - rx, cy + ry),
                ],
                false,
            )
        }
        "polygon" | "polyline" => {
            let v = numbers(&NUMBER, el.get("points").unwrap_or_default())?;
            let pts = v.chunks_exact(2).map(|p| (p[0], p[1])).collect();
            (
                pts,
                tag == "polyline" && el.get("fill").unwrap_or("none") == "none",
            )
        }
        "line" => (vec![(f("x1"), f("y1")), (f("x2"), f("y2"))], true),
        "path" => (
            path_points(el.get("d").unwrap_or_default())?,
            h.stroked && el.get("fill").unwrap_or_default() == "none",
        ),
        "text" => {
            shapes.push(text_shape(el, &h, up.m, here));
            *at += el.elements().len() - 1; // its `<tspan>`s are elements of `root.iter()` too
            return Ok(());
        }
        _ => (Vec::new(), false),
    };
    if pts.len() >= 2 {
        let tp: Vec<Pt> = pts.iter().map(|&p| apply(h.m, p)).collect();
        let base = Shape {
            tag: tag.clone(),
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
            shapes.push(Shape {
                poly: tp,
                half: h.stroke_w / 2.0,
                line: true,
                leader: el.get("data-leader") == Some("1"),
                dark: luma(Some(&h.ink.0)) < DARK,
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
                ..base
            });
        }
    }
    for c in &el.children {
        walk(c, &h, at, shapes)?;
    }
    Ok(())
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
