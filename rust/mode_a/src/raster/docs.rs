//! The documents a picture is rendered from (`raster.py`'s off-map rule and tiles, features 200, 326, 327; ported by feature 449 T150):
//! a drawn string less every element, and every merged subpath, lying wholly outside the viewBox plus [`super::OFFMAP_MARGIN`] - invisible
//! by construction, the viewBox clipping what is dropped - and a tile's text, its window as the viewBox and each classed line clipped to it.
//! The parse and the judgment are two steps (feature 327): a picture parses a line once for all its tiles.
//!
//! Research: raster plumbing - NONE: what is cut is outside the window that clips it

use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::{Viewbox, OFFMAP_MARGIN};
use crate::page::merge::{attrs, get, NUM};
use crate::py::fmt_g;

static PATH: LazyLock<Regex> = LazyLock::new(|| py(r#"(<path [^>]*?d=")([^"]*)("[^>]*/>)"#));
static SHAPE: LazyLock<Regex> =
    LazyLock::new(|| py(r"<(circle|ellipse|line|rect|polygon|polyline)\b([^>]*)/>"));
/// The merge's own grammar (`page._sub`): a line `M x,y L x,y`, a disc `M x-r,y a r,r 0 1 0 2r,0 a ...`, matched whole.
static MERGE_GRAMMAR: LazyLock<Regex> =
    LazyLock::new(|| py(r"\A(?:(M-?[\d.]+,-?[\d.]+(L-?[\d.]+,-?[\d.]+|a[^Mm]*))+)\z"));
static SUBPATH: LazyLock<Regex> = LazyLock::new(|| py(r"[Mm][^Mm]*"));
static VIEWBOX_ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"viewBox="[^"]*""#));
/// The writer's own attribute order, read directly (feature 224); any other order falls to the general parse, with the same verdict.
static FAST_CIRCLE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"\A\s*cx="(-?[\d.]+)" cy="(-?[\d.]+)" r="(-?[\d.]+)""#));
static FAST_ELLIPSE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"\A\s*cx="(-?[\d.]+)" cy="(-?[\d.]+)" rx="(-?[\d.]+)" ry="(-?[\d.]+)""#));
static FAST_LINE: LazyLock<Regex> =
    LazyLock::new(|| py(r#"\A\s*x1="(-?[\d.]+)" y1="(-?[\d.]+)" x2="(-?[\d.]+)" y2="(-?[\d.]+)""#));
static FAST_RECT: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"\A\s*x="(-?[\d.]+)" y="(-?[\d.]+)" width="(-?[\d.]+)" height="(-?[\d.]+)""#)
});

/// How `page.wrap` opens a classed string - the strings the page itself clips to its viewBox.
const CLASSED_LINE: &str = "<g class=\"f ";

/// A box: x min, x max, y min, y max.
pub type Box4 = (f64, f64, f64, f64);

/// One part of a prepared line: text kept whole, a shape with its box, or a merged path's opening, its subpaths with their boxes, and its
/// closing.
#[derive(Debug, Clone, PartialEq)]
pub enum Part {
    Text(String),
    Shape(String, Box4),
    Path(String, Vec<(String, Box4)>, String),
}

/// A prepared document: each line, a classed one prepared.
#[derive(Debug, Clone, PartialEq)]
pub enum Line {
    Plain(String),
    Prepared(Vec<Part>),
}

fn bx(xs: &[f64], ys: &[f64]) -> Box4 {
    let ((x0, x1), (y0, y1)) = (crate::page::value::span(xs), crate::page::value::span(ys));
    (x0, x1, y0, y1)
}

fn fast(tag: &str) -> Option<&'static Regex> {
    Some(match tag {
        "circle" => &FAST_CIRCLE,
        "ellipse" => &FAST_ELLIPSE,
        "line" => &FAST_LINE,
        "rect" => &FAST_RECT,
        _ => return None,
    })
}

/// The extent the off-map rule judges a shape by, or none for one it does not judge (kept whole) (`raster._shape_box`).
///
/// # Errors
/// A figure of the writer's own order that `[\d.]+` took and the Python's `float()` refused (read outside its `try`).
pub fn shape_box(tag: &str, body: &str) -> Result<Option<Box4>, Error> {
    if let Some(c) = fast(tag).and_then(|re| re.captures(body).ok().flatten()) {
        let g: Vec<f64> = (1..c.len())
            .map(|i| crate::py::float(&c[i]))
            .collect::<Result<_, _>>()?;
        return Ok(Some(match tag {
            "circle" => bx(&[g[0] - g[2], g[0] + g[2]], &[g[1] - g[2], g[1] + g[2]]),
            "ellipse" => bx(&[g[0] - g[2], g[0] + g[2]], &[g[1] - g[3], g[1] + g[3]]),
            "line" => bx(&[g[0], g[2]], &[g[1], g[3]]),
            _ => bx(&[g[0], g[0] + g[2]], &[g[1], g[1] + g[3]]),
        }));
    }
    let at = attrs(body);
    let read = |k: &str| get(&at, k).and_then(|v| crate::py::float(v).ok());
    let (xs, ys): (Vec<f64>, Vec<f64>) = match tag {
        "circle" => {
            let (Some(cx), Some(cy), Some(r)) = (read("cx"), read("cy"), read("r")) else {
                return Ok(None);
            };
            (vec![cx - r, cx + r], vec![cy - r, cy + r])
        }
        "ellipse" => {
            let (Some(cx), Some(cy), Some(rx), Some(ry)) =
                (read("cx"), read("cy"), read("rx"), read("ry"))
            else {
                return Ok(None);
            };
            (vec![cx - rx, cx + rx], vec![cy - ry, cy + ry])
        }
        "line" => {
            let (Some(x1), Some(x2), Some(y1), Some(y2)) =
                (read("x1"), read("x2"), read("y1"), read("y2"))
            else {
                return Ok(None);
            };
            (vec![x1, x2], vec![y1, y2])
        }
        "rect" => {
            let (Some(left), Some(top), Some(width), Some(height)) =
                (read("x"), read("y"), read("width"), read("height"))
            else {
                return Ok(None);
            };
            (vec![left, left + width], vec![top, top + height])
        }
        _ => {
            let Some(points) = get(&at, "points") else {
                return Ok(None);
            };
            let nums: Option<Vec<f64>> = NUM
                .find_iter(points)
                .flatten()
                .map(|m| crate::py::float(m.as_str()).ok())
                .collect();
            let Some(nums) = nums else { return Ok(None) };
            (
                nums.iter().step_by(2).copied().collect(),
                nums.iter().skip(1).step_by(2).copied().collect(),
            )
        }
    };
    if xs.is_empty() || ys.is_empty() {
        return Ok(None);
    }
    Ok(Some(bx(&xs, &ys)))
}

/// A merged subpath's box: its numbers in pairs, and an arc subpath's disc (it starts a radius left of its center).
///
/// # Errors
/// An arc subpath with no number after its `a` (the Python's `IndexError`).
pub fn subpath_box(sp: &str) -> Result<Box4, Error> {
    let nums = |t: &str| -> Vec<f64> {
        NUM.find_iter(t)
            .flatten()
            .filter_map(|m| crate::py::float(m.as_str()).ok())
            .collect()
    };
    let all = nums(sp);
    let mut xs: Vec<f64> = all.iter().step_by(2).copied().collect();
    let mut ys: Vec<f64> = all.iter().skip(1).step_by(2).copied().collect();
    if let Some((_, after)) = sp.split_once('a') {
        let r = *nums(after)
            .first()
            .ok_or_else(|| Error::new("IndexError", "list index out of range"))?;
        xs = vec![xs[0], xs[0] + 2.0 * r];
        ys = vec![ys[0] - r, ys[0] + r];
    }
    Ok(bx(&xs, &ys))
}

/// One drawn string as the parts the off-map rule judges, each with its extent, parsed ONCE (`raster.prepare_offmap`): a string carrying a
/// `transform` is one whole part, and so is a path outside the merge grammar and a shape the rule does not read.
///
/// # Errors
/// [`shape_box`]'s or [`subpath_box`]'s.
pub fn prepare_offmap(s: &str) -> Result<Vec<Part>, Error> {
    if s.contains("transform=") {
        return Ok(vec![Part::Text(s.to_owned())]);
    }
    let mut found: Vec<(usize, usize, bool, fancy_regex::Captures<'_>)> = PATH
        .captures_iter(s)
        .flatten()
        .map(|c| {
            let r = c.get(0).map_or(0..0, |m| m.range());
            (r.start, r.end, true, c)
        })
        .collect();
    let paths: Vec<(usize, usize)> = found.iter().map(|(a, b, _, _)| (*a, *b)).collect();
    for c in SHAPE.captures_iter(s).flatten() {
        let r = c.get(0).map_or(0..0, |m| m.range());
        // a shape never sits inside a path's tag, but say so rather than assume it
        if !paths.iter().any(|&(a, b)| a <= r.start && r.start < b) {
            found.push((r.start, r.end, false, c));
        }
    }
    found.sort_by_key(|f| f.0);
    let mut parts = Vec::new();
    let mut at = 0;
    for (a, b, is_path, m) in found {
        if a > at {
            parts.push(Part::Text(s[at..a].to_owned()));
        }
        if is_path {
            let d = &m[2];
            if MERGE_GRAMMAR.is_match(d).unwrap_or(false) {
                let subs: Vec<(String, Box4)> = SUBPATH
                    .find_iter(d)
                    .flatten()
                    .map(|sp| subpath_box(sp.as_str()).map(|b| (sp.as_str().to_owned(), b)))
                    .collect::<Result<_, _>>()?;
                parts.push(Part::Path(m[1].to_owned(), subs, m[3].to_owned()));
            } else {
                parts.push(Part::Text(m[0].to_owned()));
            }
        } else {
            parts.push(match shape_box(&m[1], &m[2])? {
                None => Part::Text(m[0].to_owned()),
                Some(bx) => Part::Shape(m[0].to_owned(), bx),
            });
        }
        at = b;
    }
    if at < s.len() {
        parts.push(Part::Text(s[at..].to_owned()));
    }
    Ok(parts)
}

/// A prepared string less every part, and every merged subpath, wholly outside the viewBox plus the margin; a merged path none of whose
/// subpaths stays is dropped whole (`raster.assemble_offmap`).
#[must_use]
pub fn assemble_offmap(parts: &[Part], vb: Viewbox) -> String {
    let (x0, y0) = (vb.0 - OFFMAP_MARGIN, vb.1 - OFFMAP_MARGIN);
    let (x1, y1) = (vb.0 + vb.2 + OFFMAP_MARGIN, vb.1 + vb.3 + OFFMAP_MARGIN);
    let inside = |b: &Box4| !(b.1 < x0 || b.0 > x1 || b.3 < y0 || b.2 > y1);
    let mut out = String::new();
    for part in parts {
        match part {
            Part::Text(t) => out += t,
            Part::Shape(t, b) => {
                if inside(b) {
                    out += t;
                }
            }
            Part::Path(open, subs, close) => {
                let keep: Vec<&str> = subs
                    .iter()
                    .filter(|(_, b)| inside(b))
                    .map(|(sp, _)| sp.as_str())
                    .collect();
                if !keep.is_empty() {
                    out += open;
                    out += &keep.concat();
                    out += close;
                }
            }
        }
    }
    out
}

/// One drawn string less what lies wholly outside the viewBox plus the margin (`raster.drop_offmap`).
///
/// # Errors
/// [`prepare_offmap`]'s.
pub fn drop_offmap(s: &str, vb: Viewbox) -> Result<String, Error> {
    Ok(assemble_offmap(&prepare_offmap(s)?, vb))
}

/// The picture's text a line at a time, each classed line prepared once (`raster.prepare_doc`).
///
/// # Errors
/// [`prepare_offmap`]'s.
pub fn prepare_doc(svg_text: &str) -> Result<Vec<Line>, Error> {
    svg_text
        .split('\n')
        .map(|line| {
            if line.starts_with(CLASSED_LINE) {
                prepare_offmap(line).map(Line::Prepared)
            } else {
                Ok(Line::Plain(line.to_owned()))
            }
        })
        .collect()
}

/// The page's text as one tile renders it (`raster.tile_doc`, feature 326): the tile's window as the viewBox, every classed line less what
/// lies wholly outside it.
#[must_use]
pub fn tile_doc(lines: &[Line], b: Viewbox) -> String {
    let text: Vec<String> = lines
        .iter()
        .map(|l| match l {
            Line::Plain(t) => t.clone(),
            Line::Prepared(parts) => assemble_offmap(parts, b),
        })
        .collect();
    let text = text.join("\n");
    let vb = format!(
        "viewBox=\"{} {} {} {}\"",
        fmt_g(b.0),
        fmt_g(b.1),
        fmt_g(b.2),
        fmt_g(b.3)
    );
    match VIEWBOX_ATTR.find(&text).ok().flatten() {
        Some(m) => format!("{}{vb}{}", &text[..m.start()], &text[m.end()..]),
        None => text,
    }
}

#[cfg(test)]
mod tests;
