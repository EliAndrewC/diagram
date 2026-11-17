//! The site's registry pages, its home page and the single page (`record/site.py`'s `_registry`, `_home` and `_single`, features 301,
//! 303, 307, 312; ported by feature 449 T148, `ask:449-phase4-slices`).

use std::fmt::Write as _;
use std::sync::LazyLock;

use fancy_regex::Regex;
use serde_json::{json, Value};

use super::{
    as_title, canon_list, esc, group_prefix, head_parts, text_of, Build, Item, Shelf, HEAD,
    UNCITED_GROUP, UNCITED_TITLE,
};
use crate::pyre::py;
use crate::record::archive;
use crate::record::contents::{self as ct, Section};
use crate::record::notes::{render_note, Placed};
use crate::record::questions::QUESTIONS;
use crate::record::site_links::REGISTRY_DIR;
use crate::record::site_notes as sn;
use crate::record::site_pages::{self as sp, HALVES, TITLE};
use crate::record::source_tags::{self as st, kind_anchor, kind_heading, section_heading, Label};
use crate::sources::linkify;
use crate::Result;

/// A registry entry's heading, which the one-page record sets a level below its works section's.
static ENTRY_H3: LazyLock<Regex> = LazyLock::new(|| py(r#"(?s)<h3( id="[^"]+">.*?)</h3>"#));
static HEADING_END: LazyLock<Regex> = LazyLock::new(|| py(r"</h[1-4]>"));
static FIRST_P: LazyLock<Regex> = LazyLock::new(|| py(r"(?s)<p>.*?</p>"));

/// A source as the sidebar lists it: its key and its page.
fn nav_row(it: &Item) -> Value {
    json!([it.title, format!("{REGISTRY_DIR}/{}.html", it.id)])
}

/// Works as a contents list: each its key, linking `#<key>`.
fn works_list(items: &[Item]) -> String {
    if items.is_empty() {
        return String::new();
    }
    let rows: Vec<String> = items
        .iter()
        .map(|i| format!("<li><a href=\"#{}\">{}</a></li>", i.id, esc(&i.title)))
        .collect();
    format!("<ul>{}</ul>", rows.concat())
}

/// A works section's line in the one-page record's contents: its kinds nested beneath it, the works beneath each kind - or beneath the
/// section, for the canon (feature 307 FR-004); `pre` scopes the anchors to the uncited group.
fn toc_section(section: &st::Section, kinds: &[(Option<Label>, Vec<Item>)], pre: &str) -> String {
    let subs: String = kinds
        .iter()
        .filter_map(|(lab, run)| {
            let lab = lab.as_ref()?;
            Some(format!(
                "<li><a href=\"#{pre}{}\">{}</a>{}</li>",
                kind_anchor(section, lab),
                esc(&lab.name),
                works_list(run)
            ))
        })
        .collect();
    let direct: Vec<Item> = kinds
        .iter()
        .filter(|(lab, _)| lab.is_none())
        .flat_map(|(_, run)| run.iter().cloned())
        .collect();
    let subs = if subs.is_empty() {
        String::new()
    } else {
        format!("<ul>{subs}</ul>")
    };
    format!(
        "<li><a href=\"#{pre}{}\">{}</a>{}{subs}</li>",
        section.id,
        esc(&section.title),
        works_list(&direct)
    )
}

/// A works section on the home page: its kinds and their works beneath it, each in a block that opens on a click (feature 307 FR-004); a
/// node holding sections (the uncited sources, feature 312) nests them the same way.
fn home_source(node: &Value) -> String {
    let rows: Vec<&Value> = node["items"].as_array().into_iter().flatten().collect();
    let works = if rows.is_empty() {
        String::new()
    } else {
        let lis: Vec<String> = rows
            .iter()
            .map(|r| {
                format!(
                    "<li><a href=\"{}\">{}</a></li>",
                    text(&r[1]),
                    esc(text(&r[0]))
                )
            })
            .collect();
        format!("<ul>{}</ul>", lis.concat())
    };
    let kids: String = node["sections"]
        .as_array()
        .into_iter()
        .flatten()
        .map(home_source)
        .collect();
    let kids = if kids.is_empty() {
        String::new()
    } else {
        format!("<ul>{kids}</ul>")
    };
    format!(
        "<li><details><summary><a href=\"{}\">{}</a></summary>{works}{kids}</details></li>",
        text(&node["href"]),
        esc(text(&node["title"]))
    )
}

fn text(v: &Value) -> &str {
    v.as_str().unwrap_or_default()
}

impl Build {
    /// Every registry entry in the order its pages are chained and listed: group by group, section by section, kind by kind.
    fn registry_run(&self) -> Vec<Item> {
        let mut out = Vec::new();
        for (_, _, items) in &self.registry.groups {
            for (_, kinds) in self.shelves(items) {
                for (_, run) in kinds {
                    out.extend(run);
                }
            }
        }
        out
    }

    /// The sidebar nodes a source's own page opens: its group's (the uncited ones), its section's and its kind's.
    fn open_keys_of(&self, key: &str) -> String {
        let Some(section) = self.catalog.section_of(key) else {
            return "sources".to_owned();
        };
        let tags = self.catalog.tags_of(key);
        let pre = group_prefix(self.group_of.get(key).map_or("", String::as_str));
        let mut keys = format!("sources/{pre}{section}");
        if let Some(t) = tags {
            let _ = write!(keys, " sources/{pre}{section}/{}", t.primary("kind"));
        }
        if pre.is_empty() {
            keys
        } else {
            format!("sources/uncited {keys}")
        }
    }

    /// The Sources group of the sidebar: each works section, its kinds beneath it, the works beneath those (feature 307 FR-001..FR-003);
    /// the uncited sources as one node holding the same sections (feature 312 FR-013).
    pub(super) fn source_nodes(&self) -> Vec<Value> {
        let index = format!("{REGISTRY_DIR}/index.html");
        let (mut nodes, mut uncited) = (Vec::new(), Vec::new());
        for (gid, _, items) in &self.registry.groups {
            let pre = group_prefix(gid);
            for (section, kinds) in self.shelves(items) {
                let Some(section) = section else { continue };
                let subs: Vec<Value> = kinds
                    .iter()
                    .filter_map(|(lab, run)| {
                        let lab = lab.as_ref()?;
                        Some(json!({
                            "key": format!("sources/{pre}{}/{}", section.id, lab.id),
                            "title": lab.name,
                            "href": format!("{index}#{pre}{}", kind_anchor(&section, lab)),
                            "sections": [],
                            "items": run.iter().map(nav_row).collect::<Vec<_>>(),
                        }))
                    })
                    .collect();
                let direct: Vec<Value> = kinds
                    .iter()
                    .filter(|(lab, _)| lab.is_none())
                    .flat_map(|(_, run)| run.iter().map(nav_row))
                    .collect();
                let node = json!({
                    "key": format!("sources/{pre}{}", section.id),
                    "title": section.title,
                    "href": format!("{index}#{pre}{}", section.id),
                    "sections": subs,
                    "items": direct,
                });
                if pre.is_empty() {
                    nodes.push(node);
                } else {
                    uncited.push(node);
                }
            }
        }
        if !uncited.is_empty() {
            nodes.push(json!({
                "key": "sources/uncited",
                "title": UNCITED_TITLE,
                "href": format!("{index}#{UNCITED_GROUP}"),
                "sections": uncited,
                "items": [],
            }));
        }
        nodes
    }

    /// A registry entry as the reader sees it: its marker gone, its labels under its heading, the URLs of its citation line made links
    /// (feature 307 FR-006), and under it the line linking each of its URLs' archived copies (feature 309 FR-010).
    pub(super) fn entry_html(&self, it: &Item) -> String {
        let text = st::strip_marker(&it.html);
        let Some(m) = HEADING_END.find(&text).ok().flatten() else {
            return text;
        };
        let (head, rest) = text.split_at(m.end());
        let labels = self.catalog.labels(&it.id);
        let Some(first) = FIRST_P.find(rest).ok().flatten() else {
            return format!("{head}\n{labels}{rest}");
        };
        let line = archive::entry_line(&it.html, &self.archive);
        let line = if line.is_empty() {
            String::new()
        } else {
            format!("\n{line}")
        };
        format!(
            "{head}\n{labels}{}{}{line}{}",
            &rest[..first.start()],
            linkify(&canon_list(first.as_str())),
            &rest[first.end()..]
        )
    }

    fn shelf_body(&mut self, shelves: &[Shelf], pre: &str, single: bool, out: &mut Vec<String>) {
        for (section, kinds) in shelves {
            if let Some(s) = section {
                out.push(section_heading(s, 3, &format!("{pre}{}", s.id)) + "\n");
            }
            for (lab, entries) in kinds {
                if let (Some(s), Some(l)) = (section, lab) {
                    out.push(kind_heading(s, l, 4, pre) + "\n");
                }
                if single {
                    for i in entries {
                        let html = self.entry_html(i);
                        let done = self.rewrite(
                            &html,
                            None,
                            "all.html",
                            &format!("{REGISTRY_DIR}/ {}", i.id),
                            true,
                        );
                        out.push(ENTRY_H3.replacen(&done, 1, "<h5$1</h5>").into_owned());
                    }
                } else {
                    let rows: Vec<String> = entries
                        .iter()
                        .map(|i| {
                            format!("<li><a href=\"{}.html\">{}</a></li>", i.id, esc(&i.title))
                        })
                        .collect();
                    out.push(format!(
                        "<ul class=\"questions\">\n{}\n</ul>\n",
                        rows.join("\n")
                    ));
                }
            }
        }
    }

    pub(super) fn registry_pages(&mut self) {
        let run = self.registry_run();
        let refs: Vec<&Item> = run.iter().collect();
        let (title, title_id) = (self.registry.title.clone(), self.registry.title_id.clone());
        for (at, it) in run.iter().enumerate() {
            let here = format!("{REGISTRY_DIR}/{}.html", it.id);
            let html = self.entry_html(it);
            let body = self.rewrite(
                &html,
                None,
                &here,
                &format!("{REGISTRY_DIR}/ {}", it.id),
                false,
            );
            let content = sp::crumbs(
                &here,
                &[(title.clone(), format!("{REGISTRY_DIR}/index.html"))],
            ) + &as_title(&body)
                + &sp::pager(&refs, at, &here, REGISTRY_DIR);
            let page = sp::shell(
                &format!("{} - {title}", it.title),
                &here,
                &self.open_keys_of(&it.id),
                &content,
            );
            self.files.set(&here, page);
        }
        let here = format!("{REGISTRY_DIR}/index.html");
        let intro = self.registry.intro.clone();
        let mut body = sp::crumbs(&here, &[])
            + &format!("<h1 id=\"{title_id}\">{}</h1>\n", esc(&title))
            + &self.rewrite(
                &intro,
                None,
                &here,
                &format!("{REGISTRY_DIR}/_front.html"),
                false,
            )
            + "\n";
        let groups = self.registry.groups.clone();
        for (gid, ghtml, items) in &groups {
            body += &self.rewrite(
                ghtml,
                None,
                &here,
                &format!("{REGISTRY_DIR}/ group {gid}"),
                false,
            );
            let shelves = self.shelves(items);
            let mut parts = Vec::new();
            self.shelf_body(&shelves, group_prefix(gid), false, &mut parts);
            body += &parts.concat();
        }
        let page = sp::shell(&title, &here, "sources", &body);
        self.files.set(&here, page);
    }

    fn home_tree(&self, half: &str, sections: &[Section]) -> String {
        let rows: Vec<String> = sections
            .iter()
            .filter(|s| self.record.holds(s, half))
            .map(|s| {
                format!(
                    "<li><a href=\"{}\">{}</a>{}</li>",
                    sp::section_file(half, s),
                    esc(&s.title),
                    self.home_tree(half, &s.sections)
                )
            })
            .collect();
        if rows.is_empty() {
            String::new()
        } else {
            format!("<ul>{}</ul>", rows.concat())
        }
    }

    pub(super) fn home(&mut self) -> Result<()> {
        let mut body = vec![
            format!("<h1 id=\"contents\">{TITLE}</h1>"),
            ct::load_opening(&self.record_dir)?,
            "<p><a href=\"all.html\">The whole record on one page</a> - every question, every note and every source, under one table of contents.</p>".to_owned(),
        ];
        for (half, label) in HALVES {
            body.push(format!(
                "<h2 id=\"{half}\">{}</h2>\n{}",
                esc(label),
                self.home_tree(half, &self.record.sections)
            ));
        }
        body.push(format!("<h2 id=\"tags\">{}</h2>", sp::TAGS_GROUP));
        for facet in ct::FACETS {
            let tags: Vec<String> = sp::facet_tags(&self.record.vocab, facet)
                .iter()
                .map(|t| {
                    format!(
                        "<a href=\"{}\">{}</a>",
                        sp::tag_file(facet, &t.id),
                        esc(&t.name)
                    )
                })
                .collect();
            body.push(format!(
                "<p><em>{}:</em> {}</p>",
                sp::facet_name(facet),
                tags.join(", ")
            ));
        }
        let sources: String = self.source_nodes().iter().map(home_source).collect();
        body.push(format!(
            "<h2><a href=\"{REGISTRY_DIR}/index.html\">{}</a></h2>\n<ul>{sources}</ul>",
            sp::REGISTRY_GROUP
        ));
        let page = sp::shell(TITLE, "index.html", "", &body.join("\n"));
        self.files.set("index.html", page);
        Ok(())
    }

    fn single_walk(
        &mut self,
        half: &str,
        sections: &[Section],
        count: &mut sn::Numbering,
        toc: &mut Vec<String>,
        out: &mut Vec<String>,
    ) -> Result<()> {
        for s in sections {
            if !self.record.holds(s, half) {
                continue;
            }
            let anchor = format!("{half}-{}", s.id);
            let run = self.section_items(s, half);
            let rows: Vec<String> = run
                .iter()
                .map(|(_, i)| format!("<li><a href=\"#{}\">{}</a></li>", i.id, esc(&i.title)))
                .collect();
            toc.push(format!(
                "<li><a href=\"#{anchor}\">{}</a><ul>{}",
                esc(&s.title),
                rows.concat()
            ));
            out.push(format!(
                "<section class=\"part\">\n<h1 id=\"{anchor}\">{}</h1>\n{}\n",
                esc(&s.title),
                sp::description(s, half)
            ));
            for (page, it) in &run {
                let place = format!("{QUESTIONS}/{}", page.file);
                let rewritten = self.rewrite(&it.html, Some(&page.file), "all.html", &place, true);
                let notes = self.notes_of(page)?;
                // `number` refuses only with a `NoteError` (a reference no note of its page defines), which the build keeps
                match count.number(&rewritten, &page.file, &notes, &place) {
                    Ok(done) => out.push(done),
                    Err(e) => self.errors.push(e.message),
                }
            }
            out.push("</section>\n".to_owned());
            self.single_walk(half, &s.sections, count, toc, out)?;
            toc.push("</ul></li>".to_owned());
        }
        Ok(())
    }

    /// The whole record on one page: contents, both halves in table-of-contents order, the citations, the sources. The page is handed to
    /// the shell in its pieces, each linked on its own, as the Python handed them (features 323, 327).
    pub(super) fn single(&mut self) -> Result<()> {
        let mut count = sn::Numbering::new();
        let mut toc = vec!["<nav class=\"toc\"><h2 id=\"contents\">Contents</h2>\n<ul>".to_owned()];
        let mut out: Vec<String> = Vec::new();
        let sections = self.record.sections.clone();
        for (half, label) in HALVES {
            toc.push(format!("<li><a href=\"#{half}\">{}</a><ul>", esc(label)));
            out.push(format!(
                "<h1 id=\"{half}\" class=\"half\">{}</h1>\n",
                esc(label)
            ));
            self.single_walk(half, &sections, &mut count, &mut toc, &mut out)?;
            toc.push("</ul></li>".to_owned());
        }
        toc.push("<li><a href=\"#citations\">Citations</a></li>".to_owned());
        let mut notes = Vec::new();
        for (file, placed) in &count.placed {
            let body = self.rewrite(
                &placed.body,
                Some(file),
                "all.html",
                &format!("{QUESTIONS}/{file} notes"),
                true,
            );
            let keyed = Placed {
                key: placed.key.clone(),
                number: placed.number,
                body: sn::keyed_to(&body, "#"),
                references: 0,
            };
            notes.push(render_note(&keyed, ""));
        }
        out.push(format!("<section class=\"part footnotes\">\n<h1 id=\"citations\">Citations</h1>\n<ol>\n{}\n</ol></section>\n", notes.join("\n")));
        let groups = self.registry.groups.clone();
        let (title, title_id) = (self.registry.title.clone(), self.registry.title_id.clone());
        let mut reg_toc = format!("<li><a href=\"#{title_id}\">{}</a><ul>", esc(&title));
        for (gid, gh, gi) in &groups {
            let name = HEAD
                .captures(gh)
                .ok()
                .flatten()
                .map_or_else(|| gid.clone(), |m| text_of(head_parts(&m).1));
            let _ = write!(reg_toc, "<li><a href=\"#{gid}\">{}</a>", esc(&name));
            if !gi.is_empty() {
                let lines: String = self
                    .shelves(gi)
                    .iter()
                    .filter_map(|(s, kinds)| {
                        Some(toc_section(s.as_ref()?, kinds, group_prefix(gid)))
                    })
                    .collect();
                let _ = write!(reg_toc, "<ul>{lines}</ul>");
            }
            reg_toc += "</li>";
        }
        toc.push(reg_toc + "</ul></li>");
        out.push(format!(
            "<section class=\"part\">\n<h1 id=\"{title_id}\">{}</h1>\n",
            esc(&title)
        ));
        let intro = self.registry.intro.clone();
        let rewritten = self.rewrite(
            &intro,
            None,
            "all.html",
            &format!("{REGISTRY_DIR}/_front.html"),
            true,
        );
        out.push(rewritten);
        for (gid, ghtml, items) in &groups {
            let rewritten = self.rewrite(
                ghtml,
                None,
                "all.html",
                &format!("{REGISTRY_DIR}/ group {gid}"),
                true,
            );
            out.push(rewritten);
            let shelves = self.shelves(items);
            self.shelf_body(&shelves, group_prefix(gid), true, &mut out);
        }
        out.push("</section>\n".to_owned());
        toc.push("</ul></nav>\n".to_owned());
        let opening = ct::load_opening(&self.record_dir)?;
        let head = format!("<h1 id=\"record\">{TITLE}</h1>\n{opening}\n<p><em>Every question, every note and every source on one page. The same record, a page per question: <a href=\"index.html\">the contents</a>.</em></p>\n");
        let mut pieces = vec![head, toc.concat()];
        pieces.append(&mut out);
        let page = sp::shell_pieces(
            &format!("{TITLE} - the whole record"),
            "all.html",
            "",
            &pieces,
        );
        self.files.set("all.html", page);
        Ok(())
    }
}
