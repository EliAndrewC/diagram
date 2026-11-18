//! MANY SAME-STYLED LINES OR CIRCLES BECOME ONE `<path>` (`page.merge_primitives` and `extents.py`, features 134, 148, 153, 199, 278;
//! ported by feature 449 T150): the page's second serialization of the drawn strings, never the SVG or the PNG (feature 134 FR-010).
//!
//! WHAT MAKES THE REORDER LEGAL (feature 148): two elements of one style paint the same ink in either order, so they may be gathered; one
//! moved BACKWARD past a different element it overlaps is not, so each bucket remembers the extents it skipped since its last member
//! (`skip`, at most [`SKIP_CAP`]) and an element joins only if it touches none. A translucent or outlined shape may not merge with a
//! member it overlaps (feature 153: a path paints every subpath fill, then its stroke). A big bucket is written one path per [`TILE`]
//! cell (feature 199: Chromium replays every display item whose box touches a tile). The extents are filed in grids of their boxes
//! ([`BoxGrid`], feature 278), which return every extent the overlap test could find.
//!
//! Research:
//!     the merge's plumbing - NONE: the extents, the buckets and the paths written, which change no pixel of the drawing

use std::collections::HashMap;
use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use crate::py::{fmt_g, max, min};

/// One element's attributes, as `dict(_ATTR.findall(body))`: each name once, at its first place, holding its last value.
pub type Attrs = Vec<(String, String)>;

/// `at.get(name)`.
#[must_use]
pub fn get<'a>(at: &'a Attrs, name: &str) -> Option<&'a str> {
    at.iter().find(|(k, _)| k == name).map(|(_, v)| v.as_str())
}

static ATTR: LazyLock<Regex> = LazyLock::new(|| py(r#"([a-z0-9-]+)="([^"]*)""#));
/// Every element the merge reasons about: the three it can MERGE, and the rest, which it locates well enough to know whether something
/// may be moved past them.
static ELEM: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"<(line|circle|ellipse|path|polygon|polyline|rect)\s((?:[a-z0-9-]+="[^"]*"\s*)+)/?>"#)
});
pub(crate) static NUM: LazyLock<Regex> = LazyLock::new(|| py(r"-?\d+(?:\.\d+)?"));

/// The attributes of an element's body, as the Python's `dict` builds them.
#[must_use]
pub fn attrs(body: &str) -> Attrs {
    let mut out = Attrs::new();
    for c in ATTR.captures_iter(body).flatten() {
        let (k, v) = (&c[1], &c[2]);
        match out.iter_mut().find(|(n, _)| n == k) {
            Some(slot) => v.clone_into(&mut slot.1),
            None => out.push((k.to_owned(), v.to_owned())),
        }
    }
    out
}

/// The coordinates of each tag the merge can merge: everything else is the STYLE.
fn coords(tag: &str) -> Option<&'static [&'static str]> {
    match tag {
        "line" => Some(&["x1", "y1", "x2", "y2"]),
        "circle" => Some(&["cx", "cy", "r"]),
        "ellipse" => Some(&["cx", "cy", "rx", "ry"]),
        _ => None,
    }
}

/// How many skipped extents one bucket holds before it gives up: a bound on the work, not a rule about the map.
pub const SKIP_CAP: usize = 400;
/// The cell a big merged scatter is written by, in map px (feature 199): 200 px measured the same as 400 and tripled the nodes, 800 gave
/// part of the gain back (specs/199 research R3).
///
/// Research: the merged scatter's cell - CONVENTION: a big same-styled bucket is written one path per 400 px cell, measured to keep the ink unchanged (0-17 pixels of 1,400,000 at the cell seams, specs/199 research R4) while a hover repaints less; nothing physical is behind the size
pub const TILE: f64 = 400.0;
/// The bucket size below which one path is kept.
///
/// Research: the merged scatter's cell - CONVENTION: a bucket under 200 members stays one path, a small path costing nothing to replay
pub const TILE_MIN: usize = 200;

/// What one element paints inside: a disc for a circle, a box for anything else; `None` (an unreadable shape) is in the way everywhere.
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum Extent {
    Disc(f64, f64, f64),
    Box(f64, f64, f64, f64),
}

impl Extent {
    /// A disc's bounding box, or a box unchanged (`extents._box`).
    #[must_use]
    pub fn bbox(self) -> (f64, f64, f64, f64) {
        match self {
            Self::Disc(x, y, r) => (x - r, y - r, x + r, y + r),
            Self::Box(a, b, c, d) => (a, b, c, d),
        }
    }
}

/// Do two painted areas touch (`extents._hits`)? An unknown one touches everything; two discs are tested as discs (feature 153: a box
/// lies most about round blobs).
#[must_use]
pub fn hits(a: Option<Extent>, b: Option<Extent>) -> bool {
    let (Some(a), Some(b)) = (a, b) else {
        return true;
    };
    if let (Extent::Disc(ax, ay, ar), Extent::Disc(bx, by, br)) = (a, b) {
        let (dx, dy, rr) = (ax - bx, ay - by, ar + br);
        return dx * dx + dy * dy <= rr * rr;
    }
    let (ba, bb) = (a.bbox(), b.bbox());
    !(ba.2 < bb.0 || bb.2 < ba.0 || ba.3 < bb.1 || bb.3 < ba.1)
}

/// `float(text)`, or `None` where Python's `float` raised.
fn num(text: &str) -> Option<f64> {
    crate::py::float(text).ok()
}

/// `float(at.get(name) or 0.0)`: an absent or empty attribute is zero.
fn or_zero(at: &Attrs, name: &str) -> Result<f64, Error> {
    match get(at, name) {
        None | Some("") => Ok(0.0),
        Some(v) => crate::py::float(v),
    }
}

/// `min(values)` and `max(values)` as Python's: the first of equals kept.
fn span(values: &[f64]) -> (f64, f64) {
    let lo = values.iter().copied().reduce(min).unwrap_or(f64::NAN);
    let hi = values.iter().copied().reduce(max).unwrap_or(f64::NAN);
    (lo, hi)
}

/// The area an element paints inside (`page._extent`): a SUPERSET IS SAFE, so a path's box is taken over every number of its geometry
/// (a curve's control points included); `None` where it cannot be known cheaply.
///
/// # Errors
/// The `ValueError` of a stroke width that is no number on a line, ellipse or rect (read outside the Python's `try`).
pub fn extent(tag: &str, at: &Attrs) -> Result<Option<Extent>, Error> {
    let read = |k: &str| get(at, k).and_then(num);
    let (xs, ys) = match tag {
        "line" => {
            let (Some(x1), Some(x2), Some(y1), Some(y2)) =
                (read("x1"), read("x2"), read("y1"), read("y2"))
            else {
                return Ok(None);
            };
            ([x1, x2], [y1, y2])
        }
        "circle" => {
            let (Some(cx), Some(cy), Some(r)) = (read("cx"), read("cy"), read("r")) else {
                return Ok(None);
            };
            return Ok(or_zero(at, "stroke-width")
                .ok()
                .map(|w| Extent::Disc(cx, cy, r + w / 2.0)));
        }
        "ellipse" => {
            let (Some(cx), Some(cy), Some(rx), Some(ry)) =
                (read("cx"), read("cy"), read("rx"), read("ry"))
            else {
                return Ok(None);
            };
            ([cx - rx, cx + rx], [cy - ry, cy + ry])
        }
        "rect" => {
            let (Some(x), Some(y), Some(w), Some(h)) =
                (read("x"), read("y"), read("width"), read("height"))
            else {
                return Ok(None);
            };
            ([x, x + w], [y, y + h])
        }
        _ => {
            let geom = [get(at, "d"), get(at, "points")]
                .into_iter()
                .flatten()
                .find(|v| !v.is_empty())
                .unwrap_or("");
            let nums: Option<Vec<f64>> = NUM
                .find_iter(geom)
                .flatten()
                .map(|m| num(m.as_str()))
                .collect();
            let Some(nums) = nums.filter(|n| n.len() >= 4) else {
                return Ok(None);
            };
            let xs: Vec<f64> = nums.iter().step_by(2).copied().collect();
            let ys: Vec<f64> = nums.iter().skip(1).step_by(2).copied().collect();
            let ((x0, x1), (y0, y1)) = (span(&xs), span(&ys));
            return Ok(Some(Extent::Box(x0, y0, x1, y1)));
        }
    };
    let pad = or_zero(at, "stroke-width")? / 2.0;
    let ((x0, x1), (y0, y1)) = (span(&xs), span(&ys));
    Ok(Some(Extent::Box(x0 - pad, y0 - pad, x1 + pad, y1 + pad)))
}

/// Does this element paint a fill AND a stroke (`page._outlined`)? Those are painted in different passes once it is a subpath, so where
/// two overlap the merge changes which is on top. A line has no fill (feature 153: reading one as outlined cost 4,336 elements on
/// Kuwabata's scrub); an absent fill is black.
#[must_use]
pub fn outlined(tag: &str, at: &Attrs) -> bool {
    if tag == "line" || get(at, "fill").unwrap_or("black") == "none" {
        return false;
    }
    if get(at, "stroke").unwrap_or("none") == "none" {
        return false;
    }
    num(get(at, "stroke-width").unwrap_or("1")).is_none_or(|w| w > 0.0)
}

/// Extents filed by their boxes in square cells (`extents._BoxGrid`, feature 278): `near` returns a superset of the filed extents whose
/// boxes touch the asked one's, since touching boxes share a cell; a box wider than [`BoxGrid::BIG`] cells is kept aside and always returned.
#[derive(Debug, Default)]
pub struct BoxGrid {
    cells: HashMap<(i64, i64), Vec<Extent>>,
    big: Vec<Extent>,
}

impl BoxGrid {
    /// The cell, in map px.
    pub const CELL: f64 = 64.0;
    /// The span, in cells, past which a box is kept aside.
    pub const BIG: i64 = 24;

    fn span(e: Extent) -> Result<(i64, i64, i64, i64), Error> {
        let (x0, y0, x1, y1) = e.bbox();
        let cell = |v: f64| crate::py::floordiv(v, Self::CELL).and_then(crate::py::int);
        Ok((cell(x0)?, cell(y0)?, cell(x1)?, cell(y1)?))
    }

    /// File `e`.
    ///
    /// # Errors
    /// The `OverflowError` or `ValueError` of a box whose edge is no finite number (`int()` of it).
    pub fn add(&mut self, e: Extent) -> Result<(), Error> {
        let (i0, j0, i1, j1) = Self::span(e)?;
        if i1 - i0 > Self::BIG || j1 - j0 > Self::BIG {
            self.big.push(e);
            return Ok(());
        }
        for i in i0..=i1 {
            for j in j0..=j1 {
                self.cells.entry((i, j)).or_default().push(e);
            }
        }
        Ok(())
    }

    /// Whether any filed extent near `e` touches it.
    ///
    /// # Errors
    /// As [`BoxGrid::add`].
    pub fn any_hit(&self, e: Extent) -> Result<bool, Error> {
        let (i0, j0, i1, j1) = Self::span(e)?;
        let touch = |x: &Extent| hits(Some(e), Some(*x));
        if self.big.iter().any(touch) {
            return Ok(true);
        }
        if i1 - i0 > Self::BIG || j1 - j0 > Self::BIG {
            return Ok(self.cells.values().flatten().any(touch));
        }
        for i in i0..=i1 {
            for j in j0..=j1 {
                if self.cells.get(&(i, j)).is_some_and(|c| c.iter().any(touch)) {
                    return Ok(true);
                }
            }
        }
        Ok(false)
    }
}

/// One style's open bucket (the Python's bucket dict, its four flags among its keys).
#[expect(
    clippy::struct_excessive_bools,
    reason = "the Python bucket's four flags, each read where the Python reads it"
)]
struct Bucket {
    members: Vec<usize>,
    skip: usize,
    blocked: bool,
    tag: String,
    translucent: bool,
    outlined: bool,
    ext_grid: BoxGrid,
    ext_none: bool,
    skip_grid: BoxGrid,
}

impl Bucket {
    /// May this bucket NOT take an element painting inside `ext` (`extents._refused`)? Blocked; a translucent or outlined bucket whose
    /// member it overlaps; or a skipped extent since its last member that it overlaps.
    fn refused(&self, ext: Option<Extent>) -> Result<bool, Error> {
        if self.blocked {
            return Ok(true);
        }
        if self.translucent || self.outlined {
            let touched = match ext {
                None => true,
                Some(e) => self.ext_none || self.ext_grid.any_hit(e)?,
            };
            if touched {
                return Ok(true);
            }
        }
        match ext {
            None => Ok(self.skip > 0),
            Some(e) => self.skip_grid.any_hit(e),
        }
    }

    /// A member's extent into the bucket's grid, or the flag that an unreadable one is among them.
    fn file(&mut self, ext: Option<Extent>) -> Result<(), Error> {
        match ext {
            None => {
                self.ext_none = true;
                Ok(())
            }
            Some(e) => self.ext_grid.add(e),
        }
    }
}

/// Whether an attribute's opacity reads under one (`float(_st.get(k, 1) or 1) < 1.0`, the three in order).
fn translucent(at: &Attrs) -> Result<bool, Error> {
    for k in ["opacity", "fill-opacity", "stroke-opacity"] {
        let v = match get(at, k) {
            None | Some("") => 1.0,
            Some(v) => crate::py::float(v)?,
        };
        if v < 1.0 {
            return Ok(true);
        }
    }
    Ok(false)
}

/// A missing coordinate, as the Python's `KeyError`.
fn key(at: &Attrs, k: &str) -> Result<String, Error> {
    get(at, k)
        .map(str::to_owned)
        .ok_or_else(|| Error::new("KeyError", k))
}

/// One element as a subpath of the merged `d` (`page._sub`).
fn sub(tag: &str, at: &Attrs) -> Result<String, Error> {
    if tag == "line" {
        return Ok(format!(
            "M{},{}L{},{}",
            key(at, "x1")?,
            key(at, "y1")?,
            key(at, "x2")?,
            key(at, "y2")?
        ));
    }
    let (rx, ry) = if tag == "circle" {
        let r = crate::py::float(&key(at, "r")?)?;
        (r, r)
    } else {
        (
            crate::py::float(&key(at, "rx")?)?,
            crate::py::float(&key(at, "ry")?)?,
        )
    };
    let cx = crate::py::float(&key(at, "cx")?)?;
    let cy = key(at, "cy")?;
    let (gx, gy) = (fmt_g(rx), fmt_g(ry));
    Ok(format!(
        "M{},{cy}a{gx},{gy} 0 1 0 {},0a{gx},{gy} 0 1 0 {},0",
        fmt_g(cx - rx),
        fmt_g(2.0 * rx),
        fmt_g(-2.0 * rx)
    ))
}

/// The TILE cell of an element's anchor (`page._cell`).
fn cell(tag: &str, at: &Attrs) -> Result<(i64, i64), Error> {
    let (ax, ay) = if tag == "line" {
        ("x1", "y1")
    } else {
        ("cx", "cy")
    };
    // both looked up before either is read, as the Python's tuple is
    let (ax, ay) = (key(at, ax)?, key(at, ay)?);
    let floor = |v: &str| crate::py::float(v).and_then(|v| crate::py::floor(v / TILE));
    Ok((floor(&ax)?, floor(&ay)?))
}

/// A bucket's members as the runs that become one path each (`page._tiles`): one run per cell in order of each cell's first appearance,
/// or the whole bucket under [`TILE_MIN`].
fn tiles(tag: &str, members: &[usize], elems: &[Elem]) -> Result<Vec<Vec<usize>>, Error> {
    if members.len() < TILE_MIN {
        return Ok(vec![members.to_vec()]);
    }
    let mut order: Vec<(i64, i64)> = Vec::new();
    let mut cells: HashMap<(i64, i64), Vec<usize>> = HashMap::new();
    for &k in members {
        let c = cell(tag, &elems[k].at)?;
        cells
            .entry(c)
            .or_insert_with(|| {
                order.push(c);
                Vec::new()
            })
            .push(k);
    }
    Ok(order
        .into_iter()
        .map(|c| cells.remove(&c).unwrap_or_default())
        .collect())
}

struct Elem {
    start: usize,
    end: usize,
    tag: String,
    at: Attrs,
}

/// The style key of a mergeable element: its tag and every attribute but its coordinates, sorted.
fn style_key(tag: &str, cs: &[&str], at: &Attrs) -> String {
    let mut pairs: Vec<&(String, String)> = at
        .iter()
        .filter(|(k, _)| !cs.contains(&k.as_str()))
        .collect();
    pairs.sort();
    let body: Vec<String> = pairs.iter().map(|(k, v)| format!("{k}={v}")).collect();
    format!("{tag}\0{}", body.join(" "))
}

/// What each merged element becomes (`merge_primitives`' second half): a bucket's first member its paths, one per run, the style its
/// first member's attributes but its coordinates (a line's fill `none` where it names none); its other members nothing.
fn replacements(buckets: &[Bucket], elems: &[Elem]) -> Result<HashMap<usize, String>, Error> {
    let mut repl: HashMap<usize, String> = HashMap::new();
    for b in buckets {
        if b.members.len() < 2 {
            continue;
        }
        let cs = coords(&b.tag).unwrap_or_default();
        let style: Vec<&(String, String)> = elems[b.members[0]]
            .at
            .iter()
            .filter(|(k, _)| !cs.contains(&k.as_str()))
            .collect();
        let body: Vec<String> = style.iter().map(|(k, v)| format!("{k}=\"{v}\"")).collect();
        let mut tail = if body.is_empty() {
            String::new()
        } else {
            format!(" {}", body.join(" "))
        };
        if b.tag == "line" && !style.iter().any(|(k, _)| k == "fill") {
            tail += " fill=\"none\"";
        }
        let mut path = String::new();
        for run in tiles(&b.tag, &b.members, elems)? {
            let d: Result<Vec<String>, Error> =
                run.iter().map(|&k| sub(&b.tag, &elems[k].at)).collect();
            let _ = write!(path, "<path d=\"{}\"{tail}/>", d?.concat());
        }
        repl.insert(b.members[0], path);
        for &k in &b.members[1..] {
            repl.insert(k, String::new());
        }
    }
    Ok(repl)
}

/// The merged string (`page.merge_primitives`): runs of same-styled lines, circles or ellipses gathered into one `<path>` wherever the
/// reorder is invisible, a big bucket one path per cell.
///
/// # Errors
/// A number the Python's `float()`, `int()` or `math.floor` refused, or a merged element missing a coordinate (its `KeyError`).
pub fn merge_primitives(s: &str) -> Result<String, Error> {
    if s.matches("/>").count() < 2 {
        return Ok(s.to_owned());
    }
    let elems: Vec<Elem> = ELEM
        .captures_iter(s)
        .flatten()
        .map(|c| {
            let whole = c.get(0).map_or(0..0, |m| m.range());
            Elem {
                start: whole.start,
                end: whole.end,
                tag: c[1].to_owned(),
                at: attrs(&c[2]),
            }
        })
        .collect();
    if elems.len() < 2 {
        return Ok(s.to_owned());
    }
    // one open bucket per style (feature 153 measured several open buckets at no gain); `keys` holds each style's position in the dict
    let mut buckets: Vec<Bucket> = Vec::new();
    let mut open: Vec<(String, usize)> = Vec::new();
    for (idx, e) in elems.iter().enumerate() {
        let ext = extent(&e.tag, &e.at)?;
        let joined = match coords(&e.tag) {
            None => None,
            Some(cs) => {
                let k = style_key(&e.tag, cs, &e.at);
                let slot = open.iter().position(|(n, _)| *n == k);
                let got = slot.map(|p| open[p].1);
                let take = match got {
                    Some(b) => !buckets[b].refused(ext)?,
                    None => false,
                };
                if let (true, Some(b)) = (take, got) {
                    buckets[b].members.push(idx);
                    buckets[b].file(ext)?;
                    Some(b)
                } else {
                    let mut b = Bucket {
                        members: vec![idx],
                        skip: 0,
                        blocked: false,
                        tag: e.tag.clone(),
                        translucent: translucent(&e.at)?,
                        outlined: outlined(&e.tag, &e.at),
                        ext_grid: BoxGrid::default(),
                        ext_none: false,
                        skip_grid: BoxGrid::default(),
                    };
                    b.file(ext)?;
                    buckets.push(b);
                    let at = buckets.len() - 1;
                    match slot {
                        Some(p) => open[p].1 = at,
                        None => open.push((k, at)),
                    }
                    Some(at)
                }
            }
        };
        for &(_, b) in &open {
            let other = &mut buckets[b];
            if Some(b) == joined || other.blocked {
                continue; // a blocked bucket never reads its skips again (feature 278)
            }
            other.skip += 1;
            match ext {
                Some(x) if other.skip <= SKIP_CAP => other.skip_grid.add(x)?,
                _ => other.blocked = true,
            }
        }
    }
    let repl = replacements(&buckets, &elems)?;
    if repl.is_empty() {
        return Ok(s.to_owned());
    }
    let mut out = String::with_capacity(s.len());
    let mut at = 0;
    for (idx, e) in elems.iter().enumerate() {
        out += &s[at..e.start];
        out += repl.get(&idx).map_or(&s[e.start..e.end], String::as_str);
        at = e.end;
    }
    out += &s[at..];
    Ok(out)
}

#[cfg(test)]
mod tests;
