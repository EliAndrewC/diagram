//! A hand-drawn sheet as an interactive page: the SVG's own `data-kind` tags are the class side list (`interactive/sheet.py`'s page half,
//! feature 262; ported by feature 449 T150, the engine port's step 2; since its part B the six pool generators' pages are written here, by
//! `l7r-mode-a sheet-page` ([`cli`]), and the Python's page half is deleted).
//!
//! The GM, 2026-09-26: *"the main important thing is that the labels and the features on the building diagram for each magistracy have a
//! common source, such that changing that source in one place is enough to change it downstream."* A subtree with no differently-tagged
//! descendant is one piece, verbatim; a group holding one is descended into and each piece emitted inside COPIES of its ancestors' opening
//! tags, so a `transform` or an inherited `fill` still applies, in the sheet's paint order. A part lights with what it is part of (feature
//! 264): each piece carries the kinds of its tagged ancestors and any `data-part-of`.
//!
//! Research:
//!     the sheet's pieces - NONE: the sheet's own bytes regrouped by their tags, deciding nothing about a building

use std::collections::HashSet;
use std::path::Path;
use std::sync::LazyLock;

use fancy_regex::Regex;
use l7r_gate_registry::about::FeatureClass;
use l7r_gate_research::pyre::py;
use l7r_gate_research::Error;

use super::{parse, Node, DEFS};
use crate::page::{ink_census, unregistered_classes, Page};
use crate::raster::Host;
use crate::tags::{ClsTag, NOT_HIGHLIGHTED};

static ID: LazyLock<Regex> = LazyLock::new(|| py(r#"\sid="[^"]*""#));

/// One piece of the page: its drawn string, its kind, and the kinds it is a part of (`sheet.Piece`).
pub type Piece = (String, ClsTag, Vec<String>);

/// Whether any descendant carries a kind of its own - the one reason to descend rather than emit whole (`Node.tagged_below`).
fn tagged_below(node: &Node<'_>) -> bool {
    node.children
        .iter()
        .any(|c| !c.name.is_empty() && (c.kind().is_some() || tagged_below(c)))
}

fn tag(kind: Option<&str>) -> ClsTag {
    kind.map_or(ClsTag::Unruled, ClsTag::key)
}

/// The kinds a piece of `kind` is a part of: every distinct kind of its lineage but its own and the ruling (`sheet._within`).
fn within(kind: Option<&str>, lineage: &[String]) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for k in lineage {
        if Some(k.as_str()) != kind && k != NOT_HIGHLIGHTED && !out.contains(k) {
            out.push(k.clone());
        }
    }
    out
}

/// `s` inside copies of its ancestors' opening tags; an ancestor's `id` rides on its FIRST copy only, so the page never carries an id
/// twice because of the reader (`sheet._wrapped`).
fn wrapped(s: &str, chain: &[&Node<'_>], seen: &mut HashSet<String>) -> String {
    let mut out = String::new();
    for a in chain {
        let mut open = a.open.to_owned();
        if let Some(m) = ID.find(a.open).ok().flatten() {
            let id = m.as_str().to_owned();
            if seen.contains(&id) {
                open = open.replacen(&id, "", 1);
            } else {
                seen.insert(id);
            }
        }
        out += &open;
    }
    out += s;
    for a in chain.iter().rev() {
        out += a.close;
    }
    out
}

/// (fragment, kind, part of) for `node` in document order (`sheet._walk`).
fn walk<'a>(
    node: &'a Node<'a>,
    chain: &mut Vec<&'a Node<'a>>,
    inherited: Option<&'a str>,
    seen: &mut HashSet<String>,
    lineage: &[String],
    out: &mut Vec<Piece>,
) {
    if node.name.is_empty() {
        if !l7r_shared::py_text::strip(node.text).is_empty() {
            out.push((
                wrapped(node.text, chain, seen),
                tag(inherited),
                within(inherited, lineage),
            ));
        }
        return;
    }
    let kind = node.kind().or(inherited);
    if node.name == DEFS {
        out.push((
            wrapped(&node.source(), chain, seen),
            ClsTag::key(NOT_HIGHLIGHTED),
            Vec::new(),
        ));
        return;
    }
    let mut deeper = lineage.to_vec();
    deeper.extend(
        [node.part_of(), node.kind()]
            .into_iter()
            .flatten()
            .map(str::to_owned),
    );
    if !node.children.is_empty() && tagged_below(node) {
        chain.push(node);
        for child in &node.children {
            walk(child, chain, kind, seen, &deeper, out);
        }
        chain.pop();
        return;
    }
    out.push((
        wrapped(&node.source(), chain, seen),
        tag(kind),
        within(kind, &deeper),
    ));
}

/// The sheet as the page's pieces in paint order (`sheet.pieces`): the `<svg>` opening tag first and its closing last, both ruled
/// not-highlighted - the page reads the viewBox from the first and inserts its layers before the one holding `</svg>`.
///
/// # Errors
/// The reader's refusal of a sheet that does not balance.
pub fn pieces(svg: &str) -> Result<Vec<Piece>, Error> {
    let root = parse(svg)?;
    let mut out: Vec<Piece> = vec![(
        root.open.to_owned(),
        ClsTag::key(NOT_HIGHLIGHTED),
        Vec::new(),
    )];
    let mut seen = HashSet::new();
    for child in &root.children {
        walk(child, &mut Vec::new(), None, &mut seen, &[], &mut out);
    }
    out.push((
        root.close.to_owned(),
        ClsTag::key(NOT_HIGHLIGHTED),
        Vec::new(),
    ));
    Ok(out)
}

/// What a sheet's tags amount to (`sheet.Census`): drawn elements per kind, the ink with no kind (capped), and the kinds the registry
/// does not know.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Census {
    pub counts: Vec<(String, i64)>,
    pub unclassed: Vec<String>,
    pub unregistered: Vec<String>,
}

/// The completeness facts the pool holds every sheet to (`sheet.census`, spec FR-006).
///
/// # Errors
/// [`pieces`]'s.
pub fn census(svg: &str, registry: &[FeatureClass]) -> Result<Census, Error> {
    let ps = pieces(svg)?;
    let (strings, tags): (Vec<String>, Vec<ClsTag>) =
        ps.into_iter().map(|(s, t, _)| (s, t)).unzip();
    let (counts, unclassed) = ink_census(&strings, &tags);
    let unregistered = unregistered_classes(&counts, registry);
    Ok(Census {
        counts,
        unclassed,
        unregistered,
    })
}

/// `str.title()`: each run of cased letters with its first letter titlecased and the rest lowercased.
#[must_use]
pub fn py_title(text: &str) -> String {
    let mut out = String::new();
    let mut cased = false;
    for c in text.chars() {
        if cased {
            out.extend(c.to_lowercase());
        } else {
            out.extend(c.to_uppercase());
        }
        cased = c.is_lowercase() || c.is_uppercase();
    }
    out
}

/// `ochiba-magistracy.svg` -> `Ochiba Magistracy`: the page's browser-tab title (`sheet.title_of`); the sheet's own title is drawn.
#[must_use]
pub fn title_of(path: &str) -> String {
    let base = path.rsplit('/').next().unwrap_or(path);
    let stem = base.rsplit_once('.').map_or(base, |(s, _)| s);
    py_title(&stem.replace('-', " "))
}

/// `<map>.html` beside `<map>.svg` (or in `out`, the map's notes still read beside the sheet: the generation cache's staging folder, feature
/// 449 T221), from the sheet's own tags, and the sheet's census for the caller to report (`sheet.write_sheet_page`).
/// `with_raster` defaults to the render condition (no picture under `DIAGRAM_SKIP_RENDER=1`, feature 208); `svg` is the sheet's text when
/// it is not the file's (a hand sheet's captions placed, feature 286). THE SHEET MARKS ITSELF (the GM 2026-09-27: highlighted text became
/// unreadable): `data-sheet` keeps a sheet's lit text in the map's ink.
///
/// # Errors
/// The sheet unreadable or refused, or the page's refusals.
///
/// Research: the sheet marks itself - CONVENTION: `data-sheet` keeps a sheet's lit labels in the map's ink, its labels sitting on their own features' fills (the GM 2026-09-27)
pub fn write_sheet_page(
    tree: &Path,
    host: &Host,
    svg_path: &str,
    registry: &[FeatureClass],
    with_raster: Option<bool>,
    svg: Option<&str>,
    out: Option<&Path>,
) -> Result<Census, Error> {
    let with_raster = with_raster.unwrap_or_else(|| host.var("DIAGRAM_SKIP_RENDER") != Some("1"));
    let read;
    let svg = if let Some(s) = svg {
        s
    } else {
        read = l7r_gate_core::record::read_text(Path::new(svg_path))
            .map_err(|e| crate::py::os_error(&e, svg_path))?;
        read.as_str()
    };
    let ps = pieces(svg)?;
    let mut strings: Vec<String> = Vec::with_capacity(ps.len());
    let mut tags = Vec::with_capacity(ps.len());
    let mut kinds = Vec::with_capacity(ps.len());
    for (s, t, k) in ps {
        strings.push(s);
        tags.push(t);
        kinds.push(k);
    }
    strings[0] = strings[0].replacen("<svg ", "<svg data-sheet=\"mode-a\" ", 1);
    let cut: String = svg_path
        .chars()
        .take(svg_path.chars().count().saturating_sub(4))
        .collect();
    let name = title_of(svg_path);
    let page = Page {
        strings: strings.clone(),
        tags: tags.clone(),
        name: &name,
        meta: None,
        manifest: None,
        notes: crate::notes::MapNotes::default(),
        with_raster,
        registry,
        within: Some(&kinds),
    };
    let html = out.map_or_else(
        || std::path::PathBuf::from(format!("{cut}.html")),
        |dir| {
            let base = cut.rsplit('/').next().unwrap_or(&cut);
            dir.join(format!("{base}.html"))
        },
    );
    let notes = std::path::PathBuf::from(format!("{cut}.notes.md"));
    crate::page::write_html_beside(tree, host, &html, Some(&notes), page)?;
    let (counts, unclassed) = ink_census(&strings, &tags);
    let unregistered = unregistered_classes(&counts, registry);
    Ok(Census {
        counts,
        unclassed,
        unregistered,
    })
}

pub mod cli;

#[cfg(test)]
mod tests;
