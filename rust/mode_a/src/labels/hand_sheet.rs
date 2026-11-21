//! A hand-drawn Mode A sheet READ (feature 449 T151, `labels/hand_sheet.py`'s reader; the placer it fed deleted by T202, which rebuilt the
//! placement from its derivation as [`crate::caption_place`]). A sheet's SVG is the drawing and, for each caption, its declaration - its
//! text, its face and what it names - never where it stands (feature 286, the GM: *"There is no point in having an automated check run
//! against an automated process"*). [`read_sheet`] reads the sheet's drawn shapes ([`read`]) as [`Shape`]s, the input
//! [`crate::caption_place::placed`] seats the captions from; [`render`] draws a placed sheet's text as its picture.
//!
//! Research: the hand sheet's reading - NONE: a sheet read as drawn, its captions measured at their face, deciding nothing about where a caption stands

use std::collections::BTreeMap;
use std::collections::BTreeSet;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use read::Pt;

#[cfg(feature = "counters")]
pub mod counted;
pub mod read;

pub use read::{read_sheet, Affine, IDENTITY};

/// An element's attributes, as `ElementTree` keyed them.
pub type Attrs = BTreeMap<String, String>;

/// Fills a name cannot be read on even as nested ground: a worked bed's rows run through the letters (feature 283).
///
/// Research: busy fills - CONVENTION: a vegetable bed's rows take no name, however light its ground
pub const BUSY_FILLS: [&str; 1] = ["url(#vegetable-rows)"];

/// Ink this dark (0-1 luma) or darker is dark to a caption.
///
/// Research: dark ink threshold - CONVENTION: ink of luma 0.3 or darker counts as dark to a caption, so a caption reads against it.
pub const DARK: f64 = 0.3;

/// How far a disc's drawn curve, sampled as a polygon, may stand inside the true curve (px): a leader's end on it lands within its 1 px trim
/// and this of the curve (feature 449 T192).
///
/// Research: a disc's sampled curve - CONVENTION: a disc's drawn curve sampled finely enough that no chord stands more than 0.05 px inside it - a drawn size on the sheet, not in the world; the sample count is the least whose chord sag R(1 - cos(pi / n)) is within it, R bounding the curve's half-axes (the pool's largest disc half-axis is 45 px, 80 samples at the bound)
pub const DISC_SAG_PX: f64 = 0.05;

/// Width per character of a hand sheet's ALL-CAPS captions (feature 267).
///
/// Research: caps caption width - NONE: a hand sheet's all-caps captions run about 0.70 em per character, a text-measuring figure.
pub const CAPS_W_EM: f64 = 0.70;

/// What bold adds per character.
///
/// Research: bold caption width - NONE: bold adds about 0.04 em per character to a caption's width, a text-measuring figure.
pub const BOLD_W_EM: f64 = 0.04;

/// Research: character width - CONVENTION: 0.55 em
pub const CHAR_W_EM: f64 = 0.55;
/// Research: line height - CONVENTION: 1.05 em
pub const LINE_H_EM: f64 = 1.05;
/// Research: line pitch - CONVENTION: 1.15 em
pub const PITCH_EM: f64 = 1.15;
/// Research: block center above the baseline - CONVENTION: 0.275 em
pub const CENTER_ABOVE_BASELINE_EM: f64 = 0.275;

/// How a stroke ends (the Python's `cap` string, SVG's `stroke-linecap`, feature 449 T193): flat at its end point (`butt`, SVG's
/// default), drawn on past it by the half-width (`square`), or rounded (`round`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Cap {
    #[default]
    Butt,
    Square,
    Round,
}

impl Cap {
    /// The cap a `stroke-linecap` value draws: "butt", "square" or "round"; None for a value SVG does not know, which SVG ignores, so the
    /// cap inherited stands (feature 449 T194; T193 drew such a stroke butt).
    #[must_use]
    pub fn of(value: &str) -> Option<Self> {
        match value {
            "butt" => Some(Self::Butt),
            "square" => Some(Self::Square),
            "round" => Some(Self::Round),
            _ => None,
        }
    }
}

/// How a stroke's corners are drawn (the Python's `join` string, SVG's `stroke-linejoin`, feature 449 T194): the two outer edges drawn on
/// until they meet (`miter`, SVG's default, a bevel past the miter limit), a disc of the half-width (`round`), or the two outer corners
/// joined straight (`bevel`).
#[derive(Debug, Clone, Copy, PartialEq, Eq, Default)]
pub enum Join {
    #[default]
    Miter,
    Round,
    Bevel,
}

impl Join {
    /// The join a `stroke-linejoin` value draws: "miter", and SVG 2's "miter-clip" and "arcs", which draw a miter within the limit, a
    /// miter; "round" and "bevel" themselves; None for a value SVG does not know, which SVG ignores, so the join inherited stands.
    #[must_use]
    pub fn of(value: &str) -> Option<Self> {
        match value {
            "miter" | "miter-clip" | "arcs" => Some(Self::Miter),
            "round" => Some(Self::Round),
            "bevel" => Some(Self::Bevel),
            _ => None,
        }
    }
}

/// One drawn element, in sheet coordinates (the Python's `Shape`): its tag and kind, its outline (or polyline and stroke half-width), and
/// for a `<text>` the caption it carries - its words, size, lines, its parent's matrix, its place in the document, its declared names and
/// whether it continues the caption before. `attrs` are its element's attributes. (The Python's `angle`, `center` and `within` were
/// written and never read, and are not carried.)
#[derive(Debug, Clone)]
#[expect(
    clippy::struct_excessive_bools,
    reason = "the Python's `Shape`, field for field"
)]
pub struct Shape {
    pub tag: String,
    pub kind: String,
    pub poly: Vec<Pt>,
    pub half: f64,
    pub line: bool,
    pub text: String,
    pub size: f64,
    pub attrs: Option<Attrs>,
    pub leader: bool,
    pub lines: Vec<String>,
    pub group: usize,
    pub frame: Affine,
    pub edge: f64,
    pub texture: bool,
    pub filled: bool,
    pub busy: bool,
    pub dark: bool,
    pub at: usize,
    pub ids: BTreeSet<String>,
    pub names: Vec<String>,
    pub cont: bool,
    /// A stroke's `stroke-linecap`, inherited as SVG inherits it (feature 449 T193).
    pub cap: Cap,
    /// A stroke's `stroke-linejoin`, inherited (feature 449 T194).
    pub join: Join,
    /// A stroke's `stroke-miterlimit`, inherited (SVG's default 4): a sharper corner's miter is drawn as a bevel (T194).
    pub miter: f64,
    /// A stroke a path's `Z` closed: drawn with a join at its start, no caps (T194).
    pub closed: bool,
    /// A stroke's `stroke-dasharray` in sheet px, an even count (empty: solid), inherited (T194).
    pub dash: Vec<f64>,
    /// A stroke's `stroke-dashoffset` in sheet px, inherited (T194).
    pub offset: f64,
}

impl Default for Shape {
    /// The Python's `Shape` defaults: nothing drawn, SVG's stroke defaults (a butt cap, a miter join, a miter limit of 4, solid).
    ///
    /// Research: its drawn sizes - NONE: SVG's default `stroke-miterlimit`, 4
    fn default() -> Self {
        Self {
            tag: String::new(),
            kind: String::new(),
            poly: Vec::new(),
            half: 0.0,
            line: false,
            text: String::new(),
            size: 0.0,
            attrs: None,
            leader: false,
            lines: Vec::new(),
            group: 0,
            frame: (0.0, 0.0, 0.0, 0.0, 0.0, 0.0),
            edge: 0.0,
            texture: false,
            filled: false,
            busy: false,
            dark: false,
            at: 0,
            ids: BTreeSet::new(),
            names: Vec::new(),
            cont: false,
            cap: Cap::Butt,
            join: Join::Miter,
            miter: 4.0,
            closed: false,
            dash: Vec::new(),
            offset: 0.0,
        }
    }
}

static LETTER: LazyLock<Regex> = LazyLock::new(|| py(r"\A\p{L}\z"));

/// A `#rgb` or `#rrggbb` fill's luma (0 black, 1 white); anything else - none, a pattern - reads as 0.5.
///
/// Research:
///     its salts, guards and sentinels - NONE: they decide nothing about the place - 0.114 (Rec.601 luma weight (blue)); 16 (hex base); 0.299 (Rec.601 luma weight (red)); 0.587 (Rec.601 luma weight (green))
#[must_use]
pub fn luma(fill: Option<&str>) -> f64 {
    let fill = l7r_shared::py_text::strip(fill.unwrap_or_default());
    // `re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})", fill)`
    let Some(h) = fill
        .strip_prefix('#')
        .filter(|h| matches!(h.len(), 3 | 6) && h.bytes().all(|c| c.is_ascii_hexdigit()))
    else {
        return 0.5;
    };
    let h: String = if h.len() == 3 {
        h.chars().flat_map(|c| [c, c]).collect()
    } else {
        h.to_owned()
    };
    let ch = |i: usize| f64::from(u8::from_str_radix(&h[i..i + 2], 16).unwrap_or(0)) / 255.0;
    0.299 * ch(0) + 0.587 * ch(2) + 0.114 * ch(4)
}

/// How wide a text's characters run, in ems, from its element's face: ALL-CAPS wider, bold wider, letter-spacing its own width.
///
/// Research: a caption's width by its face - NONE: the text metrics of its face applied, caps, bold and letter-spacing
#[must_use]
pub fn char_w_of(attrs: Option<&Attrs>, text: &str, size: f64) -> f64 {
    let letters: Vec<char> = text
        .chars()
        .filter(|c| LETTER.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false))
        .collect();
    let mut w = if !letters.is_empty() && letters.iter().all(|c| c.is_uppercase()) {
        CAPS_W_EM
    } else {
        CHAR_W_EM
    };
    if let Some(a) = attrs {
        if a.get("font-weight").map(String::as_str) == Some("bold") {
            w += BOLD_W_EM;
        }
        if size != 0.0 {
            w += read::attr_f(a, "letter-spacing", 0.0) / size;
        }
    }
    w
}

/// The half-width and half-height of a caption set on `lines` at `size` - the block `label()` records. `char_w` is the width per character
/// in ems, the standard's unless a caller measured its text as wider.
///
/// Research: caption block size - NONE: the text metrics applied, the widest line by its characters and the lines by their pitch
#[must_use]
#[expect(clippy::cast_precision_loss, reason = "Python's `len()` as a float")]
pub fn block_half(lines: &[String], size: f64, char_w: f64) -> (f64, f64) {
    // the lengths are whole numbers, so the largest is the largest whichever comes first
    let widest = lines
        .iter()
        .map(|l| l.chars().count() as f64)
        .fold(0.0, f64::max);
    let w = widest * size * char_w;
    let h = size * LINE_H_EM + (lines.len() as f64 - 1.0) * size * PITCH_EM;
    (w / 2.0, h / 2.0)
}

/// The arguments every sheet's picture is drawn with (`resvg --width 2400 --serif-family "DejaVu Serif"`).
///
/// Research: the sheets' face and width - CONVENTION: every sheet's picture is drawn 2400 px wide, its serif lettering in `DejaVu Serif` - a display choice of the sheets, not of the world
#[must_use]
pub fn render_args() -> Vec<String> {
    ["--width", "2400", "--serif-family", "DejaVu Serif"]
        .map(str::to_owned)
        .to_vec()
}

/// Render a sheet's placed text to `png` with resvg, as every sheet's gen does - the `resvg` crate in process (`raster/render.rs`, the
/// binary the Python ran, as a library), where the Python wrote a temporary file beside the picture for the binary to read.
///
/// # Errors
/// The renderer's refusal, or the picture that could not be written (Python's `OSError`, its class and words).
pub fn render(src: &str, png: &std::path::Path) -> Result<(), Error> {
    let bytes = crate::raster::render::png(src, &render_args())?;
    std::fs::write(png, bytes).map_err(|e| crate::py::os_error(&e, &png.to_string_lossy()))
}
