//! Light one class on a map's page and report which classes' pixels change - the reviewer's page measurement (`tools/page_lit.py`,
//! feature 231; ported by feature 449 T150, the engine port's step 2, and the Python deleted).
//!
//! WHY THIS EXISTS (feature 231, the GM 2026-09-12: *"there's no reason to need to write a scratch script to do pixel checks every single
//! time ... think about what that reviewer pass is actually doing and what tools it needs, and then give it those tools"*): for a class
//! lit on the page, what share of every OTHER class's pixels changes? The page knows which class every map pixel belongs to - its class
//! id map, carried in its payload with its palette - and exposes `window.l7rMap.highlight`, so the measure is a screenshot before and
//! after lighting, each screen pixel attributed through the SVG's screen transform to the class the id map answers there. The browser
//! half is `l7r-browser lit` (`rust/browser/src/lit.rs`), run as a program through the tree's launcher, as the gate's archive runs it;
//! the attribution and the report are here, the numpy arithmetic's exactly. MEASUREMENT, NEVER VERDICT (feature 193).
//!
//! Research: the page measure - NONE: a measurement for a reviewer, no map decision

use std::collections::BTreeMap;
use std::path::{Path, PathBuf};

use l7r_gate_core::Reply;
use l7r_gate_research::Error;
use serde_json::Value;

use super::args::{parse, Parsed, Takes};
use super::image::{decode_idmap, rgb, IdMap, Key};
use super::picture_diff::{deltas, lookup, sorted_palette, THRESHOLD};
use crate::raster::encode::Rgb;

const USAGE: &str = "usage: l7r-mode-a page-lit [-h] [--vector] [--out OUT] page key\n";
const HELP: &str = "usage: l7r-mode-a page-lit [-h] [--vector] [--out OUT] page key\n\n\
Light one class on a map's page and report which classes' pixels change - the reviewer's page measurement.\n\n\
positional arguments:\n  page        the map's .html\n  key         the class to light, e.g. 'mulberry dike'\n\noptions:\n  \
-h, --help  show this help message and exit\n  --vector    zoom past the raster switch first\n  --out OUT   save the lit screenshot here\n";

/// What the browser answered: the page's mode and zoom, the map's screen transform and viewBox, and the two screenshots.
pub struct Shot {
    pub mode: Value,
    pub zoom: Value,
    pub ctm: Value,
    pub viewbox: Value,
    pub before: Vec<u8>,
    pub after: Vec<u8>,
}

/// A JSON number as Python's `float()` takes it.
fn number(v: &Value, what: &str) -> Result<f64, Error> {
    v.as_f64().ok_or_else(|| {
        Error::new(
            "TypeError",
            format!(
                "float() argument must be a string or a real number, not '{}' ({what})",
                crate::py::type_name(v)
            ),
        )
    })
}

/// The `n` numbers of a JSON list, unpacked as the Python unpacked them.
fn numbers(v: &Value, n: usize, what: &str) -> Result<Vec<f64>, Error> {
    let items = v.as_array().map(Vec::as_slice).unwrap_or_default();
    if items.len() != n {
        return Err(Error::new(
            "ValueError",
            format!("{what}: expected {n} values to unpack, got {}", items.len()),
        ));
    }
    items.iter().map(|x| number(x, what)).collect()
}

/// A class and its (changed pixels, on-screen pixels).
pub type Share = (String, (usize, usize));

/// `{class: (changed pixels, on-screen pixels)}` for a screenshot pair (`attribute`): each screen pixel's center carried to map
/// coordinates through the inverse of the screen transform, shifted by the viewBox's origin and scaled by the id map's pixels per user
/// unit (feature 200 crops the viewBox, so the id map IS the viewBox), and answered by the id map as the page answers the pointer. Each
/// operation in numpy's order, nothing fused.
///
/// # Errors
/// Screenshots of different sizes, or a transform or viewBox that is not numbers.
#[expect(
    clippy::many_single_char_names,
    reason = "the screen transform's own names, a to f, as `getScreenCTM` and the Python name them"
)]
pub fn attribute(
    before: &Rgb,
    after: &Rgb,
    map: &IdMap,
    ctm: &Value,
    viewbox: &Value,
) -> Result<Vec<Share>, Error> {
    if (before.width, before.height) != (after.width, after.height) {
        return Err(Error::new(
            "ValueError",
            "operands could not be broadcast together",
        ));
    }
    let changed: Vec<bool> = deltas(before, after)
        .iter()
        .map(|&d| i64::from(d) > THRESHOLD)
        .collect();
    let m = numbers(ctm, 6, "the screen transform")?;
    let (a, b, c, d, e, f) = (m[0], m[1], m[2], m[3], m[4], m[5]);
    let det = a * d - b * c;
    let (rows, cols) = (map.height, map.width);
    let (vx, vy, vw, vh) = if viewbox.is_null() {
        (0.0, 0.0, super::f(cols), super::f(rows))
    } else {
        let v = numbers(viewbox, 4, "the viewBox")?;
        (v[0], v[1], v[2], v[3])
    };
    let (kx, ky) = (super::f(cols) / vw, super::f(rows) / vh);
    let palette: BTreeMap<Key, String> = sorted_palette(&map.palette);
    let keys: Vec<Key> = palette.keys().copied().collect();
    let lut = lookup(&keys);
    let mut counts = vec![(0_usize, 0_usize); keys.len()];
    let w = before.width;
    for (i, lit) in changed.iter().enumerate() {
        let (sx, sy) = (super::f(i % w) + 0.5, super::f(i / w) + 0.5);
        let ux = ((sx - e) * d - (sy - f) * c) / det;
        let uy = ((sy - f) * a - (sx - e) * b) / det;
        let (mx, my) = (((ux - vx) * kx).floor(), ((uy - vy) * ky).floor());
        // numpy casts a non-finite float to the most negative int64 - off the map; `as` would make NaN 0, on it
        if !(mx.is_finite()
            && my.is_finite()
            && mx >= 0.0
            && my >= 0.0
            && mx < super::f(cols)
            && my < super::f(rows))
        {
            continue;
        }
        #[expect(
            clippy::cast_possible_truncation,
            clippy::cast_sign_loss,
            reason = "inside the id map: a whole, non-negative index"
        )]
        let at = my as usize * cols + mx as usize;
        let class = lut[usize::from(map.red[at]) * 256 + usize::from(map.green[at])];
        if let Ok(k) = usize::try_from(class) {
            counts[k].1 += 1;
            counts[k].0 += usize::from(*lit);
        }
    }
    let mut out: Vec<(String, (usize, usize))> = Vec::new();
    for (k, n) in palette.values().zip(counts) {
        match out.iter_mut().find(|(name, _)| name == k) {
            Some(slot) => slot.1 = n,
            None => out.push((k.clone(), n)),
        }
    }
    Ok(out)
}

/// The shares, largest first; the lit class is what should sit at the top (`report`).
///
/// # Errors
/// A zoom that is no number.
pub fn report(
    key: &str,
    mode: &Value,
    zoom: &Value,
    classes: &[(String, (usize, usize))],
) -> Result<String, Error> {
    let mode = mode
        .as_str()
        .map_or_else(|| l7r_guard::shared::pyjson::py_str(mode), str::to_owned);
    let mut lines = vec![format!(
        "lit: {key}  mode: {mode}  zoom: {:.2}x of fit",
        number(zoom, "the zoom")?
    )];
    if !classes.iter().any(|(k, _)| k == key) {
        lines.push(format!(
            "  (no pixels of '{key}' are on screen in this view)"
        ));
    }
    let mut rows: Vec<(f64, usize, usize, &str)> = classes
        .iter()
        .filter(|(_, (_, t))| *t > 0)
        .map(|(k, (c, t))| (super::f(*c) / super::f(*t), *c, *t, k.as_str()))
        .collect();
    rows.sort_by(|p, q| q.partial_cmp(p).unwrap_or(std::cmp::Ordering::Equal));
    lines.push(format!(
        "{:>8}  {:>9}/{:<9}  class",
        "changed", "changed", "on screen"
    ));
    for (share, c, t, k) in rows {
        lines.push(format!("{:7.1}%  {c:>9}/{t:<9}  {k}", 100.0 * share));
    }
    Ok(lines.join("\n"))
}

/// `os.path.abspath`: joined to the working directory and normalized, `.` and `..` resolved by name, no link followed.
#[must_use]
pub fn abspath(path: &str) -> String {
    let joined = if path.starts_with('/') {
        PathBuf::from(path)
    } else {
        std::env::current_dir().unwrap_or_default().join(path)
    };
    let mut parts: Vec<String> = Vec::new();
    for c in joined.components() {
        match c {
            std::path::Component::Normal(s) => parts.push(s.to_string_lossy().into_owned()),
            std::path::Component::ParentDir => {
                parts.pop();
            }
            _ => {}
        }
    }
    format!("/{}", parts.join("/"))
}

/// The browser's half run as a program: `<launcher> browser lit <page> <key> <before> <after> [--vector]`.
///
/// # Errors
/// The browser failed (its own words), or its answer is not what `lit` prints.
pub fn shoot(launcher: &Path, page: &str, key: &str, vector: bool) -> Result<Shot, Error> {
    let dir = l7r_guard::shared::tempdir::TempDir::new("page-lit");
    let (before, after) = (dir.path().join("before.png"), dir.path().join("after.png"));
    let mut cmd = std::process::Command::new(launcher);
    cmd.args(["browser", "lit", page, key])
        .arg(&before)
        .arg(&after);
    if vector {
        cmd.arg("--vector");
    }
    let out = cmd
        .output()
        .map_err(|e| Error::new("OSError", format!("{}: {e}", launcher.display())))?;
    if !out.status.success() {
        return Err(Error::new(
            "playwright._impl._errors.Error",
            String::from_utf8_lossy(&out.stderr).trim_end().to_owned(),
        ));
    }
    let said: Value = serde_json::from_slice(&out.stdout)
        .map_err(|e| Error::new("RuntimeError", format!("the browser answered {e}")))?;
    let read =
        |p: &Path| std::fs::read(p).map_err(|e| crate::py::os_error(&e, &p.to_string_lossy()));
    Ok(Shot {
        mode: said["mode"].clone(),
        zoom: said["zoom"].clone(),
        ctm: said["ctm"].clone(),
        viewbox: said["viewbox"].clone(),
        before: read(&before)?,
        after: read(&after)?,
    })
}

/// The sides of the icons PIL wrote (`IcoImagePlugin._save`'s default `sizes`), each square.
const ICON_SIDES: [u32; 7] = [16, 24, 32, 48, 64, 128, 256];

/// The size PIL's `thumbnail` gives a `w` x `h` image fitted in a `side` square: the long side the square's, the short one whichever of its
/// floor and ceiling keeps the aspect closer (the floor on a tie, never below 1), in exact integers where PIL compared floats.
fn thumbnail(w: u32, h: u32, side: u32) -> (u32, u32) {
    let (w, h, s) = (u64::from(w), u64::from(h), u64::from(side));
    let fit = |n: u64| u32::try_from(n.max(1)).unwrap_or(side);
    if h >= w {
        // PIL's key |w/h - n/s|, over the common denominator h*s
        let (lo, off) = (s * w / h, |n: u64| (w * s).abs_diff(n * h));
        (fit(if off(lo + 1) < off(lo) { lo + 1 } else { lo }), side)
    } else {
        // PIL's key |w/h - s/n|, its denominators h*n cross-multiplied; a zero the closest, as PIL's key put it
        let (lo, off) = (s * h / w, |n: u64| (w * n).abs_diff(s * h));
        let ceil_closer = lo > 0 && off(lo + 1) * lo < off(lo) * (lo + 1);
        (side, fit(if ceil_closer { lo + 1 } else { lo }))
    }
}

/// One of PIL's frames of an icon: the shot fitted in a `side` square by PIL's `thumbnail` size, resampled by the `image` crate's
/// Lanczos3 (PIL's LANCZOS is the same three-lobed kernel; its pixels differ by the two filters' rounding, measured in the tests).
fn icon_frame(
    image: &image::RgbImage,
    side: u32,
) -> image::ImageResult<image::codecs::ico::IcoFrame<'static>> {
    let (fw, fh) = thumbnail(image.width(), image.height(), side);
    let frame = image::imageops::resize(image, fw, fh, image::imageops::FilterType::Lanczos3);
    image::codecs::ico::IcoFrame::as_png(frame.as_raw(), fw, fh, image::ExtendedColorType::Rgb8)
}

/// The lit shot saved where `--out` names (PIL's `after.save(out)`): the format chosen by the name's extension, as PIL chose it - a PNG
/// as the screenshot's own bytes (the same pixels PIL's re-encode held), any other format the `image` crate writes encoded from the
/// screenshot's pixels (feature 449 T150; a lossy or quantizing format's pixels are its encoder's, not PIL's - measured in the task's
/// report). A name with no format PIL or this port knows is refused in PIL's words.
///
/// # Errors
/// The name's format unknown or not written here, or the file unwritable.
pub fn save(out: &str, png: &[u8]) -> Result<(), Error> {
    let ext = Path::new(out)
        .extension()
        .map(|e| e.to_string_lossy().to_lowercase())
        .unwrap_or_default();
    let write_err = |e: std::io::Error| crate::py::os_error(&e, out);
    if ext == "png" {
        return std::fs::write(out, png).map_err(write_err);
    }
    let unknown = || {
        Error::new(
            "ValueError",
            format!(
                "unknown file extension: {}",
                if ext.is_empty() {
                    String::new()
                } else {
                    format!(".{ext}")
                }
            ),
        )
    };
    let format = image::ImageFormat::from_extension(&ext)
        .filter(image::ImageFormat::writing_enabled)
        .ok_or_else(unknown)?;
    let shot = rgb(png, "<the lit shot>")?;
    let w = u32::try_from(shot.width).unwrap_or(0);
    let image = image::RgbImage::from_fn(w, u32::try_from(shot.height).unwrap_or(0), |x, y| {
        let at = 3 * (y as usize * shot.width + x as usize);
        image::Rgb([shot.data[at], shot.data[at + 1], shot.data[at + 2]])
    });
    let mut buf = std::io::Cursor::new(Vec::new());
    // AS PIL WROTE THESE TWO (feature 449 T150's differential): an RGB image as a binary pixmap (`P6`) whatever the name, where the
    // crate's default wrote a PAM PIL cannot read; and a TGA uncompressed, PIL's default, where the crate's run-length packets crossed
    // rows PIL's reader refused ("buffer overrun")
    let (w, h) = (image.width(), image.height());
    let written = match format {
        image::ImageFormat::Pnm => image::ImageEncoder::write_image(
            image::codecs::pnm::PnmEncoder::new(&mut buf).with_subtype(
                image::codecs::pnm::PnmSubtype::Pixmap(image::codecs::pnm::SampleEncoding::Binary),
            ),
            image.as_raw(),
            w,
            h,
            image::ExtendedColorType::Rgb8,
        ),
        image::ImageFormat::Tga => image::ImageEncoder::write_image(
            image::codecs::tga::TgaEncoder::new(&mut buf).disable_rle(),
            image.as_raw(),
            w,
            h,
            image::ExtendedColorType::Rgb8,
        ),
        // AN ICON PAST 256 PX A SIDE SHRUNK AS PIL SHRANK IT (FIXED, feature 449 T183, T150's finding: the encoder refused it): a frame for
        // each of PIL's sizes that fits the shot; a shot no size fits, of which PIL wrote an icon with no image, refused naming the format
        image::ImageFormat::Ico if w > 256 || h > 256 => {
            let sides: Vec<u32> = ICON_SIDES.into_iter().filter(|s| *s <= w.min(h)).collect();
            if sides.is_empty() {
                return Err(Error::new(
                    "OSError",
                    format!("cannot write {out}: an ICO's smallest image is 16 x 16 px and the lit shot is {w} x {h} px, so no size of PIL's fits it"),
                ));
            }
            sides
                .into_iter()
                .map(|side| icon_frame(&image, side))
                .collect::<image::ImageResult<Vec<_>>>()
                .and_then(|frames| {
                    image::codecs::ico::IcoEncoder::new(&mut buf).encode_images(&frames)
                })
        }
        _ => image::DynamicImage::ImageRgb8(image).write_to(&mut buf, format),
    };
    written.map_err(|e| Error::new("OSError", format!("cannot write {out}: {e}")))?;
    std::fs::write(out, buf.into_inner()).map_err(write_err)
}

/// The measure (`measure` and `report`): the page's id map first (no browser where it carries none), the shots, the lit one saved to
/// `out` - as a PNG, the screenshot's own bytes - then the attribution.
fn measure(
    launcher: &Path,
    page: &str,
    key: &str,
    vector: bool,
    out: Option<&str>,
) -> Result<String, Error> {
    let html = l7r_gate_core::record::read_text(Path::new(page))
        .map_err(|e| crate::py::os_error(&e, page))?;
    let Some(map) = decode_idmap(&html)? else {
        return Err(Error::new(
            "SystemExit",
            format!("{page} carries no class id map (rendered without resvg?) - nothing to attribute pixels to"),
        ));
    };
    let shot = shoot(launcher, &abspath(page), key, vector)?;
    number(&shot.zoom, "the zoom")?; // read before the shots are used, as the Python's `float(...)` was
    if let Some(out) = out {
        save(out, &shot.after)?;
    }
    let before = rgb(&shot.before, "<the before shot>")?;
    let after = rgb(&shot.after, "<the after shot>")?;
    let classes = attribute(&before, &after, &map, &shot.ctm, &shot.viewbox)?;
    Ok(report(key, &shot.mode, &shot.zoom, &classes)? + "\n")
}

/// `make page-lit`: the command line read as the Python's argparse read it, and the measure, the browser started through `launcher`.
#[must_use]
pub fn main(args: &[String], launcher: &Path) -> Reply {
    let opts = [("vector", Takes::Flag), ("out", Takes::Value)];
    let (pos, options) = match parse(args, &opts) {
        Ok(Parsed::Help) => return super::reply(HELP.to_owned(), "", 0),
        Ok(Parsed::Run {
            positionals,
            options,
        }) if positionals.len() == 2 => (positionals, options),
        Ok(Parsed::Run { .. }) => {
            return super::usage(
                USAGE,
                "page-lit",
                "the arguments page and key are required, and no more",
            )
        }
        Err(e) => return super::usage(USAGE, "page-lit", &e),
    };
    let vector = options.iter().any(|(k, _)| *k == "vector");
    // an empty `--out` saves nothing, as the Python's `if out:` read it
    let out = options
        .iter()
        .find(|(k, _)| *k == "out")
        .map(|(_, v)| v.as_str())
        .filter(|v| !v.is_empty());
    super::answer(measure(launcher, &pos[0], &pos[1], vector, out))
}

#[cfg(test)]
mod tests;
