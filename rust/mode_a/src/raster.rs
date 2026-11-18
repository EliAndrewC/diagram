//! The low-zoom RASTER of the page and the CLASS ID MAP that answers the pointer while it shows (`interactive/raster.py`, feature 200;
//! ported by feature 449 T150, the engine port's step 2, the Python deleted by its part B with `picture_diff` and `page_lit`, now
//! `diagnostics/`).
//!
//! THE GM, 2026-09-07: "all of the above feel slow, so please proceed with the hybrid approach". Below a screen scale the page shows ONE
//! IMAGE of the whole picture, rendered by resvg (the PNG's renderer) at [`RASTER_R`] px per map px, and the lit class alone drawn as
//! vector above it; hidden groups cannot answer the pointer, so a second render, the ID MAP, paints every class one flat color (its hit
//! geometry included, every opacity stripped, no anti-aliasing) and the page reads the class under the pointer from a canvas. The off-map
//! ink is dropped (specs/200 R2). Every number here is a rendering decision recorded in its spec with its measurement.
//!
//! THE RENDERER IS THE `resvg` CRATE IN PROCESS (feature 449 T150; FR-001's phase-4 paragraph, `ask:449-phase4-slices` Q7 as amended by
//! `ask:449-engine-order`), pinned to the version of the binary the Python ran and driven as that binary drove it ([`render`]): the
//! documents handed to it are built here byte for byte as the Python built them, and its PNGs were the binary's byte for byte on every
//! render of the six pool pages and part A's cases (39 renders, 2026-11-18), so the id map is the Python's (its colors answer the pointer).
//! The picture's tiles are pasted and encoded as a JPEG by [`encode`] in process, where the Python ran a PIL child - the one step whose
//! pixels differ, every channel within one level on the six pool pages' 13 pictures (part A's lockstep, 2026-11-18).
//!
//! Research:
//!     raster plumbing - NONE: tiling, the off-map drop, the id map's documents and encoding, each picture setting a CONVENTION claimed beside it
//!     low-zoom picture - CONVENTION: one image of the whole picture below a screen scale, at `RASTER_R` px per map px

use std::sync::{Condvar, LazyLock, Mutex};

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;
use l7r_guard::shared::html_text::unescape;

use crate::py::{fmt_g, max, min};

pub mod docs;
pub mod encode;
pub mod render;

pub use docs::{assemble_offmap, drop_offmap, prepare_doc, prepare_offmap, tile_doc, Part};

/// Px per map px of the picture: feature 223 set it to 2 (the GM 2026-09-11, on feature 222's pattern - make it, look, reverse it in one
/// line if bad), 44% of the pixels of 3 for the render, the decode, the JPEG and the page's bytes; a DPR-2 reader's opening view is the
/// priced cost (spec 223 D3).
///
/// Research: the picture's resolution - CONVENTION: 2 px per map px, chosen for the render and page size (specs/223 research R2); to reverse, 3.0
pub const RASTER_R: f64 = 2.0;
/// THE PICTURE IS A LOSSY JPEG (feature 222, the GM 2026-09-11: "I am willing to at least try the lossy JPEG compression for the final
/// image if that seems like it will gain us about four seconds"): quality 90, 4:4:4 so a thin colored stroke keeps its chroma.
///
/// Research: the picture's encoding - CONVENTION: a JPEG at quality 90 with no chroma subsampling, the GM's choice for speed over a lossless WebP (specs/222 research R1)
pub const PICTURE_QUALITY: u8 = 90;
/// The picture's format, as PIL named it.
///
/// Research: the picture's encoding - CONVENTION: a JPEG, the GM's choice for speed (feature 222)
pub const PICTURE_FORMAT: &str = "JPEG";
/// PIL's `subsampling=0`: 4:4:4, full chroma resolution on the map's thin colored strokes ([`encode::jpeg`] writes it so).
///
/// Research: the picture's encoding - CONVENTION: no chroma subsampling, so a thin colored stroke keeps its color (feature 222)
pub const PICTURE_SUBSAMPLING: u8 = 0;
/// The picture's media type.
pub const PICTURE_MIME: &str = "image/jpeg";
/// THE PICTURE IS RENDERED IN TILES (feature 223): resvg is single-threaded and the cost is the pixel count, so the picture splits into the
/// smallest n x n grid of pixel-aligned tiles each under this many megapixels.
///
/// Research: the picture's tiles - CONVENTION: tiles under 8 megapixels each, a hamlet at 2 x 2 and a city at 3 x 3 (specs/223 research R1)
pub const TILE_MPX: f64 = 8.0;
/// AT MOST THREE TILES RENDER AT ONCE (feature 324: each tile's resvg parses the whole document, ~100 MB; three at once ~540 MB).
///
/// Research: the tiles' concurrency - CONVENTION: three tiles at once, measured against memory and time (specs/324-render-memory research R2)
pub const TILE_WORKERS: usize = 3;
/// AT MOST FOUR RESVG PROCESSES AT ONCE IN THIS PROCESS (feature 327: one shared cap over the tiles and the id map).
///
/// Research: the renders' concurrency - CONVENTION: four resvg processes at once in one process (specs/327-lean-site-fast-clip research R3)
pub const RESVG_SLOTS: usize = 4;
/// How far past the viewBox an element may lie and still be kept - wider than any stroke width or blob radius the writer emits (spec 200 D6).
///
/// Research: the off-map margin - CONVENTION: 24 px past the viewBox, wider than any stroke or blob the writer emits, so nothing visible is dropped
pub const OFFMAP_MARGIN: f64 = 24.0;
/// The id map's palette: class i paints red = ((i - 1) % 63 + 1) * 4 and green = ((i - 1) // 63) * 4 (feature 264: past 63, green counts
/// the rows), so a value one off the grid snaps back.
///
/// Research: the id map's palette - CONVENTION: a step of 4 per class in red, rows of 63 in green, so a canvas round trip snaps back
pub const PALETTE_STEP: i64 = 4;
/// Classes in one palette row.
///
/// Research: the id map's palette - CONVENTION: 63 classes a row of red, green counting the rows (feature 264)
pub const PALETTE_ROW: i64 = 255 / PALETTE_STEP;
/// Classes one page may hold.
pub const PALETTE_MAX: i64 = PALETTE_ROW * (PALETTE_ROW + 1);
/// resvg names MS fonts for the generic families; 'serif' must be `DejaVu Serif` or every label changes face (`RESVG_FONT_ARGS`).
///
/// Research: the renders' serif - CONVENTION: `DejaVu Serif` for resvg's serif family, the map PNG's own face
pub const RESVG_FONT_ARGS: [&str; 2] = ["--serif-family", "DejaVu Serif"];
/// The widest raster a test may ask for while `DIAGRAM_SKIP_RENDER` is set (`_census.TEST_RENDER_PX`).
pub const TEST_RENDER_PX: f64 = 1200.0;

/// A map's viewBox: x, y, width, height.
pub type Viewbox = (f64, f64, f64, f64);

/// (red, green) of class `i`, 1-based.
#[must_use]
pub fn palette_rgb(i: i64) -> (i64, i64) {
    (
        ((i - 1) % PALETTE_ROW + 1) * PALETTE_STEP,
        ((i - 1) / PALETTE_ROW) * PALETTE_STEP,
    )
}

/// The palette's key for a pixel's snapped (red, green): the red alone on the first row.
#[must_use]
pub fn palette_key(red: i64, green: i64) -> String {
    if green == 0 {
        red.to_string()
    } else {
        format!("{red},{green}")
    }
}

static VIEWBOX: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"viewBox="\s*(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+(-?[\d.]+)[ ,]+(-?[\d.]+)\s*""#)
});
static TEXT: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<text\b[^>]*>.*?</text>"));
pub(crate) static GROUP: LazyLock<Regex> =
    LazyLock::new(|| py(r#"<g class="f f-[a-z0-9-]+(?: planted)?" data-k="([^"]*)"[^>]*>"#));
static GTAG: LazyLock<Regex> = LazyLock::new(|| py(r"<g\b|</g>"));
static OPACITY: LazyLock<Regex> =
    LazyLock::new(|| py(r#"\s(?:fill-opacity|stroke-opacity|opacity)="[^"]*""#));
static HIT_FILL_GROUP: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"(?s)<g class="hit" fill="none" style="pointer-events: fill">(.*?)</g>"#)
});
static HIT_STROKE: LazyLock<Regex> = LazyLock::new(|| {
    py(r#"fill="none" class="hit" style="pointer-events: stroke; stroke-width: ([\d.]+)px""#)
});
static HIT_BEAD: LazyLock<Regex> =
    LazyLock::new(|| py(r#"r="([\d.]+)" fill="none" class="hit" style="pointer-events: fill""#));
static PAINT_FILL: LazyLock<Regex> =
    LazyLock::new(|| py(r#"fill="(?:#[0-9A-Fa-f]{3,8}|url\([^)]*\))""#));
static PAINT_STROKE: LazyLock<Regex> = LazyLock::new(|| py(r##"stroke="#[0-9A-Fa-f]{3,8}""##));
static WIDTH: LazyLock<Regex> = LazyLock::new(|| py(r#"width="([\d.]+)""#));

/// (x, y, w, h) from the page's `<svg>` open tag, or none when it carries none.
///
/// # Errors
/// A figure `[\d.]+` took that the Python's `float()` refused.
pub fn viewbox_of(svg_open: &str) -> Result<Option<Viewbox>, Error> {
    let Some(c) = VIEWBOX.captures(svg_open).ok().flatten() else {
        return Ok(None);
    };
    let f = |i: usize| crate::py::float(&c[i]);
    Ok(Some((f(1)?, f(2)?, f(3)?, f(4)?)))
}

/// The SVG less every `<text>` - what the PICTURE is rendered from (feature 201): text is never in the image and always the browser's.
///
/// Research: the picture carries no text - CONVENTION: every text stays the browser's, in both modes (feature 201)
#[must_use]
pub fn without_text(svg_text: &str) -> String {
    TEXT.replace_all(svg_text, "").into_owned()
}

/// Every class key on the page, in order of first appearance, unescaped (feature 262: `data-k` is written HTML-escaped).
#[must_use]
pub fn class_keys(svg_text: &str) -> Vec<String> {
    let mut keys: Vec<String> = Vec::new();
    for c in GROUP.captures_iter(svg_text).flatten() {
        let key = unescape(&c[1]);
        if !keys.contains(&key) {
            keys.push(key);
        }
    }
    keys
}

/// `regex.sub(f(m), text)`, a replacement built from each match's first group.
fn sub_with(re: &Regex, text: &str, f: impl Fn(&str) -> String) -> String {
    re.replace_all(text, |c: &fancy_regex::Captures| f(&c[1]))
        .into_owned()
}

/// One class group painted flat in `c`, its HIT GEOMETRY painted as the DOM would hit it (`raster._recolor_group`).
///
/// Research: the id map's paint - CONVENTION: each class flat in its palette color, its hit regions and widened copies painted as the page hits them
#[must_use]
pub fn recolor_group(text: &str, c: &str) -> String {
    let text = sub_with(&HIT_FILL_GROUP, text, |inner| {
        format!(
            "<g fill=\"{c}\">{}</g>",
            inner.replace(" fill=\"none\"", "")
        )
    });
    let text = text.replace(
        "fill=\"none\" style=\"pointer-events: fill\"",
        &format!("fill=\"{c}\""),
    );
    let text = sub_with(&HIT_STROKE, &text, |w| {
        format!("stroke=\"{c}\" stroke-width=\"{w}\" fill=\"none\"")
    });
    let text = sub_with(&HIT_BEAD, &text, |r| format!("r=\"{r}\" fill=\"{c}\""));
    let fill = format!("fill=\"{c}\"");
    let text = PAINT_FILL.replace_all(&text, fancy_regex::NoExpand(&fill));
    let stroke = format!("stroke=\"{c}\"");
    let text = PAINT_STROKE.replace_all(&text, fancy_regex::NoExpand(&stroke));
    text.replacen('>', &format!(" fill=\"{c}\">"), 1)
}

/// Text OUTSIDE every class group with its paints removed: nothing there may answer the pointer (`raster._unpaint`).
///
/// Research: nothing outside a class answers - CONVENTION: the ink outside every class group is painted none in the id map
#[must_use]
pub fn unpaint(text: &str) -> String {
    let text = PAINT_FILL.replace_all(text, "fill=\"none\"");
    PAINT_STROKE
        .replace_all(&text, "stroke=\"none\"")
        .into_owned()
}

/// The id map's document and palette (`raster.id_map`'s text half): every class group recolored flat, the ink outside them unpainted,
/// every opacity stripped, crisp edges asked for.
///
/// # Errors
/// More classes than the palette holds (the Python's `ValueError`), or a class group never closed (its `AssertionError`).
pub fn id_map_doc(
    svg_text: &str,
    keys: &[String],
) -> Result<(String, Vec<(String, String)>), Error> {
    if i64::try_from(keys.len()).unwrap_or(i64::MAX) > PALETTE_MAX {
        return Err(Error::new(
            "ValueError",
            format!(
                "{} classes on one page - past the id map's {PALETTE_MAX}-class palette",
                keys.len()
            ),
        ));
    }
    let mut palette = Vec::new();
    let mut color = Vec::new();
    for (i, k) in (1_i64..).zip(keys) {
        let (r, g) = palette_rgb(i);
        palette.push((palette_key(r, g), k.clone()));
        color.push((k.clone(), format!("#{r:02X}{g:02X}00")));
    }
    let mut out = String::new();
    let mut pos = 0;
    for m in GROUP.captures_iter(svg_text).flatten() {
        let whole = m.get(0).map_or(0..0, |w| w.range());
        if whole.start < pos {
            continue;
        }
        let (mut depth, mut i) = (1, whole.end);
        while depth > 0 {
            let Some(t) = GTAG.find_from_pos(svg_text, i).ok().flatten() else {
                return Err(Error::new("AssertionError", "an unclosed class group"));
            };
            depth += if t.as_str() == "</g>" { -1 } else { 1 };
            i = t.end();
        }
        out += &unpaint(&svg_text[pos..whole.start]);
        let key = unescape(&m[1]);
        let c = color
            .iter()
            .find(|(k, _)| *k == key)
            .map(|(_, c)| c.as_str())
            .ok_or_else(|| Error::new("KeyError", key.clone()))?;
        out += &recolor_group(&svg_text[whole.start..i], c);
        pos = i;
    }
    out += &unpaint(&svg_text[pos..]);
    let doc = OPACITY.replace_all(&out, "").into_owned();
    Ok((
        doc.replacen("<svg ", "<svg shape-rendering=\"crispEdges\" ", 1),
        palette,
    ))
}

/// The id map's resvg arguments: zoom 1, crisp edges, and (feature 264) a Mode A sheet's text unblended, so a label never answers as its
/// neighbor in the palette - `crisp_text`, given only for a sheet's page.
///
/// Research: the id map's crisp text - CONVENTION: a sheet's labels drawn unblended so a label never answers as its neighbor in the palette (feature 264); a hamlet's id map unchanged
#[must_use]
pub fn id_map_args(crisp_text: bool) -> Vec<String> {
    let mut args: Vec<String> = ["--zoom", "1", "--shape-rendering", "crispEdges"]
        .map(str::to_owned)
        .to_vec();
    if crisp_text {
        args.extend(["--text-rendering", "optimizeSpeed"].map(str::to_owned));
    }
    args.extend(RESVG_FONT_ARGS.map(str::to_owned));
    args
}

/// (the id map as PNG at 1 px per map px, {palette key: class key}) (`raster.id_map`).
///
/// # Errors
/// [`id_map_doc`]'s refusals, or the render's.
pub fn id_map(
    host: &Host,
    svg_text: &str,
    keys: &[String],
    crisp_text: bool,
) -> Result<IdMap, Error> {
    let (doc, palette) = id_map_doc(svg_text, keys)?;
    Ok((host.resvg_png(&doc, &id_map_args(crisp_text))?, palette))
}

/// The tiles per axis for a picture of `vb` at `r` px per map px - the smallest n with each tile under [`TILE_MPX`].
///
/// # Errors
/// A viewBox whose area is no finite number (`math.ceil`'s refusal).
pub fn tile_count(vb: Viewbox, r: f64) -> Result<i64, Error> {
    let area = vb.2 * r * vb.3 * r / (TILE_MPX * 1e6);
    if area < 0.0 {
        return Err(Error::new(
            "ValueError",
            format!(
                "expected a nonnegative input, got {}",
                l7r_guard::shared::pyjson::py_float(area)
            ),
        ));
    }
    Ok(crate::py::ceil(area.sqrt())?.max(1))
}

/// (column, row, viewBox) for an n x n split of `vb` on whole map pixels: every tile but the last in each axis `ceil(size / n)` map px,
/// the last the remainder, so an integer zoom lands every tile on the picture's own pixel grid.
///
/// # Errors
/// A viewBox size that is no finite number.
#[expect(
    clippy::cast_precision_loss,
    reason = "tile edges are whole map pixels, far inside f64's exact integers"
)]
pub fn tile_boxes(vb: Viewbox, n: i64) -> Result<Vec<(i64, i64, Viewbox)>, Error> {
    let (mw, mh) = (
        crate::py::ceil(vb.2 / n as f64)?,
        crate::py::ceil(vb.3 / n as f64)?,
    );
    let edge = |i: i64, m: i64, size: f64| min((i * m) as f64, size);
    let xs: Vec<f64> = (0..=n).map(|i| edge(i, mw, vb.2)).collect();
    let ys: Vec<f64> = (0..=n).map(|j| edge(j, mh, vb.3)).collect();
    let mut out = Vec::new();
    for j in 0..n {
        for i in 0..n {
            let (iu, ju) = (
                usize::try_from(i).unwrap_or(0),
                usize::try_from(j).unwrap_or(0),
            );
            if xs[iu + 1] > xs[iu] && ys[ju + 1] > ys[ju] {
                out.push((
                    i,
                    j,
                    (
                        vb.0 + xs[iu],
                        vb.1 + ys[ju],
                        xs[iu + 1] - xs[iu],
                        ys[ju + 1] - ys[ju],
                    ),
                ));
            }
        }
    }
    Ok(out)
}

/// The picture's resvg arguments at `r`.
#[must_use]
pub fn picture_args(r: f64) -> Vec<String> {
    let mut args = vec!["--zoom".to_owned(), fmt_g(r)];
    args.extend(RESVG_FONT_ARGS.map(str::to_owned));
    args
}

/// The whole picture at `r` px per map px as a JPEG (`raster.picture`), rendered as `tiles` x `tiles` pixel-aligned tiles at most
/// [`TILE_WORKERS`] at once (none picks the count from the area; a fractional `r` renders single, never with a seam).
///
/// # Errors
/// The render's or the encode's.
///
/// Research: the low-zoom picture - CONVENTION: one image of the whole map at `RASTER_R` px per map px, rendered in pixel-aligned tiles at once (features 200, 223)
pub fn picture(host: &Host, svg_text: &str, r: f64, tiles: Option<i64>) -> Result<Vec<u8>, Error> {
    host.census_record("render", "raster");
    let head = svg_text.find('>').map_or("", |at| &svg_text[..=at]);
    let vb = viewbox_of(head)?;
    let mut n = match (tiles.filter(|&t| t != 0), vb) {
        (Some(t), _) => t,
        (None, Some(vb)) => tile_count(vb, r)?,
        (None, None) => 1,
    };
    if r.fract() != 0.0 {
        n = 1;
    }
    let args = picture_args(r);
    let Some(vb) = vb.filter(|_| n > 1) else {
        return encode::encode_picture(&[(0, 0, host.resvg_png(svg_text, &args)?)]);
    };
    let boxes = tile_boxes(vb, n)?;
    let prepared = prepare_doc(svg_text)?;
    let next = std::sync::atomic::AtomicUsize::new(0);
    let done: Mutex<Vec<TileRender>> = Mutex::new(Vec::new());
    std::thread::scope(|scope| {
        for _ in 0..boxes.len().min(TILE_WORKERS) {
            scope.spawn(|| loop {
                let k = next.fetch_add(1, std::sync::atomic::Ordering::SeqCst);
                let Some(&(_, _, b)) = boxes.get(k) else {
                    break;
                };
                let png = host.resvg_png(&tile_doc(&prepared, b), &args);
                done.lock()
                    .unwrap_or_else(std::sync::PoisonError::into_inner)
                    .push((k, png));
            });
        }
    });
    let mut rendered = done
        .into_inner()
        .unwrap_or_else(std::sync::PoisonError::into_inner);
    rendered.sort_by_key(|(k, _)| *k);
    // every tile's result taken in order before any is judged, as the Python's list of results was: a failed render raises first
    let results: Vec<Vec<u8>> = rendered
        .into_iter()
        .map(|(_, png)| png)
        .collect::<Result<_, _>>()?;
    let mut pngs = Vec::new();
    for ((i, j, _), png) in boxes.iter().zip(results) {
        pngs.push((*i, *j, png));
    }
    encode::encode_picture(&pngs)
}

/// `data:<mime>;base64,<data>`.
#[must_use]
pub fn data_uri(mime: &str, data: &[u8]) -> String {
    format!("data:{mime};base64,{}", encode::base64(data))
}

/// The id map's PNG and its palette, `(palette key, class key)` in class order.
pub type IdMap = (Vec<u8>, Vec<(String, String)>);

/// One tile's render, by its place in the grid.
type TileRender = (usize, Result<Vec<u8>, Error>);

/// The names of the variables a render reads: the test-render switch and the roll census's.
pub const HOST_VARS: [&str; 7] = [
    "DIAGRAM_SKIP_RENDER",
    "L7R_ROLL_CENSUS",
    "L7R_ROLL_CENSUS_TEST",
    "L7R_ROLL_CENSUS_REQUEST",
    "L7R_ROLL_CENSUS_WORKER",
    "L7R_COV_CONTEXT",
    "L7R_ROLL_CENSUS_GEN",
];

/// What a render reads of its host: [`HOST_VARS`] as they stand - handed in, so a test states its host rather than changing the process's.
/// (The `resvg` program the Python looked up on the PATH is gone: the renderer is the crate, feature 449 T150.)
#[derive(Debug, Clone, Default)]
pub struct Host {
    pub vars: Vec<(String, String)>,
    /// Where a caller that asks keeps every render: the document's and the PNG's sha256 and the arguments - how the crate's lockstep holds
    /// each document handed to resvg to the Python's, so equal documents through the one binary are equal images.
    pub log: Option<std::sync::Arc<Mutex<Vec<Rendered>>>>,
}

/// One render as [`Host::log`] keeps it: the document's sha256, the arguments, the PNG's sha256.
pub type Rendered = (String, Vec<String>, String);

/// The slots of [`RESVG_SLOTS`]: a count under a lock, and the wait for one to free.
static SLOTS: LazyLock<(Mutex<usize>, Condvar)> = LazyLock::new(|| (Mutex::new(0), Condvar::new()));

impl Host {
    /// This process's host.
    #[must_use]
    pub fn current() -> Self {
        Self {
            log: None,
            vars: HOST_VARS
                .iter()
                .filter_map(|v| Some(((*v).to_owned(), std::env::var(v).ok()?)))
                .collect(),
        }
    }

    /// A variable's value, as `os.environ.get`.
    #[must_use]
    pub fn var(&self, name: &str) -> Option<&str> {
        self.vars
            .iter()
            .find(|(k, _)| k == name)
            .map(|(_, v)| v.as_str())
    }

    /// `_census.refuse_render_in_a_test`: a raster wider than [`TEST_RENDER_PX`] while `DIAGRAM_SKIP_RENDER` is set is refused where it
    /// would be spawned (GM 2026-09-12: *"they keep getting added back in because we just forget and then don't notice"*).
    ///
    /// # Errors
    /// That raster, as the Python's `RenderedInATest`.
    ///
    /// Research: the render guard - NONE: test-suite bookkeeping, no map decision
    pub fn refuse_render_in_a_test(&self, what: &str, px: f64) -> Result<(), Error> {
        if self.var("DIAGRAM_SKIP_RENDER").is_none_or(str::is_empty) || px <= TEST_RENDER_PX {
            return Ok(());
        }
        let bar = TEST_RENDER_PX;
        // named as the Python's traceback names it, its module with it
        Err(Error::new(
            "l7r.diagram._census.RenderedInATest",
            format!(
                "a test asked to render {what} at {} px wide, over the {bar:.0} px a test may ask for.\n\
                 Tests do not render real images - a map's PNG is resvg at ~420 MB and the page's picture a PIL child at\n\
                 ~444 MB, and the suite's memory is the sum of its workers. MOCK IT: patch the plate or the render helper,\n\
                 or assert on the SVG or the manifest the renderer would have read. A small probe is fine and needs nothing:\n\
                 the deliberate render tests work on a 40x40 document, well under {bar:.0} px.\n\
                 A test that genuinely needs a large render marks itself `@pytest.mark.renders` and clears the switch with\n\
                 `monkeypatch.delenv(\"DIAGRAM_SKIP_RENDER\", raising=False)` - the contract feature 213 set, now enforced\n\
                 where the renderer is spawned rather than only where `finish()` consults the switch (GM 2026-09-12).",
                crate::py::fixed(px, 0)
            ),
        ))
    }

    /// `_census.record(kind, what=...)`: one JSON line appended to the roll census when one is open; never fails.
    pub fn census_record(&self, kind: &str, what: &str) {
        let Some(path) = self.var("L7R_ROLL_CENSUS").filter(|p| !p.is_empty()) else {
            return;
        };
        let now = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)
            .map_or(0.0, |d| d.as_secs_f64());
        let var = |n: &str| {
            self.var(n)
                .map_or(serde_json::Value::Null, serde_json::Value::from)
        };
        let row = serde_json::json!({
            "kind": kind, "t": crate::py::round_to(now, 3), "pid": std::process::id(),
            "test": var("L7R_ROLL_CENSUS_TEST"), "request": var("L7R_ROLL_CENSUS_REQUEST"),
            "worker": var("L7R_ROLL_CENSUS_WORKER"), "context": var("L7R_COV_CONTEXT"),
            "gen": var("L7R_ROLL_CENSUS_GEN"), "what": what,
        });
        let line = l7r_guard::shared::pyjson::dumps(&row, None, true) + "\n";
        let _ = std::fs::OpenOptions::new()
            .create(true)
            .append(true)
            .open(path)
            .and_then(|mut f| std::io::Write::write_all(&mut f, line.as_bytes()));
    }

    /// The size a render asks for: the largest `--width`, or `--zoom` times the document's own width (`resvg_png`'s probe).
    fn asked_px(doc: &str, args: &[String]) -> Result<f64, Error> {
        let mut px = 0.0;
        for (i, a) in args.iter().enumerate() {
            let Some(v) = args.get(i + 1) else { continue };
            if a == "--width" {
                px = max(px, crate::py::float(v)?);
            } else if a == "--zoom" {
                let head: String = doc.chars().take(400).collect();
                let w = match WIDTH.captures(&head).ok().flatten() {
                    Some(c) => crate::py::float(&c[1])?,
                    None => 1.0,
                };
                px = max(px, crate::py::float(v)? * w);
            }
        }
        Ok(px)
    }

    /// `doc` rendered by resvg with `args`, as PNG bytes (`raster.resvg_png`); at most [`RESVG_SLOTS`] at once - the memory bound the
    /// Python's processes kept, held for the renders now in this one.
    ///
    /// # Errors
    /// [`Host::refuse_render_in_a_test`]'s refusal, a size argument that is no number, or a render that failed.
    pub fn resvg_png(&self, doc: &str, args: &[String]) -> Result<Vec<u8>, Error> {
        self.refuse_render_in_a_test("the page's raster picture", Self::asked_px(doc, args)?)?;
        let head = doc.find('>').map_or("", |at| &doc[..=at]);
        let doc = if head.contains("xmlns=") {
            doc.to_owned()
        } else {
            // a test page's bare `<svg viewBox=...>`: resvg needs the namespace
            doc.replacen("<svg ", "<svg xmlns=\"http://www.w3.org/2000/svg\" ", 1)
        };
        let png = {
            let _slot = Slot::take();
            render::png(&doc, args)?
        };
        if let Some(log) = &self.log {
            let hex = l7r_guard::shared::sha256::hex;
            let row = (hex(doc.as_bytes()), args.to_vec(), hex(&png));
            log.lock()
                .unwrap_or_else(std::sync::PoisonError::into_inner)
                .push(row);
        }
        Ok(png)
    }
}

/// One of the [`RESVG_SLOTS`], held while a render runs.
struct Slot;

impl Slot {
    fn take() -> Self {
        let (lock, freed) = &*SLOTS;
        let mut held = lock
            .lock()
            .unwrap_or_else(std::sync::PoisonError::into_inner);
        while *held >= RESVG_SLOTS {
            held = freed
                .wait(held)
                .unwrap_or_else(std::sync::PoisonError::into_inner);
        }
        *held += 1;
        Self
    }
}

impl Drop for Slot {
    fn drop(&mut self) {
        let (lock, freed) = &*SLOTS;
        *lock
            .lock()
            .unwrap_or_else(std::sync::PoisonError::into_inner) -= 1;
        freed.notify_one();
    }
}

#[cfg(test)]
mod tests;
