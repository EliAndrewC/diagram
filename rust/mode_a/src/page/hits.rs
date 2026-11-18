//! What takes the pointer on the page (`page.py`'s hit copies, regions and layer, features 134, 153, 298; ported by feature 449 T150):
//! fat invisible copies of thin marks, a scatter's recorded footprint as an invisible region, and the layer of lifted boxes clipped clear
//! of every recorded structure.
//!
//! Research:
//!     the page's hit geometry - NONE: invisible copies and regions that only move the pointer, each sizing a CONVENTION claimed beside it

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::html_text::escape;
use serde_json::Value;

use super::value::{float_of, items, unpack2};
use crate::py::{fixed, max};
use crate::tags::{ClsTag, Key};

/// Per thin class, its FAT INVISIBLE HIT COPY: (stroke factor, stroke floor px, bead radius factor) - the GM, 2026-08-28: "very thin and
/// hard for me to move my mouse over very precisely"; testing the first cut, the bund and bean boxes "about twice as wide", the channels
/// and the stream could "stand to widen", the lanes "seem fine".
///
/// Research: the thin marks' hit widths - CONVENTION: the widening each thin class's invisible hit copy takes, tuned by the GM by hand on 2026-08-28; it changes what the pointer finds, never what is drawn
pub const HIT_WIDEN: [(&str, (f64, f64, f64)); 7] = [
    ("bund", (8.0, 12.0, 6.0)),
    ("bund beans", (8.0, 12.0, 6.0)),
    ("irrigation ditch", (6.0, 9.0, 4.5)),
    ("drainage ditch", (6.0, 9.0, 4.5)),
    ("pond canal", (6.0, 9.0, 4.5)),
    ("stream", (1.5, 12.0, 4.5)),
    ("village lane", (4.0, 6.0, 3.0)),
];

/// WHOSE BOX RIDES ABOVE THE INK instead of inside its own class group (feature 153): only a mark that cannot be hit any other way. EMPTY
/// SINCE FEATURE 280 - the pond sluice it was built for is retired - and the mechanism stays, tested on a stand-in ([`hit_layer_with`]).
///
/// Research: the lifted boxes - CONVENTION: no class's hit box is lifted above the ink today; lifting every box was tried and blanketed the map (feature 153)
pub const HIT_ON_TOP: [&str; 0] = [];

/// Among the lifted ones, hardest-to-hit last (it wins); a lifted class the list forgets sorts last.
///
/// Research: the lifted boxes' order - CONVENTION: the order a lifted box wins in, hardest to hit last
pub const HIT_PRIORITY: [&str; 7] = [
    "stream",
    "village lane",
    "bund",
    "bund beans",
    "irrigation ditch",
    "drainage ditch",
    "pond canal",
];

/// THE STRUCTURES A LIFTED BOX MUST NOT SWALLOW: each a rect in the manifest, held clear as a hole of the layer's clip (feature 153: the
/// sluice box took 88.4% of a pig sty's own footprint). Every key listed records `x/y/w/h`.
///
/// Research: the keep-clear structures - CONVENTION: a lifted hit box may beat open ground and area fills, never another feature's drawn glyph
pub const HIT_KEEP_CLEAR: [&str; 7] = [
    "houses",
    "byres",
    "farm_sheds",
    "retirement_houses",
    "farm_fixtures",
    "pig_sties",
    "kosatsuba",
];

/// Which recorded footprints become HIT REGIONS, by class (the GM, 2026-08-28: "moving my mouse over the scrublands is surprisingly
/// difficult because I need my mouse to be over one of these specific trees or little lines").
///
/// Research: the scatter's hit regions - CONVENTION: a scatter feature takes the pointer over its recorded footprint wherever nothing drawn above it does
pub const HIT_REGIONS: [(&str, &[(&str, &str)]); 4] = [
    (
        "commons",
        &[
            ("grazing", "scrub and rough grazing"),
            ("commons", "scrub and rough grazing"),
            ("woodland", "woodland commons"),
        ],
    ),
    ("marshes", &[("*", "marsh")]),
    (
        "village_groves",
        &[("windbreak", "windbreak"), ("copse", "copse")],
    ),
    (
        "bamboo_stands",
        &[
            ("homestead", "homestead bamboo"),
            ("*", "shared bamboo grove"),
        ],
    ),
];

/// The default widening, its floor and a bead's radius factor (`hit_copies`' defaults; the GM's "three or four times the width").
///
/// Research: the default hit width - CONVENTION: four times the drawn width with a 6 px floor, the GM's "three or four times the width"
pub const HIT_DEFAULT: (f64, f64, f64) = (4.0, 6.0, 3.0);

static STROKE_W: LazyLock<Regex> = LazyLock::new(|| py(r#"stroke-width="([\d.]+)""#));
static GROUP_W: LazyLock<Regex> = LazyLock::new(|| py(r#"<g [^>]*stroke-width="([\d.]+)""#));
static STROKED: LazyLock<Regex> = LazyLock::new(|| py(r"<(line|path|polygon|polyline) ([^>]*?)/>"));
static GEOM: LazyLock<Regex> = LazyLock::new(|| py(r#"(?:points|d|x1|y1|x2|y2)="[^"]*""#));
static BEAD: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<circle cx="([-\d.]+)" cy="([-\d.]+)" r="([-\d.]+)"[^>]*/>"#));
pub(super) static ATTR_STROKE: LazyLock<Regex> = LazyLock::new(|| py(r#"\sstroke="[^"]*""#));
pub(super) static ATTR_FILL: LazyLock<Regex> = LazyLock::new(|| py(r#"\sfill="[^"]*""#));

/// The widening of `key`, when it is a thin class.
#[must_use]
pub fn widen(key: &str) -> Option<(f64, f64, f64)> {
    HIT_WIDEN.iter().find(|(k, _)| *k == key).map(|(_, w)| *w)
}

/// The fat invisible copies of every stroked mark and every bead in one classed string (`page.hit_copies`).
///
/// # Errors
/// A stroke width or radius the Python's `float()` refused (`[\d.]+` takes `1.2.3`).
///
/// Research: the thin marks' hit copies - CONVENTION: a stroked mark's invisible copy its factor times its drawn width with a floor, a bead's its radius times its factor; a filled shape takes the pointer over its own body
pub fn hit_copies(s: &str, (factor, floor, bead): (f64, f64, f64)) -> Result<String, Error> {
    let width = |w: f64| max(factor * w, floor);
    let mut out = String::new();
    let default_w = match GROUP_W.captures(s).ok().flatten() {
        Some(c) => crate::py::float(&c[1])?,
        None => 1.0,
    };
    for c in STROKED.captures_iter(s).flatten() {
        let (tag, attrs) = (&c[1], &c[2]);
        let open_fill = !attrs.contains("fill=\"none\"");
        if (tag == "polygon" || tag == "polyline") && open_fill {
            continue; // a filled shape already takes the pointer over its whole body
        }
        if tag == "path" && open_fill && !attrs.contains("stroke") {
            continue;
        }
        let w = match STROKE_W.captures(attrs).ok().flatten() {
            Some(m) => crate::py::float(&m[1])?,
            None => default_w,
        };
        let geom: Vec<&str> = GEOM
            .find_iter(attrs)
            .flatten()
            .map(|m| m.as_str())
            .collect();
        let _ = write!(
            out,
            "<{tag} {} fill=\"none\" class=\"hit\" style=\"pointer-events: stroke; stroke-width: {}px\"/>",
            geom.join(" "),
            fixed(width(w), 1)
        );
    }
    for c in BEAD.captures_iter(s).flatten() {
        let r = crate::py::float(&c[3])?;
        let _ = write!(
            out,
            "<circle cx=\"{}\" cy=\"{}\" r=\"{}\" fill=\"none\" class=\"hit\" style=\"pointer-events: fill\"/>",
            &c[1],
            &c[2],
            fixed(max(bead * r, floor / 2.0), 1)
        );
    }
    Ok(out)
}

/// A class group's opening tag (`page._open`); `planted` adds the token that keeps a feature's greenery legible while it is lit.
#[must_use]
pub fn open(key: &str, planted: bool) -> String {
    format!(
        "<g class=\"f f-{}{}\" data-k=\"{}\">",
        l7r_gate_registry::about::slug(key),
        if planted { " planted" } else { "" },
        escape(key, true)
    )
}

/// The widened copies that stay INSIDE their class group - every widened class but the lifted ones (`page._inline_hits`).
fn inline_hits(s: &str, key: &str) -> Result<String, Error> {
    match widen(key) {
        Some(w) if !HIT_ON_TOP.contains(&key) => hit_copies(s, w),
        _ => Ok(String::new()),
    }
}

/// The HTML form of one drawn string (`page.wrap`): unchanged when unclassed or ruled out; inside its class group when classed; a fill
/// copy and a stroke copy for a `Split`; piece by piece for `Parts`.
///
/// # Errors
/// The merge's or the hit copies' refusal.
///
/// Research: a class's group - CONVENTION: a split element lights its fill and its stroke apart (spec US3), a planting keeps its greenery legible when lit (feature 153)
pub fn wrap(s: &str, tag: &ClsTag) -> Result<String, Error> {
    if tag.is_ruled_out() || s.is_empty() {
        return Ok(s.to_owned());
    }
    match tag {
        ClsTag::Key(Key { name, planted }) => Ok(open(name, *planted)
            + &super::merge::merge_primitives(s)?
            + &inline_hits(s, name)?
            + "</g>"),
        ClsTag::Split { fill, stroke } => {
            let fill_copy = ATTR_STROKE.replace_all(s, " stroke=\"none\"");
            let stroke_copy = ATTR_FILL.replace_all(s, " fill=\"none\"");
            Ok(open(fill, false)
                + &fill_copy
                + "</g>"
                + &open(stroke, false)
                + &stroke_copy
                + &inline_hits(&stroke_copy, stroke)?
                + "</g>")
        }
        ClsTag::Parts(parts) => {
            let mut out = String::new();
            for (c, piece) in parts {
                out += &match c {
                    Some(k) => wrap(piece, &ClsTag::Key(k.clone()))?,
                    None => piece.clone(),
                };
            }
            Ok(out)
        }
        ClsTag::Unruled => Ok(s.to_owned()),
    }
}

/// A wrapped string that is a PART of other kinds carries them as `data-in` AFTER `data-k` (`page.part_of`, feature 264): the id map
/// finds a group by `class` then `data-k`, and a part whose `data-in` came between them was named as its parent.
///
/// # Errors
/// An opening that never closes (the Python's `str.index` refusal; a group [`wrap`] opened always closes).
///
/// Research: a part lights with its parent - CONVENTION: the kinds a piece is part of ride as `data-in` after `data-k` (feature 264)
pub fn part_of(wrapped: &str, kinds: &[String]) -> Result<String, Error> {
    if kinds.is_empty() || !wrapped.starts_with("<g class=\"f ") {
        return Ok(wrapped.to_owned());
    }
    let Some(end) = wrapped.find('>') else {
        return Err(Error::new("ValueError", "substring not found"));
    };
    Ok(format!(
        "{} data-in=\"{}\"{}",
        &wrapped[..end],
        escape(&kinds.join("|"), true),
        &wrapped[end..]
    ))
}

/// Invisible footprint polygons for the scatter classes present (`page.hit_regions`), at the bottom of the stack: `fill="none"` with
/// `pointer-events: fill` hit-tests the area without painting it. A cover's record carries the shape its tile fills (feature 298), holes
/// and all.
///
/// # Errors
/// A ring's point that is not a pair of numbers, as the Python's unpacking or `float()` refused it.
///
/// Research: the scatter's hit regions - CONVENTION: a recorded footprint, or its cover's own shape with its holes (feature 298), takes the pointer at the bottom of the stack
pub fn hit_regions(
    manifest: Option<&Value>,
    present: &std::collections::BTreeSet<String>,
) -> Result<String, Error> {
    let Some(manifest) = manifest.filter(|m| l7r_guard::shared::pyjson::truthy(m)) else {
        return Ok(String::new());
    };
    let mut out = String::new();
    for (key, roles) in HIT_REGIONS {
        let role_of = |r: &str| roles.iter().find(|(k, _)| *k == r).map(|(_, c)| *c);
        for rec in items(manifest.get(key))? {
            let Value::Object(rec) = &rec else { continue };
            if !rec
                .get("poly")
                .is_some_and(l7r_guard::shared::pyjson::truthy)
            {
                continue;
            }
            let role = rec
                .get("role")
                .map_or_else(|| "*".to_owned(), l7r_guard::shared::pyjson::py_str);
            let Some(cls) = role_of(&role).or_else(|| role_of("*")) else {
                continue;
            };
            if !present.contains(cls) {
                continue;
            }
            let rings = if rec.contains_key("cover") || cls == "scrub and rough grazing" {
                rec.get("cover").cloned().unwrap_or(Value::Null)
            } else {
                Value::Array(vec![rec["poly"].clone()])
            };
            if !l7r_guard::shared::pyjson::truthy(&rings) {
                continue;
            }
            let mut d = String::new();
            for ring in items(Some(&rings))? {
                let mut pts = Vec::new();
                for p in items(Some(&ring))? {
                    let (x, y) = unpack2(&p)?;
                    pts.push(format!(
                        "{},{}",
                        fixed(float_of(&x)?, 1),
                        fixed(float_of(&y)?, 1)
                    ));
                }
                let _ = write!(d, "M{}Z", pts.join("L"));
            }
            let _ = write!(
                out,
                "{}<path class=\"hit\" d=\"{d}\" fill-rule=\"evenodd\" fill=\"none\" style=\"pointer-events: fill\"/></g>",
                open(cls, false)
            );
        }
    }
    Ok(out)
}

/// (class, the ink a widened copy is taken from) for one drawn string (`page._hit_pieces`): a `Split` widens its STROKE class only.
fn hit_pieces(s: &str, tag: &ClsTag, out: &mut Vec<(String, String)>) {
    match tag {
        ClsTag::Key(k) => out.push((k.name.clone(), s.to_owned())),
        ClsTag::Split { stroke, .. } => {
            out.push((
                stroke.clone(),
                ATTR_FILL.replace_all(s, " fill=\"none\"").into_owned(),
            ));
        }
        ClsTag::Parts(parts) => {
            for (c, piece) in parts {
                if let Some(k) = c {
                    out.push((k.name.clone(), piece.clone()));
                }
            }
        }
        ClsTag::Unruled => {}
    }
}

/// Every widened hit copy of a lifted class in ONE layer, thinnest-drawn class last (`page.hit_layer`), clipped clear of the recorded
/// structures; `on_top` the lifted classes ([`HIT_ON_TOP`] on a page).
///
/// # Errors
/// The hit copies' refusal, or the clip's.
///
/// Research: the lifted boxes' layer - CONVENTION: one layer above the ink, hardest-to-hit last, clipped clear of every recorded structure (feature 153)
pub fn hit_layer_with(
    strings: &[String],
    tags: &[ClsTag],
    manifest: Option<&Value>,
    on_top: &[&str],
) -> Result<String, Error> {
    let mut per: Vec<(String, Vec<String>)> = Vec::new();
    for (s, tag) in strings.iter().zip(tags) {
        let mut pieces = Vec::new();
        hit_pieces(s, tag, &mut pieces);
        for (key, piece) in pieces {
            let Some(w) = widen(&key).filter(|_| on_top.contains(&key.as_str())) else {
                continue;
            };
            let copies = hit_copies(&piece, w)?;
            if copies.is_empty() {
                continue;
            }
            match per.iter_mut().find(|(k, _)| *k == key) {
                Some((_, list)) => list.push(copies),
                None => per.push((key, vec![copies])),
            }
        }
    }
    let rank = |k: &str| {
        HIT_PRIORITY
            .iter()
            .position(|p| *p == k)
            .unwrap_or(HIT_PRIORITY.len())
    };
    per.sort_by(|(a, _), (b, _)| (rank(a), a).cmp(&(rank(b), b)));
    let (clip, attr) = keep_clear_clip(manifest)?;
    let mut out = clip;
    for (k, copies) in per {
        let g = open(&k, false);
        let _ = write!(out, "{}{attr}>{}</g>", &g[..g.len() - 1], copies.concat());
    }
    Ok(out)
}

/// [`hit_layer_with`] the page's own lifted classes.
///
/// # Errors
/// As [`hit_layer_with`].
pub fn hit_layer(
    strings: &[String],
    tags: &[ClsTag],
    manifest: Option<&Value>,
) -> Result<String, Error> {
    hit_layer_with(strings, tags, manifest, &HIT_ON_TOP)
}

/// A record's `x`, `y`, `w`, `h` and rotation, or none where the Python's `try` skipped it.
fn footprint(rec: &serde_json::Map<String, Value>) -> Option<[f64; 5]> {
    let f = |k: &str| rec.get(k).and_then(|v| float_of(v).ok());
    let rot = match rec.get("rot") {
        Some(v) if l7r_guard::shared::pyjson::truthy(v) => float_of(v).ok()?,
        _ => 0.0,
    };
    Some([f("x")?, f("y")?, f("w")?, f("h")?, rot.to_radians()])
}

/// (the clipPath, the attribute that applies it): the map less every recorded structure footprint (`page._keep_clear_clip`), each hole the
/// axis-aligned box of its rotated footprint padded by the tenth of a pixel the coordinates are rounded to, and any record's `poly` held
/// clear too.
///
/// # Errors
/// A `poly` point that is not a pair of numbers, as the Python's indexing or `float()` refused it.
///
/// Research: the keep-clear clip - CONVENTION: each structure's rotated box padded by the tenth of a pixel its coordinates are rounded to, and any polygon its record carries, held clear of a lifted box
pub fn keep_clear_clip(manifest: Option<&Value>) -> Result<(String, String), Error> {
    let mut holes: Vec<String> = Vec::new();
    for key in HIT_KEEP_CLEAR {
        for rec in items(manifest.and_then(|m| m.get(key)))? {
            let Value::Object(rec) = &rec else { continue };
            let Some([x, y, w, h, rot]) = footprint(rec) else {
                continue;
            };
            let bw = (w * rot.cos()).abs() + (h * rot.sin()).abs() + 0.2;
            let bh = (w * rot.sin()).abs() + (h * rot.cos()).abs() + 0.2;
            holes.push(format!(
                "M{},{}h{}v{}h{}Z",
                fixed(x - bw / 2.0, 1),
                fixed(y - bh / 2.0, 1),
                fixed(bw, 1),
                fixed(bh, 1),
                fixed(-bw, 1)
            ));
            if let Some(Value::Array(pts)) = rec.get("poly") {
                if pts.len() > 2 {
                    let coord = |i: usize| -> Result<Vec<f64>, Error> {
                        pts.iter()
                            .map(|q| super::value::index(q, i).and_then(|v| float_of(&v)))
                            .collect()
                    };
                    let (xs, ys) = (coord(0)?, coord(1)?);
                    let (x0, x1) = super::value::span(&xs);
                    let (y0, y1) = super::value::span(&ys);
                    let (ew, eh) = (x1 - x0 + 0.2, y1 - y0 + 0.2);
                    holes.push(format!(
                        "M{},{}h{}v{}h{}Z",
                        fixed(x0 - 0.1, 1),
                        fixed(y0 - 0.1, 1),
                        fixed(ew, 1),
                        fixed(eh, 1),
                        fixed(-ew, 1)
                    ));
                }
            }
        }
    }
    if holes.is_empty() {
        return Ok((String::new(), String::new()));
    }
    Ok((
        format!(
            "<clipPath id=\"hit-keep-clear\"><path clip-rule=\"evenodd\" d=\"M-99999,-99999h199998v199998h-199998Z{}\"/></clipPath>",
            holes.concat()
        ),
        " clip-path=\"url(#hit-keep-clear)\"".to_owned(),
    ))
}

#[cfg(test)]
mod tests;
