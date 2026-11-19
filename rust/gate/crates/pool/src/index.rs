//! THE POOL INDEX, `pool/index.html` (feature 449 T220; the derivation's `index_row`, one a map): every map folder of both trees, the
//! hamlets and the frozen exhibits included, grouped by tree and tier, each linking to its rendered page where its folder holds one (its
//! picture where it holds no page). Written from the walk, never from a second listing; composed whole each run and rewritten only when it
//! differs from the page on disk, so a run that changed nothing leaves the file and its time alone. The page names no time or run, so
//! the same pool always composes the same page.
//!
//! The index it replaces listed 6 of the pool's 30 maps (measured 2026-11-19 on the page `make pool-index` had written: the six Mode A
//! sheets alone); the page was designed fresh for this phase, not carried over.
//!
//! Research: plumbing - NONE: lists the pool's maps and links their pages, and decides nothing about a place

use std::fmt::Write as _;
use std::path::Path;

use crate::walk::{Kind, Map, Walk, LEGACY, LIVE};

/// The index, from the tree's root.
pub const INDEX: &str = "pool/index.html";

/// The page's own look: plain, readable, light and dark.
const STYLE: &str = "\
:root{--bg:#fbfaf7;--fg:#1d1c1a;--muted:#6b675f;--rule:#dedad2;--link:#1f5f8b;--tag:#efece5}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#e9e6df;--muted:#a19c92;--rule:#34322e;--link:#8cc4ec;--tag:#24231f}}
body{margin:0;background:var(--bg);color:var(--fg);font:16px/1.5 system-ui,-apple-system,'Segoe UI',sans-serif}
main{max-width:52rem;margin:0 auto;padding:1.5rem 1rem 3rem}
h1{font-size:1.6rem;margin:0 0 .25rem}
h2{font-size:1.25rem;margin:2rem 0 .25rem;border-bottom:1px solid var(--rule);padding-bottom:.25rem}
h3{font-size:1rem;margin:1.25rem 0 .25rem;color:var(--muted);font-weight:600}
p{margin:.25rem 0}
.muted,.where{color:var(--muted)}
.where{font-size:.85rem;font-weight:400;margin-left:.5rem}
ul{list-style:none;margin:0;padding:0}
li{display:flex;flex-wrap:wrap;gap:.25rem .75rem;align-items:baseline;padding:.35rem 0;border-bottom:1px solid var(--rule)}
li .name{font-weight:600;min-width:12rem}
.kind{font-size:.8rem;background:var(--tag);border-radius:.25rem;padding:0 .4rem}
.links{font-size:.9rem}
a{color:var(--link)}
";

/// `&`, `<`, `>` and `"` escaped for a text node or a quoted attribute.
fn escape(text: &str) -> String {
    text.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
}

/// The path of a map's file from `pool/`, where the index stands.
fn href(map: &Map, suffix: &str) -> String {
    let inner = format!("{}/{}/{}{suffix}", map.tier, map.name, map.name);
    if map.tree == LIVE {
        inner
    } else {
        format!("../{}/{inner}", map.tree)
    }
}

/// One map's row: its name (its page's link where it has one), its kind, and its picture and notes where its folder holds them.
fn row(map: &Map) -> String {
    let name = escape(&map.name);
    let shown = if map.has(".html") {
        format!(
            "<a class=\"name\" href=\"{}\">{name}</a>",
            escape(&href(map, ".html"))
        )
    } else {
        format!("<span class=\"name\">{name}</span>")
    };
    let mut links = Vec::new();
    if !map.has(".html") {
        links.push("<span class=\"muted\">no rendered page</span>".to_owned());
    }
    // a hamlet's own drawing is the Rust driver's `<map>.driver.svg`
    for (suffix, what) in [
        (".png", "picture"),
        (".svg", "drawing"),
        (".driver.svg", "driver drawing"),
        (".notes.md", "notes"),
    ] {
        if map.has(suffix) && !(suffix == ".svg" && map.has(".png")) {
            links.push(format!(
                "<a href=\"{}\">{what}</a>",
                escape(&href(map, suffix))
            ));
        }
    }
    format!(
        "<li>{shown} <span class=\"kind\">{}</span> <span class=\"links\">{}</span></li>\n",
        map.kind.label(),
        links.join(" &middot; ")
    )
}

/// `n` and its noun, plural past one.
fn many(n: usize, one: &str, more: &str) -> String {
    format!("{n} {}", if n == 1 { one } else { more })
}

/// The whole page from the walk, one row a map counted (`index_row`) to the map's tree.
#[must_use]
pub fn page(walk: &mut Walk) -> String {
    let maps = &walk.maps;
    let counts = &mut walk.counts;
    let live = maps.iter().filter(|m| m.tree == LIVE).count();
    let mut out = String::from(
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n\
         <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n<title>Map pool</title>\n<style>\n",
    );
    out += STYLE;
    let _ = write!(
        out,
        "</style>\n</head>\n<body>\n<main>\n<h1>Map pool</h1>\n<p>{}: {} in the live pool, {} in the frozen exhibits. Written by \
         <code>make pool-index</code> from the pool walk.</p>\n",
        many(maps.len(), "map", "maps"),
        live,
        maps.len() - live
    );
    let unclassified = maps.iter().filter(|m| m.kind == Kind::Report).count();
    if unclassified > 0 {
        let _ = writeln!(
            out,
            "<p class=\"muted\">{} the walk could not classify (marked unclassified below; <code>make pool-index</code> says why).</p>",
            many(unclassified, "folder", "folders")
        );
    }
    for (tree, title, about) in [
        (LIVE, "Live pool", "regenerated by their engines"),
        (LEGACY, "Frozen exhibits", "hand-authored, kept as they are"),
    ] {
        let _ = writeln!(
            out,
            "<h2>{title}<span class=\"where\">{tree}/ - {about}</span></h2>"
        );
        let mut tier: Option<&str> = None;
        let mut any = false;
        for map in maps.iter().filter(|m| m.tree == tree) {
            if tier != Some(map.tier.as_str()) {
                if tier.is_some() {
                    out += "</ul>\n";
                }
                let n = maps
                    .iter()
                    .filter(|m| m.tree == tree && m.tier == map.tier)
                    .count();
                let _ = write!(
                    out,
                    "<h3>{}<span class=\"where\">{}</span></h3>\n<ul>\n",
                    escape(&map.tier),
                    many(n, "map", "maps")
                );
                tier = Some(map.tier.as_str());
            }
            counts.add(map.tree, "index_row", 1);
            out += &row(map);
            any = true;
        }
        out += if any {
            "</ul>\n"
        } else {
            "<p class=\"muted\">No maps.</p>\n"
        };
    }
    out += "</main>\n</body>\n</html>\n";
    out
}

/// The page composed and compared with the one at [`INDEX`]: `(the page, whether it differs)`. Nothing is written.
#[must_use]
pub fn compare(root: &Path, walk: &mut Walk) -> (String, bool) {
    let page = page(walk);
    let differs = std::fs::read_to_string(root.join(INDEX)).ok().as_deref() != Some(page.as_str());
    (page, differs)
}

/// Write the index where it differs from the page on disk (a temporary file renamed into place, so a reader sees the old page or the
/// new one, never part): whether it was written.
///
/// # Errors
/// The temporary file cannot be written or renamed (no `pool/`, or no permission).
pub fn write(root: &Path, walk: &mut Walk) -> std::io::Result<bool> {
    let (page, differs) = compare(root, walk);
    if !differs {
        return Ok(false);
    }
    let path = root.join(INDEX);
    let tmp = path.with_extension(format!("html.tmp{}", std::process::id()));
    std::fs::write(&tmp, page)?;
    std::fs::rename(&tmp, &path).inspect_err(|_| {
        let _ = std::fs::remove_file(&tmp);
    })?;
    Ok(true)
}

#[cfg(test)]
mod tests;
