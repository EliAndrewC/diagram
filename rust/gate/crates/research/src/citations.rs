//! The works a question's notes cite, and what kind of note each is (`interactive/citations.py`, features 211, 235, 303; ported by feature
//! 449 T148, phase 4's S5, `ask:449-phase4-slices`). A work's write-up is written once, in its registry entry (the GM, feature 211: *"we
//! do not want to have multiple different write ups of a single paper"*); what is DERIVED is the works block at the foot of a question's
//! page of the site ([`works_html`]), each work under the section its tags put it in (feature 305), in order of first citation.
//!
//! The note classifier ([`footnote_form`]) is the one the build's census reads, so the census and any later reader cannot disagree about
//! what a note is (feature 195; the third form, a GROUNDS note, feature 235).

use std::sync::LazyLock;

use fancy_regex::Regex;

use crate::pyre::py;
use crate::record::absence;
use crate::record::source_tags::{section_heading, Catalog};
use crate::sources::{link_target, linkify, Entry, WHAT_LABEL, WHY_LABEL};
use crate::{drop_all, re};
use l7r_guard::shared::py_text::{repr, strip};

static KEY_LINK: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<a href="[^"]*"><code>([a-z0-9][a-z0-9-]*)</code></a>"#));
static BACK: LazyLock<Regex> =
    LazyLock::new(|| py(r#"\s*<a class="fnback" href="[^"]*">back</a>"#));
static HREF_OF_KEY: LazyLock<Regex> =
    LazyLock::new(|| re(r#"<a href="([^"]*)"><code>[a-z0-9][a-z0-9-]*</code></a>"#));
/// The markers the works block is derived between.
pub const WORKS_OPEN: &str = "<!-- works-cited: DERIVED by `make citations` from SOURCES.html - change a work's write-up in its registry entry, never here -->";
pub const WORKS_CLOSE: &str = "<!-- /works-cited -->";

/// An ABSENCE note: no key, no link, what was searched and when - THE BACKLOG, the only kind that owes work. The search may be an HTML
/// comment after the marker (feature 292).
static ABSENCE: LazyLock<Regex> = LazyLock::new(|| {
    py(
        r"^no publicly readable source\s*(?:\(searched \d{4}-\d{2}-\d{2}:|<!--\s*searched \d{4}-\d{2}-\d{2}:)",
    )
});
/// An absence searched to exhaustion by two dated passes carries the marker beside its search (feature 235 FR-004).
static SETTLED: LazyLock<Regex> = LazyLock::new(|| re(r"settled \d{4}-\d{2}-\d{2}"));
/// THE SIX REASONS A GROUNDS NOTE MAY NAME (feature 235, the GM 2026-09-12), closed on purpose: a seventh is a change to the spec.
pub const GROUNDS_REASONS: [&str; 6] = [
    "measured on our own maps",
    "the record's own silence",
    "follows from the definitions",
    "physical necessity",
    "a drawing convention",
    "this project's decision",
];
/// The reason captured with `*`, so a grounds note with NO reason is one the classifier can name. `$` as Python's: the end, or before a
/// final newline.
static GROUNDS: LazyLock<Regex> =
    LazyLock::new(|| py(r"(?s)^no source is owed:\s*(.*?)\s*(?:<!--|$)"));
static REASON_SPLIT: LazyLock<Regex> = LazyLock::new(|| {
    let alternatives: Vec<String> = GROUNDS_REASONS
        .iter()
        .map(|r| fancy_regex::escape(r).into_owned())
        .collect();
    py(&format!(r";|,(?=\s*(?:{}))", alternatives.join("|")))
});

/// The registry keys the notes cite, in order of first citation, once each - the order the works block lists them.
#[must_use]
pub fn cited_keys<'a>(bodies: impl IntoIterator<Item = &'a str>) -> Vec<String> {
    let mut keys: Vec<String> = Vec::new();
    for body in bodies {
        for c in KEY_LINK.captures_iter(body).flatten() {
            if !keys.iter().any(|k| k == &c[1]) {
                keys.push(c[1].to_owned());
            }
        }
    }
    keys
}

/// The works block for `keys`, and the keys whose entry lacks a write-up (a refusal: a new source cannot be cited without one). Each work:
/// its key linked as feature 190 links it, its labels, its citation line, and the two write-ups; a work the catalog refused is left out.
#[must_use]
pub fn works_html(
    keys: &[String],
    entries: &[(String, Entry)],
    rel: &str,
    catalog: &Catalog,
) -> (String, Vec<String>) {
    let entry = |k: &str| entries.iter().find(|(key, _)| key == k).map(|(_, e)| e);
    let missing: Vec<String> = keys
        .iter()
        .filter(|k| entry(k).is_none_or(|e| e.what.is_empty() || e.why.is_empty()))
        .cloned()
        .collect();
    let kept: Vec<String> = keys
        .iter()
        .filter(|k| !missing.contains(k))
        .cloned()
        .collect();
    let mut parts = vec![WORKS_OPEN.to_owned()];
    for (section, run) in catalog.grouped(&kept) {
        parts.push(section_heading(
            &section,
            3,
            &format!("page-{}", section.id),
        ));
        for key in run {
            let Some(e) = entry(&key) else { continue };
            parts.push(format!(
                r#"<h4 id="work-{key}"><a href="{}"><code>{key}</code></a></h4>"#,
                link_target(&key, &e.line, rel)
            ));
            parts.push(catalog.labels(&key));
            parts.push(format!("<p>{}</p>", linkify(&e.cite)));
            parts.push(format!("<p><em>{WHAT_LABEL}</em> {}</p>", e.what));
            parts.push(format!("<p><em>{WHY_LABEL}</em> {}</p>", e.why));
        }
    }
    parts.push(WORKS_CLOSE.to_owned());
    (parts.join("\n"), missing)
}

/// The reasons a grounds note names, in order.
#[must_use]
pub fn grounds_reasons(body: &str) -> Vec<String> {
    let unbacked = drop_all(&BACK, body);
    let Some(c) = GROUNDS.captures(strip(&unbacked)).ok().flatten() else {
        return Vec::new();
    };
    let reasons = c.get(1).map_or("", |m| m.as_str());
    py_split(&REASON_SPLIT, reasons)
        .into_iter()
        .map(|r| strip(r).to_owned())
        .filter(|r| !r.is_empty())
        .collect()
}

/// `re.split(pattern, text)` of a pattern with no groups.
fn py_split<'t>(pattern: &Regex, text: &'t str) -> Vec<&'t str> {
    let mut out = Vec::new();
    let mut at = 0;
    for m in pattern.find_iter(text).flatten() {
        out.push(&text[at..m.start()]);
        at = m.end();
    }
    out.push(&text[at..]);
    out
}

/// An absence note that two dated passes have searched to exhaustion.
#[must_use]
pub fn is_settled(body: &str) -> bool {
    SETTLED.is_match(body).unwrap_or(false)
}

fn matches(pattern: &Regex, text: &str) -> bool {
    pattern.is_match(text).unwrap_or(false)
}

/// `citation`, `absence`, `grounds`, or the defect (feature 195 FR-002; feature 235 the third form); None for a note of no form. A
/// citation links its key to an http(s) page unless the key is canon; an absence or grounds note carries no key and no link.
#[must_use]
pub fn footnote_form(body: &str, canon: &std::collections::BTreeSet<String>) -> Option<String> {
    let body = drop_all(&BACK, body);
    let has_link = body.contains("<code>") || body.contains("href=\"");
    if matches(&GROUNDS, strip(&body)) {
        if has_link {
            return Some("a grounds note carries no key and no link".to_owned());
        }
        let named = grounds_reasons(&body);
        let unknown: Vec<String> = named
            .iter()
            .filter(|r| !GROUNDS_REASONS.contains(&r.as_str()))
            .map(|r| repr(r))
            .collect();
        if !unknown.is_empty() {
            return Some(format!(
                "names a reason that is not one of the six: [{}]",
                unknown.join(", ")
            ));
        }
        if named.is_empty() {
            return Some("a grounds note names at least one of the six reasons".to_owned());
        }
        return Some("grounds".to_owned());
    }
    let unrendered = absence::unrender(&body);
    if matches(
        &ABSENCE,
        unrendered.trim_start_matches(l7r_guard::shared::py_text::is_space),
    ) {
        if has_link {
            return Some("an absence note carries no key and no link".to_owned());
        }
        return Some("absence".to_owned());
    }
    let key = KEY_LINK.captures(&body).ok().flatten()?;
    let target = HREF_OF_KEY.captures(&body).ok().flatten()?[1].to_owned();
    if target.starts_with("http://") || target.starts_with("https://") {
        return Some("citation".to_owned());
    }
    if target.contains("SOURCES.html#") && canon.contains(&key[1]) {
        return Some("citation".to_owned());
    }
    Some(format!(
        "links the key to {}, which is not a page on the public internet where the quote can be read",
        repr(&target)
    ))
}

#[cfg(test)]
mod tests;
