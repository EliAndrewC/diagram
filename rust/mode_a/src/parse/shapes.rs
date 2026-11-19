//! The parse's shapes (feature 449 T170, `parse.py`'s `_rects`, `path_rings`, `_path_rects`, `rooms_folded`, `_wall_bands`, `_trees`
//! and `_roofed_courts`): every rect, a rectilinear path as the rects it covers, the walls' inked bands, the canopies and the roofed
//! courts, each read as the Python read it.
//!
//! Research:
//!     the parse's shapes - NONE: a sheet's rects, paths, walls and canopies read by their tags and palette, deciding nothing about a building

use std::collections::BTreeMap;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::{py, WORD};
use l7r_gate_research::Error;

use super::{cp, wall_kind, Rect, COURT_FLOORS, MIN_TREE_R_PX, ROOF_STROKES, TREE_FILL};
use crate::py::{float, min};
use crate::sheet::Offsets;
use crate::tagged::attrs;

// PYTHON'S `\b` AFTER A TAG'S NAME, WRITTEN OUT (feature 449 T170): `<rect\b([^>]*)>` holds when the character after the name is no
// word character of Python's (`pyre::WORD`) - so the attributes are empty or open on such a character. Written as a lookaround, each such
// pattern ran the backtracking engine at every offset of the sheet, 1.5-2.6 ms a scan against 24 us for the same pattern without it
// (observed 2026-11-17 on the shrine's sheet); written out, the regex crate runs it. The same matches, offsets and groups, which the
// lockstep's fixtures (`<rectangle`, a combining mark after `<g`) hold against the Python.
// The optional part is LAZY, as the Python's own group was where it was lazy: `<g/>`'s attributes are "" (not "/") either way.
pub(crate) fn after_name(rest: &str) -> String {
    format!("(?:[^>{WORD}]{rest})??")
}
static RECT_TAG: LazyLock<Regex> =
    LazyLock::new(|| py(&format!("<rect({})>", after_name("[^>]*"))));
static ATTR_ANY: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w:-]+)="([^"]*)""#));
static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([\w-]+)="([^"]*)""#));
static PATH_TAG: LazyLock<Regex> =
    LazyLock::new(|| py(&format!("<path({})>", after_name("[^>]*"))));
static PATH_TOKEN: LazyLock<Regex> = LazyLock::new(|| py(r"[MLHVZ]|-?\d+(?:\.\d+)?"));
static PATH_OTHER: LazyLock<Regex> = LazyLock::new(|| py(r"[^MLHVZ\d\s.,-]"));
static ELEM: LazyLock<Regex> =
    LazyLock::new(|| py(&format!("<(/?)(g|line)({})/?>", after_name("[^>]*?"))));
static TREE_GROUP: LazyLock<Regex> =
    // `<g\b[^>]*\bid=`: the attributes before the name open and close on a non-word character (a name straight after `<g` fails both)
    LazyLock::new(|| {
        py(&format!(
            r##"(?s)<g[^>{WORD}](?:[^>]*[^>{WORD}])?(?:id="trees"|fill="#7A8C5C")[^>]*>(.*?)</g>"##
        ))
    });
static CIRCLE_TAG: LazyLock<Regex> =
    LazyLock::new(|| py(&format!("<circle({})>", after_name("[^>]*"))));
// `<defs\b.*?`: here the character after the name may be the tag's own `>`
static DEFS: LazyLock<Regex> = LazyLock::new(|| py(&format!("(?s)<defs(?:[^{WORD}].*?)??</defs>")));

type Attrs = BTreeMap<String, String>;

fn get<'a>(a: &'a Attrs, key: &str) -> &'a str {
    a.get(key).map_or("", String::as_str)
}

/// `float(attrs[key])`: a missing attribute is the Python's `KeyError`.
fn number(a: &Attrs, key: &str) -> Result<f64, Error> {
    let text = a
        .get(key)
        .ok_or_else(|| Error::new("KeyError", key.to_owned()))?;
    float(text)
}

/// Every `<rect>` with x, y, width, height and a fill (any rect at all with `need_fill` false, its fill ""), whatever its attribute
/// order, in draw order - with the filled rectilinear paths' rects among them where a fill is needed.
pub(super) fn rects(text: &str, need_fill: bool) -> Result<Vec<Rect>, Error> {
    let offsets = Offsets::new(text);
    let mut out = Vec::new();
    for tag in RECT_TAG.captures_iter(text).map_while(Result::ok) {
        let attr = attrs(&ATTR_ANY, &tag[1]);
        if !["x", "y", "width", "height"]
            .iter()
            .all(|k| attr.contains_key(*k))
            || (need_fill && !attr.contains_key("fill"))
        {
            continue;
        }
        // a value `float()` refuses skips the rect, as the Python's `except ValueError: continue`
        let (Ok(x), Ok(y), Ok(w), Ok(h)) = (
            float(get(&attr, "x")),
            float(get(&attr, "y")),
            float(get(&attr, "width")),
            float(get(&attr, "height")),
        ) else {
            continue;
        };
        out.push(Rect {
            ident: get(&attr, "id").to_owned(),
            ..Rect::new(
                x,
                y,
                w,
                h,
                get(&attr, "fill"),
                cp(&offsets, tag.get(0).map_or(0, |g| g.start())),
            )
        });
    }
    if need_fill {
        out.extend(path_rects(text, &offsets)?);
        // a stable sort, as the Python's `sorted(..., key=pos)`
        out.sort_by_key(|r| r.pos);
    }
    Ok(out)
}

/// Python's `sorted()` order of two floats: equal ones (`-0.0` and `0.0`) keep their order, the sort being stable.
#[expect(
    clippy::trivially_copy_pass_by_ref,
    reason = "`sort_by`'s comparator takes its items by reference"
)]
fn py_order(a: &f64, b: &f64) -> std::cmp::Ordering {
    a.partial_cmp(b).unwrap_or(std::cmp::Ordering::Equal)
}

/// One ring of a path.
pub type Ring = Vec<(f64, f64)>;

/// The rings of a path drawn only with absolute moves, lines and axis steps, every edge axis-aligned - the form a hand sheet draws an
/// L-shaped or holed ground in; None for any other path (a curve, a relative step, a diagonal).
///
/// # Errors
/// The Python's: a coordinate missing after a move (`IndexError`) or a command letter where a number is read (`ValueError`).
#[expect(
    clippy::float_cmp,
    reason = "an edge is axis-aligned when its ends' coordinates are EQUAL, as the Python compared them"
)]
pub fn path_rings(d: &str) -> Result<Option<Vec<Ring>>, Error> {
    if PATH_OTHER.is_match(d).unwrap_or(false) {
        return Ok(None);
    }
    let toks: Vec<&str> = PATH_TOKEN
        .find_iter(d)
        .map_while(Result::ok)
        .map(|m| m.as_str())
        .collect();
    let mut rings: Vec<Ring> = Vec::new();
    let (mut px, mut py_) = (0.0, 0.0);
    let mut cmd = "";
    let mut at = 0;
    while at < toks.len() {
        let tok = toks[at];
        if matches!(tok, "M" | "L" | "H" | "V" | "Z") {
            (cmd, at) = (tok, at + 1);
            if tok == "M" {
                rings.push(Vec::new());
            }
            continue;
        }
        // the Python's `cmd in "ML"`: true of the empty command too, so a number before any command is a move's
        if matches!(cmd, "" | "M" | "L") {
            px = float(tok)?;
            let next = toks
                .get(at + 1)
                .ok_or_else(|| Error::new("IndexError", "list index out of range"))?;
            (py_, at) = (float(next)?, at + 2);
        } else if cmd == "H" {
            (px, at) = (float(tok)?, at + 1);
        } else {
            (py_, at) = (float(tok)?, at + 1);
        }
        let Some(ring) = rings.last_mut() else {
            return Ok(None);
        };
        ring.push((px, py_));
    }
    for ring in &rings {
        for (k, &(ax, ay)) in ring.iter().enumerate() {
            let (bx, by) = ring[(k + 1) % ring.len()];
            if ax != bx && ay != by {
                return Ok(None);
            }
        }
    }
    let kept: Vec<Ring> = rings.into_iter().filter(|r| r.len() >= 4).collect();
    Ok(if kept.is_empty() { None } else { Some(kept) })
}

/// A filled rectilinear `<path>` as the rects it covers, cut into horizontal slabs by the even-odd rule (feature 283: Ochiba's inner
/// garden, drawn as an L, was invisible to every fills-based check).
#[expect(
    clippy::float_cmp,
    reason = "an edge is vertical when its ends' x are EQUAL, as the Python compared them"
)]
#[expect(
    clippy::manual_midpoint,
    reason = "the Python's `(y0 + y1) / 2`, written as it computed it"
)]
fn path_rects(text: &str, offsets: &Offsets) -> Result<Vec<Rect>, Error> {
    let mut out = Vec::new();
    for m in PATH_TAG.captures_iter(text).map_while(Result::ok) {
        let a = attrs(&ATTR_ANY, &m[1]);
        let fill = get(&a, "fill");
        if fill.is_empty() || fill == "none" {
            continue;
        }
        let Some(rings) = path_rings(get(&a, "d"))? else {
            continue;
        };
        let at = cp(offsets, m.get(0).map_or(0, |g| g.start()));
        let mut verticals = Vec::new();
        let mut ys: Vec<f64> = Vec::new();
        for ring in &rings {
            for (k, &(ax, ay)) in ring.iter().enumerate() {
                let (bx, by) = ring[(k + 1) % ring.len()];
                if ax == bx && ay != by {
                    verticals.push((ax, min(ay, by), if by > ay { by } else { ay }));
                }
            }
        }
        // `sorted({p[1] ...})`: each y once (the first of equals kept, as a set keeps -0.0 or 0.0 by which came first)
        for &(_, py_) in rings.iter().flatten() {
            if !ys.contains(&py_) {
                ys.push(py_);
            }
        }
        ys.sort_by(py_order);
        for pair in ys.windows(2) {
            let (y0, y1) = (pair[0], pair[1]);
            let mid = (y0 + y1) / 2.0;
            let mut xs: Vec<f64> = verticals
                .iter()
                .filter(|&&(_, lo, hi)| lo < mid && mid < hi)
                .map(|&(x, _, _)| x)
                .collect();
            xs.sort_by(py_order);
            for p in xs.chunks_exact(2) {
                if p[1] > p[0] {
                    out.push(Rect {
                        ident: get(&a, "id").to_owned(),
                        ..Rect::new(p[0], y0, p[1] - p[0], y1 - y0, fill, at)
                    });
                }
            }
        }
    }
    Ok(out)
}

/// The buildings less their ROOMS: a rect of a building's own fill drawn wholly inside an earlier one is a room's floor (feature 264),
/// not a second building.
#[must_use]
pub fn rooms_folded(buildings: Vec<Rect>) -> Vec<Rect> {
    let mut out: Vec<Rect> = Vec::new();
    for r in buildings {
        if !out.iter().any(|o| {
            o.fill == r.fill
                && o.x <= r.x
                && o.y <= r.y
                && r.x + r.w <= o.x + o.w
                && r.y + r.h <= o.y + o.h
        }) {
            out.push(r);
        }
    }
    out
}

/// The INKED band of every wall or court-divider stroke as an axis-aligned rect, a `<g>`'s attributes inherited by its lines (both
/// authoring forms in the pool); `fill` carries the stroke's color, and a square cap inks half a stroke past each end.
pub(super) fn wall_bands(text: &str, offsets: &Offsets) -> Result<Vec<Rect>, Error> {
    let mut stack: Vec<Attrs> = Vec::new();
    let mut out = Vec::new();
    for m in ELEM.captures_iter(text).map_while(Result::ok) {
        let (closing, name, own) = (&m[1], &m[2], &m[3]);
        if name == "g" {
            if closing.is_empty() {
                stack.push(attrs(&ATTR, own));
            } else {
                stack.pop();
            }
            continue;
        }
        let mut d = Attrs::new();
        for frame in &stack {
            d.extend(frame.iter().map(|(k, v)| (k.clone(), v.clone())));
        }
        d.extend(attrs(&ATTR, own));
        let stroke = get(&d, "stroke");
        if wall_kind(stroke).is_none() || !d.contains_key("x1") {
            continue;
        }
        let sw = float(d.get("stroke-width").map_or("1", String::as_str))?;
        let hw = sw / 2.0;
        let cap = if get(&d, "stroke-linecap") == "square" {
            hw
        } else {
            0.0
        };
        let (x1, y1, x2, y2) = (
            number(&d, "x1")?,
            number(&d, "y1")?,
            number(&d, "x2")?,
            number(&d, "y2")?,
        );
        let at = cp(offsets, m.get(0).map_or(0, |g| g.start()));
        out.push(if (y2 - y1).abs() <= (x2 - x1).abs() {
            Rect::new(
                min(x1, x2) - cap,
                min(y1, y2) - hw,
                (x2 - x1).abs() + 2.0 * cap,
                sw,
                stroke,
                at,
            )
        } else {
            Rect::new(
                min(x1, x2) - hw,
                min(y1, y2) - cap,
                sw,
                (y2 - y1).abs() + 2.0 * cap,
                stroke,
                at,
            )
        });
    }
    Ok(out)
}

/// Every court floor drawn with a roof's solid outline, in draw order.
pub(super) fn roofed_courts(text: &str, offsets: &Offsets) -> Result<Vec<Rect>, Error> {
    let mut out = Vec::new();
    for tag in RECT_TAG.captures_iter(text).map_while(Result::ok) {
        let attr = attrs(&ATTR_ANY, &tag[1]);
        if COURT_FLOORS.contains(&get(&attr, "fill"))
            && ROOF_STROKES.contains(&get(&attr, "stroke"))
        {
            let at = cp(offsets, tag.get(0).map_or(0, |g| g.start()));
            let (left, top) = (number(&attr, "x")?, number(&attr, "y")?);
            let (w, h) = (number(&attr, "width")?, number(&attr, "height")?);
            out.push(Rect::new(left, top, w, h, get(&attr, "fill"), at));
        }
    }
    Ok(out)
}

/// Every canopy on the sheet as its bounding rect, `pos` the circle's offset (so the glyph pass can skip it): a circle in the canopy
/// green, or any circle in a group marked `id="trees"` or painted that green, outside the definitions and at least the glyph floor.
pub(super) fn trees(text: &str, offsets: &Offsets) -> Result<Vec<Rect>, Error> {
    let mut starts: Vec<usize> = Vec::new();
    for grp in TREE_GROUP.captures_iter(text).map_while(Result::ok) {
        let (whole, body) = (&grp[0], &grp[1]);
        // the Python's `grp.group(0).index(grp.group(1))`: the body's FIRST occurrence in the match, which is where its circles are read
        let base = grp.get(0).map_or(0, |m| m.start()) + whole.find(body).unwrap_or(0);
        starts.extend(
            CIRCLE_TAG
                .find_iter(body)
                .map_while(Result::ok)
                .map(|c| base + c.start()),
        );
    }
    for c in CIRCLE_TAG.captures_iter(text).map_while(Result::ok) {
        if get(&attrs(&ATTR_ANY, &c[1]), "fill") == TREE_FILL {
            starts.push(c.get(0).map_or(0, |m| m.start()));
        }
    }
    starts.sort_unstable();
    starts.dedup();
    let defs: Vec<(usize, usize)> = DEFS
        .find_iter(text)
        .map_while(Result::ok)
        .map(|m| (m.start(), m.end()))
        .collect();
    let mut out = Vec::new();
    for start in starts {
        if defs.iter().any(|&(a, b)| a <= start && start < b) {
            continue;
        }
        // `start` is a `<circle` offset by construction (the Python asserts it), so the tag is read from there
        let tag = CIRCLE_TAG.captures_from_pos(text, start).ok().flatten();
        let attr = attrs(
            &ATTR_ANY,
            tag.as_ref()
                .map_or("", |c| c.get(1).map_or("", |m| m.as_str())),
        );
        let num = |k: &str| float(attr.get(k).map_or("0", String::as_str));
        let (cx, cy, rad) = (num("cx")?, num("cy")?, num("r")?);
        if rad >= MIN_TREE_R_PX {
            out.push(Rect::new(
                cx - rad,
                cy - rad,
                2.0 * rad,
                2.0 * rad,
                TREE_FILL,
                cp(offsets, start),
            ));
        }
    }
    Ok(out)
}
