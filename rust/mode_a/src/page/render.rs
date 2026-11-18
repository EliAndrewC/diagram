//! The whole page as one string (`page.render_page`, `write_html`, `raster_wanted`, features 134, 156, 200, 208, 222, 262, 297, 319;
//! ported by feature 449 T150).
//!
//! THE OFF-MAP INK IS DROPPED FIRST (feature 200, FR-001): invisible by construction. THE PICTURE AND THE ID MAP RENDER WHILE THE DATA IS
//! BUILT (features 222, 297): each a resvg process this one waits on. A HAMLET'S FEATURE MODALS ARE THE SAME ON EVERY MAP (feature 319,
//! plan D10): its notes' features and the per-map sentences go on the title card. NO HEADER ON THE PAGE (the GM, 2026-08-28: "we can get
//! rid of the entire header").
//!
//! Research:
//!     the page's assembly - NONE: the page's parts put together in their order, each part's decisions claimed where it is made

use std::path::Path;
use std::sync::{Mutex, PoisonError};

use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::Error;
use l7r_guard::shared::html_text::escape;
use serde_json::{json, Map, Value};

use super::hits::{hit_layer, hit_regions, part_of, wrap};
use super::{asset, explanations, glossary_for, meta_str, present_classes};
use crate::notes::MapNotes;
use crate::place::{
    homestead_grove_default, lane_default, place_card, retirement_fact, windbreak_default,
    HOMESTEAD_GROVE, LANE, WINDBREAK,
};
use crate::py::fmt_g;
use crate::raster::{self, Host, IdMap, Viewbox};
use crate::tags::{ClsTag, PLACE};

/// What one page is written from: the drawn strings and their tags, the tab's title, the map's record and manifest where it has them, its
/// notes, whether it gets its picture, its vocabulary, and (a Mode A sheet's) the kinds each string is a part of.
pub struct Page<'a> {
    pub strings: Vec<String>,
    pub tags: Vec<ClsTag>,
    pub name: &'a str,
    pub meta: Option<&'a Map<String, Value>>,
    pub manifest: Option<&'a Value>,
    pub notes: MapNotes,
    pub with_raster: bool,
    pub registry: &'a [FeatureClass],
    pub within: Option<&'a [Vec<String>]>,
}

/// Whether the page gets its picture: asked for (the render condition, feature 208) AND a viewBox to render.
#[must_use]
pub fn raster_wanted(with_raster: bool, vb: Option<Viewbox>) -> bool {
    with_raster && vb.is_some()
}

/// `zip(a, b, strict=True)`'s refusal of two lists of different lengths.
fn strict(a: usize, b: usize) -> Result<(), Error> {
    match a.cmp(&b) {
        std::cmp::Ordering::Equal => Ok(()),
        std::cmp::Ordering::Greater => Err(Error::new(
            "ValueError",
            "zip() argument 2 is shorter than argument 1",
        )),
        std::cmp::Ordering::Less => Err(Error::new(
            "ValueError",
            "zip() argument 2 is longer than argument 1",
        )),
    }
}

/// The per-map sentences on a hamlet's card and the defaults a non-hamlet's classes take where its notes say nothing (spec FR-021,
/// features 261, 291).
///
/// Research: a class's map default - CONVENTION: a lane's destination, a windbreak's side and a farmstead grove's sides filled only where the notes say nothing, never on a hamlet's modals (spec FR-021, features 261, 291, 319)
fn defaults(
    data: &mut Map<String, Value>,
    meta: &Map<String, Value>,
    hamlet: bool,
    notes: &MapNotes,
) {
    let scale = meta_str(meta, "scale");
    let fills: [(&str, String); 3] = [
        (LANE, lane_default(&scale, &notes.place)),
        (WINDBREAK, windbreak_default(meta)),
        (HOMESTEAD_GROVE, homestead_grove_default(meta)),
    ];
    if hamlet {
        return;
    }
    for (key, text) in fills {
        if let Some(Value::Object(entry)) = data.get_mut(key) {
            let empty = entry
                .get("on_this_map")
                .is_none_or(|v| !l7r_guard::shared::pyjson::truthy(v));
            if empty {
                entry.insert("on_this_map".to_owned(), Value::String(text));
            }
        }
    }
}

/// The title card's choices and facts on a hamlet (plan D10): each choice the map made, its modal's entry riding in the data; then this
/// settlement's own sentences.
///
/// Research: the hamlet's title card - CONVENTION: its choices, each value a modal, then its own facts (feature 319, plan D10)
fn hamlet_card(
    tree: &Path,
    data: &mut Map<String, Value>,
    meta: &Map<String, Value>,
    present: &std::collections::BTreeSet<String>,
    notes: &MapNotes,
) -> Result<(), Error> {
    let choices = l7r_gate_registry::choices::made(tree, meta)?;
    let reg = l7r_gate_registry::choices::registry_for(tree, meta)?;
    let keys = reg.iter().map(|fc| fc.key.clone()).collect();
    let extra = explanations(tree, &keys, &MapNotes::default(), &reg, meta)?;
    let facts: Vec<String> = [
        if present.contains(WINDBREAK) {
            windbreak_default(meta)
        } else {
            String::new()
        },
        if present.contains(LANE) {
            lane_default("hamlet", &notes.place)
        } else {
            String::new()
        },
        retirement_fact(meta),
    ]
    .into_iter()
    .filter(|f| !f.is_empty())
    .collect();
    if let Some(Value::Object(card)) = data.get_mut(PLACE) {
        card.insert("choices".to_owned(), Value::Array(choices));
    }
    for (k, v) in extra {
        data.insert(k, v);
    }
    if let Some(Value::Object(card)) = data.get_mut(PLACE) {
        card.insert("facts".to_owned(), json!(facts));
    }
    Ok(())
}

/// The fixed parts of the page around its map and its data.
///
/// Research: the modal's tabs - CONVENTION: About, Guesses, Depiction and References in one dialog of one size (the GM 2026-10-03, 2026-10-04)
const DIALOG: &str = concat!(
    "<nav id=\"zoom\" aria-label=\"zoom\"><button type=\"button\" data-z=\"in\" title=\"zoom in (+)\">+</button>",
    "<button type=\"button\" data-z=\"out\" title=\"zoom out (-)\">-</button>",
    "<button type=\"button\" data-z=\"fit\" title=\"fit the whole map (0)\">fit</button></nav>\n",
    "<div id=\"shade\" hidden></div>\n",
    "<dialog id=\"explain\" aria-labelledby=\"x-name\"><article>",
    "<header><h2 id=\"x-name\"></h2><nav id=\"x-tabs\" role=\"tablist\">",
    "<button type=\"button\" role=\"tab\" id=\"t-about\" data-tab=\"about\" aria-controls=\"p-about\">About</button>",
    "<button type=\"button\" role=\"tab\" id=\"t-guesses\" data-tab=\"guesses\" aria-controls=\"p-guesses\">Guesses</button>",
    "<button type=\"button\" role=\"tab\" id=\"t-depict\" data-tab=\"depict\" aria-controls=\"p-depict\">Depiction</button>",
    "<button type=\"button\" role=\"tab\" id=\"t-refs\" data-tab=\"refs\" aria-controls=\"p-refs\">References</button></nav></header>",
    "<div id=\"x-panels\"><div id=\"p-about\" role=\"tabpanel\" aria-labelledby=\"t-about\">",
    "<section id=\"x-about\"></section><section id=\"x-what\"></section><section id=\"x-why\"></section>",
    "<section id=\"x-choices\" class=\"choices\" hidden></section><section id=\"x-facts\" class=\"facts\" hidden></section>",
    "<section id=\"x-onmap\" class=\"onmap\" hidden></section><section id=\"x-basis\" class=\"basis\" hidden></section>",
    "<section id=\"x-siblings\"></section></div>",
    "<div id=\"p-guesses\" role=\"tabpanel\" aria-labelledby=\"t-guesses\" hidden><ul id=\"x-guesses\"></ul></div>",
    "<div id=\"p-depict\" role=\"tabpanel\" aria-labelledby=\"t-depict\" hidden><section id=\"x-depiction\"></section><section id=\"d-list\"></section></div>",
    "<div id=\"p-refs\" role=\"tabpanel\" aria-labelledby=\"t-refs\" hidden><section id=\"r-list\"></section></div></div>",
    "<footer><button id=\"x-close\" type=\"button\">Close</button></footer>",
    "</article></dialog>\n",
    "<div id=\"tip\" role=\"tooltip\" hidden></div>\n",
);

/// The picture and the id map, rendered at once while `build` runs on this thread (features 222, 297).
type Raster = (Vec<u8>, IdMap);

/// The two renders run on their own threads, each result set once; a render thread that panicked is the scope's panic, carried here.
fn rendered_beside<T>(
    host: &Host,
    picture_doc: Option<String>,
    id_doc: &(String, Vec<String>, bool),
    build: impl FnOnce() -> Result<T, Error>,
) -> Result<(T, Option<Raster>), Error> {
    let Some(picture_doc) = picture_doc else {
        return Ok((build()?, None));
    };
    let picture: Mutex<Result<Vec<u8>, Error>> = Mutex::new(Ok(Vec::new()));
    let id_map: Mutex<Result<IdMap, Error>> = Mutex::new(Ok((Vec::new(), Vec::new())));
    let data = std::thread::scope(|scope| {
        scope.spawn(|| {
            *picture.lock().unwrap_or_else(PoisonError::into_inner) =
                raster::picture(host, &picture_doc, raster::RASTER_R, None);
        });
        let (svg, keys, crisp) = id_doc;
        scope.spawn(|| {
            *id_map.lock().unwrap_or_else(PoisonError::into_inner) =
                raster::id_map(host, svg, keys, *crisp);
        });
        build()
    })?;
    let pic = picture
        .into_inner()
        .unwrap_or_else(PoisonError::into_inner)?;
    let id = id_map
        .into_inner()
        .unwrap_or_else(PoisonError::into_inner)?;
    Ok((data, Some((pic, id))))
}

/// The whole page as one string (`page.render_page`); `tree` the repository its assets, record and vocabulary are read from.
///
/// # Errors
/// What the Python raised: a figure its `float()` refused, a malformed modal condition, the assets unreadable, a render that failed.
///
/// Research: the page's assembly - CONVENTION: the off-map ink dropped (invisible, feature 200), a hamlet's per-map facts on its title card so its modals are the same on every map (feature 319, plan D10), and no header (the GM 2026-08-28)
pub fn render_page(tree: &Path, host: &Host, p: &Page<'_>) -> Result<String, Error> {
    let empty = Map::new();
    let meta = p.meta.unwrap_or(&empty);
    strict(p.strings.len(), p.tags.len())?;
    if let Some(within) = p.within {
        strict(p.strings.len(), within.len())?;
    }
    let present = present_classes(&p.tags);
    let vb = match p.strings.first() {
        Some(first) => raster::viewbox_of(first)?,
        None => None,
    };
    let mut strings = p.strings.clone();
    if let Some(vb) = vb {
        for (s, t) in strings.iter_mut().zip(&p.tags) {
            if !t.is_unruled() && !t.is_ruled_out() {
                *s = raster::drop_offmap(s, vb)?;
            }
        }
    }
    let mut wrapped: Vec<String> = strings
        .iter()
        .zip(&p.tags)
        .map(|(s, t)| wrap(s, t))
        .collect::<Result<_, _>>()?;
    if let Some(within) = p.within {
        wrapped = wrapped
            .iter()
            .zip(within)
            .map(|(w, ks)| part_of(w, ks))
            .collect::<Result<_, _>>()?;
    }
    let wanted = raster_wanted(p.with_raster, vb);
    let picture_doc = wanted.then(|| {
        raster::without_text(&wrapped.join("\n").replacen("<svg ", "<svg id=\"map\" ", 1))
    });
    // the hit regions right after the SHEET (the first ruled-out string), under everything drawn
    let sheet = p.tags.iter().position(ClsTag::is_ruled_out).unwrap_or(0);
    // `list.insert` past the end appends
    let at = (sheet + 1).min(wrapped.len());
    wrapped.insert(at, hit_regions(p.manifest, &present)?);
    let close = wrapped
        .iter()
        .rposition(|w| w.contains("</svg>"))
        .unwrap_or(wrapped.len());
    wrapped.insert(close, hit_layer(&strings, &p.tags, p.manifest)?);
    let svg = wrapped.join("\n").replacen("<svg ", "<svg id=\"map\" ", 1);
    let hamlet = meta_str(meta, "scale") == "hamlet";
    let build = || -> Result<Map<String, Value>, Error> {
        let notes = if hamlet {
            MapNotes {
                place: p.notes.place.clone(),
                features: Vec::new(),
            }
        } else {
            p.notes.clone()
        };
        let mut data = explanations(tree, &present, &notes, p.registry, meta)?;
        let manifest = p.manifest.cloned().unwrap_or_else(|| json!({}));
        let card = place_card(tree, meta, &present, &p.notes, &manifest)?;
        let has_card = card.is_some();
        if let Some(card) = card {
            data.insert(PLACE.to_owned(), card);
        }
        if hamlet && has_card {
            hamlet_card(tree, &mut data, meta, &present, &p.notes)?;
        }
        defaults(&mut data, meta, hamlet, &p.notes);
        Ok(data)
    };
    let id_doc = (svg.clone(), raster::class_keys(&svg), p.within.is_some());
    let (data, raster_out) = rendered_beside(host, picture_doc, &id_doc, build)?;
    let (payload, svg) = with_raster(raster_out, vb, svg);
    crate::reads::asset(tree, "glossary.json");
    let terms = l7r_gate_research::glossary::load(tree)?;
    let glossary = glossary_for(&data, &terms);
    let blob = l7r_guard::shared::pyjson::dumps(
        &json!({"classes": data, "glossary": glossary, "raster": payload}),
        None,
        false,
    )
    .replace("</", "<\\/");
    document(tree, p.name, &svg, &blob)
}

/// The raster's payload and the page's map with the picture's image above the sheet (`render_page`'s, feature 200): `"r": 0` and the map
/// as it was where no picture was drawn. The image rides below the first class group, with no href: `page.js` sets it, so its `load`
/// cannot fire before anyone listens (FR-016).
///
/// Research: the picture's place - CONVENTION: the image above the sheet and below the first class group (feature 200)
fn with_raster(raster_out: Option<Raster>, vb: Option<Viewbox>, svg: String) -> (Value, String) {
    let mut payload = json!({"r": 0});
    let mut svg = svg;
    // both are drawn together, so the picture is never carried without its id map (the Python asserts as much)
    if let (Some((pic, (idpng, palette))), Some(vb)) = (raster_out, vb) {
        let palette: Map<String, Value> = palette
            .into_iter()
            .map(|(k, v)| (k, Value::String(v)))
            .collect();
        payload = json!({
            "r": raster::RASTER_R, "step": raster::PALETTE_STEP, "palette": palette,
            "picture": raster::data_uri(raster::PICTURE_MIME, &pic), "idmap": raster::data_uri("image/png", &idpng),
        });
        let image = format!(
            "<g class=\"raster\"><image id=\"raster\" x=\"{}\" y=\"{}\" width=\"{}\" height=\"{}\" style=\"pointer-events: none\"/></g>",
            fmt_g(vb.0),
            fmt_g(vb.1),
            fmt_g(vb.2),
            fmt_g(vb.3)
        );
        svg = match svg.find("<g class=\"f ") {
            Some(at) => format!("{}{image}{}", &svg[..at], &svg[at..]),
            None => svg.replacen("</svg>", &format!("{image}</svg>"), 1),
        };
    }
    (payload, svg)
}

/// The page around its map and its data: the CSS and the script inlined, the title escaped (`render_page`'s return).
fn document(tree: &Path, name: &str, svg: &str, blob: &str) -> Result<String, Error> {
    let (css, js) = (asset(tree, "page.css")?, asset(tree, "page.js")?);
    Ok(format!(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n\
         <title>{} - interactive map</title>\n<style>\n{css}</style>\n</head>\n<body>\n<main id=\"stage\">\n{svg}\n</main>\n{DIALOG}\
         <script id=\"classes\" type=\"application/json\">{blob}</script>\n<script>\n{js}</script>\n</body>\n</html>\n",
        escape(name, true)
    ))
}

/// `<base>.html` beside the map's other outputs (`page.write_html`): the map's `<base>.notes.md` read from the output path alone, so a
/// stale or foreign notes file is never picked up.
///
/// # Errors
/// [`render_page`]'s, or the file unwritable.
pub fn write_html(tree: &Path, host: &Host, path: &Path, mut p: Page<'_>) -> Result<(), Error> {
    let text = path.to_string_lossy();
    if let Some(base) = text.strip_suffix(".html") {
        p.notes = crate::notes::read_map_notes(Path::new(&format!("{base}.notes.md")));
    }
    // THE FILE IS OPENED BEFORE THE PAGE IS RENDERED, as the Python's `with open(path, "w")` opened it (feature 449 T150's differential),
    // so an unwritable path refuses before any render - but NOT EMPTIED until the page is in hand (FIXED, feature 449 T183, T150's
    // finding: the Python's open emptied it, and a render that refused left an empty page where the last good one had been). A refused
    // render leaves the path as it found it: the last page, or no file where there was none
    let io = |e: std::io::Error| crate::py::os_error(&e, &text);
    let existed = path.exists();
    let mut file = std::fs::OpenOptions::new()
        .write(true)
        .create(true)
        .truncate(false)
        .open(path)
        .map_err(io)?;
    let page = match render_page(tree, host, &p) {
        Ok(page) => page,
        Err(e) => {
            drop(file);
            if !existed {
                let _ = std::fs::remove_file(path);
            }
            return Err(e);
        }
    };
    file.set_len(0).map_err(io)?;
    std::io::Write::write_all(&mut file, page.as_bytes()).map_err(io)
}
