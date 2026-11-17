//! Where a link in the record goes once the record is a site (`record/site_links.py`, features 301, 303; ported by feature 449 T148,
//! `ask:449-phase4-slices`). A question's fragment links from `questions/`: another question's page as its file name, an id on the same
//! page as `#id`, the registry as `../SOURCES.html#<key>`, an asset as `../assets/...`, a section as `../contents.json#<section id>`. The
//! site writes every page twice - its own small page and its anchor on the single page - so each `href` is resolved once, against the
//! page it was written in, and written for both. Nothing is guessed: a link that lands nowhere is a refusal naming the fragment (spec 301
//! FR-006); a link in a session note (an HTML comment) is not a link and is left alone.

use std::collections::{HashMap, HashSet};
use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::pyre::py;
use crate::re;

/// The registry's page, as a link names it, and its site directory.
pub const REGISTRY: &str = "SOURCES.html";
pub const REGISTRY_DIR: &str = "sources";
/// The record's table of contents: a link to `contents.json#<id>` is a link to that section.
pub const CONTENTS: &str = "contents.json";
pub const QUESTIONS: &str = "questions";
/// Where a question's small page is - flat, so a regrouping moves no URL (spec 303 FR-004).
pub const QUESTION_DIR: &str = "q";

/// Where each half's section pages are in the site.
#[must_use]
pub fn section_dir(half: &str) -> &'static str {
    if half == "research" {
        "findings"
    } else {
        "drawing"
    }
}

/// Python's `\w` for one character (`pyre::WORD`).
static WORD: LazyLock<Regex> = LazyLock::new(|| re(&format!("^[{}]$", crate::pyre::WORD)));
static COMMENT: LazyLock<Regex> = LazyLock::new(|| re(r"(?s)<!--.*?-->"));
static SCHEME: LazyLock<Regex> = LazyLock::new(|| py(r"(?i)^[a-z][a-z0-9+.-]*:"));

/// Where an anchor lives in the site: a question page (`q`, its heading id), the registry (`source`, an entry's key or none for the
/// registry's own page) or a section (`section`, its anchor on the single page, `half-id`), and the anchor (none for the top).
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Loc {
    pub kind: &'static str,
    pub page: Option<String>,
    pub anchor: Option<String>,
}

/// What a link resolves to: a place in the site, a file of the record that is not a page (an asset), or nothing (it leaves the record).
#[derive(Debug, Clone, PartialEq, Eq)]
pub enum Target {
    Loc(Loc),
    Asset(String),
    Outside,
}

fn is_word(c: Option<char>) -> bool {
    c.is_some_and(|c| WORD.is_match(c.encode_utf8(&mut [0; 4])).unwrap_or(false))
}

/// Every id in a piece of markup, outside session notes: the Python's `\bid="([^"]+)"` found by hand, because the regex engine has no
/// `\b` of Python's and the backtracking one took two seconds of the build's index over the record (feature 449 T148): an `id="` whose
/// `i` follows no word character, then one or more characters to the next quote; a failed one is tried again a character on.
#[must_use]
pub fn ids_in(html: &str) -> Vec<String> {
    let bare = COMMENT.replace_all(html, "");
    let mut out = Vec::new();
    let mut at = 0;
    while let Some(found) = bare[at..].find("id=\"") {
        let start = at + found;
        let value = start + 4;
        let follows_word = is_word(bare[..start].chars().next_back());
        match bare[value..].find('"') {
            Some(len) if len > 0 && !follows_word => {
                out.push(bare[value..value + len].to_owned());
                at = value + len + 1;
            }
            _ => at = start + 1,
        }
    }
    out
}

/// One link or image source, found as the Python's `(<(?:a|img)\b[^>]*?\s(?:href|src)=")([^"]*)(")` finds it: the tag's opening, its
/// value, and where the match ends. By hand for the reason [`ids_in`] gives.
fn attr_at(text: &str, start: usize) -> Option<(usize, usize, usize)> {
    let rest = &text[start + 1..];
    let name = if rest.starts_with('a') {
        1
    } else if rest.starts_with("img") {
        3
    } else {
        return None;
    };
    let after = start + 1 + name;
    if is_word(text[after..].chars().next()) {
        return None;
    }
    // the lazy run: the first space-and-attribute before a `>`
    let mut at = after;
    for c in text[after..].chars() {
        if c == '>' {
            return None;
        }
        if l7r_guard::shared::py_text::is_space(c) {
            let next = at + c.len_utf8();
            if let Some(attr) = ["href=\"", "src=\""]
                .iter()
                .find(|a| text[next..].starts_with(**a))
            {
                // no closing quote after this value means none after any later one either
                let value = next + attr.len();
                let close = text[value..].find('"')?;
                return Some((value, value + close, value + close + 1));
            }
        }
        at += c.len_utf8();
    }
    None
}

/// Every id in the record, mapped to where it lives - built once, asked per link.
#[derive(Debug, Default)]
pub struct Index {
    /// question file name to its page's heading id
    pub files: HashMap<String, String>,
    ids: HashMap<String, HashSet<String>>,
    /// id on the registry to the entry holding it (None: its own page)
    pub registry: HashMap<String, Option<String>>,
    /// section id to the half whose page a link to it opens
    sections: HashMap<String, String>,
}

impl Index {
    #[must_use]
    pub fn new() -> Self {
        Self::default()
    }

    /// A section with a page in `half`; the first half given is the one a link opens.
    pub fn add_section(&mut self, section_id: &str, half: &str) {
        self.sections
            .entry(section_id.to_owned())
            .or_insert_with(|| half.to_owned());
    }

    pub fn add_page(&mut self, file: &str, heading_id: &str, html: &str) {
        self.files.insert(file.to_owned(), heading_id.to_owned());
        let mut ids: HashSet<String> = ids_in(html).into_iter().collect();
        ids.insert(heading_id.to_owned());
        self.ids.insert(file.to_owned(), ids);
    }

    pub fn add_registry(&mut self, entry: Option<&str>, html: &str) {
        for found in ids_in(html) {
            self.registry
                .entry(found)
                .or_insert_with(|| entry.map(str::to_owned));
        }
        if let Some(e) = entry {
            self.registry.insert(e.to_owned(), Some(e.to_owned()));
        }
    }

    /// What `href` points at, written in the question page `own` (or, with `own` none, in the registry).
    ///
    /// # Errors
    /// A link into the record that lands nowhere, its words naming the link.
    pub fn resolve(&self, href: &str, own: Option<&str>) -> Result<Target, String> {
        if href.is_empty() || SCHEME.is_match(href).unwrap_or(false) || href.starts_with("//") {
            return Ok(Target::Outside);
        }
        let (path, anchor) = href.split_once('#').unwrap_or((href, ""));
        if path.is_empty() {
            return match own {
                None => self.in_registry(anchor, href),
                Some(file) => self.in_question(file, anchor, href),
            };
        }
        let joined = if own.is_some() && !path.starts_with('/') {
            format!("{QUESTIONS}/{path}")
        } else {
            path.to_owned()
        };
        let target = normpath(&joined);
        if target == REGISTRY {
            return self.in_registry(anchor, href);
        }
        if target == CONTENTS {
            let Some(half) = self.sections.get(anchor) else {
                return Err(format!(
                    "`{href}` - no section `{anchor}` in the record's contents"
                ));
            };
            return Ok(Target::Loc(Loc {
                kind: "section",
                page: Some(format!("{half}-{anchor}")),
                anchor: None,
            }));
        }
        if let Some(file) = target.strip_prefix(&format!("{QUESTIONS}/")) {
            return self.in_question(file, anchor, href);
        }
        if crate::has_ext(&target, "html") {
            return Err(format!("`{href}` - no such page in the record"));
        }
        Ok(Target::Asset(if anchor.is_empty() {
            target
        } else {
            format!("{target}#{anchor}")
        }))
    }

    fn in_question(&self, file: &str, anchor: &str, href: &str) -> Result<Target, String> {
        let Some(heading) = self.files.get(file) else {
            return Err(format!("`{href}` - no question page {file}"));
        };
        if !anchor.is_empty() && !self.ids[file].contains(anchor) {
            return Err(format!("`{href}` - no id `{anchor}` on {file}"));
        }
        Ok(Target::Loc(Loc {
            kind: "q",
            page: Some(heading.clone()),
            anchor: (!anchor.is_empty() && anchor != heading).then(|| anchor.to_owned()),
        }))
    }

    fn in_registry(&self, anchor: &str, href: &str) -> Result<Target, String> {
        if anchor.is_empty() {
            return Ok(Target::Loc(Loc {
                kind: "source",
                page: None,
                anchor: None,
            }));
        }
        let Some(entry) = self.registry.get(anchor) else {
            return Err(format!("`{href}` - no id `{anchor}` on the registry"));
        };
        Ok(Target::Loc(Loc {
            kind: "source",
            page: entry.clone(),
            anchor: (entry.as_deref() != Some(anchor)).then(|| anchor.to_owned()),
        }))
    }
}

/// The site file a place in the record is on.
#[must_use]
pub fn site_file(loc: &Loc) -> String {
    match (loc.kind, &loc.page) {
        ("q", page) => format!("{QUESTION_DIR}/{}.html", page.as_deref().unwrap_or("None")),
        ("section", page) => {
            let page = page.as_deref().unwrap_or("");
            let (half, sid) = page.split_once('-').unwrap_or((page, ""));
            format!("{}/{sid}.html", section_dir(half))
        }
        (_, Some(page)) => format!("{REGISTRY_DIR}/{page}.html"),
        (_, None) => format!("{REGISTRY_DIR}/index.html"),
    }
}

/// The link from the site file `here` to `loc` on the multi-page site.
#[must_use]
pub fn site_href(loc: &Loc, here: &str) -> String {
    let file = site_file(loc);
    if let Some(anchor) = loc.anchor.as_deref().filter(|_| file == here) {
        return format!("#{anchor}");
    }
    let rel = relpath(&file, dirname(here));
    match &loc.anchor {
        Some(a) => format!("{rel}#{a}"),
        None => rel,
    }
}

/// The same link on the single page, where every page is an anchor (a section's is its `page`, `half-id`).
#[must_use]
pub fn single_href(loc: &Loc, registry_title: &str) -> String {
    let to = loc
        .anchor
        .as_deref()
        .filter(|a| !a.is_empty())
        .or(loc.page.as_deref().filter(|p| !p.is_empty()))
        .unwrap_or(registry_title);
    format!("#{to}")
}

/// A file of the record that is not a page (`assets/record.css`), from the site file `here`.
#[must_use]
pub fn asset_href(target: &str, here: &str) -> String {
    let (path, anchor) = target.split_once('#').unwrap_or((target, ""));
    let rel = relpath(path, dirname(&format!("site/{here}")));
    if anchor.is_empty() {
        rel
    } else {
        format!("{rel}#{anchor}")
    }
}

/// `markup` with every link rewritten for one form - the small pages (`single` false, `here` the file it is written to) or the single
/// page - and the refusals, each naming `place`. `own` is the question page the markup belongs to (none: the registry).
#[must_use]
pub fn rewrite(
    markup: &str,
    own: Option<&str>,
    index: &Index,
    here: &str,
    single: bool,
    place: &str,
    registry_title: &str,
) -> (String, Vec<String>) {
    let hidden: Vec<(usize, usize)> = COMMENT
        .find_iter(markup)
        .flatten()
        .map(|m| (m.start(), m.end()))
        .collect();
    let mut errors = Vec::new();
    let mut out = String::with_capacity(markup.len());
    let (mut copied, mut at) = (0, 0);
    while let Some(found) = markup[at..].find('<') {
        let start = at + found;
        let Some((value, close, end)) = attr_at(markup, start) else {
            at = start + 1;
            continue;
        };
        at = end;
        if hidden.iter().any(|(a, b)| *a <= start && start < *b) {
            continue;
        }
        let href = match index.resolve(&markup[value..close], own) {
            Err(e) => {
                errors.push(format!("{place}: {e}"));
                continue;
            }
            Ok(Target::Outside) => continue,
            Ok(Target::Asset(t)) => asset_href(&t, if single { "all.html" } else { here }),
            Ok(Target::Loc(loc)) if single => single_href(&loc, registry_title),
            Ok(Target::Loc(loc)) => site_href(&loc, here),
        };
        out.push_str(&markup[copied..value]);
        out.push_str(&href);
        copied = close;
    }
    out.push_str(&markup[copied..]);
    (out, errors)
}

/// `posixpath.dirname`.
#[must_use]
pub fn dirname(p: &str) -> &str {
    let head = &p[..p.rfind('/').map_or(0, |at| at + 1)];
    if head.bytes().all(|b| b == b'/') {
        head
    } else {
        head.trim_end_matches('/')
    }
}

/// `posixpath.normpath`: `.` and empty parts dropped, `..` taken back over the part before it (at the root of an absolute path,
/// dropped), the leading slash kept - two kept as two, three or more as one.
#[must_use]
pub fn normpath(p: &str) -> String {
    let lead = match p.bytes().take_while(|b| *b == b'/').count() {
        0 => "",
        2 => "//",
        _ => "/",
    };
    let mut out: Vec<&str> = Vec::new();
    for part in p.split('/') {
        match part {
            "" | "." => {}
            ".." if out.last().is_some_and(|l| *l != "..") => {
                out.pop();
            }
            ".." if !lead.is_empty() => {}
            other => out.push(other),
        }
    }
    let body = out.join("/");
    if lead.is_empty() && body.is_empty() {
        ".".to_owned()
    } else {
        format!("{lead}{body}")
    }
}

/// `posixpath.relpath(path, start)`, `start` "" read as `.`: both made absolute from the working directory first, as `abspath` makes them
/// (a relative pair's common part cancels; an absolute link in the record is written relative to where the build ran, as the Python
/// wrote it).
#[must_use]
pub fn relpath(path: &str, start: &str) -> String {
    let cwd = std::env::current_dir().unwrap_or_default();
    let abs = |p: &str| {
        if p.starts_with('/') {
            p.to_owned()
        } else {
            format!("{}/{p}", cwd.display())
        }
    };
    let split = |p: &str| -> Vec<String> {
        normpath(&abs(p))
            .split('/')
            .filter(|x| !x.is_empty())
            .map(str::to_owned)
            .collect()
    };
    let (a, b) = (
        split(path),
        split(if start.is_empty() { "." } else { start }),
    );
    let common = a.iter().zip(&b).take_while(|(x, y)| x == y).count();
    let mut parts: Vec<String> = vec!["..".to_owned(); b.len() - common];
    parts.extend(a[common..].iter().cloned());
    if parts.is_empty() {
        ".".to_owned()
    } else {
        parts.join("/")
    }
}

#[cfg(test)]
mod tests;
