//! Two renders of a map compared: how many pixels differ, by how much, where, and on which class's ink (`tools/picture_diff.py`, feature
//! 231; ported by feature 449 T150, the engine port's step 2, and the Python deleted).
//!
//! WHY THIS EXISTS (feature 231, the GM 2026-09-12): the other half of what a settlement-review of a rendering change does by hand - on
//! feature 228 the reviewer rendered main's SVG and the clone's at full size, diffed them, and measured how far every differing pixel
//! lay from a pond outline, eight of its eighteen minutes. Two renders (a PNG, or an SVG rendered here by the engine's own `resvg` at
//! the other's width), the share of differing pixels, the largest channel delta, the bounding box, and - when the map's PAGE is given -
//! the share of differing pixels on each class's ink, read from the id map the page carries. MEASUREMENT, NEVER VERDICT (feature 193):
//! the reviewer decides whether 0.14% at the pond's edge is antialiasing or a defect. The counts and figures are the numpy statistics'
//! exactly, the same pixels counted the same way and printed in the same words.
//!
//! Research: the picture measure - NONE: a measurement for a reviewer, no map decision

use std::collections::BTreeMap;
use std::path::Path;

use l7r_gate_core::Reply;
use l7r_gate_research::Error;

use super::args::{parse, py_int, Parsed, Takes};
use super::image::{decode_idmap, palette_key_of, rgb, Key};
use crate::raster::encode::Rgb;
use crate::raster::Host;

/// A channel must move by MORE than this for a pixel to count as differing (see `page_lit`'s threshold).
pub const THRESHOLD: i64 = 6;
/// Where a differing pixel on no class's ink is counted.
pub const OFF_CLASS: &str = "off any class";

const USAGE: &str =
    "usage: l7r-mode-a picture-diff [-h] [--svg SVG] [--page PAGE] [--threshold THRESHOLD] a b\n";
const HELP: &str = "usage: l7r-mode-a picture-diff [-h] [--svg SVG] [--page PAGE] [--threshold THRESHOLD] a b\n\n\
Two renders of a map compared: how many pixels differ, by how much, where, and on which class's ink.\n\n\
positional arguments:\n  a                     the first render (.png or .svg) - main's, by convention\n  \
b                     the second render (.png or .svg) - the clone's\n\noptions:\n  -h, --help            show this help message and exit\n  \
--svg SVG             a document CARRYING class groups (a page's SVG), for the per-class attribution\n  \
--page PAGE           the map's rendered .html - its own id map answers which class each differing pixel lies on\n  \
--threshold THRESHOLD\n";

/// The statistics of two renders: pixels, differing, the largest channel delta, the bbox (inclusive) and which pixels differ.
#[derive(Debug, PartialEq, Eq)]
pub struct Stats {
    pub width: usize,
    pub pixels: usize,
    pub differing: usize,
    pub max_delta: u8,
    pub bbox: Option<(usize, usize, usize, usize)>,
    pub mask: Vec<bool>,
}

/// The largest channel delta of each pixel (`np.abs(a - b).max(axis=2)`).
#[must_use]
pub fn deltas(a: &Rgb, b: &Rgb) -> Vec<u8> {
    a.data
        .chunks(3)
        .zip(b.data.chunks(3))
        .map(|(p, q)| (0..3).map(|i| p[i].abs_diff(q[i])).max().unwrap_or(0))
        .collect()
}

/// `diff_stats`: the pixels whose largest channel delta is over `threshold`.
///
/// # Errors
/// Renders of different sizes.
pub fn diff_stats(a: &Rgb, b: &Rgb, threshold: i64) -> Result<Stats, Error> {
    if (a.width, a.height) != (b.width, b.height) {
        return Err(Error::new(
            "ValueError",
            format!(
                "the renders differ in size: ({}, {}) against ({}, {}) - render the SVG at the other's width",
                a.width, a.height, b.width, b.height
            ),
        ));
    }
    let delta = deltas(a, b);
    let mask: Vec<bool> = delta.iter().map(|&d| i64::from(d) > threshold).collect();
    let mut bbox: Option<(usize, usize, usize, usize)> = None;
    for (i, _) in mask.iter().enumerate().filter(|(_, m)| **m) {
        let (x, y) = (i % a.width, i / a.width);
        bbox = Some(bbox.map_or((x, y, x, y), |(x0, y0, x1, y1)| {
            (x0.min(x), y0.min(y), x1.max(x), y1.max(y))
        }));
    }
    Ok(Stats {
        width: a.width,
        pixels: mask.len(),
        differing: mask.iter().filter(|m| **m).count(),
        max_delta: delta.iter().copied().max().unwrap_or(0),
        bbox,
        mask,
    })
}

/// The class each `(red, green)` answers, at `red * 256 + green`: for each palette entry in order, `lut[max(0, r - 1) : min(256, r + 2)] = i`
/// with Python's slice bounds - the page answers a red value within 1 of an entry's as that class (`page.js keyAtPoint`) - and, where the
/// palette has rows past its first (more than 63 kinds), a green value within 1 of the entry's row too; on a palette of one row the green
/// channel is not read, as the Python never read it.
#[must_use]
pub fn lookup(keys: &[Key]) -> Vec<i64> {
    let mut lut = vec![-1_i64; 256 * 256];
    let rows = keys.iter().any(|(g, _)| *g != 0);
    let bound = |at: i64| {
        let at = if at < 0 { (at + 256).max(0) } else { at };
        usize::try_from(at.min(256)).unwrap_or(0)
    };
    for (i, &(g, r)) in (0_i64..).zip(keys) {
        let (start, stop) = (
            bound(0.max(r.saturating_sub(1))),
            bound(256.min(r.saturating_add(2))),
        );
        let greens = if rows {
            bound(0.max(g - 1))..bound(256.min(g + 2))
        } else {
            0..256
        };
        for red in start..stop {
            for green in greens.clone() {
                lut[red * 256 + green] = i;
            }
        }
    }
    lut
}

/// `{key: class}` with a repeated key's last class, as a Python dict keeps it, in sorted order (row, then red).
#[must_use]
pub fn sorted_palette(palette: &[(Key, String)]) -> BTreeMap<Key, String> {
    palette.iter().cloned().collect()
}

/// `(name, count)` pairs set as a dict sets them: a repeated name keeps its first place and takes the last count.
pub fn set(out: &mut Vec<(String, usize)>, name: &str, n: usize) {
    match out.iter_mut().find(|(k, _)| k == name) {
        Some(slot) => slot.1 = n,
        None => out.push((name.to_owned(), n)),
    }
}

/// `by_class`: the differing pixels on each class's ink, a picture pixel read at its map coordinate (`scale` picture px per map px), the
/// rest under [`OFF_CLASS`].
#[must_use]
pub fn by_class(
    stats: &Stats,
    (red, green): (&[u8], &[u8]),
    cols: usize,
    palette: &BTreeMap<Key, String>,
    scale: f64,
) -> Vec<(String, usize)> {
    let rows = red.len().checked_div(cols).unwrap_or(0);
    let keys: Vec<Key> = palette.keys().copied().collect();
    let lut = lookup(&keys);
    let mut counts = vec![0_usize; keys.len()];
    let mut off = 0;
    for (i, _) in stats.mask.iter().enumerate().filter(|(_, m)| **m) {
        let (x, y) = (i % stats.width, i / stats.width);
        let at = |v: usize| (super::f(v) / scale).floor();
        let (mx, my) = (at(x), at(y));
        let inside = mx < super::f(cols) && my < super::f(rows);
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "inside the id map: a whole, non-negative index"
        )]
        let class = if inside {
            let at = my as usize * cols + mx as usize;
            lut[usize::from(red[at]) * 256 + usize::from(green[at])]
        } else {
            -1
        };
        match usize::try_from(class) {
            Ok(c) => counts[c] += 1,
            Err(_) => off += 1,
        }
    }
    let mut out = Vec::new();
    for (k, n) in palette.values().zip(&counts) {
        set(&mut out, k, *n);
    }
    out.retain(|(_, n)| *n > 0);
    set(&mut out, OFF_CLASS, off);
    out
}

/// The report's lines (`report`).
#[must_use]
pub fn report(stats: &Stats, classes: Option<&[(String, usize)]>) -> String {
    let share = super::f(stats.differing) / super::f(stats.pixels);
    let bbox = stats.bbox.map_or_else(
        || "none (identical)".to_owned(),
        |(a, b, c, d)| format!("({a}, {b}, {c}, {d})"),
    );
    let mut lines = vec![
        format!(
            "differing: {} of {} px = {:.3}%   max channel delta: {}/255",
            stats.differing,
            stats.pixels,
            100.0 * share,
            stats.max_delta
        ),
        format!("bbox: {bbox}"),
    ];
    if let Some(classes) = classes.filter(|c| !c.is_empty()) {
        let total = stats.differing.max(1);
        lines.push("on the ink of:".to_owned());
        let mut sorted: Vec<&(String, usize)> = classes.iter().collect();
        sorted.sort_by(|a, b| b.1.cmp(&a.1));
        for (k, n) in sorted {
            lines.push(format!(
                "{:7.1}%  {n:>9}  {k}",
                super::f(100 * n) / super::f(total)
            ));
        }
    }
    lines.join("\n")
}

/// `load`: a PNG as it is; an SVG rendered by resvg at `width` px (at 1 px per map px when none), with the page's font mapping.
///
/// # Errors
/// The file unreadable or no image, or the render's own failure.
pub fn load(host: &Host, path: &str, width: Option<usize>) -> Result<Rgb, Error> {
    if !is_svg(path) {
        let bytes = std::fs::read(path).map_err(|e| crate::py::os_error(&e, path))?;
        return rgb(&bytes, path);
    }
    let text = l7r_gate_core::record::read_text(Path::new(path))
        .map_err(|e| crate::py::os_error(&e, path))?;
    let mut args: Vec<String> = match width.filter(|w| *w > 0) {
        Some(w) => vec!["--width".into(), w.to_string()],
        None => vec!["--zoom".into(), "1".into()],
    };
    args.extend(crate::raster::RESVG_FONT_ARGS.map(str::to_owned));
    // (the Python's refusal where resvg was not installed has no case left: the renderer is the crate, feature 449 T150)
    rgb(&host.resvg_png(&text, &args)?, path)
}

/// The Python's `path.endswith(".svg")`: a `.SVG` was read as an image, not rendered.
#[expect(
    clippy::case_sensitive_file_extension_comparisons,
    reason = "the Python's own test, case and all"
)]
fn is_svg(path: &str) -> bool {
    path.ends_with(".svg")
}

/// An id map read for the attribution: its red and green channels, its width and its palette.
type Ids = (Vec<u8>, Vec<u8>, usize, BTreeMap<Key, String>);

/// The id map of a document carrying class groups (`id_map_of`): none where it carries no class group.
fn id_map_of(host: &Host, svg_text: &str) -> Result<Option<Ids>, Error> {
    let keys = crate::raster::class_keys(svg_text);
    if keys.is_empty() {
        return Ok(None);
    }
    let (png, palette) = crate::raster::id_map(host, svg_text, &keys, false)?;
    let image = rgb(&png, "<the id map>")?;
    let mut values = Vec::new();
    for (k, v) in palette {
        values.push((palette_key_of(&k)?, v));
    }
    Ok(Some((
        image.data.iter().step_by(3).copied().collect(),
        image.data.iter().skip(1).step_by(3).copied().collect(),
        image.width,
        sorted_palette(&values),
    )))
}

/// The measure the arguments ask for: its report, or the Python's refusal.
fn measure(
    host: &Host,
    a: &str,
    b: &str,
    svg: Option<&str>,
    page: Option<&str>,
    threshold: i64,
) -> Result<String, Error> {
    // a PNG fixes the size; an SVG is rendered at the other's width, or at 1 px per map px when both are SVGs
    let (first, second) = if is_svg(a) { (b, a) } else { (a, b) };
    let one = load(host, first, None)?;
    let two = load(host, second, is_svg(second).then_some(one.width))?;
    let stats = diff_stats(&one, &two, threshold)?;
    let mut classes = None;
    if let Some(source) = page.or(svg).filter(|_| stats.differing > 0) {
        let text = l7r_gate_core::record::read_text(Path::new(source))
            .map_err(|e| crate::py::os_error(&e, source))?;
        let ids = if page.is_some() {
            decode_idmap(&text)?.map(|m| (m.red, m.green, m.width, sorted_palette(&m.palette)))
        } else {
            id_map_of(host, &text)?
        };
        if let Some((red, green, cols, palette)) = ids {
            classes = Some(by_class(
                &stats,
                (&red, &green),
                cols,
                &palette,
                super::f(one.width) / super::f(cols),
            ));
        }
    }
    Ok(report(&stats, classes.as_deref()) + "\n")
}

/// `make picture-diff`: the command line read as the Python's argparse read it, and the measure.
#[must_use]
pub fn main(args: &[String], host: &Host) -> Reply {
    let opts = [
        ("svg", Takes::Value),
        ("page", Takes::Value),
        ("threshold", Takes::Int),
    ];
    let parsed = match parse(args, &opts) {
        Ok(Parsed::Help) => return super::reply(HELP.to_owned(), "", 0),
        Ok(Parsed::Run {
            positionals,
            options,
        }) if positionals.len() == 2 => (positionals, options),
        Ok(Parsed::Run { .. }) => {
            return super::usage(
                USAGE,
                "picture-diff",
                "the arguments a and b are required, and no more",
            )
        }
        Err(e) => return super::usage(USAGE, "picture-diff", &e),
    };
    let (pos, options) = parsed;
    // an empty `--page` or `--svg` is no source, as the Python's `args.page or args.svg` reads it
    let get = |n: &str| {
        options
            .iter()
            .find(|(k, _)| *k == n)
            .map(|(_, v)| v.as_str())
            .filter(|v| !v.is_empty())
    };
    let threshold = options
        .iter()
        .find(|(k, _)| *k == "threshold")
        .map_or(Ok(THRESHOLD), |(_, v)| py_int(v))
        .unwrap_or(THRESHOLD);
    super::answer(measure(
        host,
        &pos[0],
        &pos[1],
        get("svg"),
        get("page"),
        threshold,
    ))
}

#[cfg(test)]
mod tests;
