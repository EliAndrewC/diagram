//! The pieces every page of the record's site is made of (`record/site_pages.py`, features 301, 303; ported by feature 449 T148,
//! `ask:449-phase4-slices`): the page shell, the trail of links at its top, a listing of questions, the pager, and the navigation tree as
//! data. The site's layout (spec 303 plan D6): `index.html` home; `findings/<section>.html` and `drawing/<section>.html` a section in each
//! half; `q/<heading id>.html` a question page of either half, flat so a regrouping moves no URL; `tags/<facet>-<tag>.html`;
//! `sources/<key>.html` and `sources/index.html` the registry; `all.html`, `nav.js`, `assets/`. Its pieces are pinned through the whole
//! site's pages against the Python's (`site/cases.json`).

use serde_json::{json, Value};

use crate::record::contents::{self as ct, Section, Tag, Tags, Vocabulary};
use crate::record::questions::Record;
use crate::record::site_links::{section_dir, QUESTION_DIR};
use crate::sources::linkify;
use l7r_shared::html_text::escape;

pub const TITLE: &str = "The research record";
/// The two halves of the record, in the order they are read; a section is shown in a half only when it, or a subsection, holds a page of
/// that half (spec 303 FR-012, FR-013).
pub const HALVES: [(&str, &str); 2] = [
    ("research", "The research"),
    ("drawing", "How our maps draw it"),
];
pub const REGISTRY_GROUP: &str = "Sources";
pub const TAGS_GROUP: &str = "Tags";

/// A facet's name as a page shows it.
#[must_use]
pub fn facet_name(facet: &str) -> &'static str {
    match facet {
        "subject" => "Subject",
        "setting" => "Setting",
        _ => "Level",
    }
}

/// A question page or a registry entry: one small page.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Item {
    pub id: String,
    pub html: String,
    pub title: String,
    pub lead: String,
}

fn esc(text: &str) -> String {
    escape(text, true)
}

/// From a site file to the site root: "" for `index.html`, `../` for `q/x.html`.
#[must_use]
pub fn root_of(here: &str) -> String {
    "../".repeat(here.matches('/').count())
}

/// The text a site page writes before its content and after it: the head, the navigation the script draws, and `<main>` around the
/// content. `open_keys` names the sections of the navigation open on the page; `lazy_glossary` marks the single page, whose glossary
/// hover `record.js` wraps a heading's run at a time (feature 301 research R8).
///
/// Research: page frame - NONE: process plumbing
#[must_use]
pub fn frame(title: &str, here: &str, open_keys: &str, lazy_glossary: bool) -> (String, String) {
    let root = root_of(here);
    let lazy = if lazy_glossary {
        " data-lazy-glossary"
    } else {
        ""
    };
    let head = format!(
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n\
         <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n\
         <title>{}</title>\n\
         <link rel=\"stylesheet\" href=\"{root}assets/record.css\">\n<link rel=\"stylesheet\" href=\"{root}assets/site.css\">\n\
         <script src=\"{root}assets/theme.js\"></script>\n\
         <script src=\"{root}assets/glossary.js\" defer></script>\n\
         <script src=\"{root}nav.js\" defer></script>\n<script src=\"{root}assets/site.js\" defer></script>\n\
         <script src=\"{root}assets/record.js\" defer></script>\n\
         </head>\n\
         <body class=\"site\" data-root=\"{root}\" data-part=\"{}\" data-page=\"{}\"{lazy}>\n\
         <div class=\"layout\">\n<nav id=\"sidebar\" aria-label=\"Contents\">\
         <noscript><p><a href=\"{root}index.html\">Contents</a> - <a href=\"{root}all.html\">the whole record on one page</a></p></noscript></nav>\n\
         <main>\n",
        esc(title),
        esc(open_keys),
        esc(here)
    );
    (head, "\n</main>\n</div>\n</body>\n</html>\n".to_owned())
}

/// A site page: its frame around its content, every bare URL in the content made a link.
#[must_use]
pub fn shell(title: &str, here: &str, open_keys: &str, body: &str) -> String {
    let (head, tail) = frame(title, here, open_keys, false);
    head + &linkify(body) + &tail
}

/// [`shell`] for a page given in PIECES (the single page, feature 323): each piece linked on its own, as the Python linked them, so a
/// piece's bare URL is found as linking the piece finds it.
#[must_use]
pub fn shell_pieces(title: &str, here: &str, open_keys: &str, body: &[String]) -> String {
    let (head, tail) = frame(title, here, open_keys, true);
    let mut out = head;
    for piece in body {
        out.push_str(&linkify(piece));
    }
    out + &tail
}

#[must_use]
pub fn half_title(half: &str) -> &'static str {
    HALVES
        .iter()
        .find(|(h, _)| *h == half)
        .map_or("", |(_, t)| t)
}

#[must_use]
pub fn section_file(half: &str, section: &Section) -> String {
    format!("{}/{}.html", section_dir(half), section.id)
}

#[must_use]
pub fn tag_file(facet: &str, tag: &str) -> String {
    format!("tags/{facet}-{tag}.html")
}

/// A section's key in the navigation, which a page names to open it.
#[must_use]
pub fn node_key(half: &str, section: &Section) -> String {
    format!("{}/{}", section_dir(half), section.id)
}

/// The navigation nodes open on a page of this section: the section and its ancestors.
#[must_use]
pub fn open_keys(half: &str, path: &[&Section]) -> String {
    path.iter()
        .map(|s| node_key(half, s))
        .collect::<Vec<_>>()
        .join(" ")
}

/// The trail at the top of a page: the record's home, then each (title, site file) given.
#[must_use]
pub fn crumbs(here: &str, trail: &[(String, String)]) -> String {
    let root = root_of(here);
    let mut links = vec![format!(r#"<a href="{root}index.html">{TITLE}</a>"#)];
    links.extend(
        trail
            .iter()
            .map(|(t, f)| format!(r#"<a href="{root}{f}">{}</a>"#, esc(t))),
    );
    format!("<p class=\"crumbs\">{}</p>\n", links.join(" &rsaquo; "))
}

#[must_use]
pub fn section_trail(half: &str, path: &[&Section]) -> Vec<(String, String)> {
    path.iter()
        .map(|s| (s.title.clone(), section_file(half, s)))
        .collect()
}

/// What a section says of itself in one half.
#[must_use]
pub fn description<'s>(section: &'s Section, half: &str) -> &'s str {
    if half == "drawing" {
        &section.drawing_description
    } else {
        &section.description
    }
}

/// Questions as a list: each title linked to its page, its opening sentence beside it.
#[must_use]
pub fn listing(items: &[&Item], here: &str) -> String {
    let root = root_of(here);
    let rows: Vec<String> = items
        .iter()
        .map(|item| {
            let lead = if item.lead.is_empty() {
                String::new()
            } else {
                format!(r#" <span class="lead">{}</span>"#, esc(&item.lead))
            };
            format!(
                r#"<li><a href="{root}q/{}.html">{}</a>{lead}</li>"#,
                item.id,
                esc(&item.title)
            )
        })
        .collect();
    format!("<ul class=\"questions\">\n{}\n</ul>\n", rows.join("\n"))
}

/// Links to the previous and next pages of a run: a section's questions, or the registry's entries.
#[must_use]
pub fn pager(items: &[&Item], at: usize, here: &str, folder: &str) -> String {
    let root = root_of(here);
    let prev = match at.checked_sub(1).and_then(|i| items.get(i)) {
        Some(p) => format!(
            r#"<a rel="prev" href="{root}{folder}/{}.html">&lsaquo; {}</a>"#,
            p.id,
            esc(&p.title)
        ),
        None => "<span></span>".to_owned(),
    };
    let next = match items.get(at + 1) {
        Some(n) => format!(
            r#"<a rel="next" href="{root}{folder}/{}.html">{} &rsaquo;</a>"#,
            n.id,
            esc(&n.title)
        ),
        None => "<span></span>".to_owned(),
    };
    format!("<nav class=\"pager\">{prev}{next}</nav>\n")
}

/// A question's tags, each linking its tag page (spec 303 FR-014).
#[must_use]
pub fn tags_line(tags: &Tags, vocab: &Vocabulary, here: &str) -> String {
    let root = root_of(here);
    let links: Vec<String> = tags
        .all()
        .iter()
        .map(|(f, t)| {
            let name = facet_tags(vocab, f)
                .into_iter()
                .find(|tag| &tag.id == t)
                .map_or_else(String::new, |tag| tag.name);
            format!(r#"<a href="{root}{}">{}</a>"#, tag_file(f, t), esc(&name))
        })
        .collect();
    format!(
        "<p class=\"tags\"><em>Tags:</em> {}</p>\n",
        links.join(", ")
    )
}

/// A facet's tags in the vocabulary's order.
#[must_use]
pub fn facet_tags(vocab: &Vocabulary, facet: &str) -> Vec<Tag> {
    if facet == "level" {
        vocab.level.clone()
    } else {
        vocab.facet(facet).into_iter().map(|(_, t)| t).collect()
    }
}

/// The navigation as data: each half's sections nested with their questions, the tags, and the sources (feature 307).
#[must_use]
pub fn nav_tree(
    record: &Record,
    item_of: &dyn Fn(&str) -> (String, String),
    sources: &[Value],
) -> Value {
    fn node(
        record: &Record,
        half: &str,
        section: &Section,
        item_of: &dyn Fn(&str) -> (String, String),
    ) -> Value {
        json!({
            "key": node_key(half, section),
            "title": section.title,
            "href": section_file(half, section),
            "sections": section.sections.iter().filter(|s| record.holds(s, half)).map(|s| node(record, half, s, item_of)).collect::<Vec<_>>(),
            "items": record.in_section(&section.id, half).iter().map(|p| {
                let (title, id) = item_of(&p.file);
                json!([title, format!("{QUESTION_DIR}/{id}.html")])
            }).collect::<Vec<_>>(),
        })
    }
    let mut groups: Vec<Value> = HALVES
        .iter()
        .map(|(half, label)| {
            json!({
                "label": label,
                "sections": record.sections.iter().filter(|s| record.holds(s, half)).map(|s| node(record, half, s, item_of)).collect::<Vec<_>>(),
            })
        })
        .collect();
    let tag_nodes: Vec<Value> = ct::FACETS
        .iter()
        .map(|facet| {
            json!({
                "key": format!("tags/{facet}"),
                "title": facet_name(facet),
                "href": "index.html#tags",
                "sections": [],
                "items": facet_tags(&record.vocab, facet).iter().map(|t| json!([t.name, tag_file(facet, &t.id)])).collect::<Vec<_>>(),
            })
        })
        .collect();
    groups.push(json!({"label": TAGS_GROUP, "sections": tag_nodes}));
    groups.push(json!({"label": REGISTRY_GROUP, "sections": sources}));
    json!({"title": TITLE, "home": "index.html", "all": "all.html", "groups": groups})
}

/// The navigation tree, once, as data, read by `assets/site.js` on every page (feature 301 research R3).
#[must_use]
pub fn nav_js(tree: &Value) -> String {
    format!(
        "// DERIVED FILE - written by `make record` from the record's fragments (features 301, 303). Never edit here.\nwindow.RECORD_NAV = {};\n",
        l7r_shared::pyjson::dumps(tree, None, false)
    )
}
